---
title: "[Research] …"
purpose: "Investigate a focused question and return evidence-backed findings."
category: research
owner: portfolio-architect
version: "1.0.0"
status: draft
best_models: [Cursor, Claude, GPT]
difficulty: medium
project_stages: [discovery, strategy]
est_input_tokens: 800
est_output_tokens: 600
recommended_context_files: []
dependencies: []
related_documents: []
quality_score: { clarity: 0, specificity: 0, token_efficiency: 0, output_quality: 0, consistency: 0, reusability: 0, maintainability: 0, overall: 0 }
---

# [Research] …

## When to Use
Need evidence before a strategy decision.

## When NOT to Use
Decision already locked; pure writing polish; aesthetic critique.

## Inputs Required
- Research question (1 sentence)
- Scope boundaries
- Context files listed above only

## Expected Output
Findings table · confidence · sources/gaps · implications for next skill

## Prompt
You are a research specialist. Read ONLY: {{recommended_context_files}}.
Question: {{question}}
Scope: {{scope}}
Return: (1) findings with confidence, (2) gaps, (3) implications — no redesign.

## Example Usage
`question = "What do HMs scan in first 60s on PD portfolios?"`

## Known Limitations
…

## Improvement Log
## Revision History
| Version | Date | What changed | Why | Expected improvement |
| 1.0.0 | | Initial | | |
