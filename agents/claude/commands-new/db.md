---
description: Database operations — schema design, query optimization, migrations, PostgreSQL/Redshift tuning.
---

# /db — Database Operations

Read the **database-pro** skill from `~/dev/skill-hub/agents/general_skills/database-pro.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `design <entity>` | Schema design | ER model, normalization, constraints, indexes |
| `optimize <query>` | Query tuning | EXPLAIN analysis, rewrite suggestions, index recommendations |
| `migrate <description>` | Migration | Generate safe migration with expand-contract pattern |
| `review` | Review | Audit schema for anti-patterns, missing indexes, N+1 risks |
| `tune` | Tuning | PostgreSQL/Redshift configuration recommendations |
| *(no args)* | Interactive | Ask what database task to perform |

## Context

Detect database from project:
- `dbt_project.yml` → Redshift/dbt context (use data-engineering-pro skill too)
- `alembic/` or `migrations/` → PostgreSQL + Alembic
- `*.sql` files → Generic SQL

## Output

Always include:
- The SQL with comments explaining decisions
- EXPLAIN output for query optimization
- Rollback strategy for migrations
