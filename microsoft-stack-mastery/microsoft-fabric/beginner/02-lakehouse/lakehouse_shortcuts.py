"""
Microsoft Fabric Lakehouse Shortcuts Module

This module demonstrates creating and managing shortcuts to external storage
in Fabric Lakehouse (ADLS Gen2, S3, OneLake).

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from typing import Optional, Dict, Any, List
import json

import requests
from dotenv import load_dotenv

# Import authentication
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from beginner.fabric_setup.authentication import FabricAuthenticator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LakehouseShortcutManager:
    """
    Manager for Lakehouse shortcuts (data virtualization).
    
    Shortcuts enable accessing external data without copying it to OneLake.
    Supported sources:
    - Azure Data Lake Storage Gen2 (ADLS)
    - Amazon S3
    - OneLake (other lakehouses)
    """
    
    BASE_URL = "https://api.fabric.microsoft.com/v1"
    
    def __init__(self, authenticator: FabricAuthenticator):
        """
        Initialize Lakehouse Shortcut Manager.
        
        Args:
            authenticator (FabricAuthenticator): Authentication handler
        """
        self.auth = authenticator
        self.session = requests.Session()
        logger.info("Initialized LakehouseShortcutManager")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return self.auth.get_auth_headers()
    
    def create_adls_shortcut(
        self,
        workspace_id: str,
        lakehouse_id: str,
        shortcut_name: str,
        adls_account: str,
        container: str,
        path: str = "/",
        connection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create shortcut to Azure Data Lake Storage Gen2.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
            shortcut_name (str): Name for the shortcut
            adls_account (str): ADLS storage account name
            container (str): Container name
            path (str): Path within container (default: root)
            connection_id (str, optional): Connection ID for authentication
        
        Returns:
            dict: Created shortcut details
        
        Example:
            >>> manager.create_adls_shortcut(
            ...     workspace_id="ws-123",
            ...     lakehouse_id="lh-456",
            ...     shortcut_name="external_data",
            ...     adls_account="mystorageaccount",
            ...     container="rawdata",
            ...     path="/sales/2024/"
            ... )
        """
        logger.info(
            f"Creating ADLS shortcut '{shortcut_name}' to "
            f"{adls_account}/{container}{path}"
        )
        
        url = (
            f"{self.BASE_URL}/workspaces/{workspace_id}/"
            f"lakehouses/{lakehouse_id}/shortcuts"
        )
        
        # Construct ADLS path
        target_path = (
            f"https://{adls_account}.dfs.core.windows.net/"
            f"{container}{path}"
        )
        
        payload = {
            "name": shortcut_name,
            "path": "Files",  # Shortcuts go under Files directory
            "target": {
                "type": "AdlsGen2",
                "adlsGen2": {
                    "location": target_path,
                    "connectionId": connection_id
                }
            }
        }
        
        try:
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            shortcut_data = response.json()
            
            logger.info(f"✅ ADLS shortcut '{shortcut_name}' created successfully")
            return shortcut_data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to create ADLS shortcut: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise
    
    def create_s3_shortcut(
        self,
        workspace_id: str,
        lakehouse_id: str,
        shortcut_name: str,
        bucket: str,
        path: str = "/",
        region: str = "us-east-1",
        connection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create shortcut to Amazon S3.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
            shortcut_name (str): Name for the shortcut
            bucket (str): S3 bucket name
            path (str): Path within bucket
            region (str): AWS region
            connection_id (str, optional): Connection ID for authentication
        
        Returns:
            dict: Created shortcut details
        """
        logger.info(f"Creating S3 shortcut '{shortcut_name}' to {bucket}{path}")
        
        url = (
            f"{self.BASE_URL}/workspaces/{workspace_id}/"
            f"lakehouses/{lakehouse_id}/shortcuts"
        )
        
        # Construct S3 path
        target_path = f"s3://{bucket}{path}"
        
        payload = {
            "name": shortcut_name,
            "path": "Files",
            "target": {
                "type": "S3",
                "s3": {
                    "location": target_path,
                    "region": region,
                    "connectionId": connection_id
                }
            }
        }
        
        try:
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            shortcut_data = response.json()
            
            logger.info(f"✅ S3 shortcut '{shortcut_name}' created successfully")
            return shortcut_data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to create S3 shortcut: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise
    
    def create_onelake_shortcut(
        self,
        workspace_id: str,
        lakehouse_id: str,
        shortcut_name: str,
        target_workspace_id: str,
        target_lakehouse_id: str,
        target_path: str = "/"
    ) -> Dict[str, Any]:
        """
        Create shortcut to another OneLake lakehouse.
        
        Args:
            workspace_id (str): Source workspace ID
            lakehouse_id (str): Source lakehouse ID
            shortcut_name (str): Name for the shortcut
            target_workspace_id (str): Target workspace ID
            target_lakehouse_id (str): Target lakehouse ID
            target_path (str): Path in target lakehouse
        
        Returns:
            dict: Created shortcut details
        
        Example:
            >>> manager.create_onelake_shortcut(
            ...     workspace_id="ws-source",
            ...     lakehouse_id="lh-source",
            ...     shortcut_name="shared_data",
            ...     target_workspace_id="ws-target",
            ...     target_lakehouse_id="lh-target",
            ...     target_path="/Tables/customers"
            ... )
        """
        logger.info(
            f"Creating OneLake shortcut '{shortcut_name}' to "
            f"workspace:{target_workspace_id}/lakehouse:{target_lakehouse_id}"
        )
        
        url = (
            f"{self.BASE_URL}/workspaces/{workspace_id}/"
            f"lakehouses/{lakehouse_id}/shortcuts"
        )
        
        payload = {
            "name": shortcut_name,
            "path": "Files",
            "target": {
                "type": "OneLake",
                "oneLake": {
                    "workspaceId": target_workspace_id,
                    "itemId": target_lakehouse_id,
                    "path": target_path
                }
            }
        }
        
        try:
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            shortcut_data = response.json()
            
            logger.info(f"✅ OneLake shortcut '{shortcut_name}' created successfully")
            return shortcut_data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to create OneLake shortcut: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise
    
    def list_shortcuts(
        self,
        workspace_id: str,
        lakehouse_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all shortcuts in a lakehouse.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
        
        Returns:
            list: List of shortcuts
        """
        logger.info(f"Listing shortcuts in lakehouse {lakehouse_id}")
        
        url = (
            f"{self.BASE_URL}/workspaces/{workspace_id}/"
            f"lakehouses/{lakehouse_id}/shortcuts"
        )
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            shortcuts = data.get('value', [])
            
            logger.info(f"✅ Found {len(shortcuts)} shortcuts")
            return shortcuts
            
        except Exception as e:
            logger.error(f"❌ Failed to list shortcuts: {str(e)}")
            raise
    
    def get_shortcut(
        self,
        workspace_id: str,
        lakehouse_id: str,
        shortcut_name: str
    ) -> Dict[str, Any]:
        """
        Get details of a specific shortcut.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
            shortcut_name (str): Shortcut name
        
        Returns:
            dict: Shortcut details
        """
        logger.info(f"Getting shortcut '{shortcut_name}'")
        
        url = (
            f"{self.BASE_URL}/workspaces/{workspace_id}/"
            f"lakehouses/{lakehouse_id}/shortcuts/{shortcut_name}"
        )
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            shortcut_data = response.json()
            
            logger.info(f"✅ Retrieved shortcut: {shortcut_name}")
            return shortcut_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get shortcut: {str(e)}")
            raise
    
    def delete_shortcut(
        self,
        workspace_id: str,
        lakehouse_id: str,
        shortcut_name: str
    ) -> bool:
        """
        Delete a shortcut.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
            shortcut_name (str): Shortcut name to delete
        
        Returns:
            bool: True if successful
        
        Note:
            Deleting a shortcut only removes the reference, not the source data.
        """
        logger.warning(f"Deleting shortcut '{shortcut_name}'")
        
        url = (
            f"{self.BASE_URL}/workspaces/{workspace_id}/"
            f"lakehouses/{lakehouse_id}/shortcuts/{shortcut_name}"
        )
        
        try:
            response = self.session.delete(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            logger.info(f"✅ Shortcut '{shortcut_name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete shortcut: {str(e)}")
            raise


def main():
    """
    Example usage of Lakehouse Shortcut Manager.
    """
    print("=" * 60)
    print("Microsoft Fabric Lakehouse Shortcuts Examples")
    print("=" * 60)
    
    # Configuration from environment
    workspace_id = os.getenv("WORKSPACE_ID")
    lakehouse_id = os.getenv("LAKEHOUSE_ID")
    adls_account = os.getenv("ADLS_ACCOUNT_NAME")
    adls_container = os.getenv("ADLS_CONTAINER_NAME")
    
    if not all([workspace_id, lakehouse_id]):
        print("❌ Required environment variables not set:")
        print("   - WORKSPACE_ID")
        print("   - LAKEHOUSE_ID")
        return
    
    try:
        # Initialize manager
        auth = FabricAuthenticator(auth_method="default")
        manager = LakehouseShortcutManager(auth)
        
        # Example 1: Create ADLS shortcut
        if adls_account and adls_container:
            print("\n1. Creating ADLS Gen2 shortcut")
            print("-" * 60)
            
            adls_shortcut = manager.create_adls_shortcut(
                workspace_id=workspace_id,
                lakehouse_id=lakehouse_id,
                shortcut_name="external_adls_data",
                adls_account=adls_account,
                container=adls_container,
                path="/raw/"
            )
            
            print(f"✅ Created ADLS shortcut: {adls_shortcut.get('name')}")
        else:
            print("\n1. Skipping ADLS shortcut (credentials not configured)")
        
        # Example 2: Create OneLake shortcut
        print("\n2. Creating OneLake shortcut")
        print("-" * 60)
        
        # Note: This requires another lakehouse to link to
        print("ℹ️  OneLake shortcuts require a target lakehouse")
        print("   Example code:")
        print("""
        onelake_shortcut = manager.create_onelake_shortcut(
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id,
            shortcut_name="shared_gold_layer",
            target_workspace_id="target-ws-id",
            target_lakehouse_id="target-lh-id",
            target_path="/Tables/dim_customers"
        )
        """)
        
        # Example 3: List all shortcuts
        print("\n3. Listing all shortcuts")
        print("-" * 60)
        
        shortcuts = manager.list_shortcuts(workspace_id, lakehouse_id)
        
        if shortcuts:
            print(f"✅ Found {len(shortcuts)} shortcuts:")
            for shortcut in shortcuts:
                print(f"\n   Name: {shortcut.get('name')}")
                print(f"   Type: {shortcut.get('target', {}).get('type')}")
                print(f"   Path: {shortcut.get('path')}")
        else:
            print("No shortcuts found in this lakehouse")
        
        # Example 4: S3 shortcut (informational)
        print("\n4. S3 Shortcut Example")
        print("-" * 60)
        print("ℹ️  To create an S3 shortcut:")
        print("""
        s3_shortcut = manager.create_s3_shortcut(
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id,
            shortcut_name="s3_external_data",
            bucket="my-s3-bucket",
            path="/data/raw/",
            region="us-east-1"
        )
        """)
        
        # Example 5: Shortcut best practices
        print("\n5. Shortcut Best Practices")
        print("-" * 60)
        print("""
        ✓ Use shortcuts for:
          - Accessing external data without copying
          - Sharing data between workspaces
          - Reducing storage costs
          - Creating virtual data lakes
        
        ✓ Naming conventions:
          - Use descriptive names: 'ext_raw_sales', 'shared_dim_customers'
          - Include source indicator: 'adls_', 's3_', 'onelake_'
        
        ✓ Security:
          - Use connections for authentication
          - Grant minimal required permissions
          - Audit shortcut access regularly
        
        ✓ Performance:
          - Shortcuts have same performance as local data
          - Consider network latency for cross-region shortcuts
          - Use shortcuts for large datasets to avoid duplication
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Detailed error:")
    
    print("\n" + "=" * 60)
    print("Lakehouse shortcuts examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
