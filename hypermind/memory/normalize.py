"""Deterministic statement normalization for memory comparison."""

from __future__ import annotations

import re
import unicodedata


_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize_statement(text: str) -> str:
    """Trim, NFKC, lowercase, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    value = unicodedata.normalize("NFKC", text).strip().lower()
    value = _PUNCT_RE.sub(" ", value)
    value = _SPACE_RE.sub(" ", value).strip()
    return value


def token_set(text: str) -> set[str]:
    norm = normalize_statement(text)
    return {t for t in norm.split(" ") if len(t) > 2}
