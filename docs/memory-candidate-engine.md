# HyperMind Memory Candidate Engine

**Status:** Phase 6A  
**Package:** `hypermind/memory/`  
**CLI:** `python hypermind.py memory propose --json`  

HyperMind may propose structured memory candidates.  
HyperMind must **not** write durable memory in this phase.

---

## Lifecycle

```text
Input text (+ optional project / source_refs)
  → knowledge_curator + memory context profile
  → ONE model generation (memory analysis instruction)
  → strict JSON parse
  → sensitivity + secret filters
  → duplicate / update / conflict compare vs retrieved context
  → CandidateMemory[] for human review elsewhere
```

No candidate becomes durable without later explicit approval (Mission Control / Phase 6B).

---

## Categories

`FACT` · `PREFERENCE` · `GOAL` · `CONSTRAINT` · `CURRENT_STATE` · `PROJECT_CONTEXT` · `DECISION_CANDIDATE`

`DECISION_CANDIDATE` is a proposal only — not a Decision Ledger write (Phase 7).

## Scopes

`global` · `project` · `session`

Prefer `global` / `project` for persistence proposals. Low-confidence `session` items are suppressed.

---

## Provenance

Every candidate includes `source_refs`. Allowed refs are the caller-supplied list plus retrieved context `source_ref` values. Fabricated refs are rejected. Default user text ref: `input:user`.

Candidates do **not** store raw conversation transcripts.

---

## Relationships

Compared against bounded retrieved context (profile, decisions, current-state) using deterministic normalization — **no embeddings**.

| Relationship | Meaning |
|--------------|---------|
| `NEW` | No strong existing match |
| `DUPLICATE` | Already represented — suppressed from default proposals, listed in `suppressed` |
| `POSSIBLE_UPDATE` | Overlapping subject with update cues |
| `POSSIBLE_CONFLICT` | Overlapping subject with conflict cues |

HyperMind never overwrites existing memory.

---

## Privacy & secrets

- Existing vault privacy deny segments remain authoritative for retrieval.
- Deterministic sensitivity: `normal` · `personal` · `restricted`.
- Restricted → `requires_explicit_sensitive_approval: true`.
- Secret-like content (passwords, API keys, tokens, private keys, OTPs, cookies) → `secret_like_content`; **no candidate proposed**; secret text is not echoed into logs/traces.

---

## Machine contract

```bash
echo '{"text":"...","project":"portfolio","source_refs":["input:user"]}' \
  | python hypermind.py memory propose --json
```

- **stdout:** JSON envelope only  
- **stderr:** diagnostics  
- Success includes `candidates`, `suppressed`, operational `trace`  
- `trace.memory_written` is always `false` in Phase 6A  
- Exactly **one** generation when a provider is available  
- Malformed model JSON → `MALFORMED_OUTPUT` (no repair retry)

---

## Non-persistence guarantee

This engine:

- does not call `memory.write` / `obsidian.write`
- does not mutate profile, decision log, or vault files
- does not create durable memory IDs (ids are `prop_…` proposal ids)

---

## Phase 6B integration boundary

Mission Control should:

1. Call `memory propose --json` with user/reflection text  
2. Render candidates for human approval  
3. Persist only approved items into MC-owned storage  
4. Never treat HyperMind proposal as already remembered  

Phase 7 will deepen Decision Ledger supersession for `DECISION_CANDIDATE` / conflicts.
