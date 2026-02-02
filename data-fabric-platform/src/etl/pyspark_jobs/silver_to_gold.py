"""
Silver to Gold ETL Job

This PySpark job transforms Silver layer data into Gold layer analytics-ready data with:
- Aggregations and metrics calculation
- Denormalization for analytics
- Dimension and fact table creation
- Business logic application
- Delta Lake support

The Gold layer represents business-level aggregated and analytics-ready data
optimized for reporting and BI tools.
"""

import argparse
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window

from shared.utils.connection_manager import connections
from shared.utils.logger import get_logger
from shared.utils.config_loader import config

logger = get_logger(__name__)


class SilverToGoldETL:
    """
    ETL job for transforming Silver layer to Gold layer
    
    This class handles the transformation of cleaned Silver layer data
    into business-ready Gold layer with aggregations, denormalization,
    and derived metrics.
    """
    
    def __init__(
        self,
        spark: SparkSession,
        source_path: str,
        target_path: str,
        source_format: str = "delta",
        target_format: str = "delta",
        partition_cols: Optional[List[str]] = None,
        table_type: str = "fact",
        aggregation_level: Optional[str] = None
    ):
        """
        Initialize Silver to Gold ETL job
        
        Args:
            spark: SparkSession instance
            source_path: Path to Silver layer data (can be dict for multiple sources)
            target_path: Path to Gold layer data
            source_format: Source data format (delta or parquet)
            target_format: Target data format (delta or parquet)
            partition_cols: List of columns to partition by
            table_type: Type of table (fact or dimension)
            aggregation_level: Level of aggregation (daily, monthly, yearly, etc.)
        """
        self.spark = spark
        self.source_path = source_path
        self.target_path = target_path
        self.source_format = source_format.lower()
        self.target_format = target_format.lower()
        self.partition_cols = partition_cols or []
        self.table_type = table_type.lower()
        self.aggregation_level = aggregation_level
        
        logger.info(f"Initialized SilverToGoldETL: {source_path} -> {target_path}")
        logger.info(f"Table type: {table_type}, Aggregation level: {aggregation_level}")
    
    def read_silver_data(self, path: Optional[str] = None) -> DataFrame:
        """
        Read data from Silver layer
        
        Args:
            path: Optional specific path (uses self.source_path if not provided)
            
        Returns:
            DataFrame with Silver layer data
        """
        read_path = path or self.source_path
        logger.info(f"Reading Silver data from {read_path} ({self.source_format})")
        
        try:
            if self.source_format == "delta":
                df = self.spark.read.format("delta").load(read_path)
            elif self.source_format == "parquet":
                df = self.spark.read.parquet(read_path)
            else:
                raise ValueError(f"Unsupported source format: {self.source_format}")
            
            # Filter for valid data quality only
            if "data_quality_flag" in df.columns:
                initial_count = df.count()
                df = df.filter(F.col("data_quality_flag") == "valid")
                filtered_count = initial_count - df.count()
                if filtered_count > 0:
                    logger.info(f"Filtered out {filtered_count} invalid quality records")
            
            logger.info(f"Successfully read {df.count()} records from Silver layer")
            return df
        
        except Exception as e:
            logger.error(f"Error reading Silver data: {str(e)}")
            raise
    
    def create_time_dimension(self, df: DataFrame, date_column: str) -> DataFrame:
        """
        Create time-based dimensions from date column
        
        Args:
            df: Input DataFrame
            date_column: Name of date column to extract dimensions from
            
        Returns:
            DataFrame with time dimensions
        """
        logger.info(f"Creating time dimensions from column: {date_column}")
        
        if date_column not in df.columns:
            logger.warning(f"Date column '{date_column}' not found, skipping time dimensions")
            return df
        
        df = df.withColumn("year", F.year(F.col(date_column))) \
               .withColumn("quarter", F.quarter(F.col(date_column))) \
               .withColumn("month", F.month(F.col(date_column))) \
               .withColumn("day", F.dayofmonth(F.col(date_column))) \
               .withColumn("day_of_week", F.dayofweek(F.col(date_column))) \
               .withColumn("day_of_year", F.dayofyear(F.col(date_column))) \
               .withColumn("week_of_year", F.weekofyear(F.col(date_column))) \
               .withColumn("month_name", F.date_format(F.col(date_column), "MMMM")) \
               .withColumn("day_name", F.date_format(F.col(date_column), "EEEE"))
        
        logger.info("Time dimensions created successfully")
        return df
    
    def apply_aggregations(
        self,
        df: DataFrame,
        group_by_cols: List[str],
        agg_expressions: Dict[str, str]
    ) -> DataFrame:
        """
        Apply aggregations to create summary data
        
        Args:
            df: Input DataFrame
            group_by_cols: Columns to group by
            agg_expressions: Dictionary of column -> aggregation function
                           e.g., {"amount": "sum", "count": "count"}
        
        Returns:
            Aggregated DataFrame
        """
        logger.info(f"Applying aggregations. Group by: {group_by_cols}")
        logger.info(f"Aggregation expressions: {agg_expressions}")
        
        # Validate group by columns exist
        missing_cols = set(group_by_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Group by columns not found: {missing_cols}")
        
        # Build aggregation expressions
        agg_exprs = []
        for col, agg_func in agg_expressions.items():
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found, skipping aggregation")
                continue
            
            agg_func_lower = agg_func.lower()
            if agg_func_lower == "sum":
                agg_exprs.append(F.sum(col).alias(f"{col}_sum"))
            elif agg_func_lower == "avg":
                agg_exprs.append(F.avg(col).alias(f"{col}_avg"))
            elif agg_func_lower == "min":
                agg_exprs.append(F.min(col).alias(f"{col}_min"))
            elif agg_func_lower == "max":
                agg_exprs.append(F.max(col).alias(f"{col}_max"))
            elif agg_func_lower == "count":
                agg_exprs.append(F.count(col).alias(f"{col}_count"))
            elif agg_func_lower == "count_distinct":
                agg_exprs.append(F.countDistinct(col).alias(f"{col}_distinct_count"))
            elif agg_func_lower == "stddev":
                agg_exprs.append(F.stddev(col).alias(f"{col}_stddev"))
            else:
                logger.warning(f"Unknown aggregation function: {agg_func}")
        
        # Add record count
        agg_exprs.append(F.count("*").alias("record_count"))
        
        # Perform aggregation
        agg_df = df.groupBy(*group_by_cols).agg(*agg_exprs)
        
        logger.info(f"Aggregation complete. Result count: {agg_df.count()}")
        return agg_df
    
    def calculate_derived_metrics(self, df: DataFrame) -> DataFrame:
        """
        Calculate derived business metrics
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with derived metrics
        """
        logger.info("Calculating derived metrics")
        
        # Example derived metrics - customize based on business needs
        
        # Calculate running totals if we have amount and date
        if all(col in df.columns for col in ["amount_sum", "partition_date"]):
            window_spec = Window.orderBy("partition_date").rowsBetween(
                Window.unboundedPreceding, Window.currentRow
            )
            df = df.withColumn("running_total", F.sum("amount_sum").over(window_spec))
        
        # Calculate percentage changes
        if "amount_sum" in df.columns and "partition_date" in df.columns:
            window_spec = Window.orderBy("partition_date").rowsBetween(-1, -1)
            df = df.withColumn("previous_amount", F.lag("amount_sum", 1).over(
                Window.orderBy("partition_date")
            ))
            df = df.withColumn(
                "amount_change_pct",
                F.when(
                    F.col("previous_amount").isNotNull() & (F.col("previous_amount") != 0),
                    ((F.col("amount_sum") - F.col("previous_amount")) / 
                     F.col("previous_amount") * 100)
                ).otherwise(None)
            ).drop("previous_amount")
        
        # Calculate moving averages
        if "amount_sum" in df.columns and "partition_date" in df.columns:
            window_7d = Window.orderBy("partition_date").rowsBetween(-6, 0)
            window_30d = Window.orderBy("partition_date").rowsBetween(-29, 0)
            
            df = df.withColumn("moving_avg_7d", F.avg("amount_sum").over(window_7d)) \
                   .withColumn("moving_avg_30d", F.avg("amount_sum").over(window_30d))
        
        logger.info("Derived metrics calculated successfully")
        return df
    
    def denormalize_with_dimensions(
        self,
        fact_df: DataFrame,
        dimension_dfs: Dict[str, DataFrame],
        join_keys: Dict[str, tuple]
    ) -> DataFrame:
        """
        Denormalize fact table with dimension tables
        
        Args:
            fact_df: Fact table DataFrame
            dimension_dfs: Dictionary of dimension name -> DataFrame
            join_keys: Dictionary of dimension name -> (fact_key, dim_key) tuple
            
        Returns:
            Denormalized DataFrame
        """
        logger.info("Starting denormalization")
        
        result_df = fact_df
        
        for dim_name, dim_df in dimension_dfs.items():
            if dim_name not in join_keys:
                logger.warning(f"No join key specified for dimension: {dim_name}")
                continue
            
            fact_key, dim_key = join_keys[dim_name]
            
            if fact_key not in result_df.columns:
                logger.warning(f"Fact key '{fact_key}' not found, skipping dimension: {dim_name}")
                continue
            
            if dim_key not in dim_df.columns:
                logger.warning(f"Dimension key '{dim_key}' not found in {dim_name}")
                continue
            
            # Add prefix to dimension columns to avoid conflicts
            dim_df_prefixed = dim_df.select([
                F.col(c).alias(f"{dim_name}_{c}") if c != dim_key else F.col(c)
                for c in dim_df.columns
            ])
            
            # Perform left join
            result_df = result_df.join(
                dim_df_prefixed,
                result_df[fact_key] == dim_df_prefixed[dim_key],
                "left"
            ).drop(dim_key)
            
            logger.info(f"Joined with dimension: {dim_name}")
        
        logger.info("Denormalization complete")
        return result_df
    
    def create_fact_table(
        self,
        df: DataFrame,
        group_by_cols: List[str],
        measure_cols: Dict[str, str]
    ) -> DataFrame:
        """
        Create a fact table with measures and dimensions
        
        Args:
            df: Input DataFrame
            group_by_cols: Dimension columns (group by)
            measure_cols: Measure columns with aggregation functions
            
        Returns:
            Fact table DataFrame
        """
        logger.info("Creating fact table")
        
        # Apply aggregations
        fact_df = self.apply_aggregations(df, group_by_cols, measure_cols)
        
        # Calculate derived metrics
        fact_df = self.calculate_derived_metrics(fact_df)
        
        return fact_df
    
    def create_dimension_table(
        self,
        df: DataFrame,
        dimension_cols: List[str],
        include_scd2: bool = False
    ) -> DataFrame:
        """
        Create a dimension table
        
        Args:
            df: Input DataFrame
            dimension_cols: Columns to include in dimension
            include_scd2: Include SCD Type 2 columns (start_date, end_date, is_current)
            
        Returns:
            Dimension table DataFrame
        """
        logger.info(f"Creating dimension table with columns: {dimension_cols}")
        
        # Validate columns exist
        missing_cols = set(dimension_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dimension columns not found: {missing_cols}")
        
        # Select and deduplicate dimension columns
        dim_df = df.select(*dimension_cols).distinct()
        
        # Add surrogate key
        dim_df = dim_df.withColumn(
            "dimension_id",
            F.monotonically_increasing_id()
        )
        
        if include_scd2:
            # Add SCD Type 2 columns
            dim_df = dim_df.withColumn("start_date", F.current_date()) \
                           .withColumn("end_date", F.lit(None).cast(DateType())) \
                           .withColumn("is_current", F.lit(True))
            
            logger.info("Added SCD Type 2 columns")
        
        logger.info(f"Dimension table created with {dim_df.count()} records")
        return dim_df
    
    def apply_business_rules(self, df: DataFrame) -> DataFrame:
        """
        Apply business-specific rules and transformations
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with business rules applied
        """
        logger.info("Applying business rules")
        
        # Example business rules - customize based on requirements
        
        # Categorize amounts into buckets
        if "amount_sum" in df.columns:
            df = df.withColumn(
                "amount_category",
                F.when(F.col("amount_sum") < 1000, "Small")
                 .when((F.col("amount_sum") >= 1000) & (F.col("amount_sum") < 10000), "Medium")
                 .when(F.col("amount_sum") >= 10000, "Large")
                 .otherwise("Unknown")
            )
        
        # Flag high-value transactions
        if "amount_sum" in df.columns:
            # Calculate percentile for flagging
            percentile_95 = df.approxQuantile("amount_sum", [0.95], 0.01)[0]
            df = df.withColumn(
                "is_high_value",
                F.when(F.col("amount_sum") >= percentile_95, True).otherwise(False)
            )
        
        # Add business date calculations
        if "partition_date" in df.columns:
            df = df.withColumn("is_weekend", 
                F.when(F.dayofweek("partition_date").isin([1, 7]), True).otherwise(False)
            )
            df = df.withColumn("is_month_end",
                F.when(
                    F.dayofmonth("partition_date") == 
                    F.dayofmonth(F.last_day("partition_date")),
                    True
                ).otherwise(False)
            )
        
        logger.info("Business rules applied successfully")
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
        
        df = df.withColumn("gold_load_timestamp", current_timestamp) \
               .withColumn("gold_layer", F.lit("gold")) \
               .withColumn("table_type", F.lit(self.table_type))
        
        if self.aggregation_level:
            df = df.withColumn("aggregation_level", F.lit(self.aggregation_level))
        
        return df
    
    def optimize_for_analytics(self, df: DataFrame) -> DataFrame:
        """
        Optimize DataFrame for analytics queries
        
        Args:
            df: Input DataFrame
            
        Returns:
            Optimized DataFrame
        """
        logger.info("Optimizing for analytics")
        
        # Cache if dataset is small enough
        row_count = df.count()
        if row_count < 1000000:  # Cache if less than 1M rows
            df = df.cache()
            logger.info("DataFrame cached for optimization")
        
        # Repartition if needed
        current_partitions = df.rdd.getNumPartitions()
        optimal_partitions = max(row_count // 100000, 1)  # ~100k rows per partition
        
        if current_partitions > optimal_partitions * 2:
            df = df.coalesce(int(optimal_partitions))
            logger.info(f"Coalesced partitions: {current_partitions} -> {optimal_partitions}")
        elif current_partitions < optimal_partitions // 2:
            df = df.repartition(int(optimal_partitions))
            logger.info(f"Repartitioned: {current_partitions} -> {optimal_partitions}")
        
        return df
    
    def write_gold_data(self, df: DataFrame, mode: str = "overwrite"):
        """
        Write data to Gold layer
        
        Args:
            df: DataFrame to write
            mode: Write mode (overwrite, append)
        """
        logger.info(f"Writing Gold data to {self.target_path} ({self.target_format})")
        logger.info(f"Write mode: {mode}")
        
        try:
            writer = df.write.mode(mode)
            
            # Add partitioning if specified
            if self.partition_cols:
                logger.info(f"Partitioning by: {self.partition_cols}")
                writer = writer.partitionBy(*self.partition_cols)
            
            # Enable optimizations for Delta
            if self.target_format == "delta":
                writer = writer \
                    .option("overwriteSchema", "true") \
                    .option("optimizeWrite", "true") \
                    .option("autoOptimize.optimizeWrite", "true")
            
            # Write based on format
            if self.target_format == "delta":
                writer.format("delta").save(self.target_path)
            elif self.target_format == "parquet":
                writer.parquet(self.target_path)
            else:
                raise ValueError(f"Unsupported target format: {self.target_format}")
            
            record_count = df.count()
            logger.info(f"Successfully wrote {record_count} records to Gold layer")
            
        except Exception as e:
            logger.error(f"Error writing Gold data: {str(e)}")
            raise
    
    def run(
        self,
        transformation_type: str = "aggregation",
        write_mode: str = "overwrite",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the complete Silver to Gold ETL pipeline
        
        Args:
            transformation_type: Type of transformation (aggregation, dimension, fact, denormalization)
            write_mode: Write mode for target data
            **kwargs: Additional parameters for specific transformations
            
        Returns:
            Dictionary with job statistics
        """
        logger.info("=" * 80)
        logger.info("Starting Silver to Gold ETL Pipeline")
        logger.info(f"Transformation type: {transformation_type}")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Read Silver data
            df = self.read_silver_data()
            source_count = df.count()
            
            # Apply transformation based on type
            if transformation_type == "aggregation":
                group_by_cols = kwargs.get("group_by_cols", ["partition_date"])
                measure_cols = kwargs.get("measure_cols", {})
                
                df = self.apply_aggregations(df, group_by_cols, measure_cols)
                df = self.calculate_derived_metrics(df)
                
            elif transformation_type == "fact":
                group_by_cols = kwargs.get("group_by_cols", ["partition_date"])
                measure_cols = kwargs.get("measure_cols", {})
                
                df = self.create_fact_table(df, group_by_cols, measure_cols)
                
            elif transformation_type == "dimension":
                dimension_cols = kwargs.get("dimension_cols", [])
                include_scd2 = kwargs.get("include_scd2", False)
                
                df = self.create_dimension_table(df, dimension_cols, include_scd2)
                
            elif transformation_type == "denormalization":
                # Assumes dimension DataFrames and join keys are provided
                dimension_dfs = kwargs.get("dimension_dfs", {})
                join_keys = kwargs.get("join_keys", {})
                
                df = self.denormalize_with_dimensions(df, dimension_dfs, join_keys)
            
            # Apply business rules
            df = self.apply_business_rules(df)
            
            # Add metadata
            df = self.add_metadata_columns(df)
            
            # Optimize for analytics
            df = self.optimize_for_analytics(df)
            
            # Write to Gold layer
            self.write_gold_data(df, mode=write_mode)
            
            target_count = df.count()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            stats = {
                "source_count": source_count,
                "target_count": target_count,
                "transformation_type": transformation_type,
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "status": "SUCCESS"
            }
            
            logger.info("=" * 80)
            logger.info("Silver to Gold ETL Pipeline Completed Successfully")
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
        description="Silver to Gold ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily aggregation
  python silver_to_gold.py \\
    --source-path /data/silver/transactions \\
    --target-path /data/gold/daily_transactions \\
    --transformation-type aggregation \\
    --group-by-cols partition_date category \\
    --measure-cols amount:sum quantity:sum \\
    --aggregation-level daily
  
  # Create fact table
  python silver_to_gold.py \\
    --source-path /data/silver/sales \\
    --target-path /data/gold/fact_sales \\
    --transformation-type fact \\
    --group-by-cols date_id product_id customer_id \\
    --measure-cols revenue:sum cost:sum profit:sum \\
    --partition-cols partition_date
  
  # Create dimension table
  python silver_to_gold.py \\
    --source-path /data/silver/customers \\
    --target-path /data/gold/dim_customers \\
    --transformation-type dimension \\
    --dimension-cols customer_id customer_name city state country \\
    --include-scd2
        """
    )
    
    parser.add_argument(
        "--source-path",
        required=True,
        help="Path to Silver layer data"
    )
    
    parser.add_argument(
        "--target-path",
        required=True,
        help="Path to Gold layer data"
    )
    
    parser.add_argument(
        "--transformation-type",
        default="aggregation",
        choices=["aggregation", "fact", "dimension", "denormalization"],
        help="Type of transformation to apply (default: aggregation)"
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
        "--group-by-cols",
        nargs="+",
        help="Columns to group by for aggregation/fact tables"
    )
    
    parser.add_argument(
        "--measure-cols",
        nargs="+",
        help="Measure columns with aggregation functions (format: col:func col:func)"
    )
    
    parser.add_argument(
        "--dimension-cols",
        nargs="+",
        help="Columns to include in dimension table"
    )
    
    parser.add_argument(
        "--include-scd2",
        action="store_true",
        help="Include SCD Type 2 columns in dimension table"
    )
    
    parser.add_argument(
        "--aggregation-level",
        choices=["hourly", "daily", "weekly", "monthly", "yearly"],
        help="Level of aggregation"
    )
    
    parser.add_argument(
        "--table-type",
        default="fact",
        choices=["fact", "dimension"],
        help="Type of table being created (default: fact)"
    )
    
    parser.add_argument(
        "--write-mode",
        default="overwrite",
        choices=["overwrite", "append"],
        help="Write mode for target data (default: overwrite)"
    )
    
    parser.add_argument(
        "--app-name",
        default="SilverToGoldETL",
        help="Spark application name"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for Silver to Gold ETL job"""
    args = parse_arguments()
    
    # Override Spark app name if provided
    if args.app_name:
        import os
        os.environ['SPARK_APP_NAME'] = args.app_name
    
    # Get Spark session from connection manager
    spark = connections.spark
    
    try:
        # Initialize ETL job
        etl = SilverToGoldETL(
            spark=spark,
            source_path=args.source_path,
            target_path=args.target_path,
            source_format=args.source_format,
            target_format=args.target_format,
            partition_cols=args.partition_cols,
            table_type=args.table_type,
            aggregation_level=args.aggregation_level
        )
        
        # Parse measure columns if provided
        measure_cols = {}
        if args.measure_cols:
            for measure in args.measure_cols:
                try:
                    col, func = measure.split(":")
                    measure_cols[col] = func
                except ValueError:
                    logger.warning(f"Invalid measure format: {measure}. Expected 'column:function'")
        
        # Build kwargs for run method
        run_kwargs = {}
        if args.group_by_cols:
            run_kwargs["group_by_cols"] = args.group_by_cols
        if measure_cols:
            run_kwargs["measure_cols"] = measure_cols
        if args.dimension_cols:
            run_kwargs["dimension_cols"] = args.dimension_cols
        if args.include_scd2:
            run_kwargs["include_scd2"] = args.include_scd2
        
        # Run ETL pipeline
        stats = etl.run(
            transformation_type=args.transformation_type,
            write_mode=args.write_mode,
            **run_kwargs
        )
        
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
