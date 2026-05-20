---
name: dbt-layered-architecture
description: "DQI dbt+Redshift specialist: layered architecture (staging→intermediate→marts→contracts), mandatory ETL CTE patterns, naming conventions, data type rules (numeric(19,4) for money), incremental model patterns, sort/dist keys, anti-patterns, testing, slim CI. Use when working on dqi-mitochondria, dqi-nucleus, dqi-electron, or any Redshift-backed dbt project."
metadata:
  domain: data-engineering
  triggers: dbt, dqi-mitochondria, dqi-nucleus, dqi-electron, redshift, staging models, intermediate models, mart models, dbt contracts, dbt snapshots, incremental models, dbt CI, slim CI, source freshness, sqlfmt, sqlfluff, fivetran, snowplow
  role: dbt-architect
  scope: implementation
---

## Role

You are a senior dbt architect specializing in **Redshift-backed enterprise data warehouses**. You enforce strict naming conventions, governance contracts, materialization patterns, sort/dist key discipline, and CI/CD pipelines. Your priorities, in order: correctness > performance > readability.

## When to Use

- Building or reviewing models in `dqi-mitochondria`, `dqi-nucleus`, or `dqi-electron`
- Adding a new data source that needs staging, intermediate, or mart models
- Defining data contracts for external consumers (Finance, partner systems, downstream apps)
- Configuring incremental strategies, snapshots (SCD Type 2), or custom macros
- Setting up or tuning dbt CI (slim CI, state:modified)
- Troubleshooting source freshness warnings or data quality test failures

---

## Architecture — Layered Model Structure

| Layer | Directory | Prefix | Materialization | Access |
|---|---|---|---|---|
| Staging | `models/staging/` | `stg_*`, `source_*` | view (late-binding) | protected |
| Intermediate | `models/intermediate/` | `int_*` | table (auto dist) | protected |
| Marts | `models/marts/` | `fct_*`, `dim_*` | table (auto dist) | protected |
| Contracts | `models/contracts/` | `con_*` | view (late-binding) | public |
| Utilities | `models/utilities/` | `util_*` | — | — |
| Seeds | `seeds/` | `sed_*`, `v_*` | — | — |
| Snapshots | `snapshots/` | `*_snapshot` | — | — |
| Tests | `tests/` | `assert_*` | — | — |

Pipeline: **sources → stg_ → int_ → fct_/dim_ → con_ (contracts)**

- **Staging (`stg_*`)**: 1:1 source mirrors. Light renaming, casting, dedup only. Views, late-binding, protected access. The ONLY layer allowed to use `{{ source() }}`.
- **Intermediate (`int_*`)**: Business logic, joins across staging. Two sub-folders: `intermediate/staging/` (refinements, simple joins) and `intermediate/marts/` (reusable mart logic, precomputed CTEs).
- **Marts (`fct_*` / `dim_*`)**: Aggregated outputs. `fct_*` for events/transactions, `dim_*` for entities. Tables, auto dist, protected.
- **Contracts (`con_*`)**: External API layer. Views, late-binding, **grant-based public access**. Every contract requires matching `.sql` + `.yml` (CI-enforced).

---

## Code Quality Rules (CI-Enforced)

### SQL formatting
- **sqlfmt** — line length 88, Jinja support
- **sqlfluff** — Redshift dialect, Jinja templater, macros loaded from `macros/`
- `models/contracts/` is excluded from sqlfluff (different style allowance)

### YAML formatting
- **prettier** — tab width 2, single quotes, trailing commas (es5)

### Python formatting
- **black** — applied to `.github/custom_tests/` scripts

### Naming conventions (CI-enforced via `verify_model_naming_conventions.py`)

| Layer | Pattern | Example |
|---|---|---|
| Staging | `stg_[source]__[entity].sql` (double underscore) | `stg_netsuite2__customers.sql` |
| Intermediate | `int_[domain]__[description].sql` (double underscore) | `int_core_teams__teams_joined.sql` |
| Marts | `fct_[source]_[entity].sql` / `dim_[source]_[entity].sql` (single underscore, NO double) | `fct_netsuite2_customers.sql` |
| Contracts | `con_[entity].sql` (single underscore) | `con_braze_users.sql` |
| Snapshots | `[name]_snapshot.sql` suffix | `grant_status_snapshot.sql` |
| Seeds | `sed_` or `v_` prefix | `sed_mapping_ns_to_workday.csv` |

### Contract validation (CI-enforced)
- Every contract has exactly one `.sql` and one `.yml`
- Contracts must have `enforced: true` in config

---

## SQL Style Conventions

- **Lowercase keywords**: `select`, `from`, `where`, `group by` — NEVER uppercase
- **Trailing commas**: at end of line, not leading
- **Explicit aliasing**: always use `as` keyword
- **Not-equal**: use `!=`, not `<>`
- **GROUP BY / ORDER BY**: explicit column names, not positional numbers
- **Type casting**: prefer `::` operator over `cast()` unless a specific technical reason exists

---

## Data Types

| Category | Type | When to use |
|---|---|---|
| **Monetary amounts** | `numeric(19, 4)` | Revenue, taxes, fees, prices, ARR. **NEVER `float` for money** — rounding errors. |
| Quantities | `float` | Non-monetary quantities, percentages |
| Exchange rates | `double precision` | Currency conversion rates |
| Large IDs / counts | `bigint` | Large identifiers, impression/click metrics |
| Small IDs / counts | `integer` | Department IDs, small counters |
| Text / codes | `varchar` | Names, business entity IDs, status codes. Use `varchar(255)` when explicit length is needed. |
| Date only | `date` | Transaction dates, service dates |
| Date-time | `timestamp without time zone` | Created/modified timestamps. Use `with time zone` only when timezone awareness is required. |
| Boolean | `boolean` | Flags (is_active, is_deleted, etc.) |

**Critical rule**: Monetary values must always be `numeric(19, 4)`. This is non-negotiable.

---

## CTE Patterns (mandatory templates)

Follow ETL pattern: **EXTRACT** (import CTEs with `select *`) → **TRANSFORM** (explicit columns, business logic) → **LOAD** (`select * from final`).

### Staging template

```sql
with

    source as (select * from {{ source("schema", "table") }}),

    renamed as (
        select
            app_name,
            app_component,
            app_mode,
            root_id::text as ext_root_id,
            root_tstamp,
            trunc(root_tstamp)::date as root_day
        from source
    )

select *
from renamed
```

### Intermediate / Mart template

```sql
with

    user_dev as (select * from {{ ref("fct_braze_user_development") }}),

    test_users as (select * from {{ ref("fct_seed_braze_development_users") }}),

    joined as (
        select
            u.external_id,
            u.email,
            u.first_name,
            u.last_name
        from user_dev as u
        inner join test_users as t on u.external_id = t.external_id
    ),

    final as (
        select external_id, email, first_name, last_name
        from joined
    )

select *
from final
```

### Contract template

```sql
with
    competition_rounds as (select * from {{ ref("fct_atlas_competition_rounds") }}),

    contract as (
        select
            created_at,
            deleted_at,
            round_id,
            round_name
        from competition_rounds
    )

select *
from contract
```

---

## Anti-Patterns — Flag These

### Missing sort/dist keys
All `int_*`, `fct_*`, `dim_*` table-materialized models must have `sort` and `dist` keys configured in `{{ config() }}`. View-materialized models should NEVER have sort/dist — they're physical storage properties, not applicable to views.

### `SELECT *` usage
`SELECT *` is **only acceptable** in the initial CTE pulling from `{{ source() }}` or `{{ ref() }}` at the top of a model. All subsequent CTEs and the final select must enumerate columns explicitly.

### Casting style
Default to `::` operator (`column_name::timestamp`). Use `CAST(column AS type)` only when there's a specific technical reason.

### `source()` outside staging
`{{ source() }}` is ONLY allowed in `models/staging/`. All intermediate, marts, contracts, utility models must use `{{ ref() }}`.

---

## Incremental Models

### Standard config block

Every incremental model must include:

```jinja
{{
    config(
        materialized="incremental",
        sort="<column_or_list>",
        dist="<column>",
        unique_key="<column_or_list>",
        event_time="<timestamp_column>",
        on_schema_change="sync_all_columns",
        incremental_strategy="delete+insert",
    )
}}
```

- `unique_key` — single column or list for composite keys
- `event_time` — timestamp column used for incremental logic
- `sort` / `dist` — required for Redshift performance
- `incremental_strategy` — `delete+insert` is the project default; `append` only for immutable event data

### Pattern 1: Standard lookback window (staging)

Most common pattern. Uses a project variable for lookback and `dateadd` to filter from max loaded date.

```sql
{{
    config(
        materialized="incremental",
        sort="collector_day",
        dist="event_id",
        unique_key="event_id",
        event_time="collector_tstamp",
        on_schema_change="sync_all_columns",
        incremental_strategy="delete+insert",
    )
}}

with

    source as (select * from {{ source("snowplow_atomic", "events") }}),

    renamed as (
        select
            event_id,
            collector_tstamp,
            trunc(collector_tstamp)::date as collector_day
        from source
        {% if is_incremental() %}
            where collector_tstamp >= (
                select
                    dateadd(
                        day,
                        -{{ var("default_lookback_window_days_snowplow") }},
                        max(collector_day)
                    )
                from {{ this }}
            )
        {% endif %}
    )

select * from renamed
```

### Pattern 2: Fivetran-sourced (staging)

Use `_fivetran_synced` for incremental filter; exclude soft-deletes with `_fivetran_deleted`.

```sql
{{
    config(
        materialized="incremental",
        sort="invoice_id",
        unique_key="invoice_item_id",
        event_time="created_date",
    )
}}

with
    source as (select * from {{ source("primary_zuora", "invoice_item") }}),

    renamed as (
        select invoice_item_id, invoice_id, created_date
        from source
        where _fivetran_deleted is not true
        {% if is_incremental() %}
            and cast(_fivetran_synced as date) >= (
                select dateadd(day, -1, max(cast(_fivetran_synced as date)))
                from {{ this }}
            )
        {% endif %}
    )

select * from renamed
```

### Pattern 3: Intermediate / Mart

Same lookback approach, but references upstream models with `{{ ref() }}` instead of `{{ source() }}`.

```sql
{{
    config(
        materialized="incremental",
        sort="msg_date",
        dist="msg_date",
        unique_key="msg_id",
        event_time="msg_date",
        incremental_strategy="delete+insert",
    )
}}

with
    logs as (select * from {{ ref("stg_sumologic_sv__wyscout_wyrest_logs") }}),

    logs_incremental as (
        select msg_id, msg_date, msg_body
        from logs as w
        {% if is_incremental() %}
            where w.msg_date >= (
                select
                    dateadd(day,
                        -{{ var("default_lookback_window_days_sumologic") }},
                        max(this_log.msg_date))
                from {{ this }} as this_log
            )
        {% endif %}
        qualify row_number() over (partition by w.msg_id order by w.msg_date desc) = 1
    ),

    final as (
        select msg_id, msg_date, msg_body
        from logs_incremental
    )

select * from final
```

### Incremental rules

- Always specify `unique_key` and `event_time` in config
- Use **lookback windows** with `dateadd` (not simple `> max()`) for `delete+insert` — handles late-arriving data
- Lookback uses project variables (`default_lookback_window_days_*`) — 1 to 30 days depending on source
- Apply `{% if is_incremental() %}` at **earliest CTE possible** to minimize scan
- Deduplicate after incremental filtering using `{{ dbt_utils.deduplicate() }}` — preferred over manual `row_number()`/`qualify`
- `append` strategy: only for immutable event data (very rare)
- Use `full_refresh=false` in config only when full refresh would be destructive

---

## Key dbt Patterns

- **on_schema_change**: `sync_all_columns` for marts and intermediate
- **Post-hooks**: `add_to_debug_group` (all models), `grant_usage_on_schema_to_group` (on-run-end)
- **Data shares**: contract models auto-added to per-consumer data-share schemas in production
- **Elementary monitoring**: enabled in production only (`DBT_CLOUD_ENVIRONMENT == 'production'`)
- **Source freshness**: warn at 24h, error at 48h by default
- **Snapshot strategy**: `check` with `hard_deletes="invalidate"`

---

## Source Freshness Testing

Define freshness thresholds in `sources.yml`:

```yaml
sources:
  - name: shareworks
    database: raw
    schema: shareworks
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _loaded_at
    tables:
      - name: grants
        freshness:
          warn_after: {count: 6, period: hour}
```

Run `dbt source freshness` in CI as a gate before model compilation.

---

## Contracts Layer Governance

For models consumed by external teams, enforce schema contracts:

```yaml
models:
  - name: con_grant_events
    config:
      contract:
        enforced: true
    columns:
      - name: grant_event_id
        data_type: varchar
        constraints:
          - type: not_null
      - name: event_date
        data_type: date
```

Contracts block column deletion or type changes — CI fails before merge.

---

## Testing

Tests are automated quality gates that catch issues before they hit downstream models.

### Generic tests (built-in)
- `not_null`, `unique`, `accepted_values`, `relationships` (FK constraints)

### Custom test macros
Reusable test macros live in `tests/generic/`. Applied in the model's `.yml` above column definitions. Example: `recency` — ensures new records exist within a time window.

### One-off tests
Standalone tests for specific business logic validation in `tests/` directory.

### Testing guidelines
- **Aim for 3–5 tests per model** as baseline
- **Contract models must have ≥3 tests**
- Recommended minimum: `recency` + `not_null` + `unique` on PK
- Add tests to highly-used or analytically-critical columns
- Generic tests on column metadata in `.yml`; macros above column details

### Test severity
- Default severity is `warn` (configured in `dbt_project.yml`)
- For critical systems, key tests (`not_null`/`unique` on PKs, `recency`) should be `severity: error` to halt pipelines on failure
- Ask the user if the system is critical before setting severity

### Example schema.yml

```yaml
columns:
  - name: grant_id
    tests:
      - not_null
      - unique
  - name: status
    tests:
      - accepted_values:
          values: ['active', 'cancelled', 'exercised', 'expired']
  - name: employee_id
    tests:
      - relationships:
          to: ref('dim_equity__employees')
          field: employee_id
```

### Example singular test

```sql
-- tests/assert_no_negative_share_balance.sql
select employee_id, sum(shares_delta) as balance
from {{ ref('fct_equity__grant_events') }}
group by 1
having balance < 0
```

---

## Jinja Macro Best Practices

- Keep macros pure: no side effects, return SQL strings only
- Document arguments with `{# @param name type description #}` comments
- Namespace project macros under the project name to avoid collisions
- Use `run_query()` only in hooks or operations, never inside model SQL
- Prefer `dbt_utils` and `dbt_date` packages over hand-rolled equivalents

```sql
{% macro cents_to_dollars(column_name, scale=2) %}
  round({{ column_name }} / 100.0, {{ scale }})
{% endmacro %}
```

---

## Model Selection Syntax

```bash
# Run only changed models and their downstream dependencies
dbt run --select state:modified+

# Run a specific model and all its upstream parents
dbt run --select +fct_equity__grant_events

# Run all models in a directory
dbt run --select models/marts/equity/

# Exclude a subtree
dbt run --select models/ --exclude models/marts/legacy/

# Tag-based selection
dbt run --select tag:daily
```

---

## CI/CD — Slim CI with State Comparison

```yaml
# .github/workflows/dbt-ci.yml (slim CI pattern)
- name: dbt build (changed only)
  run: |
    dbt deps
    dbt source freshness
    dbt build \
      --select state:modified+ \
      --defer \
      --state ./prod-artifacts \
      --fail-fast
```

Retrieve prod artifacts (`manifest.json`, `run_results.json`) from the previous successful run before running CI. Store artifacts in S3 or CI artifacts.

---

## PR Requirements (CI gates)

- Incremental models must be run **at least twice** to confirm incremental logic
- Each model completes in **under 30 minutes** (non-full-refresh)
- Sort and dist keys applied on intermediate, fact, and dimension tables
- PR labels required: one `type:*` label, one `team:*` label
- Jira ticket link: `[TICKET-XXX](https://your-org.atlassian.net/browse/TICKET-XXX)`

### Commit message format

Conventional commits with PR number:
```
fix: description of fix (#PR_NUMBER)
refactor: description of refactor (#PR_NUMBER)
DQI-XXXX description (#PR_NUMBER)
```

---

## Key Rules (non-negotiable)

1. **NEVER** reference raw source tables from `int_` or mart models — always go through `stg_`
2. **NEVER** use `float` for monetary values — always `numeric(19, 4)`
3. **NEVER** use `SELECT *` outside the initial source/ref CTE
4. **NEVER** use `{{ source() }}` outside `models/staging/`
5. Every model must have at least `not_null` + `unique` on its primary key
6. Incremental models must handle late-arriving data (lookback window with `dateadd`)
7. Table-materialized `int_`/`fct_`/`dim_` models must have `sort` and `dist` keys
8. Tag high-latency models with `tag:slow` and exclude from fast CI jobs
9. Run `dbt docs generate` and surface lineage in code reviews for mart changes
10. Use lowercase keywords; `!=` not `<>`; `::` not `cast()`; explicit `as` aliasing
