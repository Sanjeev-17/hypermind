"""Deterministic context pack profiles — ceilings by task need, not store size."""

from __future__ import annotations

from dataclasses import dataclass, field

from hypermind.config.context_config import ContextEngineConfig, ContextProfileSpec
from hypermind.request import HyperMindRequest

# Hard clamps for overrides (also mirrored in config)
_MIN_CHARS = 500
_MAX_CHARS = 12000
_MIN_ITEMS = 1
_MAX_ITEMS = 12


@dataclass(frozen=True)
class ContextProfile:
    id: str
    max_items: int
    max_chars: int
    decisions_max: int
    include_profile: bool
    include_agent_identity: bool
    preferred_source_types: tuple[str, ...] = ()
    section_max_chars: int = 1500
    source: str = "intent"  # intent | override | fallback
    model_cap_chars: int | None = None

    def utilization(self, used_chars: int) -> float:
        if self.max_chars <= 0:
            return 0.0
        return round(min(1.0, used_chars / self.max_chars), 3)


class ContextProfileError(ValueError):
    """Invalid profile override or budget."""


class ContextProfileResolver:
    def __init__(self, config: ContextEngineConfig) -> None:
        self.config = config
        self._by_id = {p.id: p for p in config.profiles}

    def known_ids(self) -> list[str]:
        return sorted(self._by_id)

    def resolve(
        self,
        intent: str,
        request: HyperMindRequest,
        *,
        project: str | None = None,
        override_profile: str | None = None,
        override_max_chars: int | None = None,
        override_max_items: int | None = None,
        model_name: str | None = None,
    ) -> ContextProfile:
        source = "intent"
        if override_profile:
            key = override_profile.strip().lower()
            if key not in self._by_id:
                raise ContextProfileError(
                    f"Unknown context profile '{override_profile}'. "
                    f"Known: {', '.join(self.known_ids())}"
                )
            spec = self._by_id[key]
            source = "override"
        else:
            intent_key = (intent or "general").lower()
            # Map communication → communication profile; unknown → general
            if intent_key in self._by_id:
                spec = self._by_id[intent_key]
            else:
                spec = self._by_id.get("general") or next(iter(self._by_id.values()))
                source = "fallback"

        max_chars = spec.max_chars
        max_items = spec.max_items
        section_max = spec.section_max_chars

        if override_max_chars is not None:
            max_chars = _clamp_chars(override_max_chars, self.config)
            source = source if source == "override" else "intent+override"
        if override_max_items is not None:
            max_items = _clamp_items(override_max_items, self.config)

        model_cap = None
        if model_name:
            model_cap = self.config.model_context_caps.get(model_name)
            if model_cap is None:
                # Allow bare name without tag
                bare = model_name.split(":")[0]
                for k, v in self.config.model_context_caps.items():
                    if k == model_name or k.split(":")[0] == bare:
                        model_cap = v
                        break
            if model_cap is not None:
                max_chars = min(max_chars, int(model_cap))

        # Never exceed global ceiling
        max_chars = min(max_chars, self.config.budget.max_chars)
        max_items = min(max_items, self.config.budget.max_items)
        section_max = min(
            section_max,
            self.config.budget.max_chars_per_section,
            max_chars,
        )

        return ContextProfile(
            id=spec.id,
            max_items=max_items,
            max_chars=max_chars,
            decisions_max=spec.decisions_max,
            include_profile=spec.include_profile,
            include_agent_identity=spec.include_agent_identity,
            preferred_source_types=spec.preferred_source_types,
            section_max_chars=section_max,
            source=source,
            model_cap_chars=model_cap,
        )


def _clamp_chars(value: int, config: ContextEngineConfig) -> int:
    ceiling = min(config.override_max_chars, _MAX_CHARS)
    if value < _MIN_CHARS or value > ceiling:
        raise ContextProfileError(
            f"max context chars must be between {_MIN_CHARS} and {ceiling} (got {value})"
        )
    return value


def _clamp_items(value: int, config: ContextEngineConfig) -> int:
    ceiling = min(config.override_max_items, _MAX_ITEMS)
    if value < _MIN_ITEMS or value > ceiling:
        raise ContextProfileError(
            f"max context items must be between {_MIN_ITEMS} and {ceiling} (got {value})"
        )
    return value
