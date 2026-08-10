"""Context Engine tests — fixture Markdown only; no real vault required."""

from __future__ import annotations

from pathlib import Path

import yaml

from hypermind.agents import AgentRegistry
from hypermind.cli import main
from hypermind.config.context_config import load_context_config
from hypermind.context import ContextBuilder, ContextKind, ContextResolver
from hypermind.context.budget import apply_budget
from hypermind.context.projects import ProjectIndex
from hypermind.context.types import ContextItem
from hypermind.executor import HyperMindExecutor
from hypermind.models.adapters import OllamaProvider, StubProvider
from hypermind.models.ollama_client import OllamaClient
from hypermind.models.router import ModelRouter
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest
from tests.test_ollama import FakeHttp, _chat_payload


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_repo(tmp_path: Path) -> tuple[Path, object]:
    repo = tmp_path / "repo"
    _write(
        repo / "hypermind" / "config" / "profile.md",
        "# Profile\n\n- Role: Senior Product Designer\n- Preference: concise\n",
    )
    _write(
        repo / "portfolio-os" / "governance" / "Decision_Log.md",
        """# Decisions

### D-001 — Freeze portfolio structure

| Status | Accepted |
| Decision | Portfolio OS v1.0 is frozen. |

### D-002 — Draft idea

| Status | Proposed |
| Decision | Ignore me.
""",
    )
    _write(
        repo / "portfolio-os" / "strategy" / "PORTFOLIO_BLUEPRINT.md",
        "# Portfolio Blueprint\n\n## Selected projects\n\n### P-006\n\nFlagship design system case.\n\nHire signal: Systems thinking.\n\n### P-001\n\nSupporting Taco Bell.\n",
    )
    _write(
        repo / "portfolio-os" / "strategy" / "EXPERIENCE_BLUEPRINT.md",
        "# Experience Blueprint\n\n## Case Study Narrative\n\nP-006 journey structure notes.\n",
    )
    _write(
        repo / "portfolio-os" / "strategy" / "PROJECT_INVENTORY.md",
        "# Project Inventory\n\n### P-006\n\nUni design system inventory row.\n",
    )
    _write(
        repo / "docs" / "intelligence-routing.md",
        "# Routing\n\nHyperMind architecture overview.\n",
    )
    _write(
        repo / "Areas" / "Health" / "secret.md",
        "# Health\n\nShould never auto-load.\n",
    )

    context_yaml = {
        "context": {
            "max_items": 8,
            "max_chars": 12000,
            "max_chars_per_item": 2000,
            "sections": {"max_chars_per_section": 1200},
        },
        "roots": {
            "profile": "hypermind/config/profile.md",
            "decision_log": "portfolio-os/governance/Decision_Log.md",
            "obsidian_vault": None,
        },
        "privacy": {
            "deny_path_segments": ["Health", "Dating", "health"],
            "profile_default": False,
        },
    }
    projects_yaml = {
        "projects": {
            "hypermind": {
                "aliases": ["hypermind", "mission control"],
                "roots": ["docs/"],
                "priority_docs": ["docs/intelligence-routing.md"],
            },
            "portfolio": {
                "aliases": ["portfolio", "p-006", "design system", "case study"],
                "roots": ["portfolio-os/"],
                "priority_docs": [
                    "portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md",
                    "portfolio-os/strategy/EXPERIENCE_BLUEPRINT.md",
                    "portfolio-os/strategy/PROJECT_INVENTORY.md",
                    "portfolio-os/governance/Decision_Log.md",
                ],
                "project_ids": {
                    "P-006": {
                        "aliases": ["p-006", "design system"],
                        "hint_docs": [
                            "portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md",
                            "portfolio-os/strategy/EXPERIENCE_BLUEPRINT.md",
                            "portfolio-os/strategy/PROJECT_INVENTORY.md",
                        ],
                    },
                    "P-001": {
                        "aliases": ["p-001", "taco bell"],
                        "hint_docs": ["portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md"],
                    },
                },
            },
        }
    }
    ctx_path = tmp_path / "context.yaml"
    proj_path = tmp_path / "projects.yaml"
    ctx_path.write_text(yaml.safe_dump(context_yaml), encoding="utf-8")
    proj_path.write_text(yaml.safe_dump(projects_yaml), encoding="utf-8")
    config = load_context_config(
        repo=repo, context_path=ctx_path, projects_path=proj_path
    )
    return repo, config


def test_project_alias_resolution(tmp_path):
    _, config = _fixture_repo(tmp_path)
    index = ProjectIndex(config)
    res = index.resolve("Help me plan the portfolio next steps")
    assert res.project is not None
    assert res.project.id == "portfolio"


def test_explicit_project_id_resolution(tmp_path):
    _, config = _fixture_repo(tmp_path)
    index = ProjectIndex(config)
    res = index.resolve("Review P-006 case study structure")
    assert res.project is not None
    assert res.project.id == "portfolio"
    assert res.project_id is not None
    assert res.project_id.id == "P-006"


def test_profile_included_for_design(tmp_path):
    _, config = _fixture_repo(tmp_path)
    resolver = ContextResolver(config=config)
    agent = AgentRegistry().get("design_critic")
    pack = resolver.resolve(
        HyperMindRequest(raw_input="Critique the portfolio hero composition"),
        agent,
        intent="design",
    )
    assert any(i.source_type == "profile" for i in pack.items)


def test_profile_excluded_for_coding(tmp_path):
    _, config = _fixture_repo(tmp_path)
    resolver = ContextResolver(config=config)
    agent = AgentRegistry().get("coder")
    pack = resolver.resolve(
        HyperMindRequest(raw_input="Debug the authentication module"),
        agent,
        intent="coding",
    )
    assert all(i.source_type != "profile" for i in pack.items)


def test_decision_priority_over_reference(tmp_path):
    items = [
        ContextItem(
            id="r",
            source_type="markdown",
            source_ref="notes/old.md",
            title="Old",
            content="x" * 100,
            priority=50,
            kind=ContextKind.REFERENCE,
        ),
        ContextItem(
            id="d",
            source_type="decision",
            source_ref="decisions#D-001",
            title="Freeze",
            content="DECISION: frozen",
            priority=20,
            kind=ContextKind.DECISION,
            relevance=0.9,
        ),
    ]
    from hypermind.config.context_config import ContextBudgetConfig

    pack = apply_budget(items, ContextBudgetConfig(max_items=1, max_chars=5000))
    assert pack.items[0].kind == ContextKind.DECISION


def test_project_context_retrieval(tmp_path):
    _, config = _fixture_repo(tmp_path)
    resolver = ContextResolver(config=config)
    agent = AgentRegistry().get("design_critic")
    pack = resolver.resolve(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        agent,
        intent="design",
    )
    assert pack.project == "portfolio"
    assert pack.project_id == "P-006"
    assert any("PORTFOLIO_BLUEPRINT" in i.source_ref for i in pack.items)
    assert any(i.kind == ContextKind.DECISION for i in pack.items)


def test_context_item_provenance(tmp_path):
    _, config = _fixture_repo(tmp_path)
    pack = ContextResolver(config=config).resolve(
        HyperMindRequest(raw_input="Review P-006 case study"),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    for item in pack.items:
        assert item.source_type
        assert item.source_ref
        assert item.title
        assert item.content


def test_max_item_enforcement(tmp_path):
    _, config = _fixture_repo(tmp_path)
    builder = ContextBuilder(ContextResolver(config=config))
    pack = builder.build(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
        max_items=2,
        max_chars=50000,
    )
    assert len(pack.items) <= 2
    assert pack.truncated is True


def test_max_character_enforcement(tmp_path):
    _, config = _fixture_repo(tmp_path)
    pack = ContextBuilder(ContextResolver(config=config)).build(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
        max_items=20,
        max_chars=400,
    )
    assert pack.total_chars <= 400
    assert pack.truncated is True


def test_deterministic_ordering(tmp_path):
    _, config = _fixture_repo(tmp_path)
    resolver = ContextResolver(config=config)
    req = HyperMindRequest(raw_input="Review P-006 case study structure")
    agent = AgentRegistry().get("design_critic")
    a = resolver.resolve(req, agent, intent="design")
    b = resolver.resolve(req, agent, intent="design")
    assert [i.source_ref for i in a.items] == [i.source_ref for i in b.items]


def test_missing_project_still_safe(tmp_path):
    _, config = _fixture_repo(tmp_path)
    pack = ContextResolver(config=config).resolve(
        HyperMindRequest(raw_input="totally unrelated xyzzy request"),
        AgentRegistry().get("coder"),
        intent="coding",
    )
    assert pack.project is None
    assert pack.context_profile in {"coding", "general", None} or pack.intent == "coding"
    # Agent identity is system-instruction only — pack may be empty
    assert pack.total_chars >= 0


def test_missing_source_file_skipped(tmp_path):
    _, config = _fixture_repo(tmp_path)
    # Point priority doc at missing file via request context_refs only
    pack = ContextResolver(config=config).resolve(
        HyperMindRequest(
            raw_input="Review portfolio",
            context_refs=["portfolio-os/strategy/DOES_NOT_EXIST.md"],
        ),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    assert all("DOES_NOT_EXIST" not in i.source_ref for i in pack.items)


def test_privacy_denies_health_path(tmp_path):
    repo, config = _fixture_repo(tmp_path)
    pack = ContextResolver(config=config).resolve(
        HyperMindRequest(
            raw_input="Review portfolio",
            context_refs=["Areas/Health/secret.md"],
        ),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    assert all("Health" not in i.source_ref for i in pack.items)
    assert (repo / "Areas" / "Health" / "secret.md").exists()


def test_cli_context_no_model(capsys, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    code = main(["context", "Review P-006 case study structure"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Intent: design" in out
    assert "Project: portfolio" in out
    assert "P-006" in out
    assert "Context profile: design" in out
    assert "Budget:" in out
    assert "Selected:" in out
    assert "Response:" not in out


def test_executor_receives_context_pack(tmp_path):
    _, config = _fixture_repo(tmp_path)
    http = FakeHttp()
    http.chat = _chat_payload("ok")
    from hypermind.config import OllamaConfig

    ollama = OllamaProvider(
        config=OllamaConfig(model="qwen3:8b"),
        client=OllamaClient("http://x", http=http),
    )
    router = IntelligenceRouter(
        models=ModelRouter(providers=[ollama, StubProvider()]),
        context=ContextBuilder(ContextResolver(config=config)),
    )
    result = HyperMindExecutor(router=router).execute(
        "Review P-006 case study structure"
    )
    assert result.ok
    assert result.route.context is not None
    assert result.route.context.project == "portfolio"
    body = __import__("json").loads(
        [c for c in http.calls if c[1].endswith("/api/chat")][0][2]
    )
    system_msgs = [m["content"] for m in body["messages"] if m["role"] == "system"]
    user_msgs = [m["content"] for m in body["messages"] if m["role"] == "user"]
    joined = "\n".join(system_msgs + user_msgs)
    assert "[CONTEXT]" in joined
    assert "SOURCE:" in joined
    assert "USER REQUEST:" in joined


def test_legacy_bounds_api(tmp_path):
    _, config = _fixture_repo(tmp_path)
    pack = ContextBuilder(ContextResolver(config=config)).build(
        HyperMindRequest(raw_input="hello", project="hypermind", context_refs=[]),
        AgentRegistry().get("coder"),
        intent="coding",
        max_items=5,
        max_tokens=100,
    )
    assert len(pack.items) <= 5
    assert pack.approx_tokens <= 100
