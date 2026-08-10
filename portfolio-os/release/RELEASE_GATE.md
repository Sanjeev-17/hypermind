---
# Release Gate

**Status:** Permanent Portfolio OS governance  
**Owner:** portfolio-producer (process) · quality-auditor (verdict for L2–L3)  
**Applies to:** Every artefact before it is marked complete or shipped

No artefact is **complete** until it passes this gate at the correct **release level**.

---

## Release levels

Not everything needs the same scrutiny. Producer assigns the level; under-leveling is a Fail on process.

| Level | What | Required reviewers | Typical artefacts |
|-------|------|--------------------|-------------------|
| **L0** | Prompt tweaks, typo fixes, trivial doc hygiene | portfolio-producer | Prompt wording patches, spelling, broken links in docs |
| **L1** | Strategy / planning documents | portfolio-producer + creative-director | Product Brief, Personas, IA, Conversion Spec, inventory/evaluation docs |
| **L2** | Design work | creative-director + quality-auditor | Wireframes, visual system, motion direction, interaction specs, systems tokens |
| **L3** | Production portfolio pages / launch | creative-director + quality-auditor + hiring-manager-simulator + **Hiring Scorecard** | Homepage, case study pages, Framer builds, full Portfolio Release |

### Level rules

- Producer may raise the level; may not lower below the table without a Decision Log entry.
- L0: Producer scores applicable categories lightly; Writing Standard still applies to any text change.
- L1+: Creative Director scores Storytelling / Writing (and Visual/Motion when present).
- L2+: Quality Auditor owns final verdict aggregation.
- L3: HM Simulator **must** complete **Hiring Scorecard** (`governance/HIRING_SCORECARD.md`) before verdict; Hiring Confidence category cites scorecard.
- **Major milestones** (Portfolio Release, L3 surfaces, narrative/slate locks, or Producer-tagged): incomplete until Hiring Scorecard + Creative review + QA approval — see D-008.
- Portfolio Release is always **L3**.

---

## Verdicts (final)

| Verdict | Meaning |
|---------|---------|
| **READY TO SHIP** | All required categories Pass (or accepted risk logged in Decision Log) |
| **REQUIRES REVISION** | One or more Needs Revision; not complete |
| **BLOCKED** | One or more Fail; must not ship or mark complete |

---

## Category scores

For each applicable category:

| Field | Values |
|-------|--------|
| Status | `Pass` · `Needs Revision` · `Fail` |
| Score | 1–5 (5 = excellent for this artefact’s job) |
| Reviewer notes | Short, specific, human (see WRITING_STANDARD) |

Skip categories that do not apply (mark `N/A` — not a Fail).

### Categories by level (minimum)

| Category | L0 | L1 | L2 | L3 |
|----------|----|----|----|-----|
| Strategy | N/A* | Required | Required | Required |
| Storytelling | N/A* | Required | If narrative | Required |
| Visual Design | N/A | N/A | Required | Required |
| Motion | N/A | N/A | If motion in scope | If motion in scope |
| Accessibility | N/A | N/A | If interactive prototype | Required if built |
| Performance | N/A | N/A | If heavy media | Required if built |
| Hiring Confidence | N/A | Light | Light | **Required** (HM Scorecard) |
| Documentation | Light | Required | Required | Required |
| Constitution | N/A | If exists | If exists | Required |
| Writing Standard | If text | Required | If text | Required |
| Prompt Standard | If prompt | If prompt | If prompt | If prompt |
| Memory Updates | If new/renamed doc | Required | Required | Required |
| Decision Log | If material decision | If material | If material | Required for release |

\*L0 typo-only: Writing Standard spot-check if prose changed; otherwise Documentation + Prompt Standard as relevant.

---

## Categories (detail)

| Category | Primary reviewer | What “Pass” means |
|----------|------------------|-------------------|
| Strategy | portfolio-producer (+ architect artefacts) | Aligns with Product Brief / hiring goal |
| Storytelling | creative-director | Decisions clear; no empty narrative |
| Visual Design | creative-director | Craft bar met; not generic template |
| Motion | creative-director (+ motion artefacts) | Direction intentional; not decoration |
| Accessibility | quality-auditor (uses a11y audit if build) | No critical access blockers for scope |
| Performance | quality-auditor (uses perf audit if build) | No critical perf blockers for scope |
| Hiring Confidence | hiring-manager-simulator (+ Creative/QA on scorecard) | Increases interview confidence; **major milestones require filed Hiring Scorecard** |
| Documentation | portfolio-producer | Required docs exist and are current |
| Portfolio Constitution Compliance | quality-auditor | No constitution breaches |
| Writing Standard Compliance | creative-director / editorial when text | Passes reading test; no banned AI fluff |
| Prompt Standard Compliance | portfolio-producer | No Experimental in production |
| Memory Updates | portfolio-producer | memory-index accurate |
| Decision Log Updates | portfolio-producer | Material decisions logged |

---

## Artefact → default level

| Artefact | Default level |
|----------|---------------|
| Prompt tweak / typo | L0 |
| Product Brief, Personas, IA, inventory, evaluation, conversion | L1 |
| Visual / motion / interaction / systems / wireframes | L2 |
| Homepage, case pages, Framer build, Portfolio Release | L3 |
| PORTFOLIO_NARRATIVE / Case_Slate (major lock) | L1 + **Hiring Scorecard** required |
| Documentation-only (non-strategy) | L0 or L1 (Producer chooses; strategy docs = L1) |

---

## Process

1. Producer assigns **level** + opens report from `RELEASE_REPORT.template.md`.
2. If **major milestone** or **L3**: open Hiring Scorecard from `governance/HIRING_SCORECARD.template.md` → file under `hm/scorecards/`.
3. Fill checklist (`RELEASE_CHECKLIST.md`) for applicable rows.
4. Required reviewers score their categories.
5. **Hiring Scorecard:** HM → Creative → QA aggregate (Final Decision). Required before complete on major milestones / L3.
6. **L0–L1:** Producer records verdict (Creative must have scored on L1; Scorecard if major).  
   **L2–L3:** quality-auditor aggregates → final verdict.
7. Map Scorecard Final Decision → Release verdict (see `HIRING_SCORECARD.md`).
8. Only **READY TO SHIP** may mark the artefact complete.

Accepted risks: Decision Log entry required; cannot override **Fail** on Constitution, invented metrics, critical A11y, or **missing Hiring Scorecard on a major milestone** without remediation.

---

## Related

- `RELEASE_CHECKLIST.md`
- `RELEASE_REPORT.template.md`
- `governance/HIRING_SCORECARD.md`
- `governance/HIRING_SCORECARD.template.md`
- `WRITING_STANDARD.md`
- `governance/Decision_Log.md`
