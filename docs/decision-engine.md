# HyperMind Decision Engine

**Status:** Phase 7A  
**Package:** `hypermind/decisions/`  
**CLI:** `python hypermind.py decision analyze --json`

HyperMind can recognize formal decisions, detect conflicts/supersession candidates, and prioritize ACTIVE decisions in context retrieval.

HyperMind must **not** write the Decision Log in this phase.

---

## Canonical decision model

```text
DecisionRecord
  id, title, statement
  scope: global | project
  project (when project-scoped)
  status: ACTIVE | SUPERSEDED | REJECTED | ARCHIVED
  effective_at
  supersedes[], superseded_by
  rationale
  source_refs[]
  metadata  (includes frozen: true when applicable)
```

A formal decision is not a memory statement. It carries identity, lifecycle, scope, and supersession links.

Decision Log prose statuses map as:

| Log status | Canonical |
|------------|-----------|
| Accepted | ACTIVE |
| Superseded | SUPERSEDED |
| Rejected | REJECTED |
| Archived | ARCHIVED |
| Proposed | skipped (not yet formal) |

Malformed or incomplete historical entries are skipped defensively; parsing never crashes retrieval.

---

## Lifecycle

- **ACTIVE** — authoritative for normal context and conflict checks
- **SUPERSEDED** — historical evidence; kept, never deleted
- **REJECTED** / **ARCHIVED** — inspectable, not authoritative

Mission Control UI workflow states are out of scope here.

---

## Active resolution

```python
DecisionResolver.get_active_decisions(scope=None, project=None)
```

Rules:

- Returns ACTIVE only
- SUPERSEDED excluded from authoritative context by default
- Broken `superseded_by` / `supersedes` links do not crash
- Historical inspection via `get_inspectable(include_superseded=True)`

---

## Supersession

A new statement may propose superseding one or more ACTIVE decisions when evidence includes:

- same project/scope
- overlapping subject / topic
- explicit replacement language (“replace”, “going forward”, “instead”, …)
- direct contradiction with replacement intent

Result relationship: `POSSIBLE_SUPERSESSION`  
Action proposed: `SUPERSEDE`  

Until human approval, nothing is written.

---

## Conflict semantics

Deterministic checks run first (normalized terms, scope, topic clusters, negation/replacement cues). No embeddings.

Examples:

| ACTIVE | New statement | Result |
|--------|---------------|--------|
| Portfolio OS v1.0 is frozen. | Change Portfolio OS v1.0 without a version bump. | POSSIBLE_CONFLICT |
| Use local-first model routing. | Prefer cloud-first for all tasks. | POSSIBLE_CONFLICT or POSSIBLE_SUPERSESSION |

Ambiguous mid-overlap may trigger **at most one** bounded model classification call. The model never mutates state.

Machine-readable conflict signal (analyze + context pack):

```json
{
  "decision_conflict": true,
  "decision_refs": ["D-007"],
  "reason_code": "conflicts_with_active_decision"
}
```

Conflicts are surfaced, not auto-blocked.

---

## Frozen decisions

`metadata.frozen: true` (inferred from freeze/lock language or explicit field).

Frozen ACTIVE decisions get stronger conflict signaling (`conflicts_with_frozen_decision`). Human-approved supersession remains possible later — HyperMind does not hard-immutably lock them in code.

---

## Retrieval priority

Approximate order:

1. Explicitly referenced ACTIVE decision  
2. Relevant ACTIVE decision  
3. Current-state project context  
4. Supporting memory / reference  
5. SUPERSEDED only in **historical query mode**

Historical cues include: “before D-007”, “what did X replace”, “how did our strategy change”, “superseded”, etc.

---

## Decision proposals (human review)

```text
DecisionProposal
  action: CREATE | SUPERSEDE | REJECT_AS_DUPLICATE | FLAG_CONFLICT
  candidate
  related_decisions[]
  relationship
  reason_code
  decision_conflict
```

HyperMind only proposes. Mission Control owns approval and durable writes.

Phase 6 `DECISION_CANDIDATE` payloads may be passed as `candidate` — statement text is reused, not regenerated.

---

## Machine contract

```bash
echo '{"statement":"...","project":"portfolio","source_refs":["input:user"]}' \
  | python hypermind.py decision analyze --json
```

Stdout: JSON envelope only.

```json
{
  "ok": true,
  "request_id": "...",
  "proposal": {
    "action": "FLAG_CONFLICT",
    "relationship": "POSSIBLE_CONFLICT",
    "related_decisions": ["D-001"],
    "reason_code": "conflicts_with_active_decision",
    "decision_conflict": true,
    "candidate": { "statement": "...", "category": "DECISION_CANDIDATE" }
  },
  "trace": {
    "active_decisions_inspected": 8,
    "model_generation_count": 0,
    "decision_written": false,
    "decision_log_mutated": false
  }
}
```

Trace fields (no full decision bodies by default): request id, project, scope, active count, relationship, related ids, model generation count, duration, status.

---

## No-write boundary

- No edits to `Decision_Log.md`
- No decision vault / ledger writes
- `trace.decision_written` / `decision_log_mutated` always false in this phase

---

## Mission Control integration point

1. Call `decision analyze --json` (or `DecisionAnalyzeEngine.analyze`) with statement or Phase 6 `DECISION_CANDIDATE`
2. Present `DecisionProposal` for human review
3. On approval, Mission Control persists Decision Log updates (CREATE / SUPERSEDE / reject) — **not** HyperMind Phase 7A
4. Use `ContextPack.signals.decision_conflict` when surfacing runtime warnings without blocking the user
