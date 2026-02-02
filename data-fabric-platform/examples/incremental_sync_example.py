"""
Example: Incremental Data Synchronization

This example demonstrates incremental data sync using CDC patterns.
"""

from src.migration import IncrementalSync
from src.migration.incremental_sync import SyncMode, ConflictResolution
from datetime import datetime, timedelta

def example_basic_incremental_sync():
    """Basic incremental synchronization"""
    
    print("=== Basic Incremental Sync ===\n")
    
    # Initialize with file-based watermark storage
    sync = IncrementalSync(
        watermark_table='sync_watermarks',
        watermark_storage='file',
        checkpoint_dir='/tmp/sync_checkpoints'
    )
    
    # First sync - full load
    print("First sync (full load)...")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/sales',
        target_path='s3://target-bucket/sales',
        sync_id='sales_sync',
        timestamp_column='updated_at',
        key_columns=['id'],
        sync_mode=SyncMode.UPSERT,
        conflict_resolution=ConflictResolution.LATEST_TIMESTAMP,
        source_format='delta',
        target_format='delta'
    )
    
    print(f"Synced: {result['records_synced']:,} records")
    print(f"Watermark: {result['watermark']}")
    
    # Simulate time passing and data changes...
    print("\nWaiting for new data...")
    
    # Second sync - incremental only
    print("\nSecond sync (incremental)...")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/sales',
        target_path='s3://target-bucket/sales',
        sync_id='sales_sync',
        timestamp_column='updated_at',
        key_columns=['id'],
        sync_mode=SyncMode.UPSERT,
        conflict_resolution=ConflictResolution.LATEST_TIMESTAMP,
        source_format='delta',
        target_format='delta'
    )
    
    print(f"Synced: {result['records_synced']:,} records (incremental)")
    print(f"New watermark: {result['watermark']}")
    print(f"Previous watermark: {result['previous_watermark']}")


def example_delta_cdf_sync():
    """Sync using Delta Lake Change Data Feed"""
    
    print("\n=== Delta Lake Change Data Feed Sync ===\n")
    
    sync = IncrementalSync(
        watermark_storage='file',
        checkpoint_dir='/tmp/sync_checkpoints'
    )
    
    # Enable CDF on source Delta table first:
    # ALTER TABLE delta.`s3://source-bucket/sales_delta` 
    # SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
    
    print("Syncing using Change Data Feed...")
    result = sync.sync_with_cdf(
        source_delta_table='s3://source-bucket/sales_delta',
        target_path='s3://target-bucket/sales_delta',
        sync_id='sales_cdf_sync',
        key_columns=['id']
    )
    
    print(f"\nCDC Sync completed!")
    print(f"Inserts: {result['inserts']:,}")
    print(f"Updates: {result['updates']:,}")
    print(f"Deletes: {result['deletes']:,}")
    print(f"Total changes: {result['total_records']:,}")
    print(f"Latest version: {result['latest_version']}")


def example_scheduled_sync():
    """Scheduled incremental sync"""
    
    print("\n=== Scheduled Incremental Sync ===\n")
    
    sync = IncrementalSync(watermark_storage='file')
    
    print("Starting scheduled sync (every 5 minutes for 30 minutes)...")
    
    results = sync.scheduled_sync(
        source_path='s3://source-bucket/transactions',
        target_path='s3://target-bucket/transactions',
        sync_id='hourly_transactions_sync',
        interval_minutes=5,
        max_iterations=6,  # 30 minutes total
        timestamp_column='created_at',
        key_columns=['transaction_id'],
        sync_mode=SyncMode.APPEND,
        source_format='delta',
        target_format='delta'
    )
    
    # Print summary
    print("\nScheduled Sync Summary:")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        if result.get('status') == 'completed':
            print(f"Iteration {i}: {result['records_synced']:,} records in {result['duration_seconds']:.2f}s")
        else:
            print(f"Iteration {i}: Failed - {result.get('error', 'Unknown error')}")


def example_custom_filter():
    """Incremental sync with custom filter function"""
    
    print("\n=== Incremental Sync with Custom Filter ===\n")
    
    sync = IncrementalSync(watermark_storage='file')
    
    # Define custom filter
    def custom_filter(df, last_watermark):
        """
        Custom filter to sync only records from specific regions
        and within the last 7 days
        """
        from pyspark.sql.functions import col, lit
        
        # Calculate cutoff date
        cutoff = datetime.now() - timedelta(days=7)
        if last_watermark and last_watermark > cutoff:
            cutoff = last_watermark
        
        # Filter by timestamp and region
        return df.filter(
            (col('updated_at') > lit(cutoff.strftime('%Y-%m-%d %H:%M:%S'))) &
            (col('region').isin(['US', 'EU', 'APAC']))
        )
    
    print("Syncing with custom filter (last 7 days, specific regions)...")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/sales',
        target_path='s3://target-bucket/sales_filtered',
        sync_id='filtered_sales_sync',
        custom_filter=custom_filter,
        key_columns=['id'],
        sync_mode=SyncMode.UPSERT,
        source_format='delta',
        target_format='delta'
    )
    
    print(f"Synced: {result['records_synced']:,} records")


def example_different_sync_modes():
    """Demonstrate different sync modes"""
    
    print("\n=== Different Sync Modes ===\n")
    
    sync = IncrementalSync(watermark_storage='file')
    
    # 1. APPEND mode - just append new records
    print("1. APPEND mode (no deduplication):")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/logs',
        target_path='s3://target-bucket/logs_append',
        sync_id='logs_append_sync',
        timestamp_column='timestamp',
        sync_mode=SyncMode.APPEND,
        source_format='parquet',
        target_format='delta'
    )
    print(f"   Appended: {result['records_synced']:,} records\n")
    
    # 2. UPSERT mode - insert new and update existing
    print("2. UPSERT mode (insert + update):")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/customers',
        target_path='s3://target-bucket/customers_upsert',
        sync_id='customers_upsert_sync',
        timestamp_column='updated_at',
        key_columns=['customer_id'],
        sync_mode=SyncMode.UPSERT,
        conflict_resolution=ConflictResolution.SOURCE_WINS,
        source_format='delta',
        target_format='delta'
    )
    print(f"   Upserted: {result['records_synced']:,} records\n")
    
    # 3. OVERWRITE mode - replace all data
    print("3. OVERWRITE mode (full refresh):")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/reference_data',
        target_path='s3://target-bucket/reference_data',
        sync_id='reference_overwrite_sync',
        timestamp_column='updated_at',
        sync_mode=SyncMode.OVERWRITE,
        source_format='delta',
        target_format='delta'
    )
    print(f"   Overwrote with: {result['records_synced']:,} records")


def example_conflict_resolution():
    """Demonstrate different conflict resolution strategies"""
    
    print("\n=== Conflict Resolution Strategies ===\n")
    
    sync = IncrementalSync(watermark_storage='file')
    
    # 1. SOURCE_WINS - always take source data
    print("1. SOURCE_WINS strategy:")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/products',
        target_path='s3://target-bucket/products_source_wins',
        sync_id='products_source_wins_sync',
        timestamp_column='updated_at',
        key_columns=['product_id'],
        sync_mode=SyncMode.UPSERT,
        conflict_resolution=ConflictResolution.SOURCE_WINS,
        source_format='delta',
        target_format='delta'
    )
    print(f"   Source always wins: {result['records_synced']:,} records\n")
    
    # 2. TARGET_WINS - only insert new, don't update existing
    print("2. TARGET_WINS strategy:")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/products',
        target_path='s3://target-bucket/products_target_wins',
        sync_id='products_target_wins_sync',
        timestamp_column='updated_at',
        key_columns=['product_id'],
        sync_mode=SyncMode.UPSERT,
        conflict_resolution=ConflictResolution.TARGET_WINS,
        source_format='delta',
        target_format='delta'
    )
    print(f"   Target preserved: {result['records_synced']:,} records (inserts only)\n")
    
    # 3. LATEST_TIMESTAMP - use timestamp to resolve conflicts
    print("3. LATEST_TIMESTAMP strategy:")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/products',
        target_path='s3://target-bucket/products_latest',
        sync_id='products_latest_sync',
        timestamp_column='updated_at',
        key_columns=['product_id'],
        sync_mode=SyncMode.UPSERT,
        conflict_resolution=ConflictResolution.LATEST_TIMESTAMP,
        source_format='delta',
        target_format='delta'
    )
    print(f"   Latest timestamp wins: {result['records_synced']:,} records")


def example_postgres_watermark_storage():
    """Use PostgreSQL for watermark storage"""
    
    print("\n=== PostgreSQL Watermark Storage ===\n")
    
    # Initialize with Postgres storage
    sync = IncrementalSync(
        watermark_table='sync_watermarks',
        watermark_storage='postgres'  # Use PostgreSQL
    )
    
    print("Using PostgreSQL for watermark persistence...")
    result = sync.sync_incremental(
        source_path='s3://source-bucket/orders',
        target_path='s3://target-bucket/orders',
        sync_id='orders_postgres_sync',
        timestamp_column='order_date',
        key_columns=['order_id'],
        sync_mode=SyncMode.UPSERT,
        source_format='delta',
        target_format='delta'
    )
    
    print(f"Synced: {result['records_synced']:,} records")
    print("Watermark stored in PostgreSQL")


def example_sync_status_monitoring():
    """Monitor sync status and list all syncs"""
    
    print("\n=== Sync Status Monitoring ===\n")
    
    sync = IncrementalSync(watermark_storage='file')
    
    # Get status of specific sync
    print("Checking sync status...")
    status = sync.get_sync_status('sales_sync')
    
    if status:
        print(f"Sync ID: {status['sync_id']}")
        print(f"Last watermark: {status['last_watermark']}")
        print(f"Metadata: {status['metadata']}")
    else:
        print("No sync found with that ID")
    
    # List all syncs
    print("\nListing all sync jobs:")
    syncs = sync.list_syncs()
    
    if syncs:
        print("-" * 80)
        for sync_info in syncs:
            print(f"Sync ID: {sync_info.get('sync_id')}")
            print(f"  Last watermark: {sync_info.get('watermark')}")
            print(f"  Updated: {sync_info.get('updated_at')}")
            print()
    else:
        print("No sync jobs found")


def example_multi_source_sync():
    """Sync from multiple sources to a single target"""
    
    print("\n=== Multi-Source Sync ===\n")
    
    sync = IncrementalSync(watermark_storage='file')
    
    # Define multiple sources
    sources = [
        {
            'sync_id': 'sales_us_sync',
            'source': 's3://source-bucket/sales/us',
            'region': 'US'
        },
        {
            'sync_id': 'sales_eu_sync',
            'source': 's3://source-bucket/sales/eu',
            'region': 'EU'
        },
        {
            'sync_id': 'sales_apac_sync',
            'source': 's3://source-bucket/sales/apac',
            'region': 'APAC'
        }
    ]
    
    target_path = 's3://target-bucket/sales_consolidated'
    
    print(f"Syncing from {len(sources)} sources to single target...\n")
    
    results = []
    for source in sources:
        print(f"Syncing {source['region']}...")
        result = sync.sync_incremental(
            source_path=source['source'],
            target_path=target_path,
            sync_id=source['sync_id'],
            timestamp_column='updated_at',
            key_columns=['id'],
            sync_mode=SyncMode.APPEND,  # Append from all sources
            source_format='delta',
            target_format='delta'
        )
        results.append({
            'region': source['region'],
            'records': result['records_synced']
        })
        print(f"  {result['records_synced']:,} records\n")
    
    # Summary
    total_records = sum(r['records'] for r in results)
    print(f"Total records synced: {total_records:,}")


if __name__ == '__main__':
    print("Incremental Data Synchronization Examples")
    print("=" * 80)
    
    # Uncomment the examples you want to run:
    
    # Basic examples
    # example_basic_incremental_sync()
    # example_delta_cdf_sync()
    # example_scheduled_sync()
    
    # Advanced examples
    # example_custom_filter()
    # example_different_sync_modes()
    # example_conflict_resolution()
    
    # Storage and monitoring
    # example_postgres_watermark_storage()
    # example_sync_status_monitoring()
    
    # Complex scenarios
    # example_multi_source_sync()
    
    print("\n" + "=" * 80)
    print("Examples completed!")
    print("\nNote: Uncomment the example functions in __main__ to run them.")
    print("Make sure to configure environment variables and have proper access to:")
    print("  - Source and target data locations (S3/ADLS)")
    print("  - Delta Lake tables (if using CDF)")
    print("  - PostgreSQL (if using Postgres watermark storage)")
    print("  - Spark cluster")
