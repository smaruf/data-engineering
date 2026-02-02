"""
Incremental Data Synchronization Module

Provides incremental data synchronization using CDC (Change Data Capture) patterns.

Features:
- Timestamp-based incremental sync
- Watermark tracking
- Merge/upsert operations
- Delta Lake change data feed
- Configurable sync intervals
- Conflict resolution strategies
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json
from enum import Enum

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, max as spark_max, lit, current_timestamp
from delta.tables import DeltaTable

from shared.utils.config_loader import config
from shared.utils.logger import get_logger
from shared.utils.connection_manager import connections
from shared.utils.helpers import get_timestamp

logger = get_logger(__name__)


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    LATEST_TIMESTAMP = "latest_timestamp"
    CUSTOM = "custom"


class SyncMode(Enum):
    """Synchronization modes"""
    APPEND = "append"
    UPSERT = "upsert"
    OVERWRITE = "overwrite"
    MERGE = "merge"


class IncrementalSync:
    """
    Incremental data synchronization with CDC patterns
    
    Supports:
    - Timestamp-based incremental updates
    - Watermark tracking and persistence
    - Delta Lake merge operations
    - Conflict resolution
    - Multiple sync strategies
    """
    
    def __init__(
        self,
        watermark_table: str = "sync_watermarks",
        watermark_storage: str = "postgres",
        checkpoint_dir: str = "/tmp/sync_checkpoints"
    ):
        """
        Initialize incremental sync
        
        Args:
            watermark_table: Table name for storing watermarks
            watermark_storage: Storage for watermarks ('postgres', 'file', 'delta')
            checkpoint_dir: Directory for checkpoints
        """
        self.watermark_table = watermark_table
        self.watermark_storage = watermark_storage
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.spark = connections.spark
        
        # Initialize watermark storage
        self._init_watermark_storage()
        
        logger.info(f"Initialized incremental sync with {watermark_storage} watermark storage")
    
    def sync_incremental(
        self,
        source_path: str,
        target_path: str,
        sync_id: str,
        timestamp_column: str = "updated_at",
        key_columns: Optional[List[str]] = None,
        sync_mode: SyncMode = SyncMode.UPSERT,
        conflict_resolution: ConflictResolution = ConflictResolution.LATEST_TIMESTAMP,
        source_format: str = "delta",
        target_format: str = "delta",
        custom_filter: Optional[Callable[[DataFrame, datetime], DataFrame]] = None
    ) -> Dict[str, Any]:
        """
        Perform incremental synchronization
        
        Args:
            source_path: Source data path
            target_path: Target data path
            sync_id: Unique identifier for this sync job
            timestamp_column: Column for timestamp-based filtering
            key_columns: Primary key columns for merge/upsert
            sync_mode: Synchronization mode
            conflict_resolution: Strategy for resolving conflicts
            source_format: Source data format
            target_format: Target data format
            custom_filter: Optional custom filter function
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting incremental sync: {sync_id}")
        logger.info(f"Source: {source_path} -> Target: {target_path}")
        logger.info(f"Mode: {sync_mode.value}, Timestamp column: {timestamp_column}")
        
        start_time = datetime.now()
        
        try:
            # Get last watermark
            last_watermark = self._get_watermark(sync_id)
            logger.info(f"Last watermark: {last_watermark}")
            
            # Read source data
            source_df = self._read_data(source_path, source_format)
            
            # Apply incremental filter
            if custom_filter:
                incremental_df = custom_filter(source_df, last_watermark)
            else:
                incremental_df = self._apply_timestamp_filter(
                    source_df, 
                    timestamp_column, 
                    last_watermark
                )
            
            # Get record count
            record_count = incremental_df.count()
            logger.info(f"Incremental records: {record_count:,}")
            
            if record_count == 0:
                logger.info("No new records to sync")
                return {
                    'sync_id': sync_id,
                    'status': 'completed',
                    'records_synced': 0,
                    'duration_seconds': 0,
                    'watermark': last_watermark.isoformat() if last_watermark else None
                }
            
            # Perform sync based on mode
            if sync_mode == SyncMode.APPEND:
                self._sync_append(incremental_df, target_path, target_format)
                
            elif sync_mode in (SyncMode.UPSERT, SyncMode.MERGE):
                if not key_columns:
                    raise ValueError("key_columns required for upsert/merge mode")
                
                self._sync_merge(
                    incremental_df,
                    target_path,
                    key_columns,
                    timestamp_column,
                    conflict_resolution,
                    target_format
                )
                
            elif sync_mode == SyncMode.OVERWRITE:
                self._sync_overwrite(incremental_df, target_path, target_format)
            
            # Calculate new watermark
            new_watermark = self._calculate_watermark(incremental_df, timestamp_column)
            logger.info(f"New watermark: {new_watermark}")
            
            # Save watermark
            self._save_watermark(sync_id, new_watermark, {
                'source_path': source_path,
                'target_path': target_path,
                'timestamp_column': timestamp_column,
                'sync_mode': sync_mode.value
            })
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'sync_id': sync_id,
                'status': 'completed',
                'records_synced': record_count,
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'watermark': new_watermark.isoformat(),
                'previous_watermark': last_watermark.isoformat() if last_watermark else None
            }
            
            logger.info(f"Sync completed: {record_count:,} records in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}", exc_info=True)
            raise
    
    def sync_with_cdf(
        self,
        source_delta_table: str,
        target_path: str,
        sync_id: str,
        key_columns: List[str],
        starting_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sync using Delta Lake Change Data Feed
        
        Args:
            source_delta_table: Source Delta table path
            target_path: Target path
            sync_id: Sync identifier
            key_columns: Primary key columns
            starting_version: Starting version for CDC (uses watermark if None)
            
        Returns:
            Sync statistics
        """
        logger.info(f"Starting CDC sync: {sync_id}")
        logger.info(f"Source: {source_delta_table}")
        
        start_time = datetime.now()
        
        try:
            # Get last version from watermark
            if starting_version is None:
                watermark_data = self._get_watermark_metadata(sync_id)
                starting_version = watermark_data.get('last_version', 0) if watermark_data else 0
            
            logger.info(f"Reading changes from version {starting_version}")
            
            # Read change data
            changes_df = self.spark.read.format("delta") \
                .option("readChangeFeed", "true") \
                .option("startingVersion", starting_version) \
                .load(source_delta_table)
            
            if changes_df.isEmpty():
                logger.info("No changes detected")
                return {
                    'sync_id': sync_id,
                    'status': 'completed',
                    'records_synced': 0,
                    'duration_seconds': 0
                }
            
            # Process changes
            inserts = changes_df.filter(col("_change_type") == "insert")
            updates = changes_df.filter(col("_change_type") == "update_postimage")
            deletes = changes_df.filter(col("_change_type") == "delete")
            
            insert_count = inserts.count()
            update_count = updates.count()
            delete_count = deletes.count()
            
            logger.info(f"Changes: {insert_count} inserts, {update_count} updates, {delete_count} deletes")
            
            # Apply changes to target
            if DeltaTable.isDeltaTable(self.spark, target_path):
                target_table = DeltaTable.forPath(self.spark, target_path)
                
                # Apply updates and inserts
                if not (inserts.isEmpty() and updates.isEmpty()):
                    upserts = inserts.union(updates)
                    
                    merge_condition = " AND ".join([
                        f"target.{col} = source.{col}" for col in key_columns
                    ])
                    
                    target_table.alias("target").merge(
                        upserts.alias("source"),
                        merge_condition
                    ).whenMatchedUpdateAll() \
                     .whenNotMatchedInsertAll() \
                     .execute()
                
                # Apply deletes
                if not deletes.isEmpty():
                    delete_condition = " OR ".join([
                        f"({' AND '.join([f'{col} = {row[col]}' for col in key_columns])})"
                        for row in deletes.select(key_columns).distinct().collect()
                    ])
                    target_table.delete(delete_condition)
            else:
                # Create new Delta table with inserts/updates
                upserts = inserts.union(updates)
                upserts.write.format("delta").mode("overwrite").save(target_path)
            
            # Get latest version
            latest_version = changes_df.select(spark_max("_commit_version")).collect()[0][0]
            
            # Save watermark with version
            self._save_watermark(sync_id, datetime.now(), {
                'last_version': latest_version,
                'source_table': source_delta_table
            })
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'sync_id': sync_id,
                'status': 'completed',
                'inserts': insert_count,
                'updates': update_count,
                'deletes': delete_count,
                'total_records': insert_count + update_count + delete_count,
                'duration_seconds': duration,
                'latest_version': latest_version
            }
            
            logger.info(f"CDC sync completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"CDC sync failed: {str(e)}", exc_info=True)
            raise
    
    def scheduled_sync(
        self,
        source_path: str,
        target_path: str,
        sync_id: str,
        interval_minutes: int = 60,
        max_iterations: Optional[int] = None,
        **sync_kwargs
    ) -> List[Dict[str, Any]]:
        """
        Run scheduled incremental sync
        
        Args:
            source_path: Source data path
            target_path: Target data path
            sync_id: Sync identifier
            interval_minutes: Sync interval in minutes
            max_iterations: Maximum iterations (None for infinite)
            **sync_kwargs: Additional arguments for sync_incremental
            
        Returns:
            List of sync results
        """
        logger.info(f"Starting scheduled sync: {sync_id}")
        logger.info(f"Interval: {interval_minutes} minutes")
        
        results = []
        iteration = 0
        
        while max_iterations is None or iteration < max_iterations:
            try:
                logger.info(f"Iteration {iteration + 1}")
                
                result = self.sync_incremental(
                    source_path=source_path,
                    target_path=target_path,
                    sync_id=sync_id,
                    **sync_kwargs
                )
                
                results.append(result)
                iteration += 1
                
                if max_iterations is None or iteration < max_iterations:
                    logger.info(f"Waiting {interval_minutes} minutes until next sync")
                    import time
                    time.sleep(interval_minutes * 60)
                    
            except KeyboardInterrupt:
                logger.info("Sync interrupted by user")
                break
            except Exception as e:
                logger.error(f"Sync iteration failed: {str(e)}")
                results.append({
                    'iteration': iteration,
                    'status': 'failed',
                    'error': str(e)
                })
                iteration += 1
        
        logger.info(f"Scheduled sync completed: {len(results)} iterations")
        return results
    
    def _read_data(self, path: str, format: str) -> DataFrame:
        """Read data from path"""
        if format == 'delta':
            return self.spark.read.format('delta').load(path)
        elif format == 'parquet':
            return self.spark.read.parquet(path)
        elif format == 'csv':
            return self.spark.read.option('header', 'true').option('inferSchema', 'true').csv(path)
        elif format == 'json':
            return self.spark.read.json(path)
        else:
            return self.spark.read.load(path)
    
    def _apply_timestamp_filter(
        self,
        df: DataFrame,
        timestamp_column: str,
        watermark: Optional[datetime]
    ) -> DataFrame:
        """Apply timestamp-based filter"""
        if watermark is None:
            return df
        
        watermark_str = watermark.strftime('%Y-%m-%d %H:%M:%S')
        return df.filter(col(timestamp_column) > lit(watermark_str))
    
    def _sync_append(self, df: DataFrame, target_path: str, target_format: str) -> None:
        """Append mode sync"""
        writer = df.write.mode('append')
        
        if target_format == 'delta':
            writer.format('delta').save(target_path)
        elif target_format == 'parquet':
            writer.parquet(target_path)
        else:
            writer.save(target_path)
    
    def _sync_merge(
        self,
        df: DataFrame,
        target_path: str,
        key_columns: List[str],
        timestamp_column: str,
        conflict_resolution: ConflictResolution,
        target_format: str
    ) -> None:
        """Merge/upsert mode sync"""
        if target_format != 'delta':
            raise ValueError("Merge mode requires Delta format")
        
        if DeltaTable.isDeltaTable(self.spark, target_path):
            target_table = DeltaTable.forPath(self.spark, target_path)
            
            # Build merge condition
            merge_condition = " AND ".join([
                f"target.{col} = source.{col}" for col in key_columns
            ])
            
            # Build update condition based on conflict resolution
            if conflict_resolution == ConflictResolution.SOURCE_WINS:
                target_table.alias("target").merge(
                    df.alias("source"),
                    merge_condition
                ).whenMatchedUpdateAll() \
                 .whenNotMatchedInsertAll() \
                 .execute()
                
            elif conflict_resolution == ConflictResolution.LATEST_TIMESTAMP:
                update_condition = f"source.{timestamp_column} > target.{timestamp_column}"
                target_table.alias("target").merge(
                    df.alias("source"),
                    merge_condition
                ).whenMatchedUpdate(
                    condition=update_condition,
                    set={}  # Update all columns
                ).whenNotMatchedInsertAll() \
                 .execute()
                
            elif conflict_resolution == ConflictResolution.TARGET_WINS:
                target_table.alias("target").merge(
                    df.alias("source"),
                    merge_condition
                ).whenNotMatchedInsertAll() \
                 .execute()
        else:
            # Create new Delta table
            df.write.format('delta').mode('overwrite').save(target_path)
    
    def _sync_overwrite(self, df: DataFrame, target_path: str, target_format: str) -> None:
        """Overwrite mode sync"""
        writer = df.write.mode('overwrite')
        
        if target_format == 'delta':
            writer.format('delta').save(target_path)
        elif target_format == 'parquet':
            writer.parquet(target_path)
        else:
            writer.save(target_path)
    
    def _calculate_watermark(self, df: DataFrame, timestamp_column: str) -> datetime:
        """Calculate new watermark from dataframe"""
        max_timestamp = df.select(spark_max(timestamp_column)).collect()[0][0]
        
        if isinstance(max_timestamp, datetime):
            return max_timestamp
        elif isinstance(max_timestamp, str):
            return datetime.fromisoformat(max_timestamp)
        else:
            # Fallback to current time
            return datetime.now()
    
    def _init_watermark_storage(self) -> None:
        """Initialize watermark storage"""
        if self.watermark_storage == 'postgres':
            # Create watermark table if not exists
            with connections.database_connection('postgres') as conn:
                conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.watermark_table} (
                        sync_id VARCHAR(255) PRIMARY KEY,
                        watermark TIMESTAMP NOT NULL,
                        metadata JSONB,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        elif self.watermark_storage == 'file':
            # File-based storage already handled by checkpoint_dir
            pass
        elif self.watermark_storage == 'delta':
            # Delta table storage
            watermark_path = str(self.checkpoint_dir / 'watermarks')
            if not DeltaTable.isDeltaTable(self.spark, watermark_path):
                schema = "sync_id STRING, watermark TIMESTAMP, metadata STRING, updated_at TIMESTAMP"
                self.spark.createDataFrame([], schema).write.format('delta').save(watermark_path)
    
    def _get_watermark(self, sync_id: str) -> Optional[datetime]:
        """Get last watermark for sync job"""
        try:
            if self.watermark_storage == 'postgres':
                with connections.database_connection('postgres') as conn:
                    result = conn.execute(
                        f"SELECT watermark FROM {self.watermark_table} WHERE sync_id = %s",
                        (sync_id,)
                    ).fetchone()
                    return result[0] if result else None
                    
            elif self.watermark_storage == 'file':
                watermark_file = self.checkpoint_dir / f"{sync_id}_watermark.json"
                if watermark_file.exists():
                    with open(watermark_file, 'r') as f:
                        data = json.load(f)
                        return datetime.fromisoformat(data['watermark'])
                return None
                
            elif self.watermark_storage == 'delta':
                watermark_path = str(self.checkpoint_dir / 'watermarks')
                df = self.spark.read.format('delta').load(watermark_path)
                result = df.filter(col('sync_id') == sync_id).select('watermark').collect()
                return result[0][0] if result else None
                
        except Exception as e:
            logger.warning(f"Failed to get watermark: {str(e)}")
            return None
    
    def _get_watermark_metadata(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """Get watermark metadata"""
        try:
            if self.watermark_storage == 'file':
                watermark_file = self.checkpoint_dir / f"{sync_id}_watermark.json"
                if watermark_file.exists():
                    with open(watermark_file, 'r') as f:
                        return json.load(f).get('metadata', {})
            return None
        except Exception as e:
            logger.warning(f"Failed to get watermark metadata: {str(e)}")
            return None
    
    def _save_watermark(
        self,
        sync_id: str,
        watermark: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save watermark"""
        try:
            if self.watermark_storage == 'postgres':
                with connections.database_connection('postgres') as conn:
                    metadata_json = json.dumps(metadata) if metadata else None
                    conn.execute(f"""
                        INSERT INTO {self.watermark_table} (sync_id, watermark, metadata, updated_at)
                        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (sync_id) DO UPDATE
                        SET watermark = EXCLUDED.watermark,
                            metadata = EXCLUDED.metadata,
                            updated_at = CURRENT_TIMESTAMP
                    """, (sync_id, watermark, metadata_json))
                    conn.commit()
                    
            elif self.watermark_storage == 'file':
                watermark_file = self.checkpoint_dir / f"{sync_id}_watermark.json"
                data = {
                    'sync_id': sync_id,
                    'watermark': watermark.isoformat(),
                    'metadata': metadata,
                    'updated_at': datetime.now().isoformat()
                }
                with open(watermark_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif self.watermark_storage == 'delta':
                watermark_path = str(self.checkpoint_dir / 'watermarks')
                data = [(sync_id, watermark, json.dumps(metadata) if metadata else None, datetime.now())]
                df = self.spark.createDataFrame(data, ["sync_id", "watermark", "metadata", "updated_at"])
                
                if DeltaTable.isDeltaTable(self.spark, watermark_path):
                    target = DeltaTable.forPath(self.spark, watermark_path)
                    target.alias("target").merge(
                        df.alias("source"),
                        "target.sync_id = source.sync_id"
                    ).whenMatchedUpdateAll() \
                     .whenNotMatchedInsertAll() \
                     .execute()
                else:
                    df.write.format('delta').save(watermark_path)
                    
            logger.debug(f"Watermark saved for {sync_id}: {watermark}")
            
        except Exception as e:
            logger.error(f"Failed to save watermark: {str(e)}", exc_info=True)
            raise
    
    def get_sync_status(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """Get sync status and watermark info"""
        watermark = self._get_watermark(sync_id)
        metadata = self._get_watermark_metadata(sync_id)
        
        if watermark:
            return {
                'sync_id': sync_id,
                'last_watermark': watermark.isoformat(),
                'metadata': metadata
            }
        return None
    
    def list_syncs(self) -> List[Dict[str, Any]]:
        """List all sync jobs"""
        syncs = []
        
        try:
            if self.watermark_storage == 'file':
                for watermark_file in self.checkpoint_dir.glob('*_watermark.json'):
                    with open(watermark_file, 'r') as f:
                        data = json.load(f)
                        syncs.append(data)
            elif self.watermark_storage == 'delta':
                watermark_path = str(self.checkpoint_dir / 'watermarks')
                if DeltaTable.isDeltaTable(self.spark, watermark_path):
                    df = self.spark.read.format('delta').load(watermark_path)
                    syncs = [row.asDict() for row in df.collect()]
        except Exception as e:
            logger.error(f"Failed to list syncs: {str(e)}")
        
        return syncs
