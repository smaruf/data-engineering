"""
Azure Data Lake Storage Gen2 Operations

This module demonstrates working with Azure Data Lake Storage Gen2 (ADLS Gen2),
which provides hierarchical namespace capabilities on top of Blob Storage.

Requirements:
    pip install azure-identity azure-storage-file-datalake

Environment Variables:
    AZURE_STORAGE_ACCOUNT_NAME: Storage account name (with HNS enabled)
    AZURE_STORAGE_ACCOUNT_KEY: Storage account key (or use DefaultAzureCredential)
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import io

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    DataLakeFileClient,
    FileSystemClient,
    ContentSettings
)
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
    AzureError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataLakeGen2Manager:
    """
    Manages Azure Data Lake Storage Gen2 operations.
    
    ADLS Gen2 combines the power of a high-performance file system with the
    massive scale of Azure Blob Storage, designed for big data analytics.
    """
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None
    ):
        """
        Initialize Data Lake Gen2 Manager.
        
        Args:
            account_name: Storage account name
            account_key: Storage account key (optional, uses DefaultAzureCredential if not provided)
        
        Note:
            The storage account must have hierarchical namespace enabled.
        """
        self.account_name = account_name or os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        
        if not self.account_name:
            raise ValueError(
                "Storage account name required. "
                "Set AZURE_STORAGE_ACCOUNT_NAME environment variable."
            )
        
        account_url = f"https://{self.account_name}.dfs.core.windows.net"
        
        if account_key or os.getenv('AZURE_STORAGE_ACCOUNT_KEY'):
            # Use account key
            key = account_key or os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
            self.service_client = DataLakeServiceClient(
                account_url=account_url,
                credential=key
            )
            logger.info(f"Initialized with account key for: {self.account_name}")
        else:
            # Use DefaultAzureCredential (recommended)
            credential = DefaultAzureCredential()
            self.service_client = DataLakeServiceClient(
                account_url=account_url,
                credential=credential
            )
            logger.info(f"Initialized with DefaultAzureCredential for: {self.account_name}")
    
    def create_file_system(
        self,
        file_system_name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> FileSystemClient:
        """
        Create a file system (container) in ADLS Gen2.
        
        Args:
            file_system_name: Name of the file system
            metadata: Optional metadata key-value pairs
        
        Returns:
            FileSystemClient instance
        """
        try:
            logger.info(f"Creating file system: {file_system_name}")
            
            file_system_client = self.service_client.create_file_system(
                file_system=file_system_name,
                metadata=metadata
            )
            
            logger.info(f"Successfully created file system: {file_system_name}")
            return file_system_client
            
        except ResourceExistsError:
            logger.warning(f"File system already exists: {file_system_name}")
            return self.service_client.get_file_system_client(file_system_name)
            
        except AzureError as e:
            logger.error(f"Failed to create file system: {e}")
            raise
    
    def create_directory(
        self,
        file_system_name: str,
        directory_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> DataLakeDirectoryClient:
        """
        Create a directory in ADLS Gen2.
        
        Args:
            file_system_name: File system name
            directory_path: Directory path (e.g., 'data/raw/2024')
            metadata: Optional metadata
        
        Returns:
            DataLakeDirectoryClient instance
        """
        try:
            logger.info(f"Creating directory: {directory_path} in {file_system_name}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            directory_client = file_system_client.create_directory(
                directory=directory_path,
                metadata=metadata
            )
            
            logger.info(f"Successfully created directory: {directory_path}")
            return directory_client
            
        except ResourceExistsError:
            logger.warning(f"Directory already exists: {directory_path}")
            return file_system_client.get_directory_client(directory_path)
            
        except AzureError as e:
            logger.error(f"Failed to create directory: {e}")
            raise
    
    def upload_file(
        self,
        file_system_name: str,
        file_path: str,
        local_file: str,
        overwrite: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to ADLS Gen2.
        
        Args:
            file_system_name: File system name
            file_path: Destination path in ADLS (e.g., 'data/file.csv')
            local_file: Local file path to upload
            overwrite: Whether to overwrite existing file
            metadata: Optional metadata
        
        Returns:
            Upload result details
        """
        try:
            logger.info(f"Uploading file: {local_file} to {file_path}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            file_client = file_system_client.get_file_client(file_path)
            
            # Read local file
            with open(local_file, 'rb') as data:
                file_contents = data.read()
            
            # Upload file
            file_client.upload_data(
                data=file_contents,
                overwrite=overwrite,
                metadata=metadata
            )
            
            logger.info(f"Successfully uploaded file: {file_path}")
            
            return {
                'file_system': file_system_name,
                'file_path': file_path,
                'size': len(file_contents),
                'url': file_client.url
            }
            
        except FileNotFoundError:
            logger.error(f"Local file not found: {local_file}")
            raise
            
        except AzureError as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def upload_data(
        self,
        file_system_name: str,
        file_path: str,
        data: bytes,
        overwrite: bool = True,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload data directly to ADLS Gen2.
        
        Args:
            file_system_name: File system name
            file_path: Destination path
            data: Data to upload
            overwrite: Whether to overwrite
            content_type: MIME type
            metadata: Optional metadata
        
        Returns:
            Upload result details
        """
        try:
            logger.info(f"Uploading data to: {file_path}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            file_client = file_system_client.get_file_client(file_path)
            
            # Set content settings
            content_settings = None
            if content_type:
                content_settings = ContentSettings(content_type=content_type)
            
            # Upload data
            file_client.upload_data(
                data=data,
                overwrite=overwrite,
                metadata=metadata,
                content_settings=content_settings
            )
            
            logger.info(f"Successfully uploaded {len(data)} bytes")
            
            return {
                'file_system': file_system_name,
                'file_path': file_path,
                'size': len(data),
                'url': file_client.url
            }
            
        except AzureError as e:
            logger.error(f"Failed to upload data: {e}")
            raise
    
    def download_file(
        self,
        file_system_name: str,
        file_path: str,
        local_file: Optional[str] = None
    ) -> bytes:
        """
        Download a file from ADLS Gen2.
        
        Args:
            file_system_name: File system name
            file_path: File path in ADLS
            local_file: Optional local path to save file
        
        Returns:
            File content as bytes
        """
        try:
            logger.info(f"Downloading file: {file_path}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            file_client = file_system_client.get_file_client(file_path)
            
            # Download file
            download = file_client.download_file()
            file_contents = download.readall()
            
            # Save to local file if specified
            if local_file:
                local_path = Path(local_file)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(local_path, 'wb') as f:
                    f.write(file_contents)
                
                logger.info(f"Saved to: {local_path}")
            
            logger.info(f"Downloaded {len(file_contents)} bytes")
            return file_contents
            
        except ResourceNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
            
        except AzureError as e:
            logger.error(f"Failed to download file: {e}")
            raise
    
    def list_paths(
        self,
        file_system_name: str,
        path: Optional[str] = None,
        recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List files and directories in a file system.
        
        Args:
            file_system_name: File system name
            path: Starting path (None for root)
            recursive: Whether to list recursively
        
        Returns:
            List of path details
        """
        try:
            logger.info(f"Listing paths in: {file_system_name}/{path or 'root'}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            paths = []
            for path_item in file_system_client.get_paths(path=path, recursive=recursive):
                paths.append({
                    'name': path_item.name,
                    'is_directory': path_item.is_directory,
                    'content_length': path_item.content_length,
                    'last_modified': path_item.last_modified,
                    'etag': path_item.etag
                })
            
            logger.info(f"Found {len(paths)} items")
            return paths
            
        except AzureError as e:
            logger.error(f"Failed to list paths: {e}")
            raise
    
    def delete_file(
        self,
        file_system_name: str,
        file_path: str
    ) -> bool:
        """
        Delete a file from ADLS Gen2.
        
        Args:
            file_system_name: File system name
            file_path: File path to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            logger.info(f"Deleting file: {file_path}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            file_client = file_system_client.get_file_client(file_path)
            file_client.delete_file()
            
            logger.info(f"Successfully deleted file: {file_path}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return False
            
        except AzureError as e:
            logger.error(f"Failed to delete file: {e}")
            raise
    
    def delete_directory(
        self,
        file_system_name: str,
        directory_path: str
    ) -> bool:
        """
        Delete a directory and its contents from ADLS Gen2.
        
        Args:
            file_system_name: File system name
            directory_path: Directory path to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            logger.warning(f"Deleting directory: {directory_path}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            directory_client = file_system_client.get_directory_client(directory_path)
            directory_client.delete_directory()
            
            logger.info(f"Successfully deleted directory: {directory_path}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Directory not found: {directory_path}")
            return False
            
        except AzureError as e:
            logger.error(f"Failed to delete directory: {e}")
            raise
    
    def set_acl(
        self,
        file_system_name: str,
        path: str,
        acl: str
    ) -> None:
        """
        Set Access Control List (ACL) on a path.
        
        Args:
            file_system_name: File system name
            path: Path to set ACL on
            acl: ACL string (e.g., 'user::rwx,group::r-x,other::r--')
        
        Example:
            manager.set_acl('myfs', 'data/file.txt', 'user::rwx,group::r-x,other::r--')
        """
        try:
            logger.info(f"Setting ACL on: {path}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            file_client = file_system_client.get_file_client(path)
            file_client.set_access_control(acl=acl)
            
            logger.info(f"ACL set successfully")
            
        except AzureError as e:
            logger.error(f"Failed to set ACL: {e}")
            raise
    
    def delete_file_system(self, file_system_name: str) -> bool:
        """
        Delete a file system.
        
        Args:
            file_system_name: File system name
        
        Returns:
            True if deleted successfully
        """
        try:
            logger.warning(f"Deleting file system: {file_system_name}")
            
            file_system_client = self.service_client.get_file_system_client(
                file_system_name
            )
            
            file_system_client.delete_file_system()
            
            logger.info(f"Successfully deleted file system: {file_system_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"File system not found: {file_system_name}")
            return False
            
        except AzureError as e:
            logger.error(f"Failed to delete file system: {e}")
            raise


def main():
    """
    Main function demonstrating ADLS Gen2 operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Data Lake Storage Gen2 Example")
        logger.info("=" * 60)
        
        # Initialize manager
        datalake_manager = DataLakeGen2Manager()
        
        file_system_name = "demo-datalake"
        
        # Create file system
        logger.info("\n--- Creating File System ---")
        datalake_manager.create_file_system(
            file_system_name=file_system_name,
            metadata={'purpose': 'demo', 'environment': 'development'}
        )
        
        # Create directory structure
        logger.info("\n--- Creating Directory Structure ---")
        directories = [
            "raw/data",
            "processed/data",
            "curated/data"
        ]
        
        for directory in directories:
            datalake_manager.create_directory(
                file_system_name=file_system_name,
                directory_path=directory
            )
        
        # Upload data
        logger.info("\n--- Uploading Data ---")
        
        # Upload CSV data
        csv_data = "id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300"
        result1 = datalake_manager.upload_data(
            file_system_name=file_system_name,
            file_path="raw/data/sample.csv",
            data=csv_data.encode('utf-8'),
            content_type='text/csv',
            metadata={'source': 'demo', 'format': 'csv'}
        )
        logger.info(f"Uploaded CSV: {result1['file_path']}")
        
        # Upload JSON data
        import json
        json_data = json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'data': [
                {'id': 1, 'value': 100},
                {'id': 2, 'value': 200}
            ]
        }, indent=2)
        
        result2 = datalake_manager.upload_data(
            file_system_name=file_system_name,
            file_path="processed/data/sample.json",
            data=json_data.encode('utf-8'),
            content_type='application/json'
        )
        logger.info(f"Uploaded JSON: {result2['file_path']}")
        
        # List all paths
        logger.info("\n--- Listing All Paths ---")
        paths = datalake_manager.list_paths(file_system_name, recursive=True)
        for path in paths:
            path_type = "DIR" if path['is_directory'] else "FILE"
            size = path['content_length'] or 0
            logger.info(f"  [{path_type}] {path['name']} ({size} bytes)")
        
        # Download file
        logger.info("\n--- Downloading File ---")
        content = datalake_manager.download_file(
            file_system_name=file_system_name,
            file_path="raw/data/sample.csv"
        )
        logger.info(f"Downloaded content:\n{content.decode('utf-8')}")
        
        # Cleanup (commented out for safety)
        # logger.info("\n--- Cleanup ---")
        # datalake_manager.delete_directory(file_system_name, "raw")
        # datalake_manager.delete_directory(file_system_name, "processed")
        # datalake_manager.delete_directory(file_system_name, "curated")
        # datalake_manager.delete_file_system(file_system_name)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up: Delete file system '{file_system_name}'")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
