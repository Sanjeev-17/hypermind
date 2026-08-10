---
title: "[Writing] …"
purpose: "Produce locked copy from a story outline and voice guide."
category: storytelling
owner: editorial-director
version: "1.0.0"
status: draft
best_models: [Claude, GPT, Cursor]
difficulty: medium
project_stages: [design, build]
est_input_tokens: 1200
est_output_tokens: 900
recommended_context_files: ["portfolio-os/editorial/Voice_Guide.md"]
dependencies: []
related_documents: []
quality_score: { clarity: 0, specificity: 0, token_efficiency: 0, output_quality: 0, consistency: 0, reusability: 0, maintainability: 0, overall: 0 }
---

# [Writing] …

## When to Use
Turning outlines into final wording.

## When NOT to Use
Inventing narrative structure or metrics; visual direction.

## Inputs Required
Outline path · voice guide · surface name

## Expected Output
`editorial/{surface}-Copy_Deck.md`

## Prompt
You are editorial-director. Read ONLY: {{recommended_context_files}}.
Do not change hire thesis or invent metrics. Output copy deck only.

## Example Usage
## Known Limitations
## Improvement Log
## Revision History
| Version | Date | What changed | Why | Expected improvement |
| 1.0.0 | | Initial | | |
