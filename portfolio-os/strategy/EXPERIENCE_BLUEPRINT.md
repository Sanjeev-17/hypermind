---
# Experience Blueprint

**Status:** Draft v0.1 — final strategy doc before design  
**Owner:** portfolio-architect (experience/IA) · story-strategist (story) · creative-director (direction later)  
**Replaces:** `INFORMATION_ARCHITECTURE.md` · `DESIGN_LANGUAGE.md`  

**Upstream:** `WRITING_STANDARD.md` · `Product_Brief.md` · `Personas.md` · `PORTFOLIO_NARRATIVE.md` · `PORTFOLIO_BLUEPRINT.md` · `HIRING_SCORECARD.md`  

**Purpose:** How the portfolio should be **experienced** — not how it should look. No wireframes. No UI. No colours/fonts.

**Optimize for:** interview conversion (Product Brief · Hiring Scorecard).

---

# 1. Experience Goals

Ideal recruiter → HM path (Priya then Elena). Sourcer (Marcus) needs the same facts faster.

| Stage | Goal | Experience must deliver |
|-------|------|-------------------------|
| **First Impression** | “Senior PD, worth a look” in ≤15–45s | Role, stake (Problems · Decisions · Clarity), one proof teaser, resume reachable |
| **Trust Building** | Credit and claims feel honest | Explicit ownership (Led); no Staff inflation; metrics only if validated |
| **Curiosity** | Open the flagship | Distinct case jobs (P-006 systems ≠ P-005 journey); problem-led titles |
| **Evidence** | Belief survives skim | Decisions/tradeoffs before galleries; artefacts that explain choices |
| **Confidence** | “I could defend interviewing them” | Range (enterprise + consumer); systems + ownership; partnership signals |
| **Interview Intent** | Next step without hunting | Contact + resume always one action away; stable flagship URL |

**Failure modes to design against:** manifesto home, process theater, metric theater, duplicate cruise memory, motion/password gates before proof.

---

# 2. Information Architecture

## Navigation

| Rule | Detail |
|------|--------|
| Always on | Work, About, Contact/Resume |
| Primary | Work / cases |
| Secondary | About |
| Off critical path | Experiments/blog (must not compete with slate) |
| Never | Password walls; proof locked behind motion |

Labels: plain product language.

## Page hierarchy

```
Home
├── Work index
│   ├── Flagship — P-006 (systems)
│   ├── Major — P-005 (journey/ops/research)
│   └── Supporting — P-001 (consumer ownership)
├── About
└── Contact / Resume
```

## Content hierarchy (all surfaces)

1. Who + Senior PD  
2. Stake  
3. Ownership  
4. Problem / decision hook  
5. Evidence (honest)  
6. Depth  
7. CTA  

## Reading order

**Home:** Who → stake → proof teasers (Blueprint order) → CTA → optional about hint  

**Case:** Stakes → ownership → insight → options → decision → outcome → artefacts → reflection → CTA  

**About:** Scope → how you work → what you don’t claim → contact  

## Recruiter journey

| Step | Need | IA answer |
|------|------|-----------|
| Land | Parse fit | Home facts + resume |
| Forward | One line + best link | Flagship URL; ownership + hook above fold |
| Exit | Progress | Contact/resume always visible |

## Progressive disclosure

| Depth | Audience | Unlocks |
|-------|----------|---------|
| 30s | Recruiter | Identity, stake, proof chips, CTA |
| 5m | HM | Problem, one tradeoff, ownership, honest outcome |
| 20m | HM / peer | Options, artefacts, constraints, reflection, collaboration |

## Decision points

| Point | Visitor question | Route |
|-------|------------------|-------|
| Home | Interview-worthy? | Stake + flagship teaser → Work |
| Work | Which case? | Slate order; distinct jobs in titles |
| Case open | Real ownership? | Role + Led early |
| Mid-case | Clear thinking? | Decision block before gallery dump |
| End | Next step? | Contact / resume |

## Content priorities

| P0 | Role, ownership, stake, decisions, contact/resume |
| P1 | Problem framing, tradeoffs, collaboration |
| P2 | Artefacts, research detail, reflection |
| P3 | Experiments, decoration |

## Page relationships

Home → Flagship (best share) · Home → Work · Work → Cases · Case → sibling cases (range, not twin stories) · Any → Contact/Resume · About → Work  

P-005 vs P-006 must never share the same memory in teasers.

## Trust-building moments

Ownership labels early · Tradeoff visible mid-case · Outcome honesty · No target-company employment implication · Consistent Senior bar  

## Placement

| Type | Where | Avoid |
|------|-------|-------|
| Evidence | Case mid/depth | Homepage metric walls |
| Decisions | Case core beat | Appendix-only |
| Metrics | Outcome; validated only | Hero as brand |
| Story | Case arc; home as hooks | Manifesto home |
| Systems proof | P-006 | Claiming systems everywhere equally |
| Research proof | P-005 | Ceremony without insight |

---

# 3. Story Architecture

| Beat | What | Why it exists |
|------|------|----------------|
| **Portfolio opening** | Senior PD + stake + one proof teaser | Recruiter gate; Narrative core story |
| **Narrative flow** | Problems → Decisions → Clarity, then depth | Decision-making product category |
| **Transitions** | Home teasers → case jobs → sibling links by capability, not employer | Prevent cruise-dupe fatigue |
| **Case study rhythm** | Context → stakes → ownership → insight → options → decision → outcome → artefacts → reflection | Elena/Jordan interview shape; Hiring Scorecard storytelling |
| **Progressive disclosure** | Skim layer then depth | 30s/5m/20m without diluting seniority |
| **Ending** | Reflection + what you’d change | Authenticity; Principal-peer signal without Staff claim |
| **Call to action** | Contact / resume / “start with flagship” | Interview intent |

**Case rhythm rule:** one primary hire signal per case (Blueprint): systems · decisions/research · consumer ownership.

---

# 4. Design Language

Principles only — no colours, fonts, or component specs.

### Writing philosophy
**Purpose:** Defendable, human, scannable copy.  
**Why:** Trust + Writing Standard; Scorecard Communication/Trust.  
**Do:** Short, concrete, active; mark evidence.  
**Don’t:** Banned fluff; unverified % as personality.  
**Anti-pattern:** “Seamless robust journey” with no decision.  
**Success:** Priya pastes one true line; Elena finds a tradeoff in 5m.

### Storytelling philosophy
**Purpose:** Decision-making is the product.  
**Why:** Narrative + Memorability/Cohesion on Scorecard.  
**Do:** Options → decision → tradeoff → honest outcome; one signal per case.  
**Don’t:** Process theater; twin cruise stories.  
**Anti-pattern:** Same arc, different screenshots only.  
**Success:** Memory is *how you decide*, not a colour.

### Visual philosophy
**Purpose:** Craft as care, not the hire thesis.  
**Why:** Scorecard Design Craft weight is capped.  
**Do:** Hierarchy that surfaces proof; artefacts that explain.  
**Don’t:** Template chrome louder than content; spectacle.  
**Anti-pattern:** Award-site energy hiding decisions.  
**Success:** Chrome removed; Senior argument remains.

### Hierarchy philosophy
**Purpose:** 15s parse.  
**Why:** Priya/Marcus gate.  
**Do:** Who → stake → ownership → proof → depth.  
**Don’t:** Long preamble before facts.  
**Anti-pattern:** Competing CTAs and proof chips.  
**Success:** Home works with motion off and images slow.

### Spacing philosophy
**Purpose:** Scan paths; reduce fatigue.  
**Why:** Portfolio fatigue red flag.  
**Do:** Space emphasizes decisions/evidence; consistent rhythm.  
**Don’t:** Empty wallpaper or cramped process walls.  
**Anti-pattern:** New spacing language per case.  
**Success:** Fatigue drops; decisions remain findable.

### Interaction philosophy
**Purpose:** Every interaction reduces load.  
**Why:** Personas; eng/PM realism.  
**Do:** Obvious targets; stable URLs; states that clarify thinking.  
**Don’t:** Hover-only critical facts; novelty that delays proof.  
**Anti-pattern:** Case locked behind animation.  
**Success:** Marcus reaches resume + flagship without help.

### Motion philosophy
**Purpose:** Clarify hierarchy and sequence.  
**Why:** Motion serves hierarchy, not impress.  
**Do:** Sequence argument; respect reduced motion.  
**Don’t:** Intro gates; perpetual decoration.  
**Anti-pattern:** Waiting for readable proof.  
**Success:** Elena never waits for content that should already be there.

### Animation philosophy
**Purpose:** Beat-to-beat transitions only.  
**Why:** Subset of motion discipline.  
**Do:** Purposeful narrative transitions.  
**Don’t:** Showreel loops, scan-breaking parallax.  
**Anti-pattern:** Portfolio as motion demo.  
**Success:** Animation removable without losing meaning.

### Accessibility philosophy
**Purpose:** Reliability + integrity.  
**Why:** Operational design; release trust.  
**Do:** Keyboard, contrast, semantics by default; text alternatives for proof images.  
**Don’t:** A11y as late badge; colour-only status.  
**Anti-pattern:** Beautiful and unusable.  
**Success:** Critical path usable without pointer/colour alone.

### Research philosophy
**Purpose:** Insight that changed a decision.  
**Why:** Secondary memory; anti–process theater.  
**Do:** Method → insight → decision; house primarily in P-005.  
**Don’t:** Double-diamond wallpaper; name-dropping.  
**Anti-pattern:** Research section with no consequence.  
**Success:** HM sees what evidence changed the choice.

### Component philosophy
**Purpose:** Cohesion across the slate.  
**Why:** Scorecard Portfolio Cohesion.  
**Do:** Reuse ownership label, decision block, outcome honesty pattern.  
**Don’t:** New pattern language per case; decorate emptiness.  
**Anti-pattern:** Components as style flex.  
**Success:** Cases feel like one portfolio, three jobs.

---

# 5. Experience Principles

Every future design decision must satisfy these:

1. **Optimize for interview conversion** — not peer applause.  
2. **Reduce cognitive load** — one job per section.  
3. **15-second homepage parse** — role, stake, proof, CTA.  
4. **Ownership made explicit** — Led/scoped; no borrowed glory.  
5. **Decisions over deliverables** — tradeoffs before chrome.  
6. **Evidence before claims** — especially metrics.  
7. **Progressive disclosure** — depth without dilution.  
8. **Reward curiosity** — flagship earns the click; depth pays off.  
9. **Motion should clarify** — never gate proof.  
10. **Every interaction earns its place** — or it goes.  
11. **Simplify before decorating.**  
12. **Remove anything that weakens trust** — hype, invented impact, Staff inflation, logo theater.  
13. **One primary hire signal per case** — systems / journey-research / consumer ownership.  
14. **Two or three deep cases beat seven shallow ones** — Blueprint minimum holds.  
15. **Interview-defendable only** — if you can’t answer it live, don’t publish it as fact.

---

# 6. Creative Direction

No visuals — only the felt experience.

| Dimension | Direction |
|-----------|-----------|
| **Personality** | Experienced Senior IC; inspectable thinker; calm confidence |
| **Tone** | Precise, honest, direct, human (Narrative + Writing Standard) |
| **Pacing** | Fast to proof; slow only where decisions need air |
| **Density** | Lean skim layer; dense only in elected depth |
| **Craftsmanship** | Careful artefacts and hierarchy; craft as signal of rigor |
| **Restraint** | High — decoration loses to clarity; Scorecard craft weight stays low |
| **Emotional response** | “I understand how they think” → “I’d interview them” — not “stunning site” |

**Reference qualities (not copies):** product sites that lead with judgment and constraints (e.g. clarity of Linear/Stripe-class product writing); portfolios that foreground decisions and ownership over galleries. Avoid award-gallery pacing and agency showreel energy as the primary mode.

---

# 7. Release Criteria

A page is **not complete** until it satisfies:

| Gate | Requirement |
|------|-------------|
| Portfolio Narrative | Stake + beliefs intact; no omitted-capability claims (fintech/AI/Staff) |
| Portfolio Blueprint | Case jobs and depths respected; no twin cruise stories |
| Hiring Scorecard | Major/L3: scorecard filed; Interview Likelihood not “No”; Trust/Evidence Pass |
| Writing Standard | Human, evidenced, no banned fluff; no invented metrics |
| Experience Principles | All 15 checked for the page’s job |
| Design Language | Relevant philosophies Pass (esp. writing, hierarchy, motion, trust) |
| Trust Building | Ownership explicit; metrics policy held |
| Interview Readiness | Page supports at least one Blueprint interview probe without collapsing |

Map Scorecard Final Decision → Release Gate per `HIRING_SCORECARD.md`.

---

# Self-review

| Check | Result |
|-------|--------|
| Consistent with Narrative stake | Yes |
| Consistent with Blueprint slate order/jobs | Yes |
| Recruiter-first (Personas) | Yes |
| Scorecard: craft not dominant | Yes |
| Metrics honesty | Yes |
| No wireframes/UI/colours/fonts | Yes |

### Inconsistencies found / corrections

| Issue | Correction applied in this doc |
|-------|--------------------------------|
| Older Narrative still cites `CASE_SLATE.md` | Experience Blueprint depends on `PORTFOLIO_BLUEPRINT.md`; treat Case Slate as superseded |
| Prior IA/Design Language duplication | This file replaces them — edit here only |
| Impact “trust layer” vs recruiter desire for outcomes | Outcomes allowed as qualified/omit until validated; never hero brand |

---

## Strategy complete

Authoritative strategy stack before design:

1. Product Brief · Personas · Narrative  
2. Portfolio Blueprint  
3. **Experience Blueprint (this file)**  
4. Hiring Scorecard (gate on major/L3)

**Next phase (not started here):** Paper wireframes → hi-fi → motion → Framer → QA → launch.

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-08-02 | Consolidated IA + design language + experience goals/principles/direction/release criteria |
