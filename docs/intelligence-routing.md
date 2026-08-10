# HyperMind Intelligence Routing

**Status:** Foundation v0.1  
**Package:** `hypermind/`  
**CLI:** `python hypermind.py route "..."`  

Provider-neutral request routing for future HyperMind agents.  
Cursor is a development environment only — this runtime does not depend on Cursor APIs.

---

## Architecture

```mermaid
flowchart LR
  U[User Request] --> I[Intent Router]
  I --> P[Project Resolver]
  P --> F[Context Profile]
  F --> Q[RetrievalQuery]
  Q --> S[Section Extractor]
  S --> R[Section Ranker]
  R --> B[Context Budget]
  B --> C[ContextPack]
  C --> M[Model Router]
  M --> E[Bounded Generate]
  E --> X[Operational Trace]
```

Execution supports **routing** plus **one bounded local generation** via Ollama when available. Context comes from the Context Engine (see `docs/context-engine.md`). No autonomous side effects or tool execution.

---

## Lifecycle of a request

1. Wrap input as `HyperMindRequest` (provider-neutral).  
2. `IntentRouter` classifies deterministically → `IntentResult`.  
3. `select_agent` / `AgentRegistry` picks a role from `agents/roles.yaml`.  
4. `ContextResolver` / `ContextBuilder` builds a **bounded ContextPack** (provenance-aware; see `docs/context-engine.md`).  
5. `ModelRouter` selects provider/model from available adapters (never LLM-chooses-LLM).  
6. `ToolRegistry` ∩ agent allowlist → `PolicyGate` filters side effects.  
7. Optional: `HyperMindExecutor` performs **one** generate using ContextPack prompt blocks.  
8. Emit `ExecutionTrace` (operational fields only).  

---

## Modules

| Module | Path | Role |
|--------|------|------|
| Request | `hypermind/request.py` | Canonical request object |
| Intent | `hypermind/intent/` | Deterministic classification |
| Agents | `hypermind/agents/` | Declarative roles YAML + registry |
| Models | `hypermind/models/` | `ModelProvider` interface + adapters + router |
| Tools | `hypermind/tools/` | Tool definitions YAML + registry |
| Policy | `hypermind/policy/` | Deterministic allow/deny |
| Context | `hypermind/context/` | Context Engine: resolver, sources, budget, pack |
| Trace | `hypermind/trace/` | JSON / JSONL operational logs |
| Pipeline | `hypermind/pipeline.py` | `IntelligenceRouter.route` |
| Executor | `hypermind/executor.py` | `HyperMindExecutor.execute` (one generate) |
| Config | `hypermind/config/` | Models + context/projects/profile |
| CLI | `hypermind.py` / `hypermind/cli.py` | `route` · `run` · `models` · `context` |

---

## Intent router

Intents: `planning` · `research` · `coding` · `design` · `writing` · `memory` · `knowledge` · `communication` · `system` · `general`

High-confidence regex rules first. Compact `reason_code` (e.g. `repo_operation`). No chain-of-thought storage.

---

## Agent registry

Declarative roles in `hypermind/agents/roles.yaml`:

- `chief_of_staff` · `researcher` · `architect` · `coder` · `design_critic` · `knowledge_curator`

Each declares supported intents, allowed tools, preferred/fallback model class, risk ceiling.

---

## Model gateway & router

`ModelProvider.generate(ModelRequest) -> ModelResponse`  

Adapters: `ollama` (real local HTTP) · `openai` / `groq` (availability stubs) · `stub` (always-on test fallback)

Availability:

- Ollama: live probe of `/api/tags` (or `HYPERMIND_OLLAMA_AVAILABLE` / `OLLAMA_HOST` / `HYPERMIND_OLLAMA_MODEL`)
- OpenAI / Groq: API key presence only in this release
- Stub: always available for routing tests

### Model-class defaults

Configured in `hypermind/config/models.yaml`:

- Explicit `models:` entries (e.g. `llama3:latest` → `local`, `llava:latest` → `vision`)
- Pattern `model_class_rules` for other installed tags (`local_fast` for `:1b`/`:3b`, vision prefixes, etc.)
- **llava is vision-reserved** — never selected for normal text generation
- HyperMind does **not** auto-download models

### Latency-aware local selection

When multiple text-eligible local models are installed, the router ranks by:

1. `latency_tier` (`fast` < `standard` < `slow`)
2. one-shot measured `estimated_latency_ms` from `.hypermind/model_latency.json`
3. model name (deterministic tie-break)

```bash
python hypermind.py models --benchmark
```

Writes a single latency sample per installed text model (optional `--include-vision`). No continuous probing.

Reason codes include `local_low_cost_match`, `latency_preferred`, `vision_required`, …

### Timeouts & streaming

```yaml
providers:
  ollama:
    timeout_seconds: 45          # generate ceiling (fail-fast; was 180)
    probe_timeout_seconds: 3     # /api/tags
    first_token_timeout_seconds: 25
    stream: false
    keep_alive: "10m"
```

CLI:

```bash
python hypermind.py run "..." --timeout 90
python hypermind.py run "..." --stream --max-tokens 256
```

Streaming uses Ollama NDJSON (`stream: true`). Timeouts return actionable errors (raise `--timeout`, try `--complexity simple`, install a smaller local model later) instead of silent 180s waits.

Config: `hypermind/config/models.yaml`

---

## Execution Layer

Bounded single-shot generation — **not** an autonomous agent loop.

### Lifecycle

1. `HyperMindExecutor.execute(request)`  
2. Route via `IntelligenceRouter` (intent → agent → bounded context → model → policy)  
3. Build provider-neutral `ModelRequest` (agent `execution_instruction` + context items + user input)  
4. Invoke **exactly one** `ModelProvider.generate`  
5. Return `ModelResponse`  
6. Record operational `ExecutionTrace` (`status=completed|failed`, `generation_count`, `duration_ms`, `context_items`)

No handoffs, tool calls, retries-as-planning, or recursive retrieval.

### Ollama adapter

- HTTP API: `GET /api/tags`, `POST /api/chat`  
- Default base URL `http://127.0.0.1:11434` (override via config or `OLLAMA_HOST`)  
- Translates `ModelRequest` ↔ Ollama messages internally  
- Typed `ProviderError` codes: `connection_failed` · `timeout` · `model_missing` · `malformed_response` · `http_error`  

### Provider detection

```text
provider: ollama
local: true
available: true|false
reason: connection_failed|model_missing|...
```

Offline Ollama does **not** crash HyperMind. `route` and `models` continue; the model router falls back (typically to `stub`).

### Agent instructions

Each role in `agents/roles.yaml` declares a short `execution_instruction` (identity + constraints). No giant hard-coded prompt library.

### Failures / fallback

| Situation | Behaviour |
|-----------|-----------|
| Ollama down | Route succeeds; `run` reports unavailable + no executable provider |
| Configured model missing | Lists installed models; does not auto-download |
| Malformed HTTP JSON | `ProviderError(malformed_response)` |
| Timeout | `ProviderError(timeout)` |

`python hypermind.py run "..."` does **not** use the stub by default (`--allow-stub` for offline demos/tests).

### Traces (generation)

```json
{
  "request_id": "...",
  "intent": "coding",
  "agent": "coder",
  "provider": "ollama",
  "model": "qwen3:8b",
  "context_items": 2,
  "route_reason": "coder_default",
  "generation_count": 1,
  "status": "completed",
  "duration_ms": 1834
}
```

Never persists chain-of-thought, full prompts (by default), vault dumps, or credentials.

### CLI

```bash
python hypermind.py route "Review the authentication module"
python hypermind.py run "Explain the architecture of this module"
python hypermind.py run "..." --trace
python hypermind.py models
```

---

## Tool registry & policy gate

Tools in `hypermind/tools/definitions.yaml`.  

Policy (deterministic):

- READ / SEARCH / git status|diff → allow if agent permitted  
- WRITE → requires agent capability  
- git commit → explicit capability  
- delete / email.send / publish → **blocked by default**  

---

## Context builder

See **`docs/context-engine.md`**.

`ContextBuilder.build(request, agent, …)` → `ContextPack` via deterministic sources (profile, decisions, project docs, repo markdown). Budgets: `max_items` / `max_chars`. No vector DB.

---

## Trace format

Routing:

```json
{
  "request_id": "...",
  "intent": "coding",
  "agent": "coder",
  "provider": "stub",
  "model": "stub-local",
  "tools_allowed": ["filesystem.read", "git.diff"],
  "route_reason": "coder_default",
  "status": "routed",
  "context_items": 4,
  "context_chars": 8420,
  "context_truncated": false,
  "context_sources": ["decision", "project", "profile"],
  "generation_count": 0
}
```

Optional persistence: `.hypermind/traces/` (gitignored).

---

## CLI

```bash
pip install -e ".[dev]"
python hypermind.py route "Review the authentication module"
python hypermind.py context "Review P-006 case study structure"
python hypermind.py run "Explain this module" --trace
python hypermind.py models
```

---

## Extension points

- Add roles in `roles.yaml` (including `execution_instruction`)  
- Add tools in `definitions.yaml` + policy rules  
- Implement `generate()` on cloud adapters or add new `ModelProvider`  
- Extend `projects.yaml` / context sources (still ContextPack-only to providers)  
- Mission Control / UI can call `IntelligenceRouter.route` / `HyperMindExecutor.execute` without Cursor coupling  

---

## Non-goals (this foundation)

Autonomous multi-agent loops · recursive planners · vector DBs · microservices · autonomous email/publish · general-purpose tool execution
