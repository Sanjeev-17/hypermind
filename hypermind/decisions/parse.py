"""Parse Decision Log markdown into canonical DecisionRecord list (defensive)."""

from __future__ import annotations

import re
from pathlib import Path

from hypermind.decisions.types import (
    LOG_STATUS_MAP,
    DecisionRecord,
    DecisionScope,
    DecisionStatus,
)

_HEADING_SPLIT = re.compile(
    r"(?m)^###\s+(D-\d+)\s+[—\-]\s+(.+)$"
)
_FIELD_ROW = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$", re.MULTILINE
)
_ID_IN_TEXT = re.compile(r"\b(D-\d+)\b", re.I)
_FREEZE_RE = re.compile(r"\b(freeze|frozen|lock(?:ed)?)\b", re.I)


def _field_map(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in _FIELD_ROW.finditer(body):
        key = match.group(1).strip().lower()
        value = match.group(2).strip()
        if key.lower() in {"field", "-------", "---"} or set(key) <= {"-"}:
            continue
        if not key or key == "value":
            continue
        fields[key] = value
    return fields


def _parse_id_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [m.upper() if m.upper().startswith("D-") else m for m in _ID_IN_TEXT.findall(raw)]


def _map_status(raw: str | None) -> str | None:
    if not raw:
        return None
    key = raw.strip().lower()
    return LOG_STATUS_MAP.get(key)


def _infer_frozen(title: str, statement: str, fields: dict[str, str]) -> bool:
    if str(fields.get("frozen", "")).strip().lower() in {"true", "yes", "1"}:
        return True
    blob = f"{title}\n{statement}\n{fields.get('decision', '')}"
    return bool(_FREEZE_RE.search(blob))


def parse_decision_log(
    raw: str,
    *,
    source_path: str = "portfolio-os/governance/Decision_Log.md",
    default_project: str | None = "portfolio",
) -> list[DecisionRecord]:
    """
    Parse Decision Log entries into DecisionRecords.

    Skips Proposed (not yet formal). Malformed entries are skipped, not raised.
    Preserves source_refs pointing at the log + decision id.
    """
    if not raw or not raw.strip():
        return []

    records: list[DecisionRecord] = []
    parts = _HEADING_SPLIT.split(raw)
    i = 1
    while i + 2 < len(parts):
        did = parts[i].strip().upper()
        title = parts[i + 1].strip()
        body = parts[i + 2]
        i += 3
        try:
            rec = _entry_to_record(
                did,
                title,
                body,
                source_path=source_path,
                default_project=default_project,
            )
        except Exception:
            continue
        if rec is not None:
            records.append(rec)
    return records


def _entry_to_record(
    did: str,
    title: str,
    body: str,
    *,
    source_path: str,
    default_project: str | None,
) -> DecisionRecord | None:
    fields = _field_map(body)
    status_raw = fields.get("status")
    # Defensive: status may appear only as prose "Accepted" without table
    if not status_raw:
        for label, mapped in LOG_STATUS_MAP.items():
            if re.search(rf"\|\s*Status\s*\|\s*{label}\s*\|", body, re.I):
                status_raw = label
                break
            if re.search(rf"\bStatus\s*[:\|]\s*{label}\b", body, re.I):
                status_raw = label
                break
            if label == "accepted" and re.search(r"\bAccepted\b", body):
                # Prefer explicit Accepted only when no other status token wins
                status_raw = status_raw or "accepted"

    # Proposed = not a formal decision yet
    if status_raw and status_raw.strip().lower() == "proposed":
        return None

    status = _map_status(status_raw)
    if status is None:
        # Malformed / unknown — skip from authoritative store
        return None

    statement = (
        fields.get("decision")
        or fields.get("statement")
        or ""
    ).strip()
    if not statement:
        # Fallback: first non-table paragraph
        paras = [
            p.strip()
            for p in re.split(r"\n\s*\n", body)
            if p.strip() and not p.strip().startswith("|")
        ]
        statement = paras[0][:500] if paras else title
    if not statement:
        statement = title

    supersedes = _parse_id_list(
        fields.get("supersedes") or fields.get("replaces")
    )
    superseded_by_list = _parse_id_list(
        fields.get("superseded by") or fields.get("superseded_by")
    )
    superseded_by = superseded_by_list[0] if superseded_by_list else None

    # If status is SUPERSEDED but link missing, keep record; resolver must not crash
    effective_at = fields.get("date") or fields.get("effective_at") or fields.get("effective at")
    rationale = fields.get("reasoning") or fields.get("rationale")

    # Scope: Decision Log under portfolio-os → project portfolio by default
    scope = DecisionScope.PROJECT.value
    project = default_project
    category = (fields.get("category") or "").lower()
    if "global" in (fields.get("scope") or "").lower():
        scope = DecisionScope.GLOBAL.value
        project = None
    elif fields.get("project"):
        project = fields["project"].strip() or default_project
        scope = DecisionScope.PROJECT.value

    frozen = _infer_frozen(title, statement, fields)
    related = fields.get("related documents") or fields.get("related documents") or ""
    source_refs = [f"{source_path}#{did}"]
    for ref in re.findall(r"`([^`]+)`", related):
        if ref not in source_refs:
            source_refs.append(ref)

    metadata: dict = {
        "category": fields.get("category"),
        "owner": fields.get("owner"),
        "log_status": status_raw,
        "frozen": frozen,
        "malformed": False,
        "raw_excerpt": body.strip()[:1800],
    }
    # Drop None values
    metadata = {k: v for k, v in metadata.items() if v is not None}

    return DecisionRecord(
        id=did,
        title=title or did,
        statement=statement,
        scope=scope,
        project=project,
        status=status,
        effective_at=effective_at,
        supersedes=supersedes,
        superseded_by=superseded_by,
        rationale=rationale,
        source_refs=source_refs,
        metadata=metadata,
    )


def load_decision_log(
    path: Path,
    *,
    default_project: str | None = "portfolio",
) -> list[DecisionRecord]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return []
    rel = str(path).replace("\\", "/")
    # Prefer repo-relative style if ends with known suffix
    for marker in ("portfolio-os/", "hypermind/"):
        if marker in rel:
            rel = rel[rel.index(marker) :]
            break
    return parse_decision_log(
        raw, source_path=rel, default_project=default_project
    )


def parse_malformed_safe(raw: str, **kwargs) -> list[DecisionRecord]:
    """Public alias — never raises on bad input."""
    try:
        return parse_decision_log(raw, **kwargs)
    except Exception:
        return []
