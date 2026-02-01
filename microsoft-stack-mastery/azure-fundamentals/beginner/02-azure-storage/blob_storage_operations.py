"""
Azure Blob Storage Operations Example

This module demonstrates comprehensive blob storage operations using Azure SDK
for Python. Covers upload, download, list, delete, and advanced operations.

Requirements:
    pip install azure-identity azure-storage-blob

Environment Variables:
    AZURE_STORAGE_ACCOUNT_NAME: Storage account name
    AZURE_STORAGE_ACCOUNT_KEY: Storage account key (or use DefaultAzureCredential)
    AZURE_STORAGE_CONNECTION_STRING: Connection string (alternative)
"""

import os
import logging
from typing import Optional, List, Dict, Any, BinaryIO
from pathlib import Path
from datetime import datetime, timedelta
import io

from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContainerClient,
    BlobProperties,
    ContentSettings,
    StandardBlobTier,
    PublicAccess
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


class BlobStorageManager:
    """
    Manages Azure Blob Storage operations.
    
    Provides comprehensive methods for working with Azure Blob Storage including
    container management, blob operations, and advanced features like metadata,
    tags, and access tiers.
    """
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        """
        Initialize Blob Storage Manager.
        
        Args:
            account_name: Storage account name
            account_key: Storage account key
            connection_string: Connection string (alternative to name/key)
        """
        self.account_name = account_name or os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        
        # Initialize BlobServiceClient
        if connection_string or os.getenv('AZURE_STORAGE_CONNECTION_STRING'):
            conn_str = connection_string or os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            self.blob_service_client = BlobServiceClient.from_connection_string(conn_str)
            logger.info("Initialized with connection string")
            
        elif self.account_name and (account_key or os.getenv('AZURE_STORAGE_ACCOUNT_KEY')):
            key = account_key or os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=key
            )
            logger.info(f"Initialized with account key for: {self.account_name}")
            
        elif self.account_name:
            # Use DefaultAzureCredential (recommended for production)
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            credential = DefaultAzureCredential()
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential
            )
            logger.info(f"Initialized with DefaultAzureCredential for: {self.account_name}")
            
        else:
            raise ValueError(
                "Must provide either connection_string or account_name. "
                "Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME."
            )
    
    def create_container(
        self,
        container_name: str,
        public_access: Optional[PublicAccess] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> ContainerClient:
        """
        Create a blob container.
        
        Args:
            container_name: Name of the container
            public_access: Public access level (None, 'blob', or 'container')
            metadata: Optional metadata key-value pairs
        
        Returns:
            ContainerClient instance
        
        Raises:
            ResourceExistsError: If container already exists
        """
        try:
            logger.info(f"Creating container: {container_name}")
            
            container_client = self.blob_service_client.create_container(
                name=container_name,
                public_access=public_access,
                metadata=metadata
            )
            
            logger.info(f"Successfully created container: {container_name}")
            return container_client
            
        except ResourceExistsError:
            logger.warning(f"Container already exists: {container_name}")
            return self.blob_service_client.get_container_client(container_name)
            
        except AzureError as e:
            logger.error(f"Failed to create container: {e}")
            raise
    
    def upload_blob(
        self,
        container_name: str,
        blob_name: str,
        data: Any,
        overwrite: bool = True,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        tier: Optional[StandardBlobTier] = None
    ) -> Dict[str, Any]:
        """
        Upload data to a blob.
        
        Args:
            container_name: Container name
            blob_name: Blob name (path)
            data: Data to upload (bytes, str, file-like object, or file path)
            overwrite: Whether to overwrite existing blob
            metadata: Optional metadata
            content_type: MIME type of the content
            tier: Storage tier (Hot, Cool, Archive)
        
        Returns:
            Upload result details
        """
        try:
            logger.info(f"Uploading blob: {blob_name} to {container_name}")
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Handle file path
            if isinstance(data, (str, Path)) and Path(data).is_file():
                with open(data, 'rb') as file_data:
                    upload_data = file_data.read()
            else:
                upload_data = data
            
            # Set content settings
            content_settings = None
            if content_type:
                content_settings = ContentSettings(content_type=content_type)
            
            # Upload blob
            result = blob_client.upload_blob(
                data=upload_data,
                overwrite=overwrite,
                metadata=metadata,
                content_settings=content_settings,
                standard_blob_tier=tier
            )
            
            logger.info(f"Successfully uploaded blob: {blob_name}")
            
            return {
                'blob_name': blob_name,
                'container': container_name,
                'etag': result['etag'],
                'last_modified': result['last_modified'],
                'url': blob_client.url
            }
            
        except AzureError as e:
            logger.error(f"Failed to upload blob: {e}")
            raise
    
    def upload_file(
        self,
        container_name: str,
        file_path: str,
        blob_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload a file to blob storage.
        
        Args:
            container_name: Container name
            file_path: Local file path
            blob_name: Blob name (defaults to filename)
            **kwargs: Additional arguments for upload_blob
        
        Returns:
            Upload result details
        """
        file_path = Path(file_path)
        
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        blob_name = blob_name or file_path.name
        
        logger.info(f"Uploading file: {file_path} as {blob_name}")
        
        with open(file_path, 'rb') as file:
            return self.upload_blob(
                container_name=container_name,
                blob_name=blob_name,
                data=file,
                **kwargs
            )
    
    def download_blob(
        self,
        container_name: str,
        blob_name: str,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Download a blob.
        
        Args:
            container_name: Container name
            blob_name: Blob name
            output_path: Optional file path to save downloaded data
        
        Returns:
            Blob content as bytes
        """
        try:
            logger.info(f"Downloading blob: {blob_name} from {container_name}")
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Download blob
            blob_data = blob_client.download_blob()
            content = blob_data.readall()
            
            # Save to file if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as file:
                    file.write(content)
                
                logger.info(f"Saved to: {output_path}")
            
            logger.info(f"Downloaded {len(content)} bytes")
            return content
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            raise
            
        except AzureError as e:
            logger.error(f"Failed to download blob: {e}")
            raise
    
    def list_blobs(
        self,
        container_name: str,
        prefix: Optional[str] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List blobs in a container.
        
        Args:
            container_name: Container name
            prefix: Filter blobs by prefix
            include_metadata: Include blob metadata
        
        Returns:
            List of blob details
        """
        try:
            logger.info(f"Listing blobs in container: {container_name}")
            
            container_client = self.blob_service_client.get_container_client(
                container_name
            )
            
            include = ['metadata'] if include_metadata else None
            
            blobs = []
            for blob in container_client.list_blobs(name_starts_with=prefix, include=include):
                blob_info = {
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_settings.content_type if blob.content_settings else None,
                    'last_modified': blob.last_modified,
                    'etag': blob.etag,
                    'blob_type': blob.blob_type,
                    'tier': blob.blob_tier
                }
                
                if include_metadata and blob.metadata:
                    blob_info['metadata'] = blob.metadata
                
                blobs.append(blob_info)
            
            logger.info(f"Found {len(blobs)} blobs")
            return blobs
            
        except AzureError as e:
            logger.error(f"Failed to list blobs: {e}")
            raise
    
    def delete_blob(
        self,
        container_name: str,
        blob_name: str,
        delete_snapshots: str = 'include'
    ) -> bool:
        """
        Delete a blob.
        
        Args:
            container_name: Container name
            blob_name: Blob name
            delete_snapshots: How to handle snapshots ('include', 'only', None)
        
        Returns:
            True if deleted successfully
        """
        try:
            logger.info(f"Deleting blob: {blob_name} from {container_name}")
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob(delete_snapshots=delete_snapshots)
            
            logger.info(f"Successfully deleted blob: {blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found: {blob_name}")
            return False
            
        except AzureError as e:
            logger.error(f"Failed to delete blob: {e}")
            raise
    
    def copy_blob(
        self,
        source_container: str,
        source_blob: str,
        dest_container: str,
        dest_blob: str
    ) -> Dict[str, Any]:
        """
        Copy a blob within the same storage account.
        
        Args:
            source_container: Source container name
            source_blob: Source blob name
            dest_container: Destination container name
            dest_blob: Destination blob name
        
        Returns:
            Copy operation details
        """
        try:
            logger.info(f"Copying blob from {source_container}/{source_blob} to {dest_container}/{dest_blob}")
            
            source_blob_client = self.blob_service_client.get_blob_client(
                container=source_container,
                blob=source_blob
            )
            
            dest_blob_client = self.blob_service_client.get_blob_client(
                container=dest_container,
                blob=dest_blob
            )
            
            # Start copy operation
            copy_status = dest_blob_client.start_copy_from_url(source_blob_client.url)
            
            logger.info(f"Copy operation started. Status: {copy_status}")
            
            return {
                'source': f"{source_container}/{source_blob}",
                'destination': f"{dest_container}/{dest_blob}",
                'copy_id': copy_status['copy_id'],
                'copy_status': copy_status['copy_status']
            }
            
        except AzureError as e:
            logger.error(f"Failed to copy blob: {e}")
            raise
    
    def set_blob_metadata(
        self,
        container_name: str,
        blob_name: str,
        metadata: Dict[str, str]
    ) -> None:
        """
        Set metadata on a blob.
        
        Args:
            container_name: Container name
            blob_name: Blob name
            metadata: Metadata key-value pairs
        """
        try:
            logger.info(f"Setting metadata on blob: {blob_name}")
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.set_blob_metadata(metadata)
            
            logger.info(f"Metadata set successfully")
            
        except AzureError as e:
            logger.error(f"Failed to set metadata: {e}")
            raise
    
    def get_blob_properties(
        self,
        container_name: str,
        blob_name: str
    ) -> Dict[str, Any]:
        """
        Get blob properties and metadata.
        
        Args:
            container_name: Container name
            blob_name: Blob name
        
        Returns:
            Blob properties
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                'name': blob_name,
                'size': properties.size,
                'content_type': properties.content_settings.content_type,
                'last_modified': properties.last_modified,
                'etag': properties.etag,
                'metadata': properties.metadata,
                'blob_type': properties.blob_type,
                'tier': properties.blob_tier,
                'creation_time': properties.creation_time
            }
            
        except AzureError as e:
            logger.error(f"Failed to get blob properties: {e}")
            raise
    
    def delete_container(self, container_name: str) -> bool:
        """
        Delete a container.
        
        Args:
            container_name: Container name
        
        Returns:
            True if deleted successfully
        """
        try:
            logger.warning(f"Deleting container: {container_name}")
            
            container_client = self.blob_service_client.get_container_client(
                container_name
            )
            
            container_client.delete_container()
            
            logger.info(f"Successfully deleted container: {container_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Container not found: {container_name}")
            return False
            
        except AzureError as e:
            logger.error(f"Failed to delete container: {e}")
            raise


def main():
    """
    Main function demonstrating blob storage operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Blob Storage Operations Example")
        logger.info("=" * 60)
        
        # Initialize manager
        storage_manager = BlobStorageManager()
        
        container_name = "demo-container"
        
        # Create container
        logger.info("\n--- Creating Container ---")
        storage_manager.create_container(
            container_name=container_name,
            metadata={'purpose': 'demo', 'created_by': 'python-sdk'}
        )
        
        # Upload text blob
        logger.info("\n--- Uploading Text Blob ---")
        text_data = "Hello, Azure Blob Storage!"
        result1 = storage_manager.upload_blob(
            container_name=container_name,
            blob_name="hello.txt",
            data=text_data.encode('utf-8'),
            metadata={'type': 'text', 'encoding': 'utf-8'},
            content_type='text/plain'
        )
        logger.info(f"Uploaded: {result1['url']}")
        
        # Upload JSON blob
        logger.info("\n--- Uploading JSON Blob ---")
        import json
        json_data = json.dumps({'message': 'Hello from Python', 'timestamp': datetime.utcnow().isoformat()})
        result2 = storage_manager.upload_blob(
            container_name=container_name,
            blob_name="data/sample.json",
            data=json_data.encode('utf-8'),
            content_type='application/json'
        )
        
        # List blobs
        logger.info("\n--- Listing Blobs ---")
        blobs = storage_manager.list_blobs(container_name, include_metadata=True)
        for blob in blobs:
            logger.info(f"  - {blob['name']} ({blob['size']} bytes) - {blob['content_type']}")
        
        # Download blob
        logger.info("\n--- Downloading Blob ---")
        content = storage_manager.download_blob(container_name, "hello.txt")
        logger.info(f"Content: {content.decode('utf-8')}")
        
        # Get blob properties
        logger.info("\n--- Getting Blob Properties ---")
        props = storage_manager.get_blob_properties(container_name, "hello.txt")
        logger.info(f"Properties: {props}")
        
        # Copy blob
        logger.info("\n--- Copying Blob ---")
        copy_result = storage_manager.copy_blob(
            source_container=container_name,
            source_blob="hello.txt",
            dest_container=container_name,
            dest_blob="hello-copy.txt"
        )
        logger.info(f"Copy status: {copy_result['copy_status']}")
        
        # Cleanup (commented out for safety)
        # logger.info("\n--- Cleanup ---")
        # storage_manager.delete_blob(container_name, "hello.txt")
        # storage_manager.delete_blob(container_name, "hello-copy.txt")
        # storage_manager.delete_blob(container_name, "data/sample.json")
        # storage_manager.delete_container(container_name)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up: Delete container '{container_name}'")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
