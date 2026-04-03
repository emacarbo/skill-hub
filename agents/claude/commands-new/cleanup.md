---
description: Code quality and refactoring — dead code, tech debt, dependency audit. Replaces /refactor, /refactor-clean, /quality-gate.
---

# /cleanup — Code Quality & Refactoring

Read the **code-quality-refactoring** skill from `~/dev/skill-hub/agents/general_skills/code-quality-refactoring.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `refactor <file/module>` | Refactor | Safe multi-file refactoring with rollback |
| `dead-code` | Dead code | Find and remove unused exports, functions, files |
| `deps` | Dependencies | Audit vulnerabilities, licenses, outdated packages |
| `complexity` | Metrics | Measure cyclomatic/cognitive complexity, flag hot spots |
| `gate` | Quality gate | Run formatter + linter + type checker + tests |
| *(no args)* | Survey | Scan codebase, report top 5 improvement opportunities |

## Workflow

1. Create git checkpoint before any changes
2. Execute the selected mode
3. Run tests after every change to verify no regressions
4. Report what was changed and why

## Safety

- Always create a checkpoint commit before refactoring
- Never refactor and change behavior in the same commit
- Run full test suite after each refactoring step
