"""Deterministic intent router — no chain-of-thought storage."""

from __future__ import annotations

import re
from functools import lru_cache

from hypermind.intent import INTENTS, IntentResult
from hypermind.request import HyperMindRequest

# (reason_code, intent, pattern) — first match wins
# Explicit action language is ordered before domain vocabulary.
_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    (
        "memory_command",
        "memory",
        re.compile(
            r"\b(remember|forget|memorize|save (this )?to memory|store (this )?in memory)\b",
            re.I,
        ),
    ),
    (
        "writing_action",
        "writing",
        re.compile(
            r"\b(linkedin(\s+post)?|blog\s+post|write\s+a\s+(post|blog|essay|article|caption)|"
            r"draft\s+a\s+(post|blog|essay|article)|tweet|essay about|article about)\b|"
            r"\b(write|draft|rewrite)\b.{0,40}\b(linkedin|blog|essay|article|post|copy|headline)\b",
            re.I,
        ),
    ),
    (
        "explicit_research_request",
        "research",
        re.compile(
            r"\b(research|competitor|compare|benchmark|investigate|gather evidence|literature)\b",
            re.I,
        ),
    ),
    (
        "architecture_request",
        "planning",
        re.compile(r"\b(architecture|system design|tech(nical)? plan|\badrs?\b)\b", re.I),
    ),
    (
        "repo_operation",
        "coding",
        re.compile(
            r"\b(repo|repository|codebase|pull request|\bpr\b|\bgit\b|debug|implement|refactor|"
            r"unit test|pytest|typescript|python module|search the (repo|code)|fix (the )?bug|"
            r"write (a |the )?function|compile|linter|authentication module)\b",
            re.I,
        ),
    ),
    (
        "design_review",
        "design",
        re.compile(
            r"\b(ui|ux|interface|visual system|design system|wireframe|layout|typography|"
            r"accessibility review|critique (the )?(design|ui)|review (this )?interface|"
            r"case study|user flow|prototype|interaction|usability|design rationale|"
            r"journey|visual design|information architecture|hire signal|case slate|"
            r"portfolio (structure|case|hero)|experience (blueprint|design))\b|"
            r"\bP-\d{3}\b.{0,48}\b(structure|case|design|portfolio|experience)\b|"
            r"\breview\b.{0,32}\b(case study|portfolio|structure|design)\b",
            re.I,
        ),
    ),
    (
        "planning_request",
        "planning",
        re.compile(
            r"\b(plan|prioriti[sz]e|roadmap|decompose|break( this)? down|coordinate|"
            r"chief of staff|what should (i|we) (do|focus))\b",
            re.I,
        ),
    ),
    (
        "knowledge_vault",
        "knowledge",
        re.compile(
            r"\b(obsidian|vault|knowledge (base|graph)|wiki|evergreen|distill (to )?notes)\b",
            re.I,
        ),
    ),
    (
        "communication_draft",
        "communication",
        re.compile(
            r"\b(email|slack|message|reply to|outreach|stakeholder update)\b",
            re.I,
        ),
    ),
    (
        "writing_request",
        "writing",
        re.compile(
            r"\b(draft|rewrite|edit( the)? (copy|prose|case study)|headline|blog post|"
            r"writing standard)\b",
            re.I,
        ),
    ),
    (
        "system_ops",
        "system",
        re.compile(
            r"\b(configure hypermind|routing config|provider status|tool permissions|"
            r"policy gate|model router)\b",
            re.I,
        ),
    ),
]


@lru_cache(maxsize=1)
def _design_vocab_pattern() -> re.Pattern[str]:
    from hypermind.context.retrieval import load_vocabulary

    terms = load_vocabulary()["design_terms"]
    # Escape and join; multi-word phrases first (already listed long-first in yaml-ish order)
    parts = [re.escape(t) for t in sorted(terms, key=len, reverse=True)]
    return re.compile(r"\b(" + "|".join(parts) + r")\b", re.I)


class IntentRouter:
    """Lightweight deterministic classifier with soft project/domain co-resolution."""

    def classify(
        self,
        request: HyperMindRequest,
        *,
        project_key: str | None = None,
        project_id: str | None = None,
    ) -> IntentResult:
        if request.intent and request.intent in INTENTS:
            return IntentResult(
                intent=request.intent,
                confidence=1.0,
                method="deterministic",
                reason_code="explicit_intent",
            )

        text = request.raw_input
        for reason_code, intent, pattern in _RULES:
            if pattern.search(text):
                return IntentResult(
                    intent=intent,
                    confidence=0.9,
                    method="deterministic",
                    reason_code=reason_code,
                )

        # Soft co-resolution: domain vocabulary / portfolio project evidence
        # only when no stronger action intent matched.
        if _design_vocab_pattern().search(text) or (
            project_key == "portfolio"
            and (
                project_id
                or re.search(r"\bP-\d{3}\b", text, re.I)
                or re.search(r"\b(case|portfolio|design)\b", text, re.I)
            )
        ):
            return IntentResult(
                intent="design",
                confidence=0.75,
                method="deterministic",
                reason_code="case_study_domain",
            )

        return IntentResult(
            intent="general",
            confidence=0.4,
            method="deterministic",
            reason_code="no_strong_signal",
        )
