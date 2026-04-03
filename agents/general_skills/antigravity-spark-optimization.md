---
name: spark-optimization
description: "Optimize Apache Spark jobs -- partitioning, caching, shuffle, memory tuning, and AQE."
---

# Apache Spark Optimization

Production patterns for optimizing Spark jobs: partitioning strategies, join optimization, shuffle reduction, memory management, and Adaptive Query Execution (AQE). Use when Spark jobs are slow, memory-constrained, or need to scale.

## Key Patterns

- **Enable AQE first**: `spark.sql.adaptive.enabled=true` handles partition coalescing, skew joins, and broadcast thresholds automatically
- **Right-size partitions**: Target 128-256 MB per partition; use `coalesce()` (no shuffle) to reduce, `repartition()` to increase
- **Broadcast small tables**: `F.broadcast(small_df)` for joins where one side is <50 MB -- eliminates shuffle entirely
- **Handle data skew**: Enable `spark.sql.adaptive.skewJoin.enabled=true`; for severe skew, use salting (add random prefix to join key)
- **Column pruning + predicate pushdown**: Select only needed columns and filter early -- Spark pushes predicates to Parquet/Delta readers
- **Use Parquet/Delta**: Columnar formats with compression; write with `partitionBy()` for partition pruning on read
- **Cache strategically**: `df.persist(StorageLevel.MEMORY_AND_DISK_SER)` only when reused multiple times; unpersist when done
- **Avoid UDFs**: Use built-in `pyspark.sql.functions` instead -- UDFs disable Catalyst optimization
- **Shuffle compression**: `spark.io.compression.codec=lz4` and `spark.shuffle.compress=true`
- **Don't collect large data**: Keep data distributed; use `.take(1)` instead of `.count()` for existence checks

## Quick Reference

### Performance Factor Cheat Sheet

| Factor | Impact | Solution |
|:-------|:-------|:---------|
| Shuffle | Network + disk I/O | Minimize wide transforms, broadcast joins |
| Data skew | Uneven task duration | Salting, AQE skew join |
| Serialization | CPU overhead | Kryo serializer, columnar formats |
| Memory | GC pressure, spills | Tune executor memory, right-size partitions |
| Partitions | Parallelism | 128-256 MB per partition |

### Optimized Session Template

```python
from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.executor.memory", "8g")
    .config("spark.executor.memoryOverhead", "2g")
    .config("spark.sql.autoBroadcastJoinThreshold", "50MB")
    .config("spark.sql.files.maxPartitionBytes", "128MB")
    .config("spark.io.compression.codec", "lz4")
    .getOrCreate())
```

### Common Operations

```python
# Efficient read + transform
result = (spark.read.parquet("s3://bucket/data/")
    .filter(F.col("date") >= "2024-01-01")        # predicate pushdown
    .select("id", "amount", "category")             # column pruning
    .groupBy("category")
    .agg(F.sum("amount").alias("total")))

# Broadcast join (small table < 50MB)
result = large_df.join(F.broadcast(small_df), on="key", how="left")

# Partitioned write
result.write.partitionBy("year", "month").mode("overwrite").parquet("s3://out/")

# Reduce partitions without shuffle
df_reduced = df.coalesce(10)

# Cache for reuse (unpersist when done)
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK_SER)
df.count()  # materialize
# ... use df multiple times ...
df.unpersist()

# Debug: check partition skew
df.withColumn("pid", F.spark_partition_id()).groupBy("pid").count().show()

# Debug: explain plan
df.explain(mode="extended")
```

### Do's and Don'ts

| Do | Don't |
|:---|:------|
| Enable AQE | Use UDFs when built-ins exist |
| Use Parquet/Delta | Collect large data to driver |
| Broadcast small tables | Over-cache (memory is limited) |
| Filter + select early | Ignore data skew |
| Use `coalesce` to reduce partitions | Use `.count()` for existence (use `.take(1)`) |
| Monitor Spark UI for spills/skew | Use `repartition` when `coalesce` suffices |

## When to Use

- Spark jobs running slower than expected or hitting OOM errors
- Tuning executor memory, partition counts, or shuffle configuration
- Optimizing joins between large tables or handling skewed join keys
- Scaling data pipelines from gigabytes to terabytes
- Choosing between caching, checkpointing, and bucketing strategies

## Resources

- [Spark Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Spark Configuration](https://spark.apache.org/docs/latest/configuration.html)
- [Databricks Optimization Guide](https://docs.databricks.com/en/optimizations/index.html)
