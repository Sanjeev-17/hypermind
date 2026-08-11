"""Active decision resolution and historical query helpers."""

from __future__ import annotations

import re
from pathlib import Path

from hypermind.decisions.parse import load_decision_log, parse_decision_log
from hypermind.decisions.types import DecisionRecord, DecisionScope, DecisionStatus

_HISTORY_CUES = (
    "what did we decide before",
    "what decision did",
    "did .* replace",
    "how did our .* change",
    "how did .* strategy change",
    "decision history",
    "historical decision",
    "previously decided",
    "before we",
    "superseded by",
    "what replaced",
)


def is_historical_query(text: str) -> bool:
    """True when the user asks for history / comparison / prior decisions."""
    lowered = (text or "").lower()
    if not lowered:
        return False
    if re.search(r"before\s+d-\d+", lowered):
        return True
    if re.search(r"d-\d+\s+replace", lowered):
        return True
    if "superseded" in lowered or "history of" in lowered:
        return True
    for cue in _HISTORY_CUES:
        if re.search(cue, lowered):
            return True
    return False


class DecisionResolver:
    """
    Deterministic resolver over parsed DecisionRecords.

    ACTIVE is authoritative. SUPERSEDED is excluded from default context.
    Broken supersession links never crash retrieval.
    """

    def __init__(self, records: list[DecisionRecord] | None = None) -> None:
        self._records: list[DecisionRecord] = list(records or [])
        self._by_id: dict[str, DecisionRecord] = {}
        self._reindex()

    def _reindex(self) -> None:
        self._by_id = {r.id.upper(): r for r in self._records}

    @classmethod
    def from_markdown(
        cls,
        raw: str,
        *,
        source_path: str = "portfolio-os/governance/Decision_Log.md",
        default_project: str | None = "portfolio",
    ) -> DecisionResolver:
        return cls(
            parse_decision_log(
                raw, source_path=source_path, default_project=default_project
            )
        )

    @classmethod
    def from_path(
        cls,
        path: Path,
        *,
        default_project: str | None = "portfolio",
    ) -> DecisionResolver:
        return cls(load_decision_log(path, default_project=default_project))

    @property
    def records(self) -> list[DecisionRecord]:
        return list(self._records)

    def get(self, decision_id: str) -> DecisionRecord | None:
        if not decision_id:
            return None
        return self._by_id.get(decision_id.strip().upper())

    def get_active_decisions(
        self,
        scope: str | None = None,
        project: str | None = None,
    ) -> list[DecisionRecord]:
        """Return ACTIVE decisions only; scope/project filter when provided."""
        out: list[DecisionRecord] = []
        for rec in self._records:
            if rec.status != DecisionStatus.ACTIVE.value:
                continue
            if not self._scope_match(rec, scope=scope, project=project):
                continue
            # Broken superseded_by on an ACTIVE row: still treat as ACTIVE
            # (human may have left inconsistent links)
            out.append(rec)
        return out

    def get_inspectable(
        self,
        *,
        include_superseded: bool = False,
        include_rejected: bool = False,
        include_archived: bool = False,
        scope: str | None = None,
        project: str | None = None,
    ) -> list[DecisionRecord]:
        allowed = {DecisionStatus.ACTIVE.value}
        if include_superseded:
            allowed.add(DecisionStatus.SUPERSEDED.value)
        if include_rejected:
            allowed.add(DecisionStatus.REJECTED.value)
        if include_archived:
            allowed.add(DecisionStatus.ARCHIVED.value)
        out: list[DecisionRecord] = []
        for rec in self._records:
            if rec.status not in allowed:
                continue
            if not self._scope_match(rec, scope=scope, project=project):
                continue
            out.append(rec)
        return out

    def resolve_supersession_chain(self, decision_id: str) -> list[DecisionRecord]:
        """Walk supersedes / superseded_by safely; stop on cycles or missing links."""
        start = self.get(decision_id)
        if start is None:
            return []
        chain: list[DecisionRecord] = [start]
        seen = {start.id.upper()}
        # Walk backward via supersedes list
        queue = list(start.supersedes)
        while queue:
            nid = queue.pop(0)
            if not nid or nid.upper() in seen:
                continue
            seen.add(nid.upper())
            rec = self.get(nid)
            if rec is None:
                continue  # broken link — skip
            chain.append(rec)
            queue.extend(rec.supersedes)
        # Walk forward via superseded_by
        cur = start.superseded_by
        hops = 0
        while cur and hops < 32:
            hops += 1
            if cur.upper() in seen:
                break
            seen.add(cur.upper())
            rec = self.get(cur)
            if rec is None:
                break
            chain.append(rec)
            cur = rec.superseded_by
        return chain

    def _scope_match(
        self,
        rec: DecisionRecord,
        *,
        scope: str | None,
        project: str | None,
    ) -> bool:
        if scope is None and project is None:
            return True
        if scope == DecisionScope.GLOBAL.value:
            return rec.scope == DecisionScope.GLOBAL.value
        if scope == DecisionScope.PROJECT.value or project:
            # Project filter: include matching project + global decisions
            if rec.scope == DecisionScope.GLOBAL.value:
                return True
            if project is None:
                return rec.scope == DecisionScope.PROJECT.value
            return (rec.project or "").lower() == project.lower()
        if scope and rec.scope != scope:
            return False
        return True
