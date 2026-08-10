"""Model provider adapters."""

from __future__ import annotations

import os
from typing import Callable, Iterable

from hypermind.config import ModelsConfig, OllamaConfig, load_models_config
from hypermind.models import (
    ModelProvider,
    ModelRequest,
    ModelResponse,
    ProviderCapabilities,
    ProviderError,
)
from hypermind.models.classify import classify_model
from hypermind.models.latency import estimated_ms
from hypermind.models.ollama_client import OllamaClient


class StubProvider(ModelProvider):
    """Deterministic stub used when no real provider is configured."""

    name = "stub"

    def __init__(self, model: str = "stub-local", model_class: str = "local") -> None:
        self._model = model
        self._model_class = model_class

    def capabilities(self) -> list[ProviderCapabilities]:
        return [
            ProviderCapabilities(
                provider=self.name,
                model=self._model,
                local=True,
                available=True,
                supports_tools=False,
                supports_structured_output=True,
                supports_vision=False,
                model_class=self._model_class,
                availability_reason="always_on",
                latency_tier="fast",
                text_eligible=True,
                estimated_latency_ms=1,
            )
        ]

    def generate(self, request: ModelRequest, model: str) -> ModelResponse:
        return ModelResponse(
            text=f"[stub:{model}] {request.prompt[:200]}",
            provider=self.name,
            model=model,
        )


class OllamaProvider(ModelProvider):
    """Local Ollama adapter — availability via live probe or env override."""

    name = "ollama"

    def __init__(
        self,
        config: OllamaConfig | None = None,
        client: OllamaClient | None = None,
        *,
        models_config: ModelsConfig | None = None,
    ) -> None:
        self.models_config = models_config or load_models_config()
        self.config = config or self.models_config.ollama
        env_host = os.getenv("OLLAMA_HOST")
        base = env_host or self.config.base_url
        if env_host and not env_host.startswith("http"):
            base = f"http://{env_host}"
        self.base_url = base.rstrip("/")
        self._client = client or OllamaClient(
            self.base_url,
            timeout_seconds=self.config.timeout_seconds,
            probe_timeout_seconds=self.config.probe_timeout_seconds,
            first_token_timeout_seconds=self.config.first_token_timeout_seconds,
            keep_alive=self.config.keep_alive,
        )
        self._configured_model = os.getenv("HYPERMIND_OLLAMA_MODEL") or self.config.model
        self._cached_tags: list[str] | None = None
        self._cached_reason: str | None = None
        self._probe_done = False

    def _env_force(self) -> bool | None:
        flag = os.getenv("HYPERMIND_OLLAMA_AVAILABLE", "").lower()
        if flag in {"1", "true", "yes"}:
            return True
        if flag in {"0", "false", "no"}:
            return False
        return None

    def _probe(self) -> tuple[list[str], str | None]:
        if self._probe_done and self._cached_tags is not None:
            return self._cached_tags, self._cached_reason
        force = self._env_force()
        if not self.config.enabled and force is not True:
            self._cached_tags = []
            self._cached_reason = "disabled"
            self._probe_done = True
            return self._cached_tags, self._cached_reason
        if force is False:
            self._cached_tags = []
            self._cached_reason = "forced_unavailable"
            self._probe_done = True
            return self._cached_tags, self._cached_reason
        try:
            tags = self._client.list_tags()
            self._cached_tags = tags
            self._cached_reason = None if tags else "no_models_installed"
            self._probe_done = True
            return self._cached_tags, self._cached_reason
        except ProviderError as exc:
            self._cached_tags = []
            self._cached_reason = exc.code
            self._probe_done = True
            return self._cached_tags, self._cached_reason

    def installed_models(self) -> list[str]:
        tags, _ = self._probe()
        return list(tags)

    def _classify(self, name: str):
        return classify_model(
            name,
            specs=self.models_config.model_specs,
            rules=self.models_config.model_class_rules,
        )

    def _cap_for(
        self,
        name: str,
        *,
        available: bool,
        reason: str | None = None,
    ) -> ProviderCapabilities:
        meta = self._classify(name)
        return ProviderCapabilities(
            provider=self.name,
            model=name,
            local=True,
            available=available,
            supports_tools=False,
            supports_structured_output=True,
            supports_vision=meta.supports_vision,
            model_class=meta.model_class,
            availability_reason=reason,
            latency_tier=meta.latency_tier,
            text_eligible=meta.text_eligible,
            estimated_latency_ms=estimated_ms(name),
        )

    def resolve_model(self) -> str | None:
        tags, _ = self._probe()
        if self._configured_model:
            for name in tags:
                if name == self._configured_model or name.startswith(
                    self._configured_model + "-"
                ):
                    return name
            if self._env_force() is True:
                return self._configured_model
            return None
        if not tags:
            return None
        # Auto-pick: text-eligible only; prefer faster tier / measured latency
        text_models = [t for t in tags if self._classify(t).text_eligible]
        pool = text_models or [
            t for t in tags if not t.lower().startswith(("llava", "bakllava", "moondream"))
        ]
        if not pool:
            return None

        def sort_key(tag: str) -> tuple:
            meta = self._classify(tag)
            from hypermind.models.classify import tier_rank

            est = estimated_ms(tag)
            return (tier_rank(meta.latency_tier), est if est is not None else 10**9, tag)

        return sorted(pool, key=sort_key)[0]

    def list_models(self) -> list[ProviderCapabilities]:
        """All installed tags for CLI discovery."""
        force = self._env_force()
        if force is False or (not self.config.enabled and force is not True):
            return self.capabilities()
        tags, reason = self._probe()
        if not tags:
            return self.capabilities()
        return [self._cap_for(name, available=True) for name in tags]

    def capabilities(self) -> list[ProviderCapabilities]:
        """Routing caps: text-eligible models, or vision when that is all that exists."""
        force = self._env_force()
        if force is True and self._configured_model:
            return [self._cap_for(self._configured_model, available=True, reason="forced_available")]

        tags, reason = self._probe()
        if self._configured_model:
            model = self.resolve_model()
            if model and (model in tags or force is True):
                return [self._cap_for(model, available=True)]
            display = self._configured_model
            return [
                self._cap_for(
                    display,
                    available=False,
                    reason=reason
                    or ("model_missing" if self._configured_model else "connection_failed"),
                )
            ]

        if not tags:
            return [
                ProviderCapabilities(
                    provider=self.name,
                    model="(none)",
                    local=True,
                    available=False,
                    model_class="local",
                    availability_reason=reason or "connection_failed",
                    latency_tier="standard",
                    text_eligible=True,
                )
            ]

        text_caps = [
            self._cap_for(t, available=True)
            for t in tags
            if self._classify(t).text_eligible
        ]
        if text_caps:
            return text_caps
        # No text models — expose vision tags as unavailable for text routing
        return [
            self._cap_for(t, available=False, reason="vision_only_no_text_model")
            for t in tags
        ]

    def vision_capabilities(self) -> list[ProviderCapabilities]:
        tags, _ = self._probe()
        return [
            self._cap_for(t, available=True)
            for t in tags
            if self._classify(t).supports_vision
        ]

    def generate(
        self,
        request: ModelRequest,
        model: str,
        *,
        on_token: Callable[[str], None] | None = None,
    ) -> ModelResponse:
        tags, reason = self._probe()
        if reason in {"connection_failed", "timeout", "disabled", "forced_unavailable"}:
            raise ProviderError("ollama", reason or "connection_failed", "Ollama unavailable")
        if tags and model not in tags and not any(
            t == model or t.startswith(model + "-") for t in tags
        ):
            available = ", ".join(tags) if tags else "(none)"
            raise ProviderError(
                "ollama",
                "model_missing",
                f"Configured Ollama model is not installed. Available models: {available}",
            )

        meta = self._classify(model)
        if not meta.text_eligible and not request.metadata.get("allow_vision_model"):
            raise ProviderError(
                "ollama",
                "vision_model_reserved",
                f"{model} is reserved for vision tasks. Use a text-eligible local model.",
            )

        timeout = request.metadata.get("timeout_seconds")
        if timeout is None:
            spec = self.models_config.model_specs.get(model)
            timeout = (
                spec.timeout_seconds
                if spec and spec.timeout_seconds is not None
                else self.config.timeout_seconds
            )
        stream = bool(request.metadata.get("stream", self.config.stream))
        first_token = request.metadata.get("first_token_timeout_seconds")
        if first_token is None:
            first_token = self.config.first_token_timeout_seconds

        try:
            text = self._client.chat(
                model,
                request,
                stream=stream or on_token is not None,
                timeout_seconds=float(timeout),
                on_token=on_token,
                first_token_timeout_seconds=float(first_token),
            )
        except ProviderError:
            raise
        except Exception as exc:  # noqa: BLE001 — normalize
            raise ProviderError("ollama", "generate_failed", str(exc)) from exc
        return ModelResponse(text=text, provider=self.name, model=model)


class OpenAIProvider(ModelProvider):
    name = "openai"

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.getenv("HYPERMIND_OPENAI_MODEL", "gpt-4o-mini")

    def capabilities(self) -> list[ProviderCapabilities]:
        available = bool(os.getenv("OPENAI_API_KEY"))
        return [
            ProviderCapabilities(
                provider=self.name,
                model=self._model,
                local=False,
                available=available,
                supports_tools=True,
                supports_structured_output=True,
                supports_vision=True,
                model_class="reasoning",
                availability_reason=None if available else "missing_api_key",
                latency_tier="standard",
                text_eligible=True,
            ),
            ProviderCapabilities(
                provider=self.name,
                model=os.getenv("HYPERMIND_OPENAI_CODING_MODEL", "gpt-4o"),
                local=False,
                available=available,
                supports_tools=True,
                supports_structured_output=True,
                supports_vision=True,
                model_class="coding",
                availability_reason=None if available else "missing_api_key",
                latency_tier="standard",
                text_eligible=True,
            ),
        ]

    def generate(self, request: ModelRequest, model: str) -> ModelResponse:
        raise ProviderError(
            "openai", "not_implemented", "OpenAI generate is not implemented yet"
        )


class GroqProvider(ModelProvider):
    name = "groq"

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.getenv("HYPERMIND_GROQ_MODEL", "llama-3.3-70b-versatile")

    def capabilities(self) -> list[ProviderCapabilities]:
        available = bool(os.getenv("GROQ_API_KEY"))
        return [
            ProviderCapabilities(
                provider=self.name,
                model=self._model,
                local=False,
                available=available,
                supports_tools=False,
                supports_structured_output=True,
                supports_vision=False,
                model_class="cheap",
                availability_reason=None if available else "missing_api_key",
                latency_tier="fast",
                text_eligible=True,
            )
        ]

    def generate(self, request: ModelRequest, model: str) -> ModelResponse:
        raise ProviderError(
            "groq", "not_implemented", "Groq generate is not implemented yet"
        )


def default_providers(config: ModelsConfig | None = None) -> list[ModelProvider]:
    """Configured adapters + always-available stub fallback."""
    cfg = config or load_models_config()
    return [
        OllamaProvider(config=cfg.ollama, models_config=cfg),
        OpenAIProvider(),
        GroqProvider(),
        StubProvider(),
    ]


def iter_capabilities(providers: Iterable[ModelProvider]) -> list[ProviderCapabilities]:
    caps: list[ProviderCapabilities] = []
    for p in providers:
        caps.extend(p.capabilities())
    return caps
