"""
Example: Cross-Cloud Migration

This example demonstrates migrating data between cloud platforms (Azure <-> AWS).
"""

from src.migration import AzureToAWSMigration, AWSToAzureMigration

def example_azure_to_aws_spark():
    """Migrate data from Azure ADLS to AWS S3 using Spark"""
    
    print("=== Azure ADLS to AWS S3 Migration (Spark) ===\n")
    
    migrator = AzureToAWSMigration(max_workers=10)
    
    # Migrate with Spark processing
    print("Migrating data with Spark processing...")
    result = migrator.migrate_data(
        adls_path='abfss://container@account.dfs.core.windows.net/data/sales',
        s3_path='s3://my-bucket/sales',
        file_format='delta',
        partition_cols=['year', 'month']
    )
    
    print(f"\nMigration completed!")
    print(f"Records migrated: {result['records_migrated']:,}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print(f"Schema saved to: {result['schema_path']}")


def example_azure_to_aws_direct():
    """Direct file transfer from ADLS to S3 (no Spark)"""
    
    print("\n=== Azure ADLS to AWS S3 Direct File Transfer ===\n")
    
    migrator = AzureToAWSMigration(max_workers=20)
    
    # Direct file transfer
    print("Transferring files directly...")
    result = migrator.migrate_files_direct(
        adls_container='my-container',
        adls_path='data/sales',
        s3_bucket='my-bucket',
        s3_prefix='sales',
        file_pattern='*.parquet',
        parallel=True
    )
    
    print(f"\nTransfer completed!")
    print(f"Files transferred: {result['files_transferred']}")
    print(f"Files failed: {result['files_failed']}")
    print(f"Total size: {result['total_bytes_readable']}")
    print(f"Throughput: {result['throughput_mbps']:.2f} MB/s")
    
    if result['failed_files']:
        print(f"\nFailed files:")
        for failed_file in result['failed_files']:
            print(f"  - {failed_file}")


def example_azure_to_aws_with_transformation():
    """Migrate with custom data transformation"""
    
    print("\n=== Azure to AWS with Data Transformation ===\n")
    
    migrator = AzureToAWSMigration()
    
    # Define transformation function
    def transform_sales_data(df):
        """Apply transformations to sales data"""
        from pyspark.sql.functions import col, upper, when
        
        # Convert country codes to uppercase
        df = df.withColumn('country_code', upper(col('country_code')))
        
        # Add region column based on country
        df = df.withColumn('region', 
            when(col('country_code').isin(['US', 'CA', 'MX']), 'NORTH_AMERICA')
            .when(col('country_code').isin(['GB', 'FR', 'DE', 'IT']), 'EUROPE')
            .when(col('country_code').isin(['JP', 'CN', 'IN', 'KR']), 'ASIA')
            .otherwise('OTHER')
        )
        
        return df
    
    print("Migrating with transformation...")
    result = migrator.migrate_data(
        adls_path='abfss://container@account.dfs.core.windows.net/data/sales',
        s3_path='s3://my-bucket/sales_transformed',
        file_format='delta',
        partition_cols=['region', 'year', 'month'],
        transformation_func=transform_sales_data
    )
    
    print(f"\nMigration with transformation completed!")
    print(f"Records migrated: {result['records_migrated']:,}")


def example_azure_container_to_s3_bucket():
    """Migrate entire Azure container to S3 bucket"""
    
    print("\n=== Migrate Entire Azure Container to S3 Bucket ===\n")
    
    migrator = AzureToAWSMigration(max_workers=20)
    
    # Define prefix mapping (optional)
    prefix_mapping = {
        'raw/': 'bronze/',
        'processed/': 'silver/',
        'curated/': 'gold/'
    }
    
    print("Migrating entire container with prefix mapping...")
    result = migrator.migrate_container(
        adls_container='my-container',
        s3_bucket='my-bucket',
        prefix_mapping=prefix_mapping,
        parallel=True
    )
    
    print(f"\nContainer migration completed!")
    print(f"Files transferred: {result['files_transferred']}")
    print(f"Files failed: {result['files_failed']}")
    print(f"Total size: {result['total_bytes']:,} bytes")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")


def example_aws_to_azure_spark():
    """Migrate data from AWS S3 to Azure ADLS using Spark"""
    
    print("\n=== AWS S3 to Azure ADLS Migration (Spark) ===\n")
    
    migrator = AWSToAzureMigration(max_workers=10)
    
    # Migrate with Spark
    print("Migrating data with Spark processing...")
    result = migrator.migrate_data(
        s3_path='s3://my-bucket/sales',
        adls_path='abfss://container@account.dfs.core.windows.net/data/sales',
        file_format='delta',
        partition_cols=['year', 'month']
    )
    
    print(f"\nMigration completed!")
    print(f"Records migrated: {result['records_migrated']:,}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")


def example_aws_to_azure_direct():
    """Direct file transfer from S3 to ADLS"""
    
    print("\n=== AWS S3 to Azure ADLS Direct File Transfer ===\n")
    
    migrator = AWSToAzureMigration(max_workers=20)
    
    # Direct file transfer
    print("Transferring files directly...")
    result = migrator.migrate_files_direct(
        s3_bucket='my-bucket',
        s3_prefix='sales',
        adls_container='my-container',
        adls_path='data/sales',
        file_pattern='*.parquet',
        parallel=True
    )
    
    print(f"\nTransfer completed!")
    print(f"Files transferred: {result['files_transferred']}")
    print(f"Total size: {result['total_bytes_readable']}")
    print(f"Throughput: {result['throughput_mbps']:.2f} MB/s")


def example_aws_bucket_to_azure_container():
    """Migrate entire S3 bucket to Azure container"""
    
    print("\n=== Migrate Entire S3 Bucket to Azure Container ===\n")
    
    migrator = AWSToAzureMigration(max_workers=20)
    
    # Define prefix mapping
    prefix_mapping = {
        'bronze/': 'raw/',
        'silver/': 'processed/',
        'gold/': 'curated/'
    }
    
    print("Migrating entire bucket with prefix mapping...")
    result = migrator.migrate_bucket(
        s3_bucket='my-bucket',
        adls_container='my-container',
        prefix_mapping=prefix_mapping,
        parallel=True
    )
    
    print(f"\nBucket migration completed!")
    print(f"Files transferred: {result['files_transferred']}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")


def example_bidirectional_sync():
    """Example of bi-directional sync between Azure and AWS"""
    
    print("\n=== Bi-Directional Sync (Azure <-> AWS) ===\n")
    
    # Azure to AWS migrator
    azure_to_aws = AzureToAWSMigration()
    
    # AWS to Azure migrator
    aws_to_azure = AWSToAzureMigration()
    
    # Sync from Azure to AWS
    print("Step 1: Syncing Azure -> AWS...")
    result1 = azure_to_aws.migrate_data(
        adls_path='abfss://container@account.dfs.core.windows.net/data/master',
        s3_path='s3://my-bucket/master_backup',
        file_format='delta'
    )
    print(f"Azure -> AWS: {result1['records_migrated']:,} records")
    
    # Sync from AWS to Azure
    print("\nStep 2: Syncing AWS -> Azure...")
    result2 = aws_to_azure.migrate_data(
        s3_path='s3://my-bucket/master_backup',
        adls_path='abfss://container@account.dfs.core.windows.net/data/master_restored',
        file_format='delta'
    )
    print(f"AWS -> Azure: {result2['records_migrated']:,} records")
    
    print("\nBi-directional sync completed!")


def example_multi_cloud_backup():
    """Example of multi-cloud backup strategy"""
    
    print("\n=== Multi-Cloud Backup Strategy ===\n")
    
    azure_to_aws = AzureToAWSMigration(max_workers=15)
    
    # Backup critical datasets from Azure to AWS
    critical_datasets = [
        {
            'name': 'customer_data',
            'source': 'abfss://prod@account.dfs.core.windows.net/customers',
            'target': 's3://backup-bucket/customers'
        },
        {
            'name': 'transactions',
            'source': 'abfss://prod@account.dfs.core.windows.net/transactions',
            'target': 's3://backup-bucket/transactions'
        },
        {
            'name': 'analytics',
            'source': 'abfss://prod@account.dfs.core.windows.net/analytics',
            'target': 's3://backup-bucket/analytics'
        }
    ]
    
    print(f"Backing up {len(critical_datasets)} critical datasets to AWS...\n")
    
    results = []
    for dataset in critical_datasets:
        print(f"Backing up {dataset['name']}...")
        try:
            result = azure_to_aws.migrate_data(
                adls_path=dataset['source'],
                s3_path=dataset['target'],
                file_format='delta'
            )
            results.append({
                'dataset': dataset['name'],
                'status': 'success',
                'records': result['records_migrated']
            })
            print(f"  ✓ Backed up {result['records_migrated']:,} records")
        except Exception as e:
            results.append({
                'dataset': dataset['name'],
                'status': 'failed',
                'error': str(e)
            })
            print(f"  ✗ Failed: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Backup Summary:")
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Successful: {successful}/{len(results)}")
    
    for result in results:
        if result['status'] == 'success':
            print(f"  ✓ {result['dataset']}: {result['records']:,} records")
        else:
            print(f"  ✗ {result['dataset']}: {result['error']}")


if __name__ == '__main__':
    print("Cross-Cloud Migration Examples")
    print("=" * 80)
    
    # Uncomment the examples you want to run:
    
    # Azure to AWS examples
    # example_azure_to_aws_spark()
    # example_azure_to_aws_direct()
    # example_azure_to_aws_with_transformation()
    # example_azure_container_to_s3_bucket()
    
    # AWS to Azure examples
    # example_aws_to_azure_spark()
    # example_aws_to_azure_direct()
    # example_aws_bucket_to_azure_container()
    
    # Advanced examples
    # example_bidirectional_sync()
    # example_multi_cloud_backup()
    
    print("\n" + "=" * 80)
    print("Examples completed!")
    print("\nNote: Uncomment the example functions in __main__ to run them.")
    print("Make sure to configure environment variables and have proper access to:")
    print("  - Azure ADLS Gen2")
    print("  - AWS S3")
    print("  - Spark cluster (for Spark-based migrations)")
