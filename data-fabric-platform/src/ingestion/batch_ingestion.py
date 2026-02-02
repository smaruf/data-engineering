"""
Batch data ingestion module

Handles batch ingestion from various sources:
- CSV files
- JSON files
- Parquet files
- Database tables
- Cloud storage (S3, ADLS, HDFS)
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from pyspark.sql import DataFrame
from shared.utils.connection_manager import connections
from shared.utils.logger import get_logger
from shared.utils.helpers import get_platform_from_path, ensure_dir

logger = get_logger(__name__)


class BatchIngestion:
    """Batch data ingestion handler"""
    
    def __init__(self, spark_session=None):
        """
        Initialize batch ingestion
        
        Args:
            spark_session: Optional Spark session (uses global if not provided)
        """
        self.spark = spark_session or connections.spark
    
    def ingest_csv(
        self,
        source_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Ingest CSV file(s)
        
        Args:
            source_path: Path to CSV file or directory
            options: Reader options (header, delimiter, etc.)
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Ingesting CSV from: {source_path}")
        
        default_options = {
            'header': True,
            'inferSchema': True,
            'mode': 'PERMISSIVE'
        }
        
        if options:
            default_options.update(options)
        
        df = self.spark.read.options(**default_options).csv(source_path)
        
        logger.info(f"Ingested {df.count()} rows from CSV")
        return df
    
    def ingest_json(
        self,
        source_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Ingest JSON file(s)
        
        Args:
            source_path: Path to JSON file or directory
            options: Reader options
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Ingesting JSON from: {source_path}")
        
        default_options = {
            'multiLine': True,
            'mode': 'PERMISSIVE'
        }
        
        if options:
            default_options.update(options)
        
        df = self.spark.read.options(**default_options).json(source_path)
        
        logger.info(f"Ingested {df.count()} rows from JSON")
        return df
    
    def ingest_parquet(
        self,
        source_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Ingest Parquet file(s)
        
        Args:
            source_path: Path to Parquet file or directory
            options: Reader options
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Ingesting Parquet from: {source_path}")
        
        default_options = options or {}
        df = self.spark.read.options(**default_options).parquet(source_path)
        
        logger.info(f"Ingested {df.count()} rows from Parquet")
        return df
    
    def ingest_delta(
        self,
        source_path: str,
        version: Optional[int] = None,
        timestamp: Optional[str] = None
    ) -> DataFrame:
        """
        Ingest Delta Lake table
        
        Args:
            source_path: Path to Delta table
            version: Specific version to read (time travel)
            timestamp: Specific timestamp to read (time travel)
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Ingesting Delta table from: {source_path}")
        
        reader = self.spark.read.format("delta")
        
        if version is not None:
            reader = reader.option("versionAsOf", version)
        elif timestamp is not None:
            reader = reader.option("timestampAsOf", timestamp)
        
        df = reader.load(source_path)
        
        logger.info(f"Ingested {df.count()} rows from Delta table")
        return df
    
    def ingest_from_database(
        self,
        connection_string: str,
        table_name: str,
        query: Optional[str] = None
    ) -> DataFrame:
        """
        Ingest data from JDBC database
        
        Args:
            connection_string: JDBC connection string
            table_name: Table to read
            query: Optional SQL query (overrides table_name)
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Ingesting from database table: {table_name}")
        
        if query:
            df = self.spark.read.format("jdbc") \
                .option("url", connection_string) \
                .option("query", query) \
                .load()
        else:
            df = self.spark.read.format("jdbc") \
                .option("url", connection_string) \
                .option("dbtable", table_name) \
                .load()
        
        logger.info(f"Ingested {df.count()} rows from database")
        return df
    
    def ingest_from_s3(
        self,
        bucket: str,
        key: str,
        file_format: str = 'parquet',
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Ingest data from AWS S3
        
        Args:
            bucket: S3 bucket name
            key: S3 object key/prefix
            file_format: File format (csv, json, parquet)
            options: Reader options
            
        Returns:
            Spark DataFrame
        """
        s3_path = f"s3a://{bucket}/{key}"
        logger.info(f"Ingesting from S3: {s3_path}")
        
        if file_format == 'csv':
            return self.ingest_csv(s3_path, options)
        elif file_format == 'json':
            return self.ingest_json(s3_path, options)
        elif file_format == 'parquet':
            return self.ingest_parquet(s3_path, options)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    def ingest_from_adls(
        self,
        container: str,
        path: str,
        storage_account: str,
        file_format: str = 'parquet',
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Ingest data from Azure Data Lake Storage
        
        Args:
            container: ADLS container name
            path: Path within container
            storage_account: Storage account name
            file_format: File format (csv, json, parquet)
            options: Reader options
            
        Returns:
            Spark DataFrame
        """
        adls_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/{path}"
        logger.info(f"Ingesting from ADLS: {adls_path}")
        
        if file_format == 'csv':
            return self.ingest_csv(adls_path, options)
        elif file_format == 'json':
            return self.ingest_json(adls_path, options)
        elif file_format == 'parquet':
            return self.ingest_parquet(adls_path, options)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    def ingest_from_hdfs(
        self,
        hdfs_path: str,
        file_format: str = 'parquet',
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Ingest data from HDFS
        
        Args:
            hdfs_path: HDFS path (e.g., hdfs://namenode:9000/path)
            file_format: File format (csv, json, parquet)
            options: Reader options
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Ingesting from HDFS: {hdfs_path}")
        
        if file_format == 'csv':
            return self.ingest_csv(hdfs_path, options)
        elif file_format == 'json':
            return self.ingest_json(hdfs_path, options)
        elif file_format == 'parquet':
            return self.ingest_parquet(hdfs_path, options)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    def auto_ingest(
        self,
        source_path: str,
        file_format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """
        Auto-detect and ingest data from path
        
        Args:
            source_path: Source path (local, S3, ADLS, HDFS)
            file_format: File format (auto-detected if not provided)
            options: Reader options
            
        Returns:
            Spark DataFrame
        """
        logger.info(f"Auto-ingesting from: {source_path}")
        
        # Detect format if not provided
        if not file_format:
            if source_path.endswith('.csv'):
                file_format = 'csv'
            elif source_path.endswith('.json'):
                file_format = 'json'
            elif source_path.endswith('.parquet') or 'parquet' in source_path:
                file_format = 'parquet'
            else:
                file_format = 'parquet'  # default
        
        # Ingest based on format
        if file_format == 'csv':
            return self.ingest_csv(source_path, options)
        elif file_format == 'json':
            return self.ingest_json(source_path, options)
        elif file_format == 'parquet':
            return self.ingest_parquet(source_path, options)
        elif file_format == 'delta':
            return self.ingest_delta(source_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
