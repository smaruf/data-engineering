"""
Azure Virtual Machine Operations

This module demonstrates managing Azure Virtual Machines using the Azure SDK.
Covers VM creation, management, and lifecycle operations.

Requirements:
    pip install azure-identity azure-mgmt-compute azure-mgmt-network azure-mgmt-resource

Environment Variables:
    AZURE_SUBSCRIPTION_ID: Azure subscription ID
    AZURE_RESOURCE_GROUP: Resource group name
    AZURE_LOCATION: Azure region (e.g., eastus)
"""

import os
import logging
from typing import Optional, Dict, Any, List

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute.models import (
    VirtualMachine,
    HardwareProfile,
    StorageProfile,
    OSProfile,
    NetworkProfile,
    ImageReference,
    OSDisk,
    DiskCreateOptionTypes,
    NetworkInterfaceReference,
    LinuxConfiguration,
    SshConfiguration,
    SshPublicKey
)
from azure.core.exceptions import AzureError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureVMManager:
    """
    Manages Azure Virtual Machine operations.
    
    Provides methods for creating, starting, stopping, and managing VMs.
    """
    
    def __init__(
        self,
        subscription_id: Optional[str] = None,
        resource_group: Optional[str] = None,
        location: str = "eastus"
    ):
        """
        Initialize VM manager.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            location: Azure region
        """
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = resource_group or os.getenv('AZURE_RESOURCE_GROUP')
        self.location = location or os.getenv('AZURE_LOCATION', 'eastus')
        
        if not self.subscription_id:
            raise ValueError("Subscription ID required. Set AZURE_SUBSCRIPTION_ID")
        
        # Initialize credential
        self.credential = DefaultAzureCredential()
        
        # Initialize management clients
        self.compute_client = ComputeManagementClient(
            self.credential,
            self.subscription_id
        )
        
        self.network_client = NetworkManagementClient(
            self.credential,
            self.subscription_id
        )
        
        self.resource_client = ResourceManagementClient(
            self.credential,
            self.subscription_id
        )
        
        logger.info(f"Initialized VM manager for subscription: {self.subscription_id}")
    
    def create_vm(
        self,
        vm_name: str,
        username: str = "azureuser",
        vm_size: str = "Standard_B1s",
        image_publisher: str = "Canonical",
        image_offer: str = "UbuntuServer",
        image_sku: str = "18.04-LTS",
        ssh_public_key: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Linux virtual machine.
        
        Args:
            vm_name: Name of the VM
            username: Admin username
            vm_size: VM size (e.g., Standard_B1s, Standard_D2s_v3)
            image_publisher: Image publisher
            image_offer: Image offer
            image_sku: Image SKU
            ssh_public_key: SSH public key for authentication
            tags: Optional tags
        
        Returns:
            VM details
        """
        try:
            logger.info(f"Creating VM: {vm_name}")
            
            # Create resource group if needed
            if self.resource_group:
                self._ensure_resource_group()
            
            # Create network resources
            logger.info("Creating network resources...")
            nic_id = self._create_network_resources(vm_name)
            
            # Generate SSH key if not provided
            if not ssh_public_key:
                logger.warning("No SSH key provided. VM will not be accessible via SSH.")
                ssh_public_key = ""
            
            # Configure VM parameters
            vm_parameters = {
                'location': self.location,
                'os_profile': {
                    'computer_name': vm_name,
                    'admin_username': username,
                    'linux_configuration': {
                        'disable_password_authentication': True,
                        'ssh': {
                            'public_keys': [{
                                'path': f'/home/{username}/.ssh/authorized_keys',
                                'key_data': ssh_public_key
                            }]
                        } if ssh_public_key else None
                    }
                },
                'hardware_profile': {
                    'vm_size': vm_size
                },
                'storage_profile': {
                    'image_reference': {
                        'publisher': image_publisher,
                        'offer': image_offer,
                        'sku': image_sku,
                        'version': 'latest'
                    },
                    'os_disk': {
                        'create_option': DiskCreateOptionTypes.from_image,
                        'managed_disk': {
                            'storage_account_type': 'Standard_LRS'
                        }
                    }
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': nic_id
                    }]
                },
                'tags': tags or {'created_by': 'azure-sdk-python'}
            }
            
            # Create VM
            logger.info(f"Provisioning VM (this may take several minutes)...")
            poller = self.compute_client.virtual_machines.begin_create_or_update(
                self.resource_group,
                vm_name,
                vm_parameters
            )
            
            vm = poller.result()
            
            logger.info(f"VM created successfully: {vm_name}")
            
            return {
                'name': vm.name,
                'id': vm.id,
                'location': vm.location,
                'vm_size': vm.hardware_profile.vm_size,
                'provisioning_state': vm.provisioning_state
            }
            
        except AzureError as e:
            logger.error(f"Failed to create VM: {e}")
            raise
    
    def start_vm(self, vm_name: str) -> None:
        """
        Start a VM.
        
        Args:
            vm_name: Name of the VM
        """
        try:
            logger.info(f"Starting VM: {vm_name}")
            
            poller = self.compute_client.virtual_machines.begin_start(
                self.resource_group,
                vm_name
            )
            
            poller.result()
            logger.info(f"VM started: {vm_name}")
            
        except AzureError as e:
            logger.error(f"Failed to start VM: {e}")
            raise
    
    def stop_vm(self, vm_name: str, deallocate: bool = True) -> None:
        """
        Stop a VM.
        
        Args:
            vm_name: Name of the VM
            deallocate: If True, deallocate (no charges). If False, just power off.
        """
        try:
            logger.info(f"Stopping VM: {vm_name} (deallocate={deallocate})")
            
            if deallocate:
                poller = self.compute_client.virtual_machines.begin_deallocate(
                    self.resource_group,
                    vm_name
                )
            else:
                poller = self.compute_client.virtual_machines.begin_power_off(
                    self.resource_group,
                    vm_name
                )
            
            poller.result()
            logger.info(f"VM stopped: {vm_name}")
            
        except AzureError as e:
            logger.error(f"Failed to stop VM: {e}")
            raise
    
    def restart_vm(self, vm_name: str) -> None:
        """
        Restart a VM.
        
        Args:
            vm_name: Name of the VM
        """
        try:
            logger.info(f"Restarting VM: {vm_name}")
            
            poller = self.compute_client.virtual_machines.begin_restart(
                self.resource_group,
                vm_name
            )
            
            poller.result()
            logger.info(f"VM restarted: {vm_name}")
            
        except AzureError as e:
            logger.error(f"Failed to restart VM: {e}")
            raise
    
    def delete_vm(self, vm_name: str) -> None:
        """
        Delete a VM.
        
        Args:
            vm_name: Name of the VM
        """
        try:
            logger.warning(f"Deleting VM: {vm_name}")
            
            poller = self.compute_client.virtual_machines.begin_delete(
                self.resource_group,
                vm_name
            )
            
            poller.result()
            logger.info(f"VM deleted: {vm_name}")
            
        except AzureError as e:
            logger.error(f"Failed to delete VM: {e}")
            raise
    
    def get_vm_status(self, vm_name: str) -> Dict[str, Any]:
        """
        Get VM status.
        
        Args:
            vm_name: Name of the VM
        
        Returns:
            VM status information
        """
        try:
            instance_view = self.compute_client.virtual_machines.instance_view(
                self.resource_group,
                vm_name
            )
            
            statuses = []
            if instance_view.statuses:
                for status in instance_view.statuses:
                    statuses.append({
                        'code': status.code,
                        'level': status.level,
                        'display_status': status.display_status,
                        'message': status.message
                    })
            
            return {
                'vm_name': vm_name,
                'statuses': statuses,
                'vm_agent_version': instance_view.vm_agent.vm_agent_version if instance_view.vm_agent else None
            }
            
        except AzureError as e:
            logger.error(f"Failed to get VM status: {e}")
            raise
    
    def list_vms(self) -> List[Dict[str, Any]]:
        """
        List all VMs in the resource group.
        
        Returns:
            List of VM details
        """
        try:
            logger.info(f"Listing VMs in resource group: {self.resource_group}")
            
            vms = []
            for vm in self.compute_client.virtual_machines.list(self.resource_group):
                vms.append({
                    'name': vm.name,
                    'location': vm.location,
                    'vm_size': vm.hardware_profile.vm_size,
                    'provisioning_state': vm.provisioning_state
                })
            
            logger.info(f"Found {len(vms)} VMs")
            return vms
            
        except AzureError as e:
            logger.error(f"Failed to list VMs: {e}")
            raise
    
    def _ensure_resource_group(self) -> None:
        """Ensure resource group exists."""
        try:
            self.resource_client.resource_groups.create_or_update(
                self.resource_group,
                {'location': self.location}
            )
            logger.debug(f"Resource group ready: {self.resource_group}")
            
        except AzureError as e:
            logger.error(f"Failed to create resource group: {e}")
            raise
    
    def _create_network_resources(self, vm_name: str) -> str:
        """
        Create network resources for VM.
        
        Args:
            vm_name: VM name (used for resource naming)
        
        Returns:
            Network interface ID
        """
        vnet_name = f"{vm_name}-vnet"
        subnet_name = f"{vm_name}-subnet"
        public_ip_name = f"{vm_name}-ip"
        nic_name = f"{vm_name}-nic"
        
        # Create virtual network
        logger.debug(f"Creating virtual network: {vnet_name}")
        vnet_poller = self.network_client.virtual_networks.begin_create_or_update(
            self.resource_group,
            vnet_name,
            {
                'location': self.location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            }
        )
        vnet = vnet_poller.result()
        
        # Create subnet
        logger.debug(f"Creating subnet: {subnet_name}")
        subnet_poller = self.network_client.subnets.begin_create_or_update(
            self.resource_group,
            vnet_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet = subnet_poller.result()
        
        # Create public IP
        logger.debug(f"Creating public IP: {public_ip_name}")
        ip_poller = self.network_client.public_ip_addresses.begin_create_or_update(
            self.resource_group,
            public_ip_name,
            {
                'location': self.location,
                'public_ip_allocation_method': 'Dynamic'
            }
        )
        public_ip = ip_poller.result()
        
        # Create network interface
        logger.debug(f"Creating network interface: {nic_name}")
        nic_poller = self.network_client.network_interfaces.begin_create_or_update(
            self.resource_group,
            nic_name,
            {
                'location': self.location,
                'ip_configurations': [{
                    'name': 'ipconfig1',
                    'subnet': {'id': subnet.id},
                    'public_ip_address': {'id': public_ip.id}
                }]
            }
        )
        nic = nic_poller.result()
        
        return nic.id


def main():
    """
    Main function demonstrating VM operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Virtual Machine Operations Example")
        logger.info("=" * 60)
        
        # Initialize manager
        vm_manager = AzureVMManager(
            resource_group="demo-rg"
        )
        
        vm_name = "demo-vm"
        
        # Note: In production, generate or provide SSH key
        # ssh_key = "ssh-rsa AAAAB3... your-public-key"
        
        # Create VM (commented out to avoid accidental creation)
        # logger.info("\n--- Creating VM ---")
        # vm_details = vm_manager.create_vm(
        #     vm_name=vm_name,
        #     username="azureuser",
        #     vm_size="Standard_B1s",
        #     ssh_public_key=ssh_key
        # )
        # logger.info(f"VM Details: {vm_details}")
        
        # List VMs
        logger.info("\n--- Listing VMs ---")
        vms = vm_manager.list_vms()
        for vm in vms:
            logger.info(f"  - {vm['name']} ({vm['vm_size']}) - {vm['provisioning_state']}")
        
        # Get VM status (if VM exists)
        # logger.info("\n--- Getting VM Status ---")
        # status = vm_manager.get_vm_status(vm_name)
        # logger.info(f"Status: {status}")
        
        # Stop VM
        # logger.info("\n--- Stopping VM ---")
        # vm_manager.stop_vm(vm_name, deallocate=True)
        
        # Start VM
        # logger.info("\n--- Starting VM ---")
        # vm_manager.start_vm(vm_name)
        
        # Delete VM (commented out for safety)
        # logger.info("\n--- Deleting VM ---")
        # vm_manager.delete_vm(vm_name)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info("\nNote: VM creation is commented out to avoid accidental charges")
        logger.info("Uncomment the code to actually create and manage VMs")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
