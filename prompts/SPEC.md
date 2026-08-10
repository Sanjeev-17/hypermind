---
# Prompt Library — Specification

Canonical rules for every prompt in `prompts/`.  
Body structure must also follow `PROMPT_GUIDELINES.md`.

---

## 0. Tiers (classification)

| Tier | Badge | Meaning | Production use |
|------|-------|---------|----------------|
| **Gold** | ⭐ | Battle-tested; preferred default | Always preferred |
| **Silver** | 🥈 | Stable; still evolving | Allowed |
| **Experimental** | 🧪 | Research/testing only | **Never** for production |

Frontmatter field: `tier: gold|silver|experimental`

### Promotion criteria

| From → To | Criteria |
|-----------|----------|
| Experimental → Silver | SPEC + PROMPT_GUIDELINES complete; ≥1 real use with Improvement Log; overall quality ≥ 3.5; no critical failures; Librarian approve |
| Silver → Gold | ≥3 successful production uses (or 2 + strong evidence); overall ≥ 4; token estimates accurate within ~20%; no open critical limitations; INDEX marks Gold; Librarian approve |
| Any → Experimental | Major rewrite untested; or demotion after repeated failures |
| Any → Deprecated | Obsolete; move to `archive/`; INDEX points to successor |

Producer **must** prefer Gold over Silver when both match the goal. Never route Experimental for Launch/QA production work.

---

## 1. Metadata (required frontmatter + body)

Use YAML frontmatter, then body sections per `PROMPT_GUIDELINES.md`.

```yaml
---
title: ""
purpose: ""
category: strategy|research|storytelling|ux|visual-design|motion|framer|frontend|accessibility|performance|review|critique|hiring|experiments
owner: ""
version: "1.0.0"
status: draft|active|deprecated
tier: experimental|silver|gold
best_models: []
difficulty: low|medium|high
project_stages: []
est_input_tokens: 0
est_output_tokens: 0
recommended_context_files: []
dependencies: []
related_documents: []
quality_score:
  clarity: 0
  specificity: 0
  token_efficiency: 0
  output_quality: 0
  consistency: 0
  reusability: 0
  maintainability: 0
  overall: 0
---
```

### Body

Follow **PROMPT_GUIDELINES.md** section order exactly, plus:

```markdown
## Improvement Log
### YYYY-MM-DD — use / test
- Worked:
- Failed:
- Hallucinations:
- Missing context:
- Better wording:
- Token savings:
- Model notes:
- Recommended improvements:
```

---

## 2. Lifecycle

```
Draft → Internal Testing → Approved → Production
         ↑_________________|          |
                Improved ←────────────┘
                     |
              Version Update (semver)
                     |
                Deprecated → archive/
```

| Stage | Meaning | Gate |
|-------|---------|------|
| Draft | Authoring | Metadata + guidelines structure |
| Internal Testing | Run ≥1 real task | Improvement log started; tier Experimental |
| Approved | Librarian sign-off | Quality overall ≥ 3.5; INDEX updated; tier ≥ Silver |
| Production | Default routing | `status: active`; prefer Gold |
| Improved | Post-use learnings | Patch/minor bump |
| Version Update | Breaking or feature change | Semver + history |
| Deprecated | Do not use | `archive/` + INDEX stub |

---

## 3. Versioning (semver)

| Bump | When |
|------|------|
| MAJOR | Breaking job / incompatible I/O |
| MINOR | New capability; compatible |
| PATCH | Clarity, tokens, wording fixes |

---

## 4. Quality score (1–5)

| Dimension | 5 means |
|-----------|---------|
| Clarity | Unambiguous |
| Specificity | Concrete I/O |
| Token Efficiency | Minimal context |
| Output Quality | Usable artefacts |
| Consistency | Stable structure |
| Reusability | Portable across projects |
| Maintainability | Easy to diff/version |
| Overall | Librarian aggregate |

Gold target: **overall ≥ 4**.

---

## 5. Improvement workflow

1. Use on real task  
2. Fill Improvement Log  
3. Patch → semver  
4. Re-score; consider tier promotion  
5. Update INDEX  

---

## 6. Review workflow (Prompt Librarian)

1. Dedupe vs INDEX  
2. SPEC + PROMPT_GUIDELINES compliance  
3. Cut tokens; validate context files vs memory-index  
4. Tier promotion/demotion  
5. Archive obsolete  

---

## 7. Token rules

- Declare est tokens + recommended_context_files  
- Ban “entire project” context  
- One primary output artefact  
- Align with Producer read-only lists  
