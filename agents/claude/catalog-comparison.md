# Skill Catalog Comparison: Old → New

## Summary

| Metric | Old (Citadel) | New (skill-hub) |
|--------|--------------|-----------------|
| Total skills | 86 | 103 |
| Total lines | 24,968 | ~25,500 |
| Avg lines/skill | 290 | 248 |
| Consolidated clusters | 0 | 26 |
| Standalone skills | 86 | 77 |
| Summary headers | no | yes (26 skills) |
| Trigger deconfliction | no | yes (9 pairs) |
| Blind spots filled | no | yes (per cluster) |
| Usage-based tightenings | no | yes (5 from Pegasus/dqi) |

---

## 1. Skills that get BETTER (consolidated with more coverage)

These old skills are replaced by a single, richer consolidated skill.

### database-pro (695 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `sql-pro` | 171 | nothing | PostgreSQL tuning, cloud DB, NoSQL, time-series, multi-tenant |
| `sql-optimization-patterns` | 38 | nothing | merged into optimization section |
| `data-quality-frameworks` | 43 | nothing | merged into data-engineering-pro instead |

### data-engineering-pro (702 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `data-engineer` | 222 | nothing | dbt patterns, Dagster/Prefect, data mesh, feature stores, downstream impact awareness |
| `dbt-transformation-patterns` | 556 | some verbose examples | dbt CI, incremental strategies consolidated |
| `data-quality-frameworks` | 43 | nothing | Great Expectations + dbt tests unified |

### python-core (891 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `python-patterns` | 750 | redundant framework selection | Pydantic multi-model, CLI (Typer/Click), logging (structlog), property-based testing |
| `python-testing` | 816 | verbose examples | Hypothesis, snapshot testing, async testing consolidated |

### python-web-frameworks (886 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `django-patterns` | 734 | nothing significant | FastAPI + Django unified, Alembic migrations, API versioning, GraphQL (Strawberry) |
| `django-tdd` | 729 | redundant TDD steps | merged into testing-qa-suite |
| `django-verification` | 469 | redundant checklists | merged into verification-before-completion |

### react-development (780 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `frontend-patterns` | 642 | some generic patterns | React 19, Server Components, primitives-first rule, Storybook, design system integration |
| `next-best-practices` | 153 | nothing | merged into Next.js section |
| `vercel-react-best-practices` | 143 | nothing | merged |
| `vercel-composition-patterns` | 89 | nothing | merged |

### typescript-javascript (609 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `coding-standards` | 530 | generic style rules | Advanced types, Deno, module federation, compiler plugins |

### testing-qa-suite (826 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `tdd-workflow` | 410 | verbose walkthrough | Playwright E2E, API testing, mutation testing, property-based, performance testing unified |
| `e2e-testing` | 326 | nothing | merged |
| `ai-regression-testing` | 385 | AI-specific regression | general regression covered |
| `pypict` | 362 | pairwise detail | mentioned as technique, not full tool reference |

### code-review-suite (687 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `review` | 193 | nothing | adversarial debate mode, automated tooling (SonarQube), review metrics |
| `plankton-code-quality` | 239 | nothing | merged into quality checks |

### security-guardian (757 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `owasp-security` | 536 | verbose OWASP detail | STRIDE, supply chain, cloud IAM, RASP, dependency scanning, compliance |

### debugging-master (706 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `debugging-code` | 267 | nothing | Distributed tracing, serverless debugging, browser DevTools, performance profiling |
| `systematic-debugging` | 112 | nothing | merged as core methodology |

### architecture-planning (733 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `backend-patterns` | 598 | generic backend | C4 diagrams, EARS specs, DDD/CQRS, tech stack evaluation, UI wiring gates |

### documentation-suite (744 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `doc-gen` | 243 | nothing | EARS spec mining, runbooks, changelogs, Mermaid diagrams, onboarding docs |

### api-design-pro (753 lines) replaces:
| Old skill | Lines | What was lost | What was gained |
|-----------|-------|---------------|-----------------|
| `api-design` | 523 | nothing | GraphQL, AsyncAPI, API gateways, SDK generation |

### devops-infrastructure (802 lines) — NEW
No direct old equivalent. Covers CI/CD, Docker, K8s, Terraform, Helm, GitOps, service mesh, FinOps.

### observability-monitoring (709 lines) — NEW
No direct old equivalent. Covers Prometheus, Grafana, OTel, incident response, SLOs.

### Other consolidated skills — NEW (no old equivalent):
| New skill | Lines | Coverage |
|-----------|-------|----------|
| `agent-engineering-pro` | 625 | Multi-agent patterns, orchestration, guardrails |
| `memory-context-pro` | 627 | Agent memory, context persistence, compression |
| `frontend-ui-ux` | 661 | Design systems, a11y, animations, i18n, PWA |
| `fp-typescript` | 720 | fp-ts, Effect-TS, optics |
| `rag-search-pro` | 485 | RAG pipelines, embeddings, vector DBs, GraphRAG |
| `data-visualization-pro` | 683 | matplotlib, seaborn, plotly, Altair, dashboards |
| `code-quality-refactoring` | 472 | Refactoring, dead code, deps, post-merge consolidation |
| `git-workflow` | 567 | Worktrees, branch completion, changelog, releases |
| `product-management` | 654 | Strategy, OKRs, PRDs, agile, analytics, UX |
| `productivity-learning` | 410 | Content extraction, learning plans, Zettelkasten |
| `verification-before-completion` | 133 | Evidence-before-claims, feature completeness gate |

---

## 2. Skills that CARRY OVER unchanged

These exist in both old and new catalogs with similar content.

| Skill | Old lines | New lines | Notes |
|-------|-----------|-----------|-------|
| `brainstorming` | 164 | 164 | identical |
| `email-html-mjml` | 161 | 161 | identical |
| `financial-analyst` | 148 | 148 | identical |
| `pandas-pro` | 178 | 178 | identical |
| `varlock` | 433 | 134 | trimmed, core rules kept |
| `writing-skills` | 655 | 179 | trimmed, TDD-for-skills methodology kept |
| `session-log` | — | 103 | new standalone |

---

## 3. Skills that get REMOVED (no new equivalent)

### Absorbed into consolidated skills (redundant as standalone):
| Old skill | Lines | Absorbed into |
|-----------|-------|---------------|
| `sql-pro` | 171 | `database-pro` |
| `sql-optimization-patterns` | 38 | `database-pro` |
| `data-quality-frameworks` | 43 | `data-engineering-pro` |
| `data-engineer` | 222 | `data-engineering-pro` |
| `dbt-transformation-patterns` | 556 | `data-engineering-pro` |
| `python-patterns` | 750 | `python-core` |
| `python-testing` | 816 | `python-core` + `testing-qa-suite` |
| `django-patterns` | 734 | `python-web-frameworks` |
| `django-tdd` | 729 | `python-web-frameworks` + `testing-qa-suite` |
| `django-verification` | 469 | `verification-before-completion` |
| `frontend-patterns` | 642 | `react-development` |
| `next-best-practices` | 153 | `react-development` |
| `vercel-react-best-practices` | 143 | `react-development` |
| `vercel-composition-patterns` | 89 | `react-development` |
| `coding-standards` | 530 | `typescript-javascript` |
| `tdd-workflow` | 410 | `testing-qa-suite` |
| `e2e-testing` | 326 | `testing-qa-suite` |
| `ai-regression-testing` | 385 | `testing-qa-suite` |
| `pypict` | 362 | `testing-qa-suite` (mentioned) |
| `review` | 193 | `code-review-suite` |
| `plankton-code-quality` | 239 | `code-review-suite` |
| `owasp-security` | 536 | `security-guardian` |
| `debugging-code` | 267 | `debugging-master` |
| `systematic-debugging` | 112 | `debugging-master` |
| `backend-patterns` | 598 | `architecture-planning` |
| `api-design` | 523 | `api-design-pro` |
| `doc-gen` | 243 | `documentation-suite` |

### Citadel orchestration skills (PRESERVED via symlinks):
| Skill | Lines | Status |
|-------|-------|--------|
| `do` | 273 | **KEEP** — entry point router (updated routing table) |
| `marshal` | 153 | **KEEP** — session orchestrator |
| `archon` | 255 | **KEEP** — campaign agent |
| `fleet` | 346 | **KEEP** — parallel orchestrator |
| `architect` | 221 | **KEEP** — system design agent |
| `create-app` | 200 | **KEEP** — app scaffolding |
| `create-skill` | 344 | **KEEP** — skill creation |
| `experiment` | 130 | **KEEP** — optimization loops |
| `research` | 118 | **KEEP** — research agent |
| `research-fleet` | 182 | **KEEP** — parallel research |
| `setup` | 292 | **KEEP** — harness configuration |
| `scaffold` | 219 | **KEEP** — module scaffolding |
| `live-preview` | 144 | **KEEP** — visual preview |
| `postmortem` | 166 | **KEEP** — incident debrief |
| `design` | 172 | **KEEP** — design manifest |
| `qa` | 200 | **KEEP** — browser testing |
| `configure-ecc` | 367 | **KEEP** — harness config |
| `continuous-learning-v2` | 365 | **KEEP** — instinct system |
| `autopilot` | 111 | **KEEP** — intake processing |
| `session-handoff` | 52 | **KEEP** — session transfer |
| `test-gen` | 169 | **KEEP** — but overlaps with testing-qa-suite |
| `refactor` | 291 | **KEEP** — but overlaps with code-quality-refactoring |

### Dropped entirely (not in new catalog, not preserved):
| Old skill | Lines | Why dropped |
|-----------|-------|-------------|
| `browser-use` | 202 | npx skill, browser automation — niche |
| `clarify` | 181 | npx skill, prompt clarification — handled by Claude natively |
| `find-skills` | 142 | npx skill, skill discovery — replaced by skill-hub-mcp |
| `polish` | 201 | npx skill, code polish — absorbed into code-quality-refactoring |
| `shadcn` | 242 | npx skill, shadcn/ui — not in active stack |
| `tailwind-design-system` | 866 | npx skill, Tailwind — absorbed into frontend-ui-ux |
| `ui-ux-pro-max` | 658 | npx skill — absorbed into frontend-ui-ux |
| `web-artifacts-builder` | 73 | npx skill, web artifacts — niche |
| `supabase-postgres-best-practices` | 64 | Supabase-specific — not in stack |
| `iterative-retrieval` | 211 | RAG-specific — absorbed into rag-search-pro |
| `frontend-slides` | 184 | Slide generation — niche |
| `project-guidelines-example` | 349 | Example template — not a skill |
| `eval-harness` | 270 | Evaluation harness — absorbed into verification-before-completion |
| `skill-stocktake` | 193 | Inventory tool — replaced by skill-hub-mcp |
| `strategic-compact` | 131 | Context compression — absorbed into memory-context-pro |
| `verification-loop` | 126 | Verification — absorbed into verification-before-completion |
| `dispatching-parallel-agents` | 182 | Agent dispatch — absorbed into agent-engineering-pro |
| `subagent-driven-development` | 277 | Subagent patterns — absorbed into agent-engineering-pro |
| `executing-plans` | 70 | Plan execution — absorbed into architecture-planning |
| `writing-plans` | 145 | Plan writing — absorbed into architecture-planning |
| `finishing-a-development-branch` | 200 | Branch completion — absorbed into git-workflow |
| `ship-learn-next` | 326 | Learning plans — absorbed into productivity-learning |
| `article-extractor` | 369 | Content extraction — absorbed into productivity-learning |
| `youtube-transcript` | 415 | YouTube extraction — absorbed into productivity-learning |
| `csv-data-summarizer` | 149 | CSV analysis — absorbed into data-visualization-pro |
| `mcp-server-patterns` | 67 | MCP patterns — absorbed into mcp-developer standalone |
| `dbt-layered-architecture` | 779 | **NOTE: custom skill for DQI** |
| `financial-reconciliation` | 350 | **NOTE: custom skill for equity work** |
| `digievolve` | 164 | Pegasus-specific evolution — project-local |

---

## 4. RISK ITEMS — things to watch after swap

| Risk | Severity | Mitigation |
|------|----------|------------|
| `dbt-layered-architecture` (779 lines) is a custom DQI skill not in new catalog | **HIGH** | Copy to general_skills or keep as project-local skill |
| `financial-reconciliation` (350 lines) is a custom equity skill not in new catalog | **HIGH** | Copy to general_skills or keep as project-local skill |
| `test-gen` and `refactor` Citadel skills overlap with new consolidated skills | MEDIUM | Both fire on same triggers — may get contradictory advice |
| `tailwind-design-system` (866 lines) was detailed — `frontend-ui-ux` may be thinner on Tailwind | LOW | Tailwind specifics are in react-development primitives-first section |
| `pypict` pairwise testing detail was 362 lines — now a mention in testing-qa-suite | LOW | Original in promoted/ if needed |
| `digievolve` was Pegasus-specific — not in new catalog | LOW | Keep as project-local if still needed |

---

## 5. RECOMMENDED ACTIONS before swap

1. **Copy `dbt-layered-architecture` and `financial-reconciliation` to general_skills/** — these are custom skills critical to daily work
2. **Decide on `test-gen`/`refactor` overlap** — either remove Citadel versions or add "defer to testing-qa-suite/code-quality-refactoring" notes
3. **Check if `digievolve` is still needed** in project_pegasus
