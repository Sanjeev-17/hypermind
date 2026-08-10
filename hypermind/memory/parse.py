"""Parse and validate model JSON for memory candidates."""

from __future__ import annotations

import json
import re
from typing import Any

from hypermind.memory.types import candidate_from_raw


_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_json_object(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("empty model output")
    fence = _FENCE_RE.search(raw)
    if fence:
        raw = fence.group(1).strip()
    # Prefer first JSON object
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object found")
    payload = json.loads(raw[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def parse_candidates_payload(
    text: str, *, allowed_sources: set[str], max_candidates: int
) -> tuple[list[Any], list[dict[str, Any]]]:
    """
    Returns (accepted MemoryCandidate list stubs via candidate_from_raw, parse_notes).
    Raises ValueError on malformed root structure.
    """
    payload = extract_json_object(text)
    if "candidates" not in payload:
        raise ValueError("missing candidates array")
    items = payload.get("candidates")
    if not isinstance(items, list):
        raise ValueError("candidates must be an array")

    accepted = []
    notes: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        if len(accepted) >= max_candidates:
            notes.append({"index": idx, "reason_code": "over_max_candidates"})
            break
        if not isinstance(item, dict):
            notes.append({"index": idx, "reason_code": "invalid_item_type"})
            continue
        try:
            cand = candidate_from_raw(item, allowed_sources=allowed_sources)
            accepted.append(cand)
        except ValueError as exc:
            notes.append(
                {
                    "index": idx,
                    "reason_code": "invalid_candidate",
                    "detail": str(exc)[:120],
                }
            )
    return accepted, notes
