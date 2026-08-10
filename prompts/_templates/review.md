---
title: "[Review] …"
purpose: "Gate-style review producing pass/fail and remediation owners."
category: review
owner: quality-auditor
version: "1.0.0"
status: draft
best_models: [Cursor, Claude]
difficulty: medium
project_stages: [review, release]
est_input_tokens: 1000
est_output_tokens: 700
recommended_context_files: ["portfolio-os/constitution/Portfolio_Constitution.md"]
dependencies: []
related_documents: ["portfolio-os/qa/Release_Readiness.md"]
quality_score: { clarity: 0, specificity: 0, token_efficiency: 0, output_quality: 0, consistency: 0, reusability: 0, maintainability: 0, overall: 0 }
---

# [Review] …

## When to Use
Release or checkpoint review against a fixed checklist.

## When NOT to Use
Exploratory ideation; first-draft creative work.

## Inputs Required
Scope · checklist docs · URL if applicable

## Expected Output
Pass/fail per area · blockers · owner skills

## Prompt
You are a review gate. Read ONLY listed files. Verdict must be go/no-go with evidence. No redesign.

## Example Usage
## Known Limitations
## Improvement Log
## Revision History
| Version | Date | What changed | Why | Expected improvement |
| 1.0.0 | | Initial | | |
