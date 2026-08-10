"""Model router tests — no paid API calls."""

import os

from hypermind.agents import AgentRegistry
from hypermind.intent import IntentResult
from hypermind.models.adapters import OpenAIProvider, StubProvider, default_providers
from hypermind.models.router import ModelRouter
from hypermind.request import HyperMindRequest


def test_simple_prefers_local_stub():
    router = ModelRouter(providers=[StubProvider(), OpenAIProvider()])
    # OpenAI unavailable without key
    os.environ.pop("OPENAI_API_KEY", None)
    req = HyperMindRequest(raw_input="summarize this")
    intent = IntentResult("general", 0.4, "deterministic", "no_strong_signal")
    agent = AgentRegistry().get("chief_of_staff")
    route = router.route(req, intent, agent, complexity="simple", prefer_local=True)
    assert route.local is True
    assert route.reason_code == "local_low_cost_match"
    assert route.provider == "stub"


def test_coder_default_class(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    router = ModelRouter(providers=default_providers())
    req = HyperMindRequest(raw_input="implement feature")
    intent = IntentResult("coding", 0.9, "deterministic", "repo_operation")
    agent = AgentRegistry().get("coder")
    route = router.route(req, intent, agent, complexity="normal")
    # Only stub available → still routes
    assert route.provider == "stub"
    assert route.reason_code in {"coder_default", "agent_preferred_class", "default_available", "local_preferred"}


def test_fallback_when_preferred_unavailable(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    router = ModelRouter(providers=default_providers())
    req = HyperMindRequest(raw_input="deep reasoning please")
    intent = IntentResult("planning", 0.9, "deterministic", "planning_request")
    agent = AgentRegistry().get("architect")
    route = router.route(req, intent, agent, complexity="deep", prefer_local=False)
    assert route.provider == "stub"
    assert route.model


def test_unavailable_openai_not_selected(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    caps = OpenAIProvider().capabilities()
    assert all(not c.available for c in caps)
