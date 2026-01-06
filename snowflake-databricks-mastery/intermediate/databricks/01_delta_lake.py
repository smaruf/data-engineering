"""
Delta Lake Fundamentals
=======================

This script demonstrates:
1. Creating Delta tables
2. ACID transactions
3. Time travel
4. Schema evolution
5. Optimization techniques
6. Merge operations (UPSERT)

Prerequisites:
- Completed beginner Databricks level
- Understanding of DataFrames
"""

import os
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable

# Load environment variables
load_dotenv()


def create_delta_session():
    """Create Spark session with Delta Lake support"""
    builder = SparkSession.builder \
        .appName("Delta Lake Learning") \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.sql.warehouse.dir", "/tmp/delta_learning/warehouse")
    
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    return spark


def example_1_create_delta_table():
    """Example 1: Create Delta table"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Create Delta Table")
    print("="*60)
    
    spark = create_delta_session()
    
    try:
        # Create sample data
        data = [
            (1, "Alice", "Engineering", 95000, "2023-01-15"),
            (2, "Bob", "Sales", 75000, "2023-02-01"),
            (3, "Charlie", "Engineering", 105000, "2023-03-10"),
            (4, "Diana", "Marketing", 80000, "2023-04-05")
        ]
        
        columns = ["id", "name", "department", "salary", "hire_date"]
        df = spark.createDataFrame(data, columns)
        
        # Write as Delta table
        delta_path = "/tmp/delta_learning/employees"
        
        print(f"\n📝 Writing Delta table to: {delta_path}")
        df.write.format("delta").mode("overwrite").save(delta_path)
        print("   ✅ Delta table created")
        
        # Read Delta table
        print("\n📊 Reading Delta table:")
        delta_df = spark.read.format("delta").load(delta_path)
        delta_df.show()
        
        # Show Delta table properties
        print("\n📊 Delta Table Properties:")
        print(f"   Format: Delta Lake")
        print(f"   Location: {delta_path}")
        print(f"   Row Count: {delta_df.count()}")
        
    finally:
        spark.stop()


def example_2_acid_transactions():
    """Example 2: ACID transactions with Delta Lake"""
    print("\n" + "="*60)
    print("EXAMPLE 2: ACID Transactions")
    print("="*60)
    
    spark = create_delta_session()
    
    try:
        delta_path = "/tmp/delta_learning/employees"
        
        # Read existing data
        print("\n📊 Original Data:")
        df = spark.read.format("delta").load(delta_path)
        df.show()
        
        # Concurrent write 1: Add new employee
        new_employee = [(5, "Eve", "Finance", 90000, "2023-05-20")]
        new_df = spark.createDataFrame(new_employee, ["id", "name", "department", "salary", "hire_date"])
        
        print("\n📝 Adding new employee (Transaction 1)...")
        new_df.write.format("delta").mode("append").save(delta_path)
        print("   ✅ Transaction committed")
        
        # Concurrent write 2: Update salary
        delta_table = DeltaTable.forPath(spark, delta_path)
        
        print("\n📝 Updating salaries (Transaction 2)...")
        delta_table.update(
            condition=col("department") == "Engineering",
            set={"salary": col("salary") * 1.10}
        )
        print("   ✅ Transaction committed")
        
        # Verify atomicity - all changes are visible
        print("\n📊 After Transactions:")
        updated_df = spark.read.format("delta").load(delta_path)
        updated_df.orderBy("id").show()
        
    finally:
        spark.stop()


def example_3_time_travel():
    """Example 3: Time travel with Delta Lake"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Time Travel")
    print("="*60)
    
    spark = create_delta_session()
    
    try:
        delta_path = "/tmp/delta_learning/employees"
        delta_table = DeltaTable.forPath(spark, delta_path)
        
        # Show version history
        print("\n📊 Version History:")
        history = delta_table.history()
        history.select("version", "timestamp", "operation", "operationMetrics").show(truncate=False)
        
        # Read version 0 (original data)
        print("\n📊 Reading Version 0 (Original Data):")
        v0_df = spark.read.format("delta").option("versionAsOf", 0).load(delta_path)
        v0_df.show()
        
        # Read latest version
        print("\n📊 Reading Latest Version:")
        latest_df = spark.read.format("delta").load(delta_path)
        latest_df.show()
        
        # Time travel to specific timestamp
        print("\n📊 Time Travel Example:")
        print("   You can query data as it existed at any point in time!")
        
    finally:
        spark.stop()


def example_4_schema_evolution():
    """Example 4: Schema evolution"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Schema Evolution")
    print("="*60)
    
    spark = create_delta_session()
    
    try:
        delta_path = "/tmp/delta_learning/employees"
        
        # Add new column to existing data
        new_data = [
            (6, "Frank", "IT", 88000, "2023-06-15", "frank@example.com"),
            (7, "Grace", "Engineering", 110000, "2023-07-01", "grace@example.com")
        ]
        
        new_columns = ["id", "name", "department", "salary", "hire_date", "email"]
        new_df = spark.createDataFrame(new_data, new_columns)
        
        print("\n📝 Adding data with new schema (email column)...")
        new_df.write.format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .save(delta_path)
        print("   ✅ Schema evolved successfully")
        
        # Read with new schema
        print("\n📊 Data with Evolved Schema:")
        evolved_df = spark.read.format("delta").load(delta_path)
        evolved_df.show()
        
        print("\n📊 New Schema:")
        evolved_df.printSchema()
        
    finally:
        spark.stop()


def example_5_merge_upsert():
    """Example 5: MERGE operations (UPSERT)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: MERGE (UPSERT)")
    print("="*60)
    
    spark = create_delta_session()
    
    try:
        delta_path = "/tmp/delta_learning/employees"
        delta_table = DeltaTable.forPath(spark, delta_path)
        
        # Create updates and new records
        updates_data = [
            (2, "Bob Smith", "Sales", 80000, "2023-02-01", "bob@example.com"),  # Update
            (8, "Henry", "Finance", 95000, "2023-08-01", "henry@example.com")   # Insert
        ]
        
        updates_df = spark.createDataFrame(
            updates_data,
            ["id", "name", "department", "salary", "hire_date", "email"]
        )
        
        print("\n📊 Updates to Apply:")
        updates_df.show()
        
        # Perform MERGE (UPSERT)
        print("\n📝 Performing MERGE operation...")
        delta_table.alias("target").merge(
            updates_df.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll() \
         .whenNotMatchedInsertAll() \
         .execute()
        print("   ✅ MERGE completed")
        
        # Show results
        print("\n📊 After MERGE:")
        result_df = spark.read.format("delta").load(delta_path)
        result_df.orderBy("id").show()
        
    finally:
        spark.stop()


def example_6_optimization():
    """Example 6: Delta Lake optimization"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Optimization")
    print("="*60)
    
    spark = create_delta_session()
    
    try:
        from delta.tables import DeltaTable
        
        delta_path = "/tmp/delta_learning/employees"
        delta_table = DeltaTable.forPath(spark, delta_path)
        
        # Show current file count
        print("\n📊 Before Optimization:")
        files = spark.read.format("delta").load(delta_path).inputFiles()
        print(f"   Number of files: {len(files)}")
        
        # Optimize - compact small files
        print("\n📝 Running OPTIMIZE...")
        delta_table.optimize().executeCompaction()
        print("   ✅ Optimization completed")
        
        # Show file count after optimization
        print("\n📊 After Optimization:")
        files = spark.read.format("delta").load(delta_path).inputFiles()
        print(f"   Number of files: {len(files)}")
        
        # Z-ORDER optimization (for better query performance)
        print("\n📝 Running Z-ORDER optimization on department...")
        delta_table.optimize().executeZOrderBy("department")
        print("   ✅ Z-ORDER optimization completed")
        
        # Vacuum old files (remove files older than retention period)
        print("\n📝 Running VACUUM...")
        print("   (Removes files no longer needed for time travel)")
        # Note: Default retention is 7 days, we're using 0 hours for demo
        spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
        delta_table.vacuum(0)
        print("   ✅ VACUUM completed")
        
    finally:
        spark.stop()


def main():
    """Run all examples"""
    print("\n🎓 DELTA LAKE FUNDAMENTALS")
    print("=" * 60)
    
    try:
        example_1_create_delta_table()
        example_2_acid_transactions()
        example_3_time_travel()
        example_4_schema_evolution()
        example_5_merge_upsert()
        example_6_optimization()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
        print("\n📚 Key Takeaways:")
        print("   ✅ Delta Lake provides ACID transactions")
        print("   ✅ Time travel enables data versioning")
        print("   ✅ Schema evolution supports changing requirements")
        print("   ✅ MERGE simplifies upsert operations")
        print("   ✅ Optimization improves query performance")
        
        print("\n📚 Next Steps:")
        print("   1. Explore streaming with Delta in 02_streaming.py")
        print("   2. Learn optimization techniques in 03_optimization.py")
        print("   3. Practice with larger datasets")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
