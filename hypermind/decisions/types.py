"""Provider-neutral formal decision types — analysis only, never durable writes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class DecisionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class DecisionScope(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"


class DecisionRelationship(str, Enum):
    NEW = "NEW"
    DUPLICATE = "DUPLICATE"
    COMPATIBLE = "COMPATIBLE"
    POSSIBLE_SUPERSESSION = "POSSIBLE_SUPERSESSION"
    POSSIBLE_CONFLICT = "POSSIBLE_CONFLICT"
    UNRELATED = "UNRELATED"


class DecisionAction(str, Enum):
    CREATE = "CREATE"
    SUPERSEDE = "SUPERSEDE"
    REJECT_AS_DUPLICATE = "REJECT_AS_DUPLICATE"
    FLAG_CONFLICT = "FLAG_CONFLICT"


STATUSES = frozenset(s.value for s in DecisionStatus)
SCOPES = frozenset(s.value for s in DecisionScope)
RELATIONSHIPS = frozenset(r.value for r in DecisionRelationship)
ACTIONS = frozenset(a.value for a in DecisionAction)

# Map Decision Log prose statuses → canonical
LOG_STATUS_MAP = {
    "accepted": DecisionStatus.ACTIVE.value,
    "active": DecisionStatus.ACTIVE.value,
    "superseded": DecisionStatus.SUPERSEDED.value,
    "rejected": DecisionStatus.REJECTED.value,
    "archived": DecisionStatus.ARCHIVED.value,
}


@dataclass
class DecisionRecord:
    """Canonical formal decision — identity, scope, status, provenance."""

    id: str
    title: str
    statement: str
    scope: str
    project: str | None
    status: str
    effective_at: str | None = None
    supersedes: list[str] = field(default_factory=list)
    superseded_by: str | None = None
    rationale: str | None = None
    source_refs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def frozen(self) -> bool:
        return bool(self.metadata.get("frozen"))

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "statement": self.statement,
            "scope": self.scope,
            "project": self.project,
            "status": self.status,
            "effective_at": self.effective_at,
            "supersedes": list(self.supersedes),
            "superseded_by": self.superseded_by,
            "rationale": self.rationale,
            "source_refs": list(self.source_refs),
            "metadata": dict(self.metadata),
        }

    def retrieval_blob(self) -> str:
        parts = [self.id, self.title, self.statement]
        if self.rationale:
            parts.append(self.rationale)
        return "\n".join(p for p in parts if p)


@dataclass
class DecisionProposal:
    """Proposed human-review action — HyperMind never executes it."""

    action: str
    candidate: dict[str, Any]
    related_decisions: list[str] = field(default_factory=list)
    relationship: str = DecisionRelationship.NEW.value
    reason_code: str = "unspecified"
    decision_conflict: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "action": self.action,
            "candidate": dict(self.candidate),
            "related_decisions": list(self.related_decisions),
            "relationship": self.relationship,
            "reason_code": self.reason_code,
            "decision_conflict": self.decision_conflict,
        }
        if self.decision_conflict:
            out["decision_refs"] = list(self.related_decisions)
        if self.metadata:
            out["metadata"] = dict(self.metadata)
        return out


@dataclass
class DecisionAnalyzeRequest:
    statement: str
    project: str | None = None
    scope: str = DecisionScope.PROJECT.value
    source_refs: list[str] = field(default_factory=lambda: ["input:user"])
    title: str | None = None
    candidate: dict[str, Any] | None = None
    allow_model_assist: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Bridge Phase 6 DECISION_CANDIDATE without regenerating text
        if self.candidate and isinstance(self.candidate, dict):
            stmt = str(self.candidate.get("statement") or "").strip()
            if stmt:
                self.statement = stmt
            if self.candidate.get("project") and not self.project:
                self.project = str(self.candidate["project"]).strip() or None
            cand_scope = str(self.candidate.get("scope") or "").lower().strip()
            if cand_scope in SCOPES:
                self.scope = cand_scope
            refs = self.candidate.get("source_refs")
            if isinstance(refs, list) and refs and self.source_refs == ["input:user"]:
                self.source_refs = [str(r).strip() for r in refs if str(r).strip()]
            if not self.title and self.candidate.get("statement"):
                # keep title optional; analysis uses statement
                pass

        self.statement = (self.statement or "").strip()
        if not self.statement:
            raise ValueError("statement must be non-empty")
        self.scope = (self.scope or DecisionScope.PROJECT.value).lower().strip()
        if self.scope not in SCOPES:
            raise ValueError(f"invalid scope: {self.scope}")
        if self.scope == DecisionScope.PROJECT.value and not self.project:
            # allow missing project — treat as portfolio default for portfolio-os log
            pass
        if not self.source_refs:
            self.source_refs = ["input:user"]


@dataclass
class DecisionAnalyzeResult:
    ok: bool
    request_id: str
    proposal: DecisionProposal | None = None
    trace: dict[str, Any] = field(default_factory=dict)
    error: dict[str, str] | None = None

    def to_envelope(self) -> dict[str, Any]:
        if not self.ok:
            return {
                "ok": False,
                "request_id": self.request_id,
                "error": self.error
                or {"code": "UNKNOWN", "message": "decision analysis failed"},
            }
        assert self.proposal is not None
        return {
            "ok": True,
            "request_id": self.request_id,
            "proposal": self.proposal.to_public_dict(),
            "trace": dict(self.trace),
        }


def new_request_id() -> str:
    return str(uuid4())


def candidate_dict_from_request(req: DecisionAnalyzeRequest) -> dict[str, Any]:
    """Structured candidate payload for DecisionProposal (not a DecisionRecord)."""
    if req.candidate and isinstance(req.candidate, dict):
        base = dict(req.candidate)
        base.setdefault("statement", req.statement)
        base.setdefault("project", req.project)
        base.setdefault("scope", req.scope)
        base.setdefault("source_refs", list(req.source_refs))
        base.setdefault("category", "DECISION_CANDIDATE")
        return base
    return {
        "category": "DECISION_CANDIDATE",
        "statement": req.statement,
        "title": req.title,
        "scope": req.scope,
        "project": req.project,
        "source_refs": list(req.source_refs),
        "status": "proposed",
    }
