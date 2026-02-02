"""
Configuration loader for Data Fabric Platform

This module provides utilities to load and manage configuration from:
- Environment variables
- YAML configuration files
- .env files
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Configuration loader with multi-source support"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration loader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / "config"
        self.config_cache: Dict[str, Any] = {}
        
        # Load environment variables
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get environment variable
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    def get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = self.get_env(key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_env_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable"""
        try:
            return int(self.get_env(key, default))
        except (ValueError, TypeError):
            return default
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration file
        
        Args:
            filename: YAML filename (without path)
            
        Returns:
            Configuration dictionary
        """
        if filename in self.config_cache:
            return self.config_cache[filename]
        
        config_path = self.config_dir / filename
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config_cache[filename] = config
        return config
    
    def get_azure_config(self) -> Dict[str, Any]:
        """Get Azure configuration"""
        return {
            'storage_account': self.get_env('AZURE_STORAGE_ACCOUNT_NAME'),
            'storage_key': self.get_env('AZURE_STORAGE_ACCOUNT_KEY'),
            'container_name': self.get_env('AZURE_CONTAINER_NAME'),
            'adls_endpoint': self.get_env('AZURE_ADLS_GEN2_ENDPOINT'),
            'subscription_id': self.get_env('AZURE_SUBSCRIPTION_ID'),
            'resource_group': self.get_env('AZURE_RESOURCE_GROUP'),
            'tenant_id': self.get_env('AZURE_TENANT_ID'),
            'client_id': self.get_env('AZURE_CLIENT_ID'),
            'client_secret': self.get_env('AZURE_CLIENT_SECRET'),
        }
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration"""
        return {
            'access_key_id': self.get_env('AWS_ACCESS_KEY_ID'),
            'secret_access_key': self.get_env('AWS_SECRET_ACCESS_KEY'),
            'region': self.get_env('AWS_DEFAULT_REGION', 'us-east-1'),
            'account_id': self.get_env('AWS_ACCOUNT_ID'),
            's3_bucket': self.get_env('AWS_S3_BUCKET'),
        }
    
    def get_hadoop_config(self) -> Dict[str, Any]:
        """Get Hadoop configuration"""
        return {
            'namenode_host': self.get_env('HADOOP_NAMENODE_HOST'),
            'namenode_port': self.get_env_int('HADOOP_NAMENODE_PORT', 9000),
            'user': self.get_env('HADOOP_USER', 'hadoop'),
            'hdfs_base_path': self.get_env('HDFS_BASE_PATH', '/data-fabric'),
            'hive_host': self.get_env('HIVE_SERVER_HOST'),
            'hive_port': self.get_env_int('HIVE_SERVER_PORT', 10000),
        }
    
    def get_spark_config(self) -> Dict[str, Any]:
        """Get Spark configuration"""
        return {
            'master': self.get_env('SPARK_MASTER', 'local[*]'),
            'app_name': self.get_env('SPARK_APP_NAME', 'DataFabricPlatform'),
            'executor_memory': self.get_env('SPARK_EXECUTOR_MEMORY', '4g'),
            'executor_cores': self.get_env_int('SPARK_EXECUTOR_CORES', 2),
            'driver_memory': self.get_env('SPARK_DRIVER_MEMORY', '2g'),
            'shuffle_partitions': self.get_env_int('SPARK_SHUFFLE_PARTITIONS', 200),
            'adaptive_enabled': self.get_env_bool('SPARK_SQL_ADAPTIVE_ENABLED', True),
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'postgres': {
                'host': self.get_env('POSTGRES_HOST', 'localhost'),
                'port': self.get_env_int('POSTGRES_PORT', 5432),
                'database': self.get_env('POSTGRES_DATABASE', 'data_fabric_metadata'),
                'user': self.get_env('POSTGRES_USER', 'postgres'),
                'password': self.get_env('POSTGRES_PASSWORD', 'postgres'),
            },
            'mongodb': {
                'host': self.get_env('MONGODB_HOST', 'localhost'),
                'port': self.get_env_int('MONGODB_PORT', 27017),
                'database': self.get_env('MONGODB_DATABASE', 'data_catalog'),
                'user': self.get_env('MONGODB_USER'),
                'password': self.get_env('MONGODB_PASSWORD'),
            }
        }


# Global config instance
config = ConfigLoader()
