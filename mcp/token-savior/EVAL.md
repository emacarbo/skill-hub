---
name: token-savior
type: mcp-server
status: approved
date_evaluated: "2026-04-03"
source: https://github.com/Mibayy/token-savior
version: 0.7.1
---

# token-savior MCP Server

Structural codebase indexer providing 34 surgical query tools. Replaces
full-file reads with symbol-level lookups for ~99% token reduction.

## Installation

```bash
# Venv at ~/.local/token-savior-venv/
# Source at ~/dev/skill-hub/mcp/token-savior/
# Registered via: claude-personal mcp add token-savior
```

## Workspace Roots

- dqi-mitochondria
- project_pegasus
- equity_reallocation
- equity_reconciliation
- trial_balances_comparison
- skill-hub

## Key Tools

| Category | Most useful |
|----------|------------|
| Navigation | `find_symbol`, `get_function_source`, `get_structure_summary` |
| Impact | `get_change_impact`, `get_call_chain`, `get_dependents` |
| Git | `get_changed_symbols`, `build_commit_summary` |
| Edit | `replace_symbol_source`, `create_checkpoint` |
| Test | `find_impacted_test_files`, `run_impacted_tests` |

## Synergy with skills

- `debugging-master` → use `get_call_chain` + `get_change_impact` for root cause
- `testing-qa-suite` → use `find_impacted_test_files` to run only affected tests
- `code-review-suite` → use `get_changed_symbols` for symbol-level diff review
- `data-engineering-pro` → use `get_dependencies` for dbt model lineage
