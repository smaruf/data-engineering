# Big Data Statistics with Apache Spark

## Overview

This guide demonstrates how to perform statistical computations on large datasets using Apache Spark, integrating with our basic statistics library.

## Why Spark for Statistics?

- **Scalability**: Process datasets that don't fit in memory
- **Distributed Computing**: Leverage cluster computing
- **Fault Tolerance**: Automatic recovery from failures
- **Rich API**: SQL, DataFrame, and RDD interfaces

## Architecture

```
┌─────────────────┐
│  Data Sources   │  (HDFS, S3, Databases)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Spark Cluster  │
│  - Driver       │
│  - Executors    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Statistics     │
│  Computation    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Results        │
└─────────────────┘
```

## Basic Examples

### 1. Descriptive Statistics with Spark

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import mean, stddev, min, max, count

# Initialize Spark
spark = SparkSession.builder \
    .appName("Statistics") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# Load data
df = spark.read.csv("large_dataset.csv", header=True, inferSchema=True)

# Compute statistics
stats = df.select([
    count("value").alias("count"),
    mean("value").alias("mean"),
    stddev("value").alias("std_dev"),
    min("value").alias("min"),
    max("value").alias("max")
])

stats.show()
```

### 2. GroupBy Statistics

```python
from pyspark.sql.functions import avg, sum, count

# Statistics by category
category_stats = df.groupBy("category").agg(
    count("*").alias("count"),
    avg("value").alias("avg_value"),
    sum("value").alias("total_value"),
    stddev("value").alias("std_dev")
)

category_stats.show()
```

### 3. Window Functions for Moving Statistics

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, lag, lead

# Define window
window_spec = Window.partitionBy("category").orderBy("date").rowsBetween(-7, 0)

# Calculate 7-day moving average
df_with_ma = df.withColumn("moving_avg_7d", avg("value").over(window_spec))

df_with_ma.show()
```

## Advanced Spark Statistics

### Custom Aggregation Functions

```python
from pyspark.sql.functions import pandas_udf, PandasUDFType
import pandas as pd
import numpy as np

@pandas_udf("double", PandasUDFType.GROUPED_AGG)
def skewness(values):
    """Calculate skewness for grouped data."""
    from scipy.stats import skew
    return skew(values)

@pandas_udf("double", PandasUDFType.GROUPED_AGG)
def kurtosis(values):
    """Calculate kurtosis for grouped data."""
    from scipy.stats import kurtosis as kurt
    return kurt(values)

# Use custom functions
advanced_stats = df.groupBy("category").agg(
    skewness("value").alias("skewness"),
    kurtosis("value").alias("kurtosis")
)
```

### Distributed Sampling

```python
# Stratified sampling
fractions = {category: 0.1 for category in df.select("category").distinct().collect()}
sample = df.sampleBy("category", fractions, seed=42)

# Random sampling
random_sample = df.sample(withReplacement=False, fraction=0.1, seed=42)
```

## Performance Optimization

### 1. Partitioning Strategy

```python
# Optimal partitioning
df_partitioned = df.repartition(200, "category")

# Check partitions
print(f"Number of partitions: {df_partitioned.rdd.getNumPartitions()}")
```

### 2. Caching for Iterative Computations

```python
# Cache frequently accessed data
df.cache()

# Perform multiple operations
mean_val = df.select(mean("value")).collect()[0][0]
std_val = df.select(stddev("value")).collect()[0][0]

# Unpersist when done
df.unpersist()
```

### 3. Broadcast Variables for Lookup Tables

```python
# Broadcast small lookup tables
small_table = spark.read.csv("small_lookup.csv")
broadcast_var = spark.sparkContext.broadcast(small_table.collect())
```

## Integration with Our Statistics Library

### Hybrid Approach: Spark for ETL, Python for Statistics

```python
from pyspark.sql import SparkSession
import sys
sys.path.append('/path/to/basic-statistics')
from src.python.descriptive import CentralTendency, Dispersion

spark = SparkSession.builder.appName("HybridStats").getOrCreate()

# 1. Use Spark for data loading and preprocessing
df = spark.read.parquet("hdfs:///large_dataset.parquet")
df_filtered = df.filter(df.value > 0)

# 2. Collect manageable subset for detailed analysis
sample_data = df_filtered.sample(0.01).select("value").rdd.flatMap(lambda x: x).collect()

# 3. Use our library for advanced statistics
print(f"Skewness: {Dispersion.skewness(sample_data)}")
print(f"Kurtosis: {Dispersion.kurtosis(sample_data)}")
print(f"IQR: {Dispersion.iqr(sample_data)}")
```

## Real-World Example: Log Analytics

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Initialize
spark = SparkSession.builder \
    .appName("LogAnalytics") \
    .getOrCreate()

# Load server logs (billions of records)
logs = spark.read.json("s3://logs/server-logs-*.json")

# Compute response time statistics by endpoint
stats = logs.groupBy("endpoint").agg(
    count("*").alias("request_count"),
    avg("response_time").alias("avg_response_time"),
    stddev("response_time").alias("std_response_time"),
    expr("percentile_approx(response_time, 0.5)").alias("median"),
    expr("percentile_approx(response_time, 0.95)").alias("p95"),
    expr("percentile_approx(response_time, 0.99)").alias("p99")
)

# Identify slow endpoints (p95 > 1000ms)
slow_endpoints = stats.filter(col("p95") > 1000)

# Save results
slow_endpoints.write.parquet("s3://results/slow-endpoints")
```

## Monitoring and Tuning

### Spark UI Metrics
- Monitor job execution time
- Check data skew across partitions
- Identify shuffle operations
- Track memory usage

### Best Practices
1. Use appropriate file formats (Parquet, ORC)
2. Leverage predicate pushdown
3. Minimize shuffles
4. Use appropriate join strategies
5. Configure memory correctly

## Conclusion

Combining Spark's distributed computing with our statistics library provides:
- Scalability for big data
- Precision for detailed analysis
- Flexibility in computation
- Production-ready performance

## Next Steps
- See [Distributed Computing](distributed-computing.md) for Dask examples
- See [Production Deployment](production-deployment.md) for containerization
