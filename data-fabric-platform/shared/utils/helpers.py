"""
Helper utilities for Data Fabric Platform

Common utility functions used across the platform
"""

from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import datetime, date
from pathlib import Path
import re


def generate_id(data: str) -> str:
    """
    Generate a unique ID from string data
    
    Args:
        data: Input string
        
    Returns:
        MD5 hash of the input
    """
    return hashlib.md5(data.encode()).hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing special characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    return filename


def get_partition_path(base_path: str, partition_cols: Dict[str, Any]) -> str:
    """
    Generate Hive-style partition path
    
    Args:
        base_path: Base directory path
        partition_cols: Dictionary of partition column names and values
        
    Returns:
        Full partition path (e.g., /base/year=2024/month=01/day=15)
    """
    path = Path(base_path)
    
    for col, value in partition_cols.items():
        path = path / f"{col}={value}"
    
    return str(path)


def json_serializer(obj: Any) -> str:
    """
    JSON serializer for objects not serializable by default
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string representation
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def to_json(data: Any, pretty: bool = False) -> str:
    """
    Convert data to JSON string
    
    Args:
        data: Data to convert
        pretty: Whether to pretty-print
        
    Returns:
        JSON string
    """
    indent = 2 if pretty else None
    return json.dumps(data, default=json_serializer, indent=indent)


def from_json(json_str: str) -> Any:
    """
    Parse JSON string to Python object
    
    Args:
        json_str: JSON string
        
    Returns:
        Python object
    """
    return json.loads(json_str)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    return Path(file_path).stat().st_size / (1024 * 1024)


def ensure_dir(directory: str) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_timestamp(fmt: str = '%Y%m%d_%H%M%S') -> str:
    """
    Get current timestamp as string
    
    Args:
        fmt: Timestamp format
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(fmt)


def parse_connection_string(conn_str: str) -> Dict[str, str]:
    """
    Parse database connection string
    
    Args:
        conn_str: Connection string (e.g., "host=localhost;port=5432;db=mydb")
        
    Returns:
        Dictionary of connection parameters
    """
    parts = conn_str.split(';')
    return dict(part.split('=', 1) for part in parts if '=' in part)


def bytes_to_human_readable(num_bytes: int) -> str:
    """
    Convert bytes to human-readable format
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Human-readable string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def validate_s3_path(path: str) -> bool:
    """
    Validate S3 path format
    
    Args:
        path: S3 path (e.g., "s3://bucket/key")
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^s3[a]?://[a-z0-9.-]+/.+', path))


def validate_adls_path(path: str) -> bool:
    """
    Validate Azure Data Lake Storage path format
    
    Args:
        path: ADLS path (e.g., "abfss://container@account.dfs.core.windows.net/path")
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^abfss?://[a-z0-9-]+@[a-z0-9]+\.dfs\.core\.windows\.net/.+', path))


def validate_hdfs_path(path: str) -> bool:
    """
    Validate HDFS path format
    
    Args:
        path: HDFS path (e.g., "hdfs://namenode:9000/path")
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^hdfs://[a-z0-9.-]+:\d+/.+', path))


def get_platform_from_path(path: str) -> Optional[str]:
    """
    Determine platform from file path
    
    Args:
        path: File path
        
    Returns:
        Platform name ('s3', 'adls', 'hdfs', 'local') or None
    """
    if path.startswith('s3://') or path.startswith('s3a://'):
        return 's3'
    elif path.startswith('abfs://') or path.startswith('abfss://'):
        return 'adls'
    elif path.startswith('hdfs://'):
        return 'hdfs'
    elif path.startswith('/') or Path(path).is_absolute():
        return 'local'
    return None
