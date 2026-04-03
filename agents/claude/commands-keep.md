# Commands to KEEP

These are explicit workflow entry points, orchestration coordinators, or infrastructure
utilities that require deliberate user invocation. Skills cannot replace these.

## Orchestration (12)

| Command | Purpose |
|---------|---------|
| `/do` | Universal intent router — backbone of the harness |
| `/marshal` | Single-session multi-step orchestrator |
| `/fleet` | Parallel campaign orchestrator (isolated worktrees) |
| `/archon` | Multi-session campaign agent with persistence |
| `/orchestrate` | Sequential agent workflow chains |
| `/devfleet` | DevFleet MCP-based parallel agent dispatch |
| `/plan` | Explicit plan-first gate — waits for CONFIRM |
| `/multi-plan` | Multi-model collaborative planning (Codex+Gemini) |
| `/multi-workflow` | Full 6-phase multi-model dev workflow |
| `/multi-backend` | Backend-focused Codex-led workflow |
| `/multi-frontend` | Frontend-focused Gemini-led workflow |
| `/multi-execute` | Multi-model execution from approved plan |

## Session & Context (10)

| Command | Purpose |
|---------|---------|
| `/checkpoint` | Create/verify named workflow checkpoints |
| `/save-session` | Save full session state to file |
| `/resume-session` | Load previous session with full context briefing |
| `/sessions` | Session management (list, alias, info) |
| `/aside` | Mid-task quick Q&A without losing context |
| `/context-budget` | Token overhead analysis across setup |
| `/model-route` | Recommend model tier for task |
| `/loop-start` | Start managed autonomous loop with safety defaults |
| `/loop-status` | Inspect active loop state/progress |
| `/claw` | NanoClaw REPL with persistent history |

## Harness & Learning (13)

| Command | Purpose |
|---------|---------|
| `/harness-audit` | Deterministic harness scorecard (7 categories) |
| `/skill-health` | Skill portfolio health dashboard |
| `/skill-create` | Analyze git history, generate SKILL.md files |
| `/learn` | Extract reusable patterns from session |
| `/learn-eval` | Learn with quality gate before saving |
| `/instinct-status` | Show learned instincts by domain/confidence |
| `/instinct-import` | Import instincts from file or URL |
| `/instinct-export` | Export instincts to shareable YAML |
| `/evolve` | Cluster instincts into commands/skills/agents |
| `/promote` | Promote project-scoped instincts to global |
| `/projects` | List project registry and instinct stats |
| `/rules-distill` | Distill cross-cutting principles into rules |
| `/prompt-optimize` | Analyze and optimize a prompt |

## Utility (6)

| Command | Purpose |
|---------|---------|
| `/verify` | On-demand build+type+lint+test+git check |
| `/docs` | Live documentation lookup via Context7 MCP |
| `/pm2` | Auto-generate PM2 service config |
| `/setup-pm` | Configure preferred package manager |
| `/experiment` | Optimization loops with scalar fitness functions |
| `/create-app` | End-to-end app creation pipeline (5 tiers) |

**Total: 41 commands**
