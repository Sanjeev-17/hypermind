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

## Open Experiments

- Translate dense textile and tile systems into subtle app navigation, borders, and state indicators.
- Use vernacular packaging hierarchy for product cards, badges, and dashboards.
- Explore archival collage as a UI metaphor for memory, knowledge, and personal operating systems.
- Test how much ornament an operational interface can carry before scan speed drops.
- Combine non-archival reference families with the original baseline without diluting the tactile, culturally specific, and editorial signal.
