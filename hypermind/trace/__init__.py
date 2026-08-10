"""Operational execution traces — no chain-of-thought."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ExecutionTrace:
    request_id: str
    intent: str
    agent: str
    provider: str
    model: str
    tools_allowed: list[str]
    route_reason: str
    status: str = "routed"
    intent_reason: str | None = None
    agent_reason: str | None = None
    policy_blocked: list[str] = field(default_factory=list)
    context_items: int = 0
    context_chars: int = 0
    context_truncated: bool = False
    context_sources: list[str] = field(default_factory=list)
    generation_count: int = 0
    duration_ms: int | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class TraceStore:
    """Optional append-only JSONL sink under .hypermind/traces/."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(".hypermind") / "traces"
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, trace: ExecutionTrace) -> Path:
        path = self.root / f"{trace.request_id}.json"
        path.write_text(trace.to_json(), encoding="utf-8")
        log = self.root / "events.jsonl"
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(trace.to_dict(), separators=(",", ":")) + "\n")
        return path
