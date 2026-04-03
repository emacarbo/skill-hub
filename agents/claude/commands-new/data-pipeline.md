---
description: Data engineering — dbt models, pipeline design, data quality, orchestration. Core for dqi-mitochondria work.
---

# /data-pipeline — Data Engineering

Read the **data-engineering-pro** skill from `~/dev/skill-hub/agents/general_skills/data-engineering-pro.md` and follow its protocols.

## Modes

Detect mode from $ARGUMENTS:

| Argument | Mode | What to do |
|----------|------|------------|
| `dbt <model/task>` | dbt | Model design, incremental strategy, testing, CI |
| `quality <source>` | Data quality | Generate dbt tests, data contracts, validation |
| `design <pipeline>` | Pipeline design | Architecture for batch/streaming/CDC pipeline |
| `debug <model>` | Debug | Trace data lineage, find transformation issues |
| *(no args)` | Context scan | Detect dbt project, show model stats, suggest improvements |

## Context

Auto-detect from project:
- `dbt_project.yml` → dbt mode (check profiles.yml for warehouse)
- `airflow/dags/` → Airflow orchestration context
- Look for `models/`, `macros/`, `tests/` directories

## dbt Conventions (from dqi-mitochondria)

- Staging: `stg_<source>__<entity>` (rename, cast, no joins)
- Intermediate: `int_<entity>_<verb>` (business logic, joins)
- Marts: `fct_<event>`, `dim_<entity>` (final consumption layer)
- Always add `dbt_valid_from`/`dbt_valid_to` for SCD Type 2
