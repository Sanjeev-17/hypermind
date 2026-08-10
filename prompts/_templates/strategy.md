---
title: "[Strategy] …"
purpose: "Produce a durable strategic artefact (audience, slate, IA, funnel)."
category: strategy
owner: portfolio-architect
version: "1.0.0"
status: draft
best_models: [Cursor, Claude]
difficulty: medium
project_stages: [strategy]
est_input_tokens: 1000
est_output_tokens: 800
recommended_context_files: ["portfolio-os/constitution/Portfolio_Constitution.md", "portfolio-os/strategy/Personas.md"]
dependencies: []
related_documents: ["portfolio-os/memory-index.md"]
quality_score: { clarity: 0, specificity: 0, token_efficiency: 0, output_quality: 0, consistency: 0, reusability: 0, maintainability: 0, overall: 0 }
---

# [Strategy] …

## When to Use
Defining or revising portfolio product strategy.

## When NOT to Use
Visual exploration; implementation; copy polish alone.

## Inputs Required
Goals · constraints · context files only

## Expected Output
Named strategy artefact matching memory-index path

## Prompt
You are portfolio-architect. Read ONLY: {{recommended_context_files}}.
Task: {{task}}
Write the artefact to the canonical path. No visuals, no final copy.

## Example Usage
Produce or update `Case_Slate.md` from a raw project list.

## Known Limitations
## Improvement Log
## Revision History
| Version | Date | What changed | Why | Expected improvement |
| 1.0.0 | | Initial | | |
