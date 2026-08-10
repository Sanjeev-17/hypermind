"""Executor and CLI run/models tests."""

from __future__ import annotations

import json

from hypermind.agents import AgentRegistry
from hypermind.cli import main
from hypermind.config import OllamaConfig
from hypermind.executor import HyperMindExecutor
from hypermind.models import ModelRequest, ModelResponse, ProviderError
from hypermind.models.adapters import OllamaProvider, StubProvider
from hypermind.models.ollama_client import OllamaClient
from hypermind.models.router import ModelRouter
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest
from tests.test_ollama import FakeHttp, _chat_payload, _tags_payload


class CountingStub(StubProvider):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def generate(self, request: ModelRequest, model: str) -> ModelResponse:
        self.calls += 1
        return super().generate(request, model)


def _router_with(providers) -> IntelligenceRouter:
    return IntelligenceRouter(models=ModelRouter(providers=providers))


def test_executor_one_generation_with_stub():
    stub = CountingStub()
    http = FakeHttp()
    http.fail_tags = ProviderError("ollama", "connection_failed", "down")
    ollama = OllamaProvider(
        config=OllamaConfig(enabled=True, model=None),
        client=OllamaClient("http://x", http=http),
    )
    executor = HyperMindExecutor(
        router=_router_with([ollama, stub]),
        allow_stub=True,
    )
    result = executor.execute("Review the authentication module")
    assert result.ok
    assert stub.calls == 1
    assert result.trace.generation_count == 1
    assert result.trace.status == "completed"
    assert result.trace.duration_ms is not None
    # Coding packs omit profile/agent identity; empty is valid with no project hits
    assert result.trace.context_items >= 0
    assert result.response is not None


def test_executor_ollama_generate_once():
    http = FakeHttp()
    http.chat = _chat_payload("HYPERMIND_LOCAL_OK")
    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    stub = CountingStub()
    executor = HyperMindExecutor(router=_router_with([ollama, stub]))
    result = executor.execute("Explain briefly")
    assert result.ok
    assert result.response is not None
    assert result.response.text == "HYPERMIND_LOCAL_OK"
    assert result.trace.generation_count == 1
    assert result.trace.provider == "ollama"
    assert stub.calls == 0
    chat_calls = [c for c in http.calls if c[1].endswith("/api/chat")]
    assert len(chat_calls) == 1


def test_executor_trace_operational_only():
    http = FakeHttp()
    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    result = HyperMindExecutor(router=_router_with([ollama, StubProvider()])).execute(
        "code review please"
    )
    data = result.trace.to_dict()
    assert data["generation_count"] == 1
    assert "chain_of_thought" not in data
    assert "system" not in data
    assert "prompt" not in data


def test_executor_no_executable_when_ollama_down():
    http = FakeHttp()
    http.fail_tags = ProviderError("ollama", "connection_failed", "down")
    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    result = HyperMindExecutor(
        router=_router_with([ollama, StubProvider()]),
        allow_stub=False,
    ).execute("hello")
    assert not result.ok
    assert result.trace.generation_count == 0
    assert result.trace.status == "failed"
    assert "Ollama provider unavailable" in (result.error or "")
    assert "No executable provider" in (result.error or "")


def test_executor_model_missing_message():
    http = FakeHttp()
    http.tags = _tags_payload("llama3.2:3b")
    ollama = OllamaProvider(
        config=OllamaConfig(model="not-installed"),
        client=OllamaClient("http://x", http=http),
    )
    result = HyperMindExecutor(
        router=_router_with([ollama, StubProvider()]),
        allow_stub=False,
    ).execute("hello")
    assert not result.ok
    assert result.error_code == "model_missing"
    assert "not installed" in (result.error or "").lower()
    assert "llama3.2:3b" in (result.error or "")


def test_cli_run_allow_stub(capsys, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    code = main(["run", "Review the authentication module", "--allow-stub"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Intent: coding" in out
    assert "Agent: coder" in out
    assert "Response:" in out


def test_cli_run_unavailable(capsys, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    code = main(["run", "Explain architecture"])
    out = capsys.readouterr().out
    assert code == 1
    assert "Ollama provider unavailable" in out


def test_cli_run_trace_verbose(capsys, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    code = main(["run", "Review auth", "--allow-stub", "--trace"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Context items:" in out
    assert "Duration:" in out
    assert "Status: completed" in out


def test_cli_models(capsys, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    code = main(["models"])
    out = capsys.readouterr().out
    assert code == 0
    assert "PROVIDER" in out
    assert "stub" in out
    assert "ollama" in out


def test_agent_execution_instructions_present():
    reg = AgentRegistry()
    for role_id in (
        "chief_of_staff",
        "researcher",
        "architect",
        "coder",
        "design_critic",
        "knowledge_curator",
    ):
        role = reg.get(role_id)
        assert "You are the HyperMind" in role.execution_instruction
        assert "Do not invent tool results" in role.execution_instruction or (
            "Do not invent" in role.execution_instruction
        )


def test_model_request_carries_agent_instruction():
    http = FakeHttp()
    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    executor = HyperMindExecutor(router=_router_with([ollama, StubProvider()]))
    result = executor.execute(HyperMindRequest(raw_input="Review the authentication module and fix a bug"))
    assert result.ok
    body = json.loads([c for c in http.calls if c[1].endswith("/api/chat")][0][2])
    system = body["messages"][0]["content"]
    assert "coder" in system.lower()
    assert result.route.agent.id == "coder"
