"""Deterministic Ollama tag → model class / latency tier classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from hypermind.config import ModelClassRule, ModelSpec


@dataclass(frozen=True)
class ModelClassification:
    model: str
    model_class: str
    latency_tier: str
    text_eligible: bool
    supports_vision: bool


_TIER_RANK = {"fast": 0, "standard": 1, "slow": 2, "vision": 9}


def tier_rank(tier: str | None) -> int:
    return _TIER_RANK.get((tier or "standard").lower(), 5)


def classify_model(
    name: str,
    *,
    specs: dict[str, ModelSpec] | None = None,
    rules: Iterable[ModelClassRule] | None = None,
) -> ModelClassification:
    """Classify an installed tag. Explicit model specs win over rules."""
    specs = specs or {}
    if name in specs:
        spec = specs[name]
        return ModelClassification(
            model=name,
            model_class=spec.model_class or "local",
            latency_tier=spec.latency_tier or "standard",
            text_eligible=True if spec.text_eligible is None else bool(spec.text_eligible),
            supports_vision=bool(spec.supports_vision),
        )

    lowered = name.lower()
    for rule in rules or ():
        if any(lowered.startswith(p.lower()) for p in rule.match_prefixes):
            return ModelClassification(
                model=name,
                model_class=rule.model_class,
                latency_tier=rule.latency_tier,
                text_eligible=rule.text_eligible,
                supports_vision=rule.supports_vision,
            )
        if any(s.lower() in lowered for s in rule.match_substrings):
            return ModelClassification(
                model=name,
                model_class=rule.model_class,
                latency_tier=rule.latency_tier,
                text_eligible=rule.text_eligible,
                supports_vision=rule.supports_vision,
            )

    # Safe default: treat unknown tags as text-eligible local chat
    visionish = lowered.startswith(("llava", "bakllava", "moondream"))
    if visionish:
        return ModelClassification(
            model=name,
            model_class="vision",
            latency_tier="vision",
            text_eligible=False,
            supports_vision=True,
        )
    return ModelClassification(
        model=name,
        model_class="local",
        latency_tier="standard",
        text_eligible=True,
        supports_vision=False,
    )
