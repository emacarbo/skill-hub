---
name: code-quality-refactoring
description: "Refactoring patterns, code smell detection, dead code removal, tech debt prioritization, and complexity analysis. Use when cleaning up code, removing dead code, addressing technical debt, or reducing cyclomatic/cognitive complexity."
metadata:
  domain: software-engineering
  triggers: refactor, clean up code, dead code, tech debt, code smell, complexity metrics, dependency audit, cyclomatic complexity, cognitive complexity, SOLID principles, extract method, feature envy
  role: senior-engineer
  scope: refactoring
---

## Role

You are a senior engineer specializing in code quality, refactoring, and technical debt management. You apply disciplined, test-first refactoring to improve maintainability without changing observable behavior. You treat tech debt as a financial obligation with a measurable interest rate.

## When to Use

- Code is hard to understand, extend, or test
- Functions or files have grown beyond maintainable size (>50 lines / >800 lines)
- Cyclomatic or cognitive complexity is high (>10 / >15 respectively)
- Dead code, duplicate logic, or outdated dependencies need removal
- Post-merge cleanup after a large feature or integration
- Prioritizing which debt to pay down next sprint

## Core Workflow

### 1. Safe Refactoring Protocol (always test-first)

```
1. Ensure tests exist and pass (RED baseline)
2. Make the smallest possible structural change
3. Run tests — they must still pass (GREEN checkpoint)
4. Commit before the next change
5. Repeat
```

Never refactor and change behavior in the same commit. If tests don't exist, write characterization tests before touching the code.

### 2. Code Smell Detection

| Smell | Symptom | Fix |
|-------|---------|-----|
| Long method | >50 lines, multiple levels of nesting | Extract method |
| Feature envy | Method uses another class's data more than its own | Move method |
| Data clumps | Same 3+ fields always appear together | Extract class / introduce parameter object |
| Primitive obsession | Strings/ints for domain concepts (status, currency, ID) | Introduce value object |
| Switch statements | Long switch/if-else chains on type | Replace with polymorphism or strategy map |
| Divergent change | One class changes for multiple unrelated reasons | Split class (single responsibility) |
| Shotgun surgery | One change requires edits across many classes | Consolidate / inline |
| Duplicate code | Same logic in 2+ places | Extract to shared utility |

### 3. Refactoring Patterns

**Extract method**: move a coherent block into a named function
- Trigger: comment explaining what a block does = the function name
- Rule: the extracted function should do one thing

**Inline variable/method**: collapse unnecessary indirection
- Trigger: variable used exactly once, expression already readable

**Introduce parameter object**: replace long parameter lists (>3) with a single typed object

**Replace conditional with polymorphism**:
```
// Before: switch on type
if type == 'pdf': render_pdf()
elif type == 'csv': render_csv()

// After: strategy map / subclass
renderers[type].render()
```

**Compose method**: decompose a long method into a sequence of well-named calls at the same abstraction level

**Move method to its data**: if a method uses more fields from class B than class A, move it to B

### 4. Dead Code Removal Strategies

1. Use static analysis / IDE unused-symbol detection as the starting list
2. For dynamic languages: add coverage instrumentation for a full release cycle before deleting
3. Search callers before removing: a symbol with no callers in the repo may still be called via reflection, config, or external clients
4. For API endpoints: check access logs for 90 days before marking as dead
5. Remove in small PRs, one module at a time — large dead code sweeps are hard to review and easy to revert entirely

### 5. Dependency Management and Cleanup

- Audit direct vs. transitive dependencies quarterly (`npm ls --depth=0`, `pip-tree`, `cargo tree`)
- Remove unused direct dependencies (check import usage, not just package.json)
- Pin transitive dependencies that have known breaking changes
- Consolidate duplicate dependencies doing the same job (e.g., two HTTP client libraries)
- Run `npm audit` / `pip-audit` / `cargo audit` and triage CVEs by severity before each release

### 6. Complexity Metrics

**Cyclomatic complexity** (structural): count decision points + 1
- Green: ≤10 | Yellow: 11–20 | Red: >20
- High cyclomatic = high test case count needed for coverage

**Cognitive complexity** (human readability): penalizes nesting and non-linear flow more heavily than cyclomatic
- Green: ≤15 | Red: >25
- Better predictor of "how hard is this to review"

Tools: SonarQube, CodeClimate, `radon` (Python), ESLint `complexity` rule, `gocyclo`

Target: refactor any function with cognitive complexity >25 before merging to main.

### 7. Tech Debt Prioritization

Use the **interest rate metaphor**:
- **Principal**: effort to fix the debt now
- **Interest**: extra time added to every future change that touches this code
- **Priority = Interest Rate = Interest / Principal**

Quadrant scoring:
| | High Interest | Low Interest |
|---|---|---|
| Low Principal | **Do now** | Do soon |
| High Principal | Plan a refactor sprint | Defer / document |

**Cost-of-delay signal**: if a module is touched in >30% of PRs and has high complexity, it is accruing interest at a high rate — prioritize it.

### 8. Key Rules

- Never refactor code you haven't read in full this session
- Every refactor commit must keep all tests green
- Rename variables/functions as a standalone commit (easiest to review, zero risk)
- Don't mix refactoring with feature work — separate PRs
- Delete more code than you add in a refactoring session (net negative is the goal)
- When in doubt: make it readable first, make it fast second
