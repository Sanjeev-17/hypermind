---
# Prompt Guidelines

**Mandatory** structure for every prompt under `prompts/` (body).  
Frontmatter still follows `SPEC.md`. This file defines the **prompt body contract**.

**Owner:** prompt-librarian  
**Compliance:** all new/edited prompts; Librarian rejects non-compliant Active/Gold prompts.

---

## Standard body structure (exact order)

```markdown
# {title}

## Objective
One sentence: what success looks like.

## Context
Only what the model needs; prefer paths over pasted docs.

## Constraints
Hard rules (no invented metrics, no redesign, read-only file list, etc.).

## Inputs
Variables the caller must supply.

## Required Documents
Paths only — subset of memory-index / project docs. Never “all docs”.

## Task
Numbered steps. One job.

## Expected Output
Artefact name/path + format (headings/table).

## Success Criteria
Checklist the output must pass.

## Anti-patterns
What the model must not do.

## Token Budget
- Max context files: N
- Est. input / output tokens (match frontmatter)
- Prefer links over inlining

## Revision History
| Version | Date | Change | Why |
```

Improvement Log remains required per `SPEC.md` (may follow Revision History).

---

## Rules

1. One objective per prompt  
2. Required Documents must be an explicit list  
3. Success Criteria must be testable  
4. Anti-patterns must include “do not load unrelated project files”  
5. Tier (Gold/Silver/Experimental) set in frontmatter `tier` — see SPEC  

---

## Non-compliance

Missing sections → stay `draft` / Experimental.  
Librarian will not promote to Silver/Gold until compliant.
