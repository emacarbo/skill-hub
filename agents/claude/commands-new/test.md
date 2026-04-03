---
description: Unified testing command — TDD, unit, integration, E2E, coverage. Replaces /tdd, /e2e, /test-coverage, /test-gen.
---

# /test — Unified Testing

Read the **testing-qa-suite** skill from `~/dev/skill-hub/agents/general_skills/testing-qa-suite.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `tdd <feature>` | TDD | Red-green-refactor cycle for the feature |
| `e2e <flow>` | E2E | Generate Playwright tests for the user flow |
| `cover` | Coverage | Run suite, analyze gaps, generate missing tests |
| `gen <file/module>` | Generate | Auto-generate tests for existing code |
| `api <endpoint>` | API | Generate integration tests for API endpoint |
| *(no args)* | Auto | Detect project test framework, run full suite, report status |

## Workflow

1. Detect project test framework (pytest, jest, vitest, playwright)
2. Execute the appropriate mode from the skill
3. Run the tests and report results
4. If coverage < 80%, suggest specific tests to add

## Output

```
TEST REPORT: [MODE]

Framework: [detected]
Tests:     [X passed, Y failed, Z skipped]
Coverage:  [X%] [▓▓▓▓▓▓▓▓░░] target: 80%
Duration:  [Xs]

[If failures: list with file:line and root cause]
[If coverage gap: list uncovered functions/branches]
```
