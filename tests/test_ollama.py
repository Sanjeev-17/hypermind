"""Ollama adapter tests — HTTP mocked; no live Ollama required."""

from __future__ import annotations

import json

import pytest

from hypermind.config import OllamaConfig
from hypermind.models import ModelRequest, ProviderError
from hypermind.models.adapters import OllamaProvider, StubProvider, default_providers
from hypermind.models.ollama_client import OllamaClient
from hypermind.models.router import ModelRouter
from hypermind.agents import AgentRegistry
from hypermind.intent import IntentResult
from hypermind.request import HyperMindRequest


def _tags_payload(*names: str) -> dict:
    return {"models": [{"name": n} for n in names]}


def _chat_payload(text: str) -> dict:
    return {"message": {"role": "assistant", "content": text}}


class FakeHttp:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, bytes | None]] = []
        self.tags = _tags_payload("qwen3:8b")
        self.chat = _chat_payload("hello from ollama")
        self.fail_tags: Exception | None = None
        self.fail_chat: Exception | None = None
        self.raw_chat: bytes | None = None

    def __call__(
        self, method: str, url: str, body: bytes | None, timeout: float
    ) -> tuple[int, dict]:
        self.calls.append((method, url, body))
        if url.endswith("/api/tags"):
            if self.fail_tags:
                raise self.fail_tags
            return 200, self.tags
        if url.endswith("/api/chat"):
            if self.fail_chat:
                raise self.fail_chat
            if self.raw_chat is not None:
                # Simulate malformed via client path — return bad structure
                return 200, json.loads(self.raw_chat.decode("utf-8"))
            return 200, self.chat
        raise AssertionError(f"unexpected url {url}")


def test_ollama_available_when_tags_ok():
    http = FakeHttp()
    client = OllamaClient("http://127.0.0.1:11434", http=http)
    provider = OllamaProvider(
        config=OllamaConfig(enabled=True, model="qwen3:8b"),
        client=client,
    )
    caps = provider.capabilities()
    assert len(caps) == 1
    assert caps[0].available is True
    assert caps[0].local is True
    assert caps[0].model == "qwen3:8b"
    assert provider.installed_models() == ["qwen3:8b"]


def test_ollama_unavailable_on_connection_failed():
    http = FakeHttp()
    http.fail_tags = ProviderError("ollama", "connection_failed", "refused")
    client = OllamaClient("http://127.0.0.1:11434", http=http)
    provider = OllamaProvider(config=OllamaConfig(enabled=True, model=None), client=client)
    caps = provider.capabilities()
    assert caps[0].available is False
    assert caps[0].availability_reason == "connection_failed"


def test_model_listing_via_client():
    http = FakeHttp()
    http.tags = _tags_payload("a:1", "b:2")
    client = OllamaClient("http://x", http=http)
    assert client.list_tags() == ["a:1", "b:2"]


def test_configured_model_available():
    http = FakeHttp()
    http.tags = _tags_payload("llama3.2:3b", "qwen3:8b")
    provider = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    assert provider.resolve_model() == "qwen3:8b"
    assert provider.capabilities()[0].available is True


def test_configured_model_missing():
    http = FakeHttp()
    http.tags = _tags_payload("llama3.2:3b")
    provider = OllamaProvider(
        config=OllamaConfig(model="missing-model"),
        client=OllamaClient("http://x", http=http),
    )
    assert provider.resolve_model() is None
    cap = provider.capabilities()[0]
    assert cap.available is False
    assert cap.availability_reason == "model_missing"


def test_request_serialization_to_ollama_payload():
    http = FakeHttp()
    client = OllamaClient("http://x", http=http)
    req = ModelRequest(
        prompt="Explain X",
        system="You are coder",
        context=["agent:coder", "project:hypermind"],
        max_tokens=128,
        temperature=0.1,
    )
    text = client.chat("qwen3:8b", req)
    assert text == "hello from ollama"
    assert len(http.calls) == 1
    method, url, body = http.calls[0]
    assert method == "POST"
    assert url.endswith("/api/chat")
    payload = json.loads(body.decode("utf-8"))
    assert payload["model"] == "qwen3:8b"
    assert payload["stream"] is False
    assert payload["options"]["num_predict"] == 128
    assert payload["options"]["temperature"] == 0.1
    assert payload["messages"][0]["role"] == "system"
    user = payload["messages"][-1]["content"]
    assert "Bounded context" in user or "[CONTEXT]" in user
    assert "USER REQUEST:" in user
    assert "Explain X" in user


def test_response_parsing_malformed():
    http = FakeHttp()
    http.chat = {"message": {"role": "assistant"}}  # missing content
    client = OllamaClient("http://x", http=http)
    with pytest.raises(ProviderError) as exc:
        client.chat("m", ModelRequest(prompt="hi"))
    assert exc.value.code == "malformed_response"


def test_timeout_handling():
    http = FakeHttp()
    http.fail_chat = ProviderError("ollama", "timeout", "request timed out")
    provider = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    # Force probe success first
    http.fail_tags = None
    with pytest.raises(ProviderError) as exc:
        provider.generate(ModelRequest(prompt="hi"), "qwen3:8b")
    assert exc.value.code == "timeout"


def test_model_router_selects_ollama_when_available():
    http = FakeHttp()
    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    router = ModelRouter(providers=[ollama, StubProvider()])
    req = HyperMindRequest(raw_input="simple note")
    intent = IntentResult("general", 0.4, "deterministic", "no_strong_signal")
    agent = AgentRegistry().get("chief_of_staff")
    route = router.route(req, intent, agent, complexity="simple", prefer_local=True)
    assert route.provider == "ollama"
    assert route.model == "qwen3:8b"
    assert route.local is True


def test_fallback_when_ollama_unavailable():
    http = FakeHttp()
    http.fail_tags = ProviderError("ollama", "connection_failed", "down")
    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    router = ModelRouter(providers=[ollama, StubProvider()])
    req = HyperMindRequest(raw_input="implement feature")
    intent = IntentResult("coding", 0.9, "deterministic", "repo_operation")
    agent = AgentRegistry().get("coder")
    route = router.route(req, intent, agent, complexity="normal")
    assert route.provider == "stub"


def test_forced_unavailable_env(monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    http = FakeHttp()
    provider = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    assert provider.capabilities()[0].available is False
    assert not http.calls  # no network when forced off
