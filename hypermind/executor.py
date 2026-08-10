"""Bounded single-generation execution — route then one model call."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from hypermind.models import ModelProvider, ModelRequest, ModelResponse, ProviderError
from hypermind.models.adapters import OllamaProvider
from hypermind.pipeline import IntelligenceRouter, RouteResult
from hypermind.request import HyperMindRequest
from hypermind.trace import ExecutionTrace, TraceStore

# Providers that may perform real generation in this release.
_REAL_PROVIDERS = frozenset({"ollama"})


@dataclass
class ExecutionResult:
    route: RouteResult
    response: ModelResponse | None
    trace: ExecutionTrace
    error: str | None = None
    error_code: str | None = None
    available_models: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.response is not None and self.trace.status == "completed"


class HyperMindExecutor:
    """
    Request → route → bounded context → model → exactly one generate → trace.

    No loops, handoffs, tool calls, or multi-step planning.
    """

    def __init__(
        self,
        *,
        router: IntelligenceRouter | None = None,
        traces: TraceStore | None = None,
        persist_trace: bool = False,
        allow_stub: bool = False,
        max_output_tokens: int = 1024,
        temperature: float | None = 0.2,
        timeout_seconds: float | None = None,
        stream: bool | None = None,
        on_token: Any | None = None,
    ) -> None:
        self.router = router or IntelligenceRouter(persist_trace=False)
        self.traces = traces
        self.persist_trace = persist_trace
        self.allow_stub = allow_stub
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds
        self.stream = stream
        self.on_token = on_token

    def execute(
        self,
        request: HyperMindRequest | str,
        *,
        complexity: str = "normal",
        prefer_local: bool = True,
    ) -> ExecutionResult:
        started = time.perf_counter()
        route = self.router.route(
            request,
            complexity=complexity,
            prefer_local=prefer_local,
        )
        provider = self._provider_named(route.model.provider)

        if provider is None:
            return self._fail(
                route,
                started,
                code="provider_missing",
                message=f"Provider '{route.model.provider}' is not registered.",
            )

        if route.model.provider not in _REAL_PROVIDERS and not (
            self.allow_stub and route.model.provider == "stub"
        ):
            return self._unavailable_executable(route, started)

        model_request = self._build_model_request(route)
        gen_started = time.perf_counter()
        try:
            if isinstance(provider, OllamaProvider):
                response = provider.generate(
                    model_request, route.model.model, on_token=self.on_token
                )
            else:
                response = provider.generate(model_request, route.model.model)
        except ProviderError as exc:
            available: list[str] = []
            if isinstance(provider, OllamaProvider):
                available = provider.installed_models()
            return self._fail(
                route,
                started,
                code=exc.code,
                message=self._format_provider_error(exc, route, available),
                available=available,
                provider_duration_ms=int((time.perf_counter() - gen_started) * 1000),
            )

        duration_ms = int((time.perf_counter() - started) * 1000)
        provider_ms = int((time.perf_counter() - gen_started) * 1000)
        trace = self._base_trace(
            route,
            generation_count=1,
            duration_ms=duration_ms,
            status="completed",
            extra={"provider_duration_ms": provider_ms},
        )
        if self.persist_trace:
            store = self.traces or TraceStore()
            store.write(trace)
        return ExecutionResult(route=route, response=response, trace=trace)

    def _format_provider_error(
        self,
        exc: ProviderError,
        route: RouteResult,
        available: list[str],
    ) -> str:
        if exc.code in {"timeout", "first_token_timeout"}:
            timeout = self.timeout_seconds
            if timeout is None and isinstance(
                self._provider_named(route.model.provider), OllamaProvider
            ):
                ollama = self._ollama_provider()
                timeout = ollama.config.timeout_seconds if ollama else 45
            listing = "\n".join(f"  - {m}" for m in available) if available else "  (none)"
            return (
                f"Ollama {exc.code} after ~{timeout:.0f}s with {route.model.model}.\n"
                f"{exc.message}\n"
                "Fail-fast: HyperMind will not wait indefinitely.\n"
                "Suggestions:\n"
                "  - Retry with a higher ceiling: --timeout 90\n"
                "  - Use --complexity simple for shorter local replies\n"
                "  - Install a smaller text model later (HyperMind will prefer local_fast)\n"
                "  - Benchmark installed models: python hypermind.py models --benchmark\n"
                f"Installed models:\n{listing}"
            )
        return exc.message

    def _unavailable_executable(
        self,
        route: RouteResult,
        started: float,
    ) -> ExecutionResult:
        ollama = self._ollama_provider()
        available: list[str] = []
        code = "no_executable_provider"
        if ollama is not None:
            caps = ollama.capabilities()
            available = ollama.installed_models()
            reason = caps[0].availability_reason if caps else "connection_failed"
            if reason == "model_missing" or (
                bool(ollama.config.model)
                and ollama.resolve_model() is None
                and available
            ):
                configured = ollama.resolve_model() or ollama.config.model or "(none)"
                if getattr(ollama, "_configured_model", None):
                    configured = ollama._configured_model
                listing = "\n".join(available) if available else "(none)"
                message = (
                    "Configured Ollama model is not installed.\n"
                    f"Requested: {configured}\n"
                    f"Available models:\n{listing}"
                )
                code = "model_missing"
            else:
                message = (
                    "Ollama provider unavailable.\n"
                    "Routing completed successfully.\n"
                    "No executable provider is currently configured."
                )
        else:
            message = (
                "Ollama provider unavailable.\n"
                "Routing completed successfully.\n"
                "No executable provider is currently configured."
            )
        return self._fail(
            route,
            started,
            code=code,
            message=message,
            available=available,
        )

    def _fail(
        self,
        route: RouteResult,
        started: float,
        *,
        code: str,
        message: str,
        available: list[str] | None = None,
        provider_duration_ms: int | None = None,
    ) -> ExecutionResult:
        duration_ms = int((time.perf_counter() - started) * 1000)
        extra: dict[str, Any] = {"error_code": code, "error": message[:800]}
        if provider_duration_ms is not None:
            extra["provider_duration_ms"] = provider_duration_ms
        trace = self._base_trace(
            route,
            generation_count=0,
            duration_ms=duration_ms,
            status="failed",
            extra=extra,
        )
        if self.persist_trace:
            store = self.traces or TraceStore()
            store.write(trace)
        return ExecutionResult(
            route=route,
            response=None,
            trace=trace,
            error=message,
            error_code=code,
            available_models=list(available or []),
        )

    def _build_model_request(self, route: RouteResult) -> ModelRequest:
        instruction = route.agent.execution_instruction or (
            f"You are the HyperMind {route.agent.id}.\n"
            f"Role: {route.agent.description}\n"
            "Constraints:\n"
            "- Answer the supplied request.\n"
            "- Use only supplied context.\n"
            "- Do not invent tool results.\n"
            "- Do not claim external actions occurred.\n"
            "- Keep uncertainty explicit."
        )
        context = route.context.prompt_blocks() if route.context else []
        meta: dict[str, Any] = {
            "request_id": route.request.id,
            "agent": route.agent.id,
            "intent": route.intent.intent,
            "context_project": route.context.project if route.context else None,
        }
        if self.timeout_seconds is not None:
            meta["timeout_seconds"] = float(self.timeout_seconds)
        if self.stream is not None:
            meta["stream"] = bool(self.stream)
        if route.model.model_class == "vision":
            meta["allow_vision_model"] = True
        return ModelRequest(
            prompt=route.request.raw_input,
            system=instruction,
            context=context,
            max_tokens=self.max_output_tokens,
            temperature=self.temperature,
            metadata=meta,
        )

    def _base_trace(
        self,
        route: RouteResult,
        *,
        generation_count: int,
        duration_ms: int,
        status: str,
        extra: dict[str, Any] | None = None,
    ) -> ExecutionTrace:
        pack = route.context
        context_items = len(pack.items) if pack else 0
        context_chars = pack.total_chars if pack else 0
        context_truncated = bool(pack.truncated) if pack else False
        context_sources = list(pack.sources_used) if pack else []
        meta = dict(route.trace.metadata) if route.trace else {}
        meta.update(
            {
                "context_items": context_items,
                "context_chars": context_chars,
                "context_truncated": context_truncated,
                "context_sources": context_sources,
                "provider_duration_ms": duration_ms,
                "context_profile": getattr(pack, "context_profile", None) if pack else None,
                "context_budget_chars": getattr(pack, "context_budget_chars", 0) if pack else 0,
                "context_utilization": getattr(pack, "context_utilization", 0.0) if pack else 0.0,
            }
        )
        if extra:
            meta.update(extra)
        return ExecutionTrace(
            request_id=route.request.id,
            intent=route.intent.intent,
            agent=route.agent.id,
            provider=route.model.provider,
            model=route.model.model,
            tools_allowed=[t.id for t in route.tools_allowed],
            route_reason=route.model.reason_code,
            status=status,
            intent_reason=route.intent.reason_code,
            agent_reason=route.agent_reason,
            policy_blocked=list(route.tools_blocked),
            context_items=context_items,
            context_chars=context_chars,
            context_truncated=context_truncated,
            context_sources=context_sources,
            generation_count=generation_count,
            duration_ms=duration_ms,
            metadata=meta,
        )

    def _provider_named(self, name: str) -> ModelProvider | None:
        for provider in self.router.models.providers:
            if provider.name == name:
                return provider
        return None

    def _ollama_provider(self) -> OllamaProvider | None:
        for provider in self.router.models.providers:
            if isinstance(provider, OllamaProvider):
                return provider
        return None
