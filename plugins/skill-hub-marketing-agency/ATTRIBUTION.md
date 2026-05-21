# Attribution

The skills in this plugin are derivative works adapted from open-source sources.
All derivations are licensed-compatible and credited below.

## seo-mastery, humanized-prose, design-ux

**Source:** [`lifenewjob/nebo-claude-skills-public`](https://github.com/lifenewjob/nebo-claude-skills-public)
**Original author:** WebCoreLab (commit signature on the upstream repository)
**License:** MIT
**Adapted skills:** `nebo-seo-mastery`, `nebo-content-writing`, `nebo-design-ux`

### Changes from the upstream sources

- Russian-language prose translated to English; technical terms (`hreflang`, `JSON-LD`,
  `E-E-A-T`, `WCAG`, `Core Web Vitals`, etc.) preserved verbatim.
- Upstream-specific metadata removed (NEBO "atom" counters, "replaces N skills"
  taxonomy markers, "SuperSkill" branding, duplicate trigger lines).
- Frontmatter rewritten to match the skill-hub house style
  (`name` + `description` + `origin`; no `user-invocable` / `allowed-tools` blocks).
- `design-ux`: Anthropic-specific brand palette removed in favor of a principle that
  brand tokens are read from the consuming project's design system; the "10 themes"
  list reframed as opinionated starter palettes rather than mandates; the
  craftsmanship-language principle rewritten to neutralize sycophantic phrasing.
- `humanized-prose`: renamed from upstream `content-writing` to reflect the actual
  scope (an anti-AI-slop prose checklist, not a general content workflow).

### MIT License terms (preserved from upstream)

> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
