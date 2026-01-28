"""
Big Data Statistics with Apache Spark
======================================

Example demonstrating statistical computations on large datasets
using Apache Spark.
"""

import sys
sys.path.append('../..')

from pyspark.sql import SparkSession
from pyspark.sql.functions import mean, stddev, min as spark_min, max as spark_max, count
from pyspark.sql.functions import col, expr
import numpy as np

def main():
    print("=" * 70)
    print("  Big Data Statistics with Apache Spark")
    print("=" * 70)
    print()
    
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("BigDataStatistics") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    
    # Suppress INFO logs
    spark.sparkContext.setLogLevel("WARN")
    
    print("Spark Session created successfully")
    print(f"Spark Version: {spark.version}")
    print()
    
    # Generate large synthetic dataset
    print("Generating synthetic dataset (1 million records)...")
    data = generate_large_dataset(spark, n_records=1000000)
    
    # Cache data for better performance
    data.cache()
    print(f"Dataset cached. Partitions: {data.rdd.getNumPartitions()}")
    print()
    
    # Basic statistics
    compute_basic_statistics(data)
    
    # Group-by statistics
    compute_grouped_statistics(data)
    
    # Advanced statistics
    compute_advanced_statistics(data)
    
    # Performance comparison
    compare_performance(data)
    
    # Cleanup
    data.unpersist()
    spark.stop()
    
    print("=" * 70)
    print("  Analysis Complete!")
    print("=" * 70)


def generate_large_dataset(spark, n_records=1000000):
    """Generate a large synthetic dataset."""
    # Create using Spark SQL
    df = spark.range(n_records) \
        .withColumn("category", (col("id") % 10).cast("string")) \
        .withColumn("value", expr("rand() * 100")) \
        .withColumn("score", expr("randn() * 15 + 100"))
    
    return df


def compute_basic_statistics(df):
    """Compute basic descriptive statistics."""
    print("Basic Descriptive Statistics:")
    print("-" * 50)
    
    # Using Spark's built-in functions
    stats = df.select([
        count("value").alias("count"),
        mean("value").alias("mean"),
        stddev("value").alias("std_dev"),
        spark_min("value").alias("min"),
        spark_max("value").alias("max")
    ])
    
    # Collect and display
    result = stats.collect()[0]
    print(f"Count:      {result['count']:,}")
    print(f"Mean:       {result['mean']:.4f}")
    print(f"Std Dev:    {result['std_dev']:.4f}")
    print(f"Min:        {result['min']:.4f}")
    print(f"Max:        {result['max']:.4f}")
    print()


def compute_grouped_statistics(df):
    """Compute statistics by groups."""
    print("Group-by Statistics (by Category):")
    print("-" * 50)
    
    grouped_stats = df.groupBy("category").agg(
        count("*").alias("count"),
        mean("value").alias("avg_value"),
        stddev("value").alias("std_value"),
        spark_min("value").alias("min_value"),
        spark_max("value").alias("max_value")
    ).orderBy("category")
    
    # Show results
    grouped_stats.show(10, False)


def compute_advanced_statistics(df):
    """Compute advanced statistics including percentiles."""
    print("Advanced Statistics:")
    print("-" * 50)
    
    # Approximate percentiles (more efficient for big data)
    percentiles = df.select([
        expr("percentile_approx(value, 0.25)").alias("Q1"),
        expr("percentile_approx(value, 0.50)").alias("Median"),
        expr("percentile_approx(value, 0.75)").alias("Q3"),
        expr("percentile_approx(value, 0.95)").alias("P95"),
        expr("percentile_approx(value, 0.99)").alias("P99")
    ])
    
    result = percentiles.collect()[0]
    print(f"Q1 (25th):   {result['Q1']:.4f}")
    print(f"Median:      {result['Median']:.4f}")
    print(f"Q3 (75th):   {result['Q3']:.4f}")
    print(f"P95:         {result['P95']:.4f}")
    print(f"P99:         {result['P99']:.4f}")
    
    # IQR
    iqr = result['Q3'] - result['Q1']
    print(f"IQR:         {iqr:.4f}")
    print()


def compare_performance(df):
    """Compare performance of different approaches."""
    import time
    
    print("Performance Comparison:")
    print("-" * 50)
    
    # Spark aggregation
    start = time.time()
    spark_mean = df.select(mean("value")).collect()[0][0]
    spark_time = time.time() - start
    print(f"Spark aggregation time: {spark_time:.4f} seconds")
    
    # Collect and compute with NumPy (not recommended for truly big data)
    start = time.time()
    sample = df.select("value").sample(0.01).rdd.flatMap(lambda x: x).collect()
    numpy_mean = np.mean(sample)
    numpy_time = time.time() - start
    print(f"NumPy time (1% sample): {numpy_time:.4f} seconds")
    
    print()
    print(f"Speedup factor: {numpy_time/spark_time:.2f}x")
    print()


if __name__ == "__main__":
    main()
