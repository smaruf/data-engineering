"""
Microsoft Fabric Lakehouse Tables Module

This module demonstrates creating and managing Delta tables in Fabric Lakehouse
using PySpark and Delta Lake features.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta import DeltaTable
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LakehouseTableManager:
    """
    Manager for Delta tables in Fabric Lakehouse.
    
    Provides methods to create, manage, and query Delta tables.
    """
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Initialize Lakehouse Table Manager.
        
        Args:
            spark (SparkSession, optional): Spark session. Creates new if None.
        """
        self.spark = spark or self._create_spark_session()
        logger.info("Initialized LakehouseTableManager")
    
    def _create_spark_session(self) -> SparkSession:
        """
        Create Spark session configured for Delta Lake.
        
        Returns:
            SparkSession: Configured Spark session
        """
        return (SparkSession.builder
                .appName("FabricLakehouseTableManager")
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                .getOrCreate())
    
    def create_managed_table(
        self,
        df: DataFrame,
        table_name: str,
        mode: str = "overwrite",
        partition_by: Optional[List[str]] = None
    ) -> bool:
        """
        Create a managed Delta table.
        
        Args:
            df (DataFrame): Spark DataFrame to save
            table_name (str): Table name
            mode (str): Save mode ('overwrite', 'append', 'error', 'ignore')
            partition_by (list, optional): Columns to partition by
        
        Returns:
            bool: True if successful
        
        Example:
            >>> df = spark.createDataFrame([(1, 'a'), (2, 'b')], ['id', 'value'])
            >>> manager.create_managed_table(df, "my_table", partition_by=['id'])
        """
        logger.info(f"Creating managed table '{table_name}'")
        
        try:
            writer = df.write.format("delta").mode(mode)
            
            if partition_by:
                writer = writer.partitionBy(*partition_by)
                logger.info(f"Partitioning by: {partition_by}")
            
            writer.saveAsTable(table_name)
            
            logger.info(f"✅ Managed table '{table_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create managed table: {e}")
            raise
    
    def create_external_table(
        self,
        df: DataFrame,
        table_path: str,
        mode: str = "overwrite",
        partition_by: Optional[List[str]] = None
    ) -> bool:
        """
        Create an external Delta table.
        
        Args:
            df (DataFrame): Spark DataFrame to save
            table_path (str): Path where table data will be stored
            mode (str): Save mode
            partition_by (list, optional): Columns to partition by
        
        Returns:
            bool: True if successful
        """
        logger.info(f"Creating external table at '{table_path}'")
        
        try:
            writer = df.write.format("delta").mode(mode)
            
            if partition_by:
                writer = writer.partitionBy(*partition_by)
            
            writer.save(table_path)
            
            logger.info(f"✅ External table created at '{table_path}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create external table: {e}")
            raise
    
    def read_table(self, table_name: str) -> DataFrame:
        """
        Read data from a Delta table.
        
        Args:
            table_name (str): Table name or path
        
        Returns:
            DataFrame: Spark DataFrame
        """
        logger.info(f"Reading table '{table_name}'")
        
        try:
            df = self.spark.read.format("delta").table(table_name)
            logger.info(f"✅ Read {df.count()} rows from '{table_name}'")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read table: {e}")
            raise
    
    def upsert_data(
        self,
        target_table: str,
        source_df: DataFrame,
        merge_key: str,
        update_columns: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Upsert (merge) data into a Delta table.
        
        Args:
            target_table (str): Target table name or path
            source_df (DataFrame): Source DataFrame with updates
            merge_key (str): Column to use for matching records
            update_columns (list, optional): Columns to update. Updates all if None.
        
        Returns:
            dict: Metrics about the merge operation
        
        Example:
            >>> updates = spark.createDataFrame([(1, 'updated'), (3, 'new')], ['id', 'value'])
            >>> manager.upsert_data("my_table", updates, "id")
        """
        logger.info(f"Upserting data into '{target_table}'")
        
        try:
            delta_table = DeltaTable.forName(self.spark, target_table)
            
            # Build update expressions
            if update_columns:
                update_expr = {col: f"source.{col}" for col in update_columns}
            else:
                update_expr = {col: f"source.{col}" for col in source_df.columns}
            
            # Perform merge
            (delta_table.alias("target")
             .merge(source_df.alias("source"), f"target.{merge_key} = source.{merge_key}")
             .whenMatchedUpdate(set=update_expr)
             .whenNotMatchedInsertAll()
             .execute())
            
            logger.info(f"✅ Upsert completed for '{target_table}'")
            
            # Get operation metrics
            history = delta_table.history(1).select("operationMetrics").collect()[0][0]
            return history
            
        except Exception as e:
            logger.error(f"Failed to upsert data: {e}")
            raise
    
    def delete_records(
        self,
        table_name: str,
        condition: str
    ) -> int:
        """
        Delete records from a Delta table.
        
        Args:
            table_name (str): Table name or path
            condition (str): SQL condition for deletion
        
        Returns:
            int: Number of rows deleted
        
        Example:
            >>> manager.delete_records("my_table", "status = 'inactive'")
        """
        logger.info(f"Deleting records from '{table_name}' where {condition}")
        
        try:
            delta_table = DeltaTable.forName(self.spark, table_name)
            
            # Get count before deletion
            before_count = self.spark.table(table_name).count()
            
            # Delete records
            delta_table.delete(condition)
            
            # Get count after deletion
            after_count = self.spark.table(table_name).count()
            deleted_count = before_count - after_count
            
            logger.info(f"✅ Deleted {deleted_count} records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete records: {e}")
            raise
    
    def optimize_table(
        self,
        table_name: str,
        z_order_by: Optional[List[str]] = None
    ) -> bool:
        """
        Optimize Delta table by compacting small files.
        
        Args:
            table_name (str): Table name or path
            z_order_by (list, optional): Columns for Z-ordering
        
        Returns:
            bool: True if successful
        """
        logger.info(f"Optimizing table '{table_name}'")
        
        try:
            delta_table = DeltaTable.forName(self.spark, table_name)
            
            optimize_cmd = delta_table.optimize()
            
            if z_order_by:
                optimize_cmd = optimize_cmd.executeZOrderBy(z_order_by)
                logger.info(f"Z-ordering by: {z_order_by}")
            else:
                optimize_cmd.executeCompaction()
            
            logger.info(f"✅ Table '{table_name}' optimized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize table: {e}")
            raise
    
    def vacuum_table(
        self,
        table_name: str,
        retention_hours: int = 168
    ) -> bool:
        """
        Clean up old files from Delta table.
        
        Args:
            table_name (str): Table name or path
            retention_hours (int): Hours to retain old files (default: 168 = 7 days)
        
        Returns:
            bool: True if successful
        
        Warning:
            This permanently deletes old file versions. Time travel to deleted
            versions will no longer be possible.
        """
        logger.info(f"Vacuuming table '{table_name}' (retention: {retention_hours}h)")
        
        try:
            delta_table = DeltaTable.forName(self.spark, table_name)
            delta_table.vacuum(retention_hours)
            
            logger.info(f"✅ Table '{table_name}' vacuumed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to vacuum table: {e}")
            raise
    
    def get_table_history(
        self,
        table_name: str,
        limit: int = 10
    ) -> DataFrame:
        """
        Get Delta table history.
        
        Args:
            table_name (str): Table name or path
            limit (int): Number of history entries to return
        
        Returns:
            DataFrame: Table history
        """
        logger.info(f"Fetching history for '{table_name}'")
        
        try:
            delta_table = DeltaTable.forName(self.spark, table_name)
            history_df = delta_table.history(limit)
            
            logger.info(f"✅ Retrieved {history_df.count()} history entries")
            return history_df
            
        except Exception as e:
            logger.error(f"Failed to get table history: {e}")
            raise
    
    def time_travel_query(
        self,
        table_name: str,
        version: Optional[int] = None,
        timestamp: Optional[str] = None
    ) -> DataFrame:
        """
        Query a Delta table as of a specific version or timestamp.
        
        Args:
            table_name (str): Table name or path
            version (int, optional): Version number
            timestamp (str, optional): Timestamp (ISO 8601 format)
        
        Returns:
            DataFrame: Data as of specified version/timestamp
        
        Example:
            >>> df = manager.time_travel_query("my_table", version=5)
            >>> df = manager.time_travel_query("my_table", timestamp="2024-01-01T00:00:00Z")
        """
        logger.info(f"Time travel query on '{table_name}'")
        
        try:
            if version is not None:
                df = self.spark.read.format("delta").option("versionAsOf", version).table(table_name)
                logger.info(f"Read table at version {version}")
            elif timestamp is not None:
                df = self.spark.read.format("delta").option("timestampAsOf", timestamp).table(table_name)
                logger.info(f"Read table at timestamp {timestamp}")
            else:
                raise ValueError("Either version or timestamp must be provided")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to perform time travel query: {e}")
            raise


def create_sample_tables(manager: LakehouseTableManager):
    """
    Create sample Delta tables for demonstration.
    
    Args:
        manager (LakehouseTableManager): Table manager instance
    """
    spark = manager.spark
    
    # Sample 1: Customer Dimension Table
    print("\n1. Creating customer dimension table")
    print("-" * 60)
    
    customers_data = [
        (1, "John Doe", "john@example.com", "USA", "2024-01-01"),
        (2, "Jane Smith", "jane@example.com", "Canada", "2024-01-02"),
        (3, "Bob Johnson", "bob@example.com", "UK", "2024-01-03"),
    ]
    
    customers_schema = StructType([
        StructField("customer_id", IntegerType(), False),
        StructField("name", StringType(), False),
        StructField("email", StringType(), False),
        StructField("country", StringType(), True),
        StructField("created_date", StringType(), True)
    ])
    
    customers_df = spark.createDataFrame(customers_data, customers_schema)
    manager.create_managed_table(customers_df, "dim_customers")
    print("✅ Created dim_customers table")
    
    # Sample 2: Sales Fact Table (partitioned)
    print("\n2. Creating sales fact table (partitioned)")
    print("-" * 60)
    
    sales_data = [
        (1, 1, 101, 5, 99.99, "2024-01-15", "2024", "01"),
        (2, 2, 102, 3, 149.99, "2024-01-16", "2024", "01"),
        (3, 1, 103, 2, 199.99, "2024-02-01", "2024", "02"),
    ]
    
    sales_schema = StructType([
        StructField("order_id", IntegerType(), False),
        StructField("customer_id", IntegerType(), False),
        StructField("product_id", IntegerType(), False),
        StructField("quantity", IntegerType(), False),
        StructField("amount", DoubleType(), False),
        StructField("order_date", StringType(), False),
        StructField("year", StringType(), False),
        StructField("month", StringType(), False)
    ])
    
    sales_df = spark.createDataFrame(sales_data, sales_schema)
    manager.create_managed_table(
        sales_df,
        "fact_sales",
        partition_by=["year", "month"]
    )
    print("✅ Created fact_sales table (partitioned by year, month)")


def main():
    """
    Example usage of Lakehouse Table Manager.
    """
    print("=" * 60)
    print("Microsoft Fabric Lakehouse Delta Tables Examples")
    print("=" * 60)
    
    try:
        # Initialize manager
        manager = LakehouseTableManager()
        
        # Create sample tables
        create_sample_tables(manager)
        
        # Example 3: Read table
        print("\n3. Reading customers table")
        print("-" * 60)
        customers_df = manager.read_table("dim_customers")
        customers_df.show()
        
        # Example 4: Upsert data
        print("\n4. Upserting data")
        print("-" * 60)
        
        updates = manager.spark.createDataFrame([
            (1, "John Doe Updated", "john.new@example.com", "USA", "2024-01-01"),
            (4, "Alice Brown", "alice@example.com", "Germany", "2024-01-04")
        ], customers_df.schema)
        
        manager.upsert_data("dim_customers", updates, "customer_id")
        
        print("After upsert:")
        manager.read_table("dim_customers").show()
        
        # Example 5: Delete records
        print("\n5. Deleting records")
        print("-" * 60)
        deleted = manager.delete_records("dim_customers", "customer_id = 4")
        print(f"Deleted {deleted} records")
        
        # Example 6: Table history
        print("\n6. Viewing table history")
        print("-" * 60)
        history = manager.get_table_history("dim_customers", limit=5)
        history.select("version", "operation", "operationMetrics").show(truncate=False)
        
        # Example 7: Time travel
        print("\n7. Time travel query")
        print("-" * 60)
        print("Data at version 0 (original):")
        original_df = manager.time_travel_query("dim_customers", version=0)
        original_df.show()
        
        # Example 8: Optimize table
        print("\n8. Optimizing table")
        print("-" * 60)
        manager.optimize_table("fact_sales", z_order_by=["customer_id"])
        print("✅ Table optimized with Z-ordering")
        
        print("\n" + "=" * 60)
        print("Delta table examples completed")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Detailed error:")


if __name__ == "__main__":
    main()
