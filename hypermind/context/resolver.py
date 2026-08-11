"""Deterministic Context Resolver — section-level retrieval, never dumps knowledge stores."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from hypermind.agents import AgentRole
from hypermind.config.context_config import (
    ContextBudgetConfig,
    ContextEngineConfig,
    load_context_config,
)
from hypermind.context.profiles import ContextProfile, ContextProfileResolver
from hypermind.context.budget import CoveragePolicy, apply_budget, dedupe_items
from hypermind.context.markdown_io import path_denied, title_from_markdown
from hypermind.context.projects import ProjectIndex
from hypermind.context.retrieval import (
    RetrievalQuery,
    build_retrieval_query,
    score_decision_entry,
    score_section,
)
from hypermind.context.sections import excerpt_around_terms, parse_markdown_sections
from hypermind.context.sources import ContextQuery, ContextSource
from hypermind.context.types import ContextItem, ContextKind, ContextPack, KIND_PRIORITY
from hypermind.request import HyperMindRequest

_PROFILE_INTENTS = frozenset(
    {"design", "writing", "planning", "communication", "knowledge", "research"}
)
_PROFILE_AGENTS = frozenset(
    {"design_critic", "chief_of_staff", "knowledge_curator", "researcher"}
)
_CODING_SKIP_PROFILE = frozenset({"coding", "system"})

# Minimum decision score to include (no free portfolio injection)
_DECISION_SCORE_FLOOR = 28.0
_SECTION_SCORE_FLOOR = 12.0


def _item_id(*parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return digest


def _rel(path: Path, repo: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _should_include_profile(intent: str, agent: AgentRole, text: str) -> bool:
    lowered = text.lower()
    if intent in _CODING_SKIP_PROFILE:
        return any(
            k in lowered
            for k in ("portfolio", "career", "hiring", "senior product", "resume")
        )
    if intent in _PROFILE_INTENTS or agent.id in _PROFILE_AGENTS:
        return True
    return False


def _parse_accepted_decisions(raw: str) -> list[dict[str, str]]:
    """Backward-compatible ACTIVE-only dict view (tests / legacy callers)."""
    from hypermind.decisions.parse import parse_decision_log
    from hypermind.decisions.types import DecisionStatus

    entries: list[dict[str, str]] = []
    for rec in parse_decision_log(raw):
        if rec.status != DecisionStatus.ACTIVE.value:
            continue
        body = str(rec.metadata.get("raw_excerpt") or rec.retrieval_blob())
        if len(body) > 1800:
            body = body[:1780].rstrip() + "\n…[truncated]"
        entries.append({"id": rec.id, "title": rec.title, "body": body})
    return entries


class ProfileSource(ContextSource):
    name = "profile"

    def __init__(self, config: ContextEngineConfig) -> None:
        self.config = config

    def can_handle(self, query: ContextQuery) -> bool:
        profile_flag = query.metadata.get("include_profile")
        if profile_flag is False:
            return False
        if profile_flag is True:
            return True
        return _should_include_profile(query.intent, query.agent, query.request.raw_input)

    def retrieve(self, query: ContextQuery) -> list[ContextItem]:
        path = self.config.roots.profile
        if path_denied(path, self.config.privacy, self.config.roots.repo):
            return []
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            return []
        content, excerpted = excerpt_around_terms(
            raw.strip(),
            query.keywords,
            max_chars=min(1200, query.max_chars_per_item),
        )
        if not content:
            return []
        rel = _rel(path, self.config.roots.repo)
        return [
            ContextItem(
                id=_item_id("profile", rel),
                source_type="profile",
                source_ref=rel,
                title=title_from_markdown(path, raw[:2000]),
                content=content,
                relevance=0.75,
                priority=22,
                kind=ContextKind.PREFERENCE,
                metadata={"path": rel, "excerpted": excerpted},
            )
        ]


class DecisionSource(ContextSource):
    """
    Retrieve formal decisions with ACTIVE-first priority.

    Default: ACTIVE only (authoritative).
    History mode: may include SUPERSEDED for comparison queries.
    """

    name = "decision"

    def __init__(self, config: ContextEngineConfig) -> None:
        self.config = config

    def can_handle(self, query: ContextQuery) -> bool:
        from hypermind.decisions.resolve import is_historical_query

        if query.project_key == "portfolio":
            return True
        if query.intent in {"planning", "design", "knowledge", "research", "writing"}:
            return True
        text = query.request.raw_input.lower()
        if is_historical_query(text):
            return True
        return any(k in text for k in ("decision", "frozen", "accepted", "portfolio os"))

    def retrieve(self, query: ContextQuery) -> list[ContextItem]:
        from hypermind.decisions.conflict import analyze_against_active
        from hypermind.decisions.resolve import DecisionResolver, is_historical_query
        from hypermind.decisions.types import DecisionStatus

        path = self.config.roots.decision_log
        if not path.is_file() or path_denied(
            path, self.config.privacy, self.config.roots.repo
        ):
            return []

        resolver = DecisionResolver.from_path(path)
        rel = _rel(path, self.config.roots.repo)
        history = bool(query.metadata.get("history_mode")) or is_historical_query(
            query.request.raw_input
        )
        query.metadata["history_mode"] = history

        if history:
            records = resolver.get_inspectable(include_superseded=True)
        else:
            # Decision Log is shared governance — do not drop ACTIVE by project key
            records = resolver.get_active_decisions()

        if not records:
            return []

        rq: RetrievalQuery | None = query.metadata.get("retrieval_query")
        scored: list[tuple[float, object, dict, bool]] = []
        for rec in records:
            entry = {
                "id": rec.id,
                "title": rec.title,
                "body": rec.retrieval_blob(),
            }
            if rq is not None:
                breakdown = score_decision_entry(entry, rq)
                score = breakdown.total
                components = dict(breakdown.components)
            else:
                score = 10.0
                components = {}

            is_active = rec.status == DecisionStatus.ACTIVE.value
            # Priority: explicit ACTIVE ref > relevant ACTIVE > (history) SUPERSEDED
            if is_active:
                components["active_decision"] = 12.0
                score += 12.0
            else:
                components["superseded_historical"] = -8.0
                score -= 8.0
                if not history:
                    continue
                # History mode: keep superseded discoverable
                components["history_mode_floor"] = 20.0
                score += 20.0
                raw_q = (rq.raw_query if rq else query.request.raw_input).lower()
                if rec.id.lower() in raw_q or (
                    rec.superseded_by and rec.superseded_by.lower() in raw_q
                ):
                    components["history_explicit_link"] = 40.0
                    score += 40.0

            if score < _DECISION_SCORE_FLOOR and not (
                rq and rec.id.lower() in (rq.raw_query or "").lower()
            ):
                continue
            scored.append((score, rec, components, is_active))

        scored.sort(key=lambda t: (-t[0], t[1].id))  # type: ignore[attr-defined]
        cap = int(query.metadata.get("decisions_max", 2))
        if history:
            # Ensure room for SUPERSEDED alongside ACTIVE
            cap = max(cap, 3)
            superseded = [t for t in scored if not t[3]]
            active_scored = [t for t in scored if t[3]]
            merged = active_scored[: max(1, cap - 1)] + superseded[:1]
            if len(merged) < cap:
                rest = [t for t in scored if t not in merged]
                merged.extend(rest[: cap - len(merged)])
            scored = merged
            # Consume full merged list below
            cap = len(scored)

        items: list[ContextItem] = []
        for score, rec, components, is_active in scored[: max(0, cap)]:
            body = str(rec.metadata.get("raw_excerpt") or rec.retrieval_blob())
            if len(body) > 1800:
                body = body[:1780].rstrip() + "\n…[truncated]"
            # ACTIVE: top decision priority; SUPERSEDED: demoted unless history mode
            if is_active:
                priority = KIND_PRIORITY[ContextKind.DECISION]
            elif history:
                # Still below ACTIVE (20) but above typical REFERENCE (50)
                priority = KIND_PRIORITY[ContextKind.DECISION] + 5
            else:
                priority = KIND_PRIORITY[ContextKind.DECISION] + 25
            items.append(
                ContextItem(
                    id=_item_id("decision", rec.id),
                    source_type="decision",
                    source_ref=f"{rel}#{rec.id}",
                    title=f"{rec.id}: {rec.title}",
                    content=body,
                    relevance=min(1.0, score / 100.0),
                    priority=priority,
                    kind=ContextKind.DECISION,
                    metadata={
                        "decision_id": rec.id,
                        "status": rec.status,
                        "log_status": rec.metadata.get("log_status"),
                        "frozen": rec.frozen,
                        "historical": not is_active,
                        "score": score,
                        "score_components": components,
                        "path": rel,
                        "scope": rec.scope,
                        "project": rec.project,
                    },
                )
            )

        # Surface conflict signal when the request contradicts ACTIVE decisions
        active_only = resolver.get_active_decisions()
        hit = analyze_against_active(
            query.request.raw_input,
            active_only,
            project=query.project_key,
        )
        if hit.decision_conflict:
            query.metadata["decision_conflict_signal"] = {
                "decision_conflict": True,
                "decision_refs": list(hit.related_ids),
                "reason_code": hit.reason_code,
            }

        return items


class ProjectDocsSource(ContextSource):
    """Section-level project document retrieval."""

    name = "project"

    def __init__(self, config: ContextEngineConfig, index: ProjectIndex) -> None:
        self.config = config
        self.index = index

    def can_handle(self, query: ContextQuery) -> bool:
        return query.project_key is not None or bool(query.request.context_refs)

    def retrieve(self, query: ContextQuery) -> list[ContextItem]:
        repo = self.config.roots.repo
        project = self.index.get(query.project_key) if query.project_key else None
        rq: RetrievalQuery | None = query.metadata.get("retrieval_query")
        section_cap = query.metadata.get(
            "max_chars_per_section", query.max_chars_per_item
        )

        paths: list[tuple[Path, float, ContextKind, bool]] = []
        # explicit_ref flag

        for ref in query.request.context_refs:
            p = Path(ref)
            if not p.is_absolute():
                p = repo / ref
            if p.is_file() and not path_denied(p, self.config.privacy, repo):
                paths.append((p, 1.0, ContextKind.FACT, True))

        if project:
            docs = list(project.priority_docs)
            if query.project_id:
                for pid in project.project_ids:
                    if pid.id == query.project_id:
                        docs = list(pid.hint_docs) + [
                            d for d in docs if d not in pid.hint_docs
                        ]
                        break
            for i, rel in enumerate(docs):
                p = repo / rel
                if not p.is_file() or path_denied(p, self.config.privacy, repo):
                    continue
                source_boost = max(0.0, 12.0 - i * 1.5)
                kind = (
                    ContextKind.CURRENT_STATE
                    if "BLUEPRINT" in rel.upper() or "INVENTORY" in rel.upper()
                    else ContextKind.REFERENCE
                )
                if "Product_Brief" in rel:
                    kind = ContextKind.FACT
                paths.append((p, source_boost, kind, False))

        candidates: list[ContextItem] = []
        docs_touched: set[str] = set()
        section_count = 0

        for path, source_boost, kind, explicit in paths:
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError:
                continue
            rel = _rel(path, repo)
            docs_touched.add(rel)
            sections = parse_markdown_sections(raw, rel)
            section_count += len(sections)

            for section in sections:
                if rq is not None:
                    breakdown = score_section(
                        section, rq, kind=kind, source_priority=source_boost
                    )
                    score = breakdown.total
                    components = breakdown.components
                else:
                    score = source_boost + 5.0
                    components = {}

                floor = _SECTION_SCORE_FLOOR
                if query.project_id:
                    has_pid = any(
                        k in {"project_id_heading", "project_id_path"}
                        for k in components
                    )
                    # With an explicit case ID, ignore weak body-only hits
                    if not has_pid and not explicit:
                        floor = 65.0

                if not explicit and score < floor:
                    continue
                if explicit and score < 5.0 and section.level not in (0, 1):
                    continue
                content, excerpted = excerpt_around_terms(
                    section.content,
                    (rq.explicit_terms if rq else query.keywords),
                    max_chars=int(section_cap),
                )
                anchor = section.anchor
                if query.project_id and query.project_id.lower() in section.heading.lower():
                    anchor = query.project_id
                source_ref = f"{rel}#{anchor}" if anchor else rel
                title = (
                    f"{Path(rel).stem.replace('_', ' ')} > {section.heading_path}"
                    if section.heading not in {"(document)", "(preamble)"}
                    else title_from_markdown(path, raw[:2000])
                )
                # Map score to priority: higher score → lower priority number
                priority = max(8, 40 - int(score // 3))
                if explicit:
                    priority = min(priority, 10)

                candidates.append(
                    ContextItem(
                        id=_item_id("project", source_ref, str(section.start_line)),
                        source_type="project",
                        source_ref=source_ref,
                        title=title,
                        content=content,
                        relevance=min(1.0, score / 100.0),
                        priority=priority,
                        kind=kind,
                        metadata={
                            "path": rel,
                            "heading": section.heading,
                            "heading_path": section.heading_path,
                            "start_line": section.start_line,
                            "end_line": section.end_line,
                            "score": score,
                            "score_components": components,
                            "excerpted": excerpted,
                            "explicit_ref": explicit,
                        },
                    )
                )

        # Keep best sections overall (pre-budget)
        candidates.sort(key=lambda i: (-i.relevance, i.priority, i.source_ref))
        # Stash diagnostics on query for resolver
        query.metadata["_section_candidates"] = section_count
        query.metadata["_documents_touched"] = len(docs_touched)
        return candidates[:24]


class DocsSource(ContextSource):
    name = "markdown"

    def __init__(self, config: ContextEngineConfig) -> None:
        self.config = config

    def can_handle(self, query: ContextQuery) -> bool:
        text = query.request.raw_input.lower()
        return query.project_key == "hypermind" or any(
            k in text for k in ("architecture", "routing", "context engine", "hypermind")
        )

    def retrieve(self, query: ContextQuery) -> list[ContextItem]:
        repo = self.config.roots.repo
        rq: RetrievalQuery | None = query.metadata.get("retrieval_query")
        section_cap = query.metadata.get(
            "max_chars_per_section", query.max_chars_per_item
        )
        candidates = [
            "docs/intelligence-routing.md",
            "docs/context-engine.md",
            "README.md",
        ]
        items: list[ContextItem] = []
        for rel in candidates:
            path = repo / rel
            if not path.is_file() or path_denied(path, self.config.privacy, repo):
                continue
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for section in parse_markdown_sections(raw, rel)[:12]:
                if rq is not None:
                    breakdown = score_section(
                        section, rq, kind=ContextKind.REFERENCE, source_priority=4.0
                    )
                    score = breakdown.total
                    components = breakdown.components
                else:
                    score = 8.0
                    components = {}
                if score < _SECTION_SCORE_FLOOR:
                    continue
                content, excerpted = excerpt_around_terms(
                    section.content,
                    (rq.explicit_terms if rq else query.keywords),
                    max_chars=int(section_cap),
                )
                source_ref = f"{rel}#{section.anchor}"
                items.append(
                    ContextItem(
                        id=_item_id("docs", source_ref),
                        source_type="markdown",
                        source_ref=source_ref,
                        title=section.heading_path,
                        content=content,
                        relevance=min(1.0, score / 100.0),
                        priority=KIND_PRIORITY[ContextKind.REFERENCE],
                        metadata={
                            "path": rel,
                            "heading_path": section.heading_path,
                            "start_line": section.start_line,
                            "end_line": section.end_line,
                            "score": score,
                            "score_components": components,
                            "excerpted": excerpted,
                        },
                        kind=ContextKind.REFERENCE,
                    )
                )
        items.sort(key=lambda i: -i.relevance)
        return items[:8]


class ContextResolver:
    """Resolve a bounded ContextPack from local sources (section-aware)."""

    def __init__(
        self,
        config: ContextEngineConfig | None = None,
        sources: list[ContextSource] | None = None,
    ) -> None:
        self.config = config or load_context_config()
        self.index = ProjectIndex(self.config)
        self.profile_resolver = ContextProfileResolver(self.config)
        self.sources = sources or [
            ProfileSource(self.config),
            DecisionSource(self.config),
            ProjectDocsSource(self.config, self.index),
            DocsSource(self.config),
        ]

    def resolve(
        self,
        request: HyperMindRequest,
        agent: AgentRole,
        *,
        intent: str | None = None,
        budget: ContextBudgetConfig | None = None,
        profile: ContextProfile | None = None,
        override_profile: str | None = None,
        override_max_chars: int | None = None,
        override_max_items: int | None = None,
        model_name: str | None = None,
    ) -> ContextPack:
        intent_name = intent or request.intent or "general"
        resolution = self.index.resolve(
            request.raw_input, explicit_project=request.project
        )
        project_key = resolution.project.id if resolution.project else None
        project_id = resolution.project_id.id if resolution.project_id else None

        active_profile = profile or self.profile_resolver.resolve(
            intent_name,
            request,
            project=project_key,
            override_profile=override_profile,
            override_max_chars=override_max_chars,
            override_max_items=override_max_items,
            model_name=model_name,
        )

        aliases: list[str] = []
        if resolution.project:
            aliases.extend(resolution.project.aliases)
            if resolution.project_id:
                aliases.extend(resolution.project_id.aliases)

        rq = build_retrieval_query(
            request.raw_input,
            intent=intent_name,
            project=project_key,
            project_ref=project_id,
            aliases=aliases,
        )
        # Prefer profile-preferred source types in retrieval query
        if active_profile.preferred_source_types:
            rq.preferred_source_types = list(active_profile.preferred_source_types)

        base = self.config.budget
        active_budget = budget or ContextBudgetConfig(
            max_items=active_profile.max_items,
            max_chars=active_profile.max_chars,
            max_chars_per_item=base.max_chars_per_item,
            max_chars_per_section=active_profile.section_max_chars,
        )

        query = ContextQuery(
            request=request,
            agent=agent,
            intent=intent_name,
            project_key=project_key,
            project_id=project_id,
            keywords=rq.explicit_terms,
            max_chars_per_item=active_budget.max_chars_per_item,
            metadata={
                "retrieval_query": rq,
                "max_chars_per_section": active_budget.max_chars_per_section,
                "decisions_max": active_profile.decisions_max,
                "include_profile": active_profile.include_profile,
                "context_profile": active_profile.id,
                "preferred_source_types": list(active_profile.preferred_source_types),
            },
        )

        candidates: list[ContextItem] = []
        candidate_sections = 0
        documents_touched = 0
        for source in self.sources:
            if not source.can_handle(query):
                continue
            try:
                got = source.retrieve(query)
            except OSError:
                continue
            candidates.extend(got)
            candidate_sections += int(query.metadata.pop("_section_candidates", 0) or 0)
            documents_touched += int(query.metadata.pop("_documents_touched", 0) or 0)

        # Optional agent identity as ContextItem (default: system instruction only)
        if active_profile.include_agent_identity:
            candidates.append(
                ContextItem(
                    id=_item_id("agent", agent.id),
                    source_type="reference",
                    source_ref=f"agent:{agent.id}",
                    title=f"Agent {agent.id}",
                    content=f"Selected agent: {agent.id}\nRole: {agent.description}",
                    relevance=0.15,
                    priority=70,
                    kind=ContextKind.REFERENCE,
                    metadata={"agent": agent.id, "score": 1.0},
                )
            )

        # Soft priority nudge from preferred source types / kinds
        preferred = set(active_profile.preferred_source_types)
        if preferred:
            nudged: list[ContextItem] = []
            for item in candidates:
                kind_key = item.kind.value.lower()
                boost = 0
                if item.source_type in preferred or kind_key in preferred:
                    boost = -3  # lower priority number = kept earlier
                if "current_state" in preferred and item.kind == ContextKind.CURRENT_STATE:
                    boost = -5
                if "decision" in preferred and item.kind == ContextKind.DECISION:
                    boost = -4
                if "profile" in preferred and item.source_type == "profile":
                    boost = -2
                if boost:
                    nudged.append(
                        ContextItem(
                            id=item.id,
                            source_type=item.source_type,
                            source_ref=item.source_ref,
                            title=item.title,
                            content=item.content,
                            relevance=item.relevance,
                            priority=max(5, item.priority + boost),
                            kind=item.kind,
                            metadata=dict(item.metadata),
                        )
                    )
                else:
                    nudged.append(item)
            candidates = nudged

        deduped, dropped = dedupe_items(candidates)
        if candidate_sections == 0:
            candidate_sections = len(candidates)

        coverage = CoveragePolicy(
            require_project=bool(project_key),
            require_decision=active_profile.decisions_max > 0,
            require_profile=active_profile.include_profile,
        )
        pack = apply_budget(
            deduped,
            active_budget,
            project=project_key,
            project_id=project_id,
            intent=intent_name,
            candidate_sections=candidate_sections,
            documents_touched=documents_touched
            or len({i.metadata.get("path") for i in deduped if i.metadata.get("path")}),
            deduplicated_items=dropped,
            context_profile=active_profile.id,
            profile_source=active_profile.source,
            coverage=coverage,
        )
        # Attach decision conflict signal when DecisionSource detected one
        signal = query.metadata.get("decision_conflict_signal")
        if isinstance(signal, dict) and signal.get("decision_conflict"):
            pack.signals = {
                "decision_conflict": True,
                "decision_refs": list(signal.get("decision_refs") or []),
                "reason_code": signal.get("reason_code")
                or "conflicts_with_active_decision",
            }
        return pack


class ContextBuilder:
    """Public builder used by the routing pipeline."""

    def __init__(self, resolver: ContextResolver | None = None) -> None:
        self.resolver = resolver or ContextResolver()

    def build(
        self,
        request: HyperMindRequest,
        agent: AgentRole,
        *,
        max_items: int | None = None,
        max_tokens: int | None = None,
        max_chars: int | None = None,
        intent: str | None = None,
        context_profile: str | None = None,
        model_name: str | None = None,
    ) -> ContextPack:
        intent_name = intent or request.intent or "general"
        resolution = self.resolver.index.resolve(
            request.raw_input, explicit_project=request.project
        )
        project_key = resolution.project.id if resolution.project else None

        # Profile selection (CLI should validate overrides before calling)
        profile = self.resolver.profile_resolver.resolve(
            intent_name,
            request,
            project=project_key,
            override_profile=context_profile,
            model_name=model_name,
        )

        chars = profile.max_chars
        items = profile.max_items
        if max_chars is not None:
            chars = max_chars
        elif max_tokens is not None:
            # Legacy token budget ≈ chars/4; treat as ceiling within profile
            chars = min(profile.max_chars, max(1, max_tokens * 4))
        if max_items is not None:
            items = max_items

        # Re-apply model cap after explicit overrides
        if profile.model_cap_chars is not None:
            chars = min(chars, profile.model_cap_chars)

        from dataclasses import replace

        profile = replace(
            profile,
            max_chars=chars,
            max_items=items,
            section_max_chars=min(profile.section_max_chars, chars),
            source=(
                "override"
                if context_profile or max_chars is not None or max_items is not None
                else profile.source
            ),
        )
        budget = ContextBudgetConfig(
            max_items=profile.max_items,
            max_chars=profile.max_chars,
            max_chars_per_item=self.resolver.config.budget.max_chars_per_item,
            max_chars_per_section=profile.section_max_chars,
        )
        return self.resolver.resolve(
            request,
            agent,
            intent=intent_name,
            budget=budget,
            profile=profile,
            model_name=model_name,
        )
