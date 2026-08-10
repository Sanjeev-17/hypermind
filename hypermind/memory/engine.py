"""Memory candidate engine — one generation, no persistence."""

from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

from hypermind.agents import AgentRegistry
from hypermind.context import ContextBuilder
from hypermind.memory.compare import compare_to_existing
from hypermind.memory.instruction import MEMORY_ANALYSIS_INSTRUCTION
from hypermind.memory.parse import parse_candidates_payload
from hypermind.memory.sensitivity import classify_sensitivity, contains_secret_like
from hypermind.memory.types import (
    MAX_CANDIDATES_DEFAULT,
    MemoryProposeRequest,
    MemoryProposeResult,
    MemoryRelationship,
    MemoryScope,
)
from hypermind.models import ModelProvider, ModelRequest, ProviderError
from hypermind.models.adapters import OllamaProvider, default_providers
from hypermind.models.router import ModelRouter
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest


class MemoryCandidateEngine:
    """
    Propose structured memory candidates. Never writes memory or files.
    Exactly one model generation per propose() call when a provider is available.
    """

    def __init__(
        self,
        *,
        router: IntelligenceRouter | None = None,
        context: ContextBuilder | None = None,
        agents: AgentRegistry | None = None,
        allow_stub: bool = False,
        max_output_tokens: int = 700,
        temperature: float = 0.1,
    ) -> None:
        self.router = router or IntelligenceRouter(persist_trace=False)
        self.context = context or self.router.context
        self.agents = agents or AgentRegistry()
        self.allow_stub = allow_stub
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

    def propose(self, request: MemoryProposeRequest) -> MemoryProposeResult:
        started = time.perf_counter()
        request_id = str(uuid4())
        allowed_sources = set(request.source_refs)

        # Early secret rejection on raw input — do not propose storing secrets.
        if contains_secret_like(request.text):
            return MemoryProposeResult(
                ok=True,
                request_id=request_id,
                candidates=[],
                suppressed=[
                    {
                        "reason_code": "secret_like_content",
                        "detail": "Input matched secret-like patterns; no candidates proposed.",
                    }
                ],
                trace=self._trace_base(
                    request_id,
                    generation_count=0,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    status="completed",
                    extra={
                        "candidate_count": 0,
                        "duplicate_count": 0,
                        "conflict_count": 0,
                        "suppressed_secret": True,
                    },
                ),
            )

        hm_request = HyperMindRequest(
            raw_input=request.text,
            id=request_id,
            intent="memory",
            project=request.project,
            context_refs=list(request.source_refs),
            metadata={"memory_propose": True},
        )

        agent = self.agents.get("knowledge_curator")
        pack = self.context.build(
            hm_request,
            agent,
            intent="memory",
            context_profile="memory",
        )
        for item in pack.items:
            allowed_sources.add(item.source_ref)

        # Route for model selection only (tools unused)
        route = self.router.route(
            hm_request,
            complexity="simple",
            prefer_local=True,
        )
        # Force curated agent identity in trace even if router picked another
        provider_name = route.model.provider
        model_name = route.model.model
        provider = self._provider_named(provider_name)

        if provider is None or (
            provider_name not in {"ollama"}
            and not (self.allow_stub and provider_name == "stub")
        ):
            # Try ollama explicitly
            ollama = self._ollama()
            if ollama is not None and any(c.available for c in ollama.capabilities()):
                provider = ollama
                provider_name = "ollama"
                model_name = ollama.resolve_model() or model_name
            elif self.allow_stub:
                provider = self._provider_named("stub")
                provider_name = "stub"
                model_name = "stub-local"
            else:
                return MemoryProposeResult(
                    ok=False,
                    request_id=request_id,
                    error={
                        "code": "PROVIDER_UNAVAILABLE",
                        "message": "No executable provider available for memory propose.",
                    },
                    trace=self._trace_base(
                        request_id,
                        generation_count=0,
                        duration_ms=int((time.perf_counter() - started) * 1000),
                        status="failed",
                        provider=provider_name,
                        model=model_name,
                        context_items=len(pack.items),
                        context_chars=pack.total_chars,
                        extra={"context_profile": pack.context_profile},
                    ),
                )

        prompt = self._user_prompt(request, allowed_sources=sorted(allowed_sources))
        model_request = ModelRequest(
            prompt=prompt,
            system=MEMORY_ANALYSIS_INSTRUCTION,
            context=pack.prompt_blocks(),
            max_tokens=self.max_output_tokens,
            temperature=self.temperature,
            metadata={"request_id": request_id, "mode": "memory_propose"},
        )

        try:
            if isinstance(provider, OllamaProvider):
                response = provider.generate(model_request, model_name)
            else:
                response = provider.generate(model_request, model_name)
        except ProviderError as exc:
            return MemoryProposeResult(
                ok=False,
                request_id=request_id,
                error={"code": exc.code.upper(), "message": exc.message[:300]},
                trace=self._trace_base(
                    request_id,
                    generation_count=0,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    status="failed",
                    provider=provider_name,
                    model=model_name,
                    context_items=len(pack.items),
                    context_chars=pack.total_chars,
                    extra={"context_profile": pack.context_profile},
                ),
            )

        try:
            accepted, parse_notes = parse_candidates_payload(
                response.text,
                allowed_sources=allowed_sources,
                max_candidates=request.max_candidates or MAX_CANDIDATES_DEFAULT,
            )
        except ValueError as exc:
            return MemoryProposeResult(
                ok=False,
                request_id=request_id,
                error={
                    "code": "MALFORMED_OUTPUT",
                    "message": str(exc)[:300],
                },
                trace=self._trace_base(
                    request_id,
                    generation_count=1,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    status="failed",
                    provider=provider_name,
                    model=model_name,
                    context_items=len(pack.items),
                    context_chars=pack.total_chars,
                    extra={"context_profile": pack.context_profile},
                ),
            )

        proposals = []
        suppressed: list[dict[str, Any]] = []
        duplicate_count = 0
        conflict_count = 0

        for cand in accepted:
            # Deterministic sensitivity override (policy > model)
            policy_sens = classify_sensitivity(cand.statement)
            if policy_sens == "restricted" or cand.sensitivity == "restricted":
                cand.sensitivity = "restricted"
                cand.requires_explicit_sensitive_approval = True
            elif policy_sens == "personal" and cand.sensitivity == "normal":
                cand.sensitivity = "personal"

            if contains_secret_like(cand.statement):
                suppressed.append(
                    {
                        "reason_code": "secret_like_content",
                        "category": cand.category,
                        # Do not echo secret statement
                    }
                )
                continue

            # Prefer not to persist pure session fluff unless model gave strong reason
            if (
                cand.scope == MemoryScope.SESSION.value
                and cand.confidence < 0.85
                and "session" not in cand.reason_code
            ):
                suppressed.append(
                    {
                        "reason_code": "session_scope_low_confidence",
                        "category": cand.category,
                    }
                )
                continue

            hit = compare_to_existing(cand.statement, pack.items)
            cand.relationship = hit.relationship
            cand.existing_ref = hit.existing_ref
            cand.metadata["compare_reason"] = hit.reason_code

            if hit.relationship == MemoryRelationship.DUPLICATE.value:
                duplicate_count += 1
                suppressed.append(
                    {
                        "reason_code": "duplicate",
                        "existing_ref": hit.existing_ref,
                        "compare_reason": hit.reason_code,
                        "category": cand.category,
                    }
                )
                continue

            if hit.relationship == MemoryRelationship.POSSIBLE_CONFLICT.value:
                conflict_count += 1

            proposals.append(cand)

        duration_ms = int((time.perf_counter() - started) * 1000)
        return MemoryProposeResult(
            ok=True,
            request_id=request_id,
            candidates=proposals[: request.max_candidates],
            suppressed=suppressed + [
                {"reason_code": n.get("reason_code"), "index": n.get("index")}
                for n in parse_notes
            ],
            trace=self._trace_base(
                request_id,
                generation_count=1,
                duration_ms=duration_ms,
                status="completed",
                provider=provider_name,
                model=model_name,
                context_items=len(pack.items),
                context_chars=pack.total_chars,
                extra={
                    "context_profile": pack.context_profile or "memory",
                    "candidate_count": len(proposals),
                    "duplicate_count": duplicate_count,
                    "conflict_count": conflict_count,
                    "intent": "memory",
                    "agent": "knowledge_curator",
                    "route_reason": route.model.reason_code,
                },
            ),
        )

    def _user_prompt(
        self, request: MemoryProposeRequest, *, allowed_sources: list[str]
    ) -> str:
        project = request.project or "(none)"
        refs = ", ".join(allowed_sources)
        return (
            "MEMORY CANDIDATE INPUT\n"
            f"project: {project}\n"
            f"allowed_source_refs: [{refs}]\n\n"
            "USER TEXT:\n"
            f"{request.text}\n"
        )

    def _provider_named(self, name: str) -> ModelProvider | None:
        for provider in self.router.models.providers:
            if provider.name == name:
                return provider
        return None

    def _ollama(self) -> OllamaProvider | None:
        for provider in self.router.models.providers:
            if isinstance(provider, OllamaProvider):
                return provider
        return None

    def _trace_base(
        self,
        request_id: str,
        *,
        generation_count: int,
        duration_ms: int,
        status: str,
        provider: str = "unknown",
        model: str = "unknown",
        context_items: int = 0,
        context_chars: int = 0,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace = {
            "request_id": request_id,
            "intent": "memory",
            "agent": "knowledge_curator",
            "provider": provider,
            "model": model,
            "context_profile": "memory",
            "context_items": context_items,
            "context_chars": context_chars,
            "generation_count": generation_count,
            "duration_ms": duration_ms,
            "status": status,
            # Explicit non-persistence guarantee in operational metadata
            "memory_written": False,
        }
        if extra:
            trace.update(extra)
        return trace
