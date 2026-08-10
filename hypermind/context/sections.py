"""Deterministic Markdown section parsing + excerpt windows."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass(frozen=True)
class MarkdownSection:
    file_ref: str
    heading: str
    heading_path: str
    level: int
    content: str
    start_line: int
    end_line: int
    anchor: str = ""

    @property
    def chars(self) -> int:
        return len(self.content)


@dataclass
class ExcerptWindow:
    start: int  # char offset in section content
    end: int
    text: str


def slug_anchor(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[^\w\s\-]", "", text)
    text = re.sub(r"\s+", "-", text).strip("-")
    return text or "section"


def parse_markdown_sections(text: str, file_ref: str) -> list[MarkdownSection]:
    """Split Markdown into heading-bounded sections with hierarchy paths."""
    if not text or not text.strip():
        return []

    lines = text.splitlines()
    # Collect heading markers (line index, level, title)
    headings: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        m = _HEADING_RE.match(line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2).strip()))

    if not headings:
        body = text.strip()
        if not body:
            return []
        return [
            MarkdownSection(
                file_ref=file_ref,
                heading="(document)",
                heading_path="(document)",
                level=0,
                content=body,
                start_line=1,
                end_line=len(lines),
                anchor="document",
            )
        ]

    sections: list[MarkdownSection] = []
    stack: list[tuple[int, str]] = []  # (level, heading)

    # Preamble before first heading
    first_line, _, _ = headings[0]
    if first_line > 0:
        preamble = "\n".join(lines[:first_line]).strip()
        if preamble:
            sections.append(
                MarkdownSection(
                    file_ref=file_ref,
                    heading="(preamble)",
                    heading_path="(preamble)",
                    level=0,
                    content=preamble,
                    start_line=1,
                    end_line=first_line,
                    anchor="preamble",
                )
            )

    for idx, (line_idx, level, title) in enumerate(headings):
        end_line = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        # Body excludes the heading line itself for content; keep heading in content for clarity
        chunk_lines = lines[line_idx:end_line]
        content = "\n".join(chunk_lines).strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        path = " > ".join(h for _, h in stack)
        sections.append(
            MarkdownSection(
                file_ref=file_ref,
                heading=title,
                heading_path=path,
                level=level,
                content=content,
                start_line=line_idx + 1,
                end_line=end_line,
                anchor=slug_anchor(title),
            )
        )
    return sections


def merge_windows(windows: list[tuple[int, int]], *, content_len: int) -> list[tuple[int, int]]:
    """Merge overlapping [start, end) windows deterministically."""
    if not windows:
        return []
    ordered = sorted((max(0, s), min(content_len, e)) for s, e in windows if e > s)
    if not ordered:
        return []
    merged: list[list[int]] = [[ordered[0][0], ordered[0][1]]]
    for s, e in ordered[1:]:
        cur = merged[-1]
        if s <= cur[1] + 40:  # small gap merge
            cur[1] = max(cur[1], e)
        else:
            merged.append([s, e])
    return [(a, b) for a, b in merged]


def excerpt_around_terms(
    content: str,
    terms: list[str],
    *,
    max_chars: int,
    window: int = 350,
    max_excerpts: int = 2,
) -> tuple[str, bool]:
    """
    Return a bounded verbatim excerpt around strongest term hits.
    If content already fits, return as-is (not excerpted).
    """
    if len(content) <= max_chars:
        return content, False

    lowered = content.lower()
    hits: list[tuple[int, str]] = []
    for term in terms:
        t = term.lower().strip()
        if len(t) < 2:
            continue
        start = 0
        while True:
            idx = lowered.find(t, start)
            if idx < 0:
                break
            hits.append((idx, t))
            start = idx + max(1, len(t))

    if not hits:
        cut = content[: max_chars - 20].rstrip() + "\n…[truncated]"
        return cut, True

    # Prefer longer term matches, then earlier position
    hits.sort(key=lambda h: (-len(h[1]), h[0]))
    windows: list[tuple[int, int]] = []
    for idx, term in hits[:8]:
        s = max(0, idx - window)
        e = min(len(content), idx + len(term) + window)
        windows.append((s, e))

    merged = merge_windows(windows, content_len=len(content))[:max_excerpts]
    parts: list[str] = []
    total = 0
    for s, e in merged:
        piece = content[s:e].strip()
        if s > 0:
            piece = "…\n" + piece
        if e < len(content):
            piece = piece + "\n…"
        if total + len(piece) > max_chars and parts:
            break
        if len(piece) > max_chars - total:
            piece = piece[: max_chars - total - 20].rstrip() + "\n…[truncated]"
        parts.append(piece)
        total += len(piece)

    text = "\n\n".join(parts).strip()
    if len(text) > max_chars:
        text = text[: max_chars - 20].rstrip() + "\n…[truncated]"
    return text, True
