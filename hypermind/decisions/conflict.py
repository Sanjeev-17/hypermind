"""Deterministic decision conflict / supersession / duplicate detection."""

from __future__ import annotations

from dataclasses import dataclass

from hypermind.decisions.types import (
    DecisionAction,
    DecisionRecord,
    DecisionRelationship,
    DecisionScope,
)
from hypermind.memory.normalize import normalize_statement, token_set

_SUPERSESSION_CUES = (
    "instead",
    "replace",
    "replaces",
    "replacing",
    "supersede",
    "supersedes",
    "override",
    "from now on",
    "going forward",
    "henceforth",
    "switch to",
    "migrate to",
    "prefer cloud",
    "cloud-first",
    "cloud first",
    "no longer",
    "retire",
)

_CONFLICT_CUES = (
    "without",
    "unfreeze",
    "unlock",
    "ignore",
    "never",
    "do not",
    "don't",
    "abandon",
    "cancel",
    "restructure",
    "change without",
    "bypass",
)

_NEGATION = ("not", "never", "no longer", "don't", "do not", "without")

# Topic clusters for stronger deterministic hits
_TOPIC_CLUSTERS: list[tuple[str, frozenset[str]]] = [
    (
        "model_routing",
        frozenset(
            {
                "local",
                "localfirst",
                "local-first",
                "ollama",
                "cloud",
                "cloudfirst",
                "cloud-first",
                "routing",
                "model",
                "models",
                "provider",
            }
        ),
    ),
    (
        "freeze_lock",
        frozenset(
            {
                "freeze",
                "frozen",
                "lock",
                "locked",
                "version",
                "bump",
                "v1",
                "vault",
                "blueprint",
                "portfolio",
            }
        ),
    ),
    (
        "writing_standard",
        frozenset({"writing", "standard", "editorial", "tone", "voice"}),
    ),
]


@dataclass(frozen=True)
class ConflictHit:
    relationship: str
    action: str
    related_ids: list[str]
    reason_code: str
    decision_conflict: bool
    confidence: float  # 0–1; <0.55 → model assist eligible
    frozen_hit: bool = False


def analyze_against_active(
    statement: str,
    active: list[DecisionRecord],
    *,
    scope: str = DecisionScope.PROJECT.value,
    project: str | None = None,
) -> ConflictHit:
    """
    Deterministic relationship vs ACTIVE decisions.

    Does not use embeddings. Ambiguous mid-overlap → low confidence for model assist.
    """
    cand_norm = normalize_statement(statement)
    if not cand_norm:
        return ConflictHit(
            DecisionRelationship.NEW.value,
            DecisionAction.CREATE.value,
            [],
            "empty_statement",
            False,
            1.0,
        )

    cand_tokens = token_set(statement)
    best: ConflictHit | None = None

    scoped = [
        d
        for d in active
        if _in_scope(d, scope=scope, project=project)
    ]

    for dec in scoped:
        hit = _compare_one(cand_norm, cand_tokens, statement, dec)
        if hit is None:
            continue
        if best is None or _rank(hit) > _rank(best):
            best = hit

    if best is None:
        return ConflictHit(
            DecisionRelationship.NEW.value,
            DecisionAction.CREATE.value,
            [],
            "no_overlapping_active_decision",
            False,
            0.9,
        )
    return best


def _in_scope(dec: DecisionRecord, *, scope: str, project: str | None) -> bool:
    # Shared Decision Log: do not drop ACTIVE rows solely for project mismatch.
    # Explicit global-only analyze still filters to global records.
    if scope == DecisionScope.GLOBAL.value:
        return dec.scope == DecisionScope.GLOBAL.value
    return True


def _compare_one(
    cand_norm: str,
    cand_tokens: set[str],
    statement: str,
    dec: DecisionRecord,
) -> ConflictHit | None:
    exist_norm = normalize_statement(dec.statement)
    title_norm = normalize_statement(dec.title)
    blob = normalize_statement(dec.retrieval_blob())
    exist_tokens = token_set(dec.statement) | token_set(dec.title)

    # Exact / containment → duplicate
    if cand_norm and (
        cand_norm == exist_norm
        or cand_norm == title_norm
        or cand_norm in blob
        or exist_norm in cand_norm
    ):
        return ConflictHit(
            DecisionRelationship.DUPLICATE.value,
            DecisionAction.REJECT_AS_DUPLICATE.value,
            [dec.id],
            "exact_or_contained_match",
            False,
            0.95,
            frozen_hit=dec.frozen,
        )

    if not cand_tokens or not exist_tokens:
        return None

    overlap = cand_tokens & exist_tokens
    union = cand_tokens | exist_tokens
    jaccard = len(overlap) / max(1, len(union))
    topic = _shared_topic(cand_tokens | set(cand_norm.split()), exist_tokens)

    explicit_replace = any(c in cand_norm for c in _SUPERSESSION_CUES)
    conflict_cue = any(c in cand_norm for c in _CONFLICT_CUES)
    polarity_flip = _polarity_conflict(cand_norm, exist_norm, overlap)

    # High overlap duplicate
    if jaccard >= 0.72 and not explicit_replace and not polarity_flip:
        return ConflictHit(
            DecisionRelationship.DUPLICATE.value,
            DecisionAction.REJECT_AS_DUPLICATE.value,
            [dec.id],
            "high_token_overlap",
            False,
            0.9,
            frozen_hit=dec.frozen,
        )

    # Supersession: same scope/topic + replacement language
    if (topic or jaccard >= 0.28) and explicit_replace:
        return ConflictHit(
            DecisionRelationship.POSSIBLE_SUPERSESSION.value,
            DecisionAction.SUPERSEDE.value,
            [dec.id],
            "same_scope_explicit_replacement",
            False,
            0.85,
            frozen_hit=dec.frozen,
        )

    # Direct contradiction / conflict
    if (topic or jaccard >= 0.28) and (conflict_cue or polarity_flip):
        reason = (
            "conflicts_with_frozen_decision"
            if dec.frozen
            else "conflicts_with_active_decision"
        )
        return ConflictHit(
            DecisionRelationship.POSSIBLE_CONFLICT.value,
            DecisionAction.FLAG_CONFLICT.value,
            [dec.id],
            reason,
            True,
            0.88 if (dec.frozen or polarity_flip) else 0.75,
            frozen_hit=dec.frozen,
        )

    # Local-first vs cloud-first special case (portfolio/hypermind routing)
    if topic == "model_routing" and _routing_polarity(cand_norm, exist_norm):
        if explicit_replace:
            return ConflictHit(
                DecisionRelationship.POSSIBLE_SUPERSESSION.value,
                DecisionAction.SUPERSEDE.value,
                [dec.id],
                "same_scope_explicit_replacement",
                False,
                0.86,
                frozen_hit=dec.frozen,
            )
        return ConflictHit(
            DecisionRelationship.POSSIBLE_CONFLICT.value,
            DecisionAction.FLAG_CONFLICT.value,
            [dec.id],
            "conflicts_with_active_decision",
            True,
            0.8,
            frozen_hit=dec.frozen,
        )

    # Mid overlap without clear cue → ambiguous (model assist)
    if jaccard >= 0.35 and len(overlap) >= 3:
        return ConflictHit(
            DecisionRelationship.COMPATIBLE.value,
            DecisionAction.CREATE.value,
            [dec.id],
            "overlapping_subject_ambiguous",
            False,
            0.4,
            frozen_hit=dec.frozen,
        )

    if topic and jaccard >= 0.2:
        return ConflictHit(
            DecisionRelationship.COMPATIBLE.value,
            DecisionAction.CREATE.value,
            [dec.id],
            "shared_topic_weak_overlap",
            False,
            0.45,
            frozen_hit=dec.frozen,
        )

    return None


def project_hint(statement: str) -> str | None:
    norm = normalize_statement(statement)
    for name in ("portfolio", "hypermind", "mission control"):
        if name in norm:
            return "portfolio" if name != "hypermind" else "hypermind"
    return None


def _shared_topic(a: set[str], b: set[str]) -> str | None:
    # normalize hyphens out of tokens already via normalize
    flat_a = {t.replace("-", "") for t in a}
    flat_b = {t.replace("-", "") for t in b}
    for name, cluster in _TOPIC_CLUSTERS:
        ca = {c.replace("-", "") for c in cluster}
        if len(flat_a & ca) >= 2 and len(flat_b & ca) >= 2:
            return name
    return None


def _routing_polarity(cand: str, exist: str) -> bool:
    cand_local = "local" in cand and ("first" in cand or "prefer" in cand or "default" in cand)
    cand_cloud = "cloud" in cand and ("first" in cand or "prefer" in cand or "default" in cand)
    exist_local = "local" in exist and ("first" in exist or "prefer" in exist or "ollama" in exist)
    exist_cloud = "cloud" in exist and ("first" in exist or "prefer" in exist)
    return (cand_cloud and exist_local) or (cand_local and exist_cloud)


def _polarity_conflict(cand: str, exist: str, overlap: set[str]) -> bool:
    if len(overlap) < 2:
        return False
    cand_neg = any(n in cand for n in _NEGATION)
    exist_neg = any(n in exist for n in _NEGATION)
    return cand_neg != exist_neg and len(overlap) >= 3


def _rank(hit: ConflictHit) -> tuple:
    order = {
        DecisionRelationship.DUPLICATE.value: 5,
        DecisionRelationship.POSSIBLE_CONFLICT.value: 4,
        DecisionRelationship.POSSIBLE_SUPERSESSION.value: 3,
        DecisionRelationship.COMPATIBLE.value: 2,
        DecisionRelationship.UNRELATED.value: 1,
        DecisionRelationship.NEW.value: 0,
    }
    return (order.get(hit.relationship, 0), hit.confidence, 1 if hit.frozen_hit else 0)
