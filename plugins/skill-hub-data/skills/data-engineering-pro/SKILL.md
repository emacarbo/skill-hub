---
name: data-engineering-pro
description: "Comprehensive data engineering specialist covering pipeline architecture, batch/streaming processing, dbt transformations, data quality, orchestration, and modern data stack design. Use when building or debugging data pipelines, choosing between batch/streaming/Lambda/Kappa architectures, implementing dbt models, setting up Great Expectations validation, designing data contracts, configuring Airflow/Prefect/Dagster DAGs, or architecting lakehouse storage with Delta Lake or Iceberg."
license: MIT
metadata:
  domain: data-ml
  triggers: data pipeline, ETL, ELT, Airflow, dbt, Kafka, streaming, Spark, data quality, Great Expectations, data contracts, data lakehouse, Delta Lake, Iceberg, Prefect, Dagster, batch processing, CDC, feature store, data mesh, data catalog
  role: specialist
  scope: implementation
  output-format: analysis-and-code
  related-skills: database-pro, spark-engineer, dbt-layered-architecture
---

# Data Engineering Pro

Senior data engineering specialist covering the complete modern data stack: pipeline architecture, batch and streaming processing, dbt transformations, data quality, orchestration, lakehouse storage, and DataOps.

## When to Use

- Designing or debugging batch, streaming, or CDC data pipelines
- Choosing between ETL/ELT, Lambda, Kappa, or Lakehouse architectures
- Building dbt models with staging/intermediate/marts layer structure
- Implementing data quality with Great Expectations or dbt tests
- Configuring Airflow, Prefect, or Dagster DAGs and schedules
- Setting up data contracts and schema evolution strategies
- Architecting Delta Lake or Iceberg tables with ACID guarantees
- Building data mesh, feature stores, or data catalog integrations
- Optimizing Spark jobs and cloud data platform costs

## Core Workflow

1. **Define** — Document sources, SLAs, data contracts, and quality requirements
2. **Architect** — Select processing pattern, storage format, and orchestration tool
3. **Implement** — Build ingestion, transformation, and validation layers
4. **Test** — Unit-test transformations; run quality suites; validate end-to-end
5. **Operate** — Monitor freshness, failure rates, and costs; automate remediation

## Architecture Decision Framework

### Batch vs Streaming

| Criteria | Batch | Streaming |
|----------|-------|-----------|
| Latency | Hours to days | Seconds to minutes |
| Volume | Large historical datasets | Continuous event streams |
| Complexity | Complex ML transforms | Simple aggregations, filtering |
| Cost | Lower infrastructure | Higher infrastructure |

**Decision tree:**
```
Is sub-minute insight required?
├── Yes → Streaming (Kafka + Flink or Spark Structured Streaming)
│   └── Exactly-once semantics needed?
│       ├── Yes → Kafka + Flink with transactional sinks
│       └── No  → Kafka consumer groups
└── No → Batch
    └── Daily volume > 1 TB?
        ├── Yes → Spark / Databricks
        └── No  → dbt + warehouse compute
```

### Architecture Patterns

| Pattern | When to Use |
|---------|-------------|
| **ELT** | Cloud warehouse available (Snowflake, BigQuery); transform in warehouse |
| **ETL** | Sensitive PII that must not land raw; heavy pre-processing needed |
| **Lambda** | Need both ML training (batch) and real-time serving |
| **Kappa** | Pure event-driven; all logic expressible as stream operations |
| **Lakehouse** | Mixed workloads (ML + analytics); need ACID + open formats |

### Storage Selection

| Need | Technology |
|------|------------|
| Analytics SQL | Snowflake, BigQuery, Redshift |
| Open lakehouse | Delta Lake, Apache Iceberg |
| Streaming buffer | Apache Kafka, AWS Kinesis |
| Feature store | Feast, Tecton, Hopsworks |
| Data catalog | DataHub, Apache Atlas, OpenMetadata |

## Pipeline Implementation Patterns

### Batch Ingestion

```python
from datetime import datetime
import pandas as pd

def extract_incremental(
    connection_string: str,
    table: str,
    watermark_col: str,
    last_watermark: datetime,
) -> pd.DataFrame:
    query = f"""
        SELECT * FROM {table}
        WHERE {watermark_col} > %(watermark)s
        ORDER BY {watermark_col}
    """
    df = pd.read_sql(query, connection_string, params={"watermark": last_watermark})
    # Attach pipeline metadata
    df["_extracted_at"] = datetime.utcnow()
    df["_source"] = table
    return df

def validate_and_route(df: pd.DataFrame, schema: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split valid records from dead-letter queue."""
    mask = df[schema["required_fields"]].notna().all(axis=1)
    return df[mask], df[~mask]  # valid, dlq
```

### Streaming with Exactly-Once Semantics

```python
from confluent_kafka import Consumer, Producer, KafkaError

consumer = Consumer({
    "bootstrap.servers": "broker:9092",
    "group.id": "pipeline-group",
    "enable.auto.commit": False,  # manual commit after processing
    "isolation.level": "read_committed",  # read only committed txn messages
})

for msg in consumer:
    if msg.error():
        handle_error(msg.error())
        continue
    try:
        record = deserialize(msg.value())
        result = transform(record)
        write_to_sink(result)
        consumer.commit(msg)  # commit only after successful write
    except Exception as e:
        route_to_dlq(msg, e)
```

### Orchestration

**Airflow DAG:**
```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(schedule="0 5 * * *", start_date=datetime(2025, 1, 1),
     retries=2, retry_delay=timedelta(minutes=5),
     catchup=False)
def orders_pipeline():
    @task
    def extract() -> str:
        return run_extraction(execution_date="{{ ds }}")

    @task
    def transform(extracted_path: str) -> str:
        return run_dbt_models(extracted_path)

    @task
    def validate(transformed_path: str) -> None:
        run_great_expectations_checkpoint("orders_suite", transformed_path)

    validate(transform(extract()))

orders_pipeline()
```

**Dagster asset-based (preferred for data products):**
```python
from dagster import asset, AssetIn, FreshnessPolicy

@asset(freshness_policy=FreshnessPolicy(maximum_lag_minutes=60))
def raw_orders(context) -> pd.DataFrame:
    return extract_orders(context.partition_key)

@asset(ins={"raw_orders": AssetIn()})
def orders_cleaned(raw_orders: pd.DataFrame) -> pd.DataFrame:
    return clean_orders(raw_orders)
```

## dbt Transformation Patterns

**Layer structure:**
```
models/
├── staging/          # 1:1 with source; rename, cast, light cleaning
│   └── stg_orders.sql
├── intermediate/     # joins and business logic not ready for marts
│   └── int_orders_enriched.sql
└── marts/            # business-facing, documented, tested
    └── fct_orders.sql
```

```sql
-- staging: incremental, dedup, add metadata
{{ config(materialized='incremental', unique_key='order_id',
          on_schema_change='sync_all_columns') }}

SELECT
    order_id,
    CAST(created_at AS TIMESTAMP) AS created_at,
    UPPER(status) AS status,
    _loaded_at
FROM {{ source('raw', 'orders') }}
{% if is_incremental() %}
WHERE _loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}

-- tests in schema.yml
models:
  - name: stg_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: status
        tests:
          - accepted_values:
              values: ['PENDING', 'PAID', 'CANCELLED']
```

**Incremental strategy selection:**
- `append` — append-only event logs
- `merge` — upsert with unique key (default for most dimensions)
- `delete+insert` — full partition replacement (time-partitioned tables)

## Data Quality Framework

```python
import great_expectations as ge

context = ge.get_context()
suite = context.add_expectation_suite("orders_suite")

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="orders_suite"
)

# Table-level expectations
validator.expect_table_row_count_to_be_between(min_value=1000)
validator.expect_table_columns_to_match_set(
    {"order_id", "user_id", "total_amount", "created_at"}
)

# Column-level expectations
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_unique("order_id")
validator.expect_column_values_to_be_between(
    "total_amount", min_value=0, max_value=100000
)

validator.save_expectation_suite()
results = context.run_checkpoint("orders_checkpoint")
if not results["success"]:
    raise DataQualityError(f"Quality gate failed: {results}")
```

**Data contracts (schema-level agreement):**
```yaml
# contract: orders_v1.yaml
schema_version: 1
tables:
  orders:
    columns:
      order_id: {type: bigint, nullable: false, unique: true}
      total_amount: {type: numeric, nullable: false, min: 0}
    freshness:
      warn_after: {count: 1, period: hour}
      error_after: {count: 4, period: hour}
```

## Lakehouse Storage

**Delta Lake operations:**
```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder.config("spark.sql.extensions",
    "io.delta.sql.DeltaSparkSessionExtension").getOrCreate()

# Upsert (merge)
delta_table = DeltaTable.forPath(spark, "s3://lake/orders")
delta_table.alias("target").merge(
    source=new_df.alias("source"),
    condition="target.order_id = source.order_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

# Compact small files + Z-order clustering
delta_table.optimize().executeZOrderBy("created_at", "user_id")

# Time travel
spark.read.format("delta") \
    .option("versionAsOf", 10) \
    .load("s3://lake/orders")

# Cleanup old files
delta_table.vacuum(retentionHours=168)
```

## DataOps Patterns

**CI/CD for data pipelines:**
- Unit test transformations with `dbt test` and `pytest` on sample data
- Integration tests: run pipeline against staging environment with production-size sample
- Data diff: compare row counts + key metrics before/after deploy
- Rollback: keep previous dbt run artifacts; re-run previous version on failure

**Cost optimization:**
- Partition by date + entity; avoid partitions smaller than 1 GB (Parquet)
- Target Parquet file sizes: 512 MB – 1 GB
- Lifecycle policies: Standard → IA after 30 days → Glacier after 90 days
- Use spot/preemptible instances for batch; on-demand for streaming
- Predicate pushdown and partition pruning reduce bytes scanned

**Data mesh principles:**
- Domain teams own their data products end-to-end
- Each product has a defined schema contract and SLA
- Self-serve infrastructure: standardized templates for ingestion, quality, catalog registration
- Federated governance: central standards, decentralized execution

## Observability

Key metrics to track:
- Records processed / failed per run
- Data freshness (time since last successful load)
- Quality gate pass rate (% of expectations passing)
- Pipeline execution time trend
- Cost per TB processed

Alerting thresholds:
- CRITICAL: pipeline failure, quality gate <95% pass rate, freshness breach
- WARNING: execution time >2x baseline, cost spike >20%

## Constraints

**MUST DO**
- Validate data before writing to production sinks
- Implement dead-letter queues for invalid records
- Track `_extracted_at` and `_source` metadata in every raw table
- Use idempotent writes (upsert/merge) — pipelines must be re-runnable
- Define freshness SLAs and alert when breached
- Protect PII with masking/tokenization at ingestion

**MUST NOT DO**
- Write directly to production tables without a staging layer
- Run migrations or schema changes without backward compatibility plan
- Process PII without data classification and access controls
- Commit secrets or credentials to code or DAG definitions
- Skip monitoring and alerting on new pipelines
