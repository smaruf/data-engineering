"""
Microsoft Fabric Authentication Module

This module provides comprehensive authentication methods for Microsoft Fabric APIs,
including Service Principal authentication, user authentication, and token management.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from functools import wraps
from datetime import datetime, timedelta

# Azure authentication libraries
from azure.identity import (
    DefaultAzureCredential,
    ClientSecretCredential,
    AzureCliCredential,
    InteractiveBrowserCredential,
    ManagedIdentityCredential,
    ChainedTokenCredential
)
from msal import ConfidentialClientApplication, PublicClientApplication
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class FabricAuthenticationError(Exception):
    """Custom exception for Fabric authentication errors."""
    pass


def retry_with_backoff(max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Decorator to retry API calls with exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        initial_delay (int): Initial delay in seconds
        backoff_factor (int): Multiplier for delay between retries
    
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator


class FabricAuthenticator:
    """
    Comprehensive authentication handler for Microsoft Fabric APIs.
    
    Supports multiple authentication methods:
    - Service Principal (Client Credentials)
    - Azure CLI
    - Interactive Browser
    - Managed Identity
    - Default Azure Credential (chained)
    """
    
    # Fabric API scopes
    FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
    POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        auth_method: str = "default"
    ):
        """
        Initialize Fabric authenticator.
        
        Args:
            tenant_id (str, optional): Azure AD tenant ID
            client_id (str, optional): Application (client) ID
            client_secret (str, optional): Client secret
            auth_method (str): Authentication method - 'default', 'service_principal',
                             'cli', 'interactive', 'managed_identity'
        """
        self.tenant_id = tenant_id or os.getenv("TENANT_ID")
        self.client_id = client_id or os.getenv("CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CLIENT_SECRET")
        self.auth_method = auth_method
        
        self._credential = None
        self._token_cache = {}
        
        logger.info(f"Initialized FabricAuthenticator with method: {auth_method}")
    
    def get_credential(self):
        """
        Get Azure credential based on configured authentication method.
        
        Returns:
            Azure credential object
        
        Raises:
            FabricAuthenticationError: If authentication setup fails
        """
        if self._credential:
            return self._credential
        
        try:
            if self.auth_method == "service_principal":
                self._credential = self._get_service_principal_credential()
            elif self.auth_method == "cli":
                self._credential = AzureCliCredential()
            elif self.auth_method == "interactive":
                self._credential = InteractiveBrowserCredential(
                    tenant_id=self.tenant_id
                )
            elif self.auth_method == "managed_identity":
                self._credential = ManagedIdentityCredential()
            elif self.auth_method == "default":
                self._credential = self._get_default_credential()
            else:
                raise FabricAuthenticationError(
                    f"Unknown authentication method: {self.auth_method}"
                )
            
            logger.info(f"Successfully created credential using {self.auth_method}")
            return self._credential
            
        except Exception as e:
            logger.error(f"Failed to create credential: {str(e)}")
            raise FabricAuthenticationError(f"Credential creation failed: {str(e)}")
    
    def _get_service_principal_credential(self):
        """
        Create Service Principal credential.
        
        Returns:
            ClientSecretCredential
        
        Raises:
            FabricAuthenticationError: If required parameters are missing
        """
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise FabricAuthenticationError(
                "Service Principal authentication requires TENANT_ID, "
                "CLIENT_ID, and CLIENT_SECRET"
            )
        
        return ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
    
    def _get_default_credential(self):
        """
        Create DefaultAzureCredential with prioritized chain.
        
        Returns:
            ChainedTokenCredential with preferred authentication methods
        """
        credentials = []
        
        # Try Service Principal first if credentials are available
        if all([self.tenant_id, self.client_id, self.client_secret]):
            credentials.append(
                ClientSecretCredential(
                    self.tenant_id,
                    self.client_id,
                    self.client_secret
                )
            )
        
        # Then try Managed Identity (for Azure resources)
        credentials.append(ManagedIdentityCredential())
        
        # Then Azure CLI
        credentials.append(AzureCliCredential())
        
        # Finally, interactive browser
        if self.tenant_id:
            credentials.append(
                InteractiveBrowserCredential(tenant_id=self.tenant_id)
            )
        
        return ChainedTokenCredential(*credentials)
    
    @retry_with_backoff(max_retries=3)
    def get_access_token(self, scope: str = None) -> str:
        """
        Get access token for Fabric API.
        
        Args:
            scope (str, optional): Token scope. Defaults to Fabric API scope.
        
        Returns:
            str: Access token
        
        Raises:
            FabricAuthenticationError: If token acquisition fails
        """
        scope = scope or self.FABRIC_SCOPE
        
        # Check cache
        cache_key = f"{self.auth_method}_{scope}"
        if cache_key in self._token_cache:
            token_data = self._token_cache[cache_key]
            # Check if token is still valid (with 5 min buffer)
            if token_data['expires_at'] > datetime.now() + timedelta(minutes=5):
                logger.debug("Using cached token")
                return token_data['token']
        
        try:
            credential = self.get_credential()
            token = credential.get_token(scope)
            
            # Cache the token
            self._token_cache[cache_key] = {
                'token': token.token,
                'expires_at': datetime.fromtimestamp(token.expires_on)
            }
            
            logger.info("Successfully acquired access token")
            return token.token
            
        except Exception as e:
            logger.error(f"Failed to acquire access token: {str(e)}")
            raise FabricAuthenticationError(f"Token acquisition failed: {str(e)}")
    
    def get_auth_headers(self, scope: str = None) -> Dict[str, str]:
        """
        Get HTTP headers with authentication token.
        
        Args:
            scope (str, optional): Token scope
        
        Returns:
            dict: Headers with Authorization bearer token
        """
        token = self.get_access_token(scope)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def validate_token(self, token: str = None) -> bool:
        """
        Validate if the token is still valid.
        
        Args:
            token (str, optional): Token to validate. If None, gets current token.
        
        Returns:
            bool: True if token is valid
        """
        if token is None:
            token = self.get_access_token()
        
        try:
            # Make a simple API call to validate token
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                "https://api.fabric.microsoft.com/v1/workspaces",
                headers=headers,
                timeout=10
            )
            
            is_valid = response.status_code in [200, 201]
            logger.info(f"Token validation: {'valid' if is_valid else 'invalid'}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return False
    
    def clear_token_cache(self):
        """Clear cached tokens."""
        self._token_cache.clear()
        logger.info("Token cache cleared")


class FabricAPIClient:
    """
    Microsoft Fabric API client with built-in authentication.
    
    Provides methods for common Fabric API operations.
    """
    
    BASE_URL = "https://api.fabric.microsoft.com/v1"
    
    def __init__(self, authenticator: FabricAuthenticator):
        """
        Initialize Fabric API client.
        
        Args:
            authenticator (FabricAuthenticator): Authentication handler
        """
        self.auth = authenticator
        self.session = requests.Session()
        logger.info("Initialized FabricAPIClient")
    
    @retry_with_backoff(max_retries=3)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make authenticated API request.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint (str): API endpoint (without base URL)
            **kwargs: Additional arguments for requests
        
        Returns:
            requests.Response: API response
        
        Raises:
            FabricAuthenticationError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        headers = self.auth.get_auth_headers()
        headers.update(kwargs.pop('headers', {}))
        
        logger.debug(f"{method} {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=kwargs.pop('timeout', 30),
                **kwargs
            )
            
            # Log response
            logger.info(
                f"{method} {endpoint} - Status: {response.status_code}"
            )
            
            # Raise for error status codes
            if response.status_code >= 400:
                logger.error(f"API Error: {response.text}")
                response.raise_for_status()
            
            return response
            
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise
    
    def get_workspaces(self) -> Dict[str, Any]:
        """
        Get list of workspaces.
        
        Returns:
            dict: Workspace list
        """
        response = self._make_request("GET", "/workspaces")
        return response.json()
    
    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get workspace details.
        
        Args:
            workspace_id (str): Workspace ID
        
        Returns:
            dict: Workspace details
        """
        response = self._make_request("GET", f"/workspaces/{workspace_id}")
        return response.json()
    
    def create_workspace(
        self,
        display_name: str,
        description: str = "",
        capacity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new workspace.
        
        Args:
            display_name (str): Workspace display name
            description (str): Workspace description
            capacity_id (str, optional): Capacity ID to assign
        
        Returns:
            dict: Created workspace details
        """
        payload = {
            "displayName": display_name,
            "description": description
        }
        
        if capacity_id:
            payload["capacityId"] = capacity_id
        
        response = self._make_request("POST", "/workspaces", json=payload)
        return response.json()


def main():
    """
    Example usage of authentication methods.
    """
    print("=" * 60)
    print("Microsoft Fabric Authentication Examples")
    print("=" * 60)
    
    # Example 1: Service Principal Authentication
    print("\n1. Service Principal Authentication")
    print("-" * 60)
    try:
        auth_sp = FabricAuthenticator(auth_method="service_principal")
        token = auth_sp.get_access_token()
        print(f"✅ Token acquired (length: {len(token)})")
        print(f"✅ Token valid: {auth_sp.validate_token(token)}")
    except FabricAuthenticationError as e:
        print(f"❌ Service Principal auth failed: {e}")
    
    # Example 2: Azure CLI Authentication
    print("\n2. Azure CLI Authentication")
    print("-" * 60)
    try:
        auth_cli = FabricAuthenticator(auth_method="cli")
        token = auth_cli.get_access_token()
        print(f"✅ Token acquired via Azure CLI")
        print(f"✅ Token valid: {auth_cli.validate_token(token)}")
    except FabricAuthenticationError as e:
        print(f"❌ CLI auth failed: {e}")
    
    # Example 3: Default Credential Chain
    print("\n3. Default Credential Chain")
    print("-" * 60)
    try:
        auth_default = FabricAuthenticator(auth_method="default")
        token = auth_default.get_access_token()
        print(f"✅ Token acquired using credential chain")
    except FabricAuthenticationError as e:
        print(f"❌ Default auth failed: {e}")
    
    # Example 4: Using API Client
    print("\n4. Using Fabric API Client")
    print("-" * 60)
    try:
        auth = FabricAuthenticator(auth_method="default")
        client = FabricAPIClient(auth)
        
        # List workspaces
        workspaces = client.get_workspaces()
        print(f"✅ Retrieved {len(workspaces.get('value', []))} workspaces")
        
        # Display first workspace
        if workspaces.get('value'):
            ws = workspaces['value'][0]
            print(f"   First workspace: {ws.get('displayName')} ({ws.get('id')})")
    except Exception as e:
        print(f"❌ API client failed: {e}")
    
    # Example 5: Get authentication headers
    print("\n5. Get Authentication Headers")
    print("-" * 60)
    try:
        auth = FabricAuthenticator(auth_method="default")
        headers = auth.get_auth_headers()
        print("✅ Authentication headers:")
        for key, value in headers.items():
            if key == "Authorization":
                print(f"   {key}: Bearer {value[:20]}...")
            else:
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Failed to get headers: {e}")
    
    print("\n" + "=" * 60)
    print("Authentication examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
