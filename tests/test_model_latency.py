"""Model class defaults, latency-aware routing, timeout/stream tests."""

from __future__ import annotations

import json

import pytest

from hypermind.agents import AgentRegistry
from hypermind.config import ModelClassRule, ModelSpec, ModelsConfig, OllamaConfig
from hypermind.executor import HyperMindExecutor
from hypermind.intent import IntentResult
from hypermind.models import ModelRequest, ProviderError
from hypermind.models.adapters import OllamaProvider, StubProvider
from hypermind.models.classify import classify_model
from hypermind.models import latency as latency_mod
from hypermind.models.latency import save_latency
from hypermind.models.ollama_client import OllamaClient
from hypermind.models.router import ModelRouter
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest
from tests.test_ollama import FakeHttp, _tags_payload


def test_classify_llava_vision_reserved():
    meta = classify_model("llava:latest")
    assert meta.model_class == "vision"
    assert meta.text_eligible is False
    assert meta.supports_vision is True


def test_classify_llama3_local():
    meta = classify_model(
        "llama3:latest",
        specs={
            "llama3:latest": ModelSpec(
                name="llama3:latest",
                model_class="local",
                latency_tier="standard",
                text_eligible=True,
            )
        },
    )
    assert meta.model_class == "local"
    assert meta.text_eligible is True


def test_classify_small_model_local_fast():
    meta = classify_model(
        "qwen2.5:3b",
        rules=(
            ModelClassRule(
                id="local_fast",
                model_class="local_fast",
                latency_tier="fast",
                match_substrings=(":3b",),
            ),
        ),
    )
    assert meta.model_class == "local_fast"
    assert meta.latency_tier == "fast"


def test_router_prefers_faster_measured_local(tmp_path, monkeypatch):
    monkeypatch.setattr(latency_mod, "repo_root", lambda: tmp_path)
    save_latency(
        {
            "llama3:latest": {"ok": True, "wall_ms": 12000},
            "tinyllama:latest": {"ok": True, "wall_ms": 800},
        },
        repo=tmp_path,
    )

    http = FakeHttp()
    http.tags = _tags_payload("llama3:latest", "tinyllama:latest", "llava:latest")
    cfg = ModelsConfig(
        ollama=OllamaConfig(model=None, timeout_seconds=45),
        model_specs={
            "llama3:latest": ModelSpec(
                "llama3:latest",
                model_class="local",
                latency_tier="standard",
                text_eligible=True,
            ),
            "tinyllama:latest": ModelSpec(
                "tinyllama:latest",
                model_class="local_fast",
                latency_tier="fast",
                text_eligible=True,
            ),
            "llava:latest": ModelSpec(
                "llava:latest",
                model_class="vision",
                latency_tier="vision",
                text_eligible=False,
                supports_vision=True,
            ),
        },
        model_class_rules=(),
    )
    ollama = OllamaProvider(
        config=cfg.ollama,
        client=OllamaClient("http://x", http=http),
        models_config=cfg,
    )
    caps = ollama.capabilities()
    assert {c.model for c in caps if c.available} == {"llama3:latest", "tinyllama:latest"}

    router = ModelRouter(providers=[ollama, StubProvider()])
    route = router.route(
        HyperMindRequest(raw_input="quick summary"),
        IntentResult("general", 0.4, "deterministic", "no_strong_signal"),
        AgentRegistry().get("chief_of_staff"),
        complexity="simple",
        prefer_local=True,
    )
    assert route.model == "tinyllama:latest"
    assert route.reason_code == "local_low_cost_match"


def test_llava_not_used_for_text_generate():
    http = FakeHttp()
    http.tags = _tags_payload("llava:latest", "llama3:latest")
    cfg = ModelsConfig(
        ollama=OllamaConfig(model="llava:latest"),
        model_specs={
            "llava:latest": ModelSpec(
                "llava:latest",
                model_class="vision",
                text_eligible=False,
                supports_vision=True,
            )
        },
    )
    provider = OllamaProvider(
        config=cfg.ollama,
        client=OllamaClient("http://x", http=http),
        models_config=cfg,
    )
    with pytest.raises(ProviderError) as exc:
        provider.generate(ModelRequest(prompt="hi"), "llava:latest")
    assert exc.value.code == "vision_model_reserved"


def test_stream_chat_assembles_tokens():
    chunks = [
        {"message": {"content": "Hel"}, "done": False},
        {"message": {"content": "lo"}, "done": True},
    ]

    def stream_http(method, url, body, timeout):
        payload = json.loads(body.decode())
        assert payload["stream"] is True
        yield from chunks

    client = OllamaClient("http://x", http_stream=stream_http)
    tokens: list[str] = []
    text = client.chat(
        "m",
        ModelRequest(prompt="hi"),
        stream=True,
        on_token=tokens.append,
    )
    assert text == "Hello"
    assert tokens == ["Hel", "lo"]


def test_timeout_error_message_is_actionable():
    http = FakeHttp()
    http.tags = _tags_payload("llama3:latest")
    http.fail_chat = ProviderError("ollama", "timeout", "request timed out")
    ollama = OllamaProvider(
        config=OllamaConfig(model="llama3:latest", timeout_seconds=45),
        client=OllamaClient("http://x", http=http),
    )
    executor = HyperMindExecutor(
        router=IntelligenceRouter(models=ModelRouter(providers=[ollama, StubProvider()])),
        timeout_seconds=45,
    )
    result = executor.execute("Say hi", complexity="simple")
    assert not result.ok
    assert result.error_code == "timeout"
    assert "--timeout" in (result.error or "")
    assert "Fail-fast" in (result.error or "")


def test_vision_route_selects_llava():
    http = FakeHttp()
    http.tags = _tags_payload("llama3:latest", "llava:latest")
    cfg = ModelsConfig(
        ollama=OllamaConfig(model=None),
        model_specs={
            "llama3:latest": ModelSpec(
                "llama3:latest", model_class="local", text_eligible=True
            ),
            "llava:latest": ModelSpec(
                "llava:latest",
                model_class="vision",
                text_eligible=False,
                supports_vision=True,
            ),
        },
    )
    ollama = OllamaProvider(
        config=cfg.ollama,
        client=OllamaClient("http://x", http=http),
        models_config=cfg,
    )
    router = ModelRouter(providers=[ollama, StubProvider()])
    route = router.route(
        HyperMindRequest(raw_input="Describe this image of the portfolio hero"),
        IntentResult("design", 0.9, "deterministic", "design_review"),
        AgentRegistry().get("design_critic"),
        prefer_local=True,
        require_vision=True,
    )
    assert route.model == "llava:latest"
    assert route.reason_code == "vision_required"
