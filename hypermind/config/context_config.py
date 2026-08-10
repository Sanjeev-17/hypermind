"""Context engine configuration loader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


def repo_root() -> Path:
    """Repository root containing the hypermind package."""
    return Path(__file__).resolve().parents[2]


def _read_pkg_yaml(name: str) -> dict[str, Any]:
    try:
        text = (
            resources.files("hypermind.config")
            .joinpath(name)
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, TypeError, AttributeError):
        text = Path(__file__).with_name(name).read_text(encoding="utf-8")
    return yaml.safe_load(text) or {}


@dataclass(frozen=True)
class ContextBudgetConfig:
    max_items: int = 8
    max_chars: int = 12000
    max_chars_per_item: int = 3500
    max_chars_per_section: int = 2500


@dataclass(frozen=True)
class ContextProfileSpec:
    id: str
    max_items: int = 4
    max_chars: int = 3000
    decisions_max: int = 1
    include_profile: bool = False
    include_agent_identity: bool = False
    preferred_source_types: tuple[str, ...] = ()
    section_max_chars: int = 1500


@dataclass(frozen=True)
class ContextRoots:
    repo: Path
    profile: Path
    decision_log: Path
    obsidian_vault: Path | None = None


@dataclass(frozen=True)
class PrivacyConfig:
    deny_path_segments: tuple[str, ...] = ()
    profile_default: bool = False


@dataclass(frozen=True)
class ProjectIdSpec:
    id: str
    aliases: tuple[str, ...]
    hint_docs: tuple[str, ...]


@dataclass(frozen=True)
class ProjectSpec:
    id: str
    aliases: tuple[str, ...]
    roots: tuple[str, ...]
    priority_docs: tuple[str, ...]
    project_ids: tuple[ProjectIdSpec, ...] = ()


@dataclass(frozen=True)
class ContextEngineConfig:
    budget: ContextBudgetConfig
    roots: ContextRoots
    privacy: PrivacyConfig
    projects: tuple[ProjectSpec, ...]
    profiles: tuple[ContextProfileSpec, ...] = ()
    model_context_caps: dict[str, int] = field(default_factory=dict)
    override_max_chars: int = 12000
    override_max_items: int = 12


def _default_profiles() -> tuple[ContextProfileSpec, ...]:
    return (
        ContextProfileSpec("general", 4, 3000, 1, False, False, ("current_state", "decision"), 1200),
        ContextProfileSpec(
            "design", 5, 4000, 2, True, False, ("current_state", "decision", "profile"), 1500
        ),
        ContextProfileSpec(
            "writing", 5, 4000, 2, True, False, ("current_state", "decision", "profile"), 1500
        ),
        ContextProfileSpec(
            "planning", 6, 4500, 2, True, False, ("current_state", "decision", "profile"), 1500
        ),
        ContextProfileSpec(
            "research", 5, 4000, 1, True, False, ("current_state", "decision", "profile"), 1500
        ),
        ContextProfileSpec(
            "coding", 4, 3000, 1, False, False, ("current_state", "decision", "markdown"), 1200
        ),
        ContextProfileSpec(
            "memory", 4, 3000, 2, True, False, ("decision", "profile", "current_state"), 1200
        ),
    )


def _parse_profiles(raw: dict[str, Any] | None) -> tuple[ContextProfileSpec, ...]:
    if not raw:
        return _default_profiles()
    out: list[ContextProfileSpec] = []
    for pid, pdata in raw.items():
        pdata = pdata or {}
        out.append(
            ContextProfileSpec(
                id=str(pid).lower(),
                max_items=int(pdata.get("max_items", 4)),
                max_chars=int(pdata.get("max_chars", 3000)),
                decisions_max=int(pdata.get("decisions_max", 1)),
                include_profile=bool(pdata.get("include_profile", False)),
                include_agent_identity=bool(pdata.get("include_agent_identity", False)),
                preferred_source_types=tuple(
                    str(x).lower() for x in (pdata.get("preferred_source_types") or [])
                ),
                section_max_chars=int(pdata.get("section_max_chars", 1500)),
            )
        )
    return tuple(out) if out else _default_profiles()


def _resolve_path(repo: Path, value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value)
    if not p.is_absolute():
        p = repo / p
    return p


def load_context_config(
    *,
    repo: Path | None = None,
    context_path: Path | None = None,
    projects_path: Path | None = None,
) -> ContextEngineConfig:
    root = repo or repo_root()
    if context_path is not None:
        ctx_data = yaml.safe_load(context_path.read_text(encoding="utf-8")) or {}
    else:
        ctx_data = _read_pkg_yaml("context.yaml")

    if projects_path is not None:
        proj_data = yaml.safe_load(projects_path.read_text(encoding="utf-8")) or {}
    else:
        proj_data = _read_pkg_yaml("projects.yaml")

    budget_raw = ctx_data.get("context") or {}
    sections_raw = budget_raw.get("sections") or {}
    budget = ContextBudgetConfig(
        max_items=int(budget_raw.get("max_items", 8)),
        max_chars=int(budget_raw.get("max_chars", 12000)),
        max_chars_per_item=int(budget_raw.get("max_chars_per_item", 3500)),
        max_chars_per_section=int(
            sections_raw.get(
                "max_chars_per_section",
                budget_raw.get("max_chars_per_section", 2500),
            )
        ),
    )

    profiles = _parse_profiles(ctx_data.get("context_profiles"))
    override_max_chars = int(budget_raw.get("override_max_chars", 12000))
    override_max_items = int(budget_raw.get("override_max_items", 12))

    roots_raw = ctx_data.get("roots") or {}
    vault_env = os.getenv("HYPERMIND_VAULT") or os.getenv("OBSIDIAN_VAULT")
    vault = _resolve_path(root, vault_env or roots_raw.get("obsidian_vault"))
    if vault is not None and not vault.exists():
        vault = None

    profile = _resolve_path(
        root, roots_raw.get("profile", "hypermind/config/profile.md")
    )
    decision = _resolve_path(
        root, roots_raw.get("decision_log", "portfolio-os/governance/Decision_Log.md")
    )
    assert profile is not None and decision is not None

    privacy_raw = ctx_data.get("privacy") or {}
    privacy = PrivacyConfig(
        deny_path_segments=tuple(privacy_raw.get("deny_path_segments") or ()),
        profile_default=bool(privacy_raw.get("profile_default", False)),
    )

    projects: list[ProjectSpec] = []
    for pid, raw in (proj_data.get("projects") or {}).items():
        id_specs: list[ProjectIdSpec] = []
        for kid, kraw in (raw.get("project_ids") or {}).items():
            id_specs.append(
                ProjectIdSpec(
                    id=str(kid),
                    aliases=tuple(a.lower() for a in (kraw.get("aliases") or [])),
                    hint_docs=tuple(kraw.get("hint_docs") or []),
                )
            )
        projects.append(
            ProjectSpec(
                id=str(pid),
                aliases=tuple(a.lower() for a in (raw.get("aliases") or [])),
                roots=tuple(raw.get("roots") or []),
                priority_docs=tuple(raw.get("priority_docs") or []),
                project_ids=tuple(id_specs),
            )
        )

    # Optional model context caps from models.yaml (loaded separately if present)
    model_caps: dict[str, int] = {}
    try:
        models_raw = _read_pkg_yaml("models.yaml")
        for mid, mdata in (models_raw.get("model_limits") or {}).items():
            if isinstance(mdata, dict) and "max_context_chars" in mdata:
                model_caps[str(mid)] = int(mdata["max_context_chars"])
            elif isinstance(mdata, int):
                model_caps[str(mid)] = int(mdata)
        # Also allow providers.ollama.models style
        for mid, mdata in (models_raw.get("models") or {}).items():
            if isinstance(mdata, dict) and "max_context_chars" in mdata:
                model_caps[str(mid)] = int(mdata["max_context_chars"])
    except OSError:
        pass

    return ContextEngineConfig(
        budget=budget,
        roots=ContextRoots(
            repo=root,
            profile=profile,
            decision_log=decision,
            obsidian_vault=vault,
        ),
        privacy=privacy,
        projects=tuple(projects),
        profiles=profiles,
        model_context_caps=model_caps,
        override_max_chars=override_max_chars,
        override_max_items=override_max_items,
    )
