"""
Azure to AWS Migration Module

Migrates data from Azure Data Lake Storage (ADLS) to AWS S3.

Features:
- ADLS to S3 data transfer
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
from azure.storage.filedatalake import FileSystemClient
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


class AzureToAWSMigration:
    """
    Migrate data from Azure ADLS to AWS S3
    
    Supports:
    - Direct file transfer
    - Spark-based data migration with transformations
    - Schema preservation
    - Metadata migration
    - Progress tracking
    """
    
    def __init__(
        self,
        checkpoint_dir: str = '/tmp/azure_aws_migration_checkpoints',
        max_workers: int = 10,
        chunk_size: int = 100 * 1024 * 1024  # 100MB chunks
    ):
        """
        Initialize Azure to AWS migration
        
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
        self.azure_client = connections.get_azure_client()
        self.s3_client = connections.get_s3_client()
        
        logger.info("Initialized Azure to AWS migration")
    
    def migrate_data(
        self,
        adls_path: str,
        s3_path: str,
        file_format: str = 'parquet',
        partition_cols: Optional[List[str]] = None,
        transformation_func: Optional[callable] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Migrate data from ADLS to S3 using Spark
        
        Args:
            adls_path: Source ADLS path (abfss://container@account/path)
            s3_path: Target S3 path (s3://bucket/key)
            file_format: File format ('parquet', 'delta', 'csv', 'json')
            partition_cols: Columns to partition by
            transformation_func: Optional transformation function to apply to DataFrame
            job_id: Job ID for tracking
            
        Returns:
            Migration statistics
        """
        logger.info(f"Starting Azure to AWS migration")
        logger.info(f"Source: {adls_path}")
        logger.info(f"Target: {s3_path}")
        
        # Validate paths
        if not validate_adls_path(adls_path):
            raise ValueError(f"Invalid ADLS path: {adls_path}")
        if not validate_s3_path(s3_path):
            raise ValueError(f"Invalid S3 path: {s3_path}")
        
        job_id = job_id or f"azure_aws_{get_timestamp()}"
        start_time = datetime.now()
        
        try:
            # Read from ADLS
            logger.info(f"Reading data from ADLS: {adls_path}")
            df = self._read_adls_data(adls_path, file_format)
            
            record_count = df.count()
            logger.info(f"Total records: {record_count:,}")
            
            # Apply transformation if provided
            if transformation_func:
                logger.info("Applying transformation")
                df = transformation_func(df)
                record_count = df.count()
                logger.info(f"Records after transformation: {record_count:,}")
            
            # Save schema
            schema_path = f"{s3_path}/_schema.json"
            self._save_schema_to_s3(df.schema, schema_path)
            
            # Write to S3
            logger.info(f"Writing data to S3: {s3_path}")
            self._write_s3_data(df, s3_path, file_format, partition_cols)
            
            # Copy metadata
            metadata = self._extract_adls_metadata(adls_path)
            self._save_metadata_to_s3(metadata, f"{s3_path}/_metadata.json")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'job_id': job_id,
                'status': 'completed',
                'records_migrated': record_count,
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'source_path': adls_path,
                'target_path': s3_path,
                'schema_path': schema_path
            }
            
            logger.info(f"Migration completed: {record_count:,} records in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            raise
    
    def migrate_files_direct(
        self,
        adls_container: str,
        adls_path: str,
        s3_bucket: str,
        s3_prefix: str,
        file_pattern: str = '*',
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Direct file transfer from ADLS to S3 (no Spark processing)
        
        Args:
            adls_container: ADLS container name
            adls_path: Path within container
            s3_bucket: Target S3 bucket
            s3_prefix: Target S3 prefix/path
            file_pattern: File pattern to match (e.g., '*.parquet')
            parallel: Whether to transfer files in parallel
            
        Returns:
            Transfer statistics
        """
        logger.info(f"Starting direct file transfer from ADLS to S3")
        logger.info(f"Source: {adls_container}/{adls_path}")
        logger.info(f"Target: s3://{s3_bucket}/{s3_prefix}")
        
        start_time = datetime.now()
        
        try:
            # Get file system client
            file_system_client = self.azure_client.get_file_system_client(adls_container)
            
            # List files
            logger.info(f"Listing files matching pattern: {file_pattern}")
            files = self._list_adls_files(file_system_client, adls_path, file_pattern)
            
            logger.info(f"Found {len(files)} files to transfer")
            
            transferred = 0
            failed = []
            total_bytes = 0
            
            if parallel and len(files) > 1:
                # Parallel transfer
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {}
                    
                    for file_path in files:
                        future = executor.submit(
                            self._transfer_file,
                            file_system_client,
                            file_path,
                            s3_bucket,
                            s3_prefix
                        )
                        futures[future] = file_path
                    
                    for future in as_completed(futures):
                        file_path = futures[future]
                        try:
                            bytes_transferred = future.result()
                            transferred += 1
                            total_bytes += bytes_transferred
                            logger.info(f"Transferred: {file_path} ({bytes_to_human_readable(bytes_transferred)})")
                        except Exception as e:
                            logger.error(f"Failed to transfer {file_path}: {str(e)}")
                            failed.append(file_path)
            else:
                # Sequential transfer
                for file_path in files:
                    try:
                        bytes_transferred = self._transfer_file(
                            file_system_client,
                            file_path,
                            s3_bucket,
                            s3_prefix
                        )
                        transferred += 1
                        total_bytes += bytes_transferred
                        logger.info(f"Transferred: {file_path} ({bytes_to_human_readable(bytes_transferred)})")
                    except Exception as e:
                        logger.error(f"Failed to transfer {file_path}: {str(e)}")
                        failed.append(file_path)
            
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
    
    def migrate_container(
        self,
        adls_container: str,
        s3_bucket: str,
        prefix_mapping: Optional[Dict[str, str]] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate entire ADLS container to S3 bucket
        
        Args:
            adls_container: Source ADLS container
            s3_bucket: Target S3 bucket
            prefix_mapping: Optional mapping of ADLS paths to S3 prefixes
            parallel: Whether to transfer in parallel
            
        Returns:
            Migration statistics
        """
        logger.info(f"Migrating container {adls_container} to bucket {s3_bucket}")
        
        start_time = datetime.now()
        
        try:
            file_system_client = self.azure_client.get_file_system_client(adls_container)
            
            # List all files in container
            all_files = self._list_adls_files(file_system_client, '', '*')
            logger.info(f"Found {len(all_files)} files in container")
            
            transferred = 0
            failed = []
            total_bytes = 0
            
            if parallel:
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = {}
                    
                    for file_path in all_files:
                        # Apply prefix mapping if provided
                        s3_key = self._apply_prefix_mapping(file_path, prefix_mapping)
                        
                        future = executor.submit(
                            self._transfer_file,
                            file_system_client,
                            file_path,
                            s3_bucket,
                            s3_key
                        )
                        futures[future] = file_path
                    
                    for future in as_completed(futures):
                        file_path = futures[future]
                        try:
                            bytes_transferred = future.result()
                            transferred += 1
                            total_bytes += bytes_transferred
                            
                            if transferred % 100 == 0:
                                logger.info(f"Progress: {transferred}/{len(all_files)} files")
                        except Exception as e:
                            logger.error(f"Failed to transfer {file_path}: {str(e)}")
                            failed.append(file_path)
            else:
                for i, file_path in enumerate(all_files):
                    try:
                        s3_key = self._apply_prefix_mapping(file_path, prefix_mapping)
                        bytes_transferred = self._transfer_file(
                            file_system_client,
                            file_path,
                            s3_bucket,
                            s3_key
                        )
                        transferred += 1
                        total_bytes += bytes_transferred
                        
                        if (i + 1) % 100 == 0:
                            logger.info(f"Progress: {i + 1}/{len(all_files)} files")
                    except Exception as e:
                        logger.error(f"Failed to transfer {file_path}: {str(e)}")
                        failed.append(file_path)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'status': 'completed',
                'container': adls_container,
                'bucket': s3_bucket,
                'files_transferred': transferred,
                'files_failed': len(failed),
                'failed_files': failed,
                'total_bytes': total_bytes,
                'duration_seconds': duration
            }
            
            logger.info(f"Container migration completed: {transferred} files in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Container migration failed: {str(e)}", exc_info=True)
            raise
    
    def _read_adls_data(self, adls_path: str, file_format: str) -> DataFrame:
        """Read data from ADLS using Spark"""
        if file_format == 'parquet':
            return self.spark.read.parquet(adls_path)
        elif file_format == 'delta':
            return self.spark.read.format('delta').load(adls_path)
        elif file_format == 'csv':
            return self.spark.read.option('header', 'true').option('inferSchema', 'true').csv(adls_path)
        elif file_format == 'json':
            return self.spark.read.json(adls_path)
        else:
            return self.spark.read.load(adls_path)
    
    def _write_s3_data(
        self,
        df: DataFrame,
        s3_path: str,
        file_format: str,
        partition_cols: Optional[List[str]] = None
    ) -> None:
        """Write data to S3 using Spark"""
        writer = df.write.mode('overwrite')
        
        if partition_cols:
            writer = writer.partitionBy(*partition_cols)
        
        if file_format == 'parquet':
            writer.option('compression', 'snappy').parquet(s3_path)
        elif file_format == 'delta':
            writer.format('delta').save(s3_path)
        elif file_format == 'csv':
            writer.option('header', 'true').csv(s3_path)
        elif file_format == 'json':
            writer.json(s3_path)
    
    def _list_adls_files(
        self,
        file_system_client: FileSystemClient,
        path: str,
        pattern: str
    ) -> List[str]:
        """List files in ADLS matching pattern"""
        import fnmatch
        
        files = []
        paths = file_system_client.get_paths(path=path)
        
        for item in paths:
            if not item.is_directory and fnmatch.fnmatch(item.name, f"*{pattern}"):
                files.append(item.name)
        
        return files
    
    def _transfer_file(
        self,
        file_system_client: FileSystemClient,
        adls_file_path: str,
        s3_bucket: str,
        s3_key_prefix: str
    ) -> int:
        """Transfer a single file from ADLS to S3"""
        # Get file client
        file_client = file_system_client.get_file_client(adls_file_path)
        
        # Download file data
        download = file_client.download_file()
        file_data = download.readall()
        
        # Construct S3 key
        file_name = Path(adls_file_path).name
        s3_key = f"{s3_key_prefix}/{file_name}".lstrip('/')
        
        # Upload to S3
        self.s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=file_data
        )
        
        return len(file_data)
    
    def _apply_prefix_mapping(
        self,
        file_path: str,
        prefix_mapping: Optional[Dict[str, str]]
    ) -> str:
        """Apply prefix mapping to file path"""
        if not prefix_mapping:
            return file_path
        
        for adls_prefix, s3_prefix in prefix_mapping.items():
            if file_path.startswith(adls_prefix):
                return file_path.replace(adls_prefix, s3_prefix, 1)
        
        return file_path
    
    def _extract_adls_metadata(self, adls_path: str) -> Dict[str, Any]:
        """Extract metadata from ADLS path"""
        # This is a placeholder - actual implementation would extract
        # custom metadata, tags, etc. from ADLS
        return {
            'source_path': adls_path,
            'migration_timestamp': datetime.now().isoformat(),
            'platform': 'azure_adls'
        }
    
    def _save_schema_to_s3(self, schema, s3_path: str) -> None:
        """Save Spark schema to S3"""
        schema_dict = {
            'schema': json.loads(schema.json()),
            'saved_at': datetime.now().isoformat()
        }
        
        schema_json = json.dumps(schema_dict, indent=2)
        
        bucket, key = self._parse_s3_path(s3_path)
        self.s3_client.put_object(Bucket=bucket, Key=key, Body=schema_json)
        
        logger.info(f"Schema saved to {s3_path}")
    
    def _save_metadata_to_s3(self, metadata: Dict[str, Any], s3_path: str) -> None:
        """Save metadata to S3"""
        metadata_json = json.dumps(metadata, indent=2)
        
        bucket, key = self._parse_s3_path(s3_path)
        self.s3_client.put_object(Bucket=bucket, Key=key, Body=metadata_json)
        
        logger.info(f"Metadata saved to {s3_path}")
    
    def _parse_s3_path(self, s3_path: str) -> tuple:
        """Parse S3 path into bucket and key"""
        path = s3_path.replace('s3://', '').replace('s3a://', '')
        parts = path.split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        return bucket, key
