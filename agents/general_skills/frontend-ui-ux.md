---
name: frontend-ui-ux
description: "Comprehensive frontend UI/UX specialist covering project scaffolding, component systems, design tokens, accessibility auditing, landing page generation, animation/motion design, and frontend security. Use when building React/Next.js frontends, creating design systems, auditing WCAG compliance, generating high-converting landing pages, adding scroll animations, or hardening frontend code against XSS."
license: MIT
metadata:
  domain: frontend
  triggers: frontend, UI, UX, design system, design tokens, accessibility, WCAG, a11y, landing page, animation, parallax, Tailwind, component library, Storybook, XSS, CSP, scaffold, bundle size, Core Web Vitals
  role: specialist
  scope: implementation
  output-format: code
  related-skills: react-development, typescript-javascript, security-guardian
---

# Frontend UI/UX

Senior frontend specialist combining project scaffolding, design systems, accessibility, high-converting marketing pages, cinematic animations, and frontend security hardening.

## When to Use This Skill

- Scaffolding new React/Next.js projects with opinionated structure
- Building and documenting component libraries (Storybook, design tokens)
- Creating design token systems (color palettes, typography, 8pt grid)
- Auditing and fixing WCAG 2.2 AA accessibility violations
- Generating high-converting landing pages with proven copy frameworks
- Adding scroll-driven animations, parallax, or cinematic site effects
- Analyzing and optimizing bundle size
- Hardening frontend code against XSS, CSP issues, and DOM security

## Core Workflow

1. **Scope the task** — Determine which domain applies: scaffolding, design system, accessibility, landing page, animation, or security
2. **Gather inputs** — Project type, brand color, target audience, existing assets, framework
3. **Design/analyze** — Tokens, component hierarchy, copy framework, depth system, or vulnerability scan
4. **Implement** — Generate production-ready code with accessibility built in
5. **Validate** — Run type check, a11y scan, bundle analysis, Core Web Vitals check
6. **Deliver** — Storybook stories, handoff docs, or compliance report as needed

## Project Scaffolding

Standard Next.js structure: `app/` (layouts, pages, API routes), `components/ui/` (Button, Input, Card), `components/layout/`, `hooks/`, `lib/` (cn(), constants), `types/`, `tailwind.config.ts`.

**Scaffolder flags:** `--template nextjs|react`, `--features auth|api|forms|testing|storybook`

Generate components with TypeScript, tests, and Storybook stories:
```tsx
// Generated button with cn() (clsx + tailwind-merge)
'use client';
import { cn } from '@/lib/utils';
interface ButtonProps { variant?: 'primary'|'ghost'; size?: 'sm'|'md'|'lg'; className?: string; children: React.ReactNode; }
export function Button({ variant='primary', size='md', className, children, ...props }: ButtonProps) {
  return (
    <button className={cn('rounded font-medium transition-colors focus-visible:ring-2',
      variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
      size === 'sm' && 'h-8 px-3 text-sm', size === 'md' && 'h-10 px-4 text-base',
      className)} {...props}>{children}</button>
  );
}
```

## Design System

### Design Token Generation
From a single brand hex color, generate a complete token system:
```bash
python scripts/design_token_generator.py "#0066CC" modern css > design-tokens.css
python scripts/design_token_generator.py "#0066CC" modern json > design-tokens.json  # for Figma Tokens Studio
```

**Token categories:** colors (50–900 scale), typography (1.25x modular scale), spacing (8pt grid: 0–64), borders, shadows (none–2xl), animation (duration/easing), breakpoints, z-index.

**Typography scale (1.25x ratio):** xs=10px, sm=13px, base=16px, lg=20px, 2xl=31px, 4xl=49px.
Fluid typography: `clamp(1rem, 0.5rem + 2vw, 1.5rem)` scales 16px–24px between 320–1200px viewport.

### WCAG Contrast Requirements

| Level | Normal Text | Large Text (≥18pt or ≥14pt bold) |
|-------|-------------|----------------------------------|
| AA | 4.5:1 | 3:1 |
| AAA | 7:1 | 4.5:1 |

**Tailwind integration:** Pass JSON tokens to `tailwind.config.ts` theme, or import CSS variables into globals.css. Use Tokens Studio Figma plugin to sync the JSON file.

### CSS-in-JS vs Utility-First

| Approach | Best For | Trade-offs |
|----------|----------|------------|
| **Tailwind CSS** | Rapid prototyping, design systems with tight constraints | Verbose JSX, requires purge config |
| **CSS Modules** | Scoped styles, traditional CSS authoring | Less co-location, no design token DX |
| **styled-components / Emotion** | Dynamic themes, component-level encapsulation | Runtime overhead, bundle size |
| **vanilla-extract** | Zero-runtime CSS-in-JS with type safety | Build complexity |

**Recommendation:** Tailwind + CSS variables for design tokens is the dominant pattern for Next.js projects. Use `cn()` (clsx + tailwind-merge) for conditional classes.

## Accessibility Audit (WCAG 2.2 AA)

### Three-Phase Pipeline: Scan → Fix → Verify

**Phase 1 — Scan:**
```bash
python scripts/a11y_scanner.py /path/to/project --framework react
```
Auto-detects framework (React, Next.js, Vue, Angular, Svelte) and categorizes violations by severity.

**Severity SLA:**

| Severity | Example | SLA |
|----------|---------|-----|
| Critical | Missing alt on informational image, no keyboard access | Fix before release |
| Major | Insufficient color contrast on body text | Fix in current sprint |
| Minor | Redundant ARIA roles | Fix in next 2 sprints |

**Phase 2 — Fix (framework-specific):** Use `aria-label` on icon-only buttons, `aria-hidden="true"` on decorative icons, skip links (`<a href="#main" className="sr-only focus:not-sr-only">`), `aria-describedby`/`aria-invalid` on form fields with errors, `role="alert"` on error messages.

**Phase 3 — Verify:** Re-run scanner; confirm zero Critical/Major; generate compliance report.

### WCAG 2.2 New Criteria (often missed)
- **2.4.11 Focus Appearance** — Focus indicator must be visible at minimum 2px outline
- **2.5.7 Dragging Movements** — Provide single-pointer alternative for any drag operation
- **2.5.8 Target Size** — Touch targets minimum 24×24px (recommend 44×44px)
- **3.3.7 Redundant Entry** — Don't ask users to re-enter previously submitted info
- **3.3.8 Accessible Authentication** — No cognitive function tests for login

## Landing Page Generation

### Generation Workflow
1. Gather: product name, tagline, audience, pain point, key benefit, pricing, design style, copy framework
2. Select design style and copy framework (or infer from brand voice)
3. Generate sections: Hero → Features → Pricing → FAQ → Testimonials → CTA → Footer
4. Validate SEO checklist before output

### Copy Frameworks

| Framework | Structure | Best For |
|-----------|-----------|----------|
| **PAS** | Problem → Agitate → Solution | Developer tools, productivity |
| **AIDA** | Attention → Interest → Desire → Action | Enterprise, formal audiences |
| **BAB** | Before → After → Bridge | Transformation-focused products |

### Design Styles (Tailwind Class Sets)

| Style | Background | Accent | Use For |
|-------|------------|--------|---------|
| Dark SaaS | `bg-gray-950 text-white` | `violet-500` | Dev tools, modern SaaS |
| Clean Minimal | `bg-white text-gray-900` | `blue-600` | B2B, professional |
| Bold Startup | `bg-white text-gray-900` | `orange-500` | Consumer, high-energy |
| Enterprise | `bg-slate-50 text-slate-900` | `slate-700` | Corporate, formal |

### Core Web Vitals Targets

| Metric | Target | Technique |
|--------|--------|-----------|
| LCP | < 1s | `priority` on hero `<Image>`, preload |
| CLS | < 0.1 | Explicit width/height on all images |
| FID/INP | < 100ms | Defer non-critical JS |
| TTFB | < 200ms | Static generation or ISR |
| Bundle | < 100KB JS | `@next/bundle-analyzer` |

### SEO Checklist
- [ ] `<title>`: primary keyword + brand (50–60 chars)
- [ ] Meta description: benefit + CTA (150–160 chars)
- [ ] Single H1 with primary keyword
- [ ] Structured data (FAQPage, Product, Organization schema)
- [ ] OG image 1200×630px
- [ ] Canonical URL set
- [ ] Alt text on all `<Image>` components

## Cinematic Animations (2.5D / Epic Design)

Use for premium product sites, Apple-style scroll effects, or immersive experiences.

### 6-Layer Depth System

| Layer | Role | Parallax | Blur |
|-------|------|----------|------|
| depth-0 | Far background | 0.10x | 8px |
| depth-1 | Atmosphere/glow | 0.25x | 4px |
| depth-2 | Mid decorations | 0.50x | 0px |
| depth-3 | Main product/hero | 0.80x | 0px |
| depth-4 | Text / UI | 1.00x | 0px |
| depth-5 | Foreground FX | 1.20x | 0px |

### Technique Selection

| User Intent | Techniques |
|-------------|------------|
| "Apple-style" | Scrub timeline + word-by-word text lighting |
| "Sections overlap/stack" | Cascading card stack + section peel |
| "Product rises between sections" | Inter-section floating product + clip-path birth |
| "Text flies in from sides" | Split converge + offset diagonal |
| "Cinematic reveal" | Curtain panel roll-up + top-down clip |

### Performance Rules (Non-Negotiable)
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
- Only animate: `transform`, `opacity`, `filter`, `clip-path` — never `width/height/top/left`
- Remove `will-change` after animations complete
- Use `IntersectionObserver` to animate only viewport-visible elements
- Detect touch/mobile: `window.matchMedia('(pointer: coarse)')` — reduce effects

## Bundle Analysis

Heavy dependency alternatives:

| Package | Size | Replace With |
|---------|------|--------------|
| moment | 290KB | date-fns (12KB) or dayjs (2KB) |
| lodash | 71KB | lodash-es with tree-shaking |
| axios | 14KB | Native fetch or ky (3KB) |
| @mui/material | Large | shadcn/ui or Radix UI |
| jquery | 87KB | Native DOM APIs |

## Frontend Security (XSS + CSP)

### XSS Prevention Rules
```typescript
// Never: innerHTML with user input
element.innerHTML = userInput;  // XSS vector

// Correct: textContent for plain text
element.textContent = userInput;

// Correct: sanitize when HTML is required
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);

// React: sanitize before dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />

// URL validation — block javascript: and data: protocols
function sanitizeURL(url: string): string {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : '#';
  } catch { return '#'; }
}
```

### CSP Configuration (Next.js)
```typescript
// next.config.js — Content Security Policy headers
const cspHeader = `
  default-src 'self';
  script-src 'self' 'nonce-${nonce}';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
`;
```

**Framework-specific XSS rules:**
- React: Sanitize before `dangerouslySetInnerHTML`; prefer JSX text nodes
- Vue: Prefer `v-text` over `v-html`; sanitize if `v-html` is required
- Angular: Use built-in DomSanitizer; never bypass security trust methods

## i18n/l10n and PWA

**i18n:** Use `next-intl` (Next.js) or `react-i18next`. Store strings in `/messages/en.json`. Use `Intl.DateTimeFormat`/`Intl.NumberFormat`. Set `lang` on `<html>` (WCAG 3.1.1). RTL: `dir="rtl"` + CSS logical properties.

**PWA:** Add `next-pwa` or `vite-plugin-pwa` for service worker + `manifest.json`. Cache static aggressively; network-first for API routes. Add `<meta name="theme-color">` and icons for installability.

## Constraints

### MUST DO
- TypeScript strict mode
- Accessibility built in from the start (not retrofitted)
- Semantic HTML elements (`<button>`, `<nav>`, `<main>`, `<article>`)
- `prefers-reduced-motion` fallback on all animations
- WCAG AA color contrast (4.5:1 normal, 3:1 large text)
- Touch targets minimum 44×44px

### MUST NOT DO
- Use `<div>` for interactive elements (use `<button>`, `<a>`)
- Animate `width`, `height`, `top`, `left` (causes layout thrash)
- Set `will-change` and leave it permanently
- Skip alt text on informational images
- Use `dangerouslySetInnerHTML` without sanitization
- Hardcode colors without checking contrast ratio
