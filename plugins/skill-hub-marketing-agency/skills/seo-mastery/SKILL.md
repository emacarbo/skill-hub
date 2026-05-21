---
name: seo-mastery
description: "Use when conducting a full SEO audit, working on on-page optimization, designing site architecture for search, generating XML sitemaps, writing JSON-LD schema, configuring hreflang for multilingual sites, optimizing for AI-driven search (GEO / AI Overviews), or planning programmatic SEO. Triggers on phrases like \"SEO audit\", \"meta tags\", \"schema markup\", \"hreflang\", \"sitemap\", \"AI Overviews\", \"E-E-A-T\", \"GEO\". NOT for paid search / Google Ads strategy."
origin: ECC
---

# SEO-Mastery

## When to Use
- Full site SEO audit (up to 500 pages)
- Single-page analysis (on-page SEO)
- SEO strategy / plan for a new site
- XML sitemap generation or validation
- Schema.org markup creation or review (JSON-LD)
- hreflang configuration for multilingual sites
- Optimization for AI-driven search engines (GEO)
- Programmatic SEO (pages generated from data)
- Competitor / alternatives page creation

## Key Principles

1. **Audit = 7 parallel specialists**: technical, content, schema, sitemap, performance, visual, geo — aggregated into an SEO Health Score (0–100)
2. **Scoring weights**: Technical 22%, Content 23%, Schema 10%, Performance 15%, GEO/AI 10%, Images 10%, Sitemap 10%
3. **E-E-A-T as the content foundation**: Experience, Expertise, Authoritativeness, Trustworthiness — check signals on every page
4. **Schema = JSON-LD only**: never microdata/RDFa; validate via Rich Results Test
5. **hreflang**: x-default is required, self-referencing is required, every pair must be reciprocal
6. **GEO (Generative Engine Optimization)**: llms.txt, passage-level citability, brand mention signals, AI crawler accessibility
7. **Programmatic SEO**: templates + unique data, protection against thin content, noindex for pages with < 300 words of unique content
8. **Competitor pages**: feature matrix with Schema (ComparisonTable), "vs" and "alternatives" URL structure

## Patterns and Techniques

### Technical SEO
- robots.txt: check Disallow on critical paths, Crawl-delay, Sitemap reference
- canonical: self-referencing on every page; no canonical on 404/5xx pages
- Core Web Vitals: LCP < 2.5s, INP < 200ms, CLS < 0.1
- Security: HTTPS, HSTS header, X-Content-Type-Options, CSP
- Mobile: viewport meta, tap targets >= 48px, font-size >= 16px
- IndexNow: instant indexing via API on publish

### Content
- Readability: Flesch-Kincaid Grade Level 8-10 for B2C, 12-14 for B2B
- Thin content detection: < 300 words = risk; check search intent coverage
- AI citation readiness: structured passages, clear claims with evidence, quotable statements
- Content depth: heading hierarchy (H1 -> H2 -> H3), internal linking >= 3 per page

### Schema.org
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "author": {"@type": "Person", "name": "..."},
  "datePublished": "2026-03-26",
  "publisher": {"@type": "Organization", "name": "..."}
}
```
- Required types: Organization (homepage), Article/Product/FAQ (by content type), BreadcrumbList (navigation)
- LocalBusiness for local SEO with GeoCoordinates
- Product with AggregateRating and Offer for e-commerce

### Sitemap
- Format: `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`
- Max 50,000 URLs or 50 MB per file; use sitemap index for large sites
- `<priority>` and `<changefreq>` are optional (Google ignores them)
- `<lastmod>` must be the real last-modified date, not the current date

### Hreflang
```html
<link rel="alternate" hreflang="en-us" href="https://example.com/en/" />
<link rel="alternate" hreflang="ru" href="https://example.com/ru/" />
<link rel="alternate" hreflang="x-default" href="https://example.com/" />
```
- Language code: ISO 639-1; region code: ISO 3166-1 Alpha-2
- Placement: `<head>`, HTTP header, or sitemap — pick ONE method

### GEO / AI Search Engines
- llms.txt in the site root — description for AI crawlers
- Passage-level citability: every paragraph is a self-contained claim
- Brand mentions: consistent NAP (Name, Address, Phone) across the web
- AI Overviews optimization: concise answers in the first 2-3 sentences

### Programmatic SEO
- URL pattern: `/[category]/[entity-slug]` — human-readable
- Template: unique data >= 60% of content, boilerplate <= 40%
- Internal linking automation: related entities, breadcrumbs, hub pages
- Index bloat prevention: noindex thin pages, canonical for duplicates

## Checklist
- [ ] All pages accessible to crawlers (not blocked in robots.txt)
- [ ] HTTPS + security headers in place
- [ ] canonical tags correct and self-referencing
- [ ] Schema.org JSON-LD valid (Rich Results Test)
- [ ] Sitemap current and registered in Search Console
- [ ] Core Web Vitals in the green zone
- [ ] hreflang reciprocal links in place (if multilingual)
- [ ] Meta title <= 60 characters, description <= 160 characters
- [ ] H1 unique on every page
- [ ] Images: alt text, WebP/AVIF format, lazy loading, width/height set
- [ ] Internal linking >= 3 links per page
- [ ] llms.txt for AI crawlers (where relevant)

## Examples

### Quick single-page audit
```
Task: "audit the SEO of https://example.com/product/widget"
Steps:
1. Fetch HTML -> check title, meta description, canonical, OG tags
2. Check Schema.org markup -> validate JSON-LD
3. Core Web Vitals -> LCP, INP, CLS
4. Content: H1, heading hierarchy, word count, internal links
5. Images: alt text, format, size, lazy loading
6. Output score 0-100 with prioritized recommendations
```

### SEO plan for a new site
```
Task: "create an SEO strategy for a SaaS product"
Steps:
1. Identify business type -> SaaS B2B
2. Keyword research -> core terms, long-tail, competitor gaps
3. Site architecture -> hub pages, topic clusters, URL structure
4. Content strategy -> pillar pages, supporting articles, FAQ
5. Technical foundation -> Next.js SSR, Schema.org, sitemap
6. Competitor analysis -> feature comparison pages, "vs" pages
7. Roadmap: Month 1-3 foundation, 4-6 content, 7-12 authority
```
