# Microsoft Fabric Learning Path

This repository contains comprehensive examples and tutorials for Microsoft Fabric, Microsoft's unified analytics platform that brings together data engineering, data science, real-time analytics, and business intelligence.

## 🎯 Overview

Microsoft Fabric is an all-in-one analytics solution for enterprises that covers everything from data movement to data science, real-time analytics, and business intelligence. It offers a comprehensive suite of services including:

- **Data Factory** - Data integration and orchestration
- **Synapse Data Engineering** - Apache Spark-based big data processing
- **Synapse Data Warehouse** - Enterprise data warehousing
- **Synapse Data Science** - Machine learning and AI
- **Synapse Real-Time Analytics** - Real-time data processing
- **Power BI** - Business intelligence and visualization
- **Data Activator** - Automated actions based on data patterns

## 📚 Learning Path

### Beginner Level

The beginner section covers foundational concepts and basic operations:

1. **Fabric Setup** - Setting up workspaces, capacity management, and authentication
2. **Lakehouse** - Creating and managing lakehouses, working with Delta tables
3. **Data Warehouse** - Building and querying Fabric data warehouses
4. **Notebooks** - Working with Fabric notebooks for data processing

### Intermediate Level (Coming Soon)

- Data pipelines and orchestration
- Advanced data transformations
- Real-time analytics with KQL
- Machine learning with Synapse Data Science

### Advanced Level (Coming Soon)

- Enterprise-grade data architectures
- Performance optimization
- Security and governance
- CI/CD for Fabric artifacts

## 🚀 Getting Started

### Prerequisites

- **Azure Subscription** - Active Azure subscription
- **Microsoft Fabric Capacity** - F2 or higher (or Trial capacity)
- **Python 3.8+** - For running examples
- **Azure CLI** - For authentication and resource management
- **Service Principal** - For programmatic access (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd microsoft-stack-mastery/microsoft-fabric
   ```

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Authenticate with Azure:**
   ```bash
   az login
   ```

### Required Python Packages

```txt
azure-identity>=1.14.0
azure-storage-blob>=12.19.0
azure-storage-file-datalake>=12.13.0
msal>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0
pandas>=2.0.0
pyarrow>=14.0.0
pyspark>=3.4.0
delta-spark>=2.4.0
```

## 🔑 Authentication

Microsoft Fabric supports multiple authentication methods:

### 1. Interactive Browser Authentication (Development)
```python
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential()
```

### 2. Azure CLI Authentication (Development)
```python
from azure.identity import AzureCliCredential

credential = AzureCliCredential()
```

### 3. Service Principal (Production)
```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

### 4. Managed Identity (Azure Resources)
```python
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential()
```

## 📖 Key Concepts

### Workspace
A collaborative environment where you can create and manage Fabric items like lakehouses, warehouses, notebooks, and reports.

### Capacity
The compute resources allocated to run Fabric workloads. Capacities can be:
- **F SKUs** - Fabric capacity (F2, F4, F8, etc.)
- **Trial** - 60-day trial capacity for evaluation

### Lakehouse
A data architecture that combines the best features of data lakes and data warehouses. Built on Delta Lake format.

### OneLake
Microsoft Fabric's unified, hierarchical data lake that serves as the single storage layer for all analytics data.

### Warehouse
A fully managed, enterprise-grade data warehouse built on top of OneLake, optimized for T-SQL analytics.

## 🔗 Useful Links

- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Microsoft Fabric REST API](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Microsoft Fabric Python SDK (Preview)](https://pypi.org/project/azure-fabric/)
- [Delta Lake Documentation](https://docs.delta.io/latest/index.html)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)

## 📝 Examples Structure

Each example includes:
- **Comprehensive docstrings** - Detailed documentation
- **Error handling** - Production-ready error management
- **Logging** - Structured logging for debugging
- **Configuration** - Environment-based configuration
- **Usage examples** - Clear usage demonstrations

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add your examples with proper documentation
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

- **Costs**: Microsoft Fabric incurs costs based on capacity usage. Monitor your consumption.
- **Security**: Never commit credentials or secrets to version control.
- **Trial Limitations**: Trial capacities have resource limitations and expire after 60 days.
- **API Changes**: Fabric APIs are evolving. Check documentation for the latest updates.

## 🆘 Support

For issues and questions:
- Review the [Microsoft Fabric documentation](https://learn.microsoft.com/en-us/fabric/)
- Check [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/tags/389/microsoft-fabric)
- Open an issue in this repository
