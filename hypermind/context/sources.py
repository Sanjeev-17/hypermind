"""Context source abstractions — read-only retrieval."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Any

from hypermind.agents import AgentRole
from hypermind.context.types import ContextItem
from hypermind.request import HyperMindRequest


@dataclass
class ContextQuery:
    request: HyperMindRequest
    agent: AgentRole
    intent: str
    project_key: str | None = None
    project_id: str | None = None
    keywords: list[str] = field(default_factory=list)
    max_chars_per_item: int = 3500
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextSource(ABC):
    name: str

    def can_handle(self, query: ContextQuery) -> bool:
        return True

    @abstractmethod
    def retrieve(self, query: ContextQuery) -> list[ContextItem]:
        ...
