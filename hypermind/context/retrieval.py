"""Internal retrieval query + section scoring (deterministic)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from hypermind.context.sections import MarkdownSection
from hypermind.context.types import ContextKind


@dataclass
class RetrievalQuery:
    raw_query: str
    intent: str
    project: str | None = None
    project_ref: str | None = None
    explicit_terms: list[str] = field(default_factory=list)
    preferred_source_types: list[str] = field(default_factory=list)
    preferred_sections: list[str] = field(default_factory=list)


@dataclass
class ScoreBreakdown:
    total: float
    components: dict[str, float] = field(default_factory=dict)

    def add(self, name: str, value: float) -> None:
        if value:
            self.components[name] = self.components.get(name, 0.0) + value
            self.total += value


def load_vocabulary() -> dict[str, list[str]]:
    try:
        text = (
            resources.files("hypermind.config")
            .joinpath("vocabulary.yaml")
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, TypeError, AttributeError):
        text = Path(__file__).resolve().parents[1].joinpath(
            "config", "vocabulary.yaml"
        ).read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    return {
        "design_terms": [str(t).lower() for t in (data.get("design_terms") or [])],
        "writing_action_terms": [
            str(t).lower() for t in (data.get("writing_action_terms") or [])
        ],
    }


def build_retrieval_query(
    raw: str,
    *,
    intent: str,
    project: str | None,
    project_ref: str | None,
    aliases: list[str] | None = None,
) -> RetrievalQuery:
    vocab = load_vocabulary()
    lowered = raw.lower()
    terms: list[str] = []
    if project_ref:
        terms.append(project_ref.lower())
    for alias in aliases or []:
        if alias and alias.lower() in lowered:
            terms.append(alias.lower())
    for term in vocab["design_terms"]:
        if term in lowered:
            terms.append(term)
    # Query tokens (keep short meaningful words)
    for tok in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-_]{2,}", lowered):
        if tok not in {"the", "and", "for", "with", "this", "that", "from", "please"}:
            terms.append(tok)
    # Preferred section hints from request
    preferred = []
    for hint in ("hire signal", "structure", "flagship", "selected projects", "depth"):
        if hint in lowered:
            preferred.append(hint)

    source_types = ["project", "decision"]
    if intent in {"design", "writing", "planning", "research"}:
        source_types.append("profile")
    if intent in {"coding", "system"} or project == "hypermind":
        source_types.append("markdown")

    return RetrievalQuery(
        raw_query=raw,
        intent=intent,
        project=project,
        project_ref=project_ref,
        explicit_terms=list(dict.fromkeys(terms))[:32],
        preferred_source_types=source_types,
        preferred_sections=preferred,
    )


def score_section(
    section: MarkdownSection,
    query: RetrievalQuery,
    *,
    kind: ContextKind,
    source_priority: float = 0.0,
) -> ScoreBreakdown:
    """Deterministic section score — heading matches outweigh body hits."""
    sb = ScoreBreakdown(total=0.0)
    heading_l = section.heading.lower()
    path_l = section.heading_path.lower()
    body_l = section.content.lower()
    # Strip heading line from body for body-only scoring
    body_only = body_l
    first_nl = section.content.find("\n")
    if first_nl > 0:
        body_only = section.content[first_nl + 1 :].lower()

    pref = (query.project_ref or "").lower()
    if pref:
        if re.search(rf"\b{re.escape(pref)}\b", heading_l) or pref in heading_l:
            sb.add("project_id_heading", 50.0)
        elif re.search(rf"\b{re.escape(pref)}\b", path_l):
            sb.add("project_id_path", 40.0)
        elif re.search(rf"\b{re.escape(pref)}\b", body_only):
            sb.add("project_id_body", 12.0)

    for term in query.explicit_terms:
        t = term.lower()
        if len(t) < 3:
            continue
        if t == pref:
            continue
        if t in heading_l or t in path_l:
            # Exact-ish heading match
            weight = 35.0 if len(t) >= 5 else 22.0
            sb.add("heading_term_match", weight)
        elif t in body_only:
            sb.add("body_keyword", 4.0)

    for hint in query.preferred_sections:
        if hint in heading_l or hint in path_l:
            sb.add("preferred_section", 25.0)

    if kind == ContextKind.DECISION:
        sb.add("decision_kind", 18.0)
    elif kind == ContextKind.CURRENT_STATE:
        sb.add("current_state_kind", 10.0)
    elif kind == ContextKind.FACT:
        sb.add("fact_kind", 8.0)

    if source_priority:
        sb.add("source_priority", source_priority)

    # Soft intent vocabulary on heading
    if query.intent == "design":
        for term in ("case", "structure", "design", "experience", "signal", "flagship"):
            if term in heading_l:
                sb.add("design_vocab_heading", 8.0)
                break

    return sb


def score_decision_entry(
    entry: dict[str, str],
    query: RetrievalQuery,
) -> ScoreBreakdown:
    sb = ScoreBreakdown(total=0.0)
    blob = f"{entry.get('id', '')} {entry.get('title', '')} {entry.get('body', '')}".lower()
    raw = query.raw_query.lower()
    pref = (query.project_ref or "").lower()

    if entry.get("id", "").lower() in raw:
        sb.add("explicit_decision_id", 50.0)
    if pref and pref in blob:
        sb.add("project_ref_in_decision", 20.0)

    for term in query.explicit_terms:
        if len(term) >= 4 and term in blob:
            sb.add("term_in_decision", 6.0)

    # High-signal portfolio governance when request is about structure/portfolio/freeze
    if any(w in raw for w in ("structure", "portfolio", "freeze", "frozen", "blueprint", "case")):
        if any(w in blob for w in ("freeze", "frozen", "blueprint", "writing standard", "release gate", "vault")):
            sb.add("governance_relevance", 22.0)

    if query.project == "portfolio":
        sb.add("portfolio_project", 5.0)

    sb.add("decision_kind", 18.0)
    return sb
