# Taste Evolution Log

Update this file when Sanjeev gives taste feedback, approves a direction, rejects an output, adds references, or asks the skill to evolve. Treat feedback as evidence before turning it into durable guidance.

## Evidence Model

- Observation: a single reaction, note, example, or piece of evidence. New feedback normally starts here.
- Pattern: a preference or rejection repeated across contexts, reinforced by multiple observations, or stated with moderate certainty by Sanjeev.
- Principle: a stable preference suitable for future guidance because it is repeated, explicitly confirmed, or supported by enough evidence.

Use these fields on every entry:

- confidence: low | medium | high
- scope: global | context | project

Promotion flow:

```text
feedback -> observation -> pattern if reinforced -> principle if sufficiently stable
```

Do not promote a like/dislike directly into a global rule unless Sanjeev explicitly says it should become one.

## Entry Format

```text
Date: YYYY-MM-DD
Type: Observation | Pattern | Principle
Confidence: low | medium | high
Scope: global | context | project
Context:
Liked:
Rejected:
Evidence:
Implication:
Reference:
```

## Current Baseline

Date: 2026-08-10
Type: Pattern
Confidence: medium
Scope: global
Context: Initial taste skill built from the local image-based reference PDF.
Liked: Cultural specificity, archival and material references, vernacular graphics, saturated accents, ornament, print texture, poster energy, and tactile imperfection.
Rejected: Generic SaaS polish, bland gradients, decorative-only effects, empty luxury, and over-sanitized minimalism.
Evidence: Multiple references in the initial board share material, vernacular, editorial, ornamental, and archival qualities.
Implication: Use the board as a strong baseline, not a complete or rigid definition of taste.
Reference: `assets/taste-skill-reference.pdf`

Date: 2026-08-10
Type: Principle
Confidence: high
Scope: global
Context: Revision request for the taste skill itself.
Liked: Scalable feedback handling, experimental references, and the existing architecture.
Rejected: Treating every like/dislike as a permanent rule; rebuilding the skill as a generic design system.
Evidence: Sanjeev explicitly requested observation, pattern, and principle levels with confidence and scope.
Implication: Record new feedback as Observation by default; promote only when reinforced, confirmed, or sufficiently evidenced.
Reference: Conversation request on 2026-08-10.

Date: 2026-08-10
Type: Observation
Confidence: high
Scope: project
Context: Framer project "Sanjeev's Portfolio" inspected via Framer agent (styles + page screenshots for `/`, `/work`, `/about`, `/experiments`).
Liked: High-contrast dark field; large Inter headlines with tight tracking; single lime accent for CTA/status; saturated case-stage cards with device mockups; clear Work/About/Experiments IA; metric-led case one-liners; sparse Experiments page for AI/prototype work.
Rejected: Treating this agency-template chrome as identical to the archival/vernacular baseline; importing textile/poster density into the current Framer pages without a restyle brief; leftover template modules (FAQ/Awards/Services) as taste authorities.
Evidence: Color styles Black/White/Accent(`rgb(130,255,28)`)/grays; fonts `[Inter]`; screenshots of home/work/about/experiments; CMS Work cases P-001/P-005/P-006.
Implication: Document a separate Framer ship-surface contract; keep baseline taste for Hypermind/experimental work; when editing Framer, match dark+lime+Inter first.
Reference: `references/framer-portfolio.md`; Framer project `6EnOOaab7bLwBHTmdNGH`

Date: 2026-08-10
Type: Pattern
Confidence: medium
Scope: context
Context: Portfolio ship surface vs personal taste board.
Liked: Explicit dual-track: baseline board remains aspirational; Framer site is the public product chrome hiring managers see.
Rejected: Collapsing both into one global aesthetic rule.
Evidence: Live site visual system diverges sharply from the initial taste PDF (dark Inter/lime vs archival/ornamental).
Implication: Agents must pick the active surface before designing. Portfolio OS interview-conversion goals apply to Framer edits.
Reference: Conversation request to update taste skill from Framer portfolio (2026-08-10).

Date: 2026-08-10
Type: Principle
Confidence: high
Scope: global
Context: Sanjeev stated inspiration from Dieter Rams and Don Norman; requested they be inspected and converted into skills, and included in taste files.
Liked: Rams' useful/honest/unobtrusive/long-lasting/thorough/as-little-as-possible judgment; Norman's affordances/signifiers, mapping, feedback, constraints, conceptual models, gulfs, design for error.
Rejected: Treating Rams as mere gray minimal styling; treating Norman as "add tooltips"; collapsing either into the archival taste palette.
Evidence: Explicit user request; public Rams Ten Principles (Vitsœ / Rams Foundation); Norman's Design of Everyday Things concepts as interaction psychology.
Implication: Ship dedicated `skills/dieter-rams` and `skills/don-norman`; wire into hypermind-taste as quality/interaction overlays beside surface dialect.
Reference: `skills/dieter-rams/SKILL.md`, `skills/don-norman/SKILL.md`, `references/influences-rams-norman.md`

## Open Experiments

- Translate dense textile and tile systems into subtle app navigation, borders, and state indicators.
- Use vernacular packaging hierarchy for product cards, badges, and dashboards.
- Explore archival collage as a UI metaphor for memory, knowledge, and personal operating systems.
- Test how much ornament an operational interface can carry before scan speed drops.
- Combine non-archival reference families with the original baseline without diluting the tactile, culturally specific, and editorial signal.
- Optionally restyle Framer toward the baseline board in a deliberate pass — do not mix dialects mid-page.
- Tighten Framer case cards around decision narratives; demote vanity-stat heroization when numbers are unverified.
- Apply Rams honesty + Norman feedback audits to Framer CTAs, empty experiment sections, and metric lines.
