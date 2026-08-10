---
# Hiring Scorecard

**Status:** Permanent Portfolio OS governance  
**Owner:** portfolio-producer (process) · hiring-manager-simulator (primary scoring) · creative-director · quality-auditor (aggregation + verdict)  
**Decision:** D-008  
**Applies to:** Every **major portfolio milestone** before it is marked complete or shipped  

This is a **hiring simulation**, not a portfolio review and not a design critique.

**One question:**  
If I were hiring this designer today, would this portfolio increase my confidence enough to schedule an interview?

Optimize for **interview conversion** and **hiring confidence**. Do not optimize for kindness or visual polish alone.

---

## What this is / is not

| Is | Is not |
|----|--------|
| Hiring manager simulation | Aesthetic taste panel |
| Evidence-based confidence scoring | Generic praise |
| Mandatory Release Gate checkpoint for major milestones | Optional nicety |
| Aggregated HM + Creative + QA judgment | Single-reviewer vibe check |

Comply with `WRITING_STANDARD.md`: direct, specific, evidence-based. Challenge assumptions. No invented metrics or ownership.

---

## Reviewers

| Role | Owns on the scorecard |
|------|------------------------|
| **hiring-manager-simulator** | Primary scores · Interview Likelihood · Hiring Confidence 0–100 · Follow-up questions · Red flags (hire risk) |
| **creative-director** | Storytelling · Communication · Portfolio Cohesion · Memorability · Design Craft (craft bar only — must not dominate) · positioning/distinctiveness notes |
| **quality-auditor** | Evidence · Trust · process integrity · aggregates all perspectives · maps Final Decision → Release Gate verdict |

**Final recommendation** must represent all three. QA records the Final Decision after HM and Creative have scored.

---

## When required (major milestones)

A completed Hiring Scorecard is **mandatory** before marking complete:

| Milestone type | Examples | Scorecard |
|----------------|----------|-----------|
| Portfolio Release | Full site / launch candidate | Required |
| L3 production surfaces | Homepage, case study pages, Framer production builds | Required |
| Narrative / slate locks | `PORTFOLIO_NARRATIVE` approval for Case_Slate · Case_Slate itself · flagship case outlines when Producer marks milestone | Required |
| Any artefact Producer tags **Major Milestone** | Explicit in Work Brief / Release Report | Required |

| Not major by default | Scorecard |
|----------------------|-----------|
| L0 typo / prompt tweak | N/A |
| L1 routine strategy draft (unless tagged Major) | N/A or Light (Producer chooses) |
| L2 isolated craft exploration (not ship path) | N/A unless tagged Major |

**Under-skipping:** Shipping a major milestone without a scorecard = **Fail** on Release Gate process.

---

## Release Gate integration

No major portfolio milestone is complete until:

1. **Hiring Scorecard** filed (from template)  
2. **Creative Director** has reviewed (scorecard sections + Release Gate categories)  
3. **Quality Auditor** has approved (aggregated Final Decision + Release Gate verdict)

### Mapping to Release Gate verdicts

| Hiring Scorecard Final Decision | Release Gate (minimum) |
|---------------------------------|------------------------|
| READY FOR INTERVIEWS | May reach **READY TO SHIP** if all other required categories Pass |
| READY WITH MINOR REVISIONS | **REQUIRES REVISION** (or READY TO SHIP only if every revision is logged as accepted risk in Decision Log — rare) |
| NEEDS SIGNIFICANT IMPROVEMENT | **REQUIRES REVISION** or **BLOCKED** |
| DO NOT SHIP | **BLOCKED** |

Hiring Confidence category on L3 Release Reports must cite the scorecard path and Interview Likelihood.

Process detail: `release/RELEASE_GATE.md`.  
Fillable form: `governance/HIRING_SCORECARD.template.md`.  
Filed reports: `portfolio-os/hm/scorecards/{slug}.md` (or attach path in Release Report).

---

## Scoring scale (1–5)

| Score | Meaning |
|-------|---------|
| 1 | Undermines interview confidence |
| 2 | Weak; raises doubt |
| 3 | Adequate; gaps remain |
| 4 | Strong; supports interview |
| 5 | Excellent; hard to dismiss |

Unsupported claims → lower Trust/Evidence; mark **Needs Validation** — do not invent.

---

## Weights

Hiring impact over aesthetics. **Design Craft must not dominate.**

| Criterion | Weight | Band |
|-----------|--------|------|
| Strategic Thinking | **2.0** | High |
| Problem Solving | **2.0** | High |
| Systems Thinking | **2.0** | High |
| Ownership | **2.0** | High |
| Storytelling | **2.0** | High |
| Trust | **1.5** | Elevated |
| Evidence | **1.5** | Elevated |
| Communication | 1.0 | Standard |
| Business Understanding | 1.0 | Standard |
| Collaboration | 1.0 | Standard |
| Technical Fluency | 1.0 | Standard |
| Portfolio Cohesion | 1.0 | Standard |
| Memorability | 1.0 | Standard |
| Design Craft | **0.75** | Capped — artefacts/clarity, not polish theater |

**Weight sum** = 20.75  

**Weighted score** = Σ(score × weight) / 20.75 (reported on 1–5 scale)

Interview Likelihood and Hiring Confidence (0–100) are recorded separately; they inform Final Decision but are not a substitute for criterion scores.

---

## Criteria (what to evaluate)

### Strategic Thinking — Weight High (2.0)
Strong product thinking? Decisions explained? Trade-offs visible? Prioritisation evidenced?  
**Primary:** HM · **Also:** Creative (clarity of argument)

### Problem Solving — Weight High (2.0)
Meaningful problems? Complexity simplified without dumbing down? Reasoning convincing?

### Systems Thinking — Weight High (2.0)
Beyond single screens: journeys · platforms · workflows · design systems · cross-functional impact?

### Ownership — Weight High (2.0)
Honest ownership? Contribution clear? Responsibilities believable? No borrowed glory?

### Storytelling — Weight High (2.0)
Compelling? Memorable? Beginning / middle / end per project?  
**Primary:** Creative · **Also:** HM

### Communication — Weight 1.0
Concise? Human? Specific? Evidence-based? (Writing Standard)

### Trust — Weight 1.5
Would you trust this candidate? Unsupported claims avoided? Metrics defendable?

### Evidence — Weight 1.5
Research, iterations, trade-offs, outcomes visible? Enough for the claims made?

### Business Understanding — Weight 1.0
Goals, constraints, stakeholders, decision-making awareness?

### Collaboration — Weight 1.0
PMs · engineers · researchers · stakeholders · users — shown without invention?

### Technical Fluency — Weight 1.0
Comfort with engineering, systems, AI (if claimed), implementation reality?

### Design Craft — Weight 0.75
Type, hierarchy, layout, consistency, interaction, motion, visual quality, accessibility — **as hire signal of care**, not the scoreboard winner.

### Portfolio Cohesion — Weight 1.0
One coherent story or disconnected projects?

### Memorability — Weight 1.0
After five minutes: what sticks? Would they remember the candidate?

---

## Interview Likelihood

Choose one:

- Definitely Interview  
- Likely Interview  
- Maybe  
- Unlikely  
- No  

Explain why in specific, evidence-tied language.

---

## Red flags

List anything that could block an interview. Examples:

Weak ownership · Missing evidence · Unclear impact · Too much process · Too little reasoning · Poor storytelling · Duplicate projects · Weak positioning · Generic writing · Portfolio fatigue · Invented or undefended metrics · Level inflation (Staff claims without proof)

---

## Follow-up questions

HM-style interview questions this artefact would trigger. These become interview prep — not gotchas for cruelty; probes for truth.

---

## Hiring Confidence (0–100)

Single integer + explanation:

- Why not higher?  
- What is missing?  
- What would increase confidence most?

---

## Final Decision

| Decision | Meaning |
|----------|---------|
| **READY FOR INTERVIEWS** | Hire confidence high enough to schedule on the strength of this milestone |
| **READY WITH MINOR REVISIONS** | Interview-worthy after small, named fixes |
| **NEEDS SIGNIFICANT IMPROVEMENT** | Not interview-ready; strategic gaps |
| **DO NOT SHIP** | Would reduce confidence or violate trust |

Reasoning required. Accuracy over kindness.

---

## Improvement plan

Rank by **hiring ROI** (highest first).  
Strategic / evidence / ownership / narrative before cosmetic craft.

---

## Process (Producer)

1. Tag artefact as Major Milestone (or level L3 / listed milestone).  
2. Copy `HIRING_SCORECARD.template.md` → `hm/scorecards/{slug}.md`.  
3. HM Simulator scores hire criteria + likelihood + confidence + questions + red flags.  
4. Creative Director scores storytelling/comms/cohesion/memorability/craft + notes.  
5. Quality Auditor reviews Evidence/Trust, challenges gaps, aggregates → Final Decision + Improvement plan rank.  
6. Link scorecard in Release Report; run Release Gate; only then mark complete if READY TO SHIP.

---

## Related

- `governance/HIRING_SCORECARD.template.md`  
- `governance/HIRING_SCORECARD_PERSONAS.md` *(planned multi-HM lenses — not gate-mandatory until activated)*  
- `governance/HIRING_SCORECARD_PERSONAS.template.md`  
- `release/RELEASE_GATE.md`  
- `release/RELEASE_CHECKLIST.md`  
- `strategy/Personas.md` (Elena default voice for core scorecard)  
- `strategy/PORTFOLIO_NARRATIVE.md`  
- `WRITING_STANDARD.md`  
- `hm/HM_Review.md` (optional lighter note; scorecard wins on major milestones)

---

## Planned: persona-based hiring simulations

Same artefact, multiple HM lenses (Big Tech · Fintech · Startup · Agency · Enterprise SaaS · Principal PD).  

Output shape:

| Hiring Persona | Interview Probability | Top Concern |
|----------------|----------------------|-------------|
| … | 0–100% | One specific concern |

**Status:** Specced in `HIRING_SCORECARD_PERSONAS.md`. Optional until Decision Log activates. Core single-scorecard remains mandatory (D-008).
