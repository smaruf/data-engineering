# Delta Lake Best Practices

## Core Principles

1. **ACID Transactions**: All operations are atomic, consistent, isolated, and durable
2. **Schema Evolution**: Handle schema changes gracefully
3. **Time Travel**: Access historical versions
4. **Performance**: Optimize for query speed
5. **Maintenance**: Regular optimization and cleanup

---

## Table Creation and Schema

### Create Table with Best Practices
```python
from delta.tables import DeltaTable

# Define schema explicitly (recommended)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DecimalType

schema = StructType([
    StructField("order_id", StringType(), nullable=False),
    StructField("customer_id", StringType(), nullable=False),
    StructField("amount", DecimalType(10,2), nullable=False),
    StructField("order_date", StringType(), nullable=False)
])

# Create with properties
(df.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("order_date")  # Partition by commonly filtered column
    .option("delta.autoOptimize.optimizeWrite", "true")
    .option("delta.autoOptimize.autoCompact", "true")
    .save("/path/to/delta/table"))

# Or SQL DDL
spark.sql("""
    CREATE TABLE orders (
        order_id STRING NOT NULL,
        customer_id STRING NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        order_date STRING NOT NULL
    )
    USING DELTA
    PARTITIONED BY (order_date)
    LOCATION '/path/to/delta/table'
    TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true',
        'delta.enableChangeDataFeed' = 'true'
    )
""")
```

### Schema Evolution
```python
# Enable schema evolution
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")

# Append with new columns
new_df_with_extra_cols.write.format("delta").mode("append").option("mergeSchema", "true").save("/path/to/table")

# Explicitly evolve schema
spark.sql("""
    ALTER TABLE orders 
    ADD COLUMNS (
        shipping_address STRING,
        tax_amount DECIMAL(10,2)
    )
""")

# Change column type (limited support)
spark.sql("ALTER TABLE orders ALTER COLUMN amount TYPE DECIMAL(12,2)")
```

---

## Write Operations

### Append Mode
```python
# Standard append
new_df.write.format("delta").mode("append").save("/path/to/table")

# Optimized append (larger, fewer files)
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
new_df.write.format("delta").mode("append").save("/path/to/table")
```

### Overwrite Mode
```python
# Overwrite entire table
df.write.format("delta").mode("overwrite").save("/path/to/table")

# Overwrite specific partitions
df.write.format("delta").mode("overwrite").option("replaceWhere", "order_date >= '2024-01-01'").save("/path/to/table")

# Dynamic partition overwrite
spark.conf.set("spark.databricks.delta.dynamicPartitionOverwrite.enabled", "true")
df.write.format("delta").mode("overwrite").save("/path/to/table")
```

### MERGE (Upsert)
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/path/to/table")

# Simple upsert
(delta_table.alias("target")
    .merge(source_df.alias("source"), "target.order_id = source.order_id")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())

# Complex upsert with conditions
(delta_table.alias("target")
    .merge(source_df.alias("source"), "target.order_id = source.order_id")
    .whenMatchedUpdate(
        condition="source.updated_at > target.updated_at",
        set={
            "amount": "source.amount",
            "status": "source.status",
            "updated_at": "source.updated_at"
        }
    )
    .whenNotMatchedInsert(
        values={
            "order_id": "source.order_id",
            "customer_id": "source.customer_id",
            "amount": "source.amount",
            "order_date": "source.order_date",
            "created_at": "source.created_at"
        }
    )
    .execute())

# SCD Type 2 with MERGE
(delta_table.alias("target")
    .merge(source_df.alias("source"), 
           "target.customer_id = source.customer_id AND target.is_current = true")
    .whenMatchedUpdate(
        condition="target.email != source.email OR target.phone != source.phone",
        set={"is_current": "false", "end_date": "current_timestamp()"}
    )
    .whenNotMatchedInsertAll()
    .execute())

# Then insert new current records
new_current = source_df.join(
    delta_table.toDF().filter("is_current = false"),
    ["customer_id"],
    "inner"
)
new_current.write.format("delta").mode("append").save("/path/to/table")
```

---

## Optimization

### OPTIMIZE Command
```python
# Compact small files
spark.sql("OPTIMIZE delta.`/path/to/table`")

# With Z-Ordering (multi-dimensional clustering)
spark.sql("OPTIMIZE delta.`/path/to/table` ZORDER BY (customer_id, product_id)")

# For specific partition
spark.sql("OPTIMIZE delta.`/path/to/table` WHERE order_date >= '2024-01-01'")

# Python API
from delta.tables import DeltaTable
delta_table = DeltaTable.forPath(spark, "/path/to/table")
delta_table.optimize().executeCompaction()
delta_table.optimize().executeZOrderBy("customer_id", "product_id")
```

### Z-Ordering Best Practices
```python
# Choose columns for Z-Ordering:
# ✅ High cardinality columns
# ✅ Frequently used together in filters
# ✅ Limit to 3-4 columns (diminishing returns)

# Good example: E-commerce orders
spark.sql("OPTIMIZE orders ZORDER BY (customer_id, product_id, order_date)")

# Query benefits from Z-Ordering
result = spark.read.format("delta").load("orders") \
    .filter((col("customer_id") == "C12345") & 
            (col("product_id") == "P67890") &
            (col("order_date") >= "2024-01-01"))
# Much faster with Z-Ordering!

# ❌ Bad: Low cardinality columns
spark.sql("OPTIMIZE orders ZORDER BY (status)")  # Only few values
```

### Auto-Optimization
```python
# Enable auto-optimize for all new tables
spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", "true")
spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.autoCompact", "true")

# Or per table
spark.sql("""
    ALTER TABLE orders SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

# What auto-optimize does:
# - optimizeWrite: Writes larger files (fewer small files)
# - autoCompact: Automatically runs OPTIMIZE after write
```

---

## Time Travel

### Query Historical Versions
```python
# By version number
df = spark.read.format("delta").option("versionAsOf", 5).load("/path/to/table")

# By timestamp
df = spark.read.format("delta").option("timestampAsOf", "2024-01-15").load("/path/to/table")

# SQL syntax
df = spark.sql("SELECT * FROM table_name VERSION AS OF 5")
df = spark.sql("SELECT * FROM table_name TIMESTAMP AS OF '2024-01-15'")

# View history
history = spark.sql("DESCRIBE HISTORY table_name")
history.show(truncate=False)

# Restore to previous version
spark.sql("RESTORE TABLE table_name TO VERSION AS OF 5")
```

### Time Travel Use Cases
```python
# 1. Audit and compliance
def audit_changes(table_path, start_version, end_version):
    """Compare two versions to see what changed"""
    df_old = spark.read.format("delta").option("versionAsOf", start_version).load(table_path)
    df_new = spark.read.format("delta").option("versionAsOf", end_version).load(table_path)
    
    # Find differences
    changed = df_new.subtract(df_old)
    return changed

# 2. Rollback bad data
# Discover issue in version 10
# Restore to version 9
spark.sql("RESTORE TABLE orders TO VERSION AS OF 9")

# 3. A/B testing
df_before = spark.read.format("delta").option("timestampAsOf", "2024-01-01").load("metrics")
df_after = spark.read.format("delta").option("timestampAsOf", "2024-01-15").load("metrics")
```

---

## Maintenance

### VACUUM
```python
# Remove old data files (not used by current version)
# Default retention: 7 days (168 hours)
spark.sql("VACUUM delta.`/path/to/table`")

# Custom retention
spark.sql("VACUUM delta.`/path/to/table` RETAIN 168 HOURS")

# Dry run (see what would be deleted)
spark.sql("VACUUM delta.`/path/to/table` DRY RUN")

# Aggressive vacuum (dangerous! breaks time travel)
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
spark.sql("VACUUM delta.`/path/to/table` RETAIN 0 HOURS")
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "true")

# Best practice: Schedule regular vacuum
def scheduled_vacuum(table_path, retention_hours=168):
    """Run weekly vacuum with 7-day retention"""
    spark.sql(f"VACUUM delta.`{table_path}` RETAIN {retention_hours} HOURS")
    
    # Log results
    detail = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]
    print(f"Table size after vacuum: {detail['sizeInBytes'] / (1024**3):.2f} GB")
```

### Statistics
```python
# Collect statistics for query optimization
spark.sql("ANALYZE TABLE orders COMPUTE STATISTICS")

# Column-level statistics
spark.sql("ANALYZE TABLE orders COMPUTE STATISTICS FOR COLUMNS customer_id, product_id, amount")

# Check statistics
stats = spark.sql("DESCRIBE EXTENDED orders")
stats.show(truncate=False)
```

---

## Change Data Feed (CDC)

### Enable CDC
```python
# Enable CDC on table
spark.sql("""
    ALTER TABLE orders 
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Or at creation
spark.sql("""
    CREATE TABLE orders (...)
    USING DELTA
    TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
```

### Read Change Data
```python
# Read changes between versions
changes = (spark.read.format("delta")
    .option("readChangeDataFeed", "true")
    .option("startingVersion", 5)
    .option("endingVersion", 10)
    .load("/path/to/table"))

# Change data columns:
# - _change_type: 'insert', 'update_preimage', 'update_postimage', 'delete'
# - _commit_version: Version number
# - _commit_timestamp: Timestamp of change

# Filter for specific change types
inserts = changes.filter(col("_change_type") == "insert")
updates = changes.filter(col("_change_type").like("update%"))
deletes = changes.filter(col("_change_type") == "delete")

# Stream processing of changes
change_stream = (spark.readStream
    .format("delta")
    .option("readChangeDataFeed", "true")
    .option("startingVersion", "latest")
    .load("/path/to/table"))
```

---

## Partitioning Strategy

### When to Partition
```python
# ✅ Partition when:
# - Queries frequently filter on column (e.g., date)
# - Large table (> 1TB)
# - Each partition will be > 1GB

# ❌ Don't partition when:
# - Small tables (< 100GB)
# - Too many partitions (> 10,000)
# - High cardinality column (millions of values)

# Good partitioning
df.write.partitionBy("order_date").format("delta").save("orders/")
# Result: orders/order_date=2024-01-01/*.parquet

# Bad partitioning
df.write.partitionBy("order_id").format("delta").save("orders/")
# Result: Millions of tiny partitions!
```

### Partition Pruning
```python
# Ensure queries benefit from partitioning
# ✅ GOOD: Partition pruning works
df = spark.read.format("delta").load("orders/") \
    .filter(col("order_date") >= "2024-01-01")
# Only reads relevant partitions

# ❌ BAD: No partition pruning
df = spark.read.format("delta").load("orders/") \
    .filter(year(col("order_date")) == 2024)
# Reads all partitions! Function prevents pruning
```

---

## Concurrent Writes

### Isolation Levels
```python
# Default: Serializable (safest, may have conflicts)
# WriteSerializable: Allow concurrent writes to different partitions

spark.conf.set("spark.databricks.delta.properties.defaults.isolationLevel", "WriteSerializable")

# Or per table
spark.sql("""
    ALTER TABLE orders 
    SET TBLPROPERTIES ('delta.isolationLevel' = 'WriteSerializable')
""")
```

### Handling Conflicts
```python
from delta.tables import DeltaTable
from pyspark.sql.utils import AnalysisException
import time

def write_with_retry(df, path, max_retries=3):
    """Write with automatic retry on conflict"""
    for attempt in range(max_retries):
        try:
            df.write.format("delta").mode("append").save(path)
            print(f"Write successful on attempt {attempt + 1}")
            return
        except AnalysisException as e:
            if "ConcurrentAppendException" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Conflict detected, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
```

---

## Streaming with Delta

### Structured Streaming Sink
```python
# Write stream to Delta
query = (streaming_df.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/checkpoints/orders")
    .trigger(processingTime="10 seconds")
    .start("/path/to/delta/table"))

# Read stream from Delta
streaming_df = (spark.readStream
    .format("delta")
    .load("/path/to/delta/table"))

# Process CDC stream
change_stream = (spark.readStream
    .format("delta")
    .option("readChangeDataFeed", "true")
    .option("startingVersion", 0)
    .load("/path/to/delta/table"))
```

---

## Performance Benchmarks

### File Size Impact
```
Small files (1MB):   Query time: 10s
Optimal files (128MB): Query time: 2s
Large files (1GB):   Query time: 3s

Recommendation: 128MB-512MB files
```

### Z-Ordering Impact
```
Without Z-Order: 10s query time
With Z-Order:    2s query time (5x improvement)

Most effective for:
- Multi-column filters
- High cardinality columns
- Large tables
```

### Partition Pruning Impact
```
Full table scan:    100s
With partitioning:  10s (10x improvement)

Requires:
- Filter on partition column
- Sargable predicates
```

---

## Checklist

### Table Design
- [ ] Define schema explicitly
- [ ] Choose appropriate partition column (date recommended)
- [ ] Enable auto-optimize
- [ ] Set retention policy
- [ ] Enable CDC if needed

### Write Operations
- [ ] Use MERGE for upserts
- [ ] Enable optimizeWrite
- [ ] Handle concurrent writes
- [ ] Validate schema compatibility

### Optimization
- [ ] Run OPTIMIZE weekly
- [ ] Z-Order on frequently filtered columns
- [ ] Monitor file sizes (128MB ideal)
- [ ] Check partition count (< 10,000)

### Maintenance
- [ ] VACUUM regularly (retain 7+ days)
- [ ] Update statistics monthly
- [ ] Monitor storage costs
- [ ] Archive old partitions

---

**Remember**: Delta Lake provides ACID guarantees, but proper maintenance and optimization are crucial for performance at scale.
