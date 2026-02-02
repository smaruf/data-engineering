# Data Migration Modules

Comprehensive data migration modules for moving data between on-premise Hadoop and cloud platforms (AWS S3, Azure ADLS), as well as cross-cloud migrations.

## Overview

The migration package provides production-ready modules for:

1. **Hadoop to Cloud** - Migrate HDFS/Hive to S3 or ADLS
2. **Azure to AWS** - Migrate ADLS to S3
3. **AWS to Azure** - Migrate S3 to ADLS
4. **Incremental Sync** - CDC patterns for incremental synchronization

## Modules

### 1. HadoopToCloudMigration

Migrate data from on-premise Hadoop (HDFS/Hive) to cloud storage.

#### Features
- HDFS to S3/ADLS migration
- Hive table migration with schema preservation
- Parallel migration of multiple tables
- Checkpointing for resume capability
- Full and incremental sync modes
- Support for Delta, Parquet, CSV, JSON formats

#### Usage

```python
from src.migration import HadoopToCloudMigration

# Initialize migrator for S3
migrator = HadoopToCloudMigration(
    target_platform='s3',
    checkpoint_dir='/tmp/migration_checkpoints',
    max_workers=10
)

# Migrate HDFS directory to S3
result = migrator.migrate_hdfs_to_cloud(
    hdfs_path='hdfs://namenode:9000/data/sales',
    cloud_path='s3://my-bucket/sales',
    sync_mode='full',
    file_format='delta',
    compression='snappy',
    partition_cols=['year', 'month']
)

print(f"Migrated {result['records_migrated']} records")

# Migrate Hive table to S3
result = migrator.migrate_hive_table(
    database='sales_db',
    table='transactions',
    cloud_path='s3://my-bucket/sales/transactions',
    file_format='delta',
    partition_cols=['year', 'month', 'day']
)

# Migrate multiple tables in parallel
tables = [
    {'database': 'sales_db', 'table': 'transactions'},
    {'database': 'sales_db', 'table': 'customers'},
    {'database': 'sales_db', 'table': 'products'}
]

results = migrator.migrate_multiple_tables(
    tables=tables,
    base_cloud_path='s3://my-bucket/warehouse',
    file_format='delta',
    parallel=True
)
```

#### Resume from Checkpoint

```python
# Resume failed migration
result = migrator.migrate_hdfs_to_cloud(
    hdfs_path='hdfs://namenode:9000/data/sales',
    cloud_path='s3://my-bucket/sales',
    job_id='hdfs_migration_20240202_120000',  # Use previous job ID
    resume=True
)
```

### 2. AzureToAWSMigration

Migrate data from Azure ADLS to AWS S3.

#### Features
- Spark-based data migration with transformations
- Direct file transfer for large files
- Schema and metadata preservation
- Parallel transfers
- Container to bucket migration

#### Usage

```python
from src.migration import AzureToAWSMigration

migrator = AzureToAWSMigration(
    max_workers=10,
    chunk_size=100 * 1024 * 1024  # 100MB chunks
)

# Migrate data with Spark (supports transformations)
result = migrator.migrate_data(
    adls_path='abfss://container@account.dfs.core.windows.net/data/sales',
    s3_path='s3://my-bucket/sales',
    file_format='parquet',
    partition_cols=['year', 'month']
)

# Direct file transfer (no Spark)
result = migrator.migrate_files_direct(
    adls_container='my-container',
    adls_path='data/sales',
    s3_bucket='my-bucket',
    s3_prefix='sales',
    file_pattern='*.parquet',
    parallel=True
)

# Migrate entire container
result = migrator.migrate_container(
    adls_container='my-container',
    s3_bucket='my-bucket',
    prefix_mapping={
        'raw/': 'bronze/',
        'processed/': 'silver/'
    },
    parallel=True
)
```

#### With Transformation

```python
def transform_data(df):
    """Custom transformation function"""
    from pyspark.sql.functions import col, upper
    return df.withColumn('country', upper(col('country')))

result = migrator.migrate_data(
    adls_path='abfss://container@account.dfs.core.windows.net/data/sales',
    s3_path='s3://my-bucket/sales',
    file_format='delta',
    transformation_func=transform_data
)
```

### 3. AWSToAzureMigration

Migrate data from AWS S3 to Azure ADLS.

#### Features
- S3 to ADLS data transfer
- Spark-based processing
- Schema and metadata preservation
- Bucket to container migration
- Parallel processing

#### Usage

```python
from src.migration import AWSToAzureMigration

migrator = AWSToAzureMigration(max_workers=10)

# Migrate data with Spark
result = migrator.migrate_data(
    s3_path='s3://my-bucket/sales',
    adls_path='abfss://container@account.dfs.core.windows.net/data/sales',
    file_format='delta',
    partition_cols=['year', 'month']
)

# Direct file transfer
result = migrator.migrate_files_direct(
    s3_bucket='my-bucket',
    s3_prefix='sales',
    adls_container='my-container',
    adls_path='data/sales',
    file_pattern='*.parquet',
    parallel=True
)

# Migrate entire bucket
result = migrator.migrate_bucket(
    s3_bucket='my-bucket',
    adls_container='my-container',
    prefix_mapping={
        'bronze/': 'raw/',
        'silver/': 'processed/'
    }
)
```

### 4. IncrementalSync

Incremental data synchronization with CDC patterns.

#### Features
- Timestamp-based incremental updates
- Watermark tracking (Postgres, file, Delta storage)
- Delta Lake Change Data Feed support
- Multiple sync modes (append, upsert, merge, overwrite)
- Conflict resolution strategies
- Scheduled sync

#### Usage

```python
from src.migration import IncrementalSync
from src.migration.incremental_sync import SyncMode, ConflictResolution

# Initialize with Postgres watermark storage
sync = IncrementalSync(
    watermark_table='sync_watermarks',
    watermark_storage='postgres'
)

# Perform incremental sync
result = sync.sync_incremental(
    source_path='s3://source-bucket/data',
    target_path='s3://target-bucket/data',
    sync_id='sales_sync',
    timestamp_column='updated_at',
    key_columns=['id'],
    sync_mode=SyncMode.UPSERT,
    conflict_resolution=ConflictResolution.LATEST_TIMESTAMP,
    source_format='delta',
    target_format='delta'
)

print(f"Synced {result['records_synced']} records")
```

#### Delta Lake Change Data Feed

```python
# Sync using Delta Change Data Feed
result = sync.sync_with_cdf(
    source_delta_table='s3://source-bucket/sales_delta',
    target_path='s3://target-bucket/sales_delta',
    sync_id='sales_cdf_sync',
    key_columns=['id']
)

print(f"Inserts: {result['inserts']}, Updates: {result['updates']}, Deletes: {result['deletes']}")
```

#### Scheduled Sync

```python
# Run scheduled sync every 60 minutes
results = sync.scheduled_sync(
    source_path='s3://source-bucket/data',
    target_path='s3://target-bucket/data',
    sync_id='hourly_sync',
    interval_minutes=60,
    max_iterations=24,  # Run for 24 hours
    timestamp_column='updated_at',
    key_columns=['id'],
    sync_mode=SyncMode.UPSERT
)
```

#### Custom Filter Function

```python
from datetime import datetime, timedelta

def custom_filter(df, last_watermark):
    """Custom incremental filter"""
    from pyspark.sql.functions import col
    
    # Get records from last 7 days only
    cutoff = datetime.now() - timedelta(days=7)
    if last_watermark:
        cutoff = max(cutoff, last_watermark)
    
    return df.filter(col('created_at') > cutoff)

result = sync.sync_incremental(
    source_path='s3://source-bucket/data',
    target_path='s3://target-bucket/data',
    sync_id='custom_sync',
    custom_filter=custom_filter,
    sync_mode=SyncMode.APPEND
)
```

## Configuration

All modules use the shared configuration system. Set the following environment variables:

### AWS Configuration
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
export AWS_S3_BUCKET=your-bucket
```

### Azure Configuration
```bash
export AZURE_STORAGE_ACCOUNT_NAME=your_account
export AZURE_STORAGE_ACCOUNT_KEY=your_key
export AZURE_CONTAINER_NAME=your-container
export AZURE_ADLS_GEN2_ENDPOINT=https://your_account.dfs.core.windows.net
```

### Hadoop Configuration
```bash
export HADOOP_NAMENODE_HOST=namenode.example.com
export HADOOP_NAMENODE_PORT=9000
export HADOOP_USER=hadoop
export HIVE_SERVER_HOST=hive.example.com
export HIVE_SERVER_PORT=10000
```

### Spark Configuration
```bash
export SPARK_MASTER=yarn
export SPARK_EXECUTOR_MEMORY=4g
export SPARK_EXECUTOR_CORES=2
export SPARK_DRIVER_MEMORY=2g
```

## Best Practices

### 1. Checkpointing
Always use checkpointing for large migrations to enable resume on failure:

```python
migrator = HadoopToCloudMigration(checkpoint_dir='/data/checkpoints')

result = migrator.migrate_hdfs_to_cloud(
    hdfs_path='hdfs://namenode:9000/large_dataset',
    cloud_path='s3://bucket/large_dataset',
    job_id='large_migration_job',
    resume=True  # Enable resume
)
```

### 2. Parallel Processing
Use parallel processing for multiple tables or files:

```python
# Parallel table migration
migrator.migrate_multiple_tables(
    tables=table_list,
    base_cloud_path='s3://bucket/warehouse',
    parallel=True
)

# Parallel file transfers
migrator.migrate_files_direct(
    adls_container='container',
    s3_bucket='bucket',
    parallel=True
)
```

### 3. Incremental Syncs
Use incremental syncs to minimize data transfer:

```python
sync = IncrementalSync(watermark_storage='postgres')

# First sync - full load
result = sync.sync_incremental(
    source_path='s3://source/data',
    target_path='s3://target/data',
    sync_id='my_sync',
    timestamp_column='updated_at',
    key_columns=['id'],
    sync_mode=SyncMode.UPSERT
)

# Subsequent syncs - incremental only
# Automatically uses watermark from previous sync
result = sync.sync_incremental(
    source_path='s3://source/data',
    target_path='s3://target/data',
    sync_id='my_sync',
    timestamp_column='updated_at',
    key_columns=['id'],
    sync_mode=SyncMode.UPSERT
)
```

### 4. Schema Preservation
Schemas are automatically saved as JSON:

```python
result = migrator.migrate_hive_table(
    database='sales_db',
    table='transactions',
    cloud_path='s3://bucket/transactions'
)

# Schema saved to: s3://bucket/transactions/_schema.json
```

### 5. Error Handling
All modules include comprehensive error handling and logging:

```python
import logging
from shared.utils.logger import get_logger

# Set log level
logger = get_logger(__name__, log_level='DEBUG')

try:
    result = migrator.migrate_data(...)
except Exception as e:
    logger.error(f"Migration failed: {e}")
    # Handle error appropriately
```

## Monitoring and Tracking

### Get Migration Status

```python
# HadoopToCloudMigration
status = migrator.get_migration_status('job_id')
print(f"Status: {status['status']}")
print(f"Progress: {status['completed_files']}/{status['total_files']}")

# IncrementalSync
status = sync.get_sync_status('sync_id')
print(f"Last watermark: {status['last_watermark']}")
```

### List All Jobs

```python
# List all migrations
migrations = migrator.list_migrations()
for migration in migrations:
    print(f"{migration['job_id']}: {migration['status']}")

# List all syncs
syncs = sync.list_syncs()
for s in syncs:
    print(f"{s['sync_id']}: {s['last_watermark']}")
```

## Performance Tips

1. **Partition Data**: Use partition columns for better query performance
2. **Use Delta Format**: Delta Lake provides ACID transactions and time travel
3. **Adjust Parallelism**: Tune `max_workers` based on your cluster size
4. **Compression**: Use `snappy` for balance of speed and compression
5. **Batch Size**: Adjust batch sizes for optimal throughput
6. **Resource Allocation**: Configure Spark executor memory and cores appropriately

## Troubleshooting

### Common Issues

#### 1. Out of Memory Errors
```python
# Reduce parallelism
migrator = HadoopToCloudMigration(max_workers=5)

# Or increase Spark memory
export SPARK_EXECUTOR_MEMORY=8g
export SPARK_DRIVER_MEMORY=4g
```

#### 2. Connection Timeouts
```python
# Increase retry logic in shared/utils/connection_manager.py
# Or check network connectivity
```

#### 3. Schema Mismatch
```python
# Enforce schema during read
df = spark.read.schema(expected_schema).parquet(path)
```

#### 4. Checkpoint Recovery Failed
```python
# Start fresh migration without resume
result = migrator.migrate_hdfs_to_cloud(
    ...,
    job_id='new_job_id',  # New job ID
    resume=False
)
```

## Examples

See the `examples/` directory for complete end-to-end examples:
- `examples/hadoop_migration_example.py`
- `examples/cross_cloud_migration_example.py`
- `examples/incremental_sync_example.py`

## Contributing

When adding new migration capabilities:
1. Follow existing patterns
2. Add comprehensive error handling
3. Include progress tracking
4. Update documentation
5. Add unit tests

## License

Part of the Data Fabric Platform project.
