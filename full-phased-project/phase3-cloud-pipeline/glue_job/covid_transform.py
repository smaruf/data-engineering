"""
Enhanced AWS Glue ETL Job for COVID-19 Data Transformation
=========================================================

This PySpark script runs as an AWS Glue job that:
1. Reads raw COVID-19 data from S3 (CSV/JSON/Parquet)
2. Performs comprehensive data cleaning and validation
3. Applies business transformations and calculations
4. Writes processed data to partitioned S3 location
5. Updates Glue Data Catalog with schema information
6. Generates data quality metrics and reports

Author: Data Engineering Team
Version: 2.0
"""

import sys
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

from pyspark.context import SparkContext
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Initialize Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
logger = glueContext.get_logger()

# Configure logging
logging.basicConfig(level=logging.INFO)


class CovidDataETL:
    """Main ETL class for COVID-19 data processing"""
    
    def __init__(self, job_args: Dict[str, str]):
        """Initialize ETL job with parameters"""
        self.job_args = job_args
        self.spark = spark
        self.glue_context = glueContext
        
        # Job parameters
        self.input_path = job_args['input_s3_path']
        self.output_path = job_args['output_s3_path']
        self.database_name = job_args.get('database_name', 'covid_data_catalog')
        self.table_name = job_args.get('table_name', 'covid_processed')
        self.partition_keys = job_args.get('partition_keys', 'year,month').split(',')
        
        # Data quality thresholds
        self.min_completeness_threshold = float(job_args.get('min_completeness', '0.95'))
        self.max_error_rate = float(job_args.get('max_error_rate', '0.05'))
        
        # Processing statistics
        self.stats = {
            'input_records': 0,
            'output_records': 0,
            'invalid_records': 0,
            'duplicate_records': 0,
            'processing_start_time': datetime.now(timezone.utc),
            'processing_end_time': None
        }
        
        logger.info(f"Initialized COVID ETL job with parameters: {job_args}")
    
    def read_source_data(self) -> DataFrame:
        """
        Read source data from S3 with automatic format detection
        
        Returns:
            DataFrame: Raw COVID-19 data
        """
        logger.info(f"Reading source data from: {self.input_path}")
        
        try:
            # Try to read as Parquet first (most efficient)
            if self.input_path.endswith('.parquet') or '/parquet/' in self.input_path:
                df = self.spark.read.parquet(self.input_path)
                logger.info("Successfully read data as Parquet format")
            
            # Try JSON format
            elif self.input_path.endswith('.json') or '/json/' in self.input_path:
                df = self.spark.read.option("multiline", "true").json(self.input_path)
                logger.info("Successfully read data as JSON format")
            
            # Default to CSV format
            else:
                df = self.spark.read \
                    .option("header", "true") \
                    .option("inferSchema", "true") \
                    .option("timestampFormat", "yyyy-MM-dd HH:mm:ss") \
                    .csv(self.input_path)
                logger.info("Successfully read data as CSV format")
            
            self.stats['input_records'] = df.count()
            logger.info(f"Read {self.stats['input_records']} records from source")
            
            # Log schema information
            logger.info("Source data schema:")
            df.printSchema()
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to read source data: {str(e)}")
            raise
    
    def validate_source_data(self, df: DataFrame) -> DataFrame:
        """
        Validate source data and log data quality issues
        
        Args:
            df: Raw DataFrame
            
        Returns:
            DataFrame: Validated DataFrame
        """
        logger.info("Starting source data validation")
        
        # Check for empty dataset
        if df.count() == 0:
            raise ValueError("Source dataset is empty")
        
        # Check for required columns
        required_columns = ['date', 'country']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Log data quality metrics
        total_records = df.count()
        
        # Check completeness for critical columns
        completeness_report = {}
        for col_name in ['date', 'country', 'cases', 'deaths']:
            if col_name in df.columns:
                non_null_count = df.filter(col(col_name).isNotNull()).count()
                completeness = non_null_count / total_records
                completeness_report[col_name] = completeness
                
                if completeness < self.min_completeness_threshold:
                    logger.warning(
                        f"Column '{col_name}' completeness ({completeness:.2%}) "
                        f"below threshold ({self.min_completeness_threshold:.2%})"
                    )
        
        logger.info(f"Data completeness report: {completeness_report}")
        
        return df
    
    def clean_and_standardize(self, df: DataFrame) -> DataFrame:
        """
        Clean and standardize the data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            DataFrame: Cleaned DataFrame
        """
        logger.info("Starting data cleaning and standardization")
        
        # Remove completely null rows
        df_clean = df.dropna(how='all')
        
        # Standardize date formats
        if 'date' in df_clean.columns:
            df_clean = df_clean.withColumn(
                'date_standardized',
                coalesce(
                    to_date(col('date'), 'yyyy-MM-dd'),
                    to_date(col('date'), 'MM/dd/yyyy'),
                    to_date(col('date'), 'dd-MM-yyyy'),
                    to_date(col('date'), 'yyyy/MM/dd')
                )
            ).drop('date').withColumnRenamed('date_standardized', 'date')
        
        # Clean and standardize country names
        if 'country' in df_clean.columns:
            df_clean = df_clean.withColumn(
                'country',
                trim(regexp_replace(upper(col('country')), r'[^\w\s]', ''))
            )
        
        # Standardize numeric columns
        numeric_columns = ['cases', 'deaths', 'recovered', 'active', 'tests']
        for col_name in numeric_columns:
            if col_name in df_clean.columns:
                df_clean = df_clean.withColumn(
                    col_name,
                    when(col(col_name) < 0, 0)  # Replace negative values with 0
                    .otherwise(coalesce(col(col_name), lit(0)))  # Replace nulls with 0
                )
        
        # Remove duplicates based on key columns
        key_columns = ['date', 'country']
        before_dedup = df_clean.count()
        df_clean = df_clean.dropDuplicates(key_columns)
        after_dedup = df_clean.count()
        
        self.stats['duplicate_records'] = before_dedup - after_dedup
        if self.stats['duplicate_records'] > 0:
            logger.info(f"Removed {self.stats['duplicate_records']} duplicate records")
        
        logger.info(f"Data cleaning completed. Records: {before_dedup} -> {after_dedup}")
        
        return df_clean
    
    def apply_business_transformations(self, df: DataFrame) -> DataFrame:
        """
        Apply business logic and create calculated fields
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            DataFrame: Transformed DataFrame
        """
        logger.info("Applying business transformations")
        
        # Add date components for partitioning
        df_transformed = df.withColumn('year', year(col('date'))) \
                          .withColumn('month', month(col('date'))) \
                          .withColumn('day', dayofmonth(col('date'))) \
                          .withColumn('quarter', quarter(col('date'))) \
                          .withColumn('week_of_year', weekofyear(col('date')))
        
        # Calculate rates and percentages
        df_transformed = df_transformed.withColumn(
            'case_fatality_rate',
            when(col('cases') > 0, round(col('deaths') / col('cases') * 100, 4))
            .otherwise(0)
        )
        
        if 'recovered' in df_transformed.columns:
            df_transformed = df_transformed.withColumn(
                'recovery_rate',
                when(col('cases') > 0, round(col('recovered') / col('cases') * 100, 4))
                .otherwise(0)
            )
        
        if 'active' in df_transformed.columns:
            df_transformed = df_transformed.withColumn(
                'active_rate',
                when(col('cases') > 0, round(col('active') / col('cases') * 100, 4))
                .otherwise(0)
            )
        
        # Add growth rates (day-over-day change)
        window_spec = Window.partitionBy('country').orderBy('date')
        
        if 'cases' in df_transformed.columns:
            df_transformed = df_transformed.withColumn(
                'cases_growth_rate',
                round(
                    (col('cases') - lag('cases', 1).over(window_spec)) / 
                    coalesce(lag('cases', 1).over(window_spec), lit(1)) * 100, 4
                )
            )
        
        # Add moving averages (7-day)
        window_7_days = Window.partitionBy('country').orderBy('date').rowsBetween(-6, 0)
        
        for col_name in ['cases', 'deaths']:
            if col_name in df_transformed.columns:
                df_transformed = df_transformed.withColumn(
                    f'{col_name}_7day_avg',
                    round(avg(col(col_name)).over(window_7_days), 2)
                )
        
        # Add data quality indicators
        df_transformed = df_transformed.withColumn(
            'data_quality_score',
            when(col('date').isNull(), 0.0)
            .when(col('country').isNull(), 0.0)
            .when(col('cases') < 0, 0.5)
            .when(col('deaths') > col('cases'), 0.5)
            .otherwise(1.0)
        )
        
        # Add processing metadata
        df_transformed = df_transformed.withColumn(
            'processed_at', 
            lit(datetime.now(timezone.utc).isoformat())
        ).withColumn(
            'processing_job_id',
            lit(self.job_args.get('JOB_RUN_ID', 'unknown'))
        )
        
        logger.info("Business transformations completed")
        
        return df_transformed
    
    def validate_output_data(self, df: DataFrame) -> DataFrame:
        """
        Validate transformed data quality
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            DataFrame: Validated DataFrame
        """
        logger.info("Validating output data quality")
        
        total_records = df.count()
        
        # Check data quality scores
        low_quality_records = df.filter(col('data_quality_score') < 1.0).count()
        quality_rate = (total_records - low_quality_records) / total_records
        
        logger.info(f"Data quality rate: {quality_rate:.2%}")
        
        if quality_rate < (1 - self.max_error_rate):
            logger.warning(
                f"Data quality rate ({quality_rate:.2%}) below threshold "
                f"({1 - self.max_error_rate:.2%})"
            )
        
        # Check for logical inconsistencies
        inconsistent_records = df.filter(
            (col('deaths') > col('cases')) |
            (col('recovered') > col('cases')) |
            (col('case_fatality_rate') > 100)
        ).count()
        
        if inconsistent_records > 0:
            inconsistency_rate = inconsistent_records / total_records
            logger.warning(
                f"Found {inconsistent_records} inconsistent records "
                f"({inconsistency_rate:.2%} of total)"
            )
            
            if inconsistency_rate > self.max_error_rate:
                raise ValueError(f"Data inconsistency rate too high: {inconsistency_rate:.2%}")
        
        # Update statistics
        self.stats['output_records'] = total_records
        self.stats['invalid_records'] = low_quality_records
        
        return df
    
    def write_output_data(self, df: DataFrame):
        """
        Write transformed data to S3 in partitioned Parquet format
        
        Args:
            df: Transformed DataFrame
        """
        logger.info(f"Writing output data to: {self.output_path}")
        
        try:
            # Write partitioned data
            df.write \
              .mode("overwrite") \
              .option("compression", "snappy") \
              .option("maxRecordsPerFile", 100000) \
              .partitionBy(*self.partition_keys) \
              .parquet(self.output_path)
            
            logger.info("Successfully wrote partitioned data to S3")
            
            # Update Glue Data Catalog
            self.update_glue_catalog(df)
            
        except Exception as e:
            logger.error(f"Failed to write output data: {str(e)}")
            raise
    
    def update_glue_catalog(self, df: DataFrame):
        """
        Update AWS Glue Data Catalog with latest schema
        
        Args:
            df: DataFrame with current schema
        """
        logger.info("Updating Glue Data Catalog")
        
        try:
            # Create DynamicFrame from DataFrame
            dynamic_frame = DynamicFrame.fromDF(df, glueContext, "covid_data")
            
            # Write to Glue Catalog
            glueContext.write_dynamic_frame.from_catalog(
                frame=dynamic_frame,
                database=self.database_name,
                table_name=self.table_name,
                transformation_ctx="update_catalog"
            )
            
            logger.info("Successfully updated Glue Data Catalog")
            
        except Exception as e:
            logger.warning(f"Failed to update Glue Data Catalog: {str(e)}")
            # Don't fail the job if catalog update fails
    
    def generate_statistics_report(self) -> Dict:
        """
        Generate processing statistics and data quality report
        
        Returns:
            Dict: Processing statistics
        """
        self.stats['processing_end_time'] = datetime.now(timezone.utc)
        processing_duration = (
            self.stats['processing_end_time'] - 
            self.stats['processing_start_time']
        ).total_seconds()
        
        self.stats['processing_duration_seconds'] = processing_duration
        self.stats['records_per_second'] = (
            self.stats['output_records'] / processing_duration 
            if processing_duration > 0 else 0
        )
        
        # Calculate data quality metrics
        if self.stats['input_records'] > 0:
            self.stats['data_retention_rate'] = (
                self.stats['output_records'] / self.stats['input_records']
            )
            self.stats['error_rate'] = (
                self.stats['invalid_records'] / self.stats['input_records']
            )
        
        logger.info("Processing Statistics:")
        for key, value in self.stats.items():
            logger.info(f"  {key}: {value}")
        
        return self.stats
    
    def run_etl_pipeline(self):
        """
        Execute the complete ETL pipeline
        """
        logger.info("Starting COVID-19 ETL pipeline execution")
        
        try:
            # Step 1: Read source data
            raw_df = self.read_source_data()
            
            # Step 2: Validate source data
            validated_df = self.validate_source_data(raw_df)
            
            # Step 3: Clean and standardize
            cleaned_df = self.clean_and_standardize(validated_df)
            
            # Step 4: Apply business transformations
            transformed_df = self.apply_business_transformations(cleaned_df)
            
            # Step 5: Validate output data
            final_df = self.validate_output_data(transformed_df)
            
            # Step 6: Write output data
            self.write_output_data(final_df)
            
            # Step 7: Generate report
            stats = self.generate_statistics_report()
            
            logger.info("COVID-19 ETL pipeline completed successfully!")
            
            return stats
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}")
            raise


def main():
    """Main entry point for the Glue job"""
    
    # Get job parameters
    args = getResolvedOptions(sys.argv, [
        'JOB_NAME',
        'input_s3_path',
        'output_s3_path',
        'database_name',
        'table_name',
        'partition_keys',
        'min_completeness',
        'max_error_rate'
    ])
    
    # Initialize Glue job
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)
    
    try:
        # Initialize and run ETL pipeline
        etl = CovidDataETL(args)
        stats = etl.run_etl_pipeline()
        
        # Commit job on success
        job.commit()
        
        logger.info("Glue job completed successfully")
        
    except Exception as e:
        logger.error(f"Glue job failed: {str(e)}")
        # Don't commit on failure
        raise


if __name__ == "__main__":
    main()