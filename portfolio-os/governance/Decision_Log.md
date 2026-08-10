---
# Decision Log

Reusable project asset. Record important product, UX, content, visual, motion, and technical decisions.  
**Do not** treat chat history as the source of truth.

**Owner:** portfolio-producer (process) · specialist named in each row (content)  
**Authoritative:** yes  
**Path:** `portfolio-os/governance/Decision_Log.md`

---

## How to use

1. Assign next ID: `D-NNN`
2. Fill all fields before marking `Accepted`
3. Link Related Documents (memory-index paths)
4. Set Review Date for reversible or high-risk decisions

### Status

`Proposed` · `Accepted` · `Superseded` · `Rejected`

### Categories

`product` · `ux` · `content` · `visual` · `motion` · `technical` · `process`

---

## Index

| ID | Title | Category | Owner | Status | Date | Review |
|----|-------|----------|-------|--------|------|--------|
| D-001 | Adopt permanent Writing Standard | process | editorial-director / portfolio-producer | Accepted | 2026-08-02 | 2026-11-02 |
| D-002 | Add design-intelligence-lab skill | process | portfolio-producer | Accepted | 2026-08-02 | 2026-11-02 |
| D-003 | Inventory → evaluation before Case_Slate | process | portfolio-architect / portfolio-producer | Accepted | 2026-08-02 | 2026-11-02 |
| D-004 | Adopt Release Gate system | process | portfolio-producer / quality-auditor | Accepted | 2026-08-02 | 2026-11-02 |
| D-005 | Add Release Gate levels L0–L3 | process | portfolio-producer / quality-auditor | Accepted | 2026-08-02 | 2026-11-02 |
| D-006 | Paper temporary · Obsidian permanent knowledge | process | portfolio-producer | Accepted | 2026-08-02 | 2026-11-02 |
| D-007 | Freeze HyperMind Vault v1.0 | process | portfolio-producer / HyperMind | Accepted | 2026-08-02 | 2027-02-02 |
| D-008 | Adopt Hiring Scorecard as mandatory Release Gate | process | portfolio-producer / hiring-manager-simulator / quality-auditor | Accepted | 2026-08-02 | 2026-11-02 |

---

## Entries

### D-001 — Adopt permanent Writing Standard

| Field | Value |
|-------|-------|
| Decision ID | D-001 |
| Title | Adopt permanent Writing Standard |
| Category | process |
| Date | 2026-08-02 |
| Owner | editorial-director (steward) · portfolio-producer |
| Context | Portfolio build phase; risk of AI marketing tone across skills |
| Problem | No single enforceable writing constitution for text-producing skills |
| Alternatives Considered | 1. Per-skill voice notes only 2. Prompt-only bans 3. Permanent OS Writing Standard |
| Decision | Add `portfolio-os/WRITING_STANDARD.md` as authoritative; wire into producer, story, editorial, creative, librarian + memory-index |
| Reasoning | One constitution beats fragmented rules; token-cheap to load when text is generated |
| Tradeoffs | Slightly more required context on writing tasks |
| Dependencies | memory-index; named skills |
| Status | Accepted |
| Related Documents | `WRITING_STANDARD.md`, `Portfolio_OS_v1.0.md` |
| Review Date | 2026-11-02 |

### D-002 — Add design-intelligence-lab skill

| Field | Value |
|-------|-------|
| Decision ID | D-002 |
| Title | Add design-intelligence-lab skill |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-producer |
| Context | Need principle-driven inspiration research without copying |
| Problem | No specialist to reverse-engineer exceptional work into reusable language |
| Alternatives Considered | 1. Fold into creative-director 2. Ad-hoc chat research 3. Dedicated design-intelligence-lab skill |
| Decision | Add `design-intelligence-lab`; outputs under `portfolio-os/intelligence/`; wire producer + memory-index |
| Reasoning | Separates research-from-inspiration from taste ownership (Creative Director) and execution (Visual/Motion) |
| Tradeoffs | One more skill to route; reduces copy-risk if guardrails held |
| Dependencies | Product Brief, Writing Standard, Creative Director handoff |
| Status | Accepted |
| Related Documents | `.cursor/skills/design-intelligence-lab/SKILL.md`, `intelligence/` |
| Review Date | 2026-11-02 |

### D-004 — Adopt Release Gate system

| Field | Value |
|-------|-------|
| Decision ID | D-004 |
| Title | Adopt Release Gate system |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-producer · quality-auditor |
| Context | Need a single completeness checkpoint for every artefact |
| Problem | “Done” was informal; risk of shipping without strategy/writing/hiring checks |
| Alternatives Considered | 1. QA-only at portfolio launch 2. Per-skill DoD only 3. Unified Release Gate for all artefacts |
| Decision | Add `portfolio-os/release/` gate + checklist + report; wire Producer, Creative Director, QA, HM Simulator |
| Reasoning | One governance checkpoint scales from Product Brief to full portfolio release |
| Tradeoffs | Extra step per artefact; prevents false completes |
| Dependencies | WRITING_STANDARD, Decision Log, memory-index |
| Status | Accepted |
| Related Documents | `release/RELEASE_GATE.md`, checklist, report template |
| Review Date | 2026-11-02 |

### D-005 — Add Release Gate levels L0–L3

| Field | Value |
|-------|-------|
| Decision ID | D-005 |
| Title | Add Release Gate levels L0–L3 |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-producer · quality-auditor |
| Context | Uniform scrutiny was too heavy for typos and too light if mis-applied |
| Problem | One gate intensity for all artefacts |
| Alternatives Considered | 1. Single gate forever 2. Ad-hoc skip rules 3. Explicit L0–L3 with required reviewers |
| Decision | L0 Producer; L1 Producer+Creative; L2 Creative+QA; L3 Creative+QA+HM. Portfolio pages/release = L3. |
| Reasoning | Matches scrutiny to risk; keeps production pages under HM review |
| Tradeoffs | Producer must assign level correctly (under-level = process Fail) |
| Dependencies | RELEASE_GATE.md |
| Status | Accepted |
| Related Documents | `release/RELEASE_GATE.md` |
| Review Date | 2026-11-02 |

### D-006 — Paper temporary · Obsidian permanent knowledge

| Field | Value |
|-------|-------|
| Decision ID | D-006 |
| Title | Paper temporary · Obsidian permanent knowledge |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-producer |
| Context | Need durable knowledge without treating Paper as source of truth |
| Problem | Insights risk dying in temporary canvases; duplication across tools |
| Alternatives Considered | 1. Paper as permanent store 2. GitHub markdown only 3. Obsidian permanent + Paper temporary + GitHub OS |
| Decision | Paper = exploration; Obsidian = permanent linked knowledge; GitHub = OS/skills/prompts; Framer = final portfolio. Pipeline: Research → Paper → Distill → Obsidian → Decisions. |
| Reasoning | Separates experiment from memory; improves reuse and token efficiency |
| Tradeoffs | Distillation step required after Paper sessions |
| Dependencies | KNOWLEDGE_PIPELINE, KNOWLEDGE_STANDARDS, OBSIDIAN_STRUCTURE |
| Status | Accepted |
| Related Documents | `knowledge/KNOWLEDGE_PIPELINE.md`, `KNOWLEDGE_STANDARDS.md`, `OBSIDIAN_STRUCTURE.md` |
| Review Date | 2026-11-02 |

### D-007 — Freeze HyperMind Vault v1.0

| Field | Value |
|-------|-------|
| Decision ID | D-007 |
| Title | Freeze HyperMind Vault v1.0 |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-producer · HyperMind |
| Context | Vault scaffold reached production quality; knowledge creation about to begin |
| Problem | Structural churn after knowledge accumulates destroys retrieval and AI contracts |
| Alternatives Considered | 1. Keep evolving folders indefinitely 2. Freeze later after first research wave 3. Freeze v1.0 now with Decision Log + version bump rule |
| Decision | Freeze HyperMind Vault at v1.0 (`HYPERMIND_VAULT_v1.0.md`). Structure includes Evergreen, lifecycle YAML, Design Pattern Library, Context Packs, Prompt Library workflow. Future structural changes require Decision Log + version bump + reason. |
| Reasoning | Locks AI/human contracts; enables compounding knowledge without redesign |
| Tradeoffs | Improvements wait for v1.x/v2; Context Packs start as stubs |
| Dependencies | Vault docs under `90 System/Documentation`; D-006 |
| Status | Accepted |
| Related Documents | Vault `HYPERMIND_VAULT_v1.0.md`, `VAULT_ARCHITECTURE.md`, `KNOWLEDGE_STANDARDS.md`, `knowledge/OBSIDIAN_STRUCTURE.md` |
| Review Date | 2027-02-02 |

### D-008 — Adopt Hiring Scorecard as mandatory Release Gate

| Field | Value |
|-------|-------|
| Decision ID | D-008 |
| Title | Adopt Hiring Scorecard as mandatory Release Gate |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-producer · hiring-manager-simulator · creative-director · quality-auditor |
| Context | Need a permanent hiring simulation before major portfolio milestones — not design critique |
| Problem | Release Gate Hiring Confidence was thin; visual polish could dominate; no shared HM+Creative+QA scorecard |
| Alternatives Considered | 1. HM_Review notes only 2. Aesthetic reviews as gate 3. Weighted Hiring Scorecard mandatory on major milestones / L3 |
| Decision | Add `governance/HIRING_SCORECARD.md` + template. Aggregate HM Simulator, Creative Director, Quality Auditor. Weighted 1–5 prioritising hire impact over craft. Mandatory before complete on major milestones and L3. Map Final Decision → Release Gate verdict. |
| Reasoning | Maximises interview conversion; forces evidence-based confidence; prevents polish-led ship decisions |
| Tradeoffs | Extra process on milestones; must not apply full scorecard to L0 noise |
| Dependencies | RELEASE_GATE, Personas, WRITING_STANDARD, PORTFOLIO_NARRATIVE |
| Status | Accepted |
| Related Documents | `governance/HIRING_SCORECARD.md`, `HIRING_SCORECARD.template.md`, `release/RELEASE_GATE.md` |
| Review Date | 2026-11-02 |

### D-003 — Inventory → evaluation before Case_Slate

| Field | Value |
|-------|-------|
| Decision ID | D-003 |
| Title | Inventory → evaluation before Case_Slate |
| Category | process |
| Date | 2026-08-02 |
| Owner | portfolio-architect · portfolio-producer |
| Context | Case_Slate was attempted without a raw project catalogue; risk of invented or premature cuts |
| Problem | No gated path from raw projects → scored evaluation → slate → flagship |
| Alternatives Considered | 1. Jump to Case_Slate from chat inventory 2. Single inventory+slate doc 3. Split PROJECT_INVENTORY then PROJECT_EVALUATION then Case_Slate |
| Decision | Require `strategy/PROJECT_INVENTORY.md` (catalogue only, no rank/cut) → `strategy/PROJECT_EVALUATION.md` → `strategy/Case_Slate.md` → flagship selection. Missing facts = Needs Validation. No invention. |
| Reasoning | Separates facts from judgment; protects Writing Standard and A-005 |
| Tradeoffs | Extra artefacts before slate; slower until owner fills inventory |
| Dependencies | Owner project intake; memory-index |
| Status | Accepted |
| Related Documents | `strategy/PROJECT_INVENTORY.md`, `producer/Work_Brief.md`, Assumption A-005 |
| Review Date | 2026-11-02 |
