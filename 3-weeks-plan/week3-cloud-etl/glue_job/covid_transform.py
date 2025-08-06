"""
AWS Glue ETL Job for COVID-19 Data Transformation
==================================================

This PySpark script is designed to run as an AWS Glue job that:
1. Reads raw COVID-19 CSV data from S3
2. Cleans and transforms the data 
3. Writes the processed data to a partitioned S3 location

Author: Data Engineering Team
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Glue context and job
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'input_s3_path',
    'output_s3_path'
])

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

def read_covid_data(input_path: str) -> DataFrame:
    """
    Read raw COVID-19 CSV data from S3
    
    Args:
        input_path: S3 path to the raw CSV files
        
    Returns:
        DataFrame: Raw COVID-19 data
    """
    print(f"Reading COVID-19 data from: {input_path}")
    
    # Read CSV files from S3
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_path)
    
    print(f"Raw data count: {df.count()} rows")
    return df

def clean_and_transform_data(df: DataFrame) -> DataFrame:
    """
    Clean and transform the COVID-19 data
    
    Args:
        df: Raw COVID-19 DataFrame
        
    Returns:
        DataFrame: Cleaned and transformed data
    """
    print("Starting data cleaning and transformation...")
    
    # Remove rows with null values in critical columns
    df_cleaned = df.filter(
        col("date").isNotNull() & 
        col("country").isNotNull()
    )
    
    # Standardize date format
    df_cleaned = df_cleaned.withColumn(
        "date_formatted", 
        to_date(col("date"), "yyyy-MM-dd")
    )
    
    # Clean country names - remove extra whitespace and standardize case
    df_cleaned = df_cleaned.withColumn(
        "country_clean",
        trim(upper(col("country")))
    )
    
    # Add calculated fields
    df_transformed = df_cleaned \
        .withColumn("year", year(col("date_formatted"))) \
        .withColumn("month", month(col("date_formatted"))) \
        .withColumn("day", dayofmonth(col("date_formatted")))
    
    # Handle null values in numeric columns
    numeric_columns = ["cases", "deaths", "recovered"]
    for column in numeric_columns:
        if column in df_transformed.columns:
            df_transformed = df_transformed.fillna({column: 0})
    
    # Add data quality flags
    df_transformed = df_transformed.withColumn(
        "data_quality_score",
        when(col("cases") >= 0, 1.0).otherwise(0.0)
    )
    
    print(f"Cleaned data count: {df_transformed.count()} rows")
    return df_transformed

def write_partitioned_data(df: DataFrame, output_path: str):
    """
    Write transformed data to partitioned S3 location
    
    Args:
        df: Transformed DataFrame
        output_path: S3 output path for partitioned data
    """
    print(f"Writing partitioned data to: {output_path}")
    
    # Write data partitioned by year and month for efficient querying
    df.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .option("compression", "snappy") \
        .parquet(output_path)
    
    print("Data successfully written to S3")

def main():
    """
    Main ETL pipeline execution
    """
    try:
        # Step 1: Read raw data from S3
        raw_df = read_covid_data(args['input_s3_path'])
        
        # Step 2: Clean and transform the data
        transformed_df = clean_and_transform_data(raw_df)
        
        # Step 3: Write processed data to partitioned S3 location
        write_partitioned_data(transformed_df, args['output_s3_path'])
        
        print("ETL job completed successfully!")
        
    except Exception as e:
        print(f"ETL job failed with error: {str(e)}")
        raise e

if __name__ == "__main__":
    main()
    job.commit()