---
description: Systematic debugging — hypothesis-driven root cause analysis. Replaces /systematic-debug and /build-fix.
---

# /debug — Systematic Debugging

Read the **debugging-master** skill from `~/dev/skill-hub/agents/general_skills/debugging-master.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `<error message or description>` | Diagnose | Hypothesis-driven root cause analysis |
| `build` | Build fix | Incremental build error resolution |
| `perf <target>` | Profile | CPU/memory profiling of target |
| *(no args)* | Interactive | Ask user to describe the symptom |

## Workflow

1. **Observe** — Gather evidence (error messages, logs, stack traces)
2. **Hypothesize** — Form ranked hypotheses (most likely first)
3. **Test** — Design minimal experiment to confirm/reject top hypothesis
4. **Fix** — Apply targeted fix, verify with tests
5. **Verify** — Run full test suite to confirm no regressions

## Rules

- NEVER guess. Every hypothesis must be testable.
- Read the actual error output before proposing fixes.
- One hypothesis at a time — don't shotgun.
- If 3 hypotheses fail, widen the search (check assumptions).
