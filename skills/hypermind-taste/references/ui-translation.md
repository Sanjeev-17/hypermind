# UI Translation

## Intensity Scale

- Low: operational tools, admin panels, data-heavy dashboards. Use restrained color, tight typography, subtle texture, clear grouping, and small ornamental details.
- Medium: consumer apps, portfolios, editorial tools, AI products. Use stronger color blocking, typographic contrast, patterned separators, richer empty states, and tactile surfaces.
- High: campaigns, cultural projects, games, experimental prototypes, posters, launches. Use dense collage, expressive type, bold patterns, saturated palettes, and custom illustration.

### Framer portfolio (special case)

Use **Medium** intensity with the ship-surface contract in `framer-portfolio.md`:

- Interaction chrome: black/gray, Inter, predictable nav and forms, lime for primary CTA/status only.
- Expression: hero claim scale, case mockup photography on saturated stage fields, sparse experiments cards.
- Do not import High-intensity archival collage into Framer pages by default.

## Surface Type

Use surface type independently from intensity. A high-intensity product still needs predictable forms; a low-intensity tool can still have expressive empty states or section boundaries.

- Interaction surfaces: navigation, forms, filters, tables, menus, and controls. Prioritize predictability, readability, accessibility, speed, clear affordances, and stable states.
- Expression surfaces: heroes, empty states, transitions, storytelling moments, section boundaries, and brand or identity surfaces. Allow stronger typography, texture, illustration, pattern, motion, and experimentation.
- Hybrid surfaces: cards, dashboards, data visualization, AI interfaces, and content modules. Allow controlled visual expression while preserving scanability and task performance.

Combine the two dimensions before designing: choose Low, Medium, or High intensity, then decide whether each screen area is an interaction, expression, or hybrid surface.

## Layout

- Prefer strong grids, clear scanning paths, and editorial composition.
- Let repeated items be disciplined. Use cards only for actual repeated objects, panels, or tools.
- Use ornament to frame or divide areas: borders, rules, corner marks, patterned strips, stamps, tabs, and labels.
- Keep control areas calm enough to operate repeatedly.

## Color

- Build palettes with warm earth, deep blue, faded neutral, and one or two saturated accents.
- Useful anchors: oxide red, turmeric yellow, indigo, ultramarine, teal, old paper, charcoal, cream, off-white, faded green.
- Framer portfolio anchors: near-black, white, mid gray, lime `#82FF1C`, plus case-stage blue/cyan/purple.
- Avoid all-purple, all-slate, all-beige, or gradient-only systems.

## Typography

- Pair a characterful display voice with readable UI text on baseline surfaces.
- On the Framer portfolio, stay with **Inter** scale shifts and tight tracking until a deliberate type restyle is requested.
- Favor poster-like headings, crisp labels, strong numerals, and small annotation text where useful.
- Keep text legible; expressive type should not compromise comprehension.

## Texture And Pattern

- Use texture to imply paper, ink, tile, metal, textile, print, or age.
- Use pattern at edges, section dividers, backgrounds, loading states, badges, and hero surfaces.
- Keep interactive controls visually stable and accessible.

## Components

- Buttons should feel precise and intentional. Prefer icons where a standard icon exists.
- Inputs, filters, tabs, tables, and menus should remain predictable.
- Empty states can carry illustration, stamps, archival labels, or small pattern fields.
- Data visualizations can use tactile palettes and annotation, but should stay numerically honest.

## Review Checklist

- Remove redundant decoration.
- Preserve one or two experimental moves that create identity.
- Strengthen hierarchy before adding more surface detail.
- Prioritize function, hierarchy, interaction, then expression.
- Check mobile and desktop for text fit, overlap, and touch target clarity.
- Make sure cultural references are specific, respectful, and connected to the product.
- Rams pass: useful, honest, understandable, thorough, as little as possible (`skills/dieter-rams`).
- Norman pass: signifiers, mapping, feedback, visible state, recoverable errors (`skills/don-norman`).
