"""Deterministic model selection — never uses an LLM to choose an LLM."""

from __future__ import annotations

from dataclasses import dataclass

from hypermind.agents import AgentRole
from hypermind.intent import IntentResult
from hypermind.models import ModelProvider, ProviderCapabilities
from hypermind.models.adapters import default_providers, iter_capabilities
from hypermind.models.classify import tier_rank
from hypermind.request import HyperMindRequest


@dataclass(frozen=True)
class ModelRoute:
    provider: str
    model: str
    model_class: str
    reason_code: str
    local: bool


def _latency_key(c: ProviderCapabilities) -> tuple:
    est = c.estimated_latency_ms if c.estimated_latency_ms is not None else 10**9
    return (tier_rank(c.latency_tier), est, c.provider, c.model)


def _pick(caps: list[ProviderCapabilities], reason: str) -> ModelRoute:
    # Stub is a last-resort routing target, never a latency "winner" over real providers.
    real = [c for c in caps if c.provider != "stub"]
    chosen = sorted(real or caps, key=_latency_key)[0]
    return ModelRoute(
        provider=chosen.provider,
        model=chosen.model,
        model_class=chosen.model_class,
        reason_code=reason,
        local=chosen.local,
    )


class ModelRouter:
    def __init__(self, providers: list[ModelProvider] | None = None) -> None:
        self.providers = providers or default_providers()

    def route(
        self,
        request: HyperMindRequest,
        intent: IntentResult,
        agent: AgentRole,
        *,
        prefer_local: bool = True,
        require_vision: bool = False,
        require_tools: bool = False,
        complexity: str = "normal",  # simple | normal | deep
    ) -> ModelRoute:
        caps = [c for c in iter_capabilities(self.providers) if c.available]
        if require_vision:
            vision = self._vision_caps()
            if vision:
                return _pick(vision, "vision_required")

        if not caps:
            return ModelRoute(
                provider="stub",
                model="stub-local",
                model_class="local",
                reason_code="fallback_provider",
                local=True,
            )

        needed_class = self._needed_class(intent, agent, complexity)
        fallback_class = (agent.fallback_model_class or "local").lower()

        def matches(c: ProviderCapabilities) -> bool:
            if require_tools and not c.supports_tools:
                return False
            if not c.text_eligible and not require_vision:
                return False
            return True

        eligible = [c for c in caps if matches(c)]
        reason_relax = None
        if not eligible:
            eligible = [c for c in caps if c.text_eligible] or caps
            reason_relax = "fallback_provider"

        class_hits = [c for c in eligible if c.model_class == needed_class]
        if not class_hits and needed_class == "local_fast":
            class_hits = [c for c in eligible if c.model_class in {"local_fast", "local"}]
        if not class_hits and fallback_class:
            class_hits = [c for c in eligible if c.model_class == fallback_class]
        pool = class_hits or eligible

        if prefer_local and complexity == "simple":
            local = [c for c in pool if c.local]
            if local:
                # Prefer faster tier / measured latency
                return _pick(local, reason_relax or "local_low_cost_match")

        if needed_class == "coding":
            coding = [c for c in pool if c.model_class == "coding"] or pool
            if prefer_local:
                local = [c for c in coding if c.local]
                if local:
                    return _pick(local, reason_relax or "coder_default")
            return _pick(coding, reason_relax or "coder_default")

        if needed_class == "reasoning" or complexity == "deep":
            reasoning = [c for c in pool if c.model_class == "reasoning"] or pool
            if prefer_local:
                local = [c for c in reasoning if c.local] or [
                    c for c in eligible if c.local
                ]
                if local and complexity != "deep":
                    return _pick(local, reason_relax or "latency_preferred")
            cloud = [c for c in reasoning if not c.local]
            chosen_pool = cloud or reasoning
            return _pick(
                chosen_pool,
                reason_relax
                or ("reasoning_required" if complexity == "deep" else "agent_preferred_class"),
            )

        if prefer_local:
            local = [c for c in pool if c.local]
            if local:
                return _pick(local, reason_relax or "local_preferred")

        return _pick(pool, reason_relax or "default_available")

    def _vision_caps(self) -> list[ProviderCapabilities]:
        out: list[ProviderCapabilities] = []
        for provider in self.providers:
            vision_fn = getattr(provider, "vision_capabilities", None)
            if callable(vision_fn):
                out.extend([c for c in vision_fn() if c.available])
            else:
                out.extend(
                    [
                        c
                        for c in provider.capabilities()
                        if c.available and c.supports_vision
                    ]
                )
        return out

    @staticmethod
    def _needed_class(
        intent: IntentResult, agent: AgentRole, complexity: str
    ) -> str:
        if complexity == "simple":
            return "local_fast"
        if complexity == "deep":
            return "reasoning"
        if intent.intent == "coding" or agent.id == "coder":
            return agent.preferred_model_class or "coding"
        # Prefer local class names when agent asks for reasoning but local is preferred
        preferred = (agent.preferred_model_class or "reasoning").lower()
        if preferred == "local":
            return "local"
        return preferred
