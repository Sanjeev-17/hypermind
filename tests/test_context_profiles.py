"""Context pack profile tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from hypermind.agents import AgentRegistry
from hypermind.cli import main
from hypermind.config.context_config import load_context_config
from hypermind.context import ContextBuilder, ContextResolver
from hypermind.context.profiles import ContextProfileError, ContextProfileResolver
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest


def _config(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "hypermind/config").mkdir(parents=True)
    (repo / "portfolio-os/governance").mkdir(parents=True)
    (repo / "portfolio-os/strategy").mkdir(parents=True)
    (repo / "hypermind/config/profile.md").write_text(
        "# Profile\nRole: Senior PD\n", encoding="utf-8"
    )
    (repo / "portfolio-os/governance/Decision_Log.md").write_text(
        "### D-007 — Freeze\n\n| Status | Accepted |\nVault frozen for portfolio structure.\n",
        encoding="utf-8",
    )
    (repo / "portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md").write_text(
        "# Blueprint\n\n## Selected projects\n\n### P-006\n\nFlagship systems.\n",
        encoding="utf-8",
    )
    ctx = {
        "context": {
            "max_items": 8,
            "max_chars": 8000,
            "override_max_chars": 12000,
            "override_max_items": 12,
            "sections": {"max_chars_per_section": 1500},
        },
        "context_profiles": {
            "general": {
                "max_items": 4,
                "max_chars": 3000,
                "decisions_max": 1,
                "include_profile": False,
            },
            "design": {
                "max_items": 5,
                "max_chars": 4000,
                "decisions_max": 2,
                "include_profile": True,
                "preferred_source_types": ["current_state", "decision", "profile"],
            },
            "writing": {
                "max_items": 5,
                "max_chars": 4000,
                "decisions_max": 2,
                "include_profile": True,
            },
            "coding": {
                "max_items": 4,
                "max_chars": 3000,
                "decisions_max": 1,
                "include_profile": False,
            },
            "planning": {
                "max_items": 6,
                "max_chars": 4500,
                "decisions_max": 2,
                "include_profile": True,
            },
        },
        "roots": {
            "profile": "hypermind/config/profile.md",
            "decision_log": "portfolio-os/governance/Decision_Log.md",
        },
        "privacy": {"deny_path_segments": []},
    }
    projects = {
        "projects": {
            "portfolio": {
                "aliases": ["portfolio", "p-006", "case study"],
                "roots": ["portfolio-os/"],
                "priority_docs": ["portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md"],
                "project_ids": {
                    "P-006": {
                        "aliases": ["p-006"],
                        "hint_docs": ["portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md"],
                    }
                },
            }
        }
    }
    ctx_path = tmp_path / "c.yaml"
    proj_path = tmp_path / "p.yaml"
    ctx_path.write_text(yaml.safe_dump(ctx), encoding="utf-8")
    proj_path.write_text(yaml.safe_dump(projects), encoding="utf-8")
    # Seed model caps via writing models.yaml beside package is hard; set on config after load
    config = load_context_config(repo=repo, context_path=ctx_path, projects_path=proj_path)
    config = type(config)(
        budget=config.budget,
        roots=config.roots,
        privacy=config.privacy,
        projects=config.projects,
        profiles=config.profiles,
        model_context_caps={"llama3:latest": 3500},
        override_max_chars=config.override_max_chars,
        override_max_items=config.override_max_items,
    )
    return config


@pytest.mark.parametrize(
    "intent,expected",
    [
        ("design", "design"),
        ("writing", "writing"),
        ("coding", "coding"),
        ("planning", "planning"),
        ("general", "general"),
        ("unknownish", "general"),
    ],
)
def test_profile_selection_by_intent(tmp_path, intent, expected):
    config = _config(tmp_path)
    resolver = ContextProfileResolver(config)
    profile = resolver.resolve(
        intent, HyperMindRequest(raw_input="hello world test"), project=None
    )
    assert profile.id == expected


def test_profile_config_loading(tmp_path):
    config = _config(tmp_path)
    ids = {p.id for p in config.profiles}
    assert "design" in ids
    assert "coding" in ids
    design = next(p for p in config.profiles if p.id == "design")
    assert design.max_chars == 4000
    assert design.decisions_max == 2
    assert design.include_profile is True


def test_profile_specific_caps_and_decisions(tmp_path):
    config = _config(tmp_path)
    builder = ContextBuilder(ContextResolver(config=config))
    design = builder.build(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    assert design.context_profile == "design"
    assert design.context_budget_chars == 4000
    assert design.context_budget_items == 5
    assert design.total_chars <= 4000
    assert len(design.items) <= 5
    assert sum(1 for i in design.items if i.kind.value == "DECISION") <= 2
    assert any(i.source_type == "profile" for i in design.items)

    coding = builder.build(
        HyperMindRequest(raw_input="Debug authentication module"),
        AgentRegistry().get("coder"),
        intent="coding",
    )
    assert coding.context_profile == "coding"
    assert coding.context_budget_chars == 3000
    assert all(i.source_type != "profile" for i in coding.items)
    assert sum(1 for i in coding.items if i.kind.value == "DECISION") <= 1


def test_budget_is_ceiling_not_target(tmp_path):
    config = _config(tmp_path)
    pack = ContextBuilder(ContextResolver(config=config)).build(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    assert pack.total_chars < pack.context_budget_chars
    assert pack.context_utilization < 1.0


def test_explicit_profile_override(tmp_path):
    config = _config(tmp_path)
    pack = ContextBuilder(ContextResolver(config=config)).build(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
        context_profile="coding",
    )
    assert pack.context_profile == "coding"
    assert pack.context_budget_chars == 3000
    assert all(i.source_type != "profile" for i in pack.items)


def test_invalid_profile_override(tmp_path):
    config = _config(tmp_path)
    with pytest.raises(ContextProfileError):
        ContextProfileResolver(config).resolve(
            "design",
            HyperMindRequest(raw_input="x"),
            override_profile="not-a-profile",
        )


def test_invalid_max_chars_override(tmp_path):
    config = _config(tmp_path)
    with pytest.raises(ContextProfileError):
        ContextProfileResolver(config).resolve(
            "design",
            HyperMindRequest(raw_input="x"),
            override_max_chars=50,
        )


def test_model_cap_applied(tmp_path):
    config = _config(tmp_path)
    profile = ContextProfileResolver(config).resolve(
        "design",
        HyperMindRequest(raw_input="Review P-006"),
        model_name="llama3:latest",
    )
    assert profile.max_chars == 3500  # min(4000, 3500)
    assert profile.model_cap_chars == 3500


def test_trace_includes_profile_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    # Use real repo for routing smoke — profile metadata from IntelligenceRouter
    result = IntelligenceRouter().route("Review P-006 case study structure")
    assert result.trace is not None
    assert result.trace.metadata.get("context_profile") == "design"
    assert "context_budget_chars" in result.trace.metadata
    assert "context_utilization" in result.trace.metadata
    assert result.context is not None
    assert result.context.context_profile == "design"


def test_cli_profile_override_and_invalid(capsys, monkeypatch):
    monkeypatch.setenv("HYPERMIND_OLLAMA_AVAILABLE", "0")
    code = main(
        ["context", "Review P-006 case study structure", "--context-profile", "coding"]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "Context profile: coding" in out

    code = main(["context", "hello", "--context-profile", "nope"])
    err = capsys.readouterr().err
    assert code == 2
    assert "Unknown context profile" in err


def test_no_agent_identity_in_pack_by_default(tmp_path):
    config = _config(tmp_path)
    pack = ContextBuilder(ContextResolver(config=config)).build(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    assert all(not i.source_ref.startswith("agent:") for i in pack.items)
