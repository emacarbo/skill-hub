# Command Cheatsheet

Your complete guide to getting the most out of the stack.
Organized by **what you're trying to do**, not alphabetically.

---

## Starting Work

| Situation | Command | Why this one |
|-----------|---------|--------------|
| "I need to do X" (anything) | `/do X` | Universal router — figures out the right tool for you |
| Complex feature, multiple steps | `/marshal implement user auth with JWT` | Chains skills autonomously in one session |
| Large project, parallelizable | `/fleet refactor all API endpoints` | Spawns 2-3 agents in isolated worktrees |
| Multi-day campaign | `/archon migrate from REST to GraphQL` | Persistent across sessions, self-corrects |
| Need a plan before coding | `/plan redesign the equity pipeline` | Creates plan, waits for your CONFIRM before any code |
| Brand new project from scratch | `/create-app Yu-Gi-Oh collection manager` | End-to-end scaffolding pipeline |

### When to use which orchestrator

```
Simple task (< 1 hour)     → just ask Claude directly
Multi-step task (1 session) → /marshal
Parallel tasks (same session) → /fleet
Multi-session campaign      → /archon
Multi-model (Codex+Gemini)  → /multi-workflow
```

---

## Writing Code

| Situation | Command | What happens |
|-----------|---------|--------------|
| New feature with tests | `/test tdd implement liquidity score` | Red-green-refactor cycle |
| Need API endpoints | `/api-design design /users resource` | REST design + OpenAPI spec |
| Database schema work | `/db design equity_transactions` | ER model, constraints, indexes, migration |
| dbt model work | `/data-pipeline dbt add stg_sharework__equity` | dbt conventions, incremental strategy |
| Infrastructure/CI | `/infra ci` | GitHub Actions workflow |

---

## Quality & Review

| Situation | Command | What happens |
|-----------|---------|--------------|
| Before committing | `/verify` | Build + types + lint + tests + git status |
| After writing code | The `code-review-suite` skill auto-triggers | No command needed — just ask "review this" |
| Security check | `/security scan` | SAST + deps + secrets scan |
| Clean up tech debt | `/cleanup dead-code` | Find and remove unused code |
| Measure complexity | `/cleanup complexity` | Cyclomatic/cognitive metrics + hot spots |

---

## Debugging

| Situation | Command | What happens |
|-----------|---------|--------------|
| Something is broken | `/debug <paste error>` | Hypothesis-driven root cause analysis |
| Build won't compile | `/debug build` | Incremental build error resolution |
| Performance issue | `/debug perf slow_function` | CPU/memory profiling |

---

## Git & Shipping

| Situation | Command | What happens |
|-----------|---------|--------------|
| Ready to ship a branch | `/git finish` | 4 options: merge / PR / keep / discard |
| Create a pull request | `/git pr` | Analyzes all commits, drafts title + body |
| Generate changelog | `/git changelog` | From conventional commits |
| Cut a release | `/git release v1.2.0` | Version bump + changelog + tag |
| Need isolated workspace | `/git worktree equity-fix` | Safe worktree with baseline tests |

---

## Mid-Session Tools

| Situation | Command | What happens |
|-----------|---------|--------------|
| Quick question mid-task | `/aside what does select_related do?` | Answers without losing context |
| Save progress for later | `/checkpoint create pre-refactor` | Git checkpoint + log entry |
| Context window getting full | `/context-budget` | Shows token usage, suggests cuts |
| Which model for this task? | `/model-route` | Recommends haiku/sonnet/opus |
| Look up library docs | `/docs fastapi Depends` | Live lookup via Context7 |

---

## Learning & Improvement

| Situation | Command | What happens |
|-----------|---------|--------------|
| After a good session | `/learn` | Extracts reusable patterns |
| Review what you've learned | `/instinct-status` | Shows instincts by domain |
| Turn instincts into tools | `/evolve` | Clusters instincts → skills/commands |
| Promote to all projects | `/promote` | Project instinct → global |
| Optimize a prompt | `/prompt-optimize` | Analyzes + improves a prompt |

---

## Skill Hub Maintenance

| Situation | Command | What happens |
|-----------|---------|--------------|
| Evaluate a new skill | `/skill-eval <skill-name>` | Checks against stack-context.yaml |
| Map skill overlaps | `/skill-consolidate` | Groups similar skills, finds blind spots |
| Ship a skill to agents/claude | `/skill-promote <cluster>` | Merges sources into one optimized file |
| Check for stale skills | `/skill-sync` | Staleness + drift audit |
| Find skill gaps | `/skill-discover` | Analyzes sessions, suggests new skills |
| Audit overall health | `/skill-health` | Portfolio health dashboard |
| Create a new skill | `/skill-create` | Generate SKILL.md from git history |

---

## Multi-Model Workflows

For tasks that benefit from multiple AI perspectives:

| Situation | Command | Models used |
|-----------|---------|-------------|
| Collaborative planning | `/multi-plan` | Claude + Codex + Gemini |
| Full dev workflow | `/multi-workflow` | 6-phase multi-model |
| Backend-heavy work | `/multi-backend` | Codex-led |
| Frontend-heavy work | `/multi-frontend` | Gemini-led |
| Execute approved plan | `/multi-execute` | From `/multi-plan` output |

> Requires `codeagent-wrapper` installed. Check with `/harness-audit`.

---

## Autonomous Loops

For long-running autonomous work:

```
/loop-start sequential --mode safe    # One task at a time, strict gates
/loop-start continuous-pr --mode fast # Continuous PR stream, reduced gates
/loop-status                          # Check progress
```

---

## Daily Workflow Cheat Sheet

```
Morning:
  /do <today's task>              # Route to the right tool
  or /plan <if complex>           # Plan first if unsure

Coding:
  /test tdd <feature>             # TDD for new features
  /debug <error>                  # When something breaks
  /aside <question>               # Quick questions mid-flow

Before commit:
  /verify                         # Full quality check
  /security scan                  # If touching auth/data

Shipping:
  /git pr                         # Create PR
  /git finish                     # Complete the branch

End of day:
  /learn                          # Extract patterns
  /checkpoint create eod-mar29    # Save state
```

---

## Quick Reference: Skills That Auto-Trigger

These skills activate automatically from natural language — no command needed:

| Say this... | Skill that activates |
|-------------|---------------------|
| "review this code" | code-review-suite |
| "write a FastAPI endpoint" | python-web-frameworks |
| "optimize this query" | database-pro |
| "set up React component" | react-development |
| "add dbt tests" | data-engineering-pro |
| "check for vulnerabilities" | security-guardian |
| "write unit tests" | testing-qa-suite |
| "design the architecture" | architecture-planning |
| "profile this function" | debugging-master |
| "generate API docs" | documentation-suite |
