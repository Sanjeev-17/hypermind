"""Tool registry — capabilities HyperMind may grant to agents."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Iterable

import yaml

from hypermind.agents import AgentRole


@dataclass(frozen=True)
class ToolDefinition:
    id: str
    category: str
    read_only: bool
    side_effect: bool
    risk_level: str
    available: bool


class ToolRegistry:
    def __init__(self, tools: list[ToolDefinition] | None = None) -> None:
        self._tools = {t.id: t for t in (tools or self._load_default())}

    @staticmethod
    def _load_default() -> list[ToolDefinition]:
        try:
            raw = resources.files("hypermind.tools").joinpath("definitions.yaml").read_text(
                encoding="utf-8"
            )
        except (FileNotFoundError, TypeError, AttributeError):
            raw = Path(__file__).with_name("definitions.yaml").read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
        return [_parse(t) for t in data.get("tools", [])]

    def get(self, tool_id: str) -> ToolDefinition:
        return self._tools[tool_id]

    def all(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def filter_for_agent(
        self, agent: AgentRole, *, available_only: bool = True
    ) -> list[ToolDefinition]:
        allowed: list[ToolDefinition] = []
        for tool_id in agent.allowed_tools:
            tool = self._tools.get(tool_id)
            if tool is None:
                continue
            if available_only and not tool.available:
                continue
            allowed.append(tool)
        return allowed


def _parse(item: dict[str, Any]) -> ToolDefinition:
    return ToolDefinition(
        id=item["id"],
        category=item.get("category", "unknown"),
        read_only=bool(item.get("read_only", True)),
        side_effect=bool(item.get("side_effect", False)),
        risk_level=item.get("risk_level", "low"),
        available=bool(item.get("available", False)),
    )
