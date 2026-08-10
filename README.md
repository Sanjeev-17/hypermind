# HyperMind

Operating system and knowledge stack for building a **Senior Product Designer** portfolio — optimized for **interview conversion**, not visual applause.

This repository is the version-controlled home for **Portfolio OS**, strategy artefacts, Cursor skills, and prompt infrastructure. The permanent knowledge vault lives in Obsidian (**Hypermind vault**); the shipped site lives in Framer.

---

## What we are building

| Layer | What it is |
|-------|------------|
| **Product** | A decision-making portfolio: *Problems · Decisions · Clarity* |
| **Job** | Help recruiters and hiring managers say **yes, interview** quickly |
| **OS** | Portfolio OS — skills, gates, playbooks, writing standard |
| **Knowledge** | Obsidian second brain (permanent) · Paper (temporary research) |
| **Ship surface** | Framer portfolio site |

**Default role signal:** Senior Product Designer (not Staff-by-default).

**Stake line:** *I solve complex product problems and communicate my thinking clearly.*

---

## Case slate (v1)

| Depth | Project | Hire signal |
|-------|---------|-------------|
| Flagship | P-006 Design system (multi-brand) | Systems thinking |
| Major | P-005 Online check-in | Decisions + research under constraint |
| Supporting | P-001 Taco Bell delivery | Consumer ownership |
| Future | Mastercard | Pending documentation |

See `portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md`.

---

## Repo map

```
portfolio-os/          Portfolio OS (playbook, governance, strategy, release, knowledge pointers)
  strategy/            Narrative, blueprint, experience blueprint, discovery/evaluation
  governance/          Decision log, hiring scorecard, assumptions
  release/             Release Gate L0–L3
.cursor/skills/        Specialist agent skills (producer, architect, HM simulator, …)
.cursor/rules/         Always-on Portfolio OS rules
portfolio/             Product Brief
prompts/               Prompt library architecture + templates
obsidian/              Stub → live vault is external Hypermind Obsidian vault
```

### Strategy stack (read in order)

1. `portfolio/Product_Brief.md`  
2. `portfolio-os/strategy/Personas.md`  
3. `portfolio-os/strategy/PORTFOLIO_NARRATIVE.md`  
4. `portfolio-os/strategy/PORTFOLIO_BLUEPRINT.md`  
5. `portfolio-os/strategy/EXPERIENCE_BLUEPRINT.md`  

Then design: Paper wireframes → hi-fi → motion → Framer → QA → launch.

---

## Tool roles

| Tool | Role |
|------|------|
| Cursor | Execution (this repo + agents) |
| Paper | Temporary research |
| Obsidian | Permanent knowledge |
| GitHub | This OS + version control |
| Framer | Final portfolio product |
| Portfolio OS | Workflow + governance |
| HyperMind | Automation + intelligence layer |

Nothing valuable should remain **only** in Paper. Distill to Obsidian / this repo.

---

## Release & hiring gates

- Artefacts are incomplete until Release Gate → **READY TO SHIP** (`portfolio-os/release/RELEASE_GATE.md`)  
- Major / L3 milestones require **Hiring Scorecard** (`portfolio-os/governance/HIRING_SCORECARD.md`)  
- Writing must follow `portfolio-os/WRITING_STANDARD.md` — no invented metrics or ownership  

---

## Status

- Portfolio OS foundation: frozen (see `portfolio-os/Portfolio_OS_v1.0.md`)  
- HyperMind Obsidian vault: v1.0 frozen (external path; see `obsidian/README.md`)  
- Strategy layer: complete through Experience Blueprint  
- Next: design implementation against the Experience Blueprint  

---

## Owner

Sanjeev Ojha — Senior Product Designer portfolio / HyperMind.
