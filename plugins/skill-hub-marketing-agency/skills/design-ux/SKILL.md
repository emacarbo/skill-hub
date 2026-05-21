---
name: design-ux
description: "Use when producing visual artifacts (posters, PDFs, infographics), designing UI/UX (component patterns, color schemes, themes), creating Excalidraw architecture diagrams, performing WCAG 2.2 accessibility audits, or applying brand identity to outputs. Triggers on \"design\", \"UI/UX\", \"color scheme\", \"theme\", \"diagram\", \"WCAG\", \"branding\", \"Excalidraw\", \"poster\", \"accessibility\". NOT for chart authoring (use a charting skill) or for production frontend implementation (use a framework-specific skill)."
origin: ECC
---

# DESIGN-UX

## When to Use
- Producing visual artifacts (posters, PDFs, PNGs, infographics)
- Excalidraw diagrams (architecture, workflows, concepts)
- Applying brand identity and themes to artifacts
- WCAG 2.2 accessibility audits and fixes
- Design systems: colors, typography, components
- UI/UX review: contrast, touch targets, keyboard navigation

## Key Principles

1. **Diagrams must ARGUE, not merely DISPLAY**: if you strip the text, the structure itself should communicate meaning (Isomorphism Test).
2. **Canvas: Philosophy → Expression**: define the visual philosophy in prose first, then express it visually (PDF/PNG). Don't skip the philosophy step.
3. **Ship at appropriate fidelity**: finish what you start. A half-polished visual is worse than a deliberately rough sketch — decide the target fidelity upfront and hit it. Don't leave undefined styles, placeholder colors, or broken layouts.
4. **Themes: 10 starter presets + custom**: Ocean Depths, Sunset Boulevard, Forest Canopy, Modern Minimalist, Golden Hour, Arctic Frost, Desert Rose, Tech Innovation, Botanical Garden, Midnight Galaxy. These are starting points, not mandates — adapt or replace them when the project's design system specifies otherwise.
5. **WCAG AA minimum**: contrast 4.5:1 for body text, 3:1 for large text, touch targets ≥ 44px, focus visible on all interactive elements.
6. **Semantic HTML first**: `<nav>`, `<main>`, `<article>`, `<section>` instead of `<div>`. Screen readers rely on landmarks.
7. **Brand tokens come from the project**: before producing any visual, read the project's design system or CLAUDE.md for its canonical color palette, typefaces, and spacing scale. Never assume or invent brand values. If none are defined, ask or use a neutral fallback.

## Patterns and Techniques

### Canvas Design (PDF/PNG)

1. **Name the movement**: give the visual a conceptual identity — "Brutalist Joy", "Chromatic Silence", "Metabolist Dreams".
2. **Articulate the philosophy** (4–6 paragraphs): cover space/form, color/material, scale/rhythm, composition/balance.
3. **Express visually**: 90% visual design, 10% text as accent — not the reverse.
4. **Avoid**: redundancy between description and visuals; generic AI aesthetics (gradients for the sake of gradients, stock-icon grids).

Philosophy examples:
- **Concrete Poetry**: monumental forms, bold geometry, Polish poster energy
- **Chromatic Language**: color as an information system, Josef Albers meets data visualization
- **Analog Meditation**: textures, negative space, Japanese photobook aesthetic

### Excalidraw Diagrams

```json
{
  "type": "excalidraw",
  "version": 2,
  "elements": [
    {
      "type": "rectangle",
      "x": 100, "y": 100,
      "width": 200, "height": 80,
      "backgroundColor": "#a5d8ff",
      "strokeColor": "#1971c2"
    }
  ]
}
```

- **Evidence artifacts**: code snippets (dark background + syntax color), JSON examples, event sequences.
- **Depth calibration**: simple/conceptual → abstract shapes; technical → concrete examples with real specs.
- **Research mandate**: for technical diagrams, look up real service names, API endpoints, and event types before drawing. Don't invent names.

### Theme Application

1. Show `theme-showcase.pdf` to the user.
2. Wait for theme selection.
3. Read the specification from the `themes/` directory.
4. Apply colors and typefaces consistently across the entire artifact.
5. Custom theme: generate from the user's description, show a preview for review before applying.

### WCAG 2.2 Accessibility

**Semantic HTML:**
```html
<header>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/" aria-current="page">Home</a></li>
    </ul>
  </nav>
</header>
<main>
  <article>
    <h1>Title</h1>
    <section aria-labelledby="specs-heading">
      <h2 id="specs-heading">Specs</h2>
    </section>
  </article>
</main>
```

**ARIA Patterns:**
- Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, Escape to close
- Tabs: `role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls`, arrow key navigation
- Accordion: `aria-expanded`, `aria-controls`, Enter/Space to toggle
- Live regions: `aria-live="polite"` for updates, `"assertive"` for alerts

**Keyboard navigation:**
- Tab: move between focusable elements
- Arrow keys: navigate within a component (tabs, menus, radio groups)
- Escape: close modal/dropdown
- Enter/Space: activate
- Focus trap in modals: Tab cycles inside; restore focus on close

**Color and Contrast:**
- Body text: ≥ 4.5:1 (AA), ≥ 7:1 (AAA)
- Large text (≥ 18pt or 14pt bold): ≥ 3:1
- Non-text UI elements: ≥ 3:1
- Never use color as the sole indicator — pair with an icon or text label

## Checklist
- [ ] All interactive elements are keyboard-accessible
- [ ] Focus visible on all focusable elements
- [ ] Alt text on all informative images
- [ ] Heading hierarchy has no gaps (H1 → H2 → H3)
- [ ] Color contrast verified (axe-core / Lighthouse)
- [ ] ARIA roles are correct and don't duplicate native semantic HTML
- [ ] Touch targets ≥ 44×44px
- [ ] Diagrams pass the education test (a viewer can learn something from the structure alone)
- [ ] Theme: colors and typefaces are consistent throughout the artifact

## Examples

### Excalidraw microservices architecture diagram
```
Task: "draw the microservices architecture"
1. Research: real service names, event types, API endpoints from the codebase/docs
2. Layout: left-to-right flow, service boxes with real names
3. Evidence: JSON event examples in dark rectangles
4. Connections: arrows labeled with event type names
5. Color: service groups share a hue, consistent palette across the diagram
```
