---
name: database-pro
description: "Comprehensive database specialist covering SQL authorship, PostgreSQL administration, schema architecture, query optimization, migrations, cloud operations, and NoSQL design. Use when writing complex queries, optimizing slow queries with EXPLAIN ANALYZE, designing schemas from scratch, planning migrations with zero downtime, tuning PostgreSQL configuration, or selecting between relational/NoSQL/time-series engines."
license: MIT
metadata:
  domain: infrastructure
  triggers: SQL optimization, query performance, database design, PostgreSQL, EXPLAIN ANALYZE, window functions, CTEs, indexing, schema design, migrations, JSONB, replication, VACUUM, NoSQL, MongoDB, DynamoDB, time-series, multi-tenant
  role: specialist
  scope: implementation
  output-format: analysis-and-code
  related-skills: data-engineering-pro, devops-infrastructure, python-core
---

# Database Pro

Senior database specialist with end-to-end coverage: SQL authorship, PostgreSQL administration, schema architecture, query optimization, migrations, cloud operations, and NoSQL/time-series design.

## When to Use

- Writing complex SQL: CTEs, window functions, recursive queries, cross-dialect
- Diagnosing slow queries and interpreting EXPLAIN ANALYZE output
- Designing schemas from requirements (ERD, normalization, constraints, RLS)
- Planning schema migrations with zero downtime (expand-contract pattern)
- Tuning PostgreSQL: VACUUM, autovacuum, shared_buffers, replication
- Selecting between PostgreSQL, MySQL, MongoDB, DynamoDB, TimescaleDB
- Designing for multi-tenancy, soft deletes, audit trails, and versioning
- Cloud DB operations: backups, failover, cost optimization, connection pooling

## Core Workflow

1. **Baseline** — Capture `EXPLAIN (ANALYZE, BUFFERS)` output before any change
2. **Design** — Model entities, relationships, access patterns, and scale targets
3. **Implement** — Write set-based SQL; add indexes with `CREATE INDEX CONCURRENTLY`
4. **Validate** — Re-run EXPLAIN; confirm index scans replace Seq Scans; measure wall-clock improvement
5. **Operate** — Schedule VACUUM/ANALYZE, monitor pg_stat views, configure replication lag alerts

## SQL Patterns

```sql
-- CTE: isolate expensive subquery logic for reuse
WITH ranked_orders AS (
    SELECT customer_id, order_id, total_amount,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
    FROM orders
    WHERE status = 'completed'
)
SELECT customer_id, order_id, total_amount
FROM ranked_orders WHERE rn = 1;

-- Window function: running total + rank without self-join
SELECT department_id, employee_id, salary,
       SUM(salary)  OVER (PARTITION BY department_id ORDER BY hire_date) AS running_payroll,
       RANK()       OVER (PARTITION BY department_id ORDER BY salary DESC) AS salary_rank
FROM employees;

-- Correlated subquery → lateral join (faster)
SELECT o.order_id, agg.item_count
FROM orders o
LEFT JOIN LATERAL (
    SELECT SUM(quantity) AS item_count
    FROM order_items oi WHERE oi.order_id = o.id
) agg ON true;
```

## EXPLAIN ANALYZE Interpretation

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42 AND status = 'pending';
```

| Pattern | Symptom | Fix |
|---------|---------|-----|
| `Seq Scan` on large table | No index on filter column | Add B-tree index |
| `Nested Loop` + large outer set | Exponential row growth | Hash Join; index inner join key |
| `actual rows >> estimated rows` | Stale statistics | `ANALYZE <table>` |
| `Buffers: read=90000` | Low cache hit rate | Increase `shared_buffers`; covering index |
| `Sort Method: external merge` | Sort spilling to disk | Increase `work_mem` |

## PostgreSQL Schema Design

```sql
-- Prefer BIGINT GENERATED ALWAYS AS IDENTITY over SERIAL/UUID for PKs
CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ON users (LOWER(email));  -- case-insensitive uniqueness

-- Data type rules
-- IDs:       BIGINT GENERATED ALWAYS AS IDENTITY (UUID only for global uniqueness)
-- Strings:   TEXT (not VARCHAR(n) or CHAR(n))
-- Timestamps: TIMESTAMPTZ (never plain TIMESTAMP)
-- Money:     NUMERIC(p,s) (never FLOAT)
-- Booleans:  BOOLEAN NOT NULL with default

-- Indexes
CREATE INDEX CONCURRENTLY idx_orders_customer_status  -- no table lock
    ON orders (customer_id, status)
    WHERE status = 'pending';  -- partial: smaller index

CREATE INDEX idx_orders_covering  -- eliminates heap fetch
    ON orders (status, created_at)
    INCLUDE (customer_id, total_amount);

-- JSONB with GIN
CREATE INDEX ON profiles USING GIN (attrs);
-- Query: WHERE attrs @> '{"theme":"dark"}'
-- For containment-only: use jsonb_path_ops opclass (smaller index)
```

## Schema Architecture Patterns

```sql
-- Multi-tenancy: organization_id on every tenant-scoped table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tasks_org_isolation ON tasks FOR ALL TO app_user
    USING (organization_id = current_setting('app.org_id')::bigint);

-- Soft deletes: never hard-delete auditable records
ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMPTZ;
CREATE INDEX ON tasks (id) WHERE deleted_at IS NULL;  -- active-only index

-- Optimistic locking: prevent concurrent overwrites
ALTER TABLE tasks ADD COLUMN version INTEGER NOT NULL DEFAULT 0;
-- UPDATE tasks SET ..., version = version + 1
-- WHERE id = $1 AND version = $2_expected

-- Audit trail
CREATE TABLE audit_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id BIGINT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
    before_data JSONB,
    after_data JSONB,
    changed_by BIGINT REFERENCES users(user_id),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## PostgreSQL Administration

```sql
-- Identify slow queries (requires pg_stat_statements)
SELECT query, calls, round(mean_exec_time::numeric, 2) AS mean_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 20;

-- VACUUM and bloat monitoring
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 20;

VACUUM (ANALYZE, VERBOSE) high_churn_table;

-- Replication lag monitoring
SELECT client_addr, state,
       (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;
```

**Key configuration levers:**
- `shared_buffers`: 25% of RAM for dedicated DB server
- `work_mem`: per-sort/hash; set session-level for heavy analytics
- `autovacuum_vacuum_scale_factor`: lower to 0.01-0.05 for high-churn tables
- `effective_cache_size`: 50-75% of RAM (planner hint only)

## Zero-Downtime Migrations (Expand-Contract)

```sql
-- Phase 1 EXPAND: add nullable column, deploy new code writing both
ALTER TABLE orders ADD COLUMN new_status TEXT;

-- Phase 2 BACKFILL: batch update in chunks to avoid lock contention
UPDATE orders SET new_status = status
WHERE id BETWEEN $start AND $end AND new_status IS NULL;

-- Phase 3 CONSTRAINT: add NOT NULL after backfill complete
ALTER TABLE orders ALTER COLUMN new_status SET NOT NULL;

-- Phase 4 CONTRACT: deploy code reading only new column, then drop old
ALTER TABLE orders DROP COLUMN status;
```

Rules:
- `CREATE INDEX CONCURRENTLY` — never plain `CREATE INDEX` in production
- `ALTER TABLE ... ADD COLUMN` with volatile default rewrites entire table
- Test all migrations in staging with production-size data
- Always have a rollback script

## Technology Selection

| Need | Recommended |
|------|-------------|
| Transactional, relational | PostgreSQL |
| Simple app/legacy | MySQL |
| Flexible documents | MongoDB (with schema validation) |
| Key-value, caching, queues | Redis |
| Serverless / AWS-native | DynamoDB |
| Time-series (IoT, metrics) | TimescaleDB or InfluxDB |
| Distributed SQL | CockroachDB / TiDB |
| Analytics / OLAP | ClickHouse, Redshift, BigQuery |

**Multi-tenant isolation options:**
- Shared schema + `org_id` column + RLS — simplest, most cost-effective
- Schema per tenant — moderate isolation, harder to query across tenants
- Database per tenant — strongest isolation, highest overhead

## NoSQL Design Principles

**MongoDB:** Embed when data is always accessed together; reference when data grows unbounded or is shared. Use schema validation with `$jsonSchema`. Index every field used in queries; compound indexes follow ESR rule (Equality, Sort, Range).

**DynamoDB:** Design around access patterns first. Single-table design with composite keys (`PK + SK`). Use GSI for alternate access patterns. Avoid hot partitions with write sharding.

**Time-series (TimescaleDB):** Use hypertables for automatic time-based partitioning. Compression policies for data older than N days. Continuous aggregates for pre-computed rollups.

## Cloud & Cost Optimization

- Right-size instances: use `pg_stat_activity` to measure real connection counts before sizing
- Connection pooling: PgBouncer (transaction mode) in front of PostgreSQL
- Read replicas for analytical queries; never hit primary for reporting
- Archive partitions to cold storage (S3/GCS) with Parquet for >90-day data
- Managed DB (RDS, Cloud SQL, Neon) vs self-managed: prefer managed unless cost or version control is critical
- Reserved instances for predictable workloads: 30-50% cost reduction

## Constraints

**MUST DO**
- `EXPLAIN (ANALYZE, BUFFERS)` baseline before any optimization
- `CREATE INDEX CONCURRENTLY` in production (no table locks)
- `ANALYZE <table>` after bulk loads to refresh statistics
- Test migrations in staging with realistic data volume
- Monitor `pg_stat_replication` for lag in replicated setups
- Use parameterized queries everywhere (prevents SQL injection)

**MUST NOT DO**
- Create indexes without first analyzing query patterns
- Make multiple changes simultaneously (can't attribute impact)
- Disable autovacuum globally
- Use `SELECT *` in production queries
- Apply schema changes to production without a rollback plan
- Store large BLOBs in the DB (use object storage + reference URL)
