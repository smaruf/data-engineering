"""
Azure Authentication Methods Example

This module demonstrates various authentication methods for Azure services using
the Azure Identity library. It covers different authentication scenarios from
development to production.

Requirements:
    pip install azure-identity azure-mgmt-resource azure-keyvault-secrets

Environment Variables:
    AZURE_SUBSCRIPTION_ID: Your Azure subscription ID
    AZURE_TENANT_ID: Your Azure AD tenant ID
    AZURE_CLIENT_ID: Service principal client ID
    AZURE_CLIENT_SECRET: Service principal secret
    AZURE_USERNAME: Azure username (for username/password auth)
    AZURE_PASSWORD: Azure password (for username/password auth)
"""

import os
import logging
from typing import Optional, Dict, Any

from azure.identity import (
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    ClientSecretCredential,
    InteractiveBrowserCredential,
    DeviceCodeCredential,
    AzureCliCredential,
    ChainedTokenCredential
)
from azure.mgmt.resource import SubscriptionClient
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ClientAuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureAuthenticationManager:
    """
    Demonstrates various Azure authentication methods and best practices.
    
    This class shows how to authenticate to Azure using different credential types
    depending on the execution environment (local development, CI/CD, production).
    """
    
    def __init__(self):
        """Initialize the authentication manager."""
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        logger.info("Authentication manager initialized")
    
    def authenticate_with_default_credential(self) -> TokenCredential:
        """
        Authenticate using DefaultAzureCredential.
        
        DefaultAzureCredential tries multiple authentication methods in order:
        1. EnvironmentCredential
        2. ManagedIdentityCredential
        3. SharedTokenCacheCredential
        4. VisualStudioCodeCredential
        5. AzureCliCredential
        6. AzurePowerShellCredential
        
        This is the recommended approach for most applications as it works
        across different environments without code changes.
        
        Returns:
            DefaultAzureCredential instance
        
        Raises:
            ClientAuthenticationError: If all authentication methods fail
        """
        try:
            logger.info("Authenticating with DefaultAzureCredential...")
            
            credential = DefaultAzureCredential(
                exclude_interactive_browser_credential=False,
                exclude_shared_token_cache_credential=False,
                exclude_visual_studio_code_credential=False,
                exclude_managed_identity_credential=False,
                exclude_environment_credential=False,
                exclude_cli_credential=False,
                exclude_powershell_credential=True
            )
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with DefaultAzureCredential")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"DefaultAzureCredential authentication failed: {e}")
            raise
    
    def authenticate_with_service_principal(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ) -> ClientSecretCredential:
        """
        Authenticate using a service principal (application identity).
        
        This method is ideal for:
        - Automated scripts and applications
        - CI/CD pipelines
        - Production workloads
        
        Args:
            tenant_id: Azure AD tenant ID (or from environment)
            client_id: Application (client) ID (or from environment)
            client_secret: Application secret (or from environment)
        
        Returns:
            ClientSecretCredential instance
        
        Raises:
            ValueError: If required parameters are missing
            ClientAuthenticationError: If authentication fails
        """
        try:
            logger.info("Authenticating with Service Principal...")
            
            tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
            client_id = client_id or os.getenv('AZURE_CLIENT_ID')
            client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')
            
            if not all([tenant_id, client_id, client_secret]):
                raise ValueError(
                    "Service principal authentication requires: "
                    "tenant_id, client_id, and client_secret"
                )
            
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Service Principal")
            logger.info(f"Tenant ID: {tenant_id}")
            logger.info(f"Client ID: {client_id}")
            
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Service Principal authentication failed: {e}")
            raise
    
    def authenticate_with_environment(self) -> EnvironmentCredential:
        """
        Authenticate using environment variables.
        
        Required environment variables:
        - AZURE_TENANT_ID
        - AZURE_CLIENT_ID
        - AZURE_CLIENT_SECRET
        
        This method is useful for containerized applications and CI/CD pipelines.
        
        Returns:
            EnvironmentCredential instance
        
        Raises:
            ClientAuthenticationError: If authentication fails
        """
        try:
            logger.info("Authenticating with Environment Credentials...")
            
            credential = EnvironmentCredential()
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Environment Credentials")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Environment credential authentication failed: {e}")
            raise
    
    def authenticate_with_managed_identity(
        self,
        client_id: Optional[str] = None
    ) -> ManagedIdentityCredential:
        """
        Authenticate using Managed Identity.
        
        Managed Identity provides an identity for applications running in Azure
        (VMs, App Services, Functions, etc.) without managing credentials.
        
        Args:
            client_id: Client ID for user-assigned managed identity (optional)
        
        Returns:
            ManagedIdentityCredential instance
        
        Raises:
            ClientAuthenticationError: If authentication fails
        
        Note:
            This only works when running inside Azure resources that support
            Managed Identity.
        """
        try:
            logger.info("Authenticating with Managed Identity...")
            
            if client_id:
                logger.info(f"Using user-assigned identity: {client_id}")
                credential = ManagedIdentityCredential(client_id=client_id)
            else:
                logger.info("Using system-assigned identity")
                credential = ManagedIdentityCredential()
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Managed Identity")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Managed Identity authentication failed: {e}")
            logger.error("This error is expected if not running in Azure")
            raise
    
    def authenticate_with_azure_cli(self) -> AzureCliCredential:
        """
        Authenticate using Azure CLI credentials.
        
        This method uses the credentials from 'az login' command.
        Perfect for local development when Azure CLI is already configured.
        
        Returns:
            AzureCliCredential instance
        
        Raises:
            ClientAuthenticationError: If Azure CLI is not logged in
        """
        try:
            logger.info("Authenticating with Azure CLI...")
            
            credential = AzureCliCredential()
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Azure CLI")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Azure CLI authentication failed: {e}")
            logger.error("Make sure you're logged in: az login")
            raise
    
    def authenticate_with_interactive_browser(
        self,
        tenant_id: Optional[str] = None
    ) -> InteractiveBrowserCredential:
        """
        Authenticate using interactive browser login.
        
        Opens a browser window for user authentication.
        Suitable for interactive scenarios and local development.
        
        Args:
            tenant_id: Azure AD tenant ID (optional)
        
        Returns:
            InteractiveBrowserCredential instance
        
        Raises:
            ClientAuthenticationError: If authentication fails
        """
        try:
            logger.info("Authenticating with Interactive Browser...")
            
            tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
            
            credential = InteractiveBrowserCredential(
                tenant_id=tenant_id
            ) if tenant_id else InteractiveBrowserCredential()
            
            logger.info("Browser window should open for authentication...")
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Interactive Browser")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Interactive browser authentication failed: {e}")
            raise
    
    def authenticate_with_device_code(
        self,
        tenant_id: Optional[str] = None
    ) -> DeviceCodeCredential:
        """
        Authenticate using device code flow.
        
        Displays a code that users enter on a separate device.
        Useful for:
        - Headless systems
        - SSH sessions
        - Systems without a browser
        
        Args:
            tenant_id: Azure AD tenant ID (optional)
        
        Returns:
            DeviceCodeCredential instance
        
        Raises:
            ClientAuthenticationError: If authentication fails
        """
        try:
            logger.info("Authenticating with Device Code...")
            
            tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
            
            credential = DeviceCodeCredential(
                tenant_id=tenant_id
            ) if tenant_id else DeviceCodeCredential()
            
            logger.info("Follow the instructions to authenticate...")
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Device Code")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Device code authentication failed: {e}")
            raise
    
    def authenticate_with_chained_credential(self) -> ChainedTokenCredential:
        """
        Authenticate using a chain of credentials.
        
        Tries multiple authentication methods in sequence until one succeeds.
        Useful for applications that run in multiple environments.
        
        Returns:
            ChainedTokenCredential instance
        
        Raises:
            ClientAuthenticationError: If all authentication methods fail
        """
        try:
            logger.info("Authenticating with Chained Credentials...")
            
            # Try credentials in order of preference
            credential = ChainedTokenCredential(
                EnvironmentCredential(),          # Try environment variables first
                ManagedIdentityCredential(),      # Try managed identity (if in Azure)
                AzureCliCredential()              # Fallback to Azure CLI
            )
            
            # Test the credential
            self._test_credential(credential)
            
            logger.info("Successfully authenticated with Chained Credentials")
            return credential
            
        except ClientAuthenticationError as e:
            logger.error(f"Chained credential authentication failed: {e}")
            raise
    
    def _test_credential(self, credential: TokenCredential) -> None:
        """
        Test a credential by making an API call.
        
        Args:
            credential: Credential to test
        
        Raises:
            ClientAuthenticationError: If credential is invalid
        """
        try:
            # Test by listing subscriptions
            subscription_client = SubscriptionClient(credential)
            subscriptions = list(subscription_client.subscriptions.list())
            
            logger.info(f"Credential validated. Access to {len(subscriptions)} subscription(s)")
            
            for sub in subscriptions[:3]:  # Show first 3
                logger.info(f"  - {sub.display_name} ({sub.subscription_id})")
                
        except Exception as e:
            logger.error(f"Credential test failed: {e}")
            raise ClientAuthenticationError(f"Invalid credential: {e}")
    
    def get_recommended_credential(self) -> TokenCredential:
        """
        Get the recommended credential based on available environment.
        
        Returns:
            Most appropriate credential for the current environment
        """
        logger.info("Determining best authentication method...")
        
        # Check for service principal in environment
        if all([
            os.getenv('AZURE_TENANT_ID'),
            os.getenv('AZURE_CLIENT_ID'),
            os.getenv('AZURE_CLIENT_SECRET')
        ]):
            logger.info("Service principal credentials found in environment")
            return self.authenticate_with_service_principal()
        
        # Check for Azure CLI
        try:
            return self.authenticate_with_azure_cli()
        except ClientAuthenticationError:
            pass
        
        # Fallback to DefaultAzureCredential
        logger.info("Using DefaultAzureCredential as fallback")
        return self.authenticate_with_default_credential()


def main():
    """
    Main function demonstrating various authentication methods.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Authentication Methods Example")
        logger.info("=" * 60)
        
        auth_manager = AzureAuthenticationManager()
        
        # Method 1: DefaultAzureCredential (Recommended for most cases)
        logger.info("\n--- Method 1: DefaultAzureCredential ---")
        try:
            credential1 = auth_manager.authenticate_with_default_credential()
            logger.info("✓ DefaultAzureCredential works!")
        except Exception as e:
            logger.warning(f"✗ DefaultAzureCredential failed: {e}")
        
        # Method 2: Azure CLI Credential
        logger.info("\n--- Method 2: Azure CLI Credential ---")
        try:
            credential2 = auth_manager.authenticate_with_azure_cli()
            logger.info("✓ Azure CLI Credential works!")
        except Exception as e:
            logger.warning(f"✗ Azure CLI Credential failed: {e}")
        
        # Method 3: Service Principal (if configured)
        logger.info("\n--- Method 3: Service Principal ---")
        try:
            credential3 = auth_manager.authenticate_with_service_principal()
            logger.info("✓ Service Principal Credential works!")
        except Exception as e:
            logger.warning(f"✗ Service Principal failed: {e}")
        
        # Method 4: Environment Credential
        logger.info("\n--- Method 4: Environment Credential ---")
        try:
            credential4 = auth_manager.authenticate_with_environment()
            logger.info("✓ Environment Credential works!")
        except Exception as e:
            logger.warning(f"✗ Environment Credential failed: {e}")
        
        # Method 5: Managed Identity (will fail if not in Azure)
        logger.info("\n--- Method 5: Managed Identity ---")
        try:
            credential5 = auth_manager.authenticate_with_managed_identity()
            logger.info("✓ Managed Identity works!")
        except Exception as e:
            logger.warning(f"✗ Managed Identity failed (expected if not in Azure): {e}")
        
        # Get recommended credential
        logger.info("\n--- Recommended Credential ---")
        recommended = auth_manager.get_recommended_credential()
        logger.info(f"Recommended credential type: {type(recommended).__name__}")
        
        logger.info("\n" + "=" * 60)
        logger.info("Authentication examples completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
