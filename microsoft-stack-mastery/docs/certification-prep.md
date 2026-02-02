# Certification Preparation Guide

## Table of Contents
1. [DP-203: Azure Data Engineer Associate](#dp-203-azure-data-engineer-associate)
2. [DP-600: Fabric Analytics Engineer](#dp-600-fabric-analytics-engineer)
3. [Study Plan](#study-plan)
4. [Practice Questions](#practice-questions)
5. [Additional Resources](#additional-resources)

---

## DP-203: Azure Data Engineer Associate

### Exam Overview

**Exam Details:**
- **Exam Code**: DP-203
- **Duration**: 100 minutes
- **Number of Questions**: 40-60
- **Passing Score**: 700/1000
- **Cost**: $165 USD
- **Format**: Multiple choice, case studies, scenario-based

**Prerequisites:**
- Understanding of Azure fundamentals
- Experience with data processing
- Knowledge of programming (Python, SQL, Scala)

### Exam Skills Measured

#### 1. Design and Implement Data Storage (15-20%)

**Topics:**
- Implement data lake storage (ADLS Gen2)
- Design folder structures (medallion architecture)
- Implement data partitioning strategies
- Configure security (ACLs, RBAC, encryption)
- Implement data lifecycle management

**Study Points:**

```python
# 1. ADLS Gen2 Hierarchical Namespace
# Key Concepts:
- Enables folder hierarchy (vs flat blob storage)
- Supports ACLs at directory and file level
- Required for big data analytics
- Better performance for file operations

# 2. Folder Structure Best Practices
raw/                    # Bronze layer
├── source1/
│   ├── year=2024/
│   │   ├── month=01/
processed/              # Silver layer  
├── domain1/
curated/               # Gold layer
├── business_area1/

# 3. Partitioning Strategies
# Partition by:
- Date (year/month/day) - most common
- Category/Region - for filtering
- Hash of key - for even distribution

# 4. Security
# - Shared Access Signatures (SAS)
# - Role-Based Access Control (RBAC)
# - Access Control Lists (ACLs)
# - Service endpoints and private endpoints
# - Customer-managed keys (CMK)

# 5. Lifecycle Management
# - Hot tier: Frequently accessed
# - Cool tier: Infrequently accessed (30+ days)
# - Archive tier: Rarely accessed (180+ days)
# - Automatic tiering policies
```

#### 2. Design and Develop Data Processing (40-45%)

**Topics:**
- Implement Azure Synapse Analytics
- Design and develop batch processing
- Design and develop stream processing
- Implement Azure Databricks
- Work with Delta Lake

**Study Points:**

```python
# AZURE SYNAPSE ANALYTICS

# 1. Dedicated SQL Pool (formerly SQL DW)
CREATE TABLE FactSales
WITH (
    DISTRIBUTION = HASH(CustomerId),  # HASH, ROUND_ROBIN, REPLICATE
    CLUSTERED COLUMNSTORE INDEX,
    PARTITION (OrderDate RANGE RIGHT FOR VALUES ('2024-01-01'))
);

# Key Decisions:
# - Distribution: HASH for large tables, REPLICATE for small (<2GB)
# - Indexing: Columnstore for analytics, Heap for staging
# - Partitioning: By date, 1GB+ per partition

# 2. Serverless SQL Pool
# - Query data in data lake without loading
# - OPENROWSET for ad-hoc queries
# - External tables for reusable queries
SELECT *
FROM OPENROWSET(
    BULK 'https://account.dfs.core.windows.net/container/file.parquet',
    FORMAT = 'PARQUET'
) AS data;

# 3. Spark Pools
# - For data engineering workloads
# - Auto-scaling, auto-pause
# - Integration with notebooks, pipelines

# BATCH PROCESSING

# 1. Azure Data Factory
# Components:
- Pipelines: Orchestration
- Activities: Units of work
- Datasets: Data references
- Linked Services: Connections
- Triggers: Schedule, tumbling window, event-based

# Key Activities:
- Copy Activity: Move data
- Data Flow: Transform data
- Stored Procedure: Execute SQL
- Notebook: Run Spark code
- ForEach: Iterate over items
- If Condition: Conditional logic

# 2. Incremental Loading Pattern
# Using watermark:
{
  "name": "IncrementalCopyPipeline",
  "properties": {
    "activities": [
      {
        "name": "LookupOldWatermark",
        "type": "Lookup"
      },
      {
        "name": "LookupNewWatermark", 
        "type": "Lookup"
      },
      {
        "name": "IncrementalCopy",
        "type": "Copy",
        "inputs": [
          {
            "referenceName": "Source",
            "parameters": {
              "watermarkValue": "@activity('LookupOldWatermark').output"
            }
          }
        ]
      }
    ]
  }
}

# STREAM PROCESSING

# 1. Azure Stream Analytics
# Input sources:
- Event Hubs
- IoT Hub
- Blob Storage

# Output sinks:
- SQL Database
- Synapse Analytics
- Power BI
- Data Lake
- Event Hubs (for chaining)

# Example Query:
SELECT 
    DeviceId,
    AVG(Temperature) AS AvgTemp,
    System.Timestamp() AS WindowEnd
INTO 
    OutputAlias
FROM 
    InputAlias TIMESTAMP BY EventTime
GROUP BY 
    DeviceId,
    TumblingWindow(minute, 5);

# Window Types:
- Tumbling: Fixed, non-overlapping
- Hopping: Fixed, overlapping
- Sliding: Dynamic, based on events
- Session: Variable, based on gaps

# 2. Event Hubs
# Concepts:
- Partitions: Parallel processing (usually 4-32)
- Consumer Groups: Multiple readers
- Retention: 1-7 days (default 1)
- Capture: Automatic to storage

# DELTA LAKE

# 1. Core Features
# - ACID transactions
# - Schema evolution
# - Time travel
# - Upserts (MERGE)
# - Streaming + batch

# 2. Key Operations
# Read:
df = spark.read.format("delta").load("/path")
df_version = spark.read.format("delta").option("versionAsOf", 5).load("/path")

# Write:
df.write.format("delta").mode("overwrite").save("/path")

# Merge (Upsert):
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "/path")
deltaTable.alias("target") \
  .merge(source.alias("source"), "target.id = source.id") \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll() \
  .execute()

# Optimize:
spark.sql("OPTIMIZE delta.`/path` ZORDER BY (col1, col2)")

# Vacuum:
spark.sql("VACUUM delta.`/path` RETAIN 168 HOURS")
```

#### 3. Design and Implement Data Security (10-15%)

**Topics:**
- Implement data masking
- Configure encryption
- Implement row-level and column-level security
- Manage sensitive data

**Study Points:**

```sql
-- 1. Dynamic Data Masking (Azure SQL/Synapse)
CREATE TABLE Customers (
    CustomerId INT,
    Email VARCHAR(100) MASKED WITH (FUNCTION = 'email()'),
    CreditCard VARCHAR(20) MASKED WITH (FUNCTION = 'partial(0,"XXXX-XXXX-XXXX-",4)'),
    Salary DECIMAL(10,2) MASKED WITH (FUNCTION = 'default()')
);

-- Masking Functions:
-- - default(): Full masking
-- - email(): Shows first letter and .com
-- - random(min, max): Random number
-- - partial(prefix, padding, suffix): Custom masking

-- Grant unmask permission:
GRANT UNMASK TO UserName;

-- 2. Row-Level Security (RLS)
CREATE FUNCTION dbo.fn_securitypredicate(@SalesRegion AS nvarchar(50))
    RETURNS TABLE
WITH SCHEMABINDING
AS
    RETURN SELECT 1 AS fn_securitypredicate_result
    WHERE @SalesRegion = USER_NAME() OR USER_NAME() = 'Manager';

CREATE SECURITY POLICY SalesFilter
ADD FILTER PREDICATE dbo.fn_securitypredicate(SalesRegion)
ON dbo.Sales
WITH (STATE = ON);

-- 3. Column-Level Security
-- Grant column permissions:
GRANT SELECT ON dbo.Employees(EmployeeId, Name, Department) TO Employee;
-- Sensitive columns (Salary) not included

-- 4. Always Encrypted
-- Encrypt sensitive columns at rest and in transit
-- Keys stored in Azure Key Vault
-- Client-side encryption/decryption

-- 5. Transparent Data Encryption (TDE)
-- Automatic encryption at rest
-- Enabled by default on Azure SQL
ALTER DATABASE MyDatabase SET ENCRYPTION ON;

-- 6. Azure Key Vault Integration
-- Store connection strings, passwords, certificates
-- Managed identities for accessing Key Vault
-- Automatic key rotation
```

```python
# 7. Data Classification and Sensitivity Labels
# Microsoft Information Protection integration
# - Classify data (Public, Internal, Confidential, Restricted)
# - Apply encryption and access controls
# - Track data lineage with labels

# 8. Network Security
# - Virtual Network Service Endpoints
# - Private Endpoints
# - Firewall rules
# - IP whitelisting

# Configure storage firewall:
az storage account update \
    --name mystorageaccount \
    --default-action Deny

az storage account network-rule add \
    --account-name mystorageaccount \
    --ip-address 203.0.113.0/24
```

#### 4. Monitor and Optimize Data Storage and Processing (10-15%)

**Topics:**
- Monitor data pipelines
- Optimize query performance
- Implement alerts and metrics
- Troubleshoot data processing

**Study Points:**

```python
# 1. Azure Monitor and Log Analytics
# - Diagnostic settings for all services
# - Kusto Query Language (KQL)
# - Workbooks for visualization
# - Action Groups for alerts

# Example KQL Query:
AzureDiagnostics
| where ResourceType == "SYNAPSE/WORKSPACES"
| where OperationName == "SQLSecurityAuditEvents"
| where TimeGenerated > ago(24h)
| summarize count() by bin(TimeGenerated, 1h)

# 2. Performance Monitoring

# Synapse:
# - Query Performance Insight
# - DMVs (Dynamic Management Views)
# - Execution plans
SELECT 
    request_id,
    command,
    total_elapsed_time,
    status
FROM sys.dm_pdw_exec_requests
WHERE status NOT IN ('Completed', 'Failed', 'Cancelled')
ORDER BY submit_time DESC;

# Databricks:
# - Cluster metrics (CPU, memory, disk)
# - Spark UI (jobs, stages, tasks)
# - Ganglia metrics
# - Query history

# 3. Cost Optimization
# - Right-size compute resources
# - Use auto-scaling and auto-pause
# - Reserved capacity for predictable workloads
# - Spot instances for fault-tolerant workloads
# - Monitor with Cost Management

# 4. Alerts
# - Metric alerts (CPU, memory, DTU)
# - Log query alerts (custom KQL)
# - Activity log alerts (service health, resource changes)
# - Smart detection (anomaly detection)

# 5. Data Quality Monitoring
# - Great Expectations (Python)
# - Deequ (Spark)
# - Custom validation rules
```

### Study Plan (4-6 Weeks)

**Week 1-2: Storage and Batch Processing**
- Day 1-2: Azure Data Lake Gen2 (hands-on: create, configure, secure)
- Day 3-4: Azure Synapse Analytics (dedicated pools, serverless)
- Day 5-6: Azure Data Factory (pipelines, activities, triggers)
- Day 7: Practice labs and review

**Week 3-4: Streaming and Advanced Processing**
- Day 8-9: Azure Stream Analytics (windowing, queries)
- Day 10-11: Event Hubs, IoT Hub
- Day 12-13: Azure Databricks (clusters, notebooks, jobs)
- Day 14: Delta Lake (operations, optimization)

**Week 5: Security and Monitoring**
- Day 15-16: Security (RLS, data masking, encryption)
- Day 17-18: Monitoring (Azure Monitor, alerts, KQL)
- Day 19: Optimization techniques
- Day 20: Practice labs

**Week 6: Review and Practice**
- Day 21-23: Practice exams
- Day 24-25: Review weak areas
- Day 26: Final review
- Day 27: Take exam!

### Recommended Resources

**Official Microsoft Learn Paths:**
1. [Azure Data Engineer Learning Path](https://docs.microsoft.com/learn/certifications/azure-data-engineer)
2. [DP-203 Exam Prep](https://docs.microsoft.com/learn/certifications/exams/dp-203)

**Hands-On Labs:**
1. Microsoft Learn Sandbox
2. Azure Free Account ($200 credit)
3. Databricks Community Edition

**Practice Exams:**
1. MeasureUp Practice Tests
2. Whizlabs DP-203
3. Microsoft Official Practice Test

**Books:**
1. "Exam Ref DP-203 Data Engineering on Microsoft Azure"
2. "Azure Data Engineering Cookbook"

**Video Courses:**
1. Pluralsight: Azure Data Engineering Path
2. A Cloud Guru: DP-203 Course
3. Udemy: DP-203 Complete Course

---

## DP-600: Fabric Analytics Engineer

### Exam Overview

**Exam Details:**
- **Exam Code**: DP-600
- **Duration**: 100 minutes
- **Number of Questions**: 40-60
- **Passing Score**: 700/1000
- **Cost**: $165 USD
- **Format**: Multiple choice, case studies

**Prerequisites:**
- Microsoft Fabric fundamentals
- Power BI knowledge
- Data modeling experience
- SQL and DAX proficiency

### Exam Skills Measured

#### 1. Plan, Implement, and Manage a Fabric Solution (30-35%)

**Topics:**
- Plan and create Fabric workspace
- Implement and manage OneLake
- Implement version control and deployment
- Manage and monitor Fabric capacity

**Study Points:**

```python
# 1. Fabric Workspaces
# Types:
- Standard: Basic features
- Premium: Advanced features (paginated reports, XMLA endpoint)
- Premium Per User: Per-user licensing
- Fabric: New unified experience

# 2. OneLake
# - Single data lake for entire organization
# - Shortcuts: Virtual references to external data
# - Automatic indexing and optimization
# - Unified security model

# Create OneLake shortcut:
# Via UI: Workspace > Lakehouse > New shortcut > Select source

# 3. Git Integration
# - Version control for Fabric items
# - CI/CD pipelines
# - Branch strategies (main, dev, feature branches)
# - Automated deployment

# 4. Capacity Management
# - F SKUs (Fabric capacity units)
# - Auto-scale settings
# - Throttling and overload protection
# - Cost monitoring
```

#### 2. Prepare and Serve Data (35-40%)

**Topics:**
- Create and manage Fabric lakehouses
- Create and manage Fabric warehouses
- Implement data pipelines
- Implement dataflows

**Study Points:**

```python
# 1. Lakehouses
# Components:
- Tables: Delta Lake format
- Files: Unstructured data
- Shortcuts: External data references

# Best Practices:
- Use medallion architecture (Bronze/Silver/Gold)
- Partition large tables
- Optimize with OPTIMIZE and ZORDER
- Enable Change Data Feed for CDC

# 2. Warehouses
# Features:
- T-SQL support
- SQL endpoint for queries
- Integration with Power BI
- Cross-database queries

# Differences from Lakehouse:
# Lakehouse: Spark-first, flexible schema
# Warehouse: SQL-first, structured data

# 3. Data Pipelines
# Similar to Azure Data Factory
# Activities:
- Copy Data
- Notebook
- Stored Procedure
- Dataflow
- Script

# 4. Dataflows Gen2
# Power Query-based transformations
# Output to:
- Lakehouse table
- Warehouse table
- Custom endpoint

# Best for:
- Self-service data prep
- Reusable transformations
- No-code/low-code scenarios
```

#### 3. Implement and Manage Semantic Models (25-30%)

**Topics:**
- Design and build semantic models
- Optimize semantic model performance
- Implement calculations using DAX
- Implement row-level security

**Study Points:**

```dax
-- 1. Semantic Model Design
-- Star Schema:
-- - Fact tables: Metrics, high row count
-- - Dimension tables: Attributes, low row count
-- - Relationships: 1:* (one-to-many)

-- 2. Performance Optimization
-- - Use Import mode when possible (fastest)
-- - DirectQuery for real-time data
-- - Composite models for best of both
-- - Aggregations for large datasets
-- - Partitioning for incremental refresh

-- 3. DAX Calculations

-- Measures (calculated at query time):
Total Sales = SUM('Sales'[Amount])

Sales YTD = TOTALYTD([Total Sales], 'Date'[Date])

Sales % of Total = 
DIVIDE(
    [Total Sales],
    CALCULATE([Total Sales], ALL('Product'))
)

-- Calculated Columns (calculated at refresh):
Profit Margin = 'Sales'[Revenue] - 'Sales'[Cost]

-- Calculated Tables:
Date Table = CALENDAR(DATE(2020,1,1), DATE(2025,12,31))

-- 4. Time Intelligence
Sales Previous Year = 
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)

Sales Growth = 
DIVIDE(
    [Total Sales] - [Sales Previous Year],
    [Sales Previous Year]
)

-- 5. Row-Level Security (RLS)
-- Create role:
[Region] = USERNAME()

-- Or with mapping table:
LOOKUPVALUE(
    'UserRegion'[Region],
    'UserRegion'[Email],
    USERPRINCIPALNAME()
) = 'Sales'[Region]

-- 6. Object-Level Security (OLS)
-- Hide sensitive tables/columns from specific roles
-- Configured in semantic model settings
```

#### 4. Explore and Analyze Data (10-15%)

**Topics:**
- Perform exploratory data analysis
- Implement AI insights
- Query data using Spark and SQL

**Study Points:**

```python
# 1. Fabric Notebooks
# Supported languages:
- PySpark (Python + Spark)
- Spark SQL
- SparkR
- Scala

# Key features:
- Multiple languages in same notebook
- Rich visualizations
- Integration with lakehouses
- Parameterization
- Scheduling

# 2. Exploratory Data Analysis
import pyspark.sql.functions as F

# Load data
df = spark.read.table("lakehouse.table_name")

# Basic statistics
df.describe().show()

# Data profiling
df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) 
           for c in df.columns]).show()

# Distribution analysis
df.groupBy("category").agg(
    F.count("*").alias("count"),
    F.avg("amount").alias("avg_amount")
).show()

# 3. AI Insights
# - Anomaly detection
# - Forecasting
# - Key influencers
# - Decomposition tree
# - Smart narrative

# 4. Copilot in Fabric
# - Natural language to SQL
# - Code generation
# - Explanation of results
# - Suggested visualizations
```

### Study Plan (4-6 Weeks)

**Week 1-2: Fabric Fundamentals**
- Day 1-3: Workspaces, OneLake, capacity
- Day 4-6: Lakehouses and warehouses
- Day 7: Git integration and deployment

**Week 3: Data Engineering in Fabric**
- Day 8-10: Data pipelines and dataflows
- Day 11-12: Notebooks and Spark
- Day 13-14: Delta Lake optimization

**Week 4: Semantic Models and DAX**
- Day 15-17: Semantic model design
- Day 18-20: DAX calculations
- Day 21: RLS and OLS

**Week 5-6: Review and Practice**
- Day 22-24: Practice exams
- Day 25-27: Hands-on labs
- Day 28: Final review

### Recommended Resources

**Official Microsoft Learn:**
1. [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric)
2. [DP-600 Exam Prep](https://learn.microsoft.com/certifications/exams/dp-600)
3. [Fabric Learning Path](https://learn.microsoft.com/training/browse/?products=fabric)

**Hands-On:**
1. Microsoft Fabric Free Trial (60 days)
2. Fabric Community Samples
3. Fabric Workshops

**Practice:**
1. Microsoft Official Practice Tests
2. Community Practice Questions
3. Scenario-Based Labs

---

## Practice Questions

### DP-203 Sample Questions

**Question 1:**
You need to design a data storage solution that:
- Stores 500 TB of historical transaction data
- Supports ad-hoc SQL queries
- Minimizes cost

What should you recommend?

A) Azure SQL Database with Business Critical tier  
B) Azure Synapse dedicated SQL pool  
C) Azure Data Lake Gen2 with Synapse serverless SQL pool  
D) Azure Cosmos DB with SQL API

**Answer: C**
*Explanation: ADLS Gen2 provides cost-effective storage for large volumes, and serverless SQL pool allows ad-hoc queries without provisioning dedicated resources.*

---

**Question 2:**
You are loading data to a Synapse dedicated SQL pool fact table with 1 billion rows. The table is frequently joined with a dimension table containing 1000 rows.

How should you distribute the tables?

A) Both HASH distributed  
B) Fact table HASH distributed, dimension table REPLICATED  
C) Both ROUND_ROBIN distributed  
D) Fact table ROUND_ROBIN, dimension table HASH

**Answer: B**
*Explanation: Large fact tables should use HASH distribution for even data distribution. Small dimension tables (<2GB) should be REPLICATED to avoid shuffles during joins.*

---

**Question 3:**
You need to incrementally load data from Azure SQL Database to Azure Data Lake. The source table has a LastModifiedDate column.

What should you use?

A) Copy activity with a query using WHERE LastModifiedDate > @lastWatermark  
B) Data Flow with a lookup transformation  
C) Copy activity with full table scan  
D) Stored procedure activity

**Answer: A**
*Explanation: Using a query with watermark is the standard incremental loading pattern. It efficiently loads only changed records.*

---

### DP-600 Sample Questions

**Question 1:**
You have a Fabric lakehouse with a large fact table. Users report slow query performance when filtering by CustomerID and OrderDate.

What should you do?

A) Create a clustered index on CustomerID and OrderDate  
B) Run OPTIMIZE with ZORDER BY (CustomerID, OrderDate)  
C) Partition the table by CustomerID  
D) Create a materialized view

**Answer: B**
*Explanation: Delta Lake Z-Ordering co-locates related data for multiple columns, improving filter performance without requiring specific indexes.*

---

**Question 2:**
You need to implement a semantic model that:
- Supports real-time data
- Provides historical trend analysis
- Minimizes refresh time

Which storage mode should you use?

A) Import only  
B) DirectQuery only  
C) Composite model with aggregations  
D) Dual storage mode

**Answer: C**
*Explanation: Composite model allows Import for historical data (fast queries) and DirectQuery for real-time data. Aggregations further optimize performance for common queries.*

---

**Question 3:**
You are implementing row-level security in a semantic model. Different users should see data based on their email domain.

Which DAX expression should you use?

A) [Email] = USERPRINCIPALNAME()  
B) RIGHT([Email], LEN([Email]) - FIND("@", [Email])) = RIGHT(USERPRINCIPALNAME(), LEN(USERPRINCIPALNAME()) - FIND("@", USERPRINCIPALNAME()))  
C) [Domain] = USERNAME()  
D) CONTAINS([Email], USERNAME())

**Answer: B**
*Explanation: This expression extracts and compares email domains. USERPRINCIPALNAME() returns the user's email.*

---

## Exam Day Tips

### Before the Exam

1. **Get good sleep** (7-8 hours)
2. **Eat a good breakfast** 
3. **Arrive 30 minutes early** (or start online exam early)
4. **Bring valid ID** (government-issued photo ID)
5. **Review key concepts** (but don't cram)

### During the Exam

1. **Read questions carefully** (watch for "NOT", "EXCEPT")
2. **Flag uncertain questions** for review
3. **Manage time**: ~1.5-2 minutes per question
4. **Eliminate wrong answers** first
5. **Use case study time wisely**
6. **Check all answers** before submitting

### After the Exam

1. **Get your score immediately** (pass/fail)
2. **Review score report** (identifies weak areas)
3. **Certificate available** within 24-48 hours
4. **Add to LinkedIn** and resume
5. **Continue learning** (certifications expire in 1 year)

---

## Certification Renewal

**Renewal Requirements:**
- Pass renewal assessment before expiration (free)
- Available 6 months before expiration
- Online, open-book format
- Must renew annually

**Or:**
- Pass a higher-level exam
- Pass a related role-based exam

---

## Summary Checklist

### DP-203 Readiness
- [ ] Can design data lake folder structures
- [ ] Understand Synapse table distributions
- [ ] Can create ADF pipelines with incremental loading
- [ ] Know when to use batch vs streaming
- [ ] Can optimize Delta Lake tables
- [ ] Understand security concepts (RLS, data masking, encryption)
- [ ] Can write KQL queries for monitoring
- [ ] Have completed 3+ practice exams (score 80%+)

### DP-600 Readiness
- [ ] Understand Fabric workspace architecture
- [ ] Can create lakehouses and warehouses
- [ ] Know data pipeline components
- [ ] Can design semantic models (star schema)
- [ ] Proficient in DAX (measures, calculated columns, time intelligence)
- [ ] Can implement RLS in semantic models
- [ ] Understand performance optimization (aggregations, partitioning)
- [ ] Have completed 3+ practice exams (score 80%+)

---

**Good luck with your certification journey! 🎯**
