# Performance Tuning Guide for Data Engineering

## Table of Contents
1. [Spark Performance Tuning](#spark-performance-tuning)
2. [Delta Lake Optimization](#delta-lake-optimization)
3. [Azure Synapse Optimization](#azure-synapse-optimization)
4. [Query Optimization Techniques](#query-optimization-techniques)
5. [Benchmarking Strategies](#benchmarking-strategies)

---

## Spark Performance Tuning

### Understanding Spark Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    DRIVER PROGRAM                         │
│  • SparkContext                                          │
│  • DAG Scheduler                                         │
│  • Task Scheduler                                        │
└────────────────┬─────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │  CLUSTER MANAGER │
        │  (YARN/K8s/etc) │
        └────────┬─────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌───▼─────┐ ┌───▼─────┐
│EXECUTOR │ │EXECUTOR │ │EXECUTOR │
│         │ │         │ │         │
│ Cache   │ │ Cache   │ │ Cache   │
│ Tasks   │ │ Tasks   │ │ Tasks   │
└─────────┘ └─────────┘ └─────────┘
```

### Memory Management

#### Memory Distribution

```
Total Executor Memory (--executor-memory 10G)
├── Reserved Memory (300MB fixed)
└── Usable Memory (9.7GB)
    ├── Spark Memory (60% = 5.82GB)
    │   ├── Storage Memory (50% = 2.91GB)
    │   │   └── Cached data, broadcast variables
    │   └── Execution Memory (50% = 2.91GB)
    │       └── Shuffles, joins, sorts, aggregations
    └── User Memory (40% = 3.88GB)
        └── User data structures, UDFs
```

#### Optimal Memory Configuration

```python
# Configuration for 10GB executor memory
spark.conf.set("spark.executor.memory", "10g")
spark.conf.set("spark.executor.memoryOverhead", "2g")  # 20% overhead for off-heap
spark.conf.set("spark.memory.fraction", "0.6")  # Default, adjust if needed
spark.conf.set("spark.memory.storageFraction", "0.5")  # Balance between storage and execution

# For memory-intensive operations (joins, aggregations)
spark.conf.set("spark.memory.fraction", "0.8")  # More for Spark operations
spark.conf.set("spark.memory.storageFraction", "0.3")  # Less for caching

# Memory tuning example
def configure_spark_memory(executor_memory_gb, workload_type="balanced"):
    """
    Configure Spark memory based on workload type
    
    workload_type:
    - 'balanced': Equal storage and execution
    - 'compute_heavy': More execution memory for shuffles/joins
    - 'cache_heavy': More storage memory for caching
    """
    configs = {
        "balanced": {
            "spark.memory.fraction": "0.6",
            "spark.memory.storageFraction": "0.5"
        },
        "compute_heavy": {
            "spark.memory.fraction": "0.8",
            "spark.memory.storageFraction": "0.3"
        },
        "cache_heavy": {
            "spark.memory.fraction": "0.6",
            "spark.memory.storageFraction": "0.7"
        }
    }
    
    config = configs.get(workload_type, configs["balanced"])
    
    spark.conf.set("spark.executor.memory", f"{executor_memory_gb}g")
    spark.conf.set("spark.executor.memoryOverhead", f"{int(executor_memory_gb * 0.2)}g")
    
    for key, value in config.items():
        spark.conf.set(key, value)
    
    return config

# Usage
configure_spark_memory(executor_memory_gb=10, workload_type="compute_heavy")
```

### Executor and Core Configuration

#### Sizing Executors

```python
# Calculate optimal executor configuration
def calculate_executor_config(total_cores, total_memory_gb, node_count):
    """
    Calculate optimal executor configuration
    
    Rules of thumb:
    - 5 cores per executor (sweet spot for HDFS throughput)
    - Leave 1 core and 1GB for OS/overhead per node
    """
    # Cores per node
    cores_per_node = total_cores // node_count
    usable_cores_per_node = cores_per_node - 1  # Reserve 1 for OS
    
    # Memory per node
    memory_per_node = total_memory_gb // node_count
    usable_memory_per_node = memory_per_node - 1  # Reserve 1GB for OS
    
    # Executors per node (target 5 cores per executor)
    cores_per_executor = 5
    executors_per_node = usable_cores_per_node // cores_per_executor
    
    # Memory per executor
    memory_per_executor = usable_memory_per_node // executors_per_node
    executor_memory = int(memory_per_executor * 0.9)  # 10% for overhead
    memory_overhead = memory_per_executor - executor_memory
    
    # Total executors
    num_executors = executors_per_node * node_count - 1  # -1 for driver
    
    return {
        "num_executors": num_executors,
        "executor_cores": cores_per_executor,
        "executor_memory": f"{executor_memory}g",
        "executor_memory_overhead": f"{memory_overhead}g",
        "driver_memory": f"{executor_memory}g",
        "driver_cores": cores_per_executor
    }

# Example: 10 nodes, 16 cores each, 64GB RAM each
config = calculate_executor_config(
    total_cores=160,
    total_memory_gb=640,
    node_count=10
)

print(f"""
Recommended Configuration:
--num-executors {config['num_executors']}
--executor-cores {config['executor_cores']}
--executor-memory {config['executor_memory']}
--executor-memory-overhead {config['executor_memory_overhead']}
--driver-memory {config['driver_memory']}
--driver-cores {config['driver_cores']}
""")

# Output:
# --num-executors 29
# --executor-cores 5
# --executor-memory 18g
# --executor-memory-overhead 2g
# --driver-memory 18g
# --driver-cores 5
```

### Partitioning Strategies

#### Optimal Partition Size

```python
# Rule of thumb: 128MB per partition
def calculate_optimal_partitions(data_size_gb, executor_cores, num_executors):
    """
    Calculate optimal number of partitions
    
    Rules:
    - 128MB per partition (default block size)
    - 2-3x number of total cores for CPU-bound tasks
    - Can be higher for I/O bound tasks
    """
    # Based on data size
    partition_size_mb = 128
    partitions_by_size = int((data_size_gb * 1024) / partition_size_mb)
    
    # Based on parallelism
    total_cores = executor_cores * num_executors
    partitions_by_cores = total_cores * 3
    
    # Use the larger value, but cap at reasonable limits
    optimal_partitions = max(partitions_by_size, partitions_by_cores)
    optimal_partitions = min(optimal_partitions, 10000)  # Cap at 10k
    
    return {
        "recommended_partitions": optimal_partitions,
        "partitions_by_size": partitions_by_size,
        "partitions_by_cores": partitions_by_cores,
        "partition_size_mb": (data_size_gb * 1024) / optimal_partitions
    }

# Example
data_size_gb = 100
result = calculate_optimal_partitions(
    data_size_gb=100,
    executor_cores=5,
    num_executors=29
)
print(f"Recommended partitions: {result['recommended_partitions']}")
print(f"Resulting partition size: {result['partition_size_mb']:.2f} MB")

# Apply partitioning
df = spark.read.parquet("large_dataset.parquet")
df = df.repartition(result['recommended_partitions'])
```

#### Repartition vs Coalesce

```python
# When to use repartition() vs coalesce()

# Repartition: Full shuffle, can increase or decrease partitions
# Use when:
# - Need to increase partitions
# - Need even distribution
# - Preparing for parallel operations

df_large = df.repartition(1000)  # Increase partitions for parallel processing

# Repartition by column (for joins)
df_partitioned = df.repartition(200, "customer_id")  # Co-locate same customer_id

# Coalesce: No shuffle, can only decrease partitions
# Use when:
# - Reducing partitions after filter
# - Writing to fewer files
# - Already well-distributed data

df_small = df.filter(col("country") == "USA")  # Filtered to 10% of data
df_small = df_small.coalesce(100)  # Reduce partitions efficiently

# Example: Adaptive repartitioning
def adaptive_repartition(df, target_partition_size_mb=128):
    """
    Automatically repartition based on DataFrame size
    """
    # Estimate DataFrame size
    num_partitions = df.rdd.getNumPartitions()
    
    # Sample to estimate size
    sample_df = df.sample(0.01)
    sample_size_bytes = sample_df.rdd.map(lambda row: len(str(row))).sum()
    estimated_size_mb = (sample_size_bytes / 0.01) / (1024 * 1024)
    
    # Calculate optimal partitions
    optimal_partitions = max(1, int(estimated_size_mb / target_partition_size_mb))
    
    print(f"Current partitions: {num_partitions}")
    print(f"Estimated size: {estimated_size_mb:.2f} MB")
    print(f"Optimal partitions: {optimal_partitions}")
    
    # Repartition if needed
    if optimal_partitions < num_partitions * 0.5:
        # Use coalesce for reduction
        return df.coalesce(optimal_partitions)
    elif optimal_partitions > num_partitions * 1.5:
        # Use repartition for increase
        return df.repartition(optimal_partitions)
    else:
        # Already optimal
        return df

# Usage
df_optimized = adaptive_repartition(df)
```

### Shuffle Optimization

#### Understanding Shuffle

Shuffle is expensive because it:
1. Writes data to disk
2. Transfers data over network
3. Reads data from disk
4. Sorts/aggregates data

#### Minimizing Shuffles

```python
# 1. Reduce data before shuffle
# BAD: Shuffle all data then filter
df_bad = (df
    .groupBy("customer_id").agg(sum("amount"))
    .filter(col("sum(amount)") > 1000))

# GOOD: Filter before shuffle
df_good = (df
    .filter(col("amount") > 0)  # Filter first
    .groupBy("customer_id").agg(sum("amount"))
    .filter(col("sum(amount)") > 1000))

# 2. Use broadcast joins for small tables
from pyspark.sql.functions import broadcast

# Small dimension table (< 10MB)
small_table = spark.read.parquet("dimensions/products.parquet")
large_table = spark.read.parquet("facts/orders.parquet")

# Force broadcast join
result = large_table.join(broadcast(small_table), "product_id")

# Auto broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024)  # 10MB

# 3. Partition by join key to avoid shuffle
# Write data partitioned by join key
orders.write.partitionBy("customer_id").parquet("orders_partitioned/")
customers.write.partitionBy("customer_id").parquet("customers_partitioned/")

# Join without shuffle (co-located data)
orders_df = spark.read.parquet("orders_partitioned/")
customers_df = spark.read.parquet("customers_partitioned/")
result = orders_df.join(customers_df, "customer_id")

# 4. Reduce shuffle partitions for small datasets
# Default is 200, too many for small data
spark.conf.set("spark.sql.shuffle.partitions", "50")

# Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

#### Handling Data Skew

```python
# Data skew: Some partitions have much more data than others

# 1. Detect skew
def detect_skew(df, partition_col):
    """
    Detect data skew in partitions
    """
    partition_counts = (df
        .groupBy(partition_col)
        .count()
        .orderBy(col("count").desc()))
    
    stats = partition_counts.select(
        avg("count").alias("avg_count"),
        max("count").alias("max_count"),
        min("count").alias("min_count")
    ).collect()[0]
    
    skew_ratio = stats.max_count / stats.avg_count
    
    print(f"Average count per partition: {stats.avg_count:.0f}")
    print(f"Max count per partition: {stats.max_count}")
    print(f"Skew ratio: {skew_ratio:.2f}x")
    
    if skew_ratio > 3:
        print("⚠️ Significant skew detected!")
        partition_counts.show(10)
    
    return skew_ratio

# 2. Fix skew with salting
def salt_join(large_df, small_df, join_key, salt_factor=10):
    """
    Use salting to handle skewed joins
    """
    from pyspark.sql.functions import concat, lit, rand, floor
    
    # Add salt to large table
    salted_large = large_df.withColumn(
        "salt",
        floor(rand() * salt_factor).cast("int")
    ).withColumn(
        f"salted_{join_key}",
        concat(col(join_key), lit("_"), col("salt"))
    )
    
    # Replicate small table
    from pyspark.sql.functions import explode, array
    
    salted_small = small_df.withColumn(
        "salt",
        explode(array([lit(i) for i in range(salt_factor)]))
    ).withColumn(
        f"salted_{join_key}",
        concat(col(join_key), lit("_"), col("salt"))
    )
    
    # Join on salted key
    result = salted_large.join(
        salted_small,
        f"salted_{join_key}"
    ).drop("salt", f"salted_{join_key}")
    
    return result

# 3. Adaptive Query Execution for skew
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# AQE will automatically detect and handle skew
result = large_df.join(small_df, "join_key")
```

### Caching and Persistence

```python
from pyspark.storagelevel import StorageLevel

# When to cache:
# ✅ DataFrame used multiple times
# ✅ After expensive operations
# ✅ Iterative algorithms
# ❌ Large DataFrames used once
# ❌ Already reading from fast storage

# Cache levels
cache_levels = {
    "MEMORY_ONLY": StorageLevel.MEMORY_ONLY,  # Default for cache()
    "MEMORY_AND_DISK": StorageLevel.MEMORY_AND_DISK,  # Spill to disk
    "MEMORY_ONLY_SER": StorageLevel.MEMORY_ONLY_SER,  # Serialized (less memory)
    "DISK_ONLY": StorageLevel.DISK_ONLY,  # Disk only
    "OFF_HEAP": StorageLevel.OFF_HEAP  # Off-heap memory
}

# Example: Complex transformation used multiple times
expensive_df = (df
    .join(dim_customers, "customer_id")
    .join(dim_products, "product_id")
    .withColumn("profit", col("revenue") - col("cost"))
    .filter(col("profit") > 0))

# Cache with appropriate level
expensive_df.persist(StorageLevel.MEMORY_AND_DISK)

# Use multiple times
daily_summary = expensive_df.groupBy("date").agg(sum("profit"))
monthly_summary = expensive_df.groupBy("month").agg(sum("profit"))
customer_summary = expensive_df.groupBy("customer_id").agg(sum("profit"))

# Don't forget to unpersist when done
expensive_df.unpersist()

# Check cache usage
def check_cache_usage():
    """
    Check current cache usage in cluster
    """
    from pyspark import SparkContext
    sc = SparkContext.getOrCreate()
    
    print("Cached RDDs:")
    for rdd_info in sc._jsc.getPersistentRDDs().values():
        print(f"  {rdd_info.name()}: {rdd_info.getStorageLevel()}")

check_cache_usage()
```

### Catalyst Optimizer and Query Plans

```python
# Understanding query plans

# 1. View logical plan
df.explain(mode="simple")

# 2. View physical plan
df.explain(mode="extended")

# 3. View cost-based optimization
df.explain(mode="cost")

# 4. View formatted plan
df.explain(mode="formatted")

# Example analysis
def analyze_query_plan(df):
    """
    Analyze query plan for optimization opportunities
    """
    plan = df._jdf.queryExecution().toString()
    
    issues = []
    
    # Check for shuffles
    if "Exchange" in plan:
        shuffle_count = plan.count("Exchange")
        issues.append(f"⚠️ {shuffle_count} shuffle(s) detected")
    
    # Check for Cartesian products
    if "CartesianProduct" in plan:
        issues.append("❌ Cartesian product detected - very expensive!")
    
    # Check for broadcast
    if "BroadcastExchange" in plan:
        issues.append("✅ Broadcast join used")
    
    # Check for whole-stage code generation
    if "WholeStageCodegen" in plan:
        issues.append("✅ Whole-stage codegen enabled")
    
    print("\n".join(issues))
    print("\nFull plan:")
    print(plan)
    
    return issues

# Usage
analyze_query_plan(df)

# Optimization example
# Before: Multiple passes over data
total = df.agg(sum("amount")).collect()[0][0]
count = df.count()
avg = df.agg(avg("amount")).collect()[0][0]

# After: Single pass
from pyspark.sql.functions import count as count_func
stats = df.agg(
    sum("amount").alias("total"),
    count_func("*").alias("count"),
    avg("amount").alias("average")
).collect()[0]

total = stats.total
count = stats.count
avg = stats.average
```

### Configuration Tuning

```python
# Comprehensive Spark configuration for performance

def configure_spark_performance(
    data_size_gb,
    executor_memory_gb=16,
    num_executors=20,
    executor_cores=5,
    workload_type="mixed"
):
    """
    Apply performance configurations based on workload
    """
    
    # Memory settings
    configs = {
        "spark.executor.memory": f"{executor_memory_gb}g",
        "spark.executor.memoryOverhead": f"{int(executor_memory_gb * 0.2)}g",
        "spark.driver.memory": f"{executor_memory_gb}g",
        "spark.driver.memoryOverhead": f"{int(executor_memory_gb * 0.2)}g",
        
        # Core settings
        "spark.executor.cores": str(executor_cores),
        "spark.executor.instances": str(num_executors),
        "spark.dynamicAllocation.enabled": "false",  # Disable for consistent performance
        
        # Shuffle settings
        "spark.sql.shuffle.partitions": str(num_executors * executor_cores * 2),
        "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        
        # Broadcast settings
        "spark.sql.autoBroadcastJoinThreshold": "10485760",  # 10MB
        
        # Compression
        "spark.sql.parquet.compression.codec": "snappy",
        "spark.io.compression.codec": "snappy",
        
        # Serialization
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.kryoserializer.buffer.max": "512m",
        
        # Network
        "spark.network.timeout": "800s",
        "spark.executor.heartbeatInterval": "60s",
        
        # Speculation
        "spark.speculation": "true",
        "spark.speculation.multiplier": "3",
        "spark.speculation.quantile": "0.9",
        
        # Tungsten
        "spark.sql.tungsten.enabled": "true",
        "spark.sql.codegen.wholeStage": "true",
        
        # I/O
        "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB
        "spark.sql.files.openCostInBytes": "4194304",  # 4MB
    }
    
    # Workload-specific tuning
    if workload_type == "join_heavy":
        configs.update({
            "spark.sql.autoBroadcastJoinThreshold": "20971520",  # 20MB
            "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
            "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "268435456",  # 256MB
        })
    elif workload_type == "aggregation_heavy":
        configs.update({
            "spark.sql.adaptive.coalescePartitions.minPartitionNum": "1",
            "spark.sql.adaptive.advisoryPartitionSizeInBytes": "67108864",  # 64MB
        })
    elif workload_type == "streaming":
        configs.update({
            "spark.streaming.backpressure.enabled": "true",
            "spark.streaming.kafka.maxRatePerPartition": "10000",
            "spark.sql.streaming.metricsEnabled": "true",
        })
    
    # Apply configurations
    for key, value in configs.items():
        spark.conf.set(key, value)
    
    print(f"Applied {len(configs)} performance configurations")
    return configs

# Usage
configure_spark_performance(
    data_size_gb=500,
    executor_memory_gb=16,
    num_executors=20,
    executor_cores=5,
    workload_type="join_heavy"
)
```

---

## Delta Lake Optimization

### Z-Ordering

```python
# Z-Ordering for multi-dimensional clustering

# Problem: Queries filter on multiple columns
# Solution: Z-Order indexes multiple columns together

# Example: E-commerce orders
orders_df = spark.read.parquet("orders_raw/")

# Write with Z-Ordering
(orders_df.write
 .format("delta")
 .partitionBy("order_date")  # Partition by date
 .save("orders_delta/"))

# Optimize with Z-Order on commonly filtered columns
spark.sql("""
    OPTIMIZE delta.`orders_delta`
    ZORDER BY (customer_id, product_id, status)
""")

# Performance comparison
import time

# Without Z-Order
start = time.time()
result1 = spark.read.format("delta").load("orders_unoptimized/") \
    .filter((col("customer_id") == "C12345") & (col("product_id") == "P67890")) \
    .count()
time_without = time.time() - start

# With Z-Order
start = time.time()
result2 = spark.read.format("delta").load("orders_delta/") \
    .filter((col("customer_id") == "C12345") & (col("product_id") == "P67890")) \
    .count()
time_with = time.time() - start

print(f"Without Z-Order: {time_without:.2f}s")
print(f"With Z-Order: {time_with:.2f}s")
print(f"Improvement: {(time_without/time_with):.2f}x faster")

# Z-Order best practices
def optimize_delta_table(table_path, partition_columns=None, zorder_columns=None):
    """
    Optimize Delta table with best practices
    
    Guidelines for Z-Order columns:
    - Choose columns frequently used together in filters
    - High cardinality columns work best
    - Limit to 3-4 columns (diminishing returns after that)
    - Order matters: put most selective column first
    """
    
    # 1. Compact small files
    print("Compacting small files...")
    spark.sql(f"OPTIMIZE delta.`{table_path}`")
    
    # 2. Apply Z-Ordering
    if zorder_columns:
        print(f"Applying Z-Order on: {zorder_columns}")
        zorder_clause = ", ".join(zorder_columns)
        spark.sql(f"""
            OPTIMIZE delta.`{table_path}`
            ZORDER BY ({zorder_clause})
        """)
    
    # 3. Vacuum old files (keep 7 days)
    print("Vacuuming old files...")
    spark.sql(f"""
        VACUUM delta.`{table_path}` RETAIN 168 HOURS
    """)
    
    # 4. Analyze table statistics
    print("Analyzing table statistics...")
    spark.sql(f"ANALYZE TABLE delta.`{table_path}` COMPUTE STATISTICS")
    
    if zorder_columns:
        for col in zorder_columns:
            spark.sql(f"""
                ANALYZE TABLE delta.`{table_path}` 
                COMPUTE STATISTICS FOR COLUMNS {col}
            """)

# Usage
optimize_delta_table(
    table_path="orders_delta/",
    partition_columns=["order_date"],
    zorder_columns=["customer_id", "product_id", "status"]
)
```

### File Compaction

```python
# Small file problem: Many small files slow down queries

def check_file_statistics(table_path):
    """
    Analyze file size distribution
    """
    files_df = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`")
    
    # Get file statistics
    stats = files_df.select("numFiles", "sizeInBytes").collect()[0]
    num_files = stats.numFiles
    size_bytes = stats.sizeInBytes
    
    avg_file_size_mb = (size_bytes / num_files) / (1024 * 1024)
    
    print(f"Number of files: {num_files:,}")
    print(f"Total size: {size_bytes / (1024**3):.2f} GB")
    print(f"Average file size: {avg_file_size_mb:.2f} MB")
    
    if avg_file_size_mb < 64:
        print("⚠️ Small file problem detected! Run OPTIMIZE.")
    elif avg_file_size_mb > 512:
        print("⚠️ Large file problem detected! Consider repartitioning.")
    else:
        print("✅ File sizes look good")
    
    return {
        "num_files": num_files,
        "avg_file_size_mb": avg_file_size_mb
    }

# Automatic compaction
def auto_compact_delta_table(table_path, target_file_size_mb=128):
    """
    Automatically compact Delta table to target file size
    """
    stats = check_file_statistics(table_path)
    
    if stats["avg_file_size_mb"] < 64:
        print("Running compaction...")
        
        # Enable auto-compaction for future writes
        spark.sql(f"""
            ALTER TABLE delta.`{table_path}`
            SET TBLPROPERTIES (
                'delta.autoOptimize.optimizeWrite' = 'true',
                'delta.autoOptimize.autoCompact' = 'true'
            )
        """)
        
        # Compact existing files
        spark.sql(f"OPTIMIZE delta.`{table_path}`")
        
        # Verify improvement
        new_stats = check_file_statistics(table_path)
        improvement = new_stats["avg_file_size_mb"] / stats["avg_file_size_mb"]
        print(f"Improvement: {improvement:.2f}x larger files")

# Usage
auto_compact_delta_table("orders_delta/")
```

### Vacuum and Time Travel

```python
# Vacuum removes old versions, but breaks time travel

def intelligent_vacuum(table_path, retention_hours=168):
    """
    Vacuum with safety checks
    
    Default retention: 168 hours (7 days)
    Minimum retention: 0 hours (dangerous!)
    """
    
    # Check current table size
    before_stats = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]
    before_size_gb = before_stats.sizeInBytes / (1024**3)
    
    print(f"Current table size: {before_size_gb:.2f} GB")
    print(f"Vacuuming files older than {retention_hours} hours...")
    
    # Disable safety check if needed (be careful!)
    # spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
    
    # Perform vacuum
    spark.sql(f"""
        VACUUM delta.`{table_path}` RETAIN {retention_hours} HOURS
    """)
    
    # Check space saved
    after_stats = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]
    after_size_gb = after_stats.sizeInBytes / (1024**3)
    saved_gb = before_size_gb - after_size_gb
    
    print(f"New table size: {after_size_gb:.2f} GB")
    print(f"Space saved: {saved_gb:.2f} GB ({(saved_gb/before_size_gb*100):.1f}%)")

# Time travel queries
def query_historical_version(table_path, version=None, timestamp=None):
    """
    Query historical version with performance tips
    """
    if version is not None:
        df = spark.read.format("delta").option("versionAsOf", version).load(table_path)
        print(f"Reading version {version}")
    elif timestamp is not None:
        df = spark.read.format("delta").option("timestampAsOf", timestamp).load(table_path)
        print(f"Reading timestamp {timestamp}")
    else:
        df = spark.read.format("delta").load(table_path)
        print("Reading latest version")
    
    return df

# View table history
def analyze_table_history(table_path, limit=20):
    """
    Analyze table history for optimization insights
    """
    history = spark.sql(f"""
        DESCRIBE HISTORY delta.`{table_path}`
        LIMIT {limit}
    """)
    
    # Analyze operation types
    history.groupBy("operation").count().show()
    
    # Show recent operations
    history.select("version", "timestamp", "operation", "operationMetrics").show(truncate=False)
    
    return history

# Usage
intelligent_vacuum("orders_delta/", retention_hours=168)
analyze_table_history("orders_delta/")
```

### Write Optimization

```python
# Optimized writes for Delta Lake

# 1. Optimize Write (fewer, larger files)
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")

# 2. Auto Compact (automatic compaction after write)
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# 3. Optimized writes example
def optimized_delta_write(
    df,
    table_path,
    mode="append",
    partition_by=None,
    optimize_write=True,
    auto_compact=True
):
    """
    Write to Delta with optimizations
    """
    writer = df.write.format("delta").mode(mode)
    
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    
    # Table properties
    options = {}
    if optimize_write:
        options["delta.autoOptimize.optimizeWrite"] = "true"
    if auto_compact:
        options["delta.autoOptimize.autoCompact"] = "true"
    
    for key, value in options.items():
        writer = writer.option(key, value)
    
    # Execute write
    writer.save(table_path)
    
    print(f"Written to {table_path} with optimizations")

# 4. Batch writes (reduce commits)
from delta.tables import DeltaTable

def batch_delta_writes(dataframes_list, table_path, batch_size=10):
    """
    Batch multiple writes to reduce commit overhead
    """
    delta_table = DeltaTable.forPath(spark, table_path)
    
    for i in range(0, len(dataframes_list), batch_size):
        batch = dataframes_list[i:i+batch_size]
        
        # Union all DataFrames in batch
        combined_df = batch[0]
        for df in batch[1:]:
            combined_df = combined_df.union(df)
        
        # Single write for batch
        combined_df.write.format("delta").mode("append").save(table_path)
        
        print(f"Batch {i//batch_size + 1} written")

# Usage
optimized_delta_write(
    df=new_orders_df,
    table_path="orders_delta/",
    mode="append",
    partition_by=["order_date"],
    optimize_write=True,
    auto_compact=True
)
```

---

## Azure Synapse Optimization

### Table Distribution Strategies

```sql
-- Understanding distribution methods

-- 1. HASH Distribution (for large fact tables)
-- Distributes rows based on hash of distribution column
-- Best for: Large tables (>2GB), joins on distribution column

CREATE TABLE FactSales
(
    SaleID INT,
    CustomerID INT,
    ProductID INT,
    SaleDate DATE,
    Amount DECIMAL(10,2)
)
WITH
(
    DISTRIBUTION = HASH(CustomerID),  -- Choose high cardinality column
    CLUSTERED COLUMNSTORE INDEX
);

-- 2. ROUND_ROBIN Distribution (for staging tables)
-- Distributes rows evenly across distributions
-- Best for: Staging tables, no clear distribution key

CREATE TABLE StagingSales
(
    SaleID INT,
    CustomerID INT,
    ProductID INT,
    Amount DECIMAL(10,2)
)
WITH
(
    DISTRIBUTION = ROUND_ROBIN,
    HEAP  -- No index for fast loading
);

-- 3. REPLICATED Distribution (for small dimension tables)
-- Full copy on each compute node
-- Best for: Small tables (<2GB), frequently joined

CREATE TABLE DimProduct
(
    ProductID INT,
    ProductName VARCHAR(100),
    Category VARCHAR(50)
)
WITH
(
    DISTRIBUTION = REPLICATE,
    CLUSTERED COLUMNSTORE INDEX
);

-- Choosing distribution column:
-- ✅ High cardinality (many unique values)
-- ✅ Frequently used in joins
-- ✅ Even data distribution
-- ❌ Date columns (causes skew)
-- ❌ Nullable columns
-- ❌ Columns with many duplicates
```

### Partitioning

```sql
-- Partitioning for large tables

-- Benefits:
-- - Faster queries (partition elimination)
-- - Easier maintenance (partition switching)
-- - Better compression

CREATE TABLE FactSalesPartitioned
(
    SaleID INT,
    CustomerID INT,
    SaleDate DATE,
    Amount DECIMAL(10,2)
)
WITH
(
    DISTRIBUTION = HASH(CustomerID),
    PARTITION (SaleDate RANGE RIGHT FOR VALUES 
        ('2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01',
         '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01',
         '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01')),
    CLUSTERED COLUMNSTORE INDEX
);

-- Partition best practices:
-- - Partition by commonly filtered column (usually date)
-- - Each partition should be 1GB+ for columnstore
-- - Don't over-partition (<100-1000 partitions)
-- - Align partitions with data loading patterns

-- Check partition distribution
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    partition_number,
    rows,
    CAST(rows * 1.0 / SUM(rows) OVER() * 100 AS DECIMAL(5,2)) AS pct_of_total
FROM sys.dm_db_partition_stats
WHERE object_id = OBJECT_ID('FactSalesPartitioned')
AND index_id IN (0,1)
ORDER BY partition_number;

-- Partition switching for fast data loading
-- Create staging partition
CREATE TABLE FactSales_Staging
WITH
(
    DISTRIBUTION = HASH(CustomerID),
    PARTITION (SaleDate RANGE RIGHT FOR VALUES ('2024-01-01')),
    CLUSTERED COLUMNSTORE INDEX
)
AS SELECT * FROM FactSales WHERE 1=0;

-- Load data to staging
INSERT INTO FactSales_Staging
SELECT * FROM ExternalDataSource WHERE SaleDate >= '2024-01-01';

-- Switch partition (instantaneous)
ALTER TABLE FactSales_Staging
SWITCH PARTITION 2 TO FactSales PARTITION 2;
```

### Columnstore Index Optimization

```sql
-- Columnstore indexes are the default and best choice for DW

-- Check columnstore quality
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    SUM(CASE WHEN state_description = 'COMPRESSED' THEN 1 ELSE 0 END) AS CompressedRowGroups,
    SUM(CASE WHEN state_description = 'OPEN' THEN 1 ELSE 0 END) AS OpenRowGroups,
    SUM(CASE WHEN state_description = 'CLOSED' THEN 1 ELSE 0 END) AS ClosedRowGroups,
    SUM(total_rows) AS TotalRows,
    AVG(total_rows) AS AvgRowsPerRowGroup,
    SUM(deleted_rows) AS DeletedRows
FROM sys.dm_db_column_store_row_group_physical_stats
WHERE object_id = OBJECT_ID('FactSales')
GROUP BY object_id;

-- Optimal rowgroup size: 1M rows
-- If rowgroups are small (<100K rows), rebuild index

-- Rebuild columnstore index
ALTER INDEX ALL ON FactSales REBUILD;

-- Force rowgroup compression
ALTER INDEX ALL ON FactSales REORGANIZE 
WITH (COMPRESS_ALL_ROW_GROUPS = ON);

-- Monitor columnstore fragmentation
CREATE PROCEDURE MonitorColumnstoreFragmentation
AS
BEGIN
    SELECT 
        OBJECT_NAME(object_id) AS TableName,
        COUNT(*) AS TotalRowGroups,
        SUM(CASE WHEN state = 3 THEN 1 ELSE 0 END) AS CompressedRowGroups,
        AVG(CASE WHEN state = 3 THEN total_rows ELSE NULL END) AS AvgRowsPerCompressedRG,
        SUM(deleted_rows) * 100.0 / NULLIF(SUM(total_rows), 0) AS PctDeleted,
        CASE 
            WHEN AVG(CASE WHEN state = 3 THEN total_rows ELSE NULL END) < 100000 
            THEN 'REBUILD RECOMMENDED'
            WHEN SUM(deleted_rows) * 100.0 / NULLIF(SUM(total_rows), 0) > 20 
            THEN 'REBUILD RECOMMENDED'
            ELSE 'OK'
        END AS Recommendation
    FROM sys.dm_db_column_store_row_group_physical_stats
    WHERE object_id IN (SELECT object_id FROM sys.tables WHERE type = 'U')
    GROUP BY object_id
    ORDER BY TableName;
END;
```

### Statistics

```sql
-- Statistics are crucial for query performance

-- Create statistics
CREATE STATISTICS stat_customer_id ON FactSales(CustomerID);
CREATE STATISTICS stat_sale_date ON FactSales(SaleDate);
CREATE STATISTICS stat_amount ON FactSales(Amount);

-- Auto-create statistics
-- Synapse automatically creates statistics on columns used in predicates
-- Enable for all queries:
CREATE DATABASE SCOPED CONFIGURATION SET AUTO_CREATE_STATISTICS = ON;

-- Update statistics
UPDATE STATISTICS FactSales;

-- Update with sample (faster for large tables)
UPDATE STATISTICS FactSales WITH SAMPLE 20 PERCENT;

-- Update specific statistic
UPDATE STATISTICS FactSales(stat_customer_id);

-- Check statistics freshness
SELECT 
    OBJECT_NAME(object_id) AS TableName,
    name AS StatisticName,
    stats_date(object_id, stats_id) AS LastUpdated,
    DATEDIFF(day, stats_date(object_id, stats_id), GETDATE()) AS DaysSinceUpdate,
    rows AS RowsAtUpdate,
    rows_sampled,
    steps,
    unfiltered_rows,
    modification_counter
FROM sys.stats
CROSS APPLY sys.dm_db_stats_properties(object_id, stats_id)
WHERE object_id = OBJECT_ID('FactSales')
ORDER BY LastUpdated DESC;

-- Automated statistics maintenance
CREATE PROCEDURE UpdateOutdatedStatistics
AS
BEGIN
    DECLARE @table NVARCHAR(128);
    DECLARE @stat NVARCHAR(128);
    DECLARE @sql NVARCHAR(MAX);
    
    DECLARE stats_cursor CURSOR FOR
    SELECT 
        OBJECT_NAME(s.object_id) AS TableName,
        s.name AS StatName
    FROM sys.stats s
    CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
    WHERE DATEDIFF(day, stats_date(s.object_id, s.stats_id), GETDATE()) > 7
    OR sp.modification_counter > sp.rows * 0.2;  -- 20% changes
    
    OPEN stats_cursor;
    FETCH NEXT FROM stats_cursor INTO @table, @stat;
    
    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @sql = 'UPDATE STATISTICS ' + @table + '(' + @stat + ') WITH SAMPLE 20 PERCENT';
        EXEC sp_executesql @sql;
        PRINT 'Updated: ' + @table + '.' + @stat;
        
        FETCH NEXT FROM stats_cursor INTO @table, @stat;
    END;
    
    CLOSE stats_cursor;
    DEALLOCATE stats_cursor;
END;
```

### Result Set Caching

```sql
-- Result set caching for repeated queries

-- Enable at database level
ALTER DATABASE SCOPED CONFIGURATION SET RESULT_SET_CACHING = ON;

-- Check if cache is used
SELECT 
    request_id,
    command,
    result_cache_hit,
    total_elapsed_time,
    result_set_cache_hit
FROM sys.dm_pdw_exec_requests
WHERE command LIKE '%SELECT%'
ORDER BY submit_time DESC;

-- Clear result cache
DBCC DROPRESULTSETCACHE;

-- Disable for specific query
SELECT TOP 100 * FROM FactSales
OPTION (LABEL = 'NoCache', NO_RESULT_SET_CACHE);

-- Best practices:
-- ✅ Great for: Dashboards, repeated reports
-- ❌ Not for: Real-time data, frequently updated tables
```

### Materialized Views

```sql
-- Materialized views for pre-aggregated data

-- Create materialized view
CREATE MATERIALIZED VIEW mvSalesByCustomer
WITH (DISTRIBUTION = HASH(CustomerID))
AS
SELECT 
    CustomerID,
    COUNT(*) AS TotalOrders,
    SUM(Amount) AS TotalSpent,
    AVG(Amount) AS AvgOrderValue
FROM FactSales
GROUP BY CustomerID;

-- Query automatically uses materialized view (transparent)
SELECT CustomerID, TotalOrders 
FROM FactSales
GROUP BY CustomerID, TotalOrders;  -- Uses mvSalesByCustomer

-- Check if MV is used
SELECT 
    request_id,
    command,
    materialized_view_name
FROM sys.dm_pdw_exec_requests
WHERE materialized_view_name IS NOT NULL;

-- Refresh materialized view
ALTER MATERIALIZED VIEW mvSalesByCustomer REBUILD;

-- Drop materialized view
DROP VIEW mvSalesByCustomer;
```

---

## Query Optimization Techniques

### Common Anti-Patterns and Solutions

```sql
-- Anti-Pattern 1: SELECT *
-- ❌ BAD
SELECT * FROM FactSales WHERE SaleDate = '2024-01-01';

-- ✅ GOOD: Select only needed columns
SELECT SaleID, CustomerID, Amount 
FROM FactSales 
WHERE SaleDate = '2024-01-01';

-- Anti-Pattern 2: Functions on WHERE columns
-- ❌ BAD: Prevents index/partition elimination
SELECT * FROM FactSales 
WHERE YEAR(SaleDate) = 2024;

-- ✅ GOOD: Sargable predicate
SELECT * FROM FactSales 
WHERE SaleDate >= '2024-01-01' AND SaleDate < '2025-01-01';

-- Anti-Pattern 3: NOT IN with large subqueries
-- ❌ BAD
SELECT * FROM Customers 
WHERE CustomerID NOT IN (SELECT CustomerID FROM FactSales);

-- ✅ GOOD: Use NOT EXISTS or LEFT JOIN
SELECT c.* FROM Customers c
WHERE NOT EXISTS (
    SELECT 1 FROM FactSales s WHERE s.CustomerID = c.CustomerID
);

-- Or
SELECT c.* FROM Customers c
LEFT JOIN FactSales s ON c.CustomerID = s.CustomerID
WHERE s.CustomerID IS NULL;

-- Anti-Pattern 4: OR in WHERE clause
-- ❌ BAD
SELECT * FROM FactSales 
WHERE CustomerID = 100 OR CustomerID = 200 OR CustomerID = 300;

-- ✅ GOOD: Use IN
SELECT * FROM FactSales 
WHERE CustomerID IN (100, 200, 300);

-- Anti-Pattern 5: Multiple OR conditions on different columns
-- ❌ BAD
SELECT * FROM FactSales 
WHERE Category = 'Electronics' OR Amount > 1000;

-- ✅ GOOD: Use UNION ALL
SELECT * FROM FactSales WHERE Category = 'Electronics'
UNION ALL
SELECT * FROM FactSales WHERE Amount > 1000 AND Category != 'Electronics';
```

### Join Optimization

```sql
-- 1. Join Order Matters
-- Query optimizer usually does this, but you can help

-- Put largest table first in FROM clause
SELECT s.*, c.CustomerName
FROM FactSales s  -- Largest table first
JOIN DimCustomer c ON s.CustomerID = c.CustomerID;

-- 2. Join on indexed columns
-- Ensure join columns have appropriate distribution/indexes

-- 3. Use EXISTS instead of JOIN for existence checks
-- ❌ SLOWER
SELECT DISTINCT c.* 
FROM DimCustomer c
JOIN FactSales s ON c.CustomerID = s.CustomerID;

-- ✅ FASTER
SELECT c.* 
FROM DimCustomer c
WHERE EXISTS (
    SELECT 1 FROM FactSales s WHERE s.CustomerID = c.CustomerID
);

-- 4. Pre-aggregate before joining
-- ❌ SLOWER: Join then aggregate
SELECT c.CustomerName, SUM(s.Amount)
FROM FactSales s
JOIN DimCustomer c ON s.CustomerID = c.CustomerID
WHERE s.SaleDate >= '2024-01-01'
GROUP BY c.CustomerName;

-- ✅ FASTER: Aggregate then join
SELECT c.CustomerName, agg.TotalAmount
FROM (
    SELECT CustomerID, SUM(Amount) AS TotalAmount
    FROM FactSales
    WHERE SaleDate >= '2024-01-01'
    GROUP BY CustomerID
) agg
JOIN DimCustomer c ON agg.CustomerID = c.CustomerID;
```

### Window Function Optimization

```sql
-- Window functions can be expensive, optimize with:

-- 1. Limit partition size with WHERE
-- ❌ SLOWER: Large partitions
SELECT 
    CustomerID,
    SaleDate,
    Amount,
    SUM(Amount) OVER (PARTITION BY CustomerID ORDER BY SaleDate) AS RunningTotal
FROM FactSales;

-- ✅ FASTER: Filter first
SELECT 
    CustomerID,
    SaleDate,
    Amount,
    SUM(Amount) OVER (PARTITION BY CustomerID ORDER BY SaleDate) AS RunningTotal
FROM FactSales
WHERE SaleDate >= DATEADD(month, -3, GETDATE());

-- 2. Reuse window definitions
-- ❌ SLOWER: Multiple identical window definitions
SELECT 
    CustomerID,
    SUM(Amount) OVER (PARTITION BY CustomerID ORDER BY SaleDate) AS RunningTotal,
    AVG(Amount) OVER (PARTITION BY CustomerID ORDER BY SaleDate) AS RunningAvg,
    COUNT(*) OVER (PARTITION BY CustomerID ORDER BY SaleDate) AS RunningCount
FROM FactSales;

-- ✅ FASTER: Define window once
SELECT 
    CustomerID,
    SUM(Amount) OVER w AS RunningTotal,
    AVG(Amount) OVER w AS RunningAvg,
    COUNT(*) OVER w AS RunningCount
FROM FactSales
WINDOW w AS (PARTITION BY CustomerID ORDER BY SaleDate);
```

---

## Benchmarking Strategies

### Comprehensive Benchmarking Framework

```python
import time
from datetime import datetime
import json

class PerformanceBenchmark:
    """
    Comprehensive performance benchmarking framework
    """
    
    def __init__(self, spark):
        self.spark = spark
        self.results = []
    
    def benchmark_query(self, name, query_func, iterations=3, warmup=True):
        """
        Benchmark a Spark operation
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking: {name}")
        print(f"{'='*60}")
        
        # Warmup run (JIT compilation, caching)
        if warmup:
            print("Warmup run...")
            _ = query_func()
        
        # Clear cache for fair comparison
        self.spark.catalog.clearCache()
        
        # Multiple iterations
        times = []
        for i in range(iterations):
            print(f"Iteration {i+1}/{iterations}...")
            start_time = time.time()
            
            result = query_func()
            
            # Force execution if lazy
            if hasattr(result, 'count'):
                row_count = result.count()
            else:
                row_count = None
            
            elapsed_time = time.time() - start_time
            times.append(elapsed_time)
            print(f"  Time: {elapsed_time:.2f}s")
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
        
        result_dict = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "iterations": iterations,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev,
            "row_count": row_count,
            "times": times
        }
        
        self.results.append(result_dict)
        
        print(f"\nResults:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        print(f"  Std Dev: {std_dev:.2f}s")
        if row_count:
            print(f"  Rows: {row_count:,}")
        
        return result_dict
    
    def compare_approaches(self, approaches_dict):
        """
        Compare multiple approaches to same problem
        
        approaches_dict: {name: query_function}
        """
        print(f"\n{'='*60}")
        print(f"COMPARING {len(approaches_dict)} APPROACHES")
        print(f"{'='*60}\n")
        
        results = {}
        for name, query_func in approaches_dict.items():
            result = self.benchmark_query(name, query_func)
            results[name] = result
        
        # Summary comparison
        print(f"\n{'='*60}")
        print("COMPARISON SUMMARY")
        print(f"{'='*60}\n")
        
        sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_time'])
        
        baseline_time = sorted_results[0][1]['avg_time']
        
        print(f"{'Approach':<30} {'Avg Time':>12} {'vs Fastest':>12}")
        print(f"{'-'*60}")
        
        for name, result in sorted_results:
            speedup = result['avg_time'] / baseline_time
            print(f"{name:<30} {result['avg_time']:>10.2f}s {speedup:>10.2f}x")
        
        return results
    
    def export_results(self, filename="benchmark_results.json"):
        """
        Export benchmark results to JSON
        """
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults exported to {filename}")

# Usage Example
benchmark = PerformanceBenchmark(spark)

# Define approaches to compare
approaches = {
    "Approach 1: No optimization": lambda: (
        spark.read.parquet("large_table.parquet")
        .filter(col("amount") > 1000)
        .groupBy("customer_id").agg(sum("amount"))
    ),
    
    "Approach 2: With broadcast join": lambda: (
        spark.read.parquet("large_table.parquet")
        .filter(col("amount") > 1000)
        .join(broadcast(dim_customers), "customer_id")
        .groupBy("customer_id").agg(sum("amount"))
    ),
    
    "Approach 3: Pre-partitioned data": lambda: (
        spark.read.parquet("large_table_partitioned.parquet")
        .filter(col("amount") > 1000)
        .groupBy("customer_id").agg(sum("amount"))
    ),
}

# Run comparison
results = benchmark.compare_approaches(approaches)

# Export results
benchmark.export_results("optimization_comparison.json")
```

### Performance Monitoring Dashboard

```python
# Monitor Spark job performance

def create_performance_report(spark):
    """
    Generate comprehensive performance report
    """
    from pyspark import SparkContext
    sc = SparkContext.getOrCreate()
    
    report = {}
    
    # 1. Spark Configuration
    report['configuration'] = {
        'executor_memory': spark.conf.get('spark.executor.memory'),
        'executor_cores': spark.conf.get('spark.executor.cores'),
        'executor_instances': spark.conf.get('spark.executor.instances'),
        'shuffle_partitions': spark.conf.get('spark.sql.shuffle.partitions'),
        'default_parallelism': sc.defaultParallelism
    }
    
    # 2. Storage Information
    report['storage'] = {
        'cache_usage_mb': sum([rdd.getStorageLevel().useMemory for rdd in sc._jsc.getPersistentRDDs().values()]),
        'cached_rdds': len(sc._jsc.getPersistentRDDs())
    }
    
    # 3. Current Jobs
    from pyspark.sql import SQLContext
    sqlContext = SQLContext.getOrCreate(sc)
    
    # Print report
    print("\n" + "="*60)
    print("PERFORMANCE REPORT")
    print("="*60 + "\n")
    
    print("Configuration:")
    for key, value in report['configuration'].items():
        print(f"  {key}: {value}")
    
    print("\nStorage:")
    for key, value in report['storage'].items():
        print(f"  {key}: {value}")
    
    return report

# Usage
report = create_performance_report(spark)
```

---

## Summary

### Quick Reference: Performance Tuning Checklist

**Spark:**
- ✅ Right-size executors (5 cores, 10-16GB each)
- ✅ Optimize partitions (128MB per partition, 2-3x cores)
- ✅ Minimize shuffles (broadcast small tables, pre-partition data)
- ✅ Handle data skew (salting, AQE)
- ✅ Cache strategically (frequently used DataFrames)
- ✅ Enable AQE and whole-stage codegen

**Delta Lake:**
- ✅ Z-Order frequently filtered columns
- ✅ Compact small files (OPTIMIZE)
- ✅ Vacuum old versions (RETAIN 168 HOURS)
- ✅ Enable auto-optimize for writes
- ✅ Monitor file sizes and row group quality

**Synapse:**
- ✅ Choose correct distribution (HASH for large tables)
- ✅ Partition large tables (1GB+ per partition)
- ✅ Maintain statistics (UPDATE STATISTICS weekly)
- ✅ Use columnstore indexes (default)
- ✅ Create materialized views for aggregations
- ✅ Enable result set caching for dashboards

**Query Optimization:**
- ✅ Select only needed columns
- ✅ Use sargable predicates
- ✅ Pre-aggregate before joins
- ✅ Use EXISTS instead of DISTINCT + JOIN
- ✅ Analyze execution plans

**Benchmarking:**
- ✅ Always do warmup runs
- ✅ Multiple iterations for statistical significance
- ✅ Clear cache between tests
- ✅ Document configurations
- ✅ Track over time

---

**Remember**: Profile first, optimize second. Focus on the biggest bottlenecks for maximum impact.
