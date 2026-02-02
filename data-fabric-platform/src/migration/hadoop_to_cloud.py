"""
Hadoop to Cloud Migration Module

Migrates data from on-premise Hadoop (HDFS/Hive) to cloud platforms (AWS S3 or Azure ADLS).

Features:
- HDFS to S3/ADLS migration
- Hive table migration with schema preservation
- Incremental and full sync modes
- Checkpointing for resume capability
- Parallel processing for large datasets
- Support for Delta Lake and Parquet formats
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.utils import AnalysisException

from shared.utils.config_loader import config
from shared.utils.logger import get_logger
from shared.utils.connection_manager import connections
from shared.utils.helpers import (
    get_timestamp, 
    bytes_to_human_readable,
    validate_s3_path,
    validate_adls_path,
    validate_hdfs_path
)

logger = get_logger(__name__)


@dataclass
class MigrationCheckpoint:
    """Checkpoint data for migration resume"""
    job_id: str
    source_path: str
    target_path: str
    total_files: int
    completed_files: int
    failed_files: List[str]
    start_time: str
    last_updated: str
    status: str  # 'running', 'completed', 'failed', 'paused'
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MigrationCheckpoint':
        return cls(**data)


class HadoopToCloudMigration:
    """
    Migrate data from Hadoop (HDFS/Hive) to cloud platforms (S3/ADLS)
    
    Supports:
    - Full and incremental migrations
    - Schema preservation
    - Checkpointing for resume
    - Parallel processing
    - Multiple file formats (Delta, Parquet, CSV, JSON)
    """
    
    def __init__(
        self,
        target_platform: str = 's3',
        checkpoint_dir: str = '/tmp/migration_checkpoints',
        max_workers: int = 10,
        batch_size: int = 1000
    ):
        """
        Initialize Hadoop to Cloud migration
        
        Args:
            target_platform: Target cloud platform ('s3' or 'adls')
            checkpoint_dir: Directory for storing checkpoints
            max_workers: Max parallel workers for file operations
            batch_size: Batch size for processing files
        """
        self.target_platform = target_platform.lower()
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        self.spark = connections.spark
        
        if self.target_platform == 's3':
            self.s3_client = connections.get_s3_client()
        elif self.target_platform == 'adls':
            self.azure_client = connections.get_azure_client()
        else:
            raise ValueError(f"Unsupported target platform: {target_platform}")
        
        logger.info(f"Initialized migration to {target_platform}")
    
    def migrate_hdfs_to_cloud(
        self,
        hdfs_path: str,
        cloud_path: str,
        sync_mode: str = 'full',
        file_format: str = 'parquet',
        compression: Optional[str] = 'snappy',
        partition_cols: Optional[List[str]] = None,
        job_id: Optional[str] = None,
        resume: bool = False
    ) -> Dict[str, Any]:
        """
        Migrate data from HDFS to cloud storage
        
        Args:
            hdfs_path: Source HDFS path (e.g., hdfs://namenode:9000/data)
            cloud_path: Target cloud path (e.g., s3://bucket/data or abfss://container@account/data)
            sync_mode: Migration mode ('full' or 'incremental')
            file_format: Output format ('parquet', 'delta', 'csv', 'json')
            compression: Compression codec (None, 'snappy', 'gzip', 'lz4')
            partition_cols: Columns to partition by
            job_id: Job ID for tracking (auto-generated if None)
            resume: Resume from checkpoint if available
            
        Returns:
            Migration statistics
        """
        logger.info(f"Starting HDFS to {self.target_platform} migration")
        logger.info(f"Source: {hdfs_path}")
        logger.info(f"Target: {cloud_path}")
        logger.info(f"Mode: {sync_mode}, Format: {file_format}")
        
        # Validate paths
        if not validate_hdfs_path(hdfs_path):
            raise ValueError(f"Invalid HDFS path: {hdfs_path}")
        
        if self.target_platform == 's3' and not validate_s3_path(cloud_path):
            raise ValueError(f"Invalid S3 path: {cloud_path}")
        elif self.target_platform == 'adls' and not validate_adls_path(cloud_path):
            raise ValueError(f"Invalid ADLS path: {cloud_path}")
        
        # Generate or load job ID
        job_id = job_id or f"hdfs_migration_{get_timestamp()}"
        
        # Check for existing checkpoint
        checkpoint = None
        if resume:
            checkpoint = self._load_checkpoint(job_id)
            if checkpoint:
                logger.info(f"Resuming migration from checkpoint: {checkpoint.completed_files}/{checkpoint.total_files} files")
        
        start_time = datetime.now()
        
        try:
            # Read data from HDFS
            logger.info(f"Reading data from HDFS: {hdfs_path}")
            df = self._read_hdfs_data(hdfs_path, file_format)
            
            if df is None:
                raise ValueError(f"Failed to read data from {hdfs_path}")
            
            # Get record count
            record_count = df.count()
            logger.info(f"Total records to migrate: {record_count:,}")
            
            # Apply incremental filter if needed
            if sync_mode == 'incremental' and checkpoint:
                df = self._apply_incremental_filter(df, checkpoint)
                record_count = df.count()
                logger.info(f"Incremental records to migrate: {record_count:,}")
            
            # Write data to cloud
            logger.info(f"Writing data to {self.target_platform}: {cloud_path}")
            write_stats = self._write_cloud_data(
                df, 
                cloud_path, 
                file_format, 
                compression,
                partition_cols
            )
            
            # Create completion checkpoint
            checkpoint = MigrationCheckpoint(
                job_id=job_id,
                source_path=hdfs_path,
                target_path=cloud_path,
                total_files=write_stats.get('files_written', 0),
                completed_files=write_stats.get('files_written', 0),
                failed_files=[],
                start_time=start_time.isoformat(),
                last_updated=datetime.now().isoformat(),
                status='completed',
                metadata={
                    'record_count': record_count,
                    'file_format': file_format,
                    'compression': compression,
                    'sync_mode': sync_mode
                }
            )
            self._save_checkpoint(checkpoint)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'job_id': job_id,
                'status': 'completed',
                'records_migrated': record_count,
                'files_written': write_stats.get('files_written', 0),
                'bytes_written': write_stats.get('bytes_written', 0),
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'source_path': hdfs_path,
                'target_path': cloud_path
            }
            
            logger.info(f"Migration completed successfully: {record_count:,} records in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            
            # Save failure checkpoint
            if checkpoint:
                checkpoint.status = 'failed'
                checkpoint.last_updated = datetime.now().isoformat()
                checkpoint.metadata['error'] = str(e)
                self._save_checkpoint(checkpoint)
            
            raise
    
    def migrate_hive_table(
        self,
        database: str,
        table: str,
        cloud_path: str,
        sync_mode: str = 'full',
        file_format: str = 'delta',
        partition_cols: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Migrate Hive table to cloud storage with schema preservation
        
        Args:
            database: Hive database name
            table: Hive table name
            cloud_path: Target cloud path
            sync_mode: Migration mode ('full' or 'incremental')
            file_format: Output format ('delta' or 'parquet')
            partition_cols: Columns to partition by (uses Hive partitions if None)
            where_clause: Optional WHERE clause for filtering
            job_id: Job ID for tracking
            
        Returns:
            Migration statistics
        """
        logger.info(f"Starting Hive table migration: {database}.{table}")
        
        job_id = job_id or f"hive_migration_{database}_{table}_{get_timestamp()}"
        start_time = datetime.now()
        
        try:
            # Get Hive table metadata
            table_metadata = self._get_hive_table_metadata(database, table)
            logger.info(f"Table schema: {len(table_metadata['columns'])} columns")
            
            # Determine partition columns
            if partition_cols is None:
                partition_cols = table_metadata.get('partition_columns', [])
            
            # Build query
            query = f"SELECT * FROM {database}.{table}"
            if where_clause:
                query += f" WHERE {where_clause}"
            
            logger.info(f"Executing query: {query}")
            
            # Read Hive table
            df = self.spark.sql(query)
            record_count = df.count()
            logger.info(f"Total records: {record_count:,}")
            
            # Save schema
            schema_path = f"{cloud_path}/_schema.json"
            self._save_schema(df.schema, schema_path, table_metadata)
            
            # Write to cloud
            logger.info(f"Writing to {cloud_path}")
            write_stats = self._write_cloud_data(
                df,
                cloud_path,
                file_format,
                compression='snappy',
                partition_cols=partition_cols
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'job_id': job_id,
                'status': 'completed',
                'database': database,
                'table': table,
                'records_migrated': record_count,
                'columns': len(table_metadata['columns']),
                'partition_columns': partition_cols,
                'files_written': write_stats.get('files_written', 0),
                'bytes_written': write_stats.get('bytes_written', 0),
                'duration_seconds': duration,
                'target_path': cloud_path,
                'schema_path': schema_path
            }
            
            logger.info(f"Hive table migration completed: {record_count:,} records in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Hive table migration failed: {str(e)}", exc_info=True)
            raise
    
    def migrate_multiple_tables(
        self,
        tables: List[Dict[str, str]],
        base_cloud_path: str,
        file_format: str = 'delta',
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Migrate multiple Hive tables in parallel
        
        Args:
            tables: List of dicts with 'database' and 'table' keys
            base_cloud_path: Base cloud path for all tables
            file_format: Output format
            parallel: Whether to migrate tables in parallel
            
        Returns:
            List of migration results
        """
        logger.info(f"Starting migration of {len(tables)} tables")
        results = []
        
        if parallel and len(tables) > 1:
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(tables))) as executor:
                futures = {}
                
                for table_info in tables:
                    db = table_info['database']
                    tbl = table_info['table']
                    cloud_path = f"{base_cloud_path}/{db}/{tbl}"
                    
                    future = executor.submit(
                        self.migrate_hive_table,
                        database=db,
                        table=tbl,
                        cloud_path=cloud_path,
                        file_format=file_format
                    )
                    futures[future] = f"{db}.{tbl}"
                
                for future in as_completed(futures):
                    table_name = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"Completed migration: {table_name}")
                    except Exception as e:
                        logger.error(f"Failed to migrate {table_name}: {str(e)}")
                        results.append({
                            'table': table_name,
                            'status': 'failed',
                            'error': str(e)
                        })
        else:
            # Sequential processing
            for table_info in tables:
                db = table_info['database']
                tbl = table_info['table']
                cloud_path = f"{base_cloud_path}/{db}/{tbl}"
                
                try:
                    result = self.migrate_hive_table(
                        database=db,
                        table=tbl,
                        cloud_path=cloud_path,
                        file_format=file_format
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to migrate {db}.{tbl}: {str(e)}")
                    results.append({
                        'database': db,
                        'table': tbl,
                        'status': 'failed',
                        'error': str(e)
                    })
        
        # Summary
        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = len(results) - successful
        logger.info(f"Migration summary: {successful} successful, {failed} failed")
        
        return results
    
    def _read_hdfs_data(self, hdfs_path: str, file_format: str) -> Optional[DataFrame]:
        """Read data from HDFS"""
        try:
            if file_format == 'parquet':
                return self.spark.read.parquet(hdfs_path)
            elif file_format == 'delta':
                return self.spark.read.format('delta').load(hdfs_path)
            elif file_format == 'csv':
                return self.spark.read.option('header', 'true').option('inferSchema', 'true').csv(hdfs_path)
            elif file_format == 'json':
                return self.spark.read.json(hdfs_path)
            else:
                # Try to infer format
                return self.spark.read.load(hdfs_path)
        except AnalysisException as e:
            logger.error(f"Failed to read from HDFS: {str(e)}")
            return None
    
    def _write_cloud_data(
        self,
        df: DataFrame,
        cloud_path: str,
        file_format: str,
        compression: Optional[str],
        partition_cols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Write data to cloud storage"""
        writer = df.write.mode('overwrite')
        
        if file_format == 'parquet':
            if compression:
                writer = writer.option('compression', compression)
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)
            writer.parquet(cloud_path)
            
        elif file_format == 'delta':
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)
            writer.format('delta').save(cloud_path)
            
        elif file_format == 'csv':
            writer = writer.option('header', 'true')
            if compression:
                writer = writer.option('compression', compression)
            writer.csv(cloud_path)
            
        elif file_format == 'json':
            if compression:
                writer = writer.option('compression', compression)
            writer.json(cloud_path)
        
        # Get write statistics
        return {
            'files_written': 1,  # Spark manages file count
            'bytes_written': 0   # Would need to query cloud storage for actual size
        }
    
    def _get_hive_table_metadata(self, database: str, table: str) -> Dict[str, Any]:
        """Get Hive table metadata"""
        try:
            # Get table description
            desc_df = self.spark.sql(f"DESCRIBE FORMATTED {database}.{table}")
            desc_rows = desc_df.collect()
            
            metadata = {
                'database': database,
                'table': table,
                'columns': [],
                'partition_columns': []
            }
            
            # Parse metadata
            in_partition_section = False
            for row in desc_rows:
                col_name = row['col_name'].strip() if row['col_name'] else ''
                
                if col_name == '# Partition Information':
                    in_partition_section = True
                    continue
                
                if col_name and not col_name.startswith('#'):
                    if in_partition_section:
                        metadata['partition_columns'].append(col_name)
                    else:
                        metadata['columns'].append({
                            'name': col_name,
                            'type': row['data_type']
                        })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get table metadata: {str(e)}")
            return {'columns': [], 'partition_columns': []}
    
    def _save_schema(self, schema: StructType, schema_path: str, metadata: Dict[str, Any]) -> None:
        """Save schema to cloud storage"""
        schema_dict = {
            'schema': json.loads(schema.json()),
            'metadata': metadata,
            'saved_at': datetime.now().isoformat()
        }
        
        schema_json = json.dumps(schema_dict, indent=2)
        
        # Write schema to cloud
        if self.target_platform == 's3':
            bucket, key = self._parse_s3_path(schema_path)
            self.s3_client.put_object(Bucket=bucket, Key=key, Body=schema_json)
        elif self.target_platform == 'adls':
            # Parse ADLS path and write
            container, path = self._parse_adls_path(schema_path)
            file_client = self.azure_client.get_file_system_client(container).get_file_client(path)
            file_client.upload_data(schema_json, overwrite=True)
        
        logger.info(f"Schema saved to {schema_path}")
    
    def _apply_incremental_filter(self, df: DataFrame, checkpoint: MigrationCheckpoint) -> DataFrame:
        """Apply incremental filter based on checkpoint"""
        # This is a placeholder - actual implementation would depend on table structure
        # Typically filter by timestamp or watermark column
        if 'timestamp' in df.columns:
            last_timestamp = checkpoint.metadata.get('last_timestamp')
            if last_timestamp:
                return df.filter(f"timestamp > '{last_timestamp}'")
        return df
    
    def _save_checkpoint(self, checkpoint: MigrationCheckpoint) -> None:
        """Save checkpoint to disk"""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint.job_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
        logger.debug(f"Checkpoint saved: {checkpoint_file}")
    
    def _load_checkpoint(self, job_id: str) -> Optional[MigrationCheckpoint]:
        """Load checkpoint from disk"""
        checkpoint_file = self.checkpoint_dir / f"{job_id}.json"
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            return MigrationCheckpoint.from_dict(data)
        return None
    
    def _parse_s3_path(self, s3_path: str) -> Tuple[str, str]:
        """Parse S3 path into bucket and key"""
        path = s3_path.replace('s3://', '').replace('s3a://', '')
        parts = path.split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        return bucket, key
    
    def _parse_adls_path(self, adls_path: str) -> Tuple[str, str]:
        """Parse ADLS path into container and path"""
        # Format: abfss://container@account.dfs.core.windows.net/path
        path = adls_path.replace('abfss://', '').replace('abfs://', '')
        container = path.split('@')[0]
        file_path = path.split('/', 1)[1] if '/' in path else ''
        return container, file_path
    
    def get_migration_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a migration job"""
        checkpoint = self._load_checkpoint(job_id)
        if checkpoint:
            return checkpoint.to_dict()
        return None
    
    def list_migrations(self) -> List[Dict[str, Any]]:
        """List all migration jobs"""
        migrations = []
        for checkpoint_file in self.checkpoint_dir.glob('*.json'):
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                migrations.append(data)
        return migrations
