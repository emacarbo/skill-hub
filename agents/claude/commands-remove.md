# Commands to REMOVE (future cleanup)

Do NOT delete these yet. This file is a reference for when we're ready to prune.

## Redundant with consolidated skills (17)

These are fully subsumed by the new skill library. The skill covers the same
behavior more richly and auto-triggers from context.

| Command | Replaced by skill | Notes |
|---------|-------------------|-------|
| `/code-review` | `code-review-suite` | Same CRITICAL/HIGH/MEDIUM taxonomy |
| `/review` | `code-review-suite` | 5-pass structured review is subset of suite |
| `/python-review` | `code-review-suite` + `python-core` | ruff/mypy/bandit already in python-core |
| `/tdd` | `testing-qa-suite` | TDD red-green-refactor is Section 1 |
| `/e2e` | `testing-qa-suite` | Playwright E2E covered |
| `/test-coverage` | `testing-qa-suite` | Coverage analysis covered |
| `/test-gen` | `testing-qa-suite` | Framework-aware test gen covered |
| `/systematic-debug` | `debugging-master` | Hypothesis-driven RCA is core of skill |
| `/build-fix` | `debugging-master` | Incremental build error fixing covered |
| `/refactor` | `code-quality-refactoring` | Safe multi-file refactoring covered |
| `/refactor-clean` | `code-quality-refactoring` | Dead code removal is Section 2 |
| `/quality-gate` | `code-quality-refactoring` + `verification-before-completion` | Formatter/lint/type pipeline covered |
| `/update-docs` | `documentation-suite` | Sync docs pattern is in the suite |
| `/update-codemaps` | `documentation-suite` | Architecture map generation covered |
| `/prd` | `product-management` | PRD generation is Section 3 of skill |
| `/eval` | `verification-before-completion` | Eval definition/check/report maps to verification gate |
| `/dev-preview` | project-specific | Hardcoded to one specific project — not global |

## Irrelevant to active stack (13)

Languages/tools not in stack-context.yaml. Keep the standalone skills in
general_skills/ for reference, but commands add noise.

| Command | Reason |
|---------|--------|
| `/cpp-build` | C++ not in stack |
| `/cpp-review` | C++ not in stack |
| `/cpp-test` | C++ not in stack |
| `/go-build` | Go not in stack |
| `/go-review` | Go not in stack |
| `/go-test` | Go not in stack |
| `/gradle-build` | Gradle/JVM not in stack |
| `/kotlin-build` | Kotlin not in stack |
| `/kotlin-review` | Kotlin not in stack |
| `/kotlin-test` | Kotlin not in stack |
| `/rust-build` | Rust not in stack |
| `/rust-review` | Rust not in stack |
| `/rust-test` | Rust not in stack |

**Total to remove: 30 commands (when ready)**
