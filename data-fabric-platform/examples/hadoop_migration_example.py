"""
Example: Hadoop to Cloud Migration

This example demonstrates migrating data from on-premise Hadoop to cloud platforms.
"""

from src.migration import HadoopToCloudMigration

def example_hdfs_to_s3():
    """Migrate HDFS directory to S3"""
    
    print("=== HDFS to S3 Migration ===\n")
    
    # Initialize migrator
    migrator = HadoopToCloudMigration(
        target_platform='s3',
        checkpoint_dir='/tmp/migration_checkpoints',
        max_workers=10
    )
    
    # Migrate HDFS directory
    print("Migrating HDFS directory to S3...")
    result = migrator.migrate_hdfs_to_cloud(
        hdfs_path='hdfs://namenode:9000/data/sales',
        cloud_path='s3://my-bucket/sales',
        sync_mode='full',
        file_format='delta',
        compression='snappy',
        partition_cols=['year', 'month'],
        job_id='sales_migration_001'
    )
    
    print(f"\nMigration completed!")
    print(f"Records migrated: {result['records_migrated']:,}")
    print(f"Files written: {result['files_written']}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Target: {result['target_path']}")


def example_hive_table_migration():
    """Migrate Hive table to S3"""
    
    print("\n=== Hive Table to S3 Migration ===\n")
    
    migrator = HadoopToCloudMigration(target_platform='s3')
    
    # Migrate single Hive table
    print("Migrating Hive table sales_db.transactions...")
    result = migrator.migrate_hive_table(
        database='sales_db',
        table='transactions',
        cloud_path='s3://my-bucket/warehouse/sales_db/transactions',
        file_format='delta',
        partition_cols=['year', 'month', 'day']
    )
    
    print(f"\nTable migration completed!")
    print(f"Records migrated: {result['records_migrated']:,}")
    print(f"Columns: {result['columns']}")
    print(f"Partition columns: {result['partition_columns']}")
    print(f"Schema saved to: {result['schema_path']}")


def example_multiple_tables_migration():
    """Migrate multiple Hive tables in parallel"""
    
    print("\n=== Multiple Hive Tables to S3 Migration ===\n")
    
    migrator = HadoopToCloudMigration(target_platform='s3', max_workers=5)
    
    # Define tables to migrate
    tables = [
        {'database': 'sales_db', 'table': 'transactions'},
        {'database': 'sales_db', 'table': 'customers'},
        {'database': 'sales_db', 'table': 'products'},
        {'database': 'sales_db', 'table': 'orders'},
        {'database': 'sales_db', 'table': 'order_items'}
    ]
    
    print(f"Migrating {len(tables)} tables in parallel...")
    results = migrator.migrate_multiple_tables(
        tables=tables,
        base_cloud_path='s3://my-bucket/warehouse',
        file_format='delta',
        parallel=True
    )
    
    # Print summary
    print("\nMigration Summary:")
    print("-" * 80)
    successful = 0
    failed = 0
    total_records = 0
    
    for result in results:
        if result.get('status') == 'completed':
            successful += 1
            total_records += result.get('records_migrated', 0)
            print(f"✓ {result['database']}.{result['table']}: {result['records_migrated']:,} records")
        else:
            failed += 1
            print(f"✗ {result.get('table', 'unknown')}: {result.get('error', 'Unknown error')}")
    
    print("-" * 80)
    print(f"Total: {successful} successful, {failed} failed")
    print(f"Total records migrated: {total_records:,}")


def example_hdfs_to_adls():
    """Migrate HDFS to Azure ADLS"""
    
    print("\n=== HDFS to Azure ADLS Migration ===\n")
    
    # Initialize migrator for Azure
    migrator = HadoopToCloudMigration(
        target_platform='adls',
        max_workers=10
    )
    
    # Migrate to ADLS
    print("Migrating HDFS directory to ADLS...")
    result = migrator.migrate_hdfs_to_cloud(
        hdfs_path='hdfs://namenode:9000/data/sales',
        cloud_path='abfss://container@storageaccount.dfs.core.windows.net/sales',
        sync_mode='full',
        file_format='delta',
        partition_cols=['year', 'month']
    )
    
    print(f"\nMigration to ADLS completed!")
    print(f"Records migrated: {result['records_migrated']:,}")
    print(f"Target: {result['target_path']}")


def example_incremental_migration():
    """Demonstrate incremental migration with resume"""
    
    print("\n=== Incremental Migration with Resume ===\n")
    
    migrator = HadoopToCloudMigration(
        target_platform='s3',
        checkpoint_dir='/tmp/migration_checkpoints'
    )
    
    job_id = 'incremental_sales_migration'
    
    # First run - full migration
    print("First run: Full migration...")
    try:
        result = migrator.migrate_hdfs_to_cloud(
            hdfs_path='hdfs://namenode:9000/data/sales',
            cloud_path='s3://my-bucket/sales',
            sync_mode='incremental',
            file_format='delta',
            job_id=job_id,
            resume=False
        )
        print(f"Migrated: {result['records_migrated']:,} records")
    except Exception as e:
        print(f"Migration failed: {e}")
    
    # Second run - resume from checkpoint
    print("\nSecond run: Resume from checkpoint...")
    result = migrator.migrate_hdfs_to_cloud(
        hdfs_path='hdfs://namenode:9000/data/sales',
        cloud_path='s3://my-bucket/sales',
        sync_mode='incremental',
        file_format='delta',
        job_id=job_id,
        resume=True  # Resume from previous checkpoint
    )
    print(f"Migrated: {result['records_migrated']:,} records")
    
    # Check migration status
    print("\nMigration status:")
    status = migrator.get_migration_status(job_id)
    if status:
        print(f"Job ID: {status['job_id']}")
        print(f"Status: {status['status']}")
        print(f"Progress: {status['completed_files']}/{status['total_files']} files")


def example_list_migrations():
    """List all migration jobs"""
    
    print("\n=== List All Migrations ===\n")
    
    migrator = HadoopToCloudMigration(
        target_platform='s3',
        checkpoint_dir='/tmp/migration_checkpoints'
    )
    
    migrations = migrator.list_migrations()
    
    if not migrations:
        print("No migrations found")
        return
    
    print(f"Found {len(migrations)} migrations:\n")
    print("-" * 100)
    print(f"{'Job ID':<40} {'Status':<15} {'Source':<25} {'Records':<15}")
    print("-" * 100)
    
    for migration in migrations:
        job_id = migration.get('job_id', 'N/A')[:40]
        status = migration.get('status', 'N/A')
        source = migration.get('source_path', 'N/A')[:25]
        records = migration.get('metadata', {}).get('record_count', 'N/A')
        
        print(f"{job_id:<40} {status:<15} {source:<25} {records:<15}")
    
    print("-" * 100)


if __name__ == '__main__':
    # Run examples
    # Note: These examples require proper configuration and running Hadoop/Spark cluster
    
    print("Hadoop to Cloud Migration Examples")
    print("=" * 80)
    
    # Uncomment the examples you want to run:
    
    # example_hdfs_to_s3()
    # example_hive_table_migration()
    # example_multiple_tables_migration()
    # example_hdfs_to_adls()
    # example_incremental_migration()
    # example_list_migrations()
    
    print("\n" + "=" * 80)
    print("Examples completed!")
    print("\nNote: Uncomment the example functions in __main__ to run them.")
    print("Make sure to configure environment variables and have proper access to:")
    print("  - Hadoop/HDFS cluster")
    print("  - Hive metastore")
    print("  - AWS S3 or Azure ADLS")
    print("  - Spark cluster")
