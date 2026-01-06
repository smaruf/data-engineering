"""
Databricks Setup and First Connection
======================================

This script demonstrates:
1. How to setup Databricks connectivity
2. How to create a SparkSession
3. How to execute basic Spark operations
4. How to work with DataFrames

Prerequisites:
- Databricks account (Community Edition or cloud-based)
- Python 3.8+
- pyspark installed
- Databricks token (for remote connection)

Note: This script can run locally with PySpark or connect to Databricks cluster
"""

import os
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, avg, count, min, max, sum
from typing import Optional

# Load environment variables
load_dotenv()


class DatabricksConnectionManager:
    """Manages Databricks/Spark connections"""
    
    def __init__(self, mode: str = "local"):
        """
        Initialize connection manager
        
        Args:
            mode: "local" for local Spark or "remote" for Databricks connection
        """
        self.mode = mode
        self.spark: Optional[SparkSession] = None
        
    def create_local_session(self) -> SparkSession:
        """
        Create a local Spark session
        
        Returns:
            SparkSession: Local Spark session
        """
        print("🔌 Creating local Spark session...")
        
        self.spark = SparkSession.builder \
            .appName("Databricks Learning - Local") \
            .master("local[*]") \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()
        
        print("✅ Local Spark session created successfully!")
        print(f"   Spark Version: {self.spark.version}")
        print(f"   Master: {self.spark.sparkContext.master}")
        
        return self.spark
    
    def create_remote_session(self) -> SparkSession:
        """
        Create a remote Databricks session using Databricks Connect
        
        Returns:
            SparkSession: Databricks Spark session
        """
        print("🔌 Connecting to Databricks cluster...")
        
        databricks_host = os.getenv('DATABRICKS_HOST')
        databricks_token = os.getenv('DATABRICKS_TOKEN')
        databricks_cluster_id = os.getenv('DATABRICKS_CLUSTER_ID')
        
        if not all([databricks_host, databricks_token, databricks_cluster_id]):
            raise ValueError("Missing Databricks credentials in environment variables")
        
        # Note: Databricks Connect configuration
        self.spark = SparkSession.builder \
            .appName("Databricks Learning - Remote") \
            .config("spark.databricks.service.address", databricks_host) \
            .config("spark.databricks.service.token", databricks_token) \
            .config("spark.databricks.service.clusterId", databricks_cluster_id) \
            .getOrCreate()
        
        print("✅ Connected to Databricks cluster!")
        print(f"   Spark Version: {self.spark.version}")
        
        return self.spark
    
    def connect(self) -> SparkSession:
        """
        Create Spark session based on mode
        
        Returns:
            SparkSession: Active Spark session
        """
        if self.mode == "local":
            return self.create_local_session()
        elif self.mode == "remote":
            return self.create_remote_session()
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'local' or 'remote'")
    
    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("🔌 Spark session stopped")


def example_1_basic_spark_session():
    """Example 1: Create and verify Spark session"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Spark Session")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Display Spark configuration
        print("\n📊 Spark Configuration:")
        print(f"   App Name: {spark.sparkContext.appName}")
        print(f"   Spark Version: {spark.version}")
        print(f"   Python Version: {sys.version.split()[0]}")
        print(f"   Master: {spark.sparkContext.master}")
        
        # Check available cores
        print(f"   Default Parallelism: {spark.sparkContext.defaultParallelism}")
        
    finally:
        conn_manager.stop()


def example_2_simple_dataframe():
    """Example 2: Create and display a simple DataFrame"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Simple DataFrame")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Create DataFrame from list
        data = [
            ("Alice", 25, "Engineering"),
            ("Bob", 30, "Sales"),
            ("Charlie", 35, "Engineering"),
            ("Diana", 28, "Marketing")
        ]
        
        columns = ["name", "age", "department"]
        
        df = spark.createDataFrame(data, columns)
        
        print("\n📊 DataFrame Schema:")
        df.printSchema()
        
        print("\n📊 DataFrame Content:")
        df.show()
        
        print(f"\n📊 Row Count: {df.count()}")
        print(f"📊 Column Count: {len(df.columns)}")
        
    finally:
        conn_manager.stop()


def example_3_dataframe_operations():
    """Example 3: Basic DataFrame operations"""
    print("\n" + "="*60)
    print("EXAMPLE 3: DataFrame Operations")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Create sample data
        data = [
            (1, "John", "Engineering", 95000),
            (2, "Jane", "Engineering", 105000),
            (3, "Bob", "Sales", 75000),
            (4, "Alice", "Marketing", 80000),
            (5, "Charlie", "Engineering", 92000)
        ]
        
        df = spark.createDataFrame(data, ["id", "name", "department", "salary"])
        
        # Select specific columns
        print("\n📊 Select Operation (name, salary):")
        df.select("name", "salary").show()
        
        # Filter operation
        print("\n📊 Filter Operation (salary > 90000):")
        df.filter(col("salary") > 90000).show()
        
        # Filter by department
        print("\n📊 Engineering Department:")
        df.filter(col("department") == "Engineering").show()
        
        # Add new column
        print("\n📊 Adding Bonus Column (10% of salary):")
        df_with_bonus = df.withColumn("bonus", col("salary") * 0.1)
        df_with_bonus.select("name", "salary", "bonus").show()
        
        # Sort by salary
        print("\n📊 Sorted by Salary (descending):")
        df.orderBy(col("salary").desc()).show()
        
    finally:
        conn_manager.stop()


def example_4_aggregations():
    """Example 4: Aggregation operations"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Aggregations")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Create sample data
        data = [
            ("Engineering", "Alice", 95000),
            ("Engineering", "Bob", 105000),
            ("Engineering", "Charlie", 92000),
            ("Sales", "David", 75000),
            ("Sales", "Eve", 78000),
            ("Marketing", "Frank", 80000),
            ("Marketing", "Grace", 85000)
        ]
        
        df = spark.createDataFrame(data, ["department", "name", "salary"])
        
        print("\n📊 Original Data:")
        df.show()
        
        # Group by department
        print("\n📊 Department Statistics:")
        df.groupBy("department").agg(
            {"salary": "avg", "*": "count"}
        ).withColumnRenamed("avg(salary)", "avg_salary") \
         .withColumnRenamed("count(1)", "employee_count") \
         .show()
        
        # Using functions
        print("\n📊 Detailed Department Statistics:")
        df.groupBy("department").agg(
            count("*").alias("employees"),
            avg("salary").alias("avg_salary"),
            min("salary").alias("min_salary"),
            max("salary").alias("max_salary"),
            sum("salary").alias("total_salary")
        ).show()
        
    finally:
        conn_manager.stop()


def example_5_sql_operations():
    """Example 5: SQL queries on DataFrames"""
    print("\n" + "="*60)
    print("EXAMPLE 5: SQL Operations")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Create sample data
        data = [
            (1, "Alice", "Engineering", 95000),
            (2, "Bob", "Sales", 75000),
            (3, "Charlie", "Engineering", 105000),
            (4, "Diana", "Marketing", 80000)
        ]
        
        df = spark.createDataFrame(data, ["id", "name", "department", "salary"])
        
        # Register DataFrame as temporary view
        df.createOrReplaceTempView("employees")
        
        # Execute SQL query
        print("\n📊 SQL Query - All Employees:")
        result = spark.sql("SELECT * FROM employees")
        result.show()
        
        # SQL with WHERE clause
        print("\n📊 SQL Query - High Earners:")
        result = spark.sql("""
            SELECT name, department, salary 
            FROM employees 
            WHERE salary >= 90000
            ORDER BY salary DESC
        """)
        result.show()
        
        # SQL with aggregation
        print("\n📊 SQL Query - Department Summary:")
        result = spark.sql("""
            SELECT 
                department,
                COUNT(*) as num_employees,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary
            FROM employees
            GROUP BY department
            ORDER BY avg_salary DESC
        """)
        result.show()
        
    finally:
        conn_manager.stop()


def example_6_reading_writing_data():
    """Example 6: Basic data I/O operations"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Reading and Writing Data")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Create sample data
        data = [
            (1, "Product A", "Electronics", 299.99),
            (2, "Product B", "Clothing", 49.99),
            (3, "Product C", "Electronics", 599.99),
            (4, "Product D", "Books", 19.99)
        ]
        
        df = spark.createDataFrame(data, ["id", "name", "category", "price"])
        
        # Write to CSV
        output_path = "/tmp/databricks_learning"
        csv_path = f"{output_path}/products_csv"
        
        print(f"\n📝 Writing to CSV: {csv_path}")
        df.write.mode("overwrite").option("header", "true").csv(csv_path)
        print("   ✅ CSV written successfully")
        
        # Read from CSV
        print(f"\n📖 Reading from CSV:")
        df_csv = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path)
        df_csv.show()
        
        # Write to Parquet
        parquet_path = f"{output_path}/products_parquet"
        print(f"\n📝 Writing to Parquet: {parquet_path}")
        df.write.mode("overwrite").parquet(parquet_path)
        print("   ✅ Parquet written successfully")
        
        # Read from Parquet
        print(f"\n📖 Reading from Parquet:")
        df_parquet = spark.read.parquet(parquet_path)
        df_parquet.show()
        
        # Write to JSON
        json_path = f"{output_path}/products_json"
        print(f"\n📝 Writing to JSON: {json_path}")
        df.write.mode("overwrite").json(json_path)
        print("   ✅ JSON written successfully")
        
        # Read from JSON
        print(f"\n📖 Reading from JSON:")
        df_json = spark.read.json(json_path)
        df_json.show()
        
    finally:
        conn_manager.stop()


def example_7_error_handling():
    """Example 7: Error handling in Spark"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Error Handling")
    print("="*60)
    
    conn_manager = DatabricksConnectionManager(mode="local")
    
    try:
        spark = conn_manager.connect()
        
        # Example: Handling invalid column reference
        try:
            df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
            # This will raise an error - column doesn't exist
            df.select("invalid_column").show()
        except Exception as e:
            print(f"\n⚠️  Caught expected error: {type(e).__name__}")
            print(f"   Message: {str(e)[:100]}")
        
        # Example: Handling file not found
        try:
            # This will raise an error - path doesn't exist
            df = spark.read.csv("/nonexistent/path")
        except Exception as e:
            print(f"\n⚠️  Caught file not found error: {type(e).__name__}")
        
        # Successful operation
        print("\n✅ Proper error handling demonstrated")
        
    finally:
        conn_manager.stop()


def verify_environment():
    """Verify that environment is set up correctly"""
    print("\n" + "="*60)
    print("ENVIRONMENT VERIFICATION")
    print("="*60)
    
    print("\n📊 Python Version:")
    print(f"   {sys.version}")
    
    print("\n📊 Required Libraries:")
    try:
        import pyspark
        print(f"   ✅ PySpark: {pyspark.__version__}")
    except ImportError:
        print("   ❌ PySpark: Not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print("   ✅ python-dotenv: Installed")
    except ImportError:
        print("   ❌ python-dotenv: Not installed")
        return False
    
    print("\n✅ Environment is ready!")
    return True


def main():
    """Run all examples"""
    print("\n🎓 DATABRICKS SETUP AND CONNECTION EXAMPLES")
    print("=" * 60)
    
    # Verify environment
    if not verify_environment():
        print("\n❌ Please install required libraries:")
        print("   pip install pyspark python-dotenv")
        sys.exit(1)
    
    # Run examples
    try:
        example_1_basic_spark_session()
        example_2_simple_dataframe()
        example_3_dataframe_operations()
        example_4_aggregations()
        example_5_sql_operations()
        example_6_reading_writing_data()
        example_7_error_handling()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
        print("\n📚 Next Steps:")
        print("   1. Explore DataFrame operations in 02_dataframe_basics.py")
        print("   2. Learn about reading/writing data in 03_read_write_data.py")
        print("   3. Practice transformations in 04_transformations.py")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
