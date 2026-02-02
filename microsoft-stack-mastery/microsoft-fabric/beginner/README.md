# Microsoft Fabric - Beginner Level

Welcome to the beginner level Microsoft Fabric learning path! This section covers fundamental concepts and basic operations to get you started with Microsoft Fabric.

## 🎯 Learning Objectives

By completing this section, you will:

- Understand Microsoft Fabric architecture and components
- Set up and configure Fabric workspaces and capacities
- Authenticate programmatically with Fabric APIs
- Create and manage lakehouses with Delta tables
- Build and query Fabric data warehouses
- Work with Fabric notebooks for data processing
- Load and transform data from various sources

## 📚 Modules

### Module 1: Fabric Setup (01-fabric-setup)

Learn the fundamentals of setting up Microsoft Fabric:

- **workspace_setup.md** - Step-by-step guide for creating and configuring workspaces
- **capacity_management.md** - Understanding and managing Fabric capacities
- **authentication.py** - Python examples for authenticating with Fabric APIs

**Prerequisites:**
- Active Azure subscription
- Microsoft Fabric capacity (Trial or paid)
- Azure CLI installed

**Duration:** 1-2 hours

### Module 2: Lakehouse (02-lakehouse)

Master the basics of Fabric Lakehouses:

- **create_lakehouse.py** - Programmatically create lakehouses using Fabric API
- **load_data_lakehouse.py** - Load data from CSV, Parquet, JSON, and other formats
- **lakehouse_tables.py** - Create and manage Delta tables in lakehouses
- **lakehouse_shortcuts.py** - Create shortcuts to external storage (ADLS Gen2, S3)

**Key Concepts:**
- OneLake and lakehouse architecture
- Delta Lake format and ACID transactions
- Shortcuts for data virtualization
- Managed vs. unmanaged tables

**Duration:** 3-4 hours

### Module 3: Data Warehouse (03-data-warehouse)

Learn to build and manage Fabric Data Warehouses:

- **create_warehouse.py** - Create Fabric warehouses programmatically
- **warehouse_tables.py** - Create tables, schemas, and load data
- **warehouse_queries.py** - Query data using T-SQL, perform cross-database queries

**Key Concepts:**
- Warehouse vs. Lakehouse (when to use each)
- T-SQL in Fabric
- Cross-database queries
- Performance optimization basics

**Duration:** 3-4 hours

### Module 4: Notebooks (04-notebooks)

Work with Fabric notebooks for data processing:

- **fabric_notebook_basics.py** - Essential notebook operations and patterns
- **pyspark_in_fabric.py** - PySpark examples for Fabric environment
- **data_exploration.py** - Data exploration and visualization techniques

**Key Concepts:**
- Fabric notebook environment
- PySpark DataFrame API
- Data visualization with matplotlib and seaborn
- Reading from lakehouse and warehouse

**Duration:** 2-3 hours

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
# Azure/Fabric Configuration
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
SUBSCRIPTION_ID=your-subscription-id

# Fabric Workspace Configuration
WORKSPACE_ID=your-workspace-id
WORKSPACE_NAME=your-workspace-name
CAPACITY_ID=your-capacity-id

# Storage Configuration (for lakehouse shortcuts)
ADLS_ACCOUNT_NAME=your-adls-account
ADLS_CONTAINER_NAME=your-container
ADLS_SAS_TOKEN=your-sas-token

# API Configuration
FABRIC_API_BASE_URL=https://api.fabric.microsoft.com/v1
```

### 2. Install Dependencies

```bash
pip install azure-identity azure-storage-blob azure-storage-file-datalake \
    msal requests python-dotenv pandas pyarrow pyspark delta-spark
```

### 3. Authenticate

Test your authentication:

```bash
cd 01-fabric-setup
python authentication.py
```

### 4. Run Examples

Execute examples in order:

```bash
# Module 1: Setup
cd 01-fabric-setup
python authentication.py

# Module 2: Lakehouse
cd ../02-lakehouse
python create_lakehouse.py
python load_data_lakehouse.py
python lakehouse_tables.py

# Module 3: Warehouse
cd ../03-data-warehouse
python create_warehouse.py
python warehouse_tables.py
python warehouse_queries.py

# Module 4: Notebooks
cd ../04-notebooks
python fabric_notebook_basics.py
python pyspark_in_fabric.py
```

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Active Azure subscription
- [ ] Microsoft Fabric capacity (Trial or F2+)
- [ ] Python 3.8 or higher installed
- [ ] Azure CLI installed and configured
- [ ] Service Principal created (optional, for programmatic access)
- [ ] Fabric workspace created
- [ ] Required Python packages installed
- [ ] Environment variables configured

## 🔑 Authentication Methods

### For Development (Local Machine)

**Option 1: Interactive Browser**
```python
from azure.identity import InteractiveBrowserCredential
credential = InteractiveBrowserCredential()
```

**Option 2: Azure CLI**
```python
from azure.identity import AzureCliCredential
credential = AzureCliCredential()
```

### For Production (Automated Workflows)

**Service Principal**
```python
from azure.identity import ClientSecretCredential
credential = ClientSecretCredential(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
)
```

## 📖 Key Concepts to Understand

### 1. Microsoft Fabric Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Microsoft Fabric                     │
├─────────────────────────────────────────────────────────┤
│                        OneLake                           │
│              (Unified Data Lake Storage)                 │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│   Data   │ Synapse  │ Synapse  │ Synapse  │   Power BI  │
│ Factory  │   Data   │   Data   │   Data   │             │
│          │Engineer  │Warehouse │ Science  │             │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

### 2. Lakehouse vs. Warehouse

**Use Lakehouse when:**
- Working with semi-structured or unstructured data
- Need schema-on-read flexibility
- Performing big data processing with Spark
- Building a medallion architecture (bronze/silver/gold)

**Use Warehouse when:**
- Need strong schema enforcement
- Performing complex SQL analytics
- Require ACID transactions at row level
- Building traditional dimensional models (star/snowflake)

### 3. Delta Lake

Delta Lake is the foundation of Fabric lakehouses, providing:
- **ACID transactions** - Data consistency guarantees
- **Time travel** - Query historical data versions
- **Schema evolution** - Safely add/modify columns
- **Upserts/Deletes** - Merge, update, and delete operations
- **Scalable metadata** - Handle millions of files efficiently

## 🎓 Learning Tips

1. **Start Sequential**: Follow the modules in order - each builds on the previous
2. **Hands-On Practice**: Run every example and modify parameters
3. **Read Documentation**: Review inline comments and docstrings
4. **Experiment**: Try variations of the examples with your own data
5. **Monitor Costs**: Keep track of capacity usage to avoid surprises
6. **Use Trial Capacity**: Start with a trial capacity for learning
7. **Clean Up Resources**: Delete test resources to minimize costs

## 🐛 Troubleshooting

### Common Issues

**Authentication Failures**
```python
# Solution: Ensure service principal has proper permissions
# Required roles: Fabric Administrator or Workspace Admin
```

**Capacity Not Available**
```python
# Solution: Verify capacity is running and has available resources
# Check Azure portal → Fabric capacities → Monitor
```

**API Rate Limiting**
```python
# Solution: Implement exponential backoff and retry logic
# See authentication.py for retry decorator example
```

**Import Errors**
```bash
# Solution: Ensure all packages are installed
pip install -r requirements.txt
```

## 📚 Additional Resources

### Microsoft Documentation
- [Fabric Get Started](https://learn.microsoft.com/en-us/fabric/get-started/)
- [Lakehouse Tutorial](https://learn.microsoft.com/en-us/fabric/data-engineering/tutorial-lakehouse-introduction)
- [Warehouse Tutorial](https://learn.microsoft.com/en-us/fabric/data-warehouse/tutorial-introduction)
- [Fabric REST API Reference](https://learn.microsoft.com/en-us/rest/api/fabric/)

### Community Resources
- [Fabric Community](https://community.fabric.microsoft.com/)
- [Fabric Blog](https://blog.fabric.microsoft.com/)
- [GitHub Samples](https://github.com/microsoft/fabric-samples)

## ✅ Progress Tracking

Track your progress through the modules:

- [ ] Module 1: Fabric Setup - Completed workspace and authentication setup
- [ ] Module 2: Lakehouse - Created lakehouse and loaded data
- [ ] Module 3: Warehouse - Built warehouse and ran queries
- [ ] Module 4: Notebooks - Executed PySpark code in notebooks

## 🎯 Next Steps

After completing the beginner level:

1. **Intermediate Level** - Data pipelines, orchestration, real-time analytics
2. **Advanced Level** - Enterprise patterns, optimization, governance
3. **Specialization** - Deep dive into specific areas (ML, real-time, etc.)
4. **Certification** - Consider Microsoft Fabric certifications

## 💡 Best Practices

- **Use descriptive names** for workspaces, lakehouses, and warehouses
- **Implement proper error handling** in all scripts
- **Log operations** for debugging and auditing
- **Use environment variables** for configuration
- **Version control** your code and notebooks
- **Document your work** with clear comments
- **Test with small datasets** before scaling up
- **Monitor resource usage** to optimize costs

Good luck with your Microsoft Fabric learning journey! 🚀
