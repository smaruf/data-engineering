"""
Data Migration Modules

Provides comprehensive data migration capabilities:
- Hadoop to Cloud (HDFS/Hive to S3/ADLS)
- Cross-cloud migrations (Azure <-> AWS)
- Incremental synchronization with CDC
"""

from .hadoop_to_cloud import HadoopToCloudMigration
from .azure_to_aws import AzureToAWSMigration
from .aws_to_azure import AWSToAzureMigration
from .incremental_sync import IncrementalSync

__all__ = [
    'HadoopToCloudMigration',
    'AzureToAWSMigration',
    'AWSToAzureMigration',
    'IncrementalSync',
]
