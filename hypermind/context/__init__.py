"""Bounded Context Engine — deterministic section-aware retrieval, no embeddings."""

from hypermind.context.budget import CoveragePolicy, apply_budget, dedupe_items
from hypermind.context.profiles import ContextProfile, ContextProfileError, ContextProfileResolver
from hypermind.context.projects import ProjectIndex, ProjectResolution
from hypermind.context.resolver import ContextBuilder, ContextResolver
from hypermind.context.retrieval import RetrievalQuery, build_retrieval_query
from hypermind.context.sections import MarkdownSection, parse_markdown_sections
from hypermind.context.sources import ContextQuery, ContextSource
from hypermind.context.types import (
    ContextBundle,
    ContextItem,
    ContextKind,
    ContextPack,
)

__all__ = [
    "CoveragePolicy",
    "ContextBuilder",
    "ContextBundle",
    "ContextItem",
    "ContextKind",
    "ContextPack",
    "ContextProfile",
    "ContextProfileError",
    "ContextProfileResolver",
    "ContextQuery",
    "ContextResolver",
    "ContextSource",
    "MarkdownSection",
    "ProjectIndex",
    "ProjectResolution",
    "RetrievalQuery",
    "apply_budget",
    "build_retrieval_query",
    "dedupe_items",
    "parse_markdown_sections",
]
