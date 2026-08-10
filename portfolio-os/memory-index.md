---
# Portfolio OS — Memory Layer

Single source of truth for **what to read / update / trust**.  
Portfolio Producer consults this **first**, then loads **only** the listed paths.

Paths under `portfolio-os/` unless noted.  
Missing file → create via **Owner** skill (never invent in chat).

---

## Memory answers

| Question | Where |
|----------|--------|
| Which document owns what? | Document map · Answers column |
| Which skill owns each document? | Document map · Owner |
| What to read for a task? | Task → read set |
| What to update after work? | Document map · Update when |
| What is authoritative? | Authority section |
| What is archived? | Archived section |

---

## How to use (Producer)

1. Match task → read set (below).
2. Emit: `For this task, read only: [list].`
3. Prefer project docs over re-reasoning.
4. After work: update only docs in **Update when**.
5. Never load all of `portfolio-os/` or `prompts/`.

---

## Authority

| Class | Meaning | Examples |
|-------|---------|----------|
| **Authoritative** | Source of truth for that concern | Product_Brief, WRITING_STANDARD, RELEASE_GATE, KNOWLEDGE_PIPELINE, KNOWLEDGE_STANDARDS, Constitution, Personas, PROJECT_INVENTORY, PROJECT_EVALUATION, Case_Slate, Site_Map, Creative_Brief, Motion_System, Tokens, audits, Release_Readiness, Decision_Log, Assumption_Register, Experiment_Log, memory-index, PLAYBOOK, Portfolio_OS_v1.0, Obsidian permanent notes |
| **Working** | Current task only; may be overwritten | `producer/Work_Brief.md`, Paper boards |
| **Derived** | Must not contradict authoritative parents | Copy decks ← outlines; Framer build ← specs |
| **Archived** | Historical; do not use for new production work | `archive/**`, deprecated prompts, Obsidian `90-Archive` |

Conflict rule: Authoritative parent wins. Log exceptions in Decision_Log + Deviation_Log.

---

## Task → read set

| Task | Read only |
|------|-----------|
| Intake / route | `memory-index.md`, `PLAYBOOK.md` (if stage unclear); `../prompts/INDEX.md` if using a library prompt |
| OS / governance | `Portfolio_OS_v1.0.md`, `PLAYBOOK.md`, relevant `governance/*` |
| Design intelligence / inspiration research | `WRITING_STANDARD.md`, `knowledge/KNOWLEDGE_PIPELINE.md`, `../portfolio/Product_Brief.md`, Personas/Constitution/Creative Brief if present, user reference list only |
| Knowledge distill (Paper → Obsidian) | `knowledge/KNOWLEDGE_PIPELINE.md`, `knowledge/KNOWLEDGE_STANDARDS.md`, named Paper export / notes only — not full vault |
| Recall a principle | Single Obsidian note path (from vault map) + `WRITING_STANDARD.md` if rewriting |
| Product / strategy brief | `../portfolio/Product_Brief.md`, `WRITING_STANDARD.md` (+ Constitution when it exists) |
| Any text generation or copy review | `WRITING_STANDARD.md` + artefacts for that surface only |
| Author/review prompts | `../prompts/SPEC.md`, `../prompts/PROMPT_GUIDELINES.md`, `../prompts/INDEX.md`, `WRITING_STANDARD.md`, target prompt only |
| Research / strategy / IA | `WRITING_STANDARD.md`, `constitution/Portfolio_Constitution.md`, `strategy/Personas.md`, `strategy/PROJECT_INVENTORY.md`, `strategy/PROJECT_EVALUATION.md` (when present), `strategy/Case_Slate.md`, `strategy/Site_Map.md`, `strategy/Conversion_Spec.md` |
| Project inventory / evaluation | `WRITING_STANDARD.md`, `../portfolio/Product_Brief.md`, `strategy/PROJECT_DISCOVERY.md`, `strategy/PROJECT_DISCOVERY_REPORT.md`, `strategy/PROJECT_INVENTORY.md`, `strategy/PROJECT_EVALUATION.md` (when present) |
| Case narrative / DDCs | `WRITING_STANDARD.md`, `strategy/Personas.md`, `strategy/PORTFOLIO_NARRATIVE.md`, `strategy/PORTFOLIO_BLUEPRINT.md`, `strategy/EXPERIENCE_BLUEPRINT.md`, `story/{case}-*`, `governance/Design_Decision_Card.template.md` |
| Creative | `WRITING_STANDARD.md`, Constitution, Personas, `creative/Creative_Brief.md`, `creative/Craft_Bar.md` |
| Visual | Creative_Brief, Craft_Bar, `visual/*` needed |
| Motion | Creative_Brief, Visual_System, `motion/*` needed |
| Interaction | Site_Map, Component_Inventory, `interaction/*` |
| Systems | Visual_System, `systems/*` |
| Copy | `WRITING_STANDARD.md`, Creative_Brief, story outline, `editorial/*` needed |
| Framer build | Producer brief + **locked specs for that surface only** |
| A11y / Perf review | Live URL + Motion_System / State_Matrix as needed + prior audit if any |
| Release Gate (artefact complete?) | `release/RELEASE_GATE.md`, `release/RELEASE_CHECKLIST.md`, artefact under review, `WRITING_STANDARD.md`, related audits/HM notes only |
| HM / Release | Constitution, Personas, Case_Slate, audits, `qa/*`, `governance/HIRING_SCORECARD.md`, `hm/scorecards/*`, `hm/HM_Review.md`, `release/RELEASE_GATE.md`, DoD |
| Log a decision / assumption / experiment | Relevant `governance/*` log only (+ related authoritative doc if amending it) |

---

## Document map

| Document | Answers | Owner | Auth | Read when | Update when |
|----------|---------|-------|------|-----------|-------------|
| `../portfolio/Product_Brief.md` | Portfolio product strategy (objectives, positioning, constraints) | portfolio-architect (+ story-strategist) | Auth | Strategy start; before personas/slate | Strategy pivots |
| `WRITING_STANDARD.md` | Writing constitution for all generated text | editorial-director (steward); all text skills | Auth | Any text generation or review | Standard amendments (Decision Log + version bump) |
| `intelligence/Research_*.md` | Inspiration reverse-engineering reports | design-intelligence-lab | Auth (research) | Before visual/motion language; competitive design study | After each study |
| `intelligence/Principles_*.md` | Extracted reusable design principles | design-intelligence-lab | Auth (research) | Creative / visual / motion briefing | After principle extraction |
| `intelligence/Patterns_*.md` | Visual / interaction / motion pattern libraries | design-intelligence-lab | Auth (research) | Systems / visual / motion | Append on new patterns |
| `intelligence/Portfolio_Recs_*.md` | Portfolio-specific implications (no copying) | design-intelligence-lab | Auth (research) | Architect, creative, HM review | After each study |
| `release/RELEASE_GATE.md` | When an artefact may be marked complete | portfolio-producer · quality-auditor | Auth | Before marking any artefact complete | Gate rules change (Decision + version) |
| `release/RELEASE_CHECKLIST.md` | Per-category pass criteria | quality-auditor | Auth | Every Release Gate run | Checklist amendments |
| `release/RELEASE_REPORT.template.md` | Report schema | quality-auditor | Auth (schema) | Every gate run | Schema changes |
| `release/reports/*.md` | Gate verdict for an artefact | quality-auditor | Auth | Completeness claims; portfolio release | Each gate run |
| `knowledge/KNOWLEDGE_PIPELINE.md` | Paper → Obsidian → decisions flow | portfolio-producer | Auth | Any research/knowledge task | Pipeline changes |
| `knowledge/KNOWLEDGE_STANDARDS.md` | Permanent note schema | portfolio-producer | Auth | Distilling to Obsidian | Standards changes |
| `knowledge/OBSIDIAN_STRUCTURE.md` | Vault folder map | portfolio-producer | Auth | Vault setup / new note placement | Structure changes |
| Obsidian vault notes | Long-term reusable knowledge | note author | Auth (knowledge) | Recall principles; after Paper distillation | When insight changes |
| Paper boards | Temporary exploration only | — | Working / temp | Exploration sessions | Discard after distill |
| `memory-index.md` | What to load/update/trust | portfolio-producer | Auth | Every route | Doc add/rename/ownership |
| `PLAYBOOK.md` | Stage workflows & gates | portfolio-producer | Auth | Stage unclear; onboarding | Pipeline changes |
| `Portfolio_OS_v1.0.md` | Frozen OS reference | portfolio-producer | Auth | OS questions; release | Only on OS version bump |
| `governance/Decision_Log.md` | Why we chose X | portfolio-producer + owners | Auth | Decisions; QA | Each important decision |
| `governance/Assumption_Register.md` | What we believe unproven | portfolio-producer + owners | Auth | Strategy; validation | New/resolved assumptions |
| `governance/Experiment_Log.md` | What we tested | owners | Auth | Experiments | Each experiment |
| `governance/Design_Decision_Card.template.md` | DDC schema for cases | story-strategist | Auth (schema) | Writing case decisions | Schema changes only |
| `../prompts/ARCHITECTURE.md` | Prompt system overview | prompt-librarian | Auth | Prompt system | Arch changes |
| `../prompts/SPEC.md` | Prompt rules/tiers | prompt-librarian | Auth | Prompt author/review | Spec changes |
| `../prompts/PROMPT_GUIDELINES.md` | Prompt body contract | prompt-librarian | Auth | Prompt author/review | Guideline changes |
| `../prompts/INDEX.md` | Which prompt / tier | producer + librarian | Auth | Routing with prompts | Prompt lifecycle |
| `constitution/Portfolio_Constitution.md` | Non-negotiables | producer (+ creative craft) | Auth | Strategy, creative, QA, HM | Goals/constraints change |
| `strategy/Personas.md` | Who we optimize for | portfolio-architect | Auth | Architect→HM | Audience change |
| `strategy/PROJECT_DISCOVERY.md` | Source-backed discovery log + pending Mastercard | portfolio-architect | Auth | Before/while inventory | Each discovery pass |
| `strategy/PROJECT_DISCOVERY_REPORT.md` | Discovery summary + user questions | portfolio-architect | Auth | After discovery pass | Each pass |
| `strategy/PROJECT_INVENTORY.md` | Raw project catalogue (no rank/cut) | portfolio-architect | Auth | Before evaluation/slate | Project list or clearance change |
| `strategy/PROJECT_EVALUATION.md` | Scored/cut rationale before slate | portfolio-architect | Auth | After inventory; before Case_Slate | Evaluation change |
| `strategy/Case_Slate.md` | What ships | portfolio-architect | Auth | Architect, story, HM, QA | Slate change |
| `strategy/Site_Map.md` | Pages & jobs | portfolio-architect | Auth | IA, interaction, build, QA | IA change |
| `strategy/Conversion_Spec.md` | Funnel/CTAs | portfolio-architect | Auth | Architect, editorial, build, QA | Funnel change |
| `strategy/Competitive_Teardown.md` | Peer positioning | portfolio-architect | Auth | Architect, creative | New insight |
| `story/{case}-Outline.md` | Hire thesis / beats | story-strategist | Auth | Story, editorial, craft beats | Argument change |
| `story/{case}-Decision_Map.md` | Options/tradeoffs | story-strategist | Auth | Story, editorial, HM | Decisions change |
| `story/{case}-Impact.md` | Claims/evidence | story-strategist | Auth | Story, editorial, HM, QA | Evidence change |
| `story/{case}/decisions/DDC-*.md` | Case decision cards | story-strategist | Auth (case) | Case work | Decision change |
| `creative/Creative_Brief.md` | Creative direction | creative-director | Auth | Craft skills | Direction pivot |
| `creative/Craft_Bar.md` | Must/banned | creative-director | Auth | Visual, motion, systems, QA | Taste bar change |
| `creative/Brand_World.md` | Brand expression | creative-director | Auth | Creative, visual, editorial | Brand change |
| `visual/Visual_System.md` | Visual language | visual-director | Auth | Visual, systems, motion, build | Look change |
| `visual/Composition_Rules.md` | Composition | visual-director | Auth | Visual, build, QA | Layout rules |
| `visual/Art_Direction.md` | Media direction | visual-director | Auth | Visual, build | Media plan |
| `motion/Motion_System.md` | Motion language | motion-director | Auth | Motion, build, reviews, QA | Motion direction |
| `motion/Choreography.md` | Beats/transitions | motion-director | Auth | Motion, build | Choreography |
| `motion/Reduced_Motion_Map.md` | Reduced motion | motion-director | Auth | Motion, a11y, build | Motion system |
| `interaction/Interaction_Spec.md` | Flows/nav | interaction-designer | Auth | Interaction, build, a11y, QA | Flows |
| `interaction/State_Matrix.md` | States | interaction-designer | Auth | Interaction, systems, build, a11y | States |
| `systems/Tokens.md` | Tokens | systems-designer | Auth | Systems, build | Tokens |
| `systems/Component_Inventory.md` | Components | systems-designer | Auth | Systems, interaction, build | Components |
| `systems/Paper_Framer_Parity.md` | Parity | systems-designer | Auth | Systems, build | Handoff rules |
| `editorial/Voice_Guide.md` | Voice | editorial-director | Auth | Editorial, build, QA | Voice |
| `editorial/Bio.md` | Bio copy | editorial-director | Auth | Editorial, build | Bio |
| `editorial/{surface}-Copy_Deck.md` | Locked copy | editorial-director | Auth | Editorial, build | Copy |
| `build/Implementation_Notes.md` | What built | framer-builder | Auth (build) | Build, QA, perf | After build |
| `build/Deviation_Log.md` | Spec vs ship | framer-builder | Auth | Build, QA, producer | Deviations |
| `a11y/A11y_Audit.md` | A11y status | accessibility-lead | Auth | A11y, QA, release | Each audit |
| `a11y/Remediation_Brief.md` | Fix outcomes | accessibility-lead | Auth | A11y, build, producer | Failed audits |
| `perf/Perf_Audit.md` | Perf status | performance-lead | Auth | Perf, QA, release | Each audit |
| `qa/Release_Readiness.md` | Release checklist | quality-auditor | Auth | QA, producer | Each RC |
| `qa/Go_No_Go.md` | Ship verdict | quality-auditor | Auth | Producer release | Each verdict |
| `governance/HIRING_SCORECARD.md` | Mandatory hiring simulation for major milestones | hiring-manager-simulator / QA | Auth | L3 / major release | Gate rule changes |
| `governance/HIRING_SCORECARD_PERSONAS.md` | Multi-HM lens sim (planned) | hiring-manager-simulator | Planned | Cluster-targeted review | When activated via Decision Log |
| `hm/HM_Review.md` | Hiring confidence | hiring-manager-simulator | Auth | HM, QA, release | Each sim |
| `producer/Work_Brief.md` | Current task | portfolio-producer | Working | Active task | Every task |
| `producer/Definition_Of_Done.md` | DoD | portfolio-producer | Auth | Task/release | DoD change |
| `producer/Release_Checklist.md` | Release process | portfolio-producer | Auth | Release | Process change |

---

## Archived

| Location | Rule |
|----------|------|
| `portfolio-os/archive/**` | Do not read for production unless recovering history |
| `prompts/archive/**` | Deprecated prompts — use INDEX successor |
| Superseded Decision Log entries | Status `Superseded` — follow replacement ID |

---

## Question → document

| Question | Document |
|----------|----------|
| How does work flow? | `PLAYBOOK.md` |
| What is the portfolio product strategy? | `../portfolio/Product_Brief.md` |
| What writing rules apply? | `WRITING_STANDARD.md` |
| What did we learn from inspiration research? | `intelligence/Research_*.md` / `Principles_*.md` |
| Where does permanent knowledge live? | `C:\Obsidian vaults\Hypermind vault` — [[Home]]; freeze `HYPERMIND_VAULT_v1.0` (D-007) |
| Vault architecture / standards | Vault `90 System/Documentation/*` (pointers in `OBSIDIAN_STRUCTURE.md`) |
| AI briefing without vault dump | Vault `90 System/Context Packs/<domain>.md` |
| How does Paper relate to Obsidian? | `knowledge/KNOWLEDGE_PIPELINE.md` + vault `KNOWLEDGE_WORKFLOW` |
| How do I connect Cursor ↔ Obsidian MCP? | `knowledge/OBSIDIAN_CONNECTION.md` + vault `MCP_READINESS` |
| Can this artefact ship / be marked complete? | `release/reports/*.md` + `release/RELEASE_GATE.md` |
| What is OS v1.0? | `Portfolio_OS_v1.0.md` |
| Why did we decide X? | `governance/Decision_Log.md` |
| What might be wrong? | `governance/Assumption_Register.md` |
| What did we test? | `governance/Experiment_Log.md` |
| Which prompt / tier? | `../prompts/INDEX.md` |
| Prompt body rules? | `../prompts/PROMPT_GUIDELINES.md` |
| Non-negotiables? | `constitution/Portfolio_Constitution.md` |
| Who is this for? | `strategy/Personas.md` |
| What projects exist? | `strategy/PROJECT_INVENTORY.md` |
| What was discovered from sources? | `strategy/PROJECT_DISCOVERY.md` / `PROJECT_DISCOVERY_REPORT.md` |
| How were projects scored/cut? | `strategy/PROJECT_EVALUATION.md` |
| What ships? | `strategy/Case_Slate.md` |
| Pages? | `strategy/Site_Map.md` |
| Convert how? | `strategy/Conversion_Spec.md` |
| Case thesis / decisions / impact? | `story/{case}-*` |
| Creative / craft bar? | `creative/Creative_Brief.md` / `Craft_Bar.md` |
| Visual / motion / interaction / tokens? | `visual/*` · `motion/*` · `interaction/*` · `systems/*` |
| Locked copy? | `editorial/{surface}-Copy_Deck.md` |
| Spec vs shipped? | `build/Deviation_Log.md` |
| A11y / perf / HM / release? | audits · `hm/HM_Review.md` · `qa/*` |

---

## Rules

1. Never “read everything under `portfolio-os/`.”
2. Work briefs include explicit **Read only** lists from this file.
3. Missing doc → Owner skill creates it.
4. Prefer paths over pasting bodies.
5. Rename/add docs → update this index in the same change.
6. Archived/deprecated ≠ authoritative for new work.
