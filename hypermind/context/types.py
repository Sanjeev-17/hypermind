"""Canonical context types — provenance-aware, provider-neutral."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContextKind(str, Enum):
    FACT = "FACT"
    DECISION = "DECISION"
    PREFERENCE = "PREFERENCE"
    CURRENT_STATE = "CURRENT_STATE"
    REFERENCE = "REFERENCE"


# Lower number = higher priority when budgeting.
KIND_PRIORITY = {
    ContextKind.DECISION: 20,
    ContextKind.FACT: 30,
    ContextKind.CURRENT_STATE: 35,
    ContextKind.PREFERENCE: 40,
    ContextKind.REFERENCE: 50,
}


@dataclass
class ContextItem:
    id: str
    source_type: str  # profile | project | decision | markdown | reference
    source_ref: str
    title: str
    content: str
    relevance: float = 0.0
    priority: int = 50
    kind: ContextKind = ContextKind.REFERENCE
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def chars(self) -> int:
        return len(self.content)


@dataclass
class ContextPack:
    """Bounded pack passed to the executor / model adapter."""

    items: list[ContextItem] = field(default_factory=list)
    total_chars: int = 0
    truncated: bool = False
    sources_used: list[str] = field(default_factory=list)
    project: str | None = None
    project_id: str | None = None  # e.g. P-006
    approx_tokens: int = 0
    # Retrieval diagnostics (not full content)
    candidate_sections: int = 0
    selected_sections: int = 0
    documents_touched: int = 0
    deduplicated_items: int = 0
    excerpted_items: int = 0
    intent: str | None = None
    context_profile: str | None = None
    context_budget_chars: int = 0
    context_budget_items: int = 0
    context_utilization: float = 0.0
    profile_source: str | None = None

    # Backward-compatible alias used by older call sites
    @property
    def sources(self) -> list[str]:
        return self.sources_used

    def prompt_blocks(self) -> list[str]:
        """Format items for ModelRequest.context with visible provenance."""
        if not self.items:
            return []
        blocks: list[str] = ["[CONTEXT]"]
        for item in self.items:
            blocks.append(
                "\n".join(
                    [
                        f"SOURCE: {item.source_type}",
                        f"KIND: {item.kind.value}",
                        f"REF: {item.source_ref}",
                        f"TITLE: {item.title}",
                        "",
                        item.content.strip(),
                    ]
                )
            )
        blocks.append("[END CONTEXT]")
        return blocks


# Alias retained for pipeline typing / docs
ContextBundle = ContextPack
