"""
Connection manager for various data sources

Manages connections to:
- Azure (ADLS, Databricks, Synapse)
- AWS (S3, Glue, EMR, Redshift)
- Hadoop (HDFS, Hive)
- Databases (PostgreSQL, MongoDB)
"""

from typing import Optional, Dict, Any
from contextlib import contextmanager
import boto3
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import ClientSecretCredential
from pyspark.sql import SparkSession
from shared.utils.config_loader import config
from shared.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages connections to various data platforms"""
    
    def __init__(self):
        self._spark_session: Optional[SparkSession] = None
        self._azure_client: Optional[DataLakeServiceClient] = None
        self._aws_session: Optional[boto3.Session] = None
    
    @property
    def spark(self) -> SparkSession:
        """
        Get or create Spark session
        
        Returns:
            SparkSession instance
        """
        if self._spark_session is None:
            spark_config = config.get_spark_config()
            
            builder = SparkSession.builder \
                .appName(spark_config['app_name']) \
                .master(spark_config['master'])
            
            # Configure Spark
            builder = builder \
                .config("spark.executor.memory", spark_config['executor_memory']) \
                .config("spark.executor.cores", spark_config['executor_cores']) \
                .config("spark.driver.memory", spark_config['driver_memory']) \
                .config("spark.sql.shuffle.partitions", spark_config['shuffle_partitions']) \
                .config("spark.sql.adaptive.enabled", spark_config['adaptive_enabled'])
            
            # Delta Lake configuration
            if config.get_env_bool('DELTA_LAKE_ENABLED', True):
                builder = builder \
                    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
                    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            
            # Azure configuration
            if config.get_env_bool('ENABLE_AZURE', True):
                azure_conf = config.get_azure_config()
                if azure_conf.get('storage_account'):
                    builder = builder.config(
                        f"fs.azure.account.key.{azure_conf['storage_account']}.dfs.core.windows.net",
                        azure_conf['storage_key']
                    )
            
            # AWS configuration
            if config.get_env_bool('ENABLE_AWS', True):
                aws_conf = config.get_aws_config()
                if aws_conf.get('access_key_id'):
                    builder = builder \
                        .config("spark.hadoop.fs.s3a.access.key", aws_conf['access_key_id']) \
                        .config("spark.hadoop.fs.s3a.secret.key", aws_conf['secret_access_key']) \
                        .config("spark.hadoop.fs.s3a.endpoint", f"s3.{aws_conf['region']}.amazonaws.com")
            
            self._spark_session = builder.getOrCreate()
            logger.info(f"Spark session created: {spark_config['app_name']}")
        
        return self._spark_session
    
    def get_azure_client(self) -> DataLakeServiceClient:
        """
        Get Azure Data Lake Storage client
        
        Returns:
            DataLakeServiceClient instance
        """
        if self._azure_client is None:
            azure_conf = config.get_azure_config()
            
            if azure_conf.get('client_id'):
                # Service Principal authentication
                credential = ClientSecretCredential(
                    tenant_id=azure_conf['tenant_id'],
                    client_id=azure_conf['client_id'],
                    client_secret=azure_conf['client_secret']
                )
                self._azure_client = DataLakeServiceClient(
                    account_url=azure_conf['adls_endpoint'],
                    credential=credential
                )
            else:
                # Account key authentication
                self._azure_client = DataLakeServiceClient(
                    account_url=azure_conf['adls_endpoint'],
                    credential=azure_conf['storage_key']
                )
            
            logger.info("Azure ADLS client created")
        
        return self._azure_client
    
    def get_aws_session(self) -> boto3.Session:
        """
        Get AWS session
        
        Returns:
            boto3.Session instance
        """
        if self._aws_session is None:
            aws_conf = config.get_aws_config()
            
            self._aws_session = boto3.Session(
                aws_access_key_id=aws_conf['access_key_id'],
                aws_secret_access_key=aws_conf['secret_access_key'],
                region_name=aws_conf['region']
            )
            
            logger.info(f"AWS session created for region: {aws_conf['region']}")
        
        return self._aws_session
    
    def get_s3_client(self):
        """Get AWS S3 client"""
        return self.get_aws_session().client('s3')
    
    def get_glue_client(self):
        """Get AWS Glue client"""
        return self.get_aws_session().client('glue')
    
    def get_emr_client(self):
        """Get AWS EMR client"""
        return self.get_aws_session().client('emr')
    
    @contextmanager
    def hdfs_connection(self):
        """
        Context manager for HDFS connection
        
        Yields:
            HDFS client
        """
        from hdfs import InsecureClient
        
        hadoop_conf = config.get_hadoop_config()
        
        client = InsecureClient(
            f"http://{hadoop_conf['namenode_host']}:{hadoop_conf.get('webhdfs_port', 50070)}",
            user=hadoop_conf['user']
        )
        
        try:
            logger.info("HDFS connection established")
            yield client
        finally:
            logger.info("HDFS connection closed")
    
    @contextmanager
    def database_connection(self, db_type: str = 'postgres'):
        """
        Context manager for database connection
        
        Args:
            db_type: Database type ('postgres' or 'mongodb')
            
        Yields:
            Database connection
        """
        import sqlalchemy
        from pymongo import MongoClient
        
        db_config = config.get_database_config()
        
        if db_type == 'postgres':
            conn_str = (
                f"postgresql://{db_config['postgres']['user']}:{db_config['postgres']['password']}"
                f"@{db_config['postgres']['host']}:{db_config['postgres']['port']}"
                f"/{db_config['postgres']['database']}"
            )
            engine = sqlalchemy.create_engine(conn_str)
            conn = engine.connect()
            try:
                logger.info("PostgreSQL connection established")
                yield conn
            finally:
                conn.close()
                logger.info("PostgreSQL connection closed")
        
        elif db_type == 'mongodb':
            mongo_conf = db_config['mongodb']
            client = MongoClient(
                host=mongo_conf['host'],
                port=mongo_conf['port'],
                username=mongo_conf.get('user'),
                password=mongo_conf.get('password')
            )
            try:
                logger.info("MongoDB connection established")
                yield client[mongo_conf['database']]
            finally:
                client.close()
                logger.info("MongoDB connection closed")
    
    def stop_spark(self):
        """Stop Spark session"""
        if self._spark_session:
            self._spark_session.stop()
            self._spark_session = None
            logger.info("Spark session stopped")


# Global connection manager instance
connections = ConnectionManager()
