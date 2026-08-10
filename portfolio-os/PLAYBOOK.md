---
# Portfolio OS — PLAYBOOK

How work flows through the OS. Producer enforces gates; specialists execute.

**Read with:** `memory-index.md` · `prompts/INDEX.md`  
**Do not** skip stages without an explicit Decision Log entry.

---

## Master pipeline

```
Research → Strategy → Architecture → Content → Visual Design → Motion
→ Implementation → Review → QA → Launch
```

Interaction + Systems sit with Visual/Motion before Implementation (see stage notes).

---

## Shared rules

- Entry: required docs exist (or create via owner skill first)
- Producer emits: `For this task, read only: …`
- One deliverable per thread
- Prefer Gold prompts from `prompts/INDEX.md`
- Exit: outputs written to canonical paths; index/DoD updated if needed

---

### 1. Research

| | |
|--|--|
| **Entry** | Clear question; not already answered in docs |
| **Required docs** | `memory-index.md`; Constitution if exists; prior research notes |
| **Skills** | portfolio-producer → portfolio-architect (or research prompt) |
| **Outputs** | Findings; new/updated `A-` assumptions; optional `E-` experiments |
| **Exit** | Question answered or scoped follow-up |
| **Review gate** | Producer: no strategy change without documented findings |

### 2. Strategy

| | |
|--|--|
| **Entry** | Research sufficient for audience/goals |
| **Required docs** | Constitution (or draft), Personas inputs |
| **Skills** | portfolio-architect · creative-director (positioning input) |
| **Outputs** | `Personas.md`, `PROJECT_INVENTORY.md` → `PROJECT_EVALUATION.md` → `Case_Slate.md`, `Conversion_Spec.md`; `D-` as needed |
| **Exit** | Slate + personas accepted (inventory + evaluation complete first — D-003) |
| **Review gate** | Producer + Architect; Creative if brand positioning shifts |

### 3. Architecture

| | |
|--|--|
| **Entry** | Strategy artefacts accepted |
| **Required docs** | Personas, Case_Slate, Conversion_Spec |
| **Skills** | portfolio-architect |
| **Outputs** | `Site_Map.md`; nav/page jobs |
| **Exit** | Site map covers slate + conversion |
| **Review gate** | Producer: pages have jobs; no orphan routes |

### 4. Content

| | |
|--|--|
| **Entry** | Slate + site map exist |
| **Required docs** | Personas, Case_Slate, site map |
| **Skills** | story-strategist → editorial-director |
| **Outputs** | Case outlines / decision maps / impact; copy decks; DDCs as needed |
| **Exit** | Hire thesis + locked copy for scoped surfaces |
| **Review gate** | No invented metrics; story before polish |

### 5. Visual Design

| | |
|--|--|
| **Entry** | Creative brief + craft bar; content direction clear for scoped surfaces |
| **Required docs** | Creative_Brief, Craft_Bar, Personas |
| **Skills** | creative-director → visual-director → systems-designer |
| **Outputs** | Visual_System, Composition_Rules; Tokens, Component_Inventory |
| **Exit** | Look locked; minimal system covers site map |
| **Review gate** | Creative taste veto; systems not overbuilt |

### 6. Motion

| | |
|--|--|
| **Entry** | Visual direction locked for surfaces that move |
| **Required docs** | Creative_Brief, Visual_System |
| **Skills** | motion-director · interaction-designer (states/flows in parallel as needed) |
| **Outputs** | Motion_System, Choreography, Reduced_Motion_Map; Interaction_Spec, State_Matrix |
| **Exit** | Motion **direction** locked before Framer motion work |
| **Review gate** | Producer: no Builder motion without Motion_System |

### 7. Implementation

| | |
|--|--|
| **Entry** | Locked specs for surface (copy, visual/system, motion/interaction as applicable) |
| **Required docs** | Per memory-index build row — only those paths |
| **Skills** | framer-builder |
| **Outputs** | Framer surface; Implementation_Notes; Deviation_Log |
| **Exit** | Scoped surface matches briefs or logged deviations |
| **Review gate** | Producer: deviations need owner confirm |

### 8. Review

| | |
|--|--|
| **Entry** | Build available (URL/staging) |
| **Required docs** | Live surface; Motion_System / State_Matrix as needed |
| **Skills** | accessibility-lead · performance-lead (review-only) |
| **Outputs** | A11y_Audit, Perf_Audit, remediation briefs |
| **Exit** | Audits filed; blockers listed |
| **Review gate** | Critical a11y/perf → no Launch |

### 9. QA

| | |
|--|--|
| **Entry** | Review audits done for release scope (or artefact ready for completeness) |
| **Required docs** | `release/RELEASE_GATE.md`, checklist, artefact, Constitution/audits as applicable |
| **Skills** | quality-auditor · hiring-manager-simulator · creative-director (category scores) · portfolio-producer |
| **Outputs** | `release/reports/{slug}.md` → READY TO SHIP / REQUIRES REVISION / BLOCKED |
| **Exit** | Explicit gate verdict |
| **Review gate** | quality-auditor final; no “complete” without READY TO SHIP |

### 10. Launch

| | |
|--|--|
| **Entry** | Portfolio Release gate = READY TO SHIP; blockers cleared or accepted in Decision Log |
| **Required docs** | Gate report, Go_No_Go, Release_Checklist |
| **Skills** | portfolio-producer · framer-builder (publish) |
| **Outputs** | Shipped site; Decision Log if needed |
| **Exit** | Live + checklist complete |
| **Review gate** | Producer closes release |

---

### Maintenance lanes (not in pipeline)

| Lane | Skill | Docs |
|------|-------|------|
| Design intelligence | design-intelligence-lab | `intelligence/*` → distill to Obsidian |
| Knowledge distill | portfolio-producer | Paper → Obsidian per KNOWLEDGE_PIPELINE |
| Prompt IP | prompt-librarian | `prompts/` + Obsidian prompt insights |
| Governance hygiene | portfolio-producer | Decision / Assumption / Experiment logs |
| Memory map | portfolio-producer | `memory-index.md` |
