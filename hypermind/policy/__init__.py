"""Deterministic policy gate — never delegated to an LLM."""

from __future__ import annotations

from dataclasses import dataclass

from hypermind.agents import AgentRole
from hypermind.tools import ToolDefinition, ToolRegistry

# Global denials regardless of agent (unless explicitly allowlisted later)
_DEFAULT_BLOCKED = frozenset(
    {
        "filesystem.delete",
        "email.send",
        "publish",
    }
)

# Require explicit capability on the agent (already filtered) + extra gate
_REQUIRES_EXPLICIT = frozenset(
    {
        "filesystem.write",
        "git.commit",
        "memory.write",
        "obsidian.write",
    }
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    tool_id: str
    reason_code: str


class PolicyGate:
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()

    def check(self, tool_id: str, agent: AgentRole) -> PolicyDecision:
        if tool_id in _DEFAULT_BLOCKED:
            return PolicyDecision(False, tool_id, "blocked_by_default")

        if tool_id not in agent.allowed_tools:
            return PolicyDecision(False, tool_id, "agent_missing_capability")

        try:
            tool = self.registry.get(tool_id)
        except KeyError:
            return PolicyDecision(False, tool_id, "unknown_tool")

        if not tool.available:
            return PolicyDecision(False, tool_id, "tool_unavailable")

        if tool_id in _REQUIRES_EXPLICIT and tool_id not in agent.allowed_tools:
            return PolicyDecision(False, tool_id, "explicit_permission_required")

        if tool.side_effect and tool.risk_level in {"high", "critical"}:
            if tool_id == "git.commit":
                return PolicyDecision(True, tool_id, "explicit_git_commit_allowed")
            if tool_id in _DEFAULT_BLOCKED:
                return PolicyDecision(False, tool_id, "blocked_by_default")

        if tool.read_only:
            return PolicyDecision(True, tool_id, "read_allowed")

        return PolicyDecision(True, tool_id, "write_capability_granted")

    def filter_tools(
        self, tools: list[ToolDefinition], agent: AgentRole
    ) -> list[ToolDefinition]:
        return [t for t in tools if self.check(t.id, agent).allowed]
