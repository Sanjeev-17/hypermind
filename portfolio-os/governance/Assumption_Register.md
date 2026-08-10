---
# Assumption Register

Prevent assumptions from becoming facts. Validate or retire every entry.

**Owner:** portfolio-producer (process) · named Owner per row  
**Authoritative:** yes  
**Path:** `portfolio-os/governance/Assumption_Register.md`

---

## How to use

1. ID: `A-NNN`
2. State the assumption as a falsifiable sentence
3. Set Confidence: `Low` · `Medium` · `High`
4. Status: `Open` · `Validating` · `Validated` · `Invalidated` · `Retired`
5. When resolved, fill Resolution and link evidence / Decision ID

---

## Register

| ID | Statement | Category | Confidence | Evidence | Validation Required | Owner | Status | Resolution |
|----|-----------|----------|------------|----------|---------------------|-------|--------|------------|
| A-001 | Recruiter/sourcer is the first hard gate; HM decides interview | hiring | Medium | Owner strategy intent; common hiring funnel patterns | HM/recruiter tests; analytics later | portfolio-architect | Open | |
| A-002 | Decision-first cases convert better than UI-first for this level | hiring | Medium | Owner: decision-making portfolio thesis | Case experiments; HM simulator | story-strategist | Open | |
| A-003 | Named target companies share overlapping proof needs | market | Medium | Owner target list diversity | Map proof needs per cluster in slate | portfolio-architect | Open | |
| A-004 | Senior PD is the v1 conversion goal; Staff is optional stretch | hiring | High | Product Brief v0.2 | Revisit after Case_Slate scoring | portfolio-architect | Open | |
| A-005 | Owner can supply ≥2–3 publicly showable cases with real decisions | content | Medium | Discovery v0.1: 4 candidate rows (2 Medium); Mastercard pending; resume unread | Owner answers Discovery Report Qs; promote/clear pending | portfolio-architect | Validating | |
| A-006 | Contact mechanism matters less than proof quality for v1 | process | Medium | Conversion thesis | CTA test post-MVP | portfolio-architect | Open | |

### Categories

`audience` · `market` · `content` · `craft` · `technical` · `process` · `hiring`

---

## Detail (optional for complex items)

<!--
### A-001
**Statement:** …
**Evidence:** …
**Validation Required:** …
**Resolution:** … (link D-xxx / doc / experiment E-xxx)
-->
