"""
Bronze to Silver ETL Job

This PySpark job transforms raw Bronze layer data into cleaned and standardized
Silver layer data with:
- Data cleaning and validation
- Deduplication logic
- Schema standardization
- Metadata enrichment
- Delta Lake support

The Silver layer represents cleaned, validated, and deduplicated data ready
for analytics and downstream processing.
"""

import argparse
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.window import Window

from shared.utils.connection_manager import connections
from shared.utils.logger import get_logger
from shared.utils.config_loader import config

logger = get_logger(__name__)


class BronzeToSilverETL:
    """
    ETL job for transforming Bronze layer to Silver layer
    
    This class handles the transformation of raw data from the Bronze layer
    into cleaned, validated, and standardized data in the Silver layer.
    """
    
    def __init__(
        self,
        spark: SparkSession,
        source_path: str,
        target_path: str,
        source_format: str = "delta",
        target_format: str = "delta",
        partition_cols: Optional[List[str]] = None,
        dedup_columns: Optional[List[str]] = None,
        order_by_column: Optional[str] = None
    ):
        """
        Initialize Bronze to Silver ETL job
        
        Args:
            spark: SparkSession instance
            source_path: Path to Bronze layer data
            target_path: Path to Silver layer data
            source_format: Source data format (delta or parquet)
            target_format: Target data format (delta or parquet)
            partition_cols: List of columns to partition by
            dedup_columns: Columns to use for deduplication
            order_by_column: Column to order by during deduplication (e.g., timestamp)
        """
        self.spark = spark
        self.source_path = source_path
        self.target_path = target_path
        self.source_format = source_format.lower()
        self.target_format = target_format.lower()
        self.partition_cols = partition_cols or []
        self.dedup_columns = dedup_columns or []
        self.order_by_column = order_by_column
        
        logger.info(f"Initialized BronzeToSilverETL: {source_path} -> {target_path}")
    
    def read_bronze_data(self) -> DataFrame:
        """
        Read data from Bronze layer
        
        Returns:
            DataFrame with Bronze layer data
        """
        logger.info(f"Reading Bronze data from {self.source_path} ({self.source_format})")
        
        try:
            if self.source_format == "delta":
                df = self.spark.read.format("delta").load(self.source_path)
            elif self.source_format == "parquet":
                df = self.spark.read.parquet(self.source_path)
            else:
                raise ValueError(f"Unsupported source format: {self.source_format}")
            
            logger.info(f"Successfully read {df.count()} records from Bronze layer")
            return df
        
        except Exception as e:
            logger.error(f"Error reading Bronze data: {str(e)}")
            raise
    
    def clean_string_columns(self, df: DataFrame) -> DataFrame:
        """
        Clean string columns by trimming whitespace and handling nulls
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with cleaned string columns
        """
        logger.info("Cleaning string columns")
        
        string_cols = [field.name for field in df.schema.fields 
                      if isinstance(field.dataType, StringType)]
        
        for col in string_cols:
            df = df.withColumn(
                col,
                F.when(
                    (F.trim(F.col(col)) == "") | F.col(col).isNull(),
                    None
                ).otherwise(F.trim(F.col(col)))
            )
        
        logger.info(f"Cleaned {len(string_cols)} string columns")
        return df
    
    def standardize_column_names(self, df: DataFrame) -> DataFrame:
        """
        Standardize column names to snake_case
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized column names
        """
        logger.info("Standardizing column names")
        
        import re
        
        for col in df.columns:
            # Convert to snake_case
            new_col = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', col)
            new_col = re.sub('([a-z0-9])([A-Z])', r'\1_\2', new_col).lower()
            new_col = re.sub(r'[^a-z0-9_]', '_', new_col)
            new_col = re.sub(r'_+', '_', new_col).strip('_')
            
            if new_col != col:
                df = df.withColumnRenamed(col, new_col)
                logger.debug(f"Renamed column: {col} -> {new_col}")
        
        return df
    
    def remove_duplicates(self, df: DataFrame) -> DataFrame:
        """
        Remove duplicate records based on dedup_columns
        
        Args:
            df: Input DataFrame
            
        Returns:
            Deduplicated DataFrame
        """
        if not self.dedup_columns:
            logger.info("No deduplication columns specified, skipping deduplication")
            return df
        
        logger.info(f"Removing duplicates based on columns: {self.dedup_columns}")
        
        initial_count = df.count()
        
        # Validate dedup columns exist
        missing_cols = set(self.dedup_columns) - set(df.columns)
        if missing_cols:
            logger.warning(f"Dedup columns not found: {missing_cols}. Skipping deduplication.")
            return df
        
        if self.order_by_column and self.order_by_column in df.columns:
            # Use window function to keep the latest record
            window_spec = Window.partitionBy(*self.dedup_columns).orderBy(
                F.col(self.order_by_column).desc()
            )
            df = df.withColumn("_row_num", F.row_number().over(window_spec)) \
                   .filter(F.col("_row_num") == 1) \
                   .drop("_row_num")
        else:
            # Simple deduplication
            df = df.dropDuplicates(self.dedup_columns)
        
        final_count = df.count()
        duplicates_removed = initial_count - final_count
        
        logger.info(f"Removed {duplicates_removed} duplicate records")
        logger.info(f"Remaining records: {final_count}")
        
        return df
    
    def add_metadata_columns(self, df: DataFrame) -> DataFrame:
        """
        Add metadata columns for tracking and auditing
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with metadata columns
        """
        logger.info("Adding metadata columns")
        
        current_timestamp = F.current_timestamp()
        
        df = df.withColumn("silver_load_timestamp", current_timestamp) \
               .withColumn("silver_layer", F.lit("silver")) \
               .withColumn("data_quality_flag", F.lit("valid"))
        
        # Add partition date if not exists
        if "partition_date" not in df.columns:
            df = df.withColumn("partition_date", F.current_date())
        
        return df
    
    def apply_data_quality_rules(self, df: DataFrame) -> DataFrame:
        """
        Apply data quality rules and flag invalid records
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with data quality flags
        """
        logger.info("Applying data quality rules")
        
        # Example quality rules - customize based on your requirements
        
        # Flag records with too many nulls
        null_count_threshold = len(df.columns) * 0.5
        null_count_expr = sum(F.when(F.col(c).isNull(), 1).otherwise(0) 
                             for c in df.columns)
        
        df = df.withColumn(
            "data_quality_flag",
            F.when(
                null_count_expr > null_count_threshold,
                "invalid_too_many_nulls"
            ).otherwise(F.col("data_quality_flag"))
        )
        
        # Count quality flags
        quality_summary = df.groupBy("data_quality_flag").count().collect()
        for row in quality_summary:
            logger.info(f"Quality flag '{row['data_quality_flag']}': {row['count']} records")
        
        return df
    
    def validate_schema(self, df: DataFrame) -> bool:
        """
        Validate the DataFrame schema
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        logger.info("Validating schema")
        
        # Check if DataFrame is empty
        if df.rdd.isEmpty():
            logger.warning("DataFrame is empty")
            return False
        
        # Check for required metadata columns
        required_cols = ["silver_load_timestamp", "silver_layer", "data_quality_flag"]
        missing_cols = set(required_cols) - set(df.columns)
        
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        logger.info("Schema validation passed")
        return True
    
    def write_silver_data(self, df: DataFrame, mode: str = "overwrite"):
        """
        Write data to Silver layer
        
        Args:
            df: DataFrame to write
            mode: Write mode (overwrite, append, merge)
        """
        logger.info(f"Writing Silver data to {self.target_path} ({self.target_format})")
        logger.info(f"Write mode: {mode}")
        
        try:
            writer = df.write.mode(mode)
            
            # Add partitioning if specified
            if self.partition_cols:
                logger.info(f"Partitioning by: {self.partition_cols}")
                writer = writer.partitionBy(*self.partition_cols)
            
            # Write based on format
            if self.target_format == "delta":
                writer.format("delta").save(self.target_path)
            elif self.target_format == "parquet":
                writer.parquet(self.target_path)
            else:
                raise ValueError(f"Unsupported target format: {self.target_format}")
            
            record_count = df.count()
            logger.info(f"Successfully wrote {record_count} records to Silver layer")
            
        except Exception as e:
            logger.error(f"Error writing Silver data: {str(e)}")
            raise
    
    def run(self, write_mode: str = "overwrite") -> Dict[str, Any]:
        """
        Execute the complete Bronze to Silver ETL pipeline
        
        Args:
            write_mode: Write mode for target data
            
        Returns:
            Dictionary with job statistics
        """
        logger.info("=" * 80)
        logger.info("Starting Bronze to Silver ETL Pipeline")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Read Bronze data
            df = self.read_bronze_data()
            source_count = df.count()
            
            # Step 2: Standardize column names
            df = self.standardize_column_names(df)
            
            # Step 3: Clean string columns
            df = self.clean_string_columns(df)
            
            # Step 4: Remove duplicates
            df = self.remove_duplicates(df)
            
            # Step 5: Apply data quality rules
            df = self.apply_data_quality_rules(df)
            
            # Step 6: Add metadata columns
            df = self.add_metadata_columns(df)
            
            # Step 7: Validate schema
            if not self.validate_schema(df):
                raise ValueError("Schema validation failed")
            
            # Step 8: Write to Silver layer
            self.write_silver_data(df, mode=write_mode)
            
            target_count = df.count()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            stats = {
                "source_count": source_count,
                "target_count": target_count,
                "records_filtered": source_count - target_count,
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "status": "SUCCESS"
            }
            
            logger.info("=" * 80)
            logger.info("Bronze to Silver ETL Pipeline Completed Successfully")
            logger.info(f"Source records: {source_count}")
            logger.info(f"Target records: {target_count}")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info("=" * 80)
            
            return stats
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)
            stats = {
                "status": "FAILED",
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
            return stats


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Bronze to Silver ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with Delta format
  python bronze_to_silver.py \\
    --source-path /data/bronze/customers \\
    --target-path /data/silver/customers
  
  # With deduplication and partitioning
  python bronze_to_silver.py \\
    --source-path /data/bronze/transactions \\
    --target-path /data/silver/transactions \\
    --dedup-columns transaction_id \\
    --order-by-column timestamp \\
    --partition-cols partition_date \\
    --write-mode append
  
  # Using Parquet format
  python bronze_to_silver.py \\
    --source-path /data/bronze/events \\
    --target-path /data/silver/events \\
    --source-format parquet \\
    --target-format parquet
        """
    )
    
    parser.add_argument(
        "--source-path",
        required=True,
        help="Path to Bronze layer data"
    )
    
    parser.add_argument(
        "--target-path",
        required=True,
        help="Path to Silver layer data"
    )
    
    parser.add_argument(
        "--source-format",
        default="delta",
        choices=["delta", "parquet"],
        help="Source data format (default: delta)"
    )
    
    parser.add_argument(
        "--target-format",
        default="delta",
        choices=["delta", "parquet"],
        help="Target data format (default: delta)"
    )
    
    parser.add_argument(
        "--partition-cols",
        nargs="+",
        help="Columns to partition by"
    )
    
    parser.add_argument(
        "--dedup-columns",
        nargs="+",
        help="Columns to use for deduplication"
    )
    
    parser.add_argument(
        "--order-by-column",
        help="Column to order by during deduplication (e.g., timestamp)"
    )
    
    parser.add_argument(
        "--write-mode",
        default="overwrite",
        choices=["overwrite", "append"],
        help="Write mode for target data (default: overwrite)"
    )
    
    parser.add_argument(
        "--app-name",
        default="BronzeToSilverETL",
        help="Spark application name"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for Bronze to Silver ETL job"""
    args = parse_arguments()
    
    # Override Spark app name if provided
    if args.app_name:
        import os
        os.environ['SPARK_APP_NAME'] = args.app_name
    
    # Get Spark session from connection manager
    spark = connections.spark
    
    try:
        # Initialize ETL job
        etl = BronzeToSilverETL(
            spark=spark,
            source_path=args.source_path,
            target_path=args.target_path,
            source_format=args.source_format,
            target_format=args.target_format,
            partition_cols=args.partition_cols,
            dedup_columns=args.dedup_columns,
            order_by_column=args.order_by_column
        )
        
        # Run ETL pipeline
        stats = etl.run(write_mode=args.write_mode)
        
        # Exit with appropriate code
        if stats["status"] == "SUCCESS":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Job failed: {str(e)}", exc_info=True)
        sys.exit(1)
    
    finally:
        # Clean up
        connections.stop_spark()


if __name__ == "__main__":
    main()
