"""Controlled memory candidate types — proposal only, never durable writes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class MemoryCategory(str, Enum):
    FACT = "FACT"
    PREFERENCE = "PREFERENCE"
    GOAL = "GOAL"
    CONSTRAINT = "CONSTRAINT"
    CURRENT_STATE = "CURRENT_STATE"
    PROJECT_CONTEXT = "PROJECT_CONTEXT"
    DECISION_CANDIDATE = "DECISION_CANDIDATE"


class MemoryScope(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"


class MemorySensitivity(str, Enum):
    NORMAL = "normal"
    PERSONAL = "personal"
    RESTRICTED = "restricted"


class MemoryRelationship(str, Enum):
    NEW = "NEW"
    DUPLICATE = "DUPLICATE"
    POSSIBLE_UPDATE = "POSSIBLE_UPDATE"
    POSSIBLE_CONFLICT = "POSSIBLE_CONFLICT"


CATEGORIES = frozenset(c.value for c in MemoryCategory)
SCOPES = frozenset(s.value for s in MemoryScope)
SENSITIVITIES = frozenset(s.value for s in MemorySensitivity)
RELATIONSHIPS = frozenset(r.value for r in MemoryRelationship)

MAX_CANDIDATES_DEFAULT = 5


@dataclass
class MemoryCandidate:
    """Temporary proposal — not a durable memory record."""

    id: str
    category: str
    statement: str
    scope: str
    confidence: float
    reason_code: str
    sensitivity: str
    relationship: str = MemoryRelationship.NEW.value
    project: str | None = None
    source_refs: list[str] = field(default_factory=list)
    existing_ref: str | None = None
    status: str = "proposed"
    requires_explicit_sensitive_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "statement": self.statement,
            "scope": self.scope,
            "project": self.project,
            "confidence": self.confidence,
            "reason_code": self.reason_code,
            "sensitivity": self.sensitivity,
            "relationship": self.relationship,
            "existing_ref": self.existing_ref,
            "source_refs": list(self.source_refs),
            "status": self.status,
            "requires_explicit_sensitive_approval": self.requires_explicit_sensitive_approval,
        }


@dataclass
class MemoryProposeRequest:
    text: str
    project: str | None = None
    source_refs: list[str] = field(default_factory=lambda: ["input:user"])
    max_candidates: int = MAX_CANDIDATES_DEFAULT
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.text = (self.text or "").strip()
        if not self.text:
            raise ValueError("text must be non-empty")
        if self.max_candidates < 0 or self.max_candidates > 10:
            raise ValueError("max_candidates must be 0–10")
        if not self.source_refs:
            self.source_refs = ["input:user"]


@dataclass
class MemoryProposeResult:
    ok: bool
    request_id: str
    candidates: list[MemoryCandidate] = field(default_factory=list)
    suppressed: list[dict[str, Any]] = field(default_factory=list)
    trace: dict[str, Any] = field(default_factory=dict)
    error: dict[str, str] | None = None

    def to_envelope(self) -> dict[str, Any]:
        if not self.ok:
            return {
                "ok": False,
                "request_id": self.request_id,
                "error": self.error
                or {"code": "UNKNOWN", "message": "proposal failed"},
            }
        return {
            "ok": True,
            "request_id": self.request_id,
            "candidates": [c.to_public_dict() for c in self.candidates],
            "suppressed": list(self.suppressed),
            "trace": dict(self.trace),
        }


def new_proposal_id() -> str:
    return f"prop_{uuid4().hex[:12]}"


def candidate_from_raw(raw: dict[str, Any], *, allowed_sources: set[str]) -> MemoryCandidate:
    """Validate one model-emitted candidate dict into MemoryCandidate."""
    category = str(raw.get("category") or "").upper().strip()
    if category not in CATEGORIES:
        raise ValueError(f"invalid category: {category}")
    statement = str(raw.get("statement") or "").strip()
    if not statement or len(statement) > 500:
        raise ValueError("statement must be 1–500 chars")
    scope = str(raw.get("scope") or "").lower().strip()
    if scope not in SCOPES:
        raise ValueError(f"invalid scope: {scope}")
    project = raw.get("project")
    if project is not None:
        project = str(project).strip() or None
    if scope == MemoryScope.PROJECT.value and not project:
        raise ValueError("project scope requires project")
    try:
        confidence = float(raw.get("confidence", 0.5))
    except (TypeError, ValueError) as exc:
        raise ValueError("confidence must be a float") from exc
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be 0–1")
    reason_code = str(raw.get("reason_code") or "unspecified").strip()[:80]
    sensitivity = str(raw.get("sensitivity") or MemorySensitivity.NORMAL.value).lower()
    if sensitivity not in SENSITIVITIES:
        raise ValueError(f"invalid sensitivity: {sensitivity}")
    refs = raw.get("source_refs") or []
    if not isinstance(refs, list) or not refs:
        raise ValueError("source_refs required")
    source_refs: list[str] = []
    for ref in refs:
        r = str(ref).strip()
        if not r:
            continue
        if r not in allowed_sources:
            raise ValueError(f"fabricated source ref: {r}")
        source_refs.append(r)
    if not source_refs:
        raise ValueError("source_refs required")

    return MemoryCandidate(
        id=new_proposal_id(),
        category=category,
        statement=statement,
        scope=scope,
        project=project,
        confidence=confidence,
        reason_code=reason_code,
        sensitivity=sensitivity,
        source_refs=source_refs,
        relationship=MemoryRelationship.NEW.value,
        requires_explicit_sensitive_approval=sensitivity
        == MemorySensitivity.RESTRICTED.value,
        metadata={},
    )
