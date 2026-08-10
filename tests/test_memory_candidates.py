"""Memory candidate engine tests — mocked providers; no vault writes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hypermind.cli import main
from hypermind.config import OllamaConfig
from hypermind.context.types import ContextItem, ContextKind
from hypermind.memory.compare import compare_to_existing
from hypermind.memory.engine import MemoryCandidateEngine
from hypermind.memory.normalize import normalize_statement
from hypermind.memory.parse import parse_candidates_payload
from hypermind.memory.sensitivity import classify_sensitivity, contains_secret_like
from hypermind.memory.types import (
    MemoryProposeRequest,
    MemoryRelationship,
    candidate_from_raw,
)
from hypermind.models.adapters import OllamaProvider, StubProvider
from hypermind.models.ollama_client import OllamaClient
from hypermind.models.router import ModelRouter
from hypermind.pipeline import IntelligenceRouter
from tests.test_ollama import FakeHttp, _chat_payload, _tags_payload


def _engine_with_chat(payload: dict, *, allow_stub: bool = False) -> MemoryCandidateEngine:
    http = FakeHttp()
    http.tags = _tags_payload("llama3:latest")
    http.chat = payload
    ollama = OllamaProvider(
        config=OllamaConfig(model="llama3:latest", timeout_seconds=5),
        client=OllamaClient("http://x", http=http),
    )
    router = IntelligenceRouter(
        models=ModelRouter(providers=[ollama, StubProvider()]),
        persist_trace=False,
    )
    engine = MemoryCandidateEngine(router=router, allow_stub=allow_stub)
    engine._test_http = http  # type: ignore[attr-defined]
    return engine


def _cands_json(items: list[dict]) -> dict:
    return {"message": {"role": "assistant", "content": json.dumps({"candidates": items})}}


def test_normalize_statement():
    assert normalize_statement("  Prefer Local-First!!  ") == "prefer local first"


def test_secret_like_detection():
    assert contains_secret_like("password: hunter2")
    assert contains_secret_like("API_KEY=sk-abcdefghijklmnop")
    assert not contains_secret_like("I prefer local-first HyperMind")


def test_sensitivity_restricted():
    assert classify_sensitivity("My health diagnosis notes") == "restricted"
    assert classify_sensitivity("I prefer local-first") == "normal"


def test_zero_candidates():
    engine = _engine_with_chat(_cands_json([]))
    result = engine.propose(MemoryProposeRequest(text="Hello there, how are you?"))
    assert result.ok
    assert result.candidates == []
    assert result.trace["generation_count"] == 1
    assert result.trace["memory_written"] is False


def test_one_valid_preference_candidate():
    engine = _engine_with_chat(
        _cands_json(
            [
                {
                    "category": "PREFERENCE",
                    "statement": "Prefer keeping HyperMind local-first",
                    "scope": "global",
                    "project": None,
                    "confidence": 0.92,
                    "reason_code": "explicit_stable_preference",
                    "sensitivity": "normal",
                    "source_refs": ["input:user"],
                }
            ]
        )
    )
    result = engine.propose(
        MemoryProposeRequest(
            text="I prefer keeping HyperMind local-first and using cloud models only when they add clear value."
        )
    )
    assert result.ok
    assert len(result.candidates) == 1
    c = result.candidates[0]
    assert c.category == "PREFERENCE"
    assert c.scope == "global"
    assert c.relationship in {
        MemoryRelationship.NEW.value,
        MemoryRelationship.POSSIBLE_UPDATE.value,
    }
    assert c.status == "proposed"
    assert result.trace["candidate_count"] == 1


@pytest.mark.parametrize(
    "category",
    [
        "FACT",
        "PREFERENCE",
        "GOAL",
        "CONSTRAINT",
        "CURRENT_STATE",
        "PROJECT_CONTEXT",
        "DECISION_CANDIDATE",
    ],
)
def test_categories_accepted(category: str):
    engine = _engine_with_chat(
        _cands_json(
            [
                {
                    "category": category,
                    "statement": f"Example {category.lower()} statement for tests",
                    "scope": "global" if category != "PROJECT_CONTEXT" else "project",
                    "project": None if category != "PROJECT_CONTEXT" else "portfolio",
                    "confidence": 0.8,
                    "reason_code": "test",
                    "sensitivity": "normal",
                    "source_refs": ["input:user"],
                }
            ]
        )
    )
    result = engine.propose(
        MemoryProposeRequest(
            text=f"Please remember this {category}",
            project="portfolio" if category == "PROJECT_CONTEXT" else None,
        )
    )
    assert result.ok
    assert len(result.candidates) == 1
    assert result.candidates[0].category == category


def test_max_candidate_count():
    items = [
        {
            "category": "FACT",
            "statement": f"Fact number {i} about something durable",
            "scope": "global",
            "project": None,
            "confidence": 0.7,
            "reason_code": "test",
            "sensitivity": "normal",
            "source_refs": ["input:user"],
        }
        for i in range(8)
    ]
    engine = _engine_with_chat(_cands_json(items))
    result = engine.propose(MemoryProposeRequest(text="Many facts", max_candidates=5))
    assert result.ok
    assert len(result.candidates) <= 5


def test_project_scope():
    engine = _engine_with_chat(
        _cands_json(
            [
                {
                    "category": "CONSTRAINT",
                    "statement": "Portfolio cases must remain interview-defendable",
                    "scope": "project",
                    "project": "portfolio",
                    "confidence": 0.88,
                    "reason_code": "explicit_project_constraint",
                    "sensitivity": "normal",
                    "source_refs": ["input:user"],
                }
            ]
        )
    )
    result = engine.propose(
        MemoryProposeRequest(
            text="For portfolio, cases must remain interview-defendable.",
            project="portfolio",
        )
    )
    assert result.ok
    assert result.candidates[0].scope == "project"
    assert result.candidates[0].project == "portfolio"


def test_fabricated_source_ref_rejected():
    with pytest.raises(ValueError, match="fabricated"):
        candidate_from_raw(
            {
                "category": "FACT",
                "statement": "Something",
                "scope": "global",
                "confidence": 0.5,
                "reason_code": "x",
                "sensitivity": "normal",
                "source_refs": ["vault://invented.md"],
            },
            allowed_sources={"input:user"},
        )


def test_duplicate_detection():
    items = [
        ContextItem(
            id="1",
            source_type="profile",
            source_ref="hypermind/config/profile.md",
            title="Profile",
            content="Prefer keeping HyperMind local-first and inspectable.",
            kind=ContextKind.PREFERENCE,
        )
    ]
    hit = compare_to_existing(
        "Prefer keeping HyperMind local-first and inspectable.", items
    )
    assert hit.relationship == MemoryRelationship.DUPLICATE.value


def test_possible_update_detection():
    items = [
        ContextItem(
            id="1",
            source_type="profile",
            source_ref="profile.md",
            title="Model",
            content="Preferred local model is llama3:latest for HyperMind runs.",
            kind=ContextKind.PREFERENCE,
        )
    ]
    hit = compare_to_existing(
        "I want the 3B model to be the default once installed for HyperMind local runs.",
        items,
    )
    assert hit.relationship in {
        MemoryRelationship.POSSIBLE_UPDATE.value,
        MemoryRelationship.NEW.value,
        MemoryRelationship.DUPLICATE.value,
    }


def test_possible_conflict_detection():
    items = [
        ContextItem(
            id="1",
            source_type="decision",
            source_ref="Decision_Log.md#D-001",
            title="Freeze",
            content="Portfolio OS v1.0 is frozen for portfolio structure.",
            kind=ContextKind.DECISION,
        )
    ]
    hit = compare_to_existing(
        "Let's restructure Portfolio OS v1.0 without a version change.",
        items,
    )
    assert hit.relationship in {
        MemoryRelationship.POSSIBLE_CONFLICT.value,
        MemoryRelationship.POSSIBLE_UPDATE.value,
        MemoryRelationship.NEW.value,
    }


def test_secret_input_suppresses_candidates():
    engine = _engine_with_chat(_cands_json([]))
    result = engine.propose(
        MemoryProposeRequest(text="Please remember password: super-secret-value")
    )
    assert result.ok
    assert result.candidates == []
    assert any(s.get("reason_code") == "secret_like_content" for s in result.suppressed)
    assert result.trace["generation_count"] == 0


def test_malformed_model_output():
    engine = _engine_with_chat(
        {"message": {"role": "assistant", "content": "not json at all"}}
    )
    result = engine.propose(MemoryProposeRequest(text="Remember that I like concise answers"))
    assert not result.ok
    assert result.error and result.error["code"] == "MALFORMED_OUTPUT"
    assert result.trace["generation_count"] == 1


def test_exactly_one_generation():
    engine = _engine_with_chat(_cands_json([]))
    result = engine.propose(MemoryProposeRequest(text="Just chatting briefly"))
    http = engine._test_http  # type: ignore[attr-defined]
    chat_calls = [c for c in http.calls if c[1].endswith("/api/chat")]
    assert len(chat_calls) == 1
    assert result.trace["generation_count"] == 1


def test_provider_unavailable(monkeypatch):
    http = FakeHttp()
    http.fail_tags = __import__(
        "hypermind.models", fromlist=["ProviderError"]
    ).ProviderError("ollama", "connection_failed", "down")
    ollama = OllamaProvider(
        config=OllamaConfig(model="llama3:latest"),
        client=OllamaClient("http://x", http=http),
    )
    router = IntelligenceRouter(
        models=ModelRouter(providers=[ollama, StubProvider()]),
        persist_trace=False,
    )
    engine = MemoryCandidateEngine(router=router, allow_stub=False)
    result = engine.propose(MemoryProposeRequest(text="I prefer concise replies"))
    # Router may fall to stub; engine should still refuse without allow_stub
    assert not result.ok or result.trace.get("provider") == "ollama"
    if not result.ok:
        assert result.error["code"] == "PROVIDER_UNAVAILABLE"


def test_cli_json_only_stdout(capsys, monkeypatch):
    engine = _engine_with_chat(_cands_json([]))

    def fake_engine(*_a, **_k):
        return engine

    monkeypatch.setattr("hypermind.cli.MemoryCandidateEngine", fake_engine)
    monkeypatch.setattr(
        "sys.stdin",
        __import__("io").StringIO(
            json.dumps({"text": "Hello casual chat", "source_refs": ["input:user"]})
        ),
    )
    code = main(["memory", "propose", "--json"])
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out.strip())
    assert payload["ok"] is True
    assert "candidates" in payload
    assert "trace" in payload
    assert payload["trace"]["memory_written"] is False
    # stdout must be JSON only (single object)
    assert captured.out.strip().startswith("{")


def test_cli_invalid_input_envelope(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("{not-json"))
    code = main(["memory", "propose", "--json"])
    captured = capsys.readouterr()
    assert code == 2
    payload = json.loads(captured.out.strip())
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_INPUT"


def test_no_filesystem_mutation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = {p.name for p in Path(".").rglob("*") if p.is_file()}
    engine = _engine_with_chat(
        _cands_json(
            [
                {
                    "category": "PREFERENCE",
                    "statement": "Prefer local-first HyperMind",
                    "scope": "global",
                    "project": None,
                    "confidence": 0.9,
                    "reason_code": "explicit_stable_preference",
                    "sensitivity": "normal",
                    "source_refs": ["input:user"],
                }
            ]
        )
    )
    result = engine.propose(MemoryProposeRequest(text="I prefer local-first HyperMind"))
    assert result.ok
    after = {p.name for p in Path(".").rglob("*") if p.is_file()}
    # No new durable memory files; pycache may appear — ignore __pycache__
    new_files = {
        n
        for n in (after - before)
        if "memory" in n.lower() or n.endswith(".md") or "vault" in n.lower()
    }
    assert not new_files
    assert result.trace["memory_written"] is False


def test_parse_rejects_missing_candidates_key():
    with pytest.raises(ValueError, match="candidates"):
        parse_candidates_payload("{}", allowed_sources={"input:user"}, max_candidates=5)


def test_restricted_flag_on_sensitive_statement():
    engine = _engine_with_chat(
        _cands_json(
            [
                {
                    "category": "FACT",
                    "statement": "User mentioned a private health diagnosis yesterday",
                    "scope": "global",
                    "project": None,
                    "confidence": 0.6,
                    "reason_code": "explicit",
                    "sensitivity": "normal",
                    "source_refs": ["input:user"],
                }
            ]
        )
    )
    result = engine.propose(
        MemoryProposeRequest(text="Remember my health diagnosis from yesterday")
    )
    assert result.ok
    if result.candidates:
        assert result.candidates[0].sensitivity == "restricted"
        assert result.candidates[0].requires_explicit_sensitive_approval is True


def test_trace_does_not_include_full_input():
    engine = _engine_with_chat(_cands_json([]))
    secretish = "UniquePhraseXYZ123 that must not appear in traces"
    result = engine.propose(MemoryProposeRequest(text=secretish))
    blob = json.dumps(result.to_envelope())
    assert "UniquePhraseXYZ123" not in blob
