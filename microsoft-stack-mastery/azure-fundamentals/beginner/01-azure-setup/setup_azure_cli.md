# Azure CLI Setup Guide

Complete guide for installing and configuring Azure CLI for data engineering projects.

## Table of Contents
1. [Installation](#installation)
2. [Authentication](#authentication)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Common Commands](#common-commands)
6. [Troubleshooting](#troubleshooting)

## Installation

### Linux (Ubuntu/Debian)

```bash
# Install Azure CLI using Microsoft repository
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version
```

### macOS

```bash
# Using Homebrew
brew update && brew install azure-cli

# Verify installation
az --version
```

### Windows

**Option 1: Using MSI Installer**
1. Download from: https://aka.ms/installazurecliwindows
2. Run the installer
3. Restart your terminal

**Option 2: Using PowerShell**
```powershell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

### Docker

```bash
docker run -it mcr.microsoft.com/azure-cli
```

## Authentication

### Interactive Login

```bash
# Standard login (opens browser)
az login

# Login with specific tenant
az login --tenant "your-tenant-id"

# Login with device code (for headless systems)
az login --use-device-code
```

### Service Principal Authentication

```bash
# Create service principal
az ad sp create-for-rbac --name "my-app-name" --role contributor \
    --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}

# Login with service principal
az login --service-principal \
    --username $AZURE_CLIENT_ID \
    --password $AZURE_CLIENT_SECRET \
    --tenant $AZURE_TENANT_ID
```

### Managed Identity (Azure VM)

```bash
# Login using system-assigned managed identity
az login --identity

# Login using user-assigned managed identity
az login --identity --username $CLIENT_ID
```

## Configuration

### Set Default Subscription

```bash
# List available subscriptions
az account list --output table

# Set default subscription
az account set --subscription "subscription-name-or-id"

# Verify current subscription
az account show
```

### Configure Default Location

```bash
# Set default location
az configure --defaults location=eastus

# Set default resource group
az configure --defaults group=my-resource-group
```

### Configure Output Format

```bash
# Set default output format (json, jsonc, table, tsv, yaml, none)
az configure --defaults output=table

# Use output format for single command
az group list --output json
```

### Configure Logging

```bash
# Enable debug logging
az configure --defaults logging.enable_log_file=true

# Set log level
az configure --defaults logging.log_level=debug
```

## Verification

### Check Installation

```bash
# Display Azure CLI version
az --version

# Display current configuration
az configure --list-defaults

# Display current account
az account show
```

### Test Resource Operations

```bash
# List resource groups
az group list

# List storage accounts
az storage account list

# List virtual machines
az vm list
```

## Common Commands

### Resource Groups

```bash
# Create resource group
az group create --name myResourceGroup --location eastus

# List resource groups
az group list --output table

# Delete resource group
az group delete --name myResourceGroup --yes --no-wait
```

### Storage Accounts

```bash
# Create storage account
az storage account create \
    --name mystorageaccount \
    --resource-group myResourceGroup \
    --location eastus \
    --sku Standard_LRS

# List storage accounts
az storage account list --resource-group myResourceGroup

# Get storage account keys
az storage account keys list \
    --account-name mystorageaccount \
    --resource-group myResourceGroup
```

### Azure SQL

```bash
# Create SQL server
az sql server create \
    --name myserver \
    --resource-group myResourceGroup \
    --location eastus \
    --admin-user myadmin \
    --admin-password MyPassword123!

# Create SQL database
az sql db create \
    --resource-group myResourceGroup \
    --server myserver \
    --name mydatabase \
    --service-objective S0
```

### Virtual Machines

```bash
# Create VM
az vm create \
    --resource-group myResourceGroup \
    --name myVM \
    --image UbuntuLTS \
    --admin-username azureuser \
    --generate-ssh-keys

# Start VM
az vm start --resource-group myResourceGroup --name myVM

# Stop VM
az vm stop --resource-group myResourceGroup --name myVM

# Delete VM
az vm delete --resource-group myResourceGroup --name myVM --yes
```

## Environment Variables

### Required Variables

```bash
# Set in ~/.bashrc or ~/.zshrc
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_RESOURCE_GROUP="your-resource-group"
export AZURE_LOCATION="eastus"
```

### For Storage Operations

```bash
export AZURE_STORAGE_ACCOUNT="your-storage-account"
export AZURE_STORAGE_KEY="your-storage-key"
export AZURE_STORAGE_CONNECTION_STRING="your-connection-string"
```

### For Database Operations

```bash
export AZURE_SQL_SERVER="your-server-name"
export AZURE_SQL_DATABASE="your-database-name"
export AZURE_SQL_USER="your-username"
export AZURE_SQL_PASSWORD="your-password"
```

## Best Practices

1. **Use Service Principals for Automation**
   - Don't use interactive login for scripts
   - Create dedicated service principals with minimal permissions
   - Rotate secrets regularly

2. **Secure Credentials**
   - Never commit credentials to version control
   - Use Azure Key Vault for secret management
   - Use managed identities when running in Azure

3. **Use Resource Groups**
   - Organize resources by project or environment
   - Tag resources for cost tracking
   - Use naming conventions

4. **Enable Logging**
   - Enable diagnostic logs for troubleshooting
   - Use Azure Monitor for production workloads
   - Review activity logs regularly

5. **Cost Management**
   - Set up budget alerts
   - Use Azure Cost Management
   - Delete unused resources
   - Use auto-shutdown for dev/test VMs

## Troubleshooting

### Authentication Issues

```bash
# Clear cached credentials
az account clear

# Re-login
az login

# Verify token
az account get-access-token
```

### Timeout Issues

```bash
# Increase timeout for long-running operations
az configure --defaults timeout=600
```

### Network Issues

```bash
# Test connectivity
curl -I https://management.azure.com

# Use proxy
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
az configure --defaults proxy.http_proxy=$HTTP_PROXY
```

### Permission Issues

```bash
# Check current user permissions
az role assignment list --assignee $(az account show --query user.name -o tsv)

# Check service principal permissions
az role assignment list --assignee $AZURE_CLIENT_ID
```

## Upgrading Azure CLI

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install --only-upgrade -y azure-cli

# macOS
brew upgrade azure-cli

# Windows (PowerShell as Admin)
az upgrade
```

## Additional Resources

- [Azure CLI Documentation](https://docs.microsoft.com/cli/azure/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/reference-index)
- [Azure CLI GitHub](https://github.com/Azure/azure-cli)
- [Azure CLI Extensions](https://docs.microsoft.com/cli/azure/azure-cli-extensions-list)

## Quick Reference Card

```bash
# Login and setup
az login
az account set --subscription "sub-id"
az configure --defaults location=eastus group=myRG

# Resource management
az group create -n myRG -l eastus
az resource list -g myRG
az group delete -n myRG --yes

# Get help
az --help
az storage --help
az storage blob --help
```
