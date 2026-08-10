"""Intent classification results."""

from __future__ import annotations

from dataclasses import dataclass


INTENTS = (
    "planning",
    "research",
    "coding",
    "design",
    "writing",
    "memory",
    "knowledge",
    "communication",
    "system",
    "general",
)


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    method: str  # deterministic | model (reserved)
    reason_code: str

    def __post_init__(self) -> None:
        if self.intent not in INTENTS:
            raise ValueError(f"unknown intent: {self.intent}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
