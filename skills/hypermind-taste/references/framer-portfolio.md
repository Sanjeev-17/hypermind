# Framer Portfolio Ship Surface

**Project:** Sanjeev's Portfolio (`6EnOOaab7bLwBHTmdNGH`)  
**Pages:** `/`, `/about`, `/work`, `/experiments`, CMS `/work/:Work`  
**Role of this file:** Concrete tokens and layout patterns for the **live Framer ship surface**.  
Do **not** replace the cultural baseline in `visual-language.md`. Use this when editing, reviewing, or extending the Framer portfolio itself.

## Visual System (observed 2026-08-10)

### Color

| Token | Value | Use |
|-------|-------|-----|
| Black | `rgb(13, 13, 13)` / near `#0D0D0D` | Page ground |
| Light Black | `rgb(18, 18, 18)` | Subtle panels |
| Dark Gray | `rgb(26, 26, 26)` | Cards / elevated surfaces |
| Medium Gray | `rgb(38, 38, 38)` | Secondary surfaces |
| Gray | `rgb(138, 138, 138)` | Secondary body |
| Light Gray | `rgb(194, 194, 194)` | Muted labels |
| White | `rgb(255, 255, 255)` | Primary type / icons |
| Accent | `rgb(130, 255, 28)` ≈ `#82FF1C` | Primary CTA fill, online/status, key icons |

Project cards also use **saturated field colors** behind device mockups (observed: royal blue, cyan, purple). These are case-specific stage colors, not global brand accents.

### Typography

- Family in project: **Inter** only (no custom display face installed).
- Large display headlines (~88px H1) with **tight negative tracking** (−0.04em to −0.05em).
- Body ~16–18px; secondary/meta ~14px.
- Hierarchy is scale + weight + gray vs white, not mixed type families.

### Layout & chrome

- Dark full-bleed pages; high contrast white type on black.
- Top nav: logo mark left; About / Work / Experiments; pill **Contact me** (outline or lime fill).
- Home composition: brand-scale hero claim → short bio → logo/client strip → lime CTA → selected work cards → stats → process steps → testimonials → writing teaser → bio/footer CTA.
- Work: stacked case cards with mockup + one-line outcome line.
- About: experience timeline, stack chips in rounded cards, leadership notes, personal interests.
- Experiments: sparse sections (AI agent card, prototypes, empty AI Generations / Illustrations).
- Footer pattern: short bio + “Don't be a stranger!” + email/phone + text nav.

### Components (Framer)

Navigation, Primary/Secondary buttons, Project/Service/Article/Experience cards, Footer, Carousel, Awards, FAQ, process, stack cards — largely template-derived agency portfolio kit.

## Product constraints (Portfolio OS)

When changing this site, prioritize **interview conversion** over award-site spectacle:

- Flagship case clarity (P-006 systems, P-005 check-in, P-001 delivery) over more chrome.
- Decision-ready narratives over vanity stats when numbers are unverified (**Rams: honest**).
- Stable contact/resume paths; do not bury CTA (**Norman: signifiers + mapping**).
- Cut unused template modules that add visual pollution without use (**Rams: as little as possible / environmentally friendly as visual noise**).
- Every primary action needs clear feedback (hover/press/navigation) (**Norman: feedback**).

Load `skills/dieter-rams` and `skills/don-norman` when reviewing this surface for quality and interaction, not only visual match.

## Intensity guidance for this surface

- Treat Framer portfolio pages as **Medium** intensity on a **hybrid** surface: expressive hero + calm interaction chrome.
- Allowed expression: lime accent, saturated case stage fields, large type, mockup photography.
- Not allowed by default on this surface: archival collage, tile/paisley density, turmeric/vermilion folk palettes, print grain, vernacular packaging — those belong to the **baseline taste board**, not the current Framer chrome unless Sanjeev explicitly asks to restyle the site toward that board.

## Anti-patterns for matching this site

- Switching to cream paper / terracotta / purple SaaS gradients.
- Soft glassmorphism as default.
- Replacing Inter with ornamental display without a deliberate restyle brief.
- Adding dense textile backgrounds behind case evidence.
