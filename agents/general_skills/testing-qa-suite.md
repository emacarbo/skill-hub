---
name: testing-qa-suite
description: "Comprehensive testing specialist covering TDD iron-law workflows, unit/integration/E2E automation, Playwright browser testing, API contract testing, coverage analysis (LCOV/JSON/XML), pairwise combinatorial generation, performance testing with k6/Artillery, mutation testing, and property-based testing. Use when writing tests, setting up test infrastructure, practicing TDD red-green-refactor, analyzing coverage gaps, debugging flaky tests, generating API test suites, or designing quality strategies across Jest, Pytest, JUnit, Vitest, and Playwright."
metadata:
  domain: quality
  triggers: test, testing, TDD, unit test, integration test, E2E, coverage, Playwright, Jest, pytest, JUnit, Vitest, API test, contract test, performance test, flaky test, test strategy, regression, quality gate, pairwise, mutation testing, property-based testing
  role: specialist
  scope: testing
---

# Testing & QA Suite

Comprehensive testing specialist enforcing test-first discipline across functional, performance, and API quality concerns — from TDD iron laws to Playwright E2E infrastructure to pairwise combinatorial generation.

## When to Use

- Writing unit, integration, or E2E tests in any framework
- Practicing or enforcing TDD red-green-refactor
- Analyzing coverage gaps and surfacing uncovered paths
- Setting up Playwright for browser/E2E automation
- Generating API test suites with auth, validation, and error matrices
- Debugging or stabilizing flaky tests
- Designing test strategy, automation frameworks, or quality gates
- Running performance tests (k6, Artillery) or mutation testing

## Core Workflow

1. **Define scope** — identify test type (unit/integration/E2E/performance), target framework, and coverage goal
2. **Red — write failing tests** — tests MUST fail before writing any implementation; verify failure is for the right reason, not a typo
3. **Green — minimal implementation** — write the least code that makes tests pass; no over-engineering
4. **Refactor** — clean up while keeping all tests green; never skip this phase
5. **Verify coverage** — parse LCOV/JSON/XML reports, surface P0/P1/P2 gaps, ensure threshold (typically 80%+) is met before closing

## TDD Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

**Red flags — stop and restart TDD:**
- Test passes immediately after writing it (you're testing existing behavior)
- "I'll add tests after" — tests-after verify what you built, not what's required
- "Just this once" — that's rationalization
- Kept implementation as "reference" while writing tests — delete means delete

**Verification checklist per cycle:**
- [ ] Test written before implementation
- [ ] Test failed for expected reason (missing feature, not typo)
- [ ] Minimal code written to pass
- [ ] All tests still green after refactor
- [ ] No test modified to make it pass

## Unit Testing Patterns

**Jest/Vitest (TypeScript/JavaScript):**
```typescript
describe('calculateDiscount', () => {
  it('applies 10% for premium users', () => {
    expect(calculateDiscount({ price: 100, tier: 'premium' })).toBe(90);
  });

  it('throws on negative price', () => {
    expect(() => calculateDiscount({ price: -1, tier: 'standard' }))
      .toThrow('Price must be non-negative');
  });
});
```

**Pytest (Python):**
```python
class TestDivide:
    def test_divide_positive_numbers(self):
        assert divide(10, 2) == 5.0

    def test_divide_by_zero_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
```

**React Testing Library (React/Next.js components):**
```typescript
describe('Button', () => {
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

// Preferred RTL queries (in priority order)
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText(/email/i)
screen.getByTestId('custom-element')  // last resort
```

## Coverage Analysis

```bash
# Jest/Istanbul
npm test -- --coverage --coverageReporters=json,lcov

# Pytest
pytest --cov --cov-report=lcov:lcov.info --cov-report=json

# Enforce threshold
python scripts/coverage_analyzer.py coverage/coverage-final.json --threshold 80
```

**Coverage gap priority tiers:**
- **P0 — Critical** (0% coverage on error/auth paths) — fix immediately
- **P1 — High** (core logic branches uncovered) — fix before release
- **P2 — Low-risk** (utility helpers) — track in backlog

**Jest threshold config:**
```javascript
coverageThreshold: {
  global: { branches: 80, functions: 80, lines: 80, statements: 80 }
}
```

## Playwright E2E Testing

**Golden Rules (Non-Negotiable):**
1. `getByRole()` over CSS/XPath — resilient to markup changes
2. Never `page.waitForTimeout()` — use web-first assertions
3. `expect(locator)` auto-retries; `expect(await locator.textContent())` does not
4. Isolate every test — no shared state between tests
5. `baseURL` in config — zero hardcoded URLs
6. Retries: `2` in CI, `0` locally; traces: `'on-first-retry'`
7. Fixtures over globals — share state via `test.extend()`
8. Mock external services only — never mock your own app

**Locator priority:**
```typescript
page.getByRole('button', { name: 'Submit' })    // 1. Role (default)
page.getByLabel('Email address')                  // 2. Label (form fields)
page.getByText('Welcome back')                    // 3. Text
page.getByTestId('checkout-summary')              // 4. Test ID (last semantic)
page.locator('.legacy-widget')                    // 5. CSS (last resort)
```

**Page Object Model:**
```typescript
export class LoginPage {
  constructor(readonly page: Page) {}
  readonly emailInput = this.page.getByLabel('Email address');
  readonly submitButton = this.page.getByRole('button', { name: 'Sign in' });

  async goto() { await this.page.goto('/login'); }
  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.submitButton.click();
  }
}
```

**Debugging flaky tests:**
```bash
# Reproduce consistently
npx playwright test <file> --repeat-each=10 --trace=on
npx playwright show-trace test-results/.../trace.zip

# Replace arbitrary sleep with proper wait
# BAD:  await page.waitForTimeout(2000);
# GOOD: await expect(page.getByRole('button', { name: 'Save' })).toBeVisible();
```

## API Integration Testing

Scan route definitions and auto-generate test suites covering auth, validation, and error codes.

**Auth test matrix (every authenticated endpoint):**

| Test Case | Expected Status |
|-----------|----------------|
| No Authorization header | 401 |
| Expired JWT token | 401 |
| Valid token, wrong role | 403 |
| Valid token, correct role | 2xx |

**Input validation matrix (POST/PUT/PATCH with body):**

| Test Case | Expected |
|-----------|----------|
| Empty body `{}` | 400 or 422 |
| Missing required fields (one at a time) | 400 or 422 |
| Boundary: value at max+1 | 400 or 422 |
| SQL injection payload | 400 or 200 (sanitized) |

**Route detection (Next.js App Router):**
```bash
find ./app/api -name "route.ts" | while read f; do
  route=$(echo $f | sed 's|./app||;s|/route.ts||')
  methods=$(grep -oE "export (async )?function (GET|POST|PUT|PATCH|DELETE)" "$f" | \
    grep -oE "(GET|POST|PUT|PATCH|DELETE)")
  echo "$methods $route"
done
```

**Common pitfalls:**
- Test only happy paths — 80% of bugs live in error paths; test those first
- Hardcoded test data IDs — use factories/fixtures; IDs change between environments
- Shared state between tests — always clean up in `afterEach`/`afterAll`
- Not testing token expiry separately from invalid tokens

## Pairwise / Combinatorial Testing

When inputs have many combinations, pairwise (t-way) combinatorial generation covers all 2-way parameter interactions with a minimal test set — typically 60-80% fewer cases than exhaustive testing with equivalent defect detection.

**When to apply:** 4+ independent fields, configuration matrices (OS x browser x locale), API endpoints with multiple optional parameters, feature flag combinations.

**Concept:**
```
# Parameters and values
Browser: Chrome, Firefox, Safari
OS:      Windows, macOS, Linux
Network: Fast, Slow, Offline
Auth:    Logged-in, Anonymous

# Pairwise → ~9 test cases instead of 3×3×3×2 = 54 exhaustive cases
# Tools: pypict (Python), PICT (Microsoft), fast-check combinatorial mode
```

## Performance Testing

Measure before optimizing. Never optimize blindly.

```bash
# k6 load test
k6 run --vus 50 --duration 60s load-test.js

# Artillery
artillery run scenario.yml
```

**Before/after documentation:**
```
| Metric       | Before  | After  | Delta  |
|--------------|---------|--------|--------|
| P50 latency  | 480ms   | 48ms   | -90%   |
| P99 latency  | 3,100ms | 280ms  | -91%   |
| RPS @ 50 VUs | 42      | 380    | +804%  |
```

Set performance budgets in CI: `p(95) < 200ms` as k6 threshold.

## Advanced Testing Techniques

**Mutation testing** — verify tests actually catch real bugs, not just achieve coverage lines:
- JavaScript/TypeScript: Stryker (`npx stryker run`)
- Python: mutmut (`mutmut run`)
- Target mutation score: >60% for core business logic
- Low score means tests pass even when logic is broken — rewrite those tests

**Property-based testing** — generate random inputs to find edge cases automatically:
- Python: Hypothesis (`@given(st.integers(), st.text())`)
- JavaScript: fast-check (`fc.property(fc.integer(), fc.string(), ...)`)
- Best for: pure functions, parsers, serialization/deserialization, math

**Database and migration testing:**
- Seed minimal data — create only what the test needs, never the full DB
- Test migration reversibility: `down()` must restore previous schema state exactly
- Verify no data loss after destructive migrations with before/after row counts
- Run migrations against production-size data volumes in CI to catch slow-migration risk

## API Mocking

```typescript
// MSW (Mock Service Worker) — recommended for React/Next.js apps
const server = setupServer(
  rest.get('/api/users', (req, res, ctx) =>
    res(ctx.json([{ id: 1, name: 'Alice' }]))
  )
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**Mock design rules:** label endpoints clearly, never use real secrets/PII, simulate realistic latency and error rates, validate mock schema matches production contract.

## Constraints

**MUST DO**
- Test happy paths AND all error/edge cases (empty, null, boundary values)
- Mock external dependencies — never call real APIs or databases in unit tests
- Use meaningful test descriptions that read as plain-English specifications
- Assert specific outcomes, not just truthiness
- Watch each test fail before implementing — confirms the test works
- Keep tests independent — each must run in isolation and in any order

**MUST NOT**
- Write implementation before the failing test exists and has been seen failing
- Test implementation details (internal method calls) — test observable behavior
- Use production data in tests — use fixtures or factories
- Ignore or disable flaky tests without diagnosing the root cause
- Skip refactor phase after going green

## Output Templates

**Test plan:** scope + approach, test cases with expected outcomes, coverage analysis, findings with severity (Critical/High/Medium/Low), specific fix recommendations.

**Coverage report:** overall %, P0/P1/P2 gap list, recommended next tests to reach threshold.

**Flaky test diagnosis:** reproduction steps, root cause category (timing/isolation/environment/infrastructure), targeted fix, verification command.
