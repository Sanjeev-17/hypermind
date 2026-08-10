"""One-shot local model benchmark — never auto-downloads."""

from __future__ import annotations

import time
from typing import Any

from hypermind.config import load_models_config
from hypermind.models import ModelRequest, ProviderError
from hypermind.models.adapters import OllamaProvider
from hypermind.models.classify import classify_model
from hypermind.models.latency import save_latency


def run_local_benchmark(
    *,
    include_vision: bool = False,
    num_predict: int = 8,
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """
    Probe each installed Ollama tag once with a tiny prompt.

    Vision models are skipped unless include_vision=True (still no downloads).
    """
    cfg = load_models_config()
    provider = OllamaProvider(config=cfg.ollama, models_config=cfg)
    tags = provider.installed_models()
    results: dict[str, Any] = {}

    for tag in tags:
        meta = classify_model(
            tag, specs=cfg.model_specs, rules=cfg.model_class_rules
        )
        if not meta.text_eligible and not include_vision:
            results[tag] = {
                "ok": False,
                "skipped_reason": "vision_reserved",
                "model_class": meta.model_class,
                "latency_tier": meta.latency_tier,
                "text_eligible": False,
            }
            continue

        req = ModelRequest(
            prompt="Reply with exactly: OK",
            temperature=0.0,
            max_tokens=num_predict,
            metadata={
                "timeout_seconds": timeout_seconds,
                "stream": False,
                "allow_vision_model": not meta.text_eligible,
            },
        )
        t0 = time.perf_counter()
        try:
            response = provider.generate(req, tag)
            wall = int((time.perf_counter() - t0) * 1000)
            results[tag] = {
                "ok": True,
                "wall_ms": wall,
                "model_class": meta.model_class,
                "latency_tier": meta.latency_tier,
                "text_eligible": meta.text_eligible,
                "preview": response.text[:80],
                "num_predict": num_predict,
            }
        except ProviderError as exc:
            wall = int((time.perf_counter() - t0) * 1000)
            results[tag] = {
                "ok": False,
                "wall_ms": wall,
                "error_code": exc.code,
                "error": exc.message[:300],
                "model_class": meta.model_class,
                "latency_tier": meta.latency_tier,
                "text_eligible": meta.text_eligible,
            }

    path = save_latency(results)
    return {"path": str(path), "models": results}
