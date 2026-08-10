"""Markdown helpers — bounded reads with privacy path filters."""

from __future__ import annotations

import re
from pathlib import Path

from hypermind.config.context_config import PrivacyConfig


def path_denied(path: Path, privacy: PrivacyConfig, repo: Path) -> bool:
    try:
        rel = str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        rel = str(path)
    lowered = rel.replace("\\", "/").lower()
    for segment in privacy.deny_path_segments:
        if segment.lower() in lowered:
            return True
    return False


def read_markdown_bounded(
    path: Path,
    *,
    max_chars: int,
    keywords: list[str] | None = None,
) -> str | None:
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    text = text.strip()
    if not text:
        return None

    if keywords:
        excerpt = _keyword_excerpt(text, keywords, max_chars)
        if excerpt:
            return excerpt

    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20].rstrip() + "\n…[truncated]"


def _keyword_excerpt(text: str, keywords: list[str], max_chars: int) -> str | None:
    lowered = text.lower()
    hits = [k for k in keywords if k.lower() in lowered]
    if not hits:
        return None

    # Prefer heading sections that mention a keyword
    sections = re.split(r"(?m)(?=^#{1,3}\s)", text)
    ranked: list[tuple[int, str]] = []
    for section in sections:
        score = sum(1 for k in hits if k.lower() in section.lower())
        if score:
            ranked.append((score, section.strip()))
    if not ranked:
        # Fall back to windows around first hit
        idx = min(lowered.index(h.lower()) for h in hits)
        start = max(0, idx - 400)
        chunk = text[start : start + max_chars]
        return chunk.strip() + ("\n…[truncated]" if start + max_chars < len(text) else "")

    ranked.sort(key=lambda t: -t[0])
    out: list[str] = []
    total = 0
    for _, section in ranked:
        if total >= max_chars:
            break
        piece = section[: max_chars - total]
        out.append(piece)
        total += len(piece)
    body = "\n\n".join(out).strip()
    if len(body) > max_chars:
        body = body[: max_chars - 20].rstrip() + "\n…[truncated]"
    return body


def title_from_markdown(path: Path, content: str) -> str:
    """Prefer a real H1 near the top; fall back to filename."""
    for line in content.splitlines()[:20]:
        stripped = line.strip()
        if stripped.startswith("# ") and not re.match(r"^#\s+\d+[\.\)]", stripped):
            title = stripped.lstrip("#").strip()
            if title:
                return title
    return path.stem.replace("_", " ").replace("-", " ")
