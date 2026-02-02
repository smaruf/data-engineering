"""
AWS to Azure Migration Module

Migrates data from AWS S3 to Azure Data Lake Storage (ADLS).

Features:
- S3 to ADLS data transfer
- Schema mapping and preservation
- Metadata preservation
- Progress tracking
- Parallel transfers
- Support for Delta Lake and Parquet formats
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyspark.sql import DataFrame
from azure.storage.filedatalake import DataLakeFileClient
import boto3

from shared.utils.config_loader import config
from shared.utils.logger import get_logger
from shared.utils.connection_manager import connections
from shared.utils.helpers import (
    get_timestamp,
    bytes_to_human_readable,
    validate_s3_path,
    validate_adls_path
)

logger = get_logger(__name__)


class AWSToAzureMigration:
    """
    Migrate data from AWS S3 to Azure ADLS
    
    Supports:
    - Direct file transfer
    - Spark-based data migration with transformations
    - Schema preservation
    - Metadata migration
    - Progress tracking
    """
    
    def __init__(
        self,
        checkpoint_dir: str = '/tmp/aws_azure_migration_checkpoints',
        max_workers: int = 10,
        chunk_size: int = 100 * 1024 * 1024  # 100MB chunks
    ):
        """
        Initialize AWS to Azure migration
        
        Args:
            checkpoint_dir: Directory for storing checkpoints
            max_workers: Maximum parallel workers
            chunk_size: Chunk size for streaming transfers
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        
        self.spark = connections.spark
        self.s3_client = connections.get_s3_client()
        self.azure_client = connections.get_azure_client()
        
        logger.info("Initialized AWS to Azure migration")
    
    def migrate_data(
        self,
        s3_path: str,
        adls_path: str,
        file_format: str = 'parquet',
        partition_cols: Optional[List[str]] = None,
        transformation_func: Optional[callable] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Migrate data from S3 to ADLS using Spark
        
        Args:
            s3_path: Source S3 path (s3://bucket/key)
            adls_path: Target ADLS path (abfss://container@account/path)
            file_format: File format ('parquet', 'delta', 'csv', 'json')
            partition_cols: Columns to partition by
            transformation_func: Optional transformation function to apply to DataFrame
            job_id: Job ID for tracking
            
        Returns:
            Migration statistics
        """
        logger.info(f"Starting AWS to Azure migration")
        logger.info(f"Source: {s3_path}")
        logger.info(f"Target: {adls_path}")
        
        # Validate paths
        if not validate_s3_path(s3_path):
            raise ValueError(f"Invalid S3 path: {s3_path}")
        if not validate_adls_path(adls_path):
            raise ValueError(f"Invalid ADLS path: {adls_path}")
        
        job_id = job_id or f"aws_azure_{get_timestamp()}"
        start_time = datetime.now()
        
        try:
            # Read from S3
            logger.info(f"Reading data from S3: {s3_path}")
            df = self._read_s3_data(s3_path, file_format)
            
            record_count = df.count()
            logger.info(f"Total records: {record_count:,}")
            
            # Apply transformation if provided
            if transformation_func:
                logger.info("Applying transformation")
                df = transformation_func(df)
                record_count = df.count()
                logger.info(f"Records after transformation: {record_count:,}")
            
            # Save schema
            schema_path = f"{adls_path}/_schema.json"
            self._save_schema_to_adls(df.schema, schema_path)
            
            # Write to ADLS
            logger.info(f"Writing data to ADLS: {adls_path}")
            self._write_adls_data(df, adls_path, file_format, partition_cols)
            
            # Copy metadata
            metadata = self._extract_s3_metadata(s3_path)
            self._save_metadata_to_adls(metadata, f"{adls_path}/_metadata.json")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'job_id': job_id,
                'status': 'completed',
                'records_migrated': record_count,
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'source_path': s3_path,
                'target_path': adls_path,
                'schema_path': schema_path
            }
            
            logger.info(f"Migration completed: {record_count:,} records in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            raise
    
    def migrate_files_direct(
        self,
        s3_bucket: str,
        s3_prefix: str,
        adls_container: str,
        adls_path: str,
        file_pattern: str = '*',
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Direct file transfer from S3 to ADLS (no Spark processing)
        
        Args:
            s3_bucket: Source S3 bucket
            s3_prefix: S3 prefix/path
            adls_container: Target ADLS container name
            adls_path: Path within ADLS container
            file_pattern: File pattern to match (e.g., '*.parquet')
            parallel: Whether to transfer files in parallel
            
        Returns:
            Transfer statistics
        """
        logger.info(f"Starting direct file transfer from S3 to ADLS")
        logger.info(f"Source: s3://{s3_bucket}/{s3_prefix}")
        logger.info(f"Target: {adls_container}/{adls_path}")
        
        start_time = datetime.now()
        
        try:
            # List S3 files
            logger.info(f"Listing files matching pattern: {file_pattern}")
            files = self._list_s3_files(s3_bucket, s3_prefix, file_pattern)
            
            logger.info(f"Found {len(files)} files to transfer")
            
            transferred = 0
            failed = []
            total_bytes = 0
            
            # Get file system client
            file_system_client = self.azure_client.get_file_system_client(adls_container)
            
            if parallel and len(files) > 1:
                # Parallel transfer
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {}
                    
                    for s3_key in files:
                        future = executor.submit(
                            self._transfer_file,
                            s3_bucket,
                            s3_key,
                            file_system_client,
                            adls_path
                        )
                        futures[future] = s3_key
                    
                    for future in as_completed(futures):
                        s3_key = futures[future]
                        try:
                            bytes_transferred = future.result()
                            transferred += 1
                            total_bytes += bytes_transferred
                            logger.info(f"Transferred: {s3_key} ({bytes_to_human_readable(bytes_transferred)})")
                        except Exception as e:
                            logger.error(f"Failed to transfer {s3_key}: {str(e)}")
                            failed.append(s3_key)
            else:
                # Sequential transfer
                for s3_key in files:
                    try:
                        bytes_transferred = self._transfer_file(
                            s3_bucket,
                            s3_key,
                            file_system_client,
                            adls_path
                        )
                        transferred += 1
                        total_bytes += bytes_transferred
                        logger.info(f"Transferred: {s3_key} ({bytes_to_human_readable(bytes_transferred)})")
                    except Exception as e:
                        logger.error(f"Failed to transfer {s3_key}: {str(e)}")
                        failed.append(s3_key)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'status': 'completed',
                'files_transferred': transferred,
                'files_failed': len(failed),
                'failed_files': failed,
                'total_bytes': total_bytes,
                'total_bytes_readable': bytes_to_human_readable(total_bytes),
                'duration_seconds': duration,
                'throughput_mbps': (total_bytes / (1024 * 1024)) / duration if duration > 0 else 0
            }
            
            logger.info(f"Transfer completed: {transferred} files, {bytes_to_human_readable(total_bytes)} in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Direct transfer failed: {str(e)}", exc_info=True)
            raise
    
    def migrate_bucket(
        self,
        s3_bucket: str,
        adls_container: str,
        prefix_mapping: Optional[Dict[str, str]] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate entire S3 bucket to ADLS container
        
        Args:
            s3_bucket: Source S3 bucket
            adls_container: Target ADLS container
            prefix_mapping: Optional mapping of S3 prefixes to ADLS paths
            parallel: Whether to transfer in parallel
            
        Returns:
            Migration statistics
        """
        logger.info(f"Migrating bucket {s3_bucket} to container {adls_container}")
        
        start_time = datetime.now()
        
        try:
            # List all files in bucket
            all_files = self._list_s3_files(s3_bucket, '', '*')
            logger.info(f"Found {len(all_files)} files in bucket")
            
            transferred = 0
            failed = []
            total_bytes = 0
            
            file_system_client = self.azure_client.get_file_system_client(adls_container)
            
            if parallel:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {}
                    
                    for s3_key in all_files:
                        # Apply prefix mapping if provided
                        adls_file_path = self._apply_prefix_mapping(s3_key, prefix_mapping)
                        
                        future = executor.submit(
                            self._transfer_file,
                            s3_bucket,
                            s3_key,
                            file_system_client,
                            adls_file_path
                        )
                        futures[future] = s3_key
                    
                    for future in as_completed(futures):
                        s3_key = futures[future]
                        try:
                            bytes_transferred = future.result()
                            transferred += 1
                            total_bytes += bytes_transferred
                            
                            if transferred % 100 == 0:
                                logger.info(f"Progress: {transferred}/{len(all_files)} files")
                        except Exception as e:
                            logger.error(f"Failed to transfer {s3_key}: {str(e)}")
                            failed.append(s3_key)
            else:
                for i, s3_key in enumerate(all_files):
                    try:
                        adls_file_path = self._apply_prefix_mapping(s3_key, prefix_mapping)
                        bytes_transferred = self._transfer_file(
                            s3_bucket,
                            s3_key,
                            file_system_client,
                            adls_file_path
                        )
                        transferred += 1
                        total_bytes += bytes_transferred
                        
                        if (i + 1) % 100 == 0:
                            logger.info(f"Progress: {i + 1}/{len(all_files)} files")
                    except Exception as e:
                        logger.error(f"Failed to transfer {s3_key}: {str(e)}")
                        failed.append(s3_key)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'status': 'completed',
                'bucket': s3_bucket,
                'container': adls_container,
                'files_transferred': transferred,
                'files_failed': len(failed),
                'failed_files': failed,
                'total_bytes': total_bytes,
                'duration_seconds': duration
            }
            
            logger.info(f"Bucket migration completed: {transferred} files in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Bucket migration failed: {str(e)}", exc_info=True)
            raise
    
    def _read_s3_data(self, s3_path: str, file_format: str) -> DataFrame:
        """Read data from S3 using Spark"""
        if file_format == 'parquet':
            return self.spark.read.parquet(s3_path)
        elif file_format == 'delta':
            return self.spark.read.format('delta').load(s3_path)
        elif file_format == 'csv':
            return self.spark.read.option('header', 'true').option('inferSchema', 'true').csv(s3_path)
        elif file_format == 'json':
            return self.spark.read.json(s3_path)
        else:
            return self.spark.read.load(s3_path)
    
    def _write_adls_data(
        self,
        df: DataFrame,
        adls_path: str,
        file_format: str,
        partition_cols: Optional[List[str]] = None
    ) -> None:
        """Write data to ADLS using Spark"""
        writer = df.write.mode('overwrite')
        
        if partition_cols:
            writer = writer.partitionBy(*partition_cols)
        
        if file_format == 'parquet':
            writer.option('compression', 'snappy').parquet(adls_path)
        elif file_format == 'delta':
            writer.format('delta').save(adls_path)
        elif file_format == 'csv':
            writer.option('header', 'true').csv(adls_path)
        elif file_format == 'json':
            writer.json(adls_path)
    
    def _list_s3_files(self, bucket: str, prefix: str, pattern: str) -> List[str]:
        """List files in S3 matching pattern"""
        import fnmatch
        
        files = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    if fnmatch.fnmatch(key, f"*{pattern}"):
                        files.append(key)
        
        return files
    
    def _transfer_file(
        self,
        s3_bucket: str,
        s3_key: str,
        file_system_client,
        adls_base_path: str
    ) -> int:
        """Transfer a single file from S3 to ADLS"""
        # Download from S3
        response = self.s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        file_data = response['Body'].read()
        
        # Construct ADLS path
        file_name = Path(s3_key).name
        adls_file_path = f"{adls_base_path}/{file_name}".lstrip('/')
        
        # Upload to ADLS
        file_client = file_system_client.get_file_client(adls_file_path)
        file_client.upload_data(file_data, overwrite=True)
        
        return len(file_data)
    
    def _apply_prefix_mapping(
        self,
        s3_key: str,
        prefix_mapping: Optional[Dict[str, str]]
    ) -> str:
        """Apply prefix mapping to S3 key"""
        if not prefix_mapping:
            return s3_key
        
        for s3_prefix, adls_prefix in prefix_mapping.items():
            if s3_key.startswith(s3_prefix):
                return s3_key.replace(s3_prefix, adls_prefix, 1)
        
        return s3_key
    
    def _extract_s3_metadata(self, s3_path: str) -> Dict[str, Any]:
        """Extract metadata from S3 path"""
        bucket, key = self._parse_s3_path(s3_path)
        
        try:
            # Get object metadata
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            
            return {
                'source_path': s3_path,
                'migration_timestamp': datetime.now().isoformat(),
                'platform': 'aws_s3',
                's3_metadata': response.get('Metadata', {}),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified').isoformat() if response.get('LastModified') else None
            }
        except Exception as e:
            logger.warning(f"Failed to extract S3 metadata: {str(e)}")
            return {
                'source_path': s3_path,
                'migration_timestamp': datetime.now().isoformat(),
                'platform': 'aws_s3'
            }
    
    def _save_schema_to_adls(self, schema, adls_path: str) -> None:
        """Save Spark schema to ADLS"""
        schema_dict = {
            'schema': json.loads(schema.json()),
            'saved_at': datetime.now().isoformat()
        }
        
        schema_json = json.dumps(schema_dict, indent=2)
        
        container, path = self._parse_adls_path(adls_path)
        file_system_client = self.azure_client.get_file_system_client(container)
        file_client = file_system_client.get_file_client(path)
        file_client.upload_data(schema_json, overwrite=True)
        
        logger.info(f"Schema saved to {adls_path}")
    
    def _save_metadata_to_adls(self, metadata: Dict[str, Any], adls_path: str) -> None:
        """Save metadata to ADLS"""
        metadata_json = json.dumps(metadata, indent=2)
        
        container, path = self._parse_adls_path(adls_path)
        file_system_client = self.azure_client.get_file_system_client(container)
        file_client = file_system_client.get_file_client(path)
        file_client.upload_data(metadata_json, overwrite=True)
        
        logger.info(f"Metadata saved to {adls_path}")
    
    def _parse_s3_path(self, s3_path: str) -> tuple:
        """Parse S3 path into bucket and key"""
        path = s3_path.replace('s3://', '').replace('s3a://', '')
        parts = path.split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        return bucket, key
    
    def _parse_adls_path(self, adls_path: str) -> tuple:
        """Parse ADLS path into container and path"""
        # Format: abfss://container@account.dfs.core.windows.net/path
        path = adls_path.replace('abfss://', '').replace('abfs://', '')
        container = path.split('@')[0]
        file_path = path.split('/', 1)[1] if '/' in path else ''
        return container, file_path
