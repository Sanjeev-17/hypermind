---
# Hiring Scorecard — Persona Simulations

**Status:** Planned (not mandatory for Release Gate v1.0.6)  
**Owner:** hiring-manager-simulator · portfolio-architect (persona definitions) · quality-auditor (aggregation)  
**Parent:** `governance/HIRING_SCORECARD.md` (D-008)  
**Activate via:** Decision Log + version bump when first used on a milestone  

**Purpose:** Review the **same** portfolio artefact through different hiring-manager lenses.  
One generic score is not enough for a multi-cluster target list (Product Brief).

Default v1 scorecard still uses a single HM voice (Elena / general Senior PD HM).  
Persona simulations are **additive** — they do not replace the core weighted scorecard.

---

## When to run (later)

| Trigger | Action |
|---------|--------|
| Portfolio Release / L3 major milestone | Optional now · **Recommended** once activated |
| Targeting a company cluster heavily (fintech, big tech, startup) | Run matching persona + baseline |
| Case_Slate tradeoffs (which proof to emphasize) | Run 2–3 personas; compare Top Concerns |

Not required for L0–L1 routine docs unless Producer tags Major + Persona Pass.

---

## Hiring personas (closed set v1)

| ID | Hiring persona | Looks for (overweight) | Underweights / risks |
|----|----------------|------------------------|----------------------|
| HP-BT | **Big Tech Hiring Manager** (Google, Microsoft, Meta-class) | Ambiguity, systems, rigor, evidenced metrics, consistency, leveling clarity | Pure delight; thin ownership; hype |
| HP-FT | **Fintech Hiring Manager** (Mastercard, Stripe, Visa-class) | Trust, risk, complexity, business consequences, metric literacy, constraint honesty | Moodboards; unverified %; consumer-only slate |
| HP-SU | **Startup Design Lead** (Series A/B) | Ownership, end-to-end shipping, speed, taste under constraint, agency | Double-diamond ceremony; process theater |
| HP-AG | **Design Agency Creative Director** | Visual exploration, craft altitude, narrative distinctiveness, interaction polish | Enterprise decks without craft; generic templates |
| HP-EN | **Enterprise SaaS Director** | Multi-stakeholder systems, workflows, ops realism, partnership with PM/eng | Portfolio as art gallery; unclear B2B impact |
| HP-PR | **Principal Product Designer** | Authorship, systems depth, defendable craft, “what I’d change”, senior altitude | Hero shots only; borrowed credit; shallow research |

Map loosely to `strategy/Personas.md` audiences (Elena/Jordan/Alex/Amara) but these IDs are **company-cluster HMs**, not the funnel personas.

---

## Output (required table)

For each persona run:

| Hiring Persona | Interview Probability | Top Concern |
|----------------|----------------------|-------------|
| Enterprise SaaS Director | 94% | Wants more fintech depth |
| Big Tech Hiring Manager | 81% | Stronger data-driven metrics needed |
| Design Agency Creative Director | 76% | Wants more visual exploration |
| Startup Design Lead | 90% | Wants faster execution examples |
| Fintech Hiring Manager | — | — |
| Principal Product Designer | — | — |

**Interview Probability:** integer 0–100 (same honesty rules as Hiring Confidence — no inflation).  
**Top Concern:** one specific, evidence-tied sentence (not generic praise).

Optional per persona: Likelihood label (Definitely / Likely / Maybe / Unlikely / No) · Red flag · One follow-up question.

---

## Scoring rules (when activated)

1. Run **core Hiring Scorecard** first (single aggregated score).  
2. Run selected persona lenses (default recommend: all six on Portfolio Release; subset on Case_Slate).  
3. Do **not** average persona % into the core weighted score blindly — report both.  
4. QA may block ship if **target-cluster** persona (from Product Brief focus) is Unlikely/No without Decision Log acceptance.  
5. No invented evidence to please a persona. Gaps stay gaps.  
6. Writing Standard applies to all notes.

### Signal emphasis cheatsheet

| Criterion | BT | FT | SU | AG | EN | PR |
|-----------|----|----|----|----|----|-----|
| Strategic Thinking | ●● | ●● | ●● | ● | ●● | ●● |
| Systems Thinking | ●● | ●● | ● | ○ | ●● | ●● |
| Ownership | ●● | ●● | ●● | ● | ●● | ●● |
| Evidence / Metrics | ●● | ●● | ● | ○ | ●● | ●● |
| Design Craft | ● | ○ | ● | ●● | ○ | ●● |
| Storytelling | ● | ● | ●● | ●● | ● | ● |
| Collaboration | ●● | ●● | ● | ○ | ●● | ● |
| Technical Fluency | ●● | ● | ●● | ○ | ●● | ●● |
| Business Understanding | ● | ●● | ●● | ○ | ●● | ● |

●● = hard gate · ● = expected · ○ = secondary

---

## Template

Fill: `governance/HIRING_SCORECARD_PERSONAS.template.md`  
File with scorecard: `hm/scorecards/{slug}-personas.md`

---

## Activation checklist

- [ ] Decision Log entry (e.g. D-00X Activate persona hiring simulations)  
- [ ] Portfolio OS version bump  
- [ ] Producer updates Release Gate “when required”  
- [ ] First run attached to a real milestone  

Until activated: keep this doc as the contract; core scorecard remains the Release Gate mandatory path.
