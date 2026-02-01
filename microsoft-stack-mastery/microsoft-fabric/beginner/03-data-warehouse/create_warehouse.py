"""
Microsoft Fabric Data Warehouse Creation Module

This module demonstrates creating and managing Fabric Data Warehouses
programmatically using the Fabric REST API.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from typing import Optional, Dict, Any, List

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


class FabricWarehouseManager:
    """
    Manager for Microsoft Fabric Data Warehouse operations.
    
    Provides methods to create, configure, and manage warehouses.
    """
    
    BASE_URL = "https://api.fabric.microsoft.com/v1"
    
    def __init__(self, authenticator: FabricAuthenticator):
        """
        Initialize Warehouse Manager.
        
        Args:
            authenticator (FabricAuthenticator): Authentication handler
        """
        self.auth = authenticator
        self.session = requests.Session()
        logger.info("Initialized FabricWarehouseManager")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return self.auth.get_auth_headers()
    
    def create_warehouse(
        self,
        workspace_id: str,
        display_name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new data warehouse in a workspace.
        
        Args:
            workspace_id (str): Workspace ID where warehouse will be created
            display_name (str): Warehouse display name
            description (str, optional): Warehouse description
        
        Returns:
            dict: Created warehouse details
        
        Example:
            >>> manager = FabricWarehouseManager(auth)
            >>> warehouse = manager.create_warehouse(
            ...     workspace_id="abc-123",
            ...     display_name="sales_warehouse",
            ...     description="Data warehouse for sales analytics"
            ... )
        """
        logger.info(f"Creating warehouse '{display_name}' in workspace {workspace_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/warehouses"
        
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
            warehouse_data = response.json()
            
            logger.info(
                f"✅ Warehouse '{display_name}' created successfully. "
                f"ID: {warehouse_data.get('id')}"
            )
            
            return warehouse_data
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to create warehouse: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            raise
    
    def get_warehouse(
        self,
        workspace_id: str,
        warehouse_id: str
    ) -> Dict[str, Any]:
        """
        Get warehouse details.
        
        Args:
            workspace_id (str): Workspace ID
            warehouse_id (str): Warehouse ID
        
        Returns:
            dict: Warehouse details
        """
        logger.info(f"Fetching warehouse {warehouse_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/warehouses/{warehouse_id}"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            warehouse_data = response.json()
            
            logger.info(f"✅ Retrieved warehouse: {warehouse_data.get('displayName')}")
            return warehouse_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get warehouse: {str(e)}")
            raise
    
    def list_warehouses(
        self,
        workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all warehouses in a workspace.
        
        Args:
            workspace_id (str): Workspace ID
        
        Returns:
            list: List of warehouse details
        """
        logger.info(f"Listing warehouses in workspace {workspace_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/warehouses"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            warehouses = data.get('value', [])
            
            logger.info(f"✅ Found {len(warehouses)} warehouses")
            return warehouses
            
        except Exception as e:
            logger.error(f"❌ Failed to list warehouses: {str(e)}")
            raise
    
    def delete_warehouse(
        self,
        workspace_id: str,
        warehouse_id: str
    ) -> bool:
        """
        Delete a warehouse.
        
        Args:
            workspace_id (str): Workspace ID
            warehouse_id (str): Warehouse ID to delete
        
        Returns:
            bool: True if deletion successful
        
        Warning:
            This is irreversible. All data and objects will be deleted.
        """
        logger.warning(f"Deleting warehouse {warehouse_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/warehouses/{warehouse_id}"
        
        try:
            response = self.session.delete(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            logger.info(f"✅ Warehouse {warehouse_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete warehouse: {str(e)}")
            raise
    
    def update_warehouse(
        self,
        workspace_id: str,
        warehouse_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update warehouse properties.
        
        Args:
            workspace_id (str): Workspace ID
            warehouse_id (str): Warehouse ID
            display_name (str, optional): New display name
            description (str, optional): New description
        
        Returns:
            dict: Updated warehouse details
        """
        logger.info(f"Updating warehouse {warehouse_id}")
        
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/warehouses/{warehouse_id}"
        
        payload = {}
        if display_name:
            payload["displayName"] = display_name
        if description:
            payload["description"] = description
        
        if not payload:
            logger.warning("No updates provided")
            return self.get_warehouse(workspace_id, warehouse_id)
        
        try:
            response = self.session.patch(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            logger.info(f"✅ Warehouse updated successfully")
            
            return self.get_warehouse(workspace_id, warehouse_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to update warehouse: {str(e)}")
            raise
    
    def get_connection_string(
        self,
        workspace_id: str,
        warehouse_id: str
    ) -> str:
        """
        Get SQL connection string for the warehouse.
        
        Args:
            workspace_id (str): Workspace ID
            warehouse_id (str): Warehouse ID
        
        Returns:
            str: Connection string
        
        Note:
            Connection strings follow the format:
            <workspace-name>.datawarehouse.fabric.microsoft.com
        """
        warehouse = self.get_warehouse(workspace_id, warehouse_id)
        
        # Construct connection string
        warehouse_name = warehouse.get('displayName')
        connection_string = (
            f"{warehouse_name}.datawarehouse.fabric.microsoft.com"
        )
        
        logger.info(f"Connection string: {connection_string}")
        return connection_string


def main():
    """
    Example usage of Fabric Warehouse Manager.
    """
    print("=" * 60)
    print("Microsoft Fabric Data Warehouse Creation Examples")
    print("=" * 60)
    
    workspace_id = os.getenv("WORKSPACE_ID")
    
    if not workspace_id:
        print("❌ WORKSPACE_ID environment variable not set")
        return
    
    try:
        # Initialize manager
        auth = FabricAuthenticator(auth_method="default")
        manager = FabricWarehouseManager(auth)
        
        # Example 1: Create a warehouse
        print("\n1. Creating a data warehouse")
        print("-" * 60)
        
        from datetime import datetime
        warehouse = manager.create_warehouse(
            workspace_id=workspace_id,
            display_name=f"demo_warehouse_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Demo warehouse for analytics"
        )
        
        warehouse_id = warehouse.get('id')
        print(f"✅ Created warehouse: {warehouse.get('displayName')}")
        print(f"   ID: {warehouse_id}")
        
        # Example 2: Get warehouse details
        print("\n2. Getting warehouse details")
        print("-" * 60)
        
        details = manager.get_warehouse(workspace_id, warehouse_id)
        print(f"✅ Warehouse Details:")
        print(f"   Name: {details.get('displayName')}")
        print(f"   Type: {details.get('type')}")
        print(f"   Created: {details.get('createdDate')}")
        
        # Example 3: List all warehouses
        print("\n3. Listing all warehouses")
        print("-" * 60)
        
        warehouses = manager.list_warehouses(workspace_id)
        print(f"✅ Found {len(warehouses)} warehouses:")
        for wh in warehouses[:5]:
            print(f"   - {wh.get('displayName')} ({wh.get('id')})")
        
        # Example 4: Update warehouse
        print("\n4. Updating warehouse")
        print("-" * 60)
        
        updated = manager.update_warehouse(
            workspace_id=workspace_id,
            warehouse_id=warehouse_id,
            description="Updated description for demo warehouse"
        )
        print(f"✅ Updated warehouse: {updated.get('displayName')}")
        print(f"   New description: {updated.get('description')}")
        
        # Example 5: Get connection string
        print("\n5. Getting connection string")
        print("-" * 60)
        
        conn_str = manager.get_connection_string(workspace_id, warehouse_id)
        print(f"✅ Connection string: {conn_str}")
        
        # Example 6: Warehouse vs Lakehouse guidance
        print("\n6. When to use Warehouse vs Lakehouse")
        print("-" * 60)
        print("""
        Use Warehouse when:
        ✓ You need strong schema enforcement
        ✓ Running complex SQL analytics (T-SQL)
        ✓ Building traditional dimensional models (star/snowflake)
        ✓ Row-level ACID transactions are critical
        ✓ Connecting BI tools that expect SQL endpoints
        
        Use Lakehouse when:
        ✓ Working with semi-structured/unstructured data
        ✓ Need schema-on-read flexibility
        ✓ Performing big data processing with Spark
        ✓ Building medallion architecture (bronze/silver/gold)
        ✓ Cost-effective storage for large data volumes
        """)
        
        # Clean up (optional - uncomment to delete)
        # print("\n7. Cleaning up demo warehouse")
        # print("-" * 60)
        # manager.delete_warehouse(workspace_id, warehouse_id)
        # print("✅ Demo warehouse deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Detailed error:")
    
    print("\n" + "=" * 60)
    print("Warehouse creation examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
