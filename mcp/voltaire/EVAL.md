---
name: voltaire
type: mcp-server (hosted)
status: reference
date_evaluated: "2026-04-03"
source: https://mcp.hivoltaire.com
---

# Voltaire MCP Server — Reference Copy

Paywall optimization and conversion intelligence SaaS. Kept as a **reference
for recyclable patterns**, not for direct use in current projects.

## Recyclable Patterns

These design patterns are worth studying and adapting:

### 1. First-run vs Recurring-run bifurcation
The command detects setup state and switches workflow entirely:
- First run: intro → confirm → setup → preview
- Recurring: lead with data → wait for user → apply on request
Useful for any tool that has a setup phase.

### 2. Agent synthesis over agent silos
Three specialized agents (Timing, Cohort, Churn) produce independent signals,
but the command synthesizes them into a single diagnosis before presenting.
Pattern: don't dump 3 agent outputs — find what they collectively say.

### 3. Describe-first, apply-after-confirmation
Never touch code without explaining what/where/why first. Then wait for
explicit "go ahead." Good trust-building pattern for any code-modifying tool.

### 4. mark_applied for historical context
Every change is logged so future runs have full history. Enables impact
measurement (cr_before vs cr_after). Applicable to any iterative optimization.

### 5. Data sufficiency gates
When agents lack data, output a fixed message and stop. No speculation,
no "you might consider." Prevents low-confidence recommendations.

### 6. Benchmark-first diagnosis
Always surface the gap vs industry median before anything else. The user
should see "you're at 2.1%, benchmark is 3.8%" before any agent analysis.

### 7. Funnel reach as mandatory calculation
Compute `shown / sessions`. If < 50%, the problem is upstream of the paywall,
not the paywall itself. Applicable to any funnel analysis.

## Files

- `voltaire.md` — main command (319 lines)
- `voltaire-status.md` — quick status check (40 lines)

## MCP Tools (5)

| Tool | Purpose |
|------|---------|
| `create_app` | Bootstrap: register app, get SDK token |
| `setup` | Connect Stripe (live secret key) |
| `get_stats` | Connection status, SDK status, conversion rate |
| `analyze_paywall` | Full raw data: metrics, behavioral, agents, trends |
| `mark_applied` | Log a change for historical context |

## Not Installed

This MCP server is NOT registered. It's a reference copy only.
To install: `curl -fsSL https://mcp.hivoltaire.com/install | bash`
