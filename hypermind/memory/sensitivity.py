"""Deterministic sensitivity + secret-like rejection for memory candidates."""

from __future__ import annotations

import re

from hypermind.memory.normalize import normalize_statement
from hypermind.memory.types import MemorySensitivity

# Never propose durable storage for these patterns.
_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)\b(password|passwd|pwd)\b\s*[:=]"),
    re.compile(r"(?i)\bapi[_-]?key\b\s*[:=]"),
    re.compile(r"(?i)\b(secret|token|access[_-]?token|refresh[_-]?token)\b\s*[:=]"),
    re.compile(r"(?i)\bbearer\s+[a-z0-9\-._~+/]+=*"),
    re.compile(r"(?i)\b(sk|pk|rk|ghp|glpat)[-_][a-z0-9]{8,}"),
    re.compile(r"(?i)-----begin (rsa |ec |openssh )?private key-----"),
    re.compile(r"(?i)\b(otp|one[_-]?time[_-]?password|recovery[_-]?code|2fa[_-]?code)\b"),
    re.compile(r"(?i)\bsession[_-]?(id|cookie|key)\b\s*[:=]"),
    re.compile(r"(?i)\bauthorization\b\s*[:=]"),
)

_RESTRICTED_TERMS = frozenset(
    {
        "health",
        "diagnosis",
        "medication",
        "dating",
        "intimate",
        "ssn",
        "social security",
        "passport number",
        "bank account",
        "credit card",
        "cvv",
        "password",
        "private key",
        "recovery code",
    }
)

_PERSONAL_TERMS = frozenset(
    {
        "my wife",
        "my husband",
        "my partner",
        "my kids",
        "my children",
        "home address",
        "phone number",
        "personal email",
    }
)


def contains_secret_like(text: str) -> bool:
    if not text:
        return False
    for pat in _SECRET_PATTERNS:
        if pat.search(text):
            return True
    return False


def classify_sensitivity(statement: str) -> str:
    """Rule-based sensitivity — never trust the model alone for policy."""
    lowered = statement.lower()
    norm = normalize_statement(statement)
    for term in _RESTRICTED_TERMS:
        if term in lowered or term in norm:
            return MemorySensitivity.RESTRICTED.value
    for term in _PERSONAL_TERMS:
        if term in lowered:
            return MemorySensitivity.PERSONAL.value
    return MemorySensitivity.NORMAL.value
