"""Declarative agent registry."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from hypermind.intent import IntentResult

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


@dataclass(frozen=True)
class AgentRole:
    id: str
    description: str
    supported_intents: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    preferred_model_class: str
    fallback_model_class: str
    risk_ceiling: str
    execution_instruction: str = ""

    def allows_risk(self, risk_level: str | None) -> bool:
        if risk_level is None:
            return True
        return _RISK_ORDER.get(risk_level, 1) <= _RISK_ORDER.get(self.risk_ceiling, 1)


class AgentRegistry:
    def __init__(self, roles: list[AgentRole] | None = None) -> None:
        self._roles = {r.id: r for r in (roles or self._load_default())}

    @staticmethod
    def _load_default() -> list[AgentRole]:
        try:
            raw = resources.files("hypermind.agents").joinpath("roles.yaml").read_text(
                encoding="utf-8"
            )
        except (FileNotFoundError, TypeError, AttributeError):
            path = Path(__file__).with_name("roles.yaml")
            raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
        return [_parse_role(item) for item in data.get("roles", [])]

    def get(self, role_id: str) -> AgentRole:
        if role_id not in self._roles:
            raise KeyError(role_id)
        return self._roles[role_id]

    def all(self) -> list[AgentRole]:
        return list(self._roles.values())

    def select(self, intent: IntentResult, risk_level: str | None = None) -> AgentRole:
        """Pick the best agent for an intent. Prefer specialist over chief_of_staff."""
        candidates = [
            r
            for r in self._roles.values()
            if intent.intent in r.supported_intents and r.allows_risk(risk_level)
        ]
        if not candidates:
            return self.get("chief_of_staff")

        # Prefer non-generalist when possible
        ranked = sorted(
            candidates,
            key=lambda r: (
                0 if r.id != "chief_of_staff" else 1,
                -len(r.supported_intents),  # more specialist ≈ fewer intents
                r.id,
            ),
        )
        # Specialists with fewer intents first
        specialists = [r for r in ranked if r.id != "chief_of_staff"]
        if specialists:
            specialists.sort(key=lambda r: (len(r.supported_intents), r.id))
            return specialists[0]
        return ranked[0]


def _parse_role(item: dict[str, Any]) -> AgentRole:
    return AgentRole(
        id=item["id"],
        description=item.get("description", ""),
        supported_intents=tuple(item.get("supported_intents", [])),
        allowed_tools=tuple(item.get("allowed_tools", [])),
        preferred_model_class=item.get("preferred_model_class", "reasoning"),
        fallback_model_class=item.get("fallback_model_class", "local"),
        risk_ceiling=item.get("risk_ceiling", "medium"),
        execution_instruction=(item.get("execution_instruction") or "").strip(),
    )


# Intent → preferred agent overrides (deterministic, compact)
INTENT_AGENT_PREFERENCE = {
    "planning": "chief_of_staff",
    "research": "researcher",
    "coding": "coder",
    "design": "design_critic",
    "writing": "chief_of_staff",
    "memory": "knowledge_curator",
    "knowledge": "knowledge_curator",
    "communication": "chief_of_staff",
    "system": "architect",
    "general": "chief_of_staff",
}


def select_agent(
    intent: IntentResult,
    registry: AgentRegistry | None = None,
    risk_level: str | None = None,
    reason_code: str | None = None,
) -> tuple[AgentRole, str]:
    """Select agent with preference map, then registry fallback."""
    reg = registry or AgentRegistry()

    # Architecture reason prefers architect over chief_of_staff
    if reason_code == "architecture_request" or (
        intent.reason_code == "architecture_request"
    ):
        role = reg.get("architect")
        if role.allows_risk(risk_level):
            return role, "architecture_specialist"

    preferred_id = INTENT_AGENT_PREFERENCE.get(intent.intent, "chief_of_staff")
    preferred = reg.get(preferred_id)
    if intent.intent in preferred.supported_intents and preferred.allows_risk(risk_level):
        return preferred, f"intent_preference_{preferred_id}"

    role = reg.select(intent, risk_level=risk_level)
    return role, f"registry_select_{role.id}"
