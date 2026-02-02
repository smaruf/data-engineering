# Spark Optimization Best Practices

## Quick Reference

| Issue | Solution | Impact |
|-------|----------|--------|
| Slow shuffles | Broadcast joins, pre-partition data | 10-100x faster |
| OOM errors | Increase executor memory, reduce partition size | Stability |
| Skewed data | Salting, adaptive query execution | 5-50x faster |
| Small files | OPTIMIZE, auto-compaction | 2-10x faster |
| Cache misses | Strategic caching, proper storage levels | 2-5x faster |

---

## Configuration Best Practices

### Executor Configuration
```python
# Optimal configuration formula:
# - 5 cores per executor (HDFS throughput sweet spot)
# - 10-16GB memory per executor
# - Total executors = (total cores / cores per executor) - 1 for driver

# Example for cluster with 160 cores, 640GB RAM across 10 nodes
spark.conf.set("spark.executor.instances", "29")  # (160/5) - 1
spark.conf.set("spark.executor.cores", "5")
spark.conf.set("spark.executor.memory", "18g")  # (640/10 nodes / 3 executors per node) * 0.9
spark.conf.set("spark.executor.memoryOverhead", "2g")  # 10-20% of executor memory
```

### Memory Tuning
```python
# Default split: 60% Spark memory, 40% user memory
# Spark memory: 50% storage, 50% execution

# For cache-heavy workloads
spark.conf.set("spark.memory.fraction", "0.6")
spark.conf.set("spark.memory.storageFraction", "0.7")  # More for caching

# For compute-heavy workloads (joins, aggregations)
spark.conf.set("spark.memory.fraction", "0.8")
spark.conf.set("spark.memory.storageFraction", "0.3")  # More for execution
```

### Adaptive Query Execution (Spark 3.0+)
```python
# Enable AQE for automatic optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")

# Fine-tune AQE
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64MB")
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionNum", "1")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
```

---

## Data Partitioning

### Rule: 128MB per partition
```python
def calculate_optimal_partitions(data_size_gb):
    """Target 128MB per partition"""
    partition_size_mb = 128
    return int((data_size_gb * 1024) / partition_size_mb)

# Example: 100GB dataset
optimal_partitions = calculate_optimal_partitions(100)  # ~800 partitions
df = df.repartition(optimal_partitions)
```

### Repartition vs Coalesce
```python
# Repartition: Full shuffle, can increase/decrease
df_large = df.repartition(1000)  # Increase for parallel processing
df_by_key = df.repartition(200, "customer_id")  # Co-locate by key

# Coalesce: No shuffle, can only decrease
df_small = df.filter(col("status") == "active")  # Filtered to 10%
df_small = df_small.coalesce(100)  # Efficiently reduce partitions
```

### Partition Before Joins
```python
# Write data partitioned by join key
orders.write.partitionBy("customer_id").parquet("orders/")
customers.write.partitionBy("customer_id").parquet("customers/")

# Join without shuffle (data already co-located)
orders_df = spark.read.parquet("orders/")
customers_df = spark.read.parquet("customers/")
result = orders_df.join(customers_df, "customer_id")  # No shuffle!
```

---

## Join Optimization

### Broadcast Joins (< 10MB)
```python
from pyspark.sql.functions import broadcast

# Manually broadcast small table
large_df.join(broadcast(small_df), "key")

# Auto-broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024)  # 10MB

# Disable auto-broadcast if needed
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
```

### Join Strategies
```python
# 1. Broadcast Hash Join (small table)
# - Best for small dimension tables (< 10MB)
# - No shuffle required

# 2. Shuffle Hash Join
# - Medium-sized tables
# - Both sides shuffled and hashed

# 3. Sort Merge Join (default for large tables)
# - Large tables
# - Both sides sorted then merged

# Force specific join strategy
df1.join(df2, "key").hint("merge")  # Force sort-merge join
df1.join(df2, "key").hint("shuffle_hash")  # Force shuffle hash join
```

### Pre-Aggregate Before Join
```python
# ❌ BAD: Join then aggregate
result = (large_fact
    .join(dimension, "product_id")
    .groupBy("category").agg(sum("sales")))

# ✅ GOOD: Aggregate then join (much smaller dataset)
aggregated = large_fact.groupBy("product_id").agg(sum("sales").alias("total_sales"))
result = aggregated.join(dimension, "product_id").groupBy("category").agg(sum("total_sales"))
```

---

## Handling Data Skew

### Detect Skew
```python
def detect_skew(df, partition_col):
    """Detect data skew in partitions"""
    stats = df.groupBy(partition_col).count()
    stats_summary = stats.select(
        max("count").alias("max"),
        avg("count").alias("avg"),
        min("count").alias("min")
    ).collect()[0]
    
    skew_ratio = stats_summary["max"] / stats_summary["avg"]
    print(f"Skew ratio: {skew_ratio:.2f}x")
    
    if skew_ratio > 3:
        print("⚠️ High skew detected!")
        stats.orderBy(col("count").desc()).show(10)
    
    return skew_ratio
```

### Fix Skew with Salting
```python
from pyspark.sql.functions import concat, lit, rand, floor

def salt_skewed_join(large_df, small_df, join_key, salt_factor=10):
    """
    Salt skewed join key to distribute load
    """
    # Add salt to large table
    large_salted = large_df.withColumn(
        "salt", floor(rand() * salt_factor).cast("int")
    ).withColumn(
        f"{join_key}_salted",
        concat(col(join_key), lit("_"), col("salt"))
    )
    
    # Replicate small table
    from pyspark.sql.functions import explode, array
    small_salted = small_df.withColumn(
        "salt",
        explode(array([lit(i) for i in range(salt_factor)]))
    ).withColumn(
        f"{join_key}_salted",
        concat(col(join_key), lit("_"), col("salt"))
    )
    
    # Join on salted key
    result = large_salted.join(small_salted, f"{join_key}_salted")
    return result.drop("salt", f"{join_key}_salted")
```

### Use AQE for Automatic Skew Handling
```python
# Spark 3.0+ automatically detects and handles skew
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# AQE will split large partitions and join them separately
result = large_df.join(small_df, "key")  # Automatically optimized
```

---

## Caching Strategies

### When to Cache
```python
# ✅ Cache when:
# - DataFrame used multiple times
# - After expensive operations (joins, aggregations)
# - Iterative algorithms (ML training)

expensive_df = (df
    .join(dim1, "key1")
    .join(dim2, "key2")
    .filter(col("amount") > 1000)
    .cache())  # Used multiple times below

# Use cached DataFrame
summary1 = expensive_df.groupBy("category").agg(sum("amount"))
summary2 = expensive_df.groupBy("region").agg(avg("amount"))
summary3 = expensive_df.groupBy("date").agg(count("*"))

# Don't forget to unpersist
expensive_df.unpersist()
```

### Storage Levels
```python
from pyspark.storagelevel import StorageLevel

# MEMORY_ONLY: Fastest, but can cause OOM
df.persist(StorageLevel.MEMORY_ONLY)

# MEMORY_AND_DISK: Safe default (spills to disk)
df.persist(StorageLevel.MEMORY_AND_DISK)

# MEMORY_ONLY_SER: Serialized in memory (saves space)
df.persist(StorageLevel.MEMORY_ONLY_SER)

# DISK_ONLY: For very large datasets
df.persist(StorageLevel.DISK_ONLY)

# OFF_HEAP: Use off-heap memory (requires configuration)
df.persist(StorageLevel.OFF_HEAP)
```

---

## File Formats

### Choose Right Format
```python
# Parquet (default choice)
# - Columnar format (great for analytics)
# - Compression
# - Schema evolution
# - Predicate pushdown
df.write.parquet("output/")

# ORC (optimized for Hive)
# - Better compression than Parquet
# - ACID support
df.write.orc("output/")

# Avro (schema evolution)
# - Row-based format
# - Good for write-heavy workloads
df.write.format("avro").save("output/")

# CSV (avoid for production)
# - Slow
# - No schema enforcement
# - Use only for human-readable output
```

### Optimize Parquet Writes
```python
# Set optimal row group size
spark.conf.set("spark.sql.parquet.block.size", 134217728)  # 128MB

# Enable compression
spark.conf.set("spark.sql.parquet.compression.codec", "snappy")  # Fast
# Or "gzip" for better compression, slower
# Or "zstd" for balance (Spark 3.0+)

# Enable statistics
spark.conf.set("spark.sql.parquet.filterPushdown", "true")
spark.conf.set("spark.sql.parquet.mergeSchema", "false")  # Unless needed
```

---

## Catalyst Optimizer

### Understand Query Plans
```python
# View execution plan
df.explain()  # Basic plan
df.explain(True)  # Extended plan (logical and physical)
df.explain("formatted")  # Pretty-printed plan

# Check for issues
plan = df._jdf.queryExecution().toString()

# Red flags:
# - CartesianProduct (very slow!)
# - Many Exchange operations (shuffles)
# - Missing BroadcastExchange for small tables
```

### Optimize for Catalyst
```python
# ✅ GOOD: Predicate pushdown
df = spark.read.parquet("large_dataset/")
result = df.filter(col("date") >= "2024-01-01")  # Filter pushed to read

# ✅ GOOD: Projection pushdown
result = df.select("customer_id", "amount")  # Only read needed columns

# ❌ BAD: Filter after expensive operation
df = spark.read.parquet("large_dataset/")
df = df.join(other_df, "key")  # Expensive
df = df.filter(col("date") >= "2024-01-01")  # Too late!

# ✅ GOOD: Filter early
df = spark.read.parquet("large_dataset/").filter(col("date") >= "2024-01-01")
df = df.join(other_df, "key")  # Join smaller dataset
```

---

## Monitoring and Debugging

### Spark UI Metrics
```python
# Key metrics to monitor:
# 1. Duration: How long each stage takes
# 2. Shuffle Read/Write: Data movement
# 3. Spill (Memory/Disk): Memory pressure
# 4. GC Time: Garbage collection overhead
# 5. Task Skew: Uneven work distribution

# Access Spark UI: http://driver:4040
```

### Enable Detailed Logging
```python
# Set log level
spark.sparkContext.setLogLevel("INFO")  # or "DEBUG" for more detail

# Configure log4j.properties
log4j.logger.org.apache.spark=INFO
log4j.logger.org.apache.spark.sql=DEBUG
```

### Add Custom Metrics
```python
from pyspark.sql.functions import current_timestamp, lit

def add_metrics(df, stage_name):
    """Add custom metrics to DataFrame"""
    return df.withColumn(
        "_metric_stage", lit(stage_name)
    ).withColumn(
        "_metric_timestamp", current_timestamp()
    )

df = add_metrics(df, "after_join")
```

---

## Complete Example: Optimized ETL

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Configure Spark
spark = (SparkSession.builder
    .appName("OptimizedETL")
    .config("spark.executor.instances", "20")
    .config("spark.executor.cores", "5")
    .config("spark.executor.memory", "16g")
    .config("spark.executor.memoryOverhead", "3g")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024)
    .getOrCreate())

# Read data with partition pruning
orders = (spark.read.parquet("orders/")
    .filter(col("order_date") >= "2024-01-01")  # Predicate pushdown
    .select("order_id", "customer_id", "product_id", "amount"))  # Projection pushdown

# Broadcast small dimension tables
products = spark.read.parquet("products/")
customers = spark.read.parquet("customers/")

# Optimize partitioning
optimal_partitions = 200
orders = orders.repartition(optimal_partitions, "customer_id")

# Cache frequently used data
orders.cache()

# Broadcast joins for dimensions
enriched = (orders
    .join(broadcast(customers), "customer_id")
    .join(broadcast(products), "product_id"))

# Aggregate efficiently
daily_sales = (enriched
    .groupBy("order_date", "customer_id")
    .agg(
        sum("amount").alias("total_amount"),
        count("*").alias("order_count")
    ))

# Write optimized Parquet
(daily_sales.write
    .mode("overwrite")
    .partitionBy("order_date")
    .option("compression", "snappy")
    .parquet("daily_sales/"))

# Cleanup
orders.unpersist()
spark.stop()
```

---

## Troubleshooting Guide

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Tasks running but slow | Large shuffles | Broadcast joins, pre-partition |
| OOM errors | Insufficient memory | Increase executor memory, reduce partition size |
| Long GC pauses | Too many objects | Increase memory, use Kryo serialization |
| Straggler tasks | Data skew | Salting, enable AQE skew join |
| Many small files | Small partitions | Coalesce, optimize writes |
| High shuffle write | Unnecessary shuffles | Filter early, reuse partitioning |

---

## Checklist

### Before Running
- [ ] Configure executors properly (5 cores, 10-16GB each)
- [ ] Enable AQE
- [ ] Set appropriate shuffle partitions
- [ ] Choose right file format (Parquet)

### During Development
- [ ] Filter early (predicate pushdown)
- [ ] Select only needed columns (projection pushdown)
- [ ] Broadcast small tables (< 10MB)
- [ ] Cache reused DataFrames
- [ ] Repartition by join keys

### After Running
- [ ] Check Spark UI for bottlenecks
- [ ] Monitor shuffle and spill metrics
- [ ] Look for skewed tasks
- [ ] Verify file sizes (128MB ideal)
- [ ] Unpersist cached DataFrames

---

**Remember**: Profile first, optimize second. Focus on the biggest bottlenecks for maximum impact.
