"""Compare candidates against existing bounded context/memory snippets."""

from __future__ import annotations

from dataclasses import dataclass

from hypermind.context.types import ContextItem
from hypermind.memory.normalize import normalize_statement, token_set
from hypermind.memory.types import MemoryRelationship


_UPDATE_CUES = frozenset(
    {
        "instead",
        "prefer",
        "preference",
        "switch",
        "change",
        "update",
        "now",
        "default",
        "once",
        "from now",
        "going forward",
    }
)

_CONFLICT_CUES = frozenset(
    {
        "not",
        "never",
        "restructure",
        "unfreeze",
        "without",
        "ignore",
        "override",
        "cancel",
        "abandon",
        "replace",
    }
)


@dataclass(frozen=True)
class CompareHit:
    relationship: str
    existing_ref: str | None
    reason_code: str


def compare_to_existing(
    statement: str, existing: list[ContextItem]
) -> CompareHit:
    """Deterministic relationship vs retrieved context items."""
    cand_norm = normalize_statement(statement)
    if not cand_norm:
        return CompareHit(MemoryRelationship.NEW.value, None, "empty_statement")

    cand_tokens = token_set(statement)
    best: CompareHit | None = None

    for item in existing:
        ref = item.source_ref
        existing_norm = normalize_statement(item.content)
        title_norm = normalize_statement(item.title)
        haystacks = [existing_norm, title_norm, f"{title_norm} {existing_norm}".strip()]

        for hay in haystacks:
            if not hay:
                continue
            if cand_norm == hay or cand_norm in hay or hay in cand_norm:
                return CompareHit(
                    MemoryRelationship.DUPLICATE.value,
                    ref,
                    "exact_or_contained_match",
                )

        exist_tokens = token_set(item.content) | token_set(item.title)
        if not cand_tokens or not exist_tokens:
            continue
        overlap = cand_tokens & exist_tokens
        union = cand_tokens | exist_tokens
        jaccard = len(overlap) / max(1, len(union))
        if jaccard >= 0.72:
            return CompareHit(
                MemoryRelationship.DUPLICATE.value,
                ref,
                "high_token_overlap",
            )
        if jaccard >= 0.35 and len(overlap) >= 3:
            joined = " ".join(cand_tokens)
            if any(c in joined for c in _CONFLICT_CUES) or any(
                c in cand_norm for c in ("without a version", "unfreeze", "restructure")
            ):
                hit = CompareHit(
                    MemoryRelationship.POSSIBLE_CONFLICT.value,
                    ref,
                    "overlapping_subject_conflict_cue",
                )
            elif any(c in cand_norm for c in _UPDATE_CUES):
                hit = CompareHit(
                    MemoryRelationship.POSSIBLE_UPDATE.value,
                    ref,
                    "overlapping_subject_update_cue",
                )
            else:
                hit = CompareHit(
                    MemoryRelationship.POSSIBLE_UPDATE.value,
                    ref,
                    "overlapping_subject",
                )
            if best is None or _rank(hit.relationship) > _rank(best.relationship):
                best = hit

    return best or CompareHit(MemoryRelationship.NEW.value, None, "no_existing_match")


def _rank(rel: str) -> int:
    order = {
        MemoryRelationship.DUPLICATE.value: 3,
        MemoryRelationship.POSSIBLE_CONFLICT.value: 2,
        MemoryRelationship.POSSIBLE_UPDATE.value: 1,
        MemoryRelationship.NEW.value: 0,
    }
    return order.get(rel, 0)
