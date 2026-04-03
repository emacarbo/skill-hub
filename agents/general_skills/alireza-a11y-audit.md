---
name: a11y-audit
description: "WCAG 2.2 accessibility audit for React, Next.js, Vue, Angular, Svelte, and HTML. Use when auditing accessibility, fixing a11y violations, checking color contrast, or integrating a11y into CI/CD."
---

# Accessibility Audit

WCAG 2.2 Level A and AA compliance. Three-phase workflow: Scan, Fix, Verify.

## Quick Reference

| Feature | Description |
|---------|-------------|
| Full WCAG 2.2 Scan | All Level A and AA criteria |
| Framework Detection | React, Next.js, Vue, Angular, Svelte, HTML |
| Severity Classification | Critical, Major, Minor |
| Fix Code Generation | Before/after diffs per framework |
| Color Contrast Checker | AA/AAA ratio validation with alternatives |
| CI/CD Integration | GitHub Actions, GitLab CI, Azure DevOps |

### Severity Definitions

| Severity | Definition | SLA |
|----------|-----------|-----|
| **Critical** | Blocks access for user groups (missing alt, no keyboard access) | Fix before release |
| **Major** | Degrades experience (contrast, missing labels) | Current sprint |
| **Minor** | Friction (redundant ARIA, heading hierarchy) | Next 2 sprints |

## Usage

```bash
python scripts/a11y_scanner.py /path/to/project          # Scan project
python scripts/a11y_scanner.py /path/to/project --json    # JSON output
python scripts/contrast_checker.py --fg "#777" --bg "#fff" # Check contrast
```

## React / Next.js Fix Patterns

### Missing Alt Text (1.1.1)

```tsx
// BEFORE
<img src={hero} />

// AFTER - Informational
<img src={hero} alt="Team collaborating around a whiteboard" />

// AFTER - Decorative
<img src={divider} alt="" role="presentation" />
```

### Non-Interactive Element with Click (2.1.1)

```tsx
// BEFORE
<div onClick={handleClick}>Click me</div>

// AFTER - Navigation
<Link href="/destination">Click me</Link>

// AFTER - Action
<button type="button" onClick={handleClick}>Click me</button>
```

### Modal Focus Management (2.4.3)

```tsx
function Modal({ isOpen, onClose, children, title }) {
  const modalRef = useRef(null);
  const previousFocus = useRef(null);

  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement;
      modalRef.current?.focus();
    } else {
      previousFocus.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeydown = (e) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        const focusable = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (!focusable?.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first.focus();
        }
      }
    };
    document.addEventListener('keydown', handleKeydown);
    return () => document.removeEventListener('keydown', handleKeydown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;
  return (
    <div className="modal-overlay" onClick={onClose} aria-hidden="true">
      <div ref={modalRef} role="dialog" aria-modal="true" aria-label={title} tabIndex={-1}
           onClick={(e) => e.stopPropagation()}>
        <button onClick={onClose} aria-label="Close dialog">&times;</button>
        {children}
      </div>
    </div>
  );
}
```

### Focus Appearance (2.4.11 -- WCAG 2.2)

```css
button:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}
```

```tsx
// Tailwind
<button className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600">
  Submit
</button>
```

## Before/After Example: React Component

```tsx
// BEFORE
function ProductCard({ product }) {
  return (
    <div onClick={() => navigate(`/product/${product.id}`)}>
      <img src={product.image} />
      <div style={{ color: '#aaa' }}>{product.name}</div>
      <span style={{ color: '#999' }}>${product.price}</span>
    </div>
  );
}

// AFTER
function ProductCard({ product }) {
  return (
    <a href={`/product/${product.id}`} aria-label={`View ${product.name} - $${product.price}`}>
      <img src={product.image} alt={product.imageAlt || product.name} />
      <div style={{ color: '#595959' }}>{product.name}</div>
      <span style={{ color: '#767676' }}>${product.price}</span>
    </a>
  );
}
```

Fixes: `div onClick` to `<a>`, added `alt`, `aria-label`, contrast-safe colors.

## Color Contrast Quick Reference

| Original | Contrast on White | Fix | New Contrast |
|----------|------------------|-----|--------------|
| `#aaaaaa` | 2.32:1 | `#767676` | 4.54:1 (AA) |
| `#999999` | 2.85:1 | `#767676` | 4.54:1 (AA) |
| `#777777` | 4.48:1 | `#757575` | 4.60:1 (AA) |

### Tailwind Accessible Alternatives

| Inaccessible | Accessible Alternative |
|--------------|----------------------|
| `text-gray-400` (2.68:1) | `text-gray-600` (5.74:1) |
| `text-blue-400` (2.81:1) | `text-blue-700` (5.96:1) |
| `text-green-400` (2.12:1) | `text-green-700` (5.18:1) |
| `text-red-400` (3.04:1) | `text-red-700` (6.05:1) |

## WCAG 2.2 New Criteria

### 2.4.11 Focus Appearance (AA)
Focus indicator: 2px perimeter, 3:1 contrast. Use `:focus-visible { outline: 2px solid #005fcc; outline-offset: 2px; }`.

### 2.5.7 Dragging Movements (AA)
Drag functionality must have single-pointer alternative (click/tap buttons for reorder).

### 2.5.8 Target Size (AA)
Interactive targets: min 24x24 CSS px. Touch targets: recommend 44x44px.

### 3.3.7 Redundant Entry (A)
Auto-populate previously entered info in multi-step forms.

### 3.3.8 Accessible Authentication (AA)
Support password managers (`autocomplete="current-password"`), offer passkeys, never block paste, provide OTP alternative to CAPTCHA.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `role="button"` on `<div>` | Use native `<button>` |
| `tabindex="0"` everywhere | Only interactive elements need focus |
| `aria-label` on non-interactive elements | Use `aria-labelledby` or headings |
| `display: none` for SR content | Use `.sr-only` class |
| Color alone conveys meaning | Add icons/text alongside color |
| Placeholder as only label | Always use visible `<label>` |
| `outline: none` without replacement | Use `focus-visible` with outline |
| `onClick` without `onKeyDown` | Prefer native elements or add keyboard |

## Screen Reader Utility

```css
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0;
}
```

Tailwind includes `sr-only` by default.

## CI/CD: GitHub Actions

```yaml
name: Accessibility Audit
on:
  pull_request:
    paths: ['src/**/*.tsx', 'src/**/*.vue', 'src/**/*.html']
jobs:
  a11y-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: python scripts/a11y_scanner.py ./src --json > a11y-results.json
      - name: Check Critical Issues
        run: |
          python -c "
          import json, sys
          data = json.load(open('a11y-results.json'))
          critical = [v for v in data.get('violations', []) if v['severity'] == 'critical']
          if critical:
              for v in critical: print(f\"  [{v['wcag']}] {v['file']}:{v['line']} - {v['message']}\")
              sys.exit(1)
          "
```

## Testing Checklist

### Keyboard
- [ ] All interactive elements reachable via Tab
- [ ] Logical tab order; visible focus indicator (2px+)
- [ ] Modals trap focus, return on close; Escape closes overlays
- [ ] Arrow keys in composite widgets (tabs, menus)

### Screen Reader
- [ ] Images have appropriate alt text
- [ ] Logical heading hierarchy (h1 > h2 > h3)
- [ ] Form inputs have labels; errors announced via `aria-live`
- [ ] Page title updates on SPA navigation

### Visual
- [ ] Text contrast 4.5:1 normal, 3:1 large; UI components 3:1
- [ ] Content reflows at 320px; text resizable to 200%
- [ ] No information by color alone

### Forms
- [ ] Visible labels; required fields indicated (not color alone)
- [ ] Errors associated via `aria-describedby`; autocomplete attributes present

## Resources

- [WCAG 2.2 Spec](https://www.w3.org/TR/WCAG22/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y)
