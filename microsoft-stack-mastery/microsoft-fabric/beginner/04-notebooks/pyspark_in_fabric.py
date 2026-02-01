"""
Microsoft Fabric PySpark Examples

This module demonstrates PySpark usage in Fabric environment with
Delta Lake, lakehouse integration, and performance optimization.

Author: Data Engineering Team
License: MIT
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def pyspark_basics():
    """PySpark basics in Fabric."""
    print("=" * 80)
    print("PySpark in Microsoft Fabric - Examples")
    print("=" * 80)
    
    print("\n1. Creating DataFrames")
    print("-" * 80)
    print("""
    from pyspark.sql import SparkSession
    from pyspark.sql.types import *
    from pyspark.sql import functions as F
    
    # Spark session is pre-configured in Fabric notebooks
    # Access via 'spark' variable
    
    # Create DataFrame from data
    data = [
        (1, "John Doe", "john@example.com", 25000),
        (2, "Jane Smith", "jane@example.com", 30000),
        (3, "Bob Johnson", "bob@example.com", 28000)
    ]
    
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False),
        StructField("email", StringType(), True),
        StructField("salary", IntegerType(), True)
    ])
    
    df = spark.createDataFrame(data, schema)
    df.show()
    
    # Create from list of dictionaries
    data_dict = [
        {"id": 1, "name": "Product A", "price": 99.99},
        {"id": 2, "name": "Product B", "price": 149.99}
    ]
    df = spark.createDataFrame(data_dict)
    """)
    
    print("\n2. Reading Data")
    print("-" * 80)
    print("""
    # Read from lakehouse Files
    df_parquet = spark.read.parquet("/lakehouse/default/Files/data.parquet")
    df_csv = spark.read.csv("/lakehouse/default/Files/data.csv", header=True, inferSchema=True)
    df_json = spark.read.json("/lakehouse/default/Files/data.json")
    
    # Read Delta tables
    df_delta = spark.read.format("delta").load("/lakehouse/default/Tables/my_table")
    
    # Read from lakehouse table catalog
    df_table = spark.table("my_lakehouse.my_table")
    
    # Read with options
    df = spark.read \\
        .option("header", "true") \\
        .option("inferSchema", "true") \\
        .option("delimiter", "|") \\
        .csv("/lakehouse/default/Files/data.csv")
    """)


def data_transformations():
    """Common PySpark transformations."""
    print("\n3. Data Transformations")
    print("-" * 80)
    print("""
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    
    # Select and rename columns
    df_selected = df.select(
        F.col("customer_id"),
        F.col("customer_name").alias("name"),
        F.col("order_date")
    )
    
    # Filter data
    df_filtered = df.filter(
        (F.col("order_date") >= "2024-01-01") &
        (F.col("total_amount") > 100)
    )
    
    # Add calculated columns
    df_calc = df.withColumn(
        "total_amount",
        F.col("quantity") * F.col("unit_price")
    ).withColumn(
        "discount_amount",
        F.col("total_amount") * 0.1
    ).withColumn(
        "final_amount",
        F.col("total_amount") - F.col("discount_amount")
    )
    
    # String operations
    df_strings = df.withColumn(
        "name_upper",
        F.upper(F.col("name"))
    ).withColumn(
        "email_domain",
        F.split(F.col("email"), "@").getItem(1)
    ).withColumn(
        "name_length",
        F.length(F.col("name"))
    )
    
    # Date operations
    df_dates = df.withColumn(
        "year",
        F.year("order_date")
    ).withColumn(
        "month",
        F.month("order_date")
    ).withColumn(
        "day_of_week",
        F.dayofweek("order_date")
    ).withColumn(
        "days_since_order",
        F.datediff(F.current_date(), F.col("order_date"))
    )
    """)


def aggregations_and_grouping():
    """Aggregation examples."""
    print("\n4. Aggregations and Grouping")
    print("-" * 80)
    print("""
    # Simple aggregations
    total_sales = df.agg(
        F.sum("total_amount").alias("total_sales"),
        F.avg("total_amount").alias("avg_sale"),
        F.count("order_id").alias("order_count")
    )
    
    # Group by
    category_summary = df.groupBy("category").agg(
        F.count("*").alias("product_count"),
        F.sum("total_amount").alias("total_revenue"),
        F.avg("unit_price").alias("avg_price"),
        F.max("total_amount").alias("max_sale"),
        F.min("total_amount").alias("min_sale")
    )
    
    # Multiple group by
    daily_category_sales = df.groupBy("order_date", "category").agg(
        F.sum("total_amount").alias("daily_sales")
    ).orderBy("order_date", "category")
    
    # Pivot
    pivot_df = df.groupBy("year").pivot("category").agg(
        F.sum("total_amount")
    )
    """)


def window_functions():
    """Window function examples."""
    print("\n5. Window Functions")
    print("-" * 80)
    print("""
    from pyspark.sql.window import Window
    
    # Ranking
    window_rank = Window.partitionBy("category").orderBy(F.desc("total_amount"))
    
    df_ranked = df.withColumn(
        "rank",
        F.rank().over(window_rank)
    ).withColumn(
        "dense_rank",
        F.dense_rank().over(window_rank)
    ).withColumn(
        "row_number",
        F.row_number().over(window_rank)
    )
    
    # Running totals
    window_running = Window.partitionBy("customer_id").orderBy("order_date") \\
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    
    df_running = df.withColumn(
        "running_total",
        F.sum("total_amount").over(window_running)
    ).withColumn(
        "cumulative_count",
        F.count("*").over(window_running)
    )
    
    # Moving averages
    window_ma = Window.partitionBy("product_id").orderBy("order_date") \\
        .rowsBetween(-6, 0)
    
    df_ma = df.withColumn(
        "moving_avg_7days",
        F.avg("total_amount").over(window_ma)
    )
    
    # Lag and lead
    window_lag = Window.partitionBy("customer_id").orderBy("order_date")
    
    df_lag = df.withColumn(
        "previous_order_amount",
        F.lag("total_amount", 1).over(window_lag)
    ).withColumn(
        "next_order_amount",
        F.lead("total_amount", 1).over(window_lag)
    ).withColumn(
        "amount_change",
        F.col("total_amount") - F.col("previous_order_amount")
    )
    """)


def joins_and_unions():
    """Join and union examples."""
    print("\n6. Joins and Unions")
    print("-" * 80)
    print("""
    # Inner join
    df_joined = df_sales.join(
        df_customers,
        df_sales.customer_id == df_customers.id,
        "inner"
    )
    
    # Left join
    df_left = df_orders.join(
        df_products,
        "product_id",
        "left"
    )
    
    # Broadcast join (for small tables)
    from pyspark.sql.functions import broadcast
    
    df_broadcast = df_large.join(
        broadcast(df_small),
        "key_column"
    )
    
    # Union (same schema)
    df_combined = df_2023.union(df_2024)
    
    # Union by name (different column order)
    df_combined = df_2023.unionByName(df_2024)
    """)


def delta_lake_operations():
    """Delta Lake specific operations."""
    print("\n7. Delta Lake Operations")
    print("-" * 80)
    print("""
    from delta.tables import DeltaTable
    
    # Write Delta table
    df.write \\
        .format("delta") \\
        .mode("overwrite") \\
        .partitionBy("year", "month") \\
        .save("/lakehouse/default/Tables/sales")
    
    # Append to Delta table
    df_new.write \\
        .format("delta") \\
        .mode("append") \\
        .save("/lakehouse/default/Tables/sales")
    
    # Upsert (merge)
    delta_table = DeltaTable.forPath(spark, "/lakehouse/default/Tables/customers")
    
    delta_table.alias("target").merge(
        df_updates.alias("source"),
        "target.customer_id = source.customer_id"
    ).whenMatchedUpdate(set={
        "name": "source.name",
        "email": "source.email",
        "updated_at": "source.updated_at"
    }).whenNotMatchedInsert(values={
        "customer_id": "source.customer_id",
        "name": "source.name",
        "email": "source.email",
        "created_at": "source.created_at"
    }).execute()
    
    # Delete records
    delta_table.delete("status = 'inactive'")
    
    # Time travel
    df_v5 = spark.read.format("delta").option("versionAsOf", 5).load(path)
    df_yesterday = spark.read.format("delta") \\
        .option("timestampAsOf", "2024-01-01") \\
        .load(path)
    
    # Optimize and vacuum
    spark.sql("OPTIMIZE sales ZORDER BY (customer_id)")
    spark.sql("VACUUM sales RETAIN 168 HOURS")
    """)


def performance_optimization():
    """Performance optimization tips."""
    print("\n8. Performance Optimization")
    print("-" * 80)
    print("""
    # Cache frequently used DataFrames
    df_cached = df.cache()
    df_cached.count()  # Materialize cache
    
    # Persist with different storage levels
    from pyspark import StorageLevel
    df.persist(StorageLevel.MEMORY_AND_DISK)
    
    # Repartition for better parallelism
    df_repartitioned = df.repartition(200)
    df_repartitioned = df.repartition("customer_id")
    
    # Coalesce to reduce partitions
    df_coalesced = df.coalesce(10)
    
    # Broadcast small DataFrames
    from pyspark.sql.functions import broadcast
    df_result = df_large.join(broadcast(df_small), "key")
    
    # Predicate pushdown (filter early)
    df = spark.read.parquet(path) \\
        .filter(F.col("date") >= "2024-01-01")
    
    # Use built-in functions instead of UDFs
    # Bad: UDF
    @udf(returnType=StringType())
    def upper_udf(s):
        return s.upper()
    
    # Good: Built-in function
    df.withColumn("name_upper", F.upper("name"))
    
    # Avoid .collect() on large datasets
    # Bad
    data = df.collect()  # Brings all data to driver
    
    # Good
    df.write.parquet(path)  # Distributed write
    """)


def main():
    """Run all PySpark examples."""
    pyspark_basics()
    data_transformations()
    aggregations_and_grouping()
    window_functions()
    joins_and_unions()
    delta_lake_operations()
    performance_optimization()
    
    print("\n" + "=" * 80)
    print("PySpark in Fabric Examples Completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
