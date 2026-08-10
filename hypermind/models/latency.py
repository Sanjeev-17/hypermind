"""Persisted local-model latency samples — no auto-download, no continuous probing."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hypermind.config.context_config import repo_root


def latency_path(repo: Path | None = None) -> Path:
    root = repo or repo_root()
    return root / ".hypermind" / "model_latency.json"


def load_latency(repo: Path | None = None) -> dict[str, Any]:
    path = latency_path(repo)
    if not path.is_file():
        return {"updated_at": None, "models": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"updated_at": None, "models": {}}
    if not isinstance(data, dict):
        return {"updated_at": None, "models": {}}
    models = data.get("models") if isinstance(data.get("models"), dict) else {}
    return {"updated_at": data.get("updated_at"), "models": models}


def save_latency(models: dict[str, Any], *, repo: Path | None = None) -> Path:
    path = latency_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "models": models,
        "note": "One-shot HyperMind benchmarks. Not continuous. Do not auto-download models.",
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def estimated_ms(model: str, *, repo: Path | None = None) -> int | None:
    entry = load_latency(repo).get("models", {}).get(model)
    if not isinstance(entry, dict) or not entry.get("ok"):
        return None
    wall = entry.get("wall_ms")
    try:
        return int(wall) if wall is not None else None
    except (TypeError, ValueError):
        return None
