---
title: "[Code] …"
purpose: "Implement or modify code against a locked spec with minimal scope."
category: frontend
owner: framer-builder
version: "1.0.0"
status: draft
best_models: [Cursor, GPT]
difficulty: medium
project_stages: [build]
est_input_tokens: 1500
est_output_tokens: 1200
recommended_context_files: []
dependencies: []
related_documents: ["portfolio-os/build/Deviation_Log.md"]
quality_score: { clarity: 0, specificity: 0, token_efficiency: 0, output_quality: 0, consistency: 0, reusability: 0, maintainability: 0, overall: 0 }
---

# [Code] …

## When to Use
Spec-locked implementation or bugfix.

## When NOT to Use
Open-ended redesign; missing specs.

## Inputs Required
Spec paths · file targets · acceptance checks

## Expected Output
Code changes · deviation log entries if any

## Prompt
Implement ONLY {{scope}}. Read ONLY: {{recommended_context_files}}.
Do not invent design. Log deviations. Match tokens/system where specified.

## Example Usage
## Known Limitations
## Improvement Log
## Revision History
| Version | Date | What changed | Why | Expected improvement |
| 1.0.0 | | Initial | | |
