"""Phase 7A decision engine tests — no Decision Log writes."""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest import mock

import pytest
import yaml

from hypermind.agents import AgentRegistry
from hypermind.cli import main
from hypermind.config.context_config import load_context_config
from hypermind.context import ContextBuilder
from hypermind.context.resolver import DecisionSource, _parse_accepted_decisions
from hypermind.decisions import (
    DecisionAnalyzeEngine,
    DecisionAnalyzeRequest,
    DecisionRecord,
    DecisionResolver,
    DecisionStatus,
    analyze_against_active,
    is_historical_query,
    parse_decision_log,
)
from hypermind.decisions.types import DecisionAction, DecisionRelationship
from hypermind.request import HyperMindRequest


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


SAMPLE_LOG = """# Decisions

### D-001 — Local-first routing

| Field | Value |
|-------|-------|
| Decision ID | D-001 |
| Title | Local-first routing |
| Decision | Use local-first model routing. |
| Status | Accepted |
| Date | 2026-08-01 |

### D-002 — Draft

| Status | Proposed |
| Decision | Should be ignored.

### D-003 — Old cloud policy

| Field | Value |
|-------|-------|
| Decision ID | D-003 |
| Title | Old cloud policy |
| Decision | Prefer cloud models for everything. |
| Status | Superseded |
| Superseded By | D-001 |
| Date | 2026-07-01 |

### D-007 — Freeze vault

| Field | Value |
|-------|-------|
| Decision ID | D-007 |
| Title | Freeze HyperMind Vault v1.0 |
| Decision | Portfolio OS v1.0 is frozen. |
| Status | Accepted |
| Date | 2026-08-02 |

### D-099 — Broken link

| Field | Value |
|-------|-------|
| Decision ID | D-099 |
| Title | Broken supersession |
| Decision | Something historical. |
| Status | Superseded |
| Superseded By | D-MISSING |
| Date | 2026-06-01 |

### D-BAD — No status row

Just some prose without a status field.
"""


GLOBAL_LOG = """# Decisions

### D-010 — Global privacy

| Field | Value |
|-------|-------|
| Decision ID | D-010 |
| Title | Global privacy |
| Decision | Never auto-load Health notes. |
| Scope | global |
| Status | Accepted |
| Date | 2026-08-01 |

### D-011 — Portfolio only

| Field | Value |
|-------|-------|
| Decision ID | D-011 |
| Title | Portfolio only |
| Decision | Use Hiring Scorecard on L3. |
| Project | portfolio |
| Status | Accepted |
| Date | 2026-08-01 |
"""


def test_parse_active_and_superseded():
    records = parse_decision_log(SAMPLE_LOG)
    by_id = {r.id: r for r in records}
    assert "D-001" in by_id
    assert by_id["D-001"].status == DecisionStatus.ACTIVE.value
    assert "D-002" not in by_id  # Proposed skipped
    assert by_id["D-003"].status == DecisionStatus.SUPERSEDED.value
    assert by_id["D-003"].superseded_by == "D-001"
    assert by_id["D-007"].frozen is True
    assert "D-BAD" not in by_id


def test_malformed_historical_does_not_crash():
    raw = "### D-X — Broken\n\n| Status | Accepted |\n"
    # Missing decision statement — still parseable
    records = parse_decision_log(
        "### D-010 — Odd\n\n| Status | Accepted |\n| Decision ID | D-010 |\n"
    )
    assert len(records) == 1
    assert records[0].statement  # falls back to title


def test_active_retrieval_excludes_superseded():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    active = resolver.get_active_decisions()
    ids = {r.id for r in active}
    assert "D-001" in ids
    assert "D-007" in ids
    assert "D-003" not in ids
    assert "D-099" not in ids


def test_historical_inspect_includes_superseded():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    hist = resolver.get_inspectable(include_superseded=True)
    ids = {r.id for r in hist}
    assert "D-003" in ids
    assert "D-001" in ids


def test_broken_supersession_link_safe():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    chain = resolver.resolve_supersession_chain("D-099")
    assert chain[0].id == "D-099"
    # Missing D-MISSING must not raise
    assert all(isinstance(r, DecisionRecord) for r in chain)


def test_create_proposal_new():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver, allow_stub=True)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Adopt a purple accent for marketing emails only.",
            project="portfolio",
            allow_model_assist=False,
        )
    )
    assert result.ok
    assert result.proposal is not None
    assert result.proposal.action == DecisionAction.CREATE.value
    assert result.trace["decision_written"] is False


def test_duplicate_proposal():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Use local-first model routing.",
            project="portfolio",
            allow_model_assist=False,
        )
    )
    assert result.proposal.action == DecisionAction.REJECT_AS_DUPLICATE.value
    assert result.proposal.relationship == DecisionRelationship.DUPLICATE.value
    assert "D-001" in result.proposal.related_decisions


def test_conflict_proposal():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Change Portfolio OS v1.0 without a version bump.",
            project="portfolio",
            allow_model_assist=False,
        )
    )
    assert result.proposal.action == DecisionAction.FLAG_CONFLICT.value
    assert result.proposal.relationship == DecisionRelationship.POSSIBLE_CONFLICT.value
    assert result.proposal.decision_conflict is True
    assert "D-007" in result.proposal.related_decisions


def test_supersession_proposal():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement=(
                "Going forward, replace local-first routing: "
                "prefer cloud-first model routing for all HyperMind tasks."
            ),
            project="hypermind",
            allow_model_assist=False,
        )
    )
    assert result.proposal.relationship in {
        DecisionRelationship.POSSIBLE_SUPERSESSION.value,
        DecisionRelationship.POSSIBLE_CONFLICT.value,
    }
    assert "D-001" in result.proposal.related_decisions
    if result.proposal.relationship == DecisionRelationship.POSSIBLE_SUPERSESSION.value:
        assert result.proposal.action == DecisionAction.SUPERSEDE.value


def test_frozen_decision_conflict_elevated():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Unfreeze Portfolio OS v1.0 and restructure freely.",
            project="portfolio",
            allow_model_assist=False,
        )
    )
    assert result.proposal.decision_conflict is True
    assert result.proposal.reason_code == "conflicts_with_frozen_decision"
    assert result.proposal.metadata.get("frozen_related") is True


def test_project_scope_isolation():
    resolver = DecisionResolver.from_markdown(GLOBAL_LOG)
    portfolio = resolver.get_active_decisions(scope="project", project="portfolio")
    ids = {r.id for r in portfolio}
    assert "D-011" in ids
    assert "D-010" in ids  # global included for project filter
    global_only = resolver.get_active_decisions(scope="global", project=None)
    assert {r.id for r in global_only} == {"D-010"}


def test_global_scope():
    resolver = DecisionResolver.from_markdown(GLOBAL_LOG)
    g = resolver.get_active_decisions(scope="global")
    assert len(g) == 1
    assert g[0].id == "D-010"


def test_decision_candidate_bridge():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="ignored placeholder",
            candidate={
                "category": "DECISION_CANDIDATE",
                "statement": "Use local-first model routing.",
                "scope": "project",
                "project": "portfolio",
                "source_refs": ["input:user"],
            },
            allow_model_assist=False,
        )
    )
    assert result.proposal.candidate["statement"] == "Use local-first model routing."
    assert result.proposal.action == DecisionAction.REJECT_AS_DUPLICATE.value


def test_no_durable_write(tmp_path):
    log = tmp_path / "Decision_Log.md"
    log.write_text(SAMPLE_LOG, encoding="utf-8")
    before = log.read_text(encoding="utf-8")
    engine = DecisionAnalyzeEngine(decision_log_path=log)
    engine.analyze(
        DecisionAnalyzeRequest(
            statement="Prefer cloud models by default for routine tasks.",
            project="hypermind",
            allow_model_assist=False,
        )
    )
    assert log.read_text(encoding="utf-8") == before
    # No sidecar write artifacts
    assert list(tmp_path.glob("*")) == [log]


def test_machine_json_stdout_only(capsys):
    payload = {
        "statement": "Adopt a one-off naming convention for temporary scratch notes.",
        "project": "portfolio",
        "source_refs": ["input:user"],
        "allow_model_assist": False,
    }
    from hypermind.decisions.types import DecisionAnalyzeResult, DecisionProposal

    with mock.patch("hypermind.cli.DecisionAnalyzeEngine") as Eng:
        Eng.return_value.analyze.return_value = DecisionAnalyzeResult(
            ok=True,
            request_id="req-test",
            proposal=DecisionProposal(
                action="CREATE",
                candidate={"statement": payload["statement"]},
                relationship="NEW",
                reason_code="no_overlapping_active_decision",
            ),
            trace={"decision_written": False, "model_generation_count": 0},
        )
        with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))):
            code = main(["decision", "analyze", "--json"])
    out = capsys.readouterr()
    assert code == 0
    data = json.loads(out.out.strip())
    assert data["ok"] is True
    assert "proposal" in data
    assert out.out.strip().startswith("{")


def test_model_assist_max_one_generation():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    calls = {"n": 0}

    def classifier(new_s: str, old_s: str) -> dict:
        calls["n"] += 1
        return {
            "relationship": "compatible",
            "reason_code": "model_says_ok",
            "confidence": 0.7,
        }

    # Craft ambiguous hit by using overlapping but vague statement — force assist path
    # via low-confidence COMPATIBLE from deterministic layer
    engine = DecisionAnalyzeEngine(
        resolver=resolver, model_classifier=classifier, allow_stub=True
    )
    # Statement that shares tokens with D-001 without hard cues
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Model routing defaults matter for HyperMind local providers.",
            project="hypermind",
            allow_model_assist=True,
        )
    )
    assert result.ok
    assert result.trace["model_generation_count"] <= 1
    assert calls["n"] <= 1


def test_deterministic_obvious_conflict_no_model():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    calls = {"n": 0}

    def classifier(new_s: str, old_s: str) -> dict:
        calls["n"] += 1
        return {"relationship": "unrelated", "reason_code": "should_not_run", "confidence": 0.9}

    engine = DecisionAnalyzeEngine(resolver=resolver, model_classifier=classifier)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Change Portfolio OS v1.0 without a version bump.",
            allow_model_assist=True,
        )
    )
    assert result.proposal.relationship == DecisionRelationship.POSSIBLE_CONFLICT.value
    assert calls["n"] == 0
    assert result.trace["model_generation_count"] == 0


def test_trace_metadata():
    resolver = DecisionResolver.from_markdown(SAMPLE_LOG)
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement="Use local-first model routing.",
            project="portfolio",
            allow_model_assist=False,
        )
    )
    t = result.trace
    assert t["request_id"]
    assert t["project"] == "portfolio"
    assert t["scope"] == "project"
    assert "active_decisions_inspected" in t
    assert t["relationship"] == DecisionRelationship.DUPLICATE.value
    assert "D-001" in t["related_decision_ids"]
    assert t["model_generation_count"] == 0
    assert "duration_ms" in t
    assert t["status"] == "completed"
    assert t["decision_written"] is False


def test_historical_query_detection():
    assert is_historical_query("What did we decide before D-007?")
    assert is_historical_query("What decision did D-012 replace?")
    assert is_historical_query("How did our model strategy change?")
    assert not is_historical_query("What is the current writing standard?")


def _context_fixture(tmp_path: Path, log_body: str) -> ContextBuilder:
    repo = tmp_path / "repo"
    _write(repo / "hypermind" / "config" / "profile.md", "# Profile\n\nRole: designer\n")
    _write(repo / "portfolio-os" / "governance" / "Decision_Log.md", log_body)
    _write(
        repo / "portfolio-os" / "strategy" / "PORTFOLIO_BLUEPRINT.md",
        "# Blueprint\n\n## Selected\n\nCurrent portfolio structure notes.\n",
    )
    context_yaml = {
        "context": {"max_items": 8, "max_chars": 8000, "max_chars_per_item": 2000},
        "roots": {
            "profile": "hypermind/config/profile.md",
            "decision_log": "portfolio-os/governance/Decision_Log.md",
            "obsidian_vault": None,
        },
        "privacy": {"deny_path_segments": ["Health"], "profile_default": False},
    }
    projects_yaml = {
        "projects": {
            "portfolio": {
                "aliases": ["portfolio"],
                "roots": ["portfolio-os/"],
                "priority_docs": ["portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md"],
            }
        }
    }
    ctx_path = tmp_path / "context.yaml"
    proj_path = tmp_path / "projects.yaml"
    ctx_path.write_text(yaml.safe_dump(context_yaml), encoding="utf-8")
    proj_path.write_text(yaml.safe_dump(projects_yaml), encoding="utf-8")
    cfg = load_context_config(
        repo=repo, context_path=ctx_path, projects_path=proj_path
    )
    from hypermind.context.resolver import ContextResolver

    return ContextBuilder(ContextResolver(config=cfg))


def test_context_engine_prioritizes_active(tmp_path):
    builder = _context_fixture(tmp_path, SAMPLE_LOG)
    agent = AgentRegistry().get("chief_of_staff")
    pack = builder.build(
        HyperMindRequest(
            raw_input="What decisions freeze the portfolio vault structure?",
            project="portfolio",
            intent="planning",
        ),
        agent,
        intent="planning",
        context_profile="planning",
    )
    decision_items = [i for i in pack.items if i.source_type == "decision"]
    assert decision_items
    statuses = {i.metadata.get("status") for i in decision_items}
    assert DecisionStatus.SUPERSEDED.value not in statuses
    assert DecisionStatus.ACTIVE.value in statuses


def test_superseded_only_in_history_mode(tmp_path):
    builder = _context_fixture(tmp_path, SAMPLE_LOG)
    agent = AgentRegistry().get("chief_of_staff")
    normal = builder.build(
        HyperMindRequest(
            raw_input="Remind me about local-first model routing decisions.",
            project="portfolio",
            intent="knowledge",
        ),
        agent,
        intent="knowledge",
    )
    normal_ids = [
        i.metadata.get("decision_id")
        for i in normal.items
        if i.source_type == "decision"
    ]
    assert "D-003" not in normal_ids

    history = builder.build(
        HyperMindRequest(
            raw_input="What decision did D-001 replace? Show superseded history.",
            project="portfolio",
            intent="knowledge",
        ),
        agent,
        intent="knowledge",
    )
    hist_meta = [
        i.metadata
        for i in history.items
        if i.source_type == "decision"
    ]
    # History mode may include superseded when relevant
    assert any(
        m.get("status") == DecisionStatus.SUPERSEDED.value or m.get("historical")
        for m in hist_meta
    ) or any(m.get("decision_id") == "D-003" for m in hist_meta)


def test_legacy_parse_accepted_compat():
    entries = _parse_accepted_decisions(SAMPLE_LOG)
    ids = {e["id"] for e in entries}
    assert "D-001" in ids
    assert "D-003" not in ids


def test_smoke_local_vs_cloud_conflict():
    """Synthetic live-style smoke without persistence."""
    resolver = DecisionResolver(
        [
            DecisionRecord(
                id="D-SYN",
                title="Local-first",
                statement="Use local-first model routing.",
                scope="project",
                project="hypermind",
                status=DecisionStatus.ACTIVE.value,
            )
        ]
    )
    engine = DecisionAnalyzeEngine(resolver=resolver)
    result = engine.analyze(
        DecisionAnalyzeRequest(
            statement=(
                "For all routine HyperMind tasks, prefer cloud models by default."
            ),
            project="hypermind",
            allow_model_assist=False,
        )
    )
    assert result.proposal.relationship in {
        DecisionRelationship.POSSIBLE_CONFLICT.value,
        DecisionRelationship.POSSIBLE_SUPERSESSION.value,
    }
    assert result.trace["decision_written"] is False
