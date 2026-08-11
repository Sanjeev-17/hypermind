"""Formal decision semantics — analyze only, never persist Decision Log."""

from hypermind.decisions.conflict import ConflictHit, analyze_against_active
from hypermind.decisions.engine import DecisionAnalyzeEngine
from hypermind.decisions.parse import load_decision_log, parse_decision_log
from hypermind.decisions.resolve import DecisionResolver, is_historical_query
from hypermind.decisions.types import (
    DecisionAction,
    DecisionAnalyzeRequest,
    DecisionAnalyzeResult,
    DecisionProposal,
    DecisionRecord,
    DecisionRelationship,
    DecisionScope,
    DecisionStatus,
)

__all__ = [
    "ConflictHit",
    "DecisionAction",
    "DecisionAnalyzeEngine",
    "DecisionAnalyzeRequest",
    "DecisionAnalyzeResult",
    "DecisionProposal",
    "DecisionRecord",
    "DecisionRelationship",
    "DecisionResolver",
    "DecisionScope",
    "DecisionStatus",
    "analyze_against_active",
    "is_historical_query",
    "load_decision_log",
    "parse_decision_log",
]
