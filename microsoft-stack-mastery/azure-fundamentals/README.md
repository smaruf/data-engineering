# Azure Fundamentals Learning Path

Comprehensive guide to Azure fundamentals with practical Python examples for data engineering.

## Overview

This learning path covers essential Azure services and concepts needed for data engineering projects. All examples use the Azure SDK for Python and follow production-ready best practices.

## Prerequisites

- Python 3.8+
- Azure subscription
- Azure CLI installed
- Basic understanding of cloud computing concepts

## Setup

### Install Required Packages

```bash
pip install azure-identity azure-mgmt-resource azure-mgmt-storage azure-storage-blob \
    azure-mgmt-compute azure-mgmt-network azure-storage-file-datalake \
    azure-cosmos azure-mgmt-sql pyodbc azure-mgmt-batch azure-batch
```

### Environment Variables

Set the following environment variables for authentication:

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

## Learning Path

### Beginner Level

1. **Azure Setup** (`beginner/01-azure-setup/`)
   - Azure CLI installation and configuration
   - Creating Azure resources programmatically
   - Understanding Azure authentication methods

2. **Azure Storage** (`beginner/02-azure-storage/`)
   - Blob Storage operations
   - Azure Data Lake Storage Gen2
   - File upload/download operations

3. **Azure Databases** (`beginner/03-azure-databases/`)
   - Azure SQL Database
   - Azure Cosmos DB
   - Azure Synapse Analytics

4. **Azure Compute** (`beginner/04-azure-compute/`)
   - Azure Functions
   - Azure Batch
   - Virtual Machines

## Best Practices

- Always use managed identities when possible
- Implement proper error handling and logging
- Use environment variables for configuration
- Follow the principle of least privilege
- Clean up resources after use to avoid costs

## Resources

- [Azure Documentation](https://docs.microsoft.com/azure/)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [Azure Architecture Center](https://docs.microsoft.com/azure/architecture/)

## Cost Management

Remember to delete resources when not in use:
- Use resource groups for easy cleanup
- Set up cost alerts
- Use Azure Cost Management tools
- Consider using Azure Dev/Test pricing

## Security Considerations

- Never commit credentials to version control
- Use Azure Key Vault for secrets
- Enable Azure Defender for cloud workloads
- Implement network security groups
- Use private endpoints when possible

## Support

For issues or questions:
- Check Azure documentation
- Review code comments and docstrings
- Open an issue in the repository
