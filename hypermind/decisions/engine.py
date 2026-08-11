"""Decision analyze engine — propose actions only; never write Decision Log."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from hypermind.decisions.conflict import ConflictHit, analyze_against_active
from hypermind.decisions.instruction import DECISION_RELATIONSHIP_INSTRUCTION
from hypermind.decisions.resolve import DecisionResolver
from hypermind.decisions.types import (
    DecisionAction,
    DecisionAnalyzeRequest,
    DecisionAnalyzeResult,
    DecisionProposal,
    DecisionRelationship,
    DecisionScope,
    candidate_dict_from_request,
    new_request_id,
)
from hypermind.models import ModelRequest, ProviderError
from hypermind.models.adapters import OllamaProvider, default_providers

_MODEL_REL_MAP = {
    "duplicate": DecisionRelationship.DUPLICATE.value,
    "compatible": DecisionRelationship.COMPATIBLE.value,
    "supersession_candidate": DecisionRelationship.POSSIBLE_SUPERSESSION.value,
    "conflict_candidate": DecisionRelationship.POSSIBLE_CONFLICT.value,
    "unrelated": DecisionRelationship.UNRELATED.value,
    "possible_supersession": DecisionRelationship.POSSIBLE_SUPERSESSION.value,
    "possible_conflict": DecisionRelationship.POSSIBLE_CONFLICT.value,
}


class DecisionAnalyzeEngine:
    """
    Analyze formal decision semantics for human review.

    Never writes Decision_Log.md or any durable decision store.
    At most ONE model generation when deterministic confidence is low.
    """

    def __init__(
        self,
        *,
        resolver: DecisionResolver | None = None,
        decision_log_path: Path | None = None,
        allow_stub: bool = False,
        model_classifier: Callable[[str, str], dict[str, Any]] | None = None,
    ) -> None:
        self.allow_stub = allow_stub
        self._model_classifier = model_classifier
        if resolver is not None:
            self.resolver = resolver
        elif decision_log_path is not None:
            self.resolver = DecisionResolver.from_path(decision_log_path)
        else:
            from hypermind.config.context_config import load_context_config

            cfg = load_context_config()
            path = cfg.roots.decision_log
            self.resolver = (
                DecisionResolver.from_path(path)
                if path.is_file()
                else DecisionResolver([])
            )

    def analyze(self, request: DecisionAnalyzeRequest) -> DecisionAnalyzeResult:
        started = time.perf_counter()
        request_id = new_request_id()
        scope = request.scope or DecisionScope.PROJECT.value
        project = request.project

        # Decision Log is shared governance — inspect all ACTIVE by default
        active = self.resolver.get_active_decisions()
        if scope == DecisionScope.GLOBAL.value:
            active = [
                d
                for d in active
                if d.scope == DecisionScope.GLOBAL.value
            ]
        elif project:
            # Prefer same-project + global; still include other ACTIVE for conflict
            # checks when the log is shared (portfolio-os). Soft order only.
            active = sorted(
                active,
                key=lambda d: (
                    0
                    if d.scope == DecisionScope.GLOBAL.value
                    or (d.project or "").lower() == project.lower()
                    else 1
                ),
            )

        hit = analyze_against_active(
            request.statement,
            active,
            scope=scope,
            project=project,
        )

        generation_count = 0
        if (
            request.allow_model_assist
            and hit.confidence < 0.55
            and hit.related_ids
            and hit.relationship
            in {
                DecisionRelationship.COMPATIBLE.value,
                DecisionRelationship.UNRELATED.value,
                DecisionRelationship.NEW.value,
            }
        ):
            related = self.resolver.get(hit.related_ids[0])
            if related is not None:
                assisted, used = self._model_assist(
                    request.statement,
                    related.statement,
                    related_id=related.id,
                    frozen=related.frozen,
                )
                generation_count = 1 if used else 0
                if assisted is not None:
                    hit = assisted

        proposal = self._to_proposal(request, hit)
        duration_ms = int((time.perf_counter() - started) * 1000)
        trace = {
            "request_id": request_id,
            "project": project,
            "scope": scope,
            "active_decisions_inspected": len(active),
            "relationship": proposal.relationship,
            "related_decision_ids": list(proposal.related_decisions),
            "model_generation_count": generation_count,
            "duration_ms": duration_ms,
            "status": "completed",
            "decision_written": False,
            "decision_log_mutated": False,
        }
        return DecisionAnalyzeResult(
            ok=True,
            request_id=request_id,
            proposal=proposal,
            trace=trace,
        )

    def _to_proposal(
        self, request: DecisionAnalyzeRequest, hit: ConflictHit
    ) -> DecisionProposal:
        action = hit.action
        relationship = hit.relationship
        # Map COMPATIBLE / UNRELATED / NEW with no conflict → CREATE
        if relationship in {
            DecisionRelationship.NEW.value,
            DecisionRelationship.COMPATIBLE.value,
            DecisionRelationship.UNRELATED.value,
        }:
            action = DecisionAction.CREATE.value
            if relationship == DecisionRelationship.COMPATIBLE.value:
                # Compatible with existing → still CREATE (coexist)
                pass
            elif relationship == DecisionRelationship.UNRELATED.value:
                relationship = DecisionRelationship.NEW.value

        decision_conflict = hit.decision_conflict or (
            relationship == DecisionRelationship.POSSIBLE_CONFLICT.value
        )
        meta: dict[str, Any] = {}
        if hit.frozen_hit:
            meta["frozen_related"] = True
            if decision_conflict:
                meta["conflict_strength"] = "elevated"

        return DecisionProposal(
            action=action,
            candidate=candidate_dict_from_request(request),
            related_decisions=list(hit.related_ids),
            relationship=relationship,
            reason_code=hit.reason_code,
            decision_conflict=decision_conflict,
            metadata=meta,
        )

    def _model_assist(
        self,
        new_statement: str,
        existing_statement: str,
        *,
        related_id: str,
        frozen: bool = False,
    ) -> tuple[ConflictHit | None, bool]:
        """At most one classification call. Returns (hit, generation_used)."""
        if self._model_classifier is not None:
            raw = self._model_classifier(new_statement, existing_statement)
            return (
                self._hit_from_model_json(
                    raw, existing_id_hint=related_id, frozen=frozen
                ),
                True,
            )

        provider = self._ollama()
        if provider is None:
            return None, False

        prompt = (
            f"NEW decision statement:\n{new_statement}\n\n"
            f"EXISTING ACTIVE decision:\n{existing_statement}\n"
        )
        try:
            resp = provider.generate(
                ModelRequest(
                    prompt=prompt,
                    system=DECISION_RELATIONSHIP_INSTRUCTION,
                    max_tokens=200,
                    temperature=0.0,
                    metadata={"decision_analyze": True},
                )
            )
        except (ProviderError, OSError, TimeoutError):
            return None, True

        text = (resp.text or "").strip()
        parsed = _extract_json_obj(text)
        if not parsed:
            return None, True
        return (
            self._hit_from_model_json(
                parsed, existing_id_hint=related_id, frozen=frozen
            ),
            True,
        )

    def _hit_from_model_json(
        self,
        raw: dict[str, Any],
        *,
        existing_id_hint: str | None,
        frozen: bool = False,
    ) -> ConflictHit | None:
        rel_raw = str(raw.get("relationship") or "").strip().lower()
        relationship = _MODEL_REL_MAP.get(rel_raw)
        if not relationship:
            return None
        reason = str(raw.get("reason_code") or "model_assist").strip()[:80]
        try:
            conf = float(raw.get("confidence", 0.6))
        except (TypeError, ValueError):
            conf = 0.6
        conf = max(0.0, min(1.0, conf))

        related: list[str] = []
        if existing_id_hint:
            related = [existing_id_hint]

        if relationship == DecisionRelationship.DUPLICATE.value:
            return ConflictHit(
                relationship,
                DecisionAction.REJECT_AS_DUPLICATE.value,
                related,
                reason,
                False,
                conf,
                frozen_hit=frozen,
            )
        if relationship == DecisionRelationship.POSSIBLE_SUPERSESSION.value:
            return ConflictHit(
                relationship,
                DecisionAction.SUPERSEDE.value,
                related,
                reason,
                False,
                conf,
                frozen_hit=frozen,
            )
        if relationship == DecisionRelationship.POSSIBLE_CONFLICT.value:
            reason_out = (
                "conflicts_with_frozen_decision"
                if frozen
                else (reason or "conflicts_with_active_decision")
            )
            return ConflictHit(
                relationship,
                DecisionAction.FLAG_CONFLICT.value,
                related,
                reason_out,
                True,
                conf,
                frozen_hit=frozen,
            )
        if relationship == DecisionRelationship.UNRELATED.value:
            return ConflictHit(
                DecisionRelationship.NEW.value,
                DecisionAction.CREATE.value,
                [],
                reason,
                False,
                conf,
                frozen_hit=frozen,
            )
        return ConflictHit(
            DecisionRelationship.COMPATIBLE.value,
            DecisionAction.CREATE.value,
            related,
            reason,
            False,
            conf,
            frozen_hit=frozen,
        )

    def _ollama(self) -> OllamaProvider | None:
        for p in default_providers():
            if isinstance(p, OllamaProvider) and any(
                c.available for c in p.capabilities()
            ):
                return p
        return None


def _extract_json_obj(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[^{}]*\}", text, re.S)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
