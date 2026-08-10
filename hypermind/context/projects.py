"""Project alias / ID resolution — deterministic, no embeddings."""

from __future__ import annotations

import re
from dataclasses import dataclass

from hypermind.config.context_config import ContextEngineConfig, ProjectIdSpec, ProjectSpec


@dataclass(frozen=True)
class ProjectResolution:
    project: ProjectSpec | None
    project_id: ProjectIdSpec | None
    reason: str


class ProjectIndex:
    def __init__(self, config: ContextEngineConfig) -> None:
        self.config = config
        self._by_id = {p.id: p for p in config.projects}

    def get(self, project_key: str) -> ProjectSpec | None:
        return self._by_id.get(project_key.lower()) or self._by_id.get(project_key)

    def resolve(
        self,
        text: str,
        *,
        explicit_project: str | None = None,
    ) -> ProjectResolution:
        if explicit_project:
            key = explicit_project.strip().lower()
            # Map P-006 style onto portfolio project
            for project in self.config.projects:
                if project.id == key or key in project.aliases:
                    return ProjectResolution(project, None, "explicit_project")
                for pid in project.project_ids:
                    if key == pid.id.lower() or key in pid.aliases:
                        return ProjectResolution(project, pid, "explicit_project_id")
            return ProjectResolution(None, None, "explicit_missing")

        lowered = text.lower()

        # Explicit project IDs first (P-006, p-005, …)
        for project in self.config.projects:
            for pid in project.project_ids:
                if re.search(rf"\b{re.escape(pid.id.lower())}\b", lowered):
                    return ProjectResolution(project, pid, "project_id_mention")
                for alias in pid.aliases:
                    if len(alias) >= 4 and alias in lowered:
                        return ProjectResolution(project, pid, "project_id_alias")

        # Longer aliases first to avoid weak partials
        scored: list[tuple[int, ProjectSpec, str]] = []
        for project in self.config.projects:
            for alias in project.aliases:
                if len(alias) < 3:
                    continue
                if alias in lowered:
                    scored.append((len(alias), project, alias))
        if scored:
            scored.sort(key=lambda t: (-t[0], t[1].id))
            _, project, alias = scored[0]
            return ProjectResolution(project, None, f"alias:{alias}")

        return ProjectResolution(None, None, "unresolved")
