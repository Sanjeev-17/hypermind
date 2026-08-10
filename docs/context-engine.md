# HyperMind Context Engine

**Status:** v0.3  
**Package:** `hypermind/context/`  
**CLI:** `python hypermind.py context "..."`  

Deterministic, bounded, provenance-aware **section-level** retrieval with **intent-specific Context Pack Profiles**.

No embeddings, vector DB, or autonomous file exploration.

---

## Principle

Retrieve the **smallest sufficient context**, not the most available context.

Budget is determined by:

```text
TASK NEED + PROJECT NEED + MODEL CONSTRAINT
```

A profile budget is a **ceiling**, not a fill target.

```text
Request → Intent (+ project hint) → Context Profile → RetrievalQuery
  → Section Extractor → Section Ranker → Budget → ContextPack → Model
```

---

## Context profiles

Configured in `hypermind/config/context.yaml` under `context_profiles`.

| Profile | Typical max chars | Profile prefs | Decision cap |
|---------|------------------:|---------------|-------------:|
| general | 3000 | no | 1 |
| design | 4000 | yes | 2 |
| writing | 4000 | yes | 2 |
| planning | 4500 | yes | 2 |
| research | 4000 | yes | 1 |
| coding | 3000 | no | 1 |
| memory / knowledge / … | ~3–3.5k | varies | 1–2 |

`ContextProfileResolver.resolve(intent, request, …)` selects the profile. Explicit `--context-profile` overrides. Invalid overrides fail closed.

### Source strategy

Profiles declare `preferred_source_types` (e.g. design → current_state, decision, profile). Coding prefers technical docs and excludes user profile by default.

### Decision caps

Relevance ranking is unchanged; only the per-profile `decisions_max` changes.

### Minimum coverage

Within a profile ceiling, HyperMind reserves slots only when candidates exist:

* project / current-state item (if a project resolved)
* one decision (if `decisions_max > 0` and a decision exists)
* profile (if `include_profile` and a profile candidate exists)

No filler is added to satisfy counts. Remaining slots fill by relevance rank.

### Agent identity

Agent role text lives in the **system instruction** (`execution_instruction`). It is **not** duplicated as a ContextItem unless a profile sets `include_agent_identity: true`.

---

## Model-specific caps

Optional in `hypermind/config/models.yaml`:

```yaml
models:
  llama3:latest:
    max_context_chars: 3500
```

Effective budget: `min(profile.max_chars, model.max_context_chars, global ceiling)`.

---

## Overrides

```bash
python hypermind.py context "Review P-006" --context-profile design
python hypermind.py context "..." --max-context-chars 5000
```

Validated ranges (default): chars 500–12000, items 1–12.

---

## Markdown section extraction & scoring

Unchanged from v0.2: heading hierarchy, section provenance (`file.md#anchor`), heading≫body scoring, excerpting, dedupe. See prior sections in git history / implementation modules:

- `hypermind/context/sections.py`
- `hypermind/context/retrieval.py`
- `hypermind/context/profiles.py`

---

## Diagnostics

```bash
python hypermind.py context "Review P-006 case study structure"
python hypermind.py context "..." --debug
```

Shows profile id, budget vs selected chars, utilization, candidates, scores.

Traces include `context_profile`, `context_budget_chars`, `context_chars`, `context_utilization`, `provider_duration_ms`.

---

## Privacy

Least-context-needed · deny Health/Dating/Personal Growth paths · no full prompt bodies in traces by default.

---

## Non-goals

Embeddings · vector DBs · LLM-selected retrieval · memory writes · tool execution · vault dumps
