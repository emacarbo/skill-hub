# Skill Library Swap Report

**Date:** 2026-04-03
**Status:** Pre-swap analysis (new library staged, not yet synced)

---

## 1. Inventory Summary

### OLD Catalog (`~/.claude/skills/`) — Currently Active

| Category | Count | Lines | Description |
|----------|-------|-------|-------------|
| Local domain skills | 50 | 17,160 | Standalone knowledge skills (sql-pro, python-patterns, etc.) |
| Citadel orchestration | 24 | 4,849 | Symlinks to `/dev/Citadel/` (/do, /marshal, /fleet, etc.) |
| npx community skills | 12 | 3,014 | Symlinks to `~/.agents/skills/` (tailwind, shadcn, etc.) |
| **Total** | **86** | **25,023** | |

**Avg lines/skill:** 291

### NEW Catalog (`skill-hub/agents/general_skills/`) — Staged

| Category | Count | Lines | Description |
|----------|-------|-------|-------------|
| Consolidated domain clusters | 50 | 21,982 | 26 deep clusters + 24 focused standalones |
| Alireza standalones | 24 | 5,882 | Promoted from alireza collection |
| Antigravity standalones | 24 | 5,148 | Promoted from antigravity collection |
| Wshobson standalones | 6 | 532 | Promoted from wshobson collection (95% trimmed) |
| Lifecycle tools | 5 | 236 | skill-eval, skill-sync, skill-promote, etc. |
| Session log | 1 | 103 | session-log utility |
| **Total** | **110** | **33,883** | |

**Avg lines/skill:** 308

**Note:** The 24 Citadel orchestration skills are NOT in general_skills — they stay as Citadel symlinks. The new catalog replaces only the 50 local domain skills + 12 npx skills (62 total, 20,174 lines).

---

## 2. What Gets Replaced (Old -> New)

### 2a. Absorbed Into Consolidated Clusters (28 old skills -> 13 new clusters)

| Old Skill | Lines | Absorbed Into | New Lines |
|-----------|-------|---------------|-----------|
| `sql-pro` | 171 | `database-pro` | 695 |
| `sql-optimization-patterns` | 38 | `database-pro` | (same) |
| `data-quality-frameworks` | 43 | `data-engineering-pro` | 702 |
| `data-engineer` | 222 | `data-engineering-pro` | (same) |
| `dbt-transformation-patterns` | 556 | `data-engineering-pro` | (same) |
| `python-patterns` | 750 | `python-core` | 891 |
| `python-testing` | 816 | `python-core` + `testing-qa-suite` | 891 + 826 |
| `django-patterns` | 734 | `python-web-frameworks` | 886 |
| `django-tdd` | 729 | `python-web-frameworks` + `testing-qa-suite` | (same) |
| `django-verification` | 469 | `verification-before-completion` | 133 |
| `frontend-patterns` | 642 | `react-development` | 780 |
| `coding-standards` | 530 | `typescript-javascript` | 609 |
| `tdd-workflow` | 410 | `testing-qa-suite` | 826 |
| `e2e-testing` | 326 | `testing-qa-suite` | (same) |
| `ai-regression-testing` | 385 | `testing-qa-suite` | (same) |
| `pypict` | 362 | `testing-qa-suite` | (mentioned) |
| `review` | 193 | `code-review-suite` | 687 |
| `plankton-code-quality` | 239 | `code-review-suite` | (same) |
| `owasp-security` | 536 | `security-guardian` | 757 |
| `debugging-code` | 267 | `debugging-master` | 706 |
| `systematic-debugging` | 112 | `debugging-master` | (same) |
| `backend-patterns` | 598 | `architecture-planning` | 733 |
| `api-design` | 523 | `api-design-pro` | 753 |
| `doc-gen` | 243 | `documentation-suite` | 744 |
| `next-best-practices` | 153 | `react-development` | (same) |
| `vercel-react-best-practices` | 143 | `react-development` | (same) |
| `vercel-composition-patterns` | 89 | `react-development` | (same) |
| `polars` | 386 | `antigravity-polars` | 386 |

**Old total:** 10,230 lines across 28 skills
**New total:** ~9,804 lines across 13 clusters (more coverage, less redundancy)

### 2b. Carried Over (Unchanged or Trimmed)

| Skill | Old Lines | New Lines | Change |
|-------|-----------|-----------|--------|
| `brainstorming` | 164 | 164 | identical |
| `email-html-mjml` | 161 | 161 | identical |
| `pandas-pro` | 178 | 178 | identical |
| `varlock` | 433 | 134 | trimmed -69% |
| `writing-skills` | 655 | 179 | trimmed -73% |
| `dbt-layered-architecture` | 779 | 779 | identical (custom DQI) |
| `financial-reconciliation` | 350 | 350 | identical (custom equity) |
| `financial-analyst` | 148 | 148 | identical (as alireza-financial-analyst) |

### 2c. Dropped Entirely (22 old skills, no direct replacement)

| Old Skill | Lines | Why Dropped |
|-----------|-------|-------------|
| `browser-use` | 202 | npx, niche browser automation |
| `clarify` | 181 | Claude handles prompt clarification natively |
| `find-skills` | 142 | Replaced by skill-hub-mcp |
| `polish` | 201 | Absorbed into `code-quality-refactoring` |
| `shadcn` | 242 | Not in active stack |
| `tailwind-design-system` | 866 | Absorbed into `frontend-ui-ux` + `react-development` |
| `ui-ux-pro-max` | 658 | Absorbed into `frontend-ui-ux` |
| `web-artifacts-builder` | 73 | Niche |
| `supabase-postgres-best-practices` | 64 | Not in stack |
| `iterative-retrieval` | 211 | Absorbed into `rag-search-pro` |
| `frontend-slides` | 184 | Niche |
| `project-guidelines-example` | 349 | Template, not a skill |
| `eval-harness` | 270 | Absorbed into `verification-before-completion` |
| `skill-stocktake` | 193 | Replaced by skill-hub-mcp |
| `strategic-compact` | 131 | Absorbed into `memory-context-pro` |
| `verification-loop` | 126 | Absorbed into `verification-before-completion` |
| `dispatching-parallel-agents` | 182 | Absorbed into `agent-engineering-pro` |
| `subagent-driven-development` | 277 | Absorbed into `agent-engineering-pro` |
| `executing-plans` | 70 | Absorbed into `architecture-planning` |
| `writing-plans` | 145 | Absorbed into `architecture-planning` |
| `finishing-a-development-branch` | 200 | Absorbed into `git-workflow` |
| `digievolve` | 164 | Pegasus-specific, project-local |
| `csv-data-summarizer` | 149 | Absorbed into `data-visualization-pro` |
| `ship-learn-next` | 326 | Absorbed into `productivity-learning` |
| `article-extractor` | 369 | Absorbed into `productivity-learning` |
| `youtube-transcript` | 415 | Absorbed into `productivity-learning` |
| `mcp-server-patterns` | 67 | Absorbed into `mcp-developer` |

**Dropped total:** 5,857 lines. All are either absorbed or irrelevant to active stack.

---

## 3. Net-New In New Catalog (No Old Equivalent)

### 3a. Consolidated Clusters (new domains)

| New Skill | Lines | Coverage |
|-----------|-------|----------|
| `devops-infrastructure` | 802 | CI/CD, Docker, K8s, Terraform, Helm, GitOps, FinOps |
| `observability-monitoring` | 709 | Prometheus, Grafana, OTel, SLOs, incident response |
| `agent-engineering-pro` | 625 | Multi-agent patterns, orchestration, guardrails |
| `memory-context-pro` | 627 | Agent memory, context persistence, compression |
| `frontend-ui-ux` | 661 | Design systems, a11y, animations, i18n, PWA |
| `fp-typescript` | 720 | fp-ts, Effect-TS, optics, algebraic types |
| `rag-search-pro` | 485 | RAG pipelines, embeddings, vector DBs, GraphRAG |
| `data-visualization-pro` | 683 | matplotlib, seaborn, plotly, Altair, dashboards |
| `code-quality-refactoring` | 472 | Refactoring, dead code, deps, post-merge consolidation |
| `git-workflow` | 567 | Worktrees, branch completion, changelog, releases |
| `product-management` | 654 | Strategy, OKRs, PRDs, agile, analytics |
| `productivity-learning` | 410 | Content extraction, learning plans, Zettelkasten |
| `verification-before-completion` | 133 | Evidence-before-claims gate, feature completeness |

**New cluster total:** 7,548 lines — entirely new domain coverage.

### 3b. Promoted Standalones (54 skills from community collections)

| Source | Count | Lines | Highlights |
|--------|-------|-------|------------|
| Alireza | 24 | 5,882 | AWS architect, Jira/Confluence, ML engineer, prompt engineering, Stripe, SaaS scaffolder |
| Antigravity | 24 | 5,148 | Django perf/access review, Prisma, Drizzle ORM, Pydantic AI, Hono, scanpy, polars |
| Wshobson | 6 | 532 | Shell scripting, systems programming, game dev, payments |

**Promoted total:** 11,562 lines across 54 skills.

### 3c. New Standalones (written or adapted)

| New Skill | Lines | Coverage |
|-----------|-------|----------|
| `cli-developer` | 113 | CLI app patterns |
| `fullstack-guardian` | 105 | Fullstack integration checks |
| `game-developer` | 161 | Game development patterns |
| `golang-pro` | 122 | Go-specific patterns |
| `java-architect` | 132 | Java/Spring patterns |
| `laravel-specialist` | 262 | Laravel/PHP framework |
| `legacy-modernizer` | 137 | Legacy code migration |
| `mcp-developer` | 143 | MCP server development |
| `nestjs-expert` | 206 | NestJS patterns |
| `php-pro` | 206 | PHP patterns |
| `rails-expert` | 154 | Ruby on Rails patterns |
| `rust-engineer` | 167 | Rust patterns |
| `spark-engineer` | 148 | Apache Spark |
| `spring-boot-engineer` | 195 | Spring Boot |
| `sre-engineer` | 181 | SRE practices |
| `the-fool` | 120 | Creative problem solving |
| `websocket-engineer` | 168 | WebSocket patterns |
| `session-log` | 103 | Session logging utility |

---

## 4. What Stays Untouched

The **24 Citadel orchestration skills** are preserved as-is (symlinks to `/dev/Citadel/`):

`architect`, `archon`, `autopilot`, `create-app`, `create-skill`, `design`, `do`, `doc-gen`, `experiment`, `fleet`, `live-preview`, `marshal`, `postmortem`, `prd`, `qa`, `refactor`, `research`, `research-fleet`, `review`, `scaffold`, `session-handoff`, `setup`, `systematic-debugging`, `test-gen`

**4,849 lines** — no changes needed. The sync script explicitly preserves these.

---

## 5. Expected Impact

### 5a. Coverage Expansion

| Domain | Old | New | Delta |
|--------|-----|-----|-------|
| Python (core + web) | 2 skills, 1,566 lines | 2 clusters, 1,777 lines | +14% depth, unified |
| Testing/QA | 4 skills, 1,937 lines | 1 cluster, 826 lines | -57% lines, +coverage (Playwright, mutation, perf) |
| Frontend/React | 4 skills, 1,027 lines | 2 clusters, 1,441 lines | +40% (Server Components, primitives-first) |
| Data engineering | 3 skills, 821 lines | 2 clusters, 1,481 lines | +80% (dbt CI, data mesh, feature stores) |
| Database | 2 skills, 209 lines | 1 cluster, 695 lines | +232% (PostgreSQL tuning, NoSQL, time-series) |
| Security | 1 skill, 536 lines | 1 cluster, 757 lines | +41% (STRIDE, supply chain, cloud IAM) |
| DevOps/Infra | 0 skills | 1 cluster, 802 lines | **NEW** |
| Observability | 0 skills | 1 cluster, 709 lines | **NEW** |
| Agent engineering | 2 skills, 459 lines | 1 cluster, 625 lines | +36% (guardrails, multi-agent) |
| API design | 1 skill, 523 lines | 1 cluster, 753 lines | +44% (GraphQL, AsyncAPI, SDK gen) |
| ML/Data science | 0 skills | 5 standalones, ~918 lines | **NEW** (via promoted) |
| Atlassian/PM tools | 0 skills | 4 standalones, ~1,166 lines | **NEW** (via promoted) |

### 5b. Redundancy Elimination

| Old Problem | Resolution |
|-------------|-----------|
| `python-patterns` (750) + `python-testing` (816) = 1,566 lines with overlap | `python-core` (891) = unified, 43% smaller |
| `django-patterns` (734) + `django-tdd` (729) + `django-verification` (469) = 1,932 lines | `python-web-frameworks` (886) = unified, 54% smaller |
| `frontend-patterns` (642) + 3 Vercel skills (385) = 1,027 lines | `react-development` (780) = unified, 24% smaller |
| `tdd-workflow` (410) + `e2e-testing` (326) + `ai-regression` (385) + `pypict` (362) = 1,483 | `testing-qa-suite` (826) = unified, 44% smaller |
| `dispatching-parallel-agents` + `subagent-driven-development` = 459 lines | `agent-engineering-pro` (625) = unified + guardrails |

### 5c. Per-Task Context Loading

**Old behavior:** `/do "fix the Django auth bug"` could trigger `django-patterns` (734) + `django-tdd` (729) + `python-patterns` (750) + `owasp-security` (536) = **2,749 lines loaded**.

**New behavior:** Same trigger loads `python-web-frameworks` (886) + `security-guardian` summary header (~30 lines, full load only if security-relevant) = **~916 lines loaded**.

**Estimated context savings per task: 50-65%** thanks to consolidation + summary headers.

### 5d. Token Cost Reduction (Model Routing)

The refined model routing (applied today) shifts:
- Research/investigation: opus -> sonnet (saves ~3x per research agent)
- Build fixes: haiku -> sonnet (prevents misdiagnosis, slight cost increase)
- Lint/format: stays haiku (cheapest tier for zero-ambiguity work)

**Net effect:** Most sub-agent work runs on sonnet. Opus reserved for planning + review only. Estimated **20-30% reduction** in per-session sub-agent costs.

---

## 6. Risk Assessment

### HIGH Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Total line count +35%** (25,023 -> 33,883) | More skills compete for context window if multiple trigger simultaneously | Summary headers prevent full loads; deconflicted triggers reduce false positives. Monitor context usage in first week. |
| **`test-gen` / `refactor` overlap** with new `testing-qa-suite` / `code-quality-refactoring` | Contradictory advice when both old Citadel skill and new cluster fire on same trigger | Decision needed: either remove Citadel versions or add "defer to X" notes. Currently unresolved. |

### MEDIUM Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| **54 promoted standalones untested** in real workflows | May contain incorrect patterns, outdated APIs, or conflict with consolidated clusters | Standalones are lower-priority triggers; skill-hub-mcp `eval_skill` can flag staleness. Review after 2 weeks. |
| **Tailwind depth reduced** (866 -> mentioned in `frontend-ui-ux` + `react-development`) | Less Tailwind-specific guidance | Tailwind patterns are in react-development primitives-first section. If insufficient, restore as standalone. |
| **pypict detail lost** (362 lines -> mention in `testing-qa-suite`) | Pairwise testing methodology less detailed | Original preserved in promoted/ archive. Restore if needed for DQI work. |
| **`configure-ecc` and `continuous-learning-v2`** are old Citadel skills not in either catalog | These local skills (367 + 365 lines) are not Citadel symlinks and not in new catalog | They exist in `~/.claude/skills/` as local dirs. Sync script should preserve non-symlink non-replaced skills, or they'll be lost. **Verify sync script behavior.** |

### LOW Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| `digievolve` dropped | Pegasus evolution pattern lost | Keep as project-local if still needed |
| Lifecycle tools (skill-eval, skill-sync, etc.) are thin | May not be useful as standalone skills | They supplement skill-hub-mcp, not replace it |
| Community standalones may overlap with consolidated clusters | e.g., `antigravity-django-perf-review` vs `python-web-frameworks` | Trigger deconfliction already applied to consolidated clusters; standalones have lower trigger priority |

---

## 7. Migration Checklist (Pre-Swap)

- [x] All 26 consolidated clusters written with summary headers
- [x] Trigger deconfliction applied (9 pairs resolved)
- [x] Custom skills preserved: `dbt-layered-architecture`, `financial-reconciliation`
- [x] Model routing tables updated across /do, /marshal, /fleet, CLAUDE.md
- [x] token-savior rule added to global CLAUDE.md
- [x] Usage-based tightenings applied (5 from Pegasus/DQI feedback)
- [x] **test-gen / refactor**: KEEP both — they're action skills (executable workflows), not knowledge skills. They complement, not overlap, the new consolidated clusters.
- [x] **configure-ecc / continuous-learning-v2**: Already in sync script PRESERVE list. Safe.
- [x] **digievolve**: DROP — redundant with `/create-skill` (Citadel). Same workflow, less confusion.
- [ ] Install 14 new commands from `agents/claude/commands-new/`
- [ ] Run `sync-skills.sh --dry-run` to verify symlink plan
- [ ] Run `sync-skills.sh` to execute swap
- [ ] Validate: run `/do status` and `/do --list` post-swap
- [ ] Monitor context usage for 1 week post-swap

---

## 8. Numbers At A Glance

| Metric | Old | New | Change |
|--------|-----|-----|--------|
| Total skills | 86 | 110 (+24 Citadel) = 134 | +56% |
| Domain skills (excl. orchestration) | 62 | 110 | +77% |
| Total lines (domain only) | 20,174 | 33,883 | +68% |
| Consolidated clusters | 0 | 26 | **NEW** |
| Net-new domains covered | 0 | 7 (DevOps, Observability, Agent Eng, RAG, DataViz, FP-TS, Product Mgmt) | **NEW** |
| Redundant skill pairs | 14+ | 0 (consolidated) | eliminated |
| Summary headers for lazy-loading | 0 | 26 | **NEW** |
| Trigger deconflictions | 0 | 9 pairs | **NEW** |
| Usage-based tightenings | 0 | 5 | **NEW** |
| Custom project skills preserved | 2 | 2 | safe |
| Skills dropped entirely | 0 | 27 old skills (absorbed) | cleanup |
| Avg lines per consolidated cluster | n/a | 692 | deep coverage |
| Avg lines per standalone | 291 | 182 | -37% (trimmed) |
| Estimated context savings per task | baseline | 50-65% | significant |
