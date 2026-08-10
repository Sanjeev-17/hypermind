"""Provider-neutral model gateway."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderCapabilities:
    provider: str
    model: str
    local: bool
    available: bool
    supports_tools: bool = False
    supports_structured_output: bool = False
    supports_vision: bool = False
    model_class: str = "reasoning"  # local_fast | local | vision | coding | reasoning | cheap
    availability_reason: str | None = None
    latency_tier: str = "standard"  # fast | standard | slow | vision
    text_eligible: bool = True
    estimated_latency_ms: int | None = None


@dataclass
class ModelRequest:
    """Provider-neutral generation request."""

    prompt: str  # user input
    system: str | None = None
    context: list[str] = field(default_factory=list)
    max_tokens: int | None = None
    temperature: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def user_input(self) -> str:
        return self.prompt

    @property
    def system_instruction(self) -> str | None:
        return self.system


@dataclass
class ModelResponse:
    text: str
    provider: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)


class ProviderError(Exception):
    """Typed provider failure — do not leak raw HTTP into CLI."""

    def __init__(self, provider: str, code: str, message: str) -> None:
        self.provider = provider
        self.code = code
        self.message = message
        super().__init__(f"{provider}:{code}: {message}")


class ModelProvider(ABC):
    """Replaceable compute adapter — HyperMind owns orchestration."""

    name: str

    @abstractmethod
    def capabilities(self) -> list[ProviderCapabilities]:
        ...

    @abstractmethod
    def generate(self, request: ModelRequest, model: str) -> ModelResponse:
        ...

    def is_available(self) -> bool:
        return any(c.available for c in self.capabilities())

    def list_models(self) -> list[ProviderCapabilities]:
        return self.capabilities()
