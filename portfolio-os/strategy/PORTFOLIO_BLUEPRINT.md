---
# Portfolio Blueprint

**Status:** Draft v0.1 — authoritative for capability + slate  
**Owner:** portfolio-architect · story-strategist  
**Replaces:** `CAPABILITY_MATRIX.md` · `CASE_SLATE.md` (see pointers there)  

**Upstream:** `WRITING_STANDARD.md` · `Product_Brief.md` · `Personas.md` · `PROJECT_EVALUATION.md` · `PORTFOLIO_NARRATIVE.md` · `HIRING_SCORECARD.md`  

**Purpose:** What the portfolio must prove, which projects prove it, and why — before Information Architecture.

---

# 1. Capability Matrix

Importance: **Critical** · **High** · **Medium** · **Deferred**  
Evidence: **Strong** · **Adequate** · **Thin** · **None** · **Needs Validation**

| Capability | Importance | Evidence Strength | Supporting Project(s) | Confidence | Missing Evidence |
|------------|------------|-------------------|----------------------|------------|------------------|
| Decision quality | Critical | Thin → Adequate potential | P-005 (primary), P-006, P-001 | Medium | Option → choice → tradeoff per case |
| Ownership clarity | Critical | Adequate | P-001, P-005, P-006 | High | Team boundaries beyond Lead / Led |
| Systems thinking | Critical | Strong (P-006) / Adequate (P-005) | P-006 (primary), P-005 | High | Governance / brand-conflict tradeoffs |
| Clarity / communication | Critical | Thin until cases outlined | All slate cases + site voice | Medium | Forwardable one-liners; 30s parse |
| Partnership (PM / eng / ops) | High | Adequate lists; depth Needs Validation | P-005, P-006 | Medium | Named partners; P-001 cross-func |
| Research literacy | High | Adequate (P-005) | P-005 (primary), P-001 | Medium | Method → insight artefacts |
| Enterprise / ops complexity | High | Adequate | P-005, P-006 | High | — |
| Consumer / marketplace narrative | High | Adequate story; impact Needs Validation | P-001 | Medium | Metric consistency; partners |
| Honest impact / outcomes | High | Thin (CMS unvalidated) | P-001, P-005, P-006 | Low–Medium | Owner-validated metrics |
| Leadership (influence) | Medium | Thin (title-level) | P-006, P-005 | Medium | Facilitation beyond title |
| Interaction design depth | Medium | Thin | P-001, P-005 | Low | States / flows called out |
| Visual craft (care signal) | Medium | Adequate artefacts | All Framer cases | Medium | — (must not dominate hire score) |
| Accessibility | Medium | Thin (named in P-006 CMS) | P-006 | Low | Concrete a11y decisions / outcomes |
| Fintech / trust / payments | Deferred | None | PD-MC-* | High (gap) | Mastercard documentation |
| AI product design | Deferred | None | — | High (gap) | Verified AI case |
| Staff-default leveling | Deferred | None | — | High | — (Senior only v1) |
| Data-heavy workflows | Medium | Thin | P-005 (partial) | Low | Logs/support → decision proof |

### Capability gaps
Fintech/payments · AI · validated metrics · recorded decision maps · Staff stretch · deep interaction/state craft · accessibility as proven practice

### Duplicated capabilities
| Overlap | Projects | Keep distinct by |
|---------|----------|------------------|
| Enterprise cruise domain | P-005 + P-006 | Journey/ops decisions vs multi-brand system |
| Lead / Led ownership | All three | Different problem types |
| Unvalidated CMS outcomes | All three | Same trust rule: validate or soften |

### Weak evidence
Decision tradeoffs (all) · Metrics as fact · P-001 cross-functional · Leadership beyond title · Accessibility depth · Interaction depth

### Overrepresented
Enterprise / cruise-adjacent (2 of 3) · Lead title signal on every case

### Underrepresented
Fintech · AI · validated business impact · startup speed beyond older P-001

---

# 2. Portfolio Blueprint

**Logic reused:** Evaluation scores P-006 > P-005 > P-001 · Narrative jobs S2 / S1 / S3 · Hiring Scorecard prioritises systems, ownership, decisions, evidence over craft · smallest set that covers Critical capabilities.

**Cruise overlap:** Keep **separate** — do not merge into one flagship narrative.  
- P-006 = systems / multi-brand  
- P-005 = journey / ops / research  
If forced to one cruise flagship → **P-006**. Do not ship both if they read as the same story.

**Mastercard:** Pending Documentation until evidence exists. Not on active slate.

## Selected projects

### P-006 — Uni design system

| Field | Value |
|-------|-------|
| Purpose | Prove systems thinking and current Senior capability |
| Hiring signal | Systems / platform craft under multi-brand constraint |
| Capability coverage | Systems · partnership · enterprise · leadership (alignment) · a11y mention |
| Narrative role | S2 — Systems that scale craft |
| Evidence strength | Strong on scope; metrics & decisions Needs Validation |
| Confidence | High (role) · Medium (impact claims) |
| Recommended depth | **Flagship** |

### P-005 — Online check-in

| Field | Value |
|-------|-------|
| Purpose | Prove decision quality under ops complexity + research |
| Hiring signal | Judgment + research + stakeholder/ops partnership |
| Capability coverage | Decision quality · research · partnership · enterprise/ops |
| Narrative role | S1 — Enterprise under constraint |
| Evidence strength | Adequate–Strong on methods/collab lists; metrics & tradeoffs Needs Validation |
| Confidence | Medium-High |
| Recommended depth | **Major Case Study** |

### P-001 — Taco Bell delivery

| Field | Value |
|-------|-------|
| Purpose | Consumer range + ownership under urgency |
| Hiring signal | End-to-end ownership; clear consumer story |
| Capability coverage | Ownership · consumer narrative · story clarity |
| Narrative role | S3 — Consumer urgency |
| Evidence strength | Adequate story; metrics Needs Validation; cross-func thin |
| Confidence | Medium-High |
| Recommended depth | **Supporting Case** |

## Depth map

| ID | Depth |
|----|-------|
| P-006 | Flagship |
| P-005 | Major Case Study |
| P-001 | Supporting Case |
| PD-MC-* | Future Candidate (Pending Documentation) |
| P-002 / P-003 / P-004 | Excluded (not verified) |

No Playground / Selected Work required for v1 minimum — three cases beat shallow extras.

**Shareable best-work default:** P-006 (P-005 if cluster is research/ops-first).

**Public metrics:** qualitative or omit until validated.

---

# 3. Interview Coverage

Experienced HM probes the portfolio should prepare for. Map = best project → evidence → confidence.

| Question | Best Project | Supporting Evidence | Confidence |
|----------|--------------|---------------------|------------|
| Tell me about ambiguity | P-005 | Check-in platform stakes; research list (interviews, logs, support) | Medium — tradeoff story Needs Validation |
| Tell me about systems thinking | P-006 | Multi-brand design system across booking journey | High on scope; Medium on governance tradeoffs |
| Tell me about stakeholder management | P-005 | Ops/stakeholders/rollout + Design QA in CMS responsibilities | Medium |
| Tell me about working with engineering / product | P-006 | Design ops workshops with product & dev; QA support | Medium |
| Tell me about ownership | P-001 or P-006 | Lead UI/UX + Led (all); consumer 0→1 story on P-001 | High on label; Medium on team boundaries |
| Tell me about research | P-005 | Explicit methods in CMS | Medium — insight artefacts Needed |
| Tell me about enterprise products | P-005 / P-006 | Cruise enterprise ops + system | High |
| Tell me about consumer products | P-001 | First delivery app narrative | Medium–High (age + metrics caveats) |
| Tell me about business / user impact | P-005 or P-006 | CMS outcome language | **Low** until metrics validated |
| Tell me about accessibility | P-006 | WCAG 2.1 named in responsibilities | **Low** — shallow until decisions shown |
| Tell me about prioritisation / tradeoffs | P-005 or P-006 | Case bodies exist | **Low–Medium** — needs recorded decision maps |
| Tell me about AI | — | None in verified slate | **Unanswered** |
| Tell me about fintech / payments / trust | PD-MC-* | Pending Documentation | **Unanswered** |
| Tell me about design leadership (people lead) | — | Non-goal v1; title-level only | **Intentionally thin** |
| Why should we interview you at Senior? | P-006 + P-005 + Narrative | Systems + decisions + ownership + clarity stake | Medium — rises when tradeoffs/metrics honest |

### Unanswered (honest)
AI · Fintech/payments · Staff-level proof · Strong validated impact · Deep a11y case · Deep interaction-state walkthrough

---

# 4. Portfolio Coverage

| Area | Coverage | Weakness |
|------|----------|----------|
| Enterprise | Strong (P-005, P-006) | Domain concentration (cruise family) |
| Consumer | Present (P-001) | Older; metrics fragile |
| AI | None | Gap vs some targets |
| Research | Strongest on P-005 | Not proven as artefacts yet |
| Systems | Strong (P-006) | — |
| Accessibility | Mention only | Gap |
| Leadership | Title / workshops | Influence stories thin |
| Business impact | CMS claims | Unvalidated — trust risk |
| Storytelling | Strong potential | Depends on decision beats |
| Interaction design | Implied | Thin explicit proof |
| Visual design | Artefacts available | Must not be the hire thesis |
| Cross-functional collaboration | P-005, P-006 lists | P-001 weak; names missing |

### Future additions (priority)
1. Mastercard (or other fintech) once documented — unlocks S5 / trust cluster  
2. One validated metric set per live case (or permanent qualitative policy)  
3. Decision maps for flagship + major  
4. Optional AI case only with real ownership/clearance  
5. Accessibility decision evidence inside P-006 (or dedicated note)

---

# 5. Final Recommendations

1. **Ship minimum slate:** Flagship P-006 · Major P-005 · Supporting P-001.  
2. **Keep cruise cases separate** with hard narrative jobs; merge only if framing fails.  
3. **Do not claim** fintech, AI, Staff-default, or quantified impact brand in v1.  
4. **Before L3 / Hiring Scorecard:** one defendable decision + rejected alternative per case; metric publish policy locked.  
5. **Best link:** P-006 for most targets; P-005 when research/ops is the cluster ask.  
6. Treat this Blueprint as source of truth; do not maintain parallel matrix/slate docs.

---

# 6. Readiness for Information Architecture

| Check | Status |
|-------|--------|
| Capabilities defined | Yes |
| Minimum slate locked | Yes (draft) |
| Narrative roles assigned | Yes |
| Gaps explicit | Yes |
| Interview holes named | Yes |
| Blocking unknowns | Metric policy · decision maps · cruise-dupe framing confirm |

**Ready for Information Architecture:** **Yes** — IA should implement this Blueprint (page jobs, case order, proof hierarchy). Do not invent new projects in IA.

---

## Self-review

- Reuses Evaluation / Narrative / prior matrix+slate conclusions; no rediscovery.  
- Aligns Hiring Scorecard: evidence/trust over polish; unanswered probes listed.  
- Writing Standard: no invented metrics/ownership.  
- Mastercard held.  
- No IA/wireframes in this doc.

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-08-02 | Consolidated capability + slate + interview + coverage into Blueprint |
