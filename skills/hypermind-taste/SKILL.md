---
name: hypermind-taste
description: "Personal UI taste and design-direction skill for Sanjeev/Hypermind. Use when designing, reviewing, refactoring, theming, or reference-hunting for apps, websites, dashboards, prototypes, landing pages, visual systems, brand surfaces, or generated UI where the output should match Sanjeev's evolving taste: culturally specific, tactile, archival, ornament-aware, editorial, expressive, and usable — and when working on the Framer portfolio ship surface (dark, Inter, lime accent). For Rams/Norman quality and interaction judgment, also load skills/dieter-rams and skills/don-norman."
---

# Hypermind Taste

Use this skill as a taste operator: translate Sanjeev's visual instincts into concrete design choices while preserving usability.

## Two surfaces (do not collapse them)

1. **Baseline taste (aspirational / personal):** culturally specific, archival, ornamental, tactile — see `references/visual-language.md` and the reference PDF.
2. **Framer portfolio ship surface (live product):** dark monochrome + lime accent + Inter + agency-portfolio IA — see `references/framer-portfolio.md`.

Match the surface the user is actually changing. Editing the Framer site ≠ applying the full archival baseline unless they ask for a restyle.

## Core influences (quality & interaction)

Sanjeev is inspired by **Dieter Rams** and **Don Norman**. They sit beside taste, not inside the palette:

- Rams → `skills/dieter-rams` — less but better, honest, useful, thorough
- Norman → `skills/don-norman` — affordances/signifiers, feedback, mapping, gulfs, design for error

Read `references/influences-rams-norman.md` for how the three work together.

## Operating Loop

1. Read the user's task and identify the product context: operational tool, consumer app, editorial page, brand surface, game, prototype, **Framer portfolio**, or review.
2. If the task is about the Framer portfolio site (pages, components, case cards, contact chrome), read `references/framer-portfolio.md` first and treat that file as the active visual contract.
3. Apply the core taste lens below for non-portfolio / experimental / Hypermind brand work, then adapt intensity to the context. A dashboard can carry baseline taste through hierarchy, color, typography, texture, and micro-ornament without becoming a poster.
4. If the task asks whether the design is *good*, honest, overbuilt, or worth shipping, load the **dieter-rams** skill and run its checklist.
5. If the task asks why something is confusing, how to make action obvious, or how to handle errors/feedback, load the **don-norman** skill and walk the gulfs / seven stages.
6. If visual direction is unclear or the user asks for inspiration, read `references/reference-search.md`.
7. If designing UI or reviewing implementation, read `references/ui-translation.md`.
8. If the task asks what the taste is, or a deeper art-direction rationale is useful, read `references/visual-language.md`.
9. If the user gives feedback about what they liked or disliked, update `references/taste-evolution.md` as evidence first. New feedback normally enters as an Observation with confidence and scope; promote it to Pattern only when reinforced, and to Principle only when stable or explicitly confirmed.

## Core Taste Lens

**Baseline:** Favor work that feels collected, made, and lived-in: archival fragments, vernacular print energy, ornamental systems, tactile material, pattern density, patina, confident typography, and saturated accents.

**Framer ship surface:** Favor high-contrast dark fields, large Inter headlines with tight tracking, a single electric lime CTA/status accent, saturated case-stage color blocks behind mockups, and calm nav/footer chrome. Optimize for scan speed and interview conversion, not collage density.

**Rams/Norman overlay:** Keep expression subordinate to usefulness, honesty, discoverability, and feedback. Complexity should reward attention, not block scanning or task completion.

Overall priority: function, then hierarchy, then interaction, then expression.

## Design Heuristics

- Start with structure: strong layout, clear hierarchy, useful interaction states, and readable content.
- On baseline surfaces: add expressive detail through borders, dividers, badges, small panels, background texture, illustration, typographic contrast, and meaningful pattern.
- On the Framer portfolio: keep chrome minimal; put expression in hero type, lime accents, and case mockup stages.
- Use color with confidence. Baseline anchors: oxide red, turmeric yellow, indigo, ultramarine, teal, faded cream, charcoal, occasional hot pink or electric blue. Framer anchors: near-black ground, white type, gray secondary, lime `#82FF1C`, case-field blue/cyan/purple.
- Prefer tactile imperfection over sterile polish on baseline surfaces. On Framer, prefer crisp dark UI over print grain unless restyling.
- Let type carry character: baseline may mix display voices; Framer currently uses Inter scale shifts only.
- Use ornament as system, not garnish — and only where the active surface allows it.
- Before shipping expressive work, ask Rams (is it honest / too much?) and Norman (can someone act and know the result?).

## Avoid

- Generic SaaS minimalism, soft startup gradients, stock-photo blandness, glassmorphism as default, decorative blobs, and empty luxury.
- Flattening cultural references into vague "ethnic" styling. Be specific about source qualities and respectful in use.
- Dense visuals that obscure affordances, states, labels, or content.
- Applying archival/textile maximalism to the current Framer portfolio chrome without an explicit restyle request.
- Treating the Framer template kit (FAQ/Awards/Services leftovers) as taste truth if it fights case clarity.
- Fashionable chrome, dishonest metrics, or silent interactions (fails Rams honesty / Norman feedback).

## Validation

Before finishing a design or review, check:

- Which surface am I on — baseline taste or Framer ship surface?
- Does the UI still work quickly for its real user (hiring manager / visitor)?
- Is hierarchy clear before expressive surface detail is added?
- Is there at least one specific visual idea beyond generic polish?
- Are color, type, texture, and spacing acting together rather than competing?
- Are experimental details preserved where they create energy?
- Have redundant motifs, repeated instructions, or decorative noise been trimmed?
- Rams: useful, honest, thorough, as little as possible?
- Norman: signifiers, mapping, feedback, recoverable errors?

## Assets

The original reference board is stored at `assets/taste-skill-reference.pdf`. Use it as a source artifact when visual fidelity matters, but rely on the reference notes for routine work. Framer page captures used for ship-surface evidence live under the HyperMind local runtime (gitignored); do not treat them as permanent skill assets.
