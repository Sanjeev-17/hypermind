"""Load HyperMind runtime configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from hypermind.config.context_config import (
    ContextBudgetConfig,
    ContextEngineConfig,
    ContextProfileSpec,
    ContextRoots,
    PrivacyConfig,
    ProjectIdSpec,
    ProjectSpec,
    load_context_config,
    repo_root,
)


@dataclass(frozen=True)
class OllamaConfig:
    enabled: bool = True
    base_url: str = "http://127.0.0.1:11434"
    model: str | None = None
    timeout_seconds: float = 45.0
    connect_timeout_seconds: float = 5.0
    probe_timeout_seconds: float = 3.0
    first_token_timeout_seconds: float = 25.0
    stream: bool = False
    keep_alive: str | None = "10m"


@dataclass(frozen=True)
class ModelClassRule:
    id: str
    model_class: str
    latency_tier: str = "standard"
    text_eligible: bool = True
    supports_vision: bool = False
    match_prefixes: tuple[str, ...] = ()
    match_substrings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelSpec:
    name: str
    max_context_chars: int | None = None
    model_class: str | None = None
    latency_tier: str | None = None
    text_eligible: bool | None = None
    supports_vision: bool | None = None
    timeout_seconds: float | None = None


@dataclass(frozen=True)
class ModelsConfig:
    ollama: OllamaConfig
    prefer_local: bool = True
    model_specs: dict[str, ModelSpec] = field(default_factory=dict)
    model_class_rules: tuple[ModelClassRule, ...] = ()


def _default_path() -> Path:
    return Path(__file__).with_name("models.yaml")


def _parse_model_specs(raw: dict[str, Any] | None) -> dict[str, ModelSpec]:
    out: dict[str, ModelSpec] = {}
    for name, pdata in (raw or {}).items():
        pdata = pdata or {}
        out[str(name)] = ModelSpec(
            name=str(name),
            max_context_chars=(
                int(pdata["max_context_chars"])
                if pdata.get("max_context_chars") is not None
                else None
            ),
            model_class=str(pdata["model_class"]) if pdata.get("model_class") else None,
            latency_tier=str(pdata["latency_tier"]) if pdata.get("latency_tier") else None,
            text_eligible=(
                bool(pdata["text_eligible"]) if "text_eligible" in pdata else None
            ),
            supports_vision=(
                bool(pdata["supports_vision"]) if "supports_vision" in pdata else None
            ),
            timeout_seconds=(
                float(pdata["timeout_seconds"])
                if pdata.get("timeout_seconds") is not None
                else None
            ),
        )
    return out


def _parse_class_rules(raw: list[Any] | None) -> tuple[ModelClassRule, ...]:
    if not raw:
        return (
            ModelClassRule(
                id="vision",
                model_class="vision",
                latency_tier="vision",
                text_eligible=False,
                supports_vision=True,
                match_prefixes=("llava", "bakllava", "moondream"),
            ),
            ModelClassRule(
                id="local_fast",
                model_class="local_fast",
                latency_tier="fast",
                text_eligible=True,
                match_substrings=(":1b", ":1.5b", ":2b", ":3b", "tinyllama", "phi3:mini"),
            ),
            ModelClassRule(
                id="local",
                model_class="local",
                latency_tier="standard",
                text_eligible=True,
                match_prefixes=("llama3", "llama2", "qwen", "mistral", "gemma", "phi"),
            ),
        )
    out: list[ModelClassRule] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(
            ModelClassRule(
                id=str(item.get("id") or item.get("model_class") or "rule"),
                model_class=str(item.get("model_class", "local")),
                latency_tier=str(item.get("latency_tier", "standard")),
                text_eligible=bool(item.get("text_eligible", True)),
                supports_vision=bool(item.get("supports_vision", False)),
                match_prefixes=tuple(item.get("match_prefixes") or ()),
                match_substrings=tuple(item.get("match_substrings") or ()),
            )
        )
    return tuple(out)


def load_models_config(path: Path | None = None) -> ModelsConfig:
    raw_text: str
    if path is not None:
        raw_text = path.read_text(encoding="utf-8")
    else:
        try:
            raw_text = (
                resources.files("hypermind.config")
                .joinpath("models.yaml")
                .read_text(encoding="utf-8")
            )
        except (FileNotFoundError, TypeError, AttributeError):
            raw_text = _default_path().read_text(encoding="utf-8")

    data: dict[str, Any] = yaml.safe_load(raw_text) or {}
    providers = data.get("providers") or {}
    ollama_raw = providers.get("ollama") or {}
    ollama = OllamaConfig(
        enabled=bool(ollama_raw.get("enabled", True)),
        base_url=str(ollama_raw.get("base_url", "http://127.0.0.1:11434")).rstrip("/"),
        model=ollama_raw.get("model"),
        timeout_seconds=float(ollama_raw.get("timeout_seconds", 45)),
        connect_timeout_seconds=float(ollama_raw.get("connect_timeout_seconds", 5)),
        probe_timeout_seconds=float(ollama_raw.get("probe_timeout_seconds", 3)),
        first_token_timeout_seconds=float(
            ollama_raw.get("first_token_timeout_seconds", 25)
        ),
        stream=bool(ollama_raw.get("stream", False)),
        keep_alive=(
            str(ollama_raw["keep_alive"])
            if ollama_raw.get("keep_alive") is not None
            else None
        ),
    )
    return ModelsConfig(
        ollama=ollama,
        prefer_local=bool(data.get("prefer_local", True)),
        model_specs=_parse_model_specs(data.get("models")),
        model_class_rules=_parse_class_rules(data.get("model_class_rules")),
    )


__all__ = [
    "ContextBudgetConfig",
    "ContextEngineConfig",
    "ContextProfileSpec",
    "ContextRoots",
    "ModelClassRule",
    "ModelSpec",
    "ModelsConfig",
    "OllamaConfig",
    "PrivacyConfig",
    "ProjectIdSpec",
    "ProjectSpec",
    "load_context_config",
    "load_models_config",
    "repo_root",
]
