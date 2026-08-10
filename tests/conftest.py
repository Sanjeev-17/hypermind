"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep provider tests isolated from developer shell overrides."""
    monkeypatch.delenv("HYPERMIND_OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("HYPERMIND_OLLAMA_AVAILABLE", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
