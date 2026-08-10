"""Provider-neutral HyperMind request object."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class HyperMindRequest:
    """What HyperMind wants done — not how a provider executes it."""

    raw_input: str
    id: str = field(default_factory=lambda: str(uuid4()))
    intent: str | None = None
    project: str | None = None
    context_refs: list[str] = field(default_factory=list)
    requested_capabilities: list[str] = field(default_factory=list)
    risk_level: str | None = None  # low | medium | high | critical
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.raw_input = (self.raw_input or "").strip()
        if not self.raw_input:
            raise ValueError("raw_input must be non-empty")
