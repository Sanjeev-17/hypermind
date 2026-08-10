---
# Portfolio OS v1.0

**Version:** `1.0.6`  
**Status:** Frozen foundation + D-001…D-008 (Hiring Scorecard gate)  
**Date:** 2026-08-02  
**Owner:** portfolio-producer (governance of the OS)

This is the official reference for Portfolio OS v1.0.  
Do not expand the OS without a version bump and Decision Log entry.

---

## Architecture summary

Portfolio OS is an agency-style operating system for building a Senior Product Designer portfolio.

| Tool | Role |
|------|------|
| **Paper** | Temporary research / exploration |
| **Obsidian** | Permanent linked knowledge |
| **GitHub** | OS, skills, prompts, templates, versioning |
| **Framer** | Final portfolio product |
| **Cursor** | Agent + skills orchestration |

```
Research → Paper → Distill → Obsidian → Portfolio Decisions
                ↘ GitHub (OS artefacts)
                     ↘ Framer (ship)
```

**Not in scope for v1.0:** building the live portfolio site itself.

---

## Skills (16)

| Priority | Skills |
|----------|--------|
| P0 | portfolio-producer · portfolio-architect · story-strategist · creative-director |
| P1 | design-intelligence-lab · visual-director · motion-director · interaction-designer · systems-designer · editorial-director |
| P2 | framer-builder |
| P3 | accessibility-lead · performance-lead · quality-auditor · hiring-manager-simulator · prompt-librarian |

A11y + Perf = **review-only**. Motion direction **before** implementation. Producer owns workflow, not design.

Paths: `.cursor/skills/{name}/SKILL.md`  
Routing rule: `.cursor/rules/portfolio-os.mdc`

---

## Documents

| Area | Paths |
|------|--------|
| Memory / playbook / release | `memory-index.md`, `PLAYBOOK.md`, `Portfolio_OS_v1.0.md`, `WRITING_STANDARD.md`, `release/RELEASE_GATE.md`, `knowledge/KNOWLEDGE_PIPELINE.md` |
| Governance | `governance/Decision_Log.md`, `Assumption_Register.md`, `Experiment_Log.md`, `Design_Decision_Card.template.md` |
| Product content (created in build phase) | `constitution/`, `strategy/`, `story/`, `creative/`, `visual/`, `motion/`, `interaction/`, `systems/`, `editorial/`, `build/`, `a11y/`, `perf/`, `qa/`, `hm/`, `producer/` |

Authority rules: see Memory Layer in `memory-index.md`.

---

## Prompt system

| Artefact | Role |
|----------|------|
| `prompts/ARCHITECTURE.md` | System overview |
| `prompts/SPEC.md` | Metadata, lifecycle, semver, quality, tiers |
| `prompts/PROMPT_GUIDELINES.md` | Mandatory body structure |
| `prompts/INDEX.md` | Searchable catalog |
| `prompts/_templates/` | Starter shells |
| Categories + `archive/` | Library + deprecated IP |
| prompt-librarian | Maintenance |

**Tiers:** ⭐ Gold (preferred) · 🥈 Silver · 🧪 Experimental (never production)

---

## Memory system

`portfolio-os/memory-index.md` answers: ownership, read sets, update triggers, authoritative vs archived.

Producer always starts there and emits an explicit read-only list.

---

## Workflow

Defined in `PLAYBOOK.md`:

Research → Strategy → Architecture → Content → Visual → Motion → Implementation → Review → QA → Launch

Each stage: entry · required docs · skills · outputs · exit · review gates.

---

## Review gates

| Gate | Skill |
|------|--------|
| Taste / craft | creative-director |
| Motion before build | motion-director artefacts exist |
| Spec lock before Framer | portfolio-producer |
| A11y | accessibility-lead |
| Perf | performance-lead |
| **Release Gate (artefact complete)** | quality-auditor (+ producer, creative, HM as required) |
| Hiring confidence (category) | hiring-manager-simulator |
| Ship | producer + READY TO SHIP |

---

## Governance

| Tool | Use |
|------|-----|
| Decision Log | Important decisions |
| Assumption Register | Unproven beliefs |
| Experiment Log | Tests & outcomes |
| Design Decision Cards | Case-level decisions |
| Deviation Log | Spec vs implementation |
| Release Gate | Completeness verdict per artefact |
| Hiring Scorecard | Mandatory hire sim on major/L3 (D-008); persona lenses planned |

---

## Release notes — v1.0.6

- Hiring Scorecard mandatory on major milestones / L3 (D-008)
- Specced **persona-based HM simulations** for later activation (`HIRING_SCORECARD_PERSONAS.md`) — not gate-mandatory yet

## Release notes — v1.0.5

- Obsidian = permanent knowledge; Paper = temporary research
- Added `knowledge/KNOWLEDGE_PIPELINE.md`, `KNOWLEDGE_STANDARDS.md`, `OBSIDIAN_STRUCTURE.md`
- Wired Producer, design-intelligence-lab, prompt-librarian, memory-index
- Decision Log D-006

## Release notes — v1.0.4

- Release Gate **levels L0–L3** with required reviewers
- Producer assigns level; QA verdicts L2–L3; HM required on L3
- Decision Log D-005

## Release notes — v1.0.3

- Added Release Gate under `portfolio-os/release/`
- Artefacts incomplete until READY TO SHIP / REQUIRES REVISION / BLOCKED
- Wired Producer, Creative Director, Quality Auditor, HM Simulator
- Decision Log D-004

## Release notes — v1.0.2

- Added **design-intelligence-lab** (inspiration → principles; never copy)
- Outputs under `portfolio-os/intelligence/`
- Producer + memory-index routing; Decision Log D-002

## Release notes — v1.0.1

- Added permanent `WRITING_STANDARD.md` (writing constitution)
- Wired enforcement into portfolio-producer, story-strategist, editorial-director, creative-director, prompt-librarian
- Memory-index read sets include Writing Standard for all text tasks
- Decision Log: D-001

## Release notes — v1.0.0

- Specialist skill team (P0–P3) with clear ownership
- Memory index + token-efficient Producer routing
- Prompt Library (spec, guidelines, tiers, templates, librarian)
- PLAYBOOK stage pipeline
- Governance: decisions, assumptions, experiments, DDCs
- Review-only a11y/perf; final QA + HM simulator
- OS freeze document (this file)

---

## Known limitations

- Portfolio content artefacts (Constitution, Personas, etc.) not yet authored — schemas indexed only
- Prompt catalog empty (templates exist; no Gold prompts yet)
- No automated CI enforcing memory-index or prompt SPEC
- Framer project not started
- Paper/Playwright integrations are skill-described, not wired as pipelines

---

## Future improvements (v1.x / v2+)

- **Activate persona-based Hiring Scorecard lenses** (`HIRING_SCORECARD_PERSONAS.md`) — Big Tech · Fintech · Startup · Agency · Enterprise SaaS · Principal PD; table: Interview Probability + Top Concern per lens
- Seed Gold prompts from real production uses
- Light automation: checklist scripts / Playwright suite templates
- Optional canvas dashboards for slate/QA / multi-persona hire confidence
- Cross-project Prompt Library extraction package

---

## Freeze rule

After v1.0, change the OS only via:

1. Decision Log entry  
2. Version bump of this document  
3. memory-index / PLAYBOOK / SPEC updates as needed  

**Next phase:** build the portfolio using this OS — do not grow the OS first.
