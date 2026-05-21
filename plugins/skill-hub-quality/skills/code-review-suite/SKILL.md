---
name: code-review-suite
description: "Comprehensive code review specialist covering structured PR analysis, blast radius assessment, security scanning (OWASP Top 10, SQL injection, XSS, secrets), N+1 detection, breaking change detection, test coverage delta, feedback reception with YAGNI checks and pushback framework, self-review checklists, automated tooling integration (SonarQube, CodeQL, Semgrep), and multi-agent review orchestration. Use when reviewing pull requests, conducting code quality audits, requesting or receiving code reviews, identifying refactoring opportunities, or checking for security vulnerabilities."
metadata:
  domain: quality
  triggers: code review, PR review, pull request, review code, code quality, code audit, OWASP, security review, refactoring, blast radius, breaking change, feedback, YAGNI, SonarQube, CodeQL
  role: specialist
  scope: review
---

# Code Review Suite

Senior engineer conducting thorough, constructive code reviews that improve quality, share knowledge, and catch issues before they reach production.

## When to Use

- Reviewing pull requests or merge requests
- Conducting code quality or security audits
- Requesting a self-review before submitting code
- Receiving and processing review feedback
- Identifying refactoring opportunities or architectural concerns
- Integrating automated review tooling into CI/CD
- Onboarding new contributors who need thorough structured feedback

## Core Workflow

1. **Context** — read PR description and linked ticket; understand the problem being solved. Summarize the PR's intent in one sentence before proceeding. If you cannot, ask the author to clarify.
2. **Blast radius** — trace which files, services, shared contracts, and downstream consumers could be affected.
3. **Structure** — review architecture and design decisions. Does this follow existing patterns? Are new abstractions justified?
4. **Details** — check code quality, security (OWASP Top 10), and performance. Flag N+1 queries, hardcoded secrets, injection risks.
5. **Tests** — validate coverage delta and quality. Are edge cases covered? Do tests assert behavior, not implementation?
6. **Feedback** — produce the categorized report (Output Template). Surface critical issues immediately; do not wait until the end.

> **Disagreement handling:** If the author explained a non-obvious choice in comments, acknowledge their reasoning before suggesting an alternative. Never block on style preferences when a linter or formatter is configured.

## Blast Radius Analysis

For each changed file, trace impact before reviewing logic:

```bash
PR=123

# Fetch diff and metadata
gh pr view $PR --json title,body,labels,milestone | jq .
gh pr diff $PR --name-only
gh pr diff $PR > /tmp/pr-$PR.diff

# Find all files importing a changed module (TypeScript)
grep -r "from ['\"].*changed-module['\"]" src/ --include="*.ts" -l

# Cross-service scope (monorepo)
gh pr diff $PR --name-only | cut -d/ -f1-2 | sort -u

# Shared contracts touched
gh pr diff $PR --name-only | grep -E "types/|interfaces/|schemas/|models/"
```

**Blast radius severity:**
- CRITICAL — shared library, DB model, auth middleware, API contract
- HIGH — service used by >3 others, shared config, env vars
- MEDIUM — single service internal, utility function
- LOW — UI component, test file, docs

## Security Scan

Run these checks against the diff before diving into logic:

```bash
DIFF=/tmp/pr-$PR.diff

# SQL injection — raw string interpolation
grep -n "query\|execute\|raw(" $DIFF | grep -E '\$\{|f"|%s|format\('

# Hardcoded secrets
grep -nE "(password|secret|api_key|token|private_key)\s*=\s*['\"][^'\"]{8,}" $DIFF

# AWS key pattern
grep -nE "AKIA[0-9A-Z]{16}" $DIFF

# XSS vectors
grep -n "dangerouslySetInnerHTML\|innerHTML\s*=" $DIFF

# Auth bypass patterns
grep -n "bypass\|skip.*auth\|noauth\|TODO.*auth" $DIFF

# eval / exec
grep -nE "\beval\(|\bexec\(|\bsubprocess\.call\(" $DIFF

# Path traversal risk
grep -nE "path\.join\(.*req\.|readFile\(.*req\." $DIFF

# Secret scanning (TruffleHog)
trufflehog git file://. --json | jq '.[] | select(.Verified == true)'
```

**OWASP Top 10 checklist:**
- A01 Broken Access Control — missing authorization, IDOR vulnerabilities
- A02 Cryptographic Failures — weak hashing (MD5/SHA1), insecure RNG
- A03 Injection — SQL, NoSQL, command injection via taint analysis
- A05 Security Misconfiguration — default credentials, missing headers
- A07 Authentication Failures — weak session management, JWT issues
- A09 Logging Failures — sensitive data in logs (PII, tokens, passwords)

## Test Coverage Delta

```bash
# Count source vs test files changed
CHANGED_SRC=$(gh pr diff $PR --name-only | grep -vE "\.test\.|\.spec\.|__tests__")
CHANGED_TESTS=$(gh pr diff $PR --name-only | grep -E "\.test\.|\.spec\.|__tests__")

echo "Source files changed: $(echo "$CHANGED_SRC" | wc -w)"
echo "Test files changed:   $(echo "$CHANGED_TESTS" | wc -w)"

# Run coverage for changed files
npm test -- --coverage --changedSince=main 2>/dev/null | tail -20
pytest --cov --cov-report=term-missing 2>/dev/null | tail -20
```

**Coverage delta rules:**
- New function without tests → flag
- Deleted tests without deleted code → flag
- Coverage drop >5% → request changes
- Auth/payments code paths → require 100% coverage

## Breaking Change Detection

```bash
# REST route removals or renames
grep "^-" /tmp/pr-$PR.diff | grep -E "router\.(get|post|put|delete|patch)\("

# TypeScript interface removals
grep "^-" /tmp/pr-$PR.diff | grep -E "^-\s*(export\s+)?(interface|type) "

# DB destructive operations
grep -E "DROP TABLE|DROP COLUMN|ALTER.*NOT NULL|TRUNCATE" /tmp/pr-$PR.diff

# New env vars referenced (might be missing in prod)
grep "^+" /tmp/pr-$PR.diff | grep -oE "process\.env\.[A-Z_]+" | sort -u

# Removed env vars (could break running instances)
grep "^-" /tmp/pr-$PR.diff | grep -oE "process\.env\.[A-Z_]+" | sort -u
```

## Review Patterns (Quick Reference)

**N+1 Query:**
```python
# BAD: query inside loop
for user in users:
    orders = Order.objects.filter(user=user)  # N+1

# GOOD: prefetch in bulk
users = User.objects.prefetch_related('orders').all()
```

**SQL Injection:**
```python
# BAD: string interpolation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD: parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

**Magic Number:**
```python
# BAD
if status == 3: ...

# GOOD
ORDER_STATUS_SHIPPED = 3
if status == ORDER_STATUS_SHIPPED: ...
```

## 30-Item Review Checklist

```markdown
### Scope & Context
- [ ] PR title accurately describes the change
- [ ] PR description explains WHY, not just WHAT
- [ ] Linked Jira/Linear ticket exists and matches scope
- [ ] No unrelated changes (scope creep)
- [ ] Breaking changes documented in PR body

### Blast Radius
- [ ] All files importing changed modules identified
- [ ] Cross-service dependencies checked
- [ ] Shared types/interfaces/schemas reviewed for breakage
- [ ] New env vars documented in .env.example
- [ ] DB migrations are reversible (have down() / rollback)

### Security
- [ ] No hardcoded secrets or API keys
- [ ] SQL queries use parameterized inputs
- [ ] User inputs validated/sanitized before use
- [ ] Auth/authorization checks on all new endpoints
- [ ] No XSS vectors (innerHTML, dangerouslySetInnerHTML)
- [ ] New dependencies checked for known CVEs
- [ ] No sensitive data in logs (PII, tokens, passwords)
- [ ] CORS configured correctly for new endpoints

### Testing
- [ ] New public functions have unit tests
- [ ] Edge cases covered (empty, null, max values)
- [ ] Error paths tested (not just happy path)
- [ ] Integration tests for API endpoint changes
- [ ] Test names clearly describe what they verify

### Breaking Changes
- [ ] No API endpoints removed without deprecation notice
- [ ] No required fields added to existing API responses without versioning
- [ ] No DB columns removed without two-phase migration plan
- [ ] Backward-compatible for external API consumers

### Performance
- [ ] No N+1 query patterns introduced
- [ ] DB indexes added for new query patterns
- [ ] No unbounded loops on potentially large datasets
- [ ] No heavy new dependencies without justification
- [ ] Async operations correctly awaited
```

## Automated Tooling Integration

Integrate static analysis into CI/CD for continuous feedback:

```yaml
# .github/workflows/review.yml
jobs:
  static-analysis:
    steps:
      - name: SonarQube
        run: sonar-scanner -Dsonar.pullrequest.key=${{ github.event.number }}

      - name: Semgrep
        run: semgrep scan --config=auto --sarif --output=semgrep.sarif

      - name: Quality Gate
        run: |
          CRITICAL=$(jq '[.[] | select(.severity == "CRITICAL")] | length' review.json)
          if [ $CRITICAL -gt 0 ]; then echo "Found $CRITICAL critical issues"; exit 1; fi
```

**Tool selection by use case:**
- **SonarQube** — code smells, complexity, duplication, maintainability index
- **CodeQL** — deep vulnerability analysis (SQL injection, XSS, auth bypasses)
- **Semgrep** — organization-specific security rules and policies
- **Snyk/Dependabot** — supply chain security and CVE scanning
- **TruffleHog/GitGuardian** — secret detection in diffs and history

**Review routing by PR size:** >1000 lines → require human review; <200 lines security-sensitive → deep AI-assisted analysis; coverage gap >20% → route to test generation before approving.

## Receiving and Requesting Reviews

**When receiving feedback — response pattern:**
1. Read all feedback completely before implementing anything
2. Restate unclear requirements in your own words — ask before implementing
3. Verify suggestion against codebase reality (does it break anything? is it used?)
4. Implement one item at a time, test each, verify no regressions

**YAGNI check before implementing suggestions:**
```bash
grep -r "endpoint_or_function_name" src/ --include="*.ts"
# If unused: "This isn't called anywhere. Remove it (YAGNI)?"
```

**When to push back:** suggestion breaks existing functionality, reviewer lacks context, YAGNI applies, or conflicts with architectural decisions. Use technical reasoning, not defensiveness.

**When feedback is correct:**
```
"Fixed. [Brief description of what changed]"      # correct
"You're absolutely right!" / "Great point!"       # avoid
```

**Before submitting code for review (self-review checklist):**
1. Read your own diff as if you're the reviewer
2. Run all tests locally — never submit code that fails CI
3. Remove debug code, TODOs marked for follow-up, temporary comments
4. PR description explains WHY, not just WHAT was changed
5. Request review after each major task, before touching shared libraries, or when stuck

## Multi-Agent Review Orchestration

For large or high-stakes PRs, orchestrate specialized agents in parallel:

1. **Phase 1 (parallel):** Code quality analysis (SonarQube, complexity) + Architecture review (SOLID, boundaries, coupling)
2. **Phase 2 (parallel, uses Phase 1 findings):** Security vulnerability assessment + Performance & scalability analysis
3. **Phase 3:** Test coverage and quality review incorporating Phase 2 security and performance requirements
4. **Final:** Consolidated report with P0/P1/P2/P3 prioritization

**Priority levels:**
- **P0 — Block merge:** security vuln CVSS >7, data loss risk, auth bypass, compliance violation
- **P1 — Fix before release:** performance bottlenecks, missing critical test coverage, architectural anti-patterns
- **P2 — Next sprint:** non-critical optimizations, documentation gaps, refactoring opportunities
- **P3 — Backlog:** style violations, minor code smells, cosmetic improvements

## Constraints

**MUST DO**
- Summarize PR intent before reviewing (prevents false positives from misunderstanding)
- Provide specific, actionable feedback with code examples
- Praise good patterns — specific praise improves team culture
- Prioritize feedback: critical → major → minor
- Review tests as thoroughly as production code
- Check CI status before reviewing — don't review code that fails to build

**MUST NOT**
- Nitpick style when a linter/formatter is configured
- Block on personal preferences
- Review without understanding the intent
- Skip blast radius analysis for changes in shared modules
- Trickle feedback across multiple rounds — batch all comments in one pass

## Output Template

```
## PR Review: [PR Title] (#NUMBER)

Blast Radius: HIGH — changes lib/auth used by 5 services
Security: 1 finding (medium severity)
Tests: Coverage delta +2% (adequate)
Breaking Changes: None detected

--- MUST FIX (Blocking) ---

1. SQL Injection risk in src/db/users.ts:42
   Raw string interpolation in WHERE clause.
   Fix: db.query("SELECT * WHERE id = $1", [userId])

--- SHOULD FIX (Non-blocking) ---

2. Missing auth check on POST /api/admin/reset
   No role verification before destructive operation.

--- SUGGESTIONS ---

3. N+1 pattern in src/services/reports.ts:88
   findUser() called inside results.map() — batch with findManyUsers(ids)

--- LOOKS GOOD ---
- Test coverage for new auth flow is thorough
- DB migration includes proper down() rollback
- Error handling consistent with existing codebase patterns

Verdict: REQUEST_CHANGES

→ For design-level challenge (not defects), invoke `adversarial-review` next.
  Defects are about what went wrong in the implementation; adversarial review
  challenges whether the design itself was the right call.
```

## Paired Skill — adversarial-review

`code-review-suite` finds defects in code that was built. `adversarial-review` challenges the design decisions that *produced* the code. They are complementary and designed to fire together: when the user invokes `/review`, both skills match and the router suggests the chain.

| Skill | Catches | Output |
|-------|---------|--------|
| `code-review-suite` (this skill) | Bugs, security holes, performance cliffs, convention drift | P0/P1/P2/P3 findings list |
| `adversarial-review` | Unjustified design choices, hidden assumptions, most-likely-failure-point | Refined design + 3 severity-rated concerns + mitigations |

For trivial PRs (single-line, lint cleanup, doc fix), invoke only this skill. For load-bearing or hard-to-reverse PRs, invoke both — defect-finding first, then design challenge against any patterns the defects reveal.

