---
name: don-norman
description: >
  Applies Don Norman's interaction-design psychology from The Design of Everyday
  Things: affordances, signifiers, mapping, feedback, constraints, conceptual
  models, gulfs of execution/evaluation, and the seven stages of action. Use when
  the user mentions Don Norman, Norman doors, affordances, signifiers, feedback,
  mapping, constraints, conceptual models, user-centered design, discoverability,
  human error, or asks why an interface is confusing or how to make actions obvious.
---

# Don Norman — Psychology of Everyday Things

Use this skill as an **interaction psychology lens**. Norman explains why people succeed or fail with products — physical or digital — and how to design so action is discoverable and evaluation is easy.

Primary reference: Don Norman, *The Design of Everyday Things* (revised editions). Summarize and apply; do not paste copyrighted book text.

## When To Load

- Debugging confusing UI, flows, forms, or controls
- Reviewing buttons, navigation, toggles, doors-as-metaphor problems
- Designing for error, feedback, and system status
- Case studies that claim “intuitive” — verify with Norman’s terms
- Pairing with `dieter-rams` when usefulness is clear but interaction is opaque
- Pairing with `hypermind-taste` when expressive UI must stay operable

## Operating Loop

1. State the user’s goal.
2. Walk the **seven stages of action** for the critical path.
3. Locate failures in the **gulf of execution** (what to do?) or **gulf of evaluation** (what happened?).
4. Fix with the six interaction primitives below (prefer signifiers, mapping, feedback, constraints before more copy).
5. Check the **system image** against the intended conceptual model.

## Core Concepts

### Affordances
What actions are possible given the object and the user. In GUIs, affordances are often abstract; designers must not assume “looks clickable” without cues.

### Signifiers
Perceivable signals of where and how to act (labels, affordance cues, focus rings, underlines, affordance shadows, cursor). **Signifiers matter more than affordances in screen UI.**

### Mapping
Relationship between controls and effects. Prefer natural/spatial mappings (left control → left result).

### Feedback
Immediate, clear information that an action registered and what changed. Silence is a failure mode.

### Constraints
Physical, cultural, semantic, logical limits that prevent invalid actions and guide correct ones.

### Conceptual model
The user’s mental model of how the system works. The designer communicates only through the **system image** (UI, docs, behavior). Mismatch between designer model and user model causes error.

### Gulfs
- **Execution:** intention → action (can I figure out what to do?)
- **Evaluation:** world → interpretation (can I tell what happened / what state I’m in?)

## Seven Stages Of Action

1. Goal — what I want  
2. Plan — approach  
3. Specify — which action  
4. Perform — do it  
5. Perceive — sense the result  
6. Interpret — understand it  
7. Compare — does it match the goal?

Design so each stage is supported without manuals.

## Human-Centered Checklist (practical)

From Norman’s design guidance (paraphrased for practice):

1. Use knowledge in the world *and* knowledge in the head (visible structure + learned conventions).
2. Simplify the structure of tasks.
3. Make things visible — bridge both gulfs.
4. Get the mappings right.
5. Exploit constraints.
6. Design for error (prevent, detect, recover; do not blame the user).
7. When all else fails, standardize.

Also ask:

- Is the current system state visible?
- Can the user tell what actions are possible *now*?
- After every important action, is there timely feedback?
- Are errors recoverable without data loss or shame?

## Translation To Portfolio / Product UI

| Norman idea | Application |
|-------------|-------------|
| Signifiers | Clear CTAs, link affordances, form labels, focus states |
| Feedback | Hover/pressed/loading/success/error — never mute primary actions |
| Mapping | Nav order matches mental model (About / Work / Experiments); case cards map to case pages |
| Constraints | Disable impossible actions; validate early |
| Conceptual model | Portfolio should teach “decision-making designer” through structure, not slogans alone |
| Design for error | Broken links, draft pages, empty experiment sections — honest empty states |
| Blame the design | If a hiring manager cannot find the flagship case, the IA failed |

## Review Checklist

- What is the user’s goal on this screen?
- Where is the gulf of execution?
- Where is the gulf of evaluation?
- Which signifiers are missing or lying?
- Is feedback immediate and intelligible?
- What invalid actions are still possible?
- Does the system image teach the right conceptual model?
- If the user errs, can they recover?

## Anti-Patterns

- Calling something an “affordance” when you mean a visual style
- Hiding primary actions behind unexplained icons
- Motion or decoration that delays feedback
- Blaming users for “not reading” when signifiers failed
- “Intuitive” as a claim without a walkthrough of the seven stages

## Pairing

- With **Dieter Rams**: Norman makes action discoverable; Rams asks whether the feature should exist and whether claims are honest.
- With **hypermind-taste**: expressive surfaces still need signifiers, mapping, and feedback — especially on hybrid cards and dark UIs with low-contrast secondary text.
