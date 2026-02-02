"""
Bulk File Upload/Download Operations for Azure Storage

This module demonstrates efficient bulk file operations with proper error handling,
parallel processing, and progress tracking for Azure Blob Storage.

Requirements:
    pip install azure-identity azure-storage-blob tqdm

Environment Variables:
    AZURE_STORAGE_ACCOUNT_NAME: Storage account name
    AZURE_STORAGE_ACCOUNT_KEY: Storage account key (or use DefaultAzureCredential)
"""

import os
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import time

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError, ResourceNotFoundError

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    logging.warning("tqdm not available. Install with: pip install tqdm")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FileOperation:
    """Represents a file operation result."""
    file_path: str
    success: bool
    error_message: Optional[str] = None
    size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None


class BulkFileTransferManager:
    """
    Manages bulk file upload and download operations with Azure Blob Storage.
    
    Features:
    - Parallel processing for improved performance
    - Progress tracking with tqdm
    - Comprehensive error handling
    - Retry logic for failed operations
    - Summary statistics
    """
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        max_workers: int = 5
    ):
        """
        Initialize bulk transfer manager.
        
        Args:
            account_name: Storage account name
            account_key: Storage account key (optional)
            max_workers: Maximum number of parallel workers
        """
        self.account_name = account_name or os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.max_workers = max_workers
        
        if not self.account_name:
            raise ValueError(
                "Storage account name required. "
                "Set AZURE_STORAGE_ACCOUNT_NAME environment variable."
            )
        
        account_url = f"https://{self.account_name}.blob.core.windows.net"
        
        if account_key or os.getenv('AZURE_STORAGE_ACCOUNT_KEY'):
            key = account_key or os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=key
            )
        else:
            credential = DefaultAzureCredential()
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential
            )
        
        logger.info(f"Initialized for account: {self.account_name}")
        logger.info(f"Max parallel workers: {self.max_workers}")
    
    def upload_files(
        self,
        container_name: str,
        file_paths: List[str],
        blob_prefix: str = "",
        overwrite: bool = True,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Upload multiple files to blob storage in parallel.
        
        Args:
            container_name: Target container name
            file_paths: List of local file paths to upload
            blob_prefix: Optional prefix for blob names
            overwrite: Whether to overwrite existing blobs
            max_retries: Maximum retry attempts for failed uploads
        
        Returns:
            Dictionary containing operation summary and results
        """
        logger.info(f"Starting bulk upload of {len(file_paths)} files")
        logger.info(f"Target: {container_name}")
        
        start_time = time.time()
        results = []
        
        # Use tqdm for progress if available
        if TQDM_AVAILABLE:
            pbar = tqdm(total=len(file_paths), desc="Uploading files")
        else:
            pbar = None
        
        def upload_single_file(file_path: str) -> FileOperation:
            """Upload a single file with error handling and retry logic."""
            file_path = Path(file_path)
            
            if not file_path.is_file():
                return FileOperation(
                    file_path=str(file_path),
                    success=False,
                    error_message=f"File not found: {file_path}"
                )
            
            # Determine blob name
            blob_name = f"{blob_prefix}{file_path.name}" if blob_prefix else file_path.name
            
            for attempt in range(max_retries):
                try:
                    op_start = time.time()
                    
                    blob_client = self.blob_service_client.get_blob_client(
                        container=container_name,
                        blob=blob_name
                    )
                    
                    with open(file_path, 'rb') as data:
                        blob_client.upload_blob(data, overwrite=overwrite)
                    
                    file_size = file_path.stat().st_size
                    duration = time.time() - op_start
                    
                    return FileOperation(
                        file_path=str(file_path),
                        success=True,
                        size_bytes=file_size,
                        duration_seconds=duration
                    )
                    
                except AzureError as e:
                    if attempt == max_retries - 1:
                        return FileOperation(
                            file_path=str(file_path),
                            success=False,
                            error_message=str(e)
                        )
                    else:
                        logger.warning(
                            f"Upload failed for {file_path}, "
                            f"attempt {attempt + 1}/{max_retries}: {e}"
                        )
                        time.sleep(2 ** attempt)  # Exponential backoff
                
                except Exception as e:
                    return FileOperation(
                        file_path=str(file_path),
                        success=False,
                        error_message=f"Unexpected error: {e}"
                    )
        
        # Execute uploads in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(upload_single_file, fp): fp 
                for fp in file_paths
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if pbar:
                    pbar.update(1)
                
                if result.success:
                    logger.debug(f"✓ Uploaded: {result.file_path}")
                else:
                    logger.error(f"✗ Failed: {result.file_path} - {result.error_message}")
        
        if pbar:
            pbar.close()
        
        # Calculate summary
        total_duration = time.time() - start_time
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        total_bytes = sum(r.size_bytes for r in successful if r.size_bytes)
        
        summary = {
            'total_files': len(file_paths),
            'successful': len(successful),
            'failed': len(failed),
            'total_bytes': total_bytes,
            'total_duration_seconds': total_duration,
            'average_speed_mbps': (total_bytes / 1024 / 1024) / total_duration if total_duration > 0 else 0,
            'results': results
        }
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Upload Summary:")
        logger.info(f"  Total files: {summary['total_files']}")
        logger.info(f"  Successful: {summary['successful']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Total size: {total_bytes / 1024 / 1024:.2f} MB")
        logger.info(f"  Duration: {total_duration:.2f} seconds")
        logger.info(f"  Average speed: {summary['average_speed_mbps']:.2f} MB/s")
        logger.info(f"{'=' * 60}\n")
        
        return summary
    
    def download_files(
        self,
        container_name: str,
        blob_names: List[str],
        local_directory: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Download multiple blobs to local directory in parallel.
        
        Args:
            container_name: Source container name
            blob_names: List of blob names to download
            local_directory: Local directory to save files
            max_retries: Maximum retry attempts for failed downloads
        
        Returns:
            Dictionary containing operation summary and results
        """
        logger.info(f"Starting bulk download of {len(blob_names)} blobs")
        logger.info(f"Source: {container_name}")
        logger.info(f"Destination: {local_directory}")
        
        # Create local directory
        local_dir = Path(local_directory)
        local_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        results = []
        
        # Use tqdm for progress if available
        if TQDM_AVAILABLE:
            pbar = tqdm(total=len(blob_names), desc="Downloading files")
        else:
            pbar = None
        
        def download_single_blob(blob_name: str) -> FileOperation:
            """Download a single blob with error handling and retry logic."""
            local_file = local_dir / Path(blob_name).name
            
            for attempt in range(max_retries):
                try:
                    op_start = time.time()
                    
                    blob_client = self.blob_service_client.get_blob_client(
                        container=container_name,
                        blob=blob_name
                    )
                    
                    # Download blob
                    with open(local_file, 'wb') as file:
                        download_stream = blob_client.download_blob()
                        file.write(download_stream.readall())
                    
                    file_size = local_file.stat().st_size
                    duration = time.time() - op_start
                    
                    return FileOperation(
                        file_path=str(local_file),
                        success=True,
                        size_bytes=file_size,
                        duration_seconds=duration
                    )
                    
                except ResourceNotFoundError:
                    return FileOperation(
                        file_path=blob_name,
                        success=False,
                        error_message=f"Blob not found: {blob_name}"
                    )
                    
                except AzureError as e:
                    if attempt == max_retries - 1:
                        return FileOperation(
                            file_path=blob_name,
                            success=False,
                            error_message=str(e)
                        )
                    else:
                        logger.warning(
                            f"Download failed for {blob_name}, "
                            f"attempt {attempt + 1}/{max_retries}: {e}"
                        )
                        time.sleep(2 ** attempt)  # Exponential backoff
                
                except Exception as e:
                    return FileOperation(
                        file_path=blob_name,
                        success=False,
                        error_message=f"Unexpected error: {e}"
                    )
        
        # Execute downloads in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(download_single_blob, bn): bn 
                for bn in blob_names
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if pbar:
                    pbar.update(1)
                
                if result.success:
                    logger.debug(f"✓ Downloaded: {result.file_path}")
                else:
                    logger.error(f"✗ Failed: {result.file_path} - {result.error_message}")
        
        if pbar:
            pbar.close()
        
        # Calculate summary
        total_duration = time.time() - start_time
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        total_bytes = sum(r.size_bytes for r in successful if r.size_bytes)
        
        summary = {
            'total_files': len(blob_names),
            'successful': len(successful),
            'failed': len(failed),
            'total_bytes': total_bytes,
            'total_duration_seconds': total_duration,
            'average_speed_mbps': (total_bytes / 1024 / 1024) / total_duration if total_duration > 0 else 0,
            'results': results
        }
        
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Download Summary:")
        logger.info(f"  Total files: {summary['total_files']}")
        logger.info(f"  Successful: {summary['successful']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Total size: {total_bytes / 1024 / 1024:.2f} MB")
        logger.info(f"  Duration: {total_duration:.2f} seconds")
        logger.info(f"  Average speed: {summary['average_speed_mbps']:.2f} MB/s")
        logger.info(f"{'=' * 60}\n")
        
        return summary
    
    def upload_directory(
        self,
        container_name: str,
        local_directory: str,
        blob_prefix: str = "",
        pattern: str = "*",
        recursive: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload all files from a directory to blob storage.
        
        Args:
            container_name: Target container name
            local_directory: Local directory to upload
            blob_prefix: Optional prefix for blob names
            pattern: File pattern to match (default: all files)
            recursive: Whether to include subdirectories
            **kwargs: Additional arguments passed to upload_files
        
        Returns:
            Dictionary containing operation summary
        """
        local_dir = Path(local_directory)
        
        if not local_dir.is_dir():
            raise ValueError(f"Directory not found: {local_directory}")
        
        # Find all files matching pattern
        if recursive:
            file_paths = list(local_dir.rglob(pattern))
        else:
            file_paths = list(local_dir.glob(pattern))
        
        # Filter only files (exclude directories)
        file_paths = [fp for fp in file_paths if fp.is_file()]
        
        logger.info(f"Found {len(file_paths)} files in {local_directory}")
        
        return self.upload_files(
            container_name=container_name,
            file_paths=[str(fp) for fp in file_paths],
            blob_prefix=blob_prefix,
            **kwargs
        )


def main():
    """
    Main function demonstrating bulk file operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Bulk File Upload/Download Example")
        logger.info("=" * 60)
        
        # Initialize manager
        transfer_manager = BulkFileTransferManager(max_workers=3)
        
        container_name = "bulk-transfer-demo"
        
        # Create test files
        logger.info("\n--- Creating Test Files ---")
        test_dir = Path("./test_upload")
        test_dir.mkdir(exist_ok=True)
        
        test_files = []
        for i in range(5):
            file_path = test_dir / f"test_file_{i}.txt"
            with open(file_path, 'w') as f:
                f.write(f"Test file {i}\n" * 100)
            test_files.append(str(file_path))
        
        logger.info(f"Created {len(test_files)} test files")
        
        # Upload files
        logger.info("\n--- Uploading Files ---")
        upload_summary = transfer_manager.upload_files(
            container_name=container_name,
            file_paths=test_files,
            blob_prefix="uploads/",
            overwrite=True
        )
        
        # Download files
        logger.info("\n--- Downloading Files ---")
        blob_names = [f"uploads/test_file_{i}.txt" for i in range(5)]
        download_dir = Path("./test_download")
        
        download_summary = transfer_manager.download_files(
            container_name=container_name,
            blob_names=blob_names,
            local_directory=str(download_dir)
        )
        
        # Cleanup local files
        logger.info("\n--- Cleanup ---")
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
        if download_dir.exists():
            shutil.rmtree(download_dir)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up: Delete container '{container_name}'")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
