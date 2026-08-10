"""Section parsing, scoring, excerpting, and compaction tests."""

from __future__ import annotations

from pathlib import Path

import yaml

from hypermind.agents import AgentRegistry
from hypermind.config.context_config import ContextBudgetConfig, load_context_config
from hypermind.context.budget import apply_budget, dedupe_items
from hypermind.context.retrieval import build_retrieval_query, score_section
from hypermind.context.sections import (
    excerpt_around_terms,
    merge_windows,
    parse_markdown_sections,
)
from hypermind.context.types import ContextItem, ContextKind
from hypermind.context import ContextBuilder, ContextResolver
from hypermind.request import HyperMindRequest


SAMPLE_MD = """# Portfolio Blueprint

Intro text.

## Flagship Projects

Overview of flagship work.

### P-006

Flagship uni design system case.
Hire signal: Systems thinking.

### P-001

Supporting delivery case.

## Hiring Signal

Portfolio-level hire narrative.
"""


def test_heading_hierarchy_parsing():
    sections = parse_markdown_sections(SAMPLE_MD, "blueprint.md")
    p006 = [s for s in sections if s.heading.startswith("P-006")][0]
    assert "Flagship Projects" in p006.heading_path
    assert "P-006" in p006.heading_path
    assert p006.level == 3
    assert p006.start_line > 0
    assert p006.end_line > p006.start_line


def test_h1_h2_h3_extraction():
    sections = parse_markdown_sections(SAMPLE_MD, "f.md")
    levels = {s.heading: s.level for s in sections if s.level}
    assert levels["Portfolio Blueprint"] == 1
    assert levels["Flagship Projects"] == 2
    assert levels["P-006"] == 3


def test_empty_and_malformed_markdown():
    assert parse_markdown_sections("", "x.md") == []
    assert parse_markdown_sections("   \n", "x.md") == []
    plain = parse_markdown_sections("no headings here at all", "x.md")
    assert len(plain) == 1
    assert plain[0].heading == "(document)"


def test_exact_heading_outranks_body():
    sections = parse_markdown_sections(SAMPLE_MD, "blueprint.md")
    rq = build_retrieval_query(
        "hire signal",
        intent="design",
        project="portfolio",
        project_ref=None,
    )
    scored = [
        (score_section(s, rq, kind=ContextKind.CURRENT_STATE).total, s.heading)
        for s in sections
    ]
    scored.sort(reverse=True)
    assert scored[0][1] == "Hiring Signal"


def test_project_id_heading_ranking():
    sections = parse_markdown_sections(SAMPLE_MD, "blueprint.md")
    rq = build_retrieval_query(
        "Review P-006",
        intent="design",
        project="portfolio",
        project_ref="P-006",
    )
    p006 = [s for s in sections if s.heading.startswith("P-006")][0]
    other = [s for s in sections if s.heading.startswith("P-001")][0]
    s1 = score_section(p006, rq, kind=ContextKind.CURRENT_STATE)
    s2 = score_section(other, rq, kind=ContextKind.CURRENT_STATE)
    assert s1.total > s2.total
    assert "project_id_heading" in s1.components


def test_per_section_size_cap_and_excerpt():
    big = "# Title\n\n" + ("keyword alpha " * 400)
    text, excerpted = excerpt_around_terms(big, ["keyword"], max_chars=200)
    assert excerpted is True
    assert len(text) <= 220
    assert "keyword" in text.lower()


def test_overlapping_excerpt_merge():
    merged = merge_windows([(10, 50), (40, 80), (200, 240)], content_len=300)
    assert merged == [(10, 80), (200, 240)]


def test_deduplication_prefers_explicit():
    a = ContextItem(
        id="1",
        source_type="project",
        source_ref="doc.md#p-006",
        title="a",
        content="x",
        priority=20,
        relevance=0.5,
        metadata={"path": "doc.md", "start_line": 1, "end_line": 10},
    )
    b = ContextItem(
        id="2",
        source_type="project",
        source_ref="doc.md#p-006",
        title="b",
        content="y",
        priority=10,
        relevance=0.9,
        metadata={
            "path": "doc.md",
            "start_line": 1,
            "end_line": 10,
            "explicit_ref": True,
        },
    )
    out, dropped = dedupe_items([a, b])
    assert dropped == 1
    assert out[0].id == "2"


def test_context_metrics_on_pack(tmp_path):
    repo = tmp_path / "repo"
    (repo / "hypermind/config").mkdir(parents=True)
    (repo / "portfolio-os/strategy").mkdir(parents=True)
    (repo / "portfolio-os/governance").mkdir(parents=True)
    (repo / "hypermind/config/profile.md").write_text("# Profile\nRole: PD\n", encoding="utf-8")
    (repo / "portfolio-os/governance/Decision_Log.md").write_text(
        "### D-007 — Freeze\n\n| Status | Accepted |\n| Decision | Vault frozen |\n",
        encoding="utf-8",
    )
    (repo / "portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md").write_text(
        SAMPLE_MD, encoding="utf-8"
    )
    ctx = {
        "context": {
            "max_items": 5,
            "max_chars": 5000,
            "max_chars_per_item": 2000,
            "sections": {"max_chars_per_section": 800},
        },
        "roots": {
            "profile": "hypermind/config/profile.md",
            "decision_log": "portfolio-os/governance/Decision_Log.md",
        },
        "privacy": {"deny_path_segments": [], "profile_default": False},
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
    config = load_context_config(repo=repo, context_path=ctx_path, projects_path=proj_path)
    pack = ContextResolver(config=config).resolve(
        HyperMindRequest(raw_input="Review P-006 case study structure"),
        AgentRegistry().get("design_critic"),
        intent="design",
    )
    assert pack.project == "portfolio"
    assert pack.project_id == "P-006"
    assert pack.candidate_sections >= 1
    assert pack.selected_sections == len(pack.items)
    assert pack.documents_touched >= 1
    assert any("P-006" in i.source_ref or "p-006" in i.source_ref.lower() for i in pack.items)
    assert all(i.source_ref and i.title for i in pack.items)
    # Compact vs whole-file style
    assert pack.total_chars < 4500


def test_deterministic_section_ordering(tmp_path):
    # reuse metrics fixture pattern lightly
    repo = tmp_path / "repo"
    (repo / "hypermind/config").mkdir(parents=True)
    (repo / "portfolio-os/strategy").mkdir(parents=True)
    (repo / "portfolio-os/governance").mkdir(parents=True)
    (repo / "hypermind/config/profile.md").write_text("# P\n", encoding="utf-8")
    (repo / "portfolio-os/governance/Decision_Log.md").write_text(
        "### D-007 — Freeze\n\n| Status | Accepted |\nFrozen blueprint.\n",
        encoding="utf-8",
    )
    (repo / "portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md").write_text(
        SAMPLE_MD, encoding="utf-8"
    )
    ctx_path = tmp_path / "c.yaml"
    proj_path = tmp_path / "p.yaml"
    ctx_path.write_text(
        yaml.safe_dump(
            {
                "context": {
                    "max_items": 6,
                    "max_chars": 6000,
                    "sections": {"max_chars_per_section": 900},
                },
                "roots": {
                    "profile": "hypermind/config/profile.md",
                    "decision_log": "portfolio-os/governance/Decision_Log.md",
                },
                "privacy": {"deny_path_segments": []},
            }
        ),
        encoding="utf-8",
    )
    proj_path.write_text(
        yaml.safe_dump(
            {
                "projects": {
                    "portfolio": {
                        "aliases": ["p-006", "case study"],
                        "roots": ["portfolio-os/"],
                        "priority_docs": ["portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md"],
                        "project_ids": {
                            "P-006": {
                                "aliases": ["p-006"],
                                "hint_docs": [
                                    "portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md"
                                ],
                            }
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    config = load_context_config(repo=repo, context_path=ctx_path, projects_path=proj_path)
    resolver = ContextResolver(config=config)
    req = HyperMindRequest(raw_input="Review P-006 case study structure")
    agent = AgentRegistry().get("design_critic")
    a = resolver.resolve(req, agent, intent="design")
    b = resolver.resolve(req, agent, intent="design")
    assert [i.source_ref for i in a.items] == [i.source_ref for i in b.items]


def test_budget_section_cap():
    items = [
        ContextItem(
            id="1",
            source_type="project",
            source_ref="a.md#x",
            title="x",
            content="Z" * 5000,
            priority=10,
            relevance=0.9,
            kind=ContextKind.CURRENT_STATE,
            metadata={},
        )
    ]
    pack = apply_budget(
        items,
        ContextBudgetConfig(
            max_items=3, max_chars=10000, max_chars_per_item=5000, max_chars_per_section=500
        ),
    )
    assert len(pack.items[0].content) <= 520
    assert pack.items[0].metadata.get("excerpted") is True
