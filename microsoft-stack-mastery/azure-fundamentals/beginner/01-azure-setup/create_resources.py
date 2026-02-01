"""
Azure Resource Creation Example

This module demonstrates how to create Azure resources programmatically using
the Azure SDK for Python. It covers resource groups, storage accounts, and
basic resource management operations.

Requirements:
    pip install azure-identity azure-mgmt-resource azure-mgmt-storage

Environment Variables:
    AZURE_SUBSCRIPTION_ID: Your Azure subscription ID
    AZURE_TENANT_ID: Your Azure AD tenant ID (optional for DefaultAzureCredential)
    AZURE_CLIENT_ID: Service principal client ID (optional)
    AZURE_CLIENT_SECRET: Service principal secret (optional)
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    Kind,
    StorageAccountUpdateParameters
)
from azure.core.exceptions import AzureError, ResourceExistsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureResourceManager:
    """
    Manages Azure resource creation and lifecycle operations.
    
    This class provides methods to create and manage Azure resources including
    resource groups, storage accounts, and other core infrastructure components.
    """
    
    def __init__(self, subscription_id: Optional[str] = None):
        """
        Initialize Azure Resource Manager.
        
        Args:
            subscription_id: Azure subscription ID. If None, reads from environment.
        
        Raises:
            ValueError: If subscription ID is not provided or found in environment.
        """
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        
        if not self.subscription_id:
            raise ValueError(
                "Azure subscription ID must be provided or set in "
                "AZURE_SUBSCRIPTION_ID environment variable"
            )
        
        # Initialize credential using DefaultAzureCredential
        # This supports multiple authentication methods in order:
        # 1. Environment variables
        # 2. Managed Identity
        # 3. Visual Studio Code
        # 4. Azure CLI
        # 5. Azure PowerShell
        logger.info("Initializing Azure credentials...")
        self.credential = DefaultAzureCredential()
        
        # Initialize management clients
        self.resource_client = ResourceManagementClient(
            self.credential,
            self.subscription_id
        )
        self.storage_client = StorageManagementClient(
            self.credential,
            self.subscription_id
        )
        
        logger.info(f"Initialized for subscription: {self.subscription_id}")
    
    def create_resource_group(
        self,
        resource_group_name: str,
        location: str = "eastus",
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create an Azure resource group.
        
        Args:
            resource_group_name: Name of the resource group
            location: Azure region (default: eastus)
            tags: Optional tags for the resource group
        
        Returns:
            Dictionary containing resource group details
        
        Raises:
            AzureError: If resource group creation fails
        """
        try:
            logger.info(f"Creating resource group: {resource_group_name}")
            
            # Add default tags
            resource_tags = tags or {}
            resource_tags.update({
                'created_by': 'azure-sdk-python',
                'created_at': datetime.utcnow().isoformat(),
                'environment': 'development'
            })
            
            # Create resource group
            resource_group = self.resource_client.resource_groups.create_or_update(
                resource_group_name,
                {
                    'location': location,
                    'tags': resource_tags
                }
            )
            
            logger.info(
                f"Successfully created resource group: {resource_group.name} "
                f"in location: {resource_group.location}"
            )
            
            return {
                'name': resource_group.name,
                'location': resource_group.location,
                'id': resource_group.id,
                'tags': resource_group.tags,
                'provisioning_state': resource_group.properties.provisioning_state
            }
            
        except ResourceExistsError:
            logger.warning(f"Resource group {resource_group_name} already exists")
            existing_rg = self.resource_client.resource_groups.get(resource_group_name)
            return {
                'name': existing_rg.name,
                'location': existing_rg.location,
                'id': existing_rg.id,
                'tags': existing_rg.tags,
                'provisioning_state': 'Existing'
            }
            
        except AzureError as e:
            logger.error(f"Failed to create resource group: {e}")
            raise
    
    def create_storage_account(
        self,
        resource_group_name: str,
        storage_account_name: str,
        location: str = "eastus",
        sku_name: str = "Standard_LRS",
        kind: str = "StorageV2",
        enable_https_only: bool = True,
        enable_hierarchical_namespace: bool = False,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create an Azure Storage account.
        
        Args:
            resource_group_name: Name of the resource group
            storage_account_name: Name of the storage account (must be globally unique)
            location: Azure region (default: eastus)
            sku_name: SKU tier (Standard_LRS, Standard_GRS, etc.)
            kind: Storage account kind (StorageV2, BlobStorage, etc.)
            enable_https_only: Require HTTPS for storage access
            enable_hierarchical_namespace: Enable Data Lake Gen2 (default: False)
            tags: Optional tags for the storage account
        
        Returns:
            Dictionary containing storage account details
        
        Raises:
            AzureError: If storage account creation fails
        """
        try:
            logger.info(f"Creating storage account: {storage_account_name}")
            
            # Validate storage account name
            if not self._validate_storage_account_name(storage_account_name):
                raise ValueError(
                    "Storage account name must be 3-24 characters, "
                    "lowercase letters and numbers only"
                )
            
            # Add default tags
            storage_tags = tags or {}
            storage_tags.update({
                'created_by': 'azure-sdk-python',
                'created_at': datetime.utcnow().isoformat(),
                'purpose': 'data-engineering'
            })
            
            # Create storage account parameters
            params = StorageAccountCreateParameters(
                sku=Sku(name=sku_name),
                kind=kind,
                location=location,
                tags=storage_tags,
                enable_https_traffic_only=enable_https_only,
                is_hns_enabled=enable_hierarchical_namespace,
                allow_blob_public_access=False,  # Security best practice
                minimum_tls_version='TLS1_2'  # Security best practice
            )
            
            # Begin async operation to create storage account
            logger.info("Starting storage account creation (this may take a minute)...")
            poller = self.storage_client.storage_accounts.begin_create(
                resource_group_name,
                storage_account_name,
                params
            )
            
            # Wait for completion
            storage_account = poller.result()
            
            logger.info(
                f"Successfully created storage account: {storage_account.name} "
                f"with SKU: {storage_account.sku.name}"
            )
            
            # Get account keys
            keys = self.storage_client.storage_accounts.list_keys(
                resource_group_name,
                storage_account_name
            )
            
            return {
                'name': storage_account.name,
                'location': storage_account.location,
                'id': storage_account.id,
                'sku': storage_account.sku.name,
                'kind': storage_account.kind,
                'primary_endpoints': {
                    'blob': storage_account.primary_endpoints.blob,
                    'dfs': storage_account.primary_endpoints.dfs,
                    'file': storage_account.primary_endpoints.file,
                    'queue': storage_account.primary_endpoints.queue,
                    'table': storage_account.primary_endpoints.table
                },
                'primary_key': keys.keys[0].value,
                'provisioning_state': storage_account.provisioning_state
            }
            
        except AzureError as e:
            logger.error(f"Failed to create storage account: {e}")
            raise
    
    def list_resource_groups(self) -> list:
        """
        List all resource groups in the subscription.
        
        Returns:
            List of resource group details
        """
        try:
            logger.info("Listing resource groups...")
            resource_groups = []
            
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append({
                    'name': rg.name,
                    'location': rg.location,
                    'id': rg.id,
                    'tags': rg.tags
                })
            
            logger.info(f"Found {len(resource_groups)} resource groups")
            return resource_groups
            
        except AzureError as e:
            logger.error(f"Failed to list resource groups: {e}")
            raise
    
    def list_storage_accounts(self, resource_group_name: Optional[str] = None) -> list:
        """
        List storage accounts.
        
        Args:
            resource_group_name: If provided, list only storage accounts in this RG
        
        Returns:
            List of storage account details
        """
        try:
            logger.info("Listing storage accounts...")
            storage_accounts = []
            
            if resource_group_name:
                accounts = self.storage_client.storage_accounts.list_by_resource_group(
                    resource_group_name
                )
            else:
                accounts = self.storage_client.storage_accounts.list()
            
            for account in accounts:
                storage_accounts.append({
                    'name': account.name,
                    'location': account.location,
                    'sku': account.sku.name,
                    'kind': account.kind,
                    'resource_group': account.id.split('/')[4]
                })
            
            logger.info(f"Found {len(storage_accounts)} storage accounts")
            return storage_accounts
            
        except AzureError as e:
            logger.error(f"Failed to list storage accounts: {e}")
            raise
    
    def delete_resource_group(
        self,
        resource_group_name: str,
        wait: bool = False
    ) -> bool:
        """
        Delete a resource group and all its resources.
        
        Args:
            resource_group_name: Name of the resource group to delete
            wait: If True, wait for deletion to complete
        
        Returns:
            True if deletion started successfully
        
        Raises:
            AzureError: If deletion fails
        """
        try:
            logger.warning(f"Deleting resource group: {resource_group_name}")
            
            # Begin async delete operation
            poller = self.resource_client.resource_groups.begin_delete(
                resource_group_name
            )
            
            if wait:
                logger.info("Waiting for resource group deletion to complete...")
                poller.result()
                logger.info(f"Successfully deleted resource group: {resource_group_name}")
            else:
                logger.info(f"Resource group deletion initiated: {resource_group_name}")
            
            return True
            
        except AzureError as e:
            logger.error(f"Failed to delete resource group: {e}")
            raise
    
    @staticmethod
    def _validate_storage_account_name(name: str) -> bool:
        """
        Validate storage account name follows Azure naming rules.
        
        Args:
            name: Storage account name to validate
        
        Returns:
            True if valid, False otherwise
        """
        if len(name) < 3 or len(name) > 24:
            return False
        if not name.islower():
            return False
        if not name.isalnum():
            return False
        return True


def main():
    """
    Main function demonstrating Azure resource creation.
    """
    try:
        # Initialize resource manager
        logger.info("=" * 60)
        logger.info("Azure Resource Creation Example")
        logger.info("=" * 60)
        
        resource_manager = AzureResourceManager()
        
        # Configuration
        resource_group_name = "rg-data-engineering-demo"
        storage_account_name = "stdataengdemo001"  # Must be globally unique
        location = "eastus"
        
        # Create resource group
        logger.info("\n--- Creating Resource Group ---")
        rg_result = resource_manager.create_resource_group(
            resource_group_name=resource_group_name,
            location=location,
            tags={
                'project': 'data-engineering-demo',
                'owner': 'data-team'
            }
        )
        logger.info(f"Resource Group Details: {rg_result}")
        
        # Create storage account
        logger.info("\n--- Creating Storage Account ---")
        storage_result = resource_manager.create_storage_account(
            resource_group_name=resource_group_name,
            storage_account_name=storage_account_name,
            location=location,
            sku_name="Standard_LRS",
            kind="StorageV2",
            enable_hierarchical_namespace=False,  # Set to True for Data Lake Gen2
            tags={
                'project': 'data-engineering-demo',
                'type': 'blob-storage'
            }
        )
        logger.info(f"Storage Account Created: {storage_result['name']}")
        logger.info(f"Blob Endpoint: {storage_result['primary_endpoints']['blob']}")
        
        # List resource groups
        logger.info("\n--- Listing Resource Groups ---")
        resource_groups = resource_manager.list_resource_groups()
        for rg in resource_groups[:5]:  # Show first 5
            logger.info(f"  - {rg['name']} ({rg['location']})")
        
        # List storage accounts
        logger.info("\n--- Listing Storage Accounts ---")
        storage_accounts = resource_manager.list_storage_accounts(resource_group_name)
        for account in storage_accounts:
            logger.info(f"  - {account['name']} ({account['sku']})")
        
        # Cleanup (commented out for safety - uncomment to delete)
        # logger.info("\n--- Cleanup ---")
        # resource_manager.delete_resource_group(resource_group_name, wait=False)
        # logger.info("Cleanup initiated. Resources will be deleted in background.")
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info("\nIMPORTANT: Remember to delete resources to avoid charges:")
        logger.info(f"  az group delete --name {resource_group_name} --yes")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
