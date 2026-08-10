"""Budget enforcement — drop lowest-priority items first."""

from __future__ import annotations

from dataclasses import dataclass

from hypermind.config.context_config import ContextBudgetConfig
from hypermind.context.types import ContextItem, ContextKind, ContextPack


@dataclass(frozen=True)
class CoveragePolicy:
    """Soft minimum coverage — reserve slots only when candidates exist (no filler)."""

    require_project: bool = False
    require_decision: bool = False
    require_profile: bool = False


def _sort_key(item: ContextItem) -> tuple:
    return (item.priority, -item.relevance, item.source_ref, item.id)


def _clamp_item(item: ContextItem, section_cap: int) -> tuple[ContextItem, bool]:
    if len(item.content) <= section_cap:
        return item, False
    meta = dict(item.metadata)
    meta["excerpted"] = True
    return (
        ContextItem(
            id=item.id,
            source_type=item.source_type,
            source_ref=item.source_ref,
            title=item.title,
            content=item.content[: section_cap - 20].rstrip() + "\n…[truncated]",
            relevance=item.relevance,
            priority=item.priority,
            kind=item.kind,
            metadata=meta,
        ),
        True,
    )


def _is_projectish(item: ContextItem) -> bool:
    return item.source_type in {"project", "markdown"} or item.kind in {
        ContextKind.CURRENT_STATE,
        ContextKind.FACT,
    }


def _is_decision(item: ContextItem) -> bool:
    return item.source_type == "decision" or item.kind == ContextKind.DECISION


def _is_profile(item: ContextItem) -> bool:
    return item.source_type == "profile"


def _reserve_coverage(
    ordered: list[ContextItem], coverage: CoveragePolicy | None
) -> list[ContextItem]:
    if coverage is None:
        return []
    reserved: list[ContextItem] = []
    seen: set[str] = set()

    def take(pred) -> None:
        for item in ordered:
            if item.id in seen:
                continue
            if pred(item):
                reserved.append(item)
                seen.add(item.id)
                return

    if coverage.require_project:
        take(_is_projectish)
    if coverage.require_decision:
        take(_is_decision)
    if coverage.require_profile:
        take(_is_profile)
    return reserved


def apply_budget(
    items: list[ContextItem],
    budget: ContextBudgetConfig,
    *,
    project: str | None = None,
    project_id: str | None = None,
    intent: str | None = None,
    candidate_sections: int = 0,
    documents_touched: int = 0,
    deduplicated_items: int = 0,
    context_profile: str | None = None,
    profile_source: str | None = None,
    coverage: CoveragePolicy | None = None,
) -> ContextPack:
    # Deterministic order: priority asc, then -relevance, then source_ref
    ordered = sorted(items, key=_sort_key)
    reserved = _reserve_coverage(ordered, coverage)
    # Fill order: reserved first (stable among themselves), then remaining ranked
    reserved_ids = {i.id for i in reserved}
    fill_order = reserved + [i for i in ordered if i.id not in reserved_ids]

    selected: list[ContextItem] = []
    truncated = False
    total = 0
    section_cap = min(budget.max_chars_per_section, budget.max_chars_per_item)

    for item in fill_order:
        item, was_clamped = _clamp_item(item, section_cap)
        if was_clamped:
            truncated = True

        if len(selected) >= budget.max_items:
            truncated = True
            break
        if total + item.chars > budget.max_chars and selected:
            truncated = True
            break
        if total + item.chars > budget.max_chars and not selected:
            room = max(0, budget.max_chars - 20)
            meta = dict(item.metadata)
            meta["excerpted"] = True
            item = ContextItem(
                id=item.id,
                source_type=item.source_type,
                source_ref=item.source_ref,
                title=item.title,
                content=item.content[:room].rstrip() + "\n…[truncated]",
                relevance=item.relevance,
                priority=item.priority,
                kind=item.kind,
                metadata=meta,
            )
            truncated = True

        selected.append(item)
        total += item.chars

    # Re-sort selected for stable pack ordering (priority), preserving coverage wins
    selected = sorted(selected, key=_sort_key)

    sources = list(dict.fromkeys(i.source_type for i in selected))
    excerpted = sum(1 for i in selected if i.metadata.get("excerpted"))
    return ContextPack(
        items=selected,
        total_chars=sum(i.chars for i in selected),
        truncated=truncated,
        sources_used=sources,
        project=project,
        project_id=project_id,
        approx_tokens=max(1, sum(i.chars for i in selected) // 4) if selected else 0,
        candidate_sections=candidate_sections,
        selected_sections=len(selected),
        documents_touched=documents_touched,
        deduplicated_items=deduplicated_items,
        excerpted_items=excerpted,
        intent=intent,
        context_profile=context_profile,
        context_budget_chars=budget.max_chars,
        context_budget_items=budget.max_items,
        context_utilization=round(
            (sum(i.chars for i in selected) / budget.max_chars) if budget.max_chars else 0.0,
            3,
        ),
        profile_source=profile_source,
    )


def dedupe_items(items: list[ContextItem]) -> tuple[list[ContextItem], int]:
    """Prefer explicit refs; drop duplicate source_ref / overlapping ranges."""
    ranked = sorted(
        items,
        key=lambda i: (
            0 if i.metadata.get("explicit_ref") else 1,
            i.priority,
            -i.relevance,
            i.source_ref,
        ),
    )
    seen_refs: set[str] = set()
    seen_ranges: set[tuple[str, int, int]] = set()
    out: list[ContextItem] = []
    dropped = 0
    for item in ranked:
        ref_key = item.source_ref
        file_key = str(item.metadata.get("path") or item.source_ref.split("#")[0])
        start = int(item.metadata.get("start_line") or 0)
        end = int(item.metadata.get("end_line") or 0)
        range_key = (file_key, start, end)
        if ref_key in seen_refs:
            dropped += 1
            continue
        if start and end and range_key in seen_ranges:
            dropped += 1
            continue
        # Overlap check within same file
        if start and end:
            overlap = False
            for f, s, e in list(seen_ranges):
                if f == file_key and not (end <= s or start >= e):
                    overlap = True
                    break
            if overlap:
                dropped += 1
                continue
            seen_ranges.add(range_key)
        seen_refs.add(ref_key)
        out.append(item)
    return out, dropped
