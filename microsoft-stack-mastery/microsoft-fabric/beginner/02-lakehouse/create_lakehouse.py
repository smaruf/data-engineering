"""
Microsoft Fabric Lakehouse Creation Module

This module demonstrates how to create and manage Microsoft Fabric Lakehouses
programmatically using the Fabric REST API.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests
from dotenv import load_dotenv

# Import authentication module
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from beginner.fabric_setup.authentication import FabricAuthenticator, FabricAuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class FabricLakehouseManager:
    """
    Manager for Microsoft Fabric Lakehouse operations.
    
    Provides methods to create, configure, and manage lakehouses.
    """
    
    BASE_URL = "https://api.fabric.microsoft.com/v1"
    
    def __init__(self, authenticator: FabricAuthenticator):
        """
        Initialize Lakehouse Manager.
        
        Args:
            authenticator (FabricAuthenticator): Authentication handler
        """
        self.auth = authenticator
        self.session = requests.Session()
        logger.info("Initialized FabricLakehouseManager")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return self.auth.get_auth_headers()
    
    def create_lakehouse(
        self,
        workspace_id: str,
        display_name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new lakehouse in a workspace.
        
        Args:
            workspace_id (str): Workspace ID where lakehouse will be created
            display_name (str): Lakehouse display name
            description (str, optional): Lakehouse description
        
        Returns:
            dict: Created lakehouse details including ID and properties
        
        Raises:
            Exception: If lakehouse creation fails
        
        Example:
            >>> manager = FabricLakehouseManager(auth)
            >>> lakehouse = manager.create_lakehouse(
            ...     workspace_id="abc-123",
            ...     display_name="sales_data_lakehouse",
            ...     description="Lakehouse for sales analytics"
            ... )
            >>> print(lakehouse['id'])
        """
        logger.info(f"Creating lakehouse '{display_name}' in workspace {workspace_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/lakehouses"
        
        payload = {
            "displayName": display_name
        }
        
        if description:
            payload["description"] = description
        
        try:
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            lakehouse_data = response.json()
            
            logger.info(
                f"✅ Lakehouse '{display_name}' created successfully. "
                f"ID: {lakehouse_data.get('id')}"
            )
            
            return lakehouse_data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to create lakehouse: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error creating lakehouse: {str(e)}")
            raise
    
    def get_lakehouse(
        self,
        workspace_id: str,
        lakehouse_id: str
    ) -> Dict[str, Any]:
        """
        Get lakehouse details.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
        
        Returns:
            dict: Lakehouse details
        """
        logger.info(f"Fetching lakehouse {lakehouse_id} from workspace {workspace_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            lakehouse_data = response.json()
            
            logger.info(f"✅ Retrieved lakehouse: {lakehouse_data.get('displayName')}")
            return lakehouse_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get lakehouse: {str(e)}")
            raise
    
    def list_lakehouses(
        self,
        workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all lakehouses in a workspace.
        
        Args:
            workspace_id (str): Workspace ID
        
        Returns:
            list: List of lakehouse details
        """
        logger.info(f"Listing lakehouses in workspace {workspace_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/lakehouses"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            lakehouses = data.get('value', [])
            
            logger.info(f"✅ Found {len(lakehouses)} lakehouses")
            return lakehouses
            
        except Exception as e:
            logger.error(f"❌ Failed to list lakehouses: {str(e)}")
            raise
    
    def delete_lakehouse(
        self,
        workspace_id: str,
        lakehouse_id: str
    ) -> bool:
        """
        Delete a lakehouse.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID to delete
        
        Returns:
            bool: True if deletion successful
        
        Warning:
            This operation is irreversible. All data in the lakehouse will be deleted.
        """
        logger.warning(f"Deleting lakehouse {lakehouse_id} from workspace {workspace_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
        
        try:
            response = self.session.delete(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            logger.info(f"✅ Lakehouse {lakehouse_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete lakehouse: {str(e)}")
            raise
    
    def update_lakehouse(
        self,
        workspace_id: str,
        lakehouse_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update lakehouse properties.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
            display_name (str, optional): New display name
            description (str, optional): New description
        
        Returns:
            dict: Updated lakehouse details
        """
        logger.info(f"Updating lakehouse {lakehouse_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
        
        payload = {}
        if display_name:
            payload["displayName"] = display_name
        if description:
            payload["description"] = description
        
        if not payload:
            logger.warning("No updates provided")
            return self.get_lakehouse(workspace_id, lakehouse_id)
        
        try:
            response = self.session.patch(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            logger.info(f"✅ Lakehouse updated successfully")
            
            # Return updated lakehouse details
            return self.get_lakehouse(workspace_id, lakehouse_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to update lakehouse: {str(e)}")
            raise
    
    def get_lakehouse_tables(
        self,
        workspace_id: str,
        lakehouse_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of tables in a lakehouse.
        
        Args:
            workspace_id (str): Workspace ID
            lakehouse_id (str): Lakehouse ID
        
        Returns:
            list: List of tables
        """
        logger.info(f"Fetching tables from lakehouse {lakehouse_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            tables = data.get('value', [])
            
            logger.info(f"✅ Found {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"❌ Failed to get tables: {str(e)}")
            raise


def create_sample_lakehouses(workspace_id: str) -> List[Dict[str, Any]]:
    """
    Create sample lakehouses for demonstration.
    
    Args:
        workspace_id (str): Workspace ID where lakehouses will be created
    
    Returns:
        list: List of created lakehouses
    """
    # Initialize authenticator
    auth = FabricAuthenticator(auth_method="default")
    manager = FabricLakehouseManager(auth)
    
    lakehouses_config = [
        {
            "display_name": "bronze_lakehouse",
            "description": "Raw data landing zone - Bronze layer of medallion architecture"
        },
        {
            "display_name": "silver_lakehouse",
            "description": "Cleaned and validated data - Silver layer of medallion architecture"
        },
        {
            "display_name": "gold_lakehouse",
            "description": "Business-level aggregated data - Gold layer of medallion architecture"
        }
    ]
    
    created_lakehouses = []
    
    for config in lakehouses_config:
        try:
            lakehouse = manager.create_lakehouse(
                workspace_id=workspace_id,
                **config
            )
            created_lakehouses.append(lakehouse)
            
            # Print lakehouse details
            print(f"\n{'='*60}")
            print(f"Lakehouse: {lakehouse.get('displayName')}")
            print(f"ID: {lakehouse.get('id')}")
            print(f"Description: {lakehouse.get('description')}")
            print(f"Created: {lakehouse.get('createdDate')}")
            print(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"Failed to create lakehouse {config['display_name']}: {e}")
    
    return created_lakehouses


def main():
    """
    Example usage of Fabric Lakehouse Manager.
    """
    print("=" * 60)
    print("Microsoft Fabric Lakehouse Creation Examples")
    print("=" * 60)
    
    # Get workspace ID from environment
    workspace_id = os.getenv("WORKSPACE_ID")
    
    if not workspace_id:
        print("❌ WORKSPACE_ID environment variable not set")
        print("Please set WORKSPACE_ID in your .env file")
        return
    
    try:
        # Initialize authenticator and manager
        auth = FabricAuthenticator(auth_method="default")
        manager = FabricLakehouseManager(auth)
        
        # Example 1: Create a single lakehouse
        print("\n1. Creating a single lakehouse")
        print("-" * 60)
        lakehouse = manager.create_lakehouse(
            workspace_id=workspace_id,
            display_name=f"demo_lakehouse_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Demo lakehouse created programmatically"
        )
        
        lakehouse_id = lakehouse.get('id')
        print(f"✅ Created lakehouse: {lakehouse.get('displayName')}")
        print(f"   ID: {lakehouse_id}")
        
        # Example 2: Get lakehouse details
        print("\n2. Getting lakehouse details")
        print("-" * 60)
        details = manager.get_lakehouse(workspace_id, lakehouse_id)
        print(f"✅ Retrieved lakehouse details:")
        print(f"   Name: {details.get('displayName')}")
        print(f"   Type: {details.get('type')}")
        print(f"   Created: {details.get('createdDate')}")
        
        # Example 3: List all lakehouses
        print("\n3. Listing all lakehouses in workspace")
        print("-" * 60)
        lakehouses = manager.list_lakehouses(workspace_id)
        print(f"✅ Found {len(lakehouses)} lakehouses:")
        for lh in lakehouses[:5]:  # Show first 5
            print(f"   - {lh.get('displayName')} ({lh.get('id')})")
        
        # Example 4: Update lakehouse
        print("\n4. Updating lakehouse")
        print("-" * 60)
        updated = manager.update_lakehouse(
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id,
            description="Updated description for demo lakehouse"
        )
        print(f"✅ Updated lakehouse: {updated.get('displayName')}")
        print(f"   New description: {updated.get('description')}")
        
        # Example 5: Get lakehouse tables
        print("\n5. Getting lakehouse tables")
        print("-" * 60)
        tables = manager.get_lakehouse_tables(workspace_id, lakehouse_id)
        print(f"✅ Found {len(tables)} tables in lakehouse")
        for table in tables:
            print(f"   - {table.get('name')}")
        
        # Example 6: Create medallion architecture lakehouses
        print("\n6. Creating Medallion Architecture (Bronze/Silver/Gold)")
        print("-" * 60)
        print("Creating bronze, silver, and gold lakehouses...")
        medallion_lakehouses = create_sample_lakehouses(workspace_id)
        print(f"✅ Created {len(medallion_lakehouses)} lakehouses for medallion architecture")
        
        # Clean up demo lakehouse (optional - uncomment to delete)
        # print("\n7. Cleaning up demo lakehouse")
        # print("-" * 60)
        # manager.delete_lakehouse(workspace_id, lakehouse_id)
        # print(f"✅ Deleted demo lakehouse")
        
    except FabricAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Detailed error:")
    
    print("\n" + "=" * 60)
    print("Lakehouse creation examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
