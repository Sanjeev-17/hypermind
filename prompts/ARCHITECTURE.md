---
# Prompt Library — Architecture

Reusable prompt IP for this portfolio and future design projects.

Prompts are versioned artefacts — not chat one-offs.

## Location

```
prompts/
  ARCHITECTURE.md      ← this file
  SPEC.md              ← metadata, lifecycle, versioning, quality, improvement
  INDEX.md             ← searchable catalog
  _templates/          ← starter shells by prompt type
  strategy/ | research/ | storytelling/ | ux/ | visual-design/
  motion/ | framer/ | frontend/ | accessibility/ | performance/
  review/ | critique/ | hiring/ | experiments/ | archive/
```

## Integration with Portfolio OS

| Concern | Owner |
|---------|--------|
| When to use a prompt | `prompts/INDEX.md` + task stage |
| Which project docs to attach | `portfolio-os/memory-index.md` (context files) + prompt’s Recommended Context Files |
| Who maintains prompts | **prompt-librarian** skill |
| Who routes work | **portfolio-producer** (may invoke librarian or a specialist with a named prompt) |

Producer rule: prefer an **Active** prompt path over inventing a new prompt in-thread.

## Principles

1. One prompt = one job
2. Metadata required — no bare text blobs
3. Body follows `PROMPT_GUIDELINES.md`
4. Tiers: Gold ⭐ · Silver 🥈 · Experimental 🧪 (see SPEC)
5. Semantic versioning on every change
6. Improve after every use
7. Token-cheap: declare context files; never “read the whole repo”
8. Archive, don’t delete

## Prompt file convention

```
prompts/{category}/{slug}.md
```

Example: `prompts/motion/scroll-storytelling-v1.md` (slug stable; version inside frontmatter)

## Status vs lifecycle

| Status field | Lifecycle stage |
|--------------|-----------------|
| Draft | Draft → Internal Testing |
| Active | Approved → Production → Improved (still Active) |
| Deprecated | Deprecated (file moved to `archive/` or marked in place) |

## Indexing strategy

- Every Active/Draft prompt listed in `INDEX.md`
- Filter columns: Goal, Category, Project Stage, Model, Difficulty, Est. Tokens, Dependencies
- Librarian updates INDEX on approve / deprecate / major version

## Optimisation strategy

- Require Estimated Input/Output Tokens + Recommended Context Files on every prompt
- Librarian rejects prompts that say “use all project context”
- After each use: log token waste in improvement notes; ship a patch version when savings are clear
- Prefer linking `portfolio-os/…` paths over inlining docs

## Related OS docs

- `portfolio-os/memory-index.md` — which product docs to load
- `.cursor/skills/prompt-librarian/SKILL.md` — maintenance role
- `.cursor/skills/portfolio-producer/SKILL.md` — routing
