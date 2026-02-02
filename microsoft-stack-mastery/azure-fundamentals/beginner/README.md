# Azure Fundamentals - Beginner Level

Welcome to the beginner level of Azure fundamentals! This section covers essential Azure services and operations needed to get started with Azure data engineering.

## Modules

### 01. Azure Setup
Learn how to set up your Azure environment, authenticate, and create basic resources.

**Topics Covered:**
- Azure CLI installation and configuration
- Creating resource groups and storage accounts
- Authentication methods (DefaultAzureCredential, Service Principal, Managed Identity)
- Environment setup best practices

**Files:**
- `setup_azure_cli.md` - Comprehensive setup guide
- `create_resources.py` - Create Azure resources programmatically
- `azure_authentication.py` - Authentication examples

### 02. Azure Storage
Master Azure Storage services including Blob Storage and Data Lake Storage Gen2.

**Topics Covered:**
- Blob Storage operations (upload, download, list, delete)
- Azure Data Lake Storage Gen2 operations
- Bulk file operations with error handling
- Container and directory management

**Files:**
- `blob_storage_operations.py` - Core blob operations
- `data_lake_gen2.py` - ADLS Gen2 examples
- `file_upload_download.py` - Bulk operations

### 03. Azure Databases
Work with Azure database services including SQL Database, Cosmos DB, and Synapse.

**Topics Covered:**
- Azure SQL Database connections and queries
- Cosmos DB CRUD operations
- Azure Synapse Analytics basics
- Parameterized queries and security

**Files:**
- `azure_sql_connector.py` - SQL Database operations
- `cosmos_db_operations.py` - Cosmos DB examples
- `azure_synapse_basics.py` - Synapse SQL pool operations

### 04. Azure Compute
Understand Azure compute services for data processing and automation.

**Topics Covered:**
- Azure Functions for serverless computing
- Azure Batch for parallel processing
- Virtual Machine management
- Trigger types and job scheduling

**Files:**
- `azure_functions.py` - Function app examples
- `azure_batch.py` - Batch processing
- `vm_operations.py` - VM lifecycle management

## Getting Started

1. **Set up your environment:**
   ```bash
   # Install Azure CLI
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Login to Azure
   az login
   
   # Set your subscription
   az account set --subscription "your-subscription-id"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   export AZURE_SUBSCRIPTION_ID="your-subscription-id"
   export AZURE_RESOURCE_GROUP="your-resource-group"
   export AZURE_LOCATION="eastus"
   ```

4. **Run examples:**
   ```bash
   cd 01-azure-setup
   python create_resources.py
   ```

## Learning Approach

1. Start with Module 01 to set up your environment
2. Progress through modules sequentially
3. Run each example and review the output
4. Modify examples to experiment with different configurations
5. Review error handling and logging implementations

## Prerequisites

- Azure subscription (free trial available)
- Python 3.8 or higher
- Basic Python programming knowledge
- Understanding of cloud computing concepts

## Tips for Success

- **Read the documentation**: Each file has comprehensive docstrings
- **Understand the code**: Don't just run it, understand what it does
- **Experiment**: Modify parameters and observe the results
- **Clean up resources**: Always delete resources to avoid charges
- **Use logging**: Enable verbose logging to understand operations

## Common Issues

### Authentication Errors
- Ensure environment variables are set correctly
- Verify your Azure credentials are valid
- Check that your service principal has necessary permissions

### Resource Creation Failures
- Verify subscription quotas
- Check resource naming conventions
- Ensure sufficient permissions
- Verify region availability

### Connection Issues
- Check firewall rules for Azure SQL and Cosmos DB
- Verify network security group settings
- Ensure client IP is whitelisted

## Next Steps

After completing the beginner level:
1. Explore intermediate topics (Azure Data Factory, Databricks)
2. Build end-to-end data pipelines
3. Implement CI/CD for Azure resources
4. Study Azure security and governance

## Additional Resources

- [Azure Python SDK Documentation](https://docs.microsoft.com/python/api/overview/azure/)
- [Azure Samples GitHub](https://github.com/Azure-Samples)
- [Microsoft Learn](https://docs.microsoft.com/learn/)
