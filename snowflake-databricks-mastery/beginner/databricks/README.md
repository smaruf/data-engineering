# 🌱 Beginner Level - Databricks

Welcome to the Databricks beginner level! This section will help you get started with Databricks and Apache Spark from scratch.

## 📚 Learning Objectives

By completing this section, you will:
- ✅ Understand Databricks architecture and key concepts
- ✅ Set up and connect to Databricks using Python
- ✅ Work with Spark DataFrames
- ✅ Perform basic transformations and actions
- ✅ Read and write data in various formats
- ✅ Execute SQL queries on DataFrames
- ✅ Understand basic Spark operations

## 📁 Files in This Section

### 01_setup_connection.py
**What you'll learn:**
- Installing PySpark
- Creating local Spark session
- Connecting to remote Databricks cluster
- Understanding Spark session configuration
- Basic Spark operations
- Error handling

**Key Concepts:**
- SparkSession
- Spark Context
- Cluster architecture (Driver, Executors)
- Local vs. Remote execution

### 02_dataframe_basics.py
**What you'll learn:**
- Creating DataFrames from various sources
- DataFrame schema and structure
- Displaying DataFrames
- Basic DataFrame operations
- Column operations
- Row filtering
- DataFrame transformations

**Key Concepts:**
- DataFrames vs. RDDs
- Lazy evaluation
- Transformations vs. Actions
- DataFrame schema
- Column expressions

### 03_read_write_data.py
**What you'll learn:**
- Reading CSV files
- Reading JSON files
- Reading Parquet files
- Writing data in various formats
- Schema inference
- Data partitioning
- Compression options

**Key Concepts:**
- File formats and performance
- Schema on read
- Partitioning strategies
- Compression codecs

### 04_transformations.py
**What you'll learn:**
- Select and drop columns
- Filter and where operations
- Adding and renaming columns
- Sorting and ordering
- Aggregations and grouping
- Joins (inner, left, right, full)
- Union and distinct operations

**Key Concepts:**
- Transformations (map, filter, flatMap)
- Actions (collect, count, show)
- Wide vs. Narrow transformations
- Shuffle operations

## 🚀 Getting Started

### Prerequisites

1. **Databricks Account** (Choose one)
   
   **Option A: Databricks Community Edition** (Free, Recommended for learning)
   - Sign up: https://databricks.com/try-databricks
   - Free tier with limited resources
   - Good for learning and experimentation
   
   **Option B: Cloud Provider Databricks**
   - AWS: https://databricks.com/aws
   - Azure: https://databricks.com/azure
   - GCP: https://databricks.com/gcp

2. **Python Environment**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

3. **Install Dependencies**
   ```bash
   cd snowflake-databricks-mastery
   pip install -r requirements.txt
   ```

### Environment Setup

#### For Local Development (PySpark)

1. **No additional setup needed!**
   - Examples run with local Spark by default
   - Perfect for learning without Databricks account

2. **Run examples:**
   ```bash
   cd beginner/databricks
   python 01_setup_connection.py
   ```

#### For Remote Databricks Connection

1. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

2. **Configure Databricks credentials in .env**
   ```env
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=your_access_token
   DATABRICKS_CLUSTER_ID=your_cluster_id
   ```

3. **Get your credentials:**
   
   **Databricks Token:**
   - Log into Databricks workspace
   - Click on your user profile (top right)
   - Go to "User Settings"
   - Click "Access Tokens" tab
   - Click "Generate New Token"
   - Copy and save the token
   
   **Cluster ID:**
   - Navigate to "Compute" in sidebar
   - Click on your cluster
   - Copy the cluster ID from the URL or cluster page

4. **Modify examples to use remote mode:**
   ```python
   conn_manager = DatabricksConnectionManager(mode="remote")
   ```

### Running the Examples

Run the examples in order:

```bash
# Navigate to beginner/databricks directory
cd beginner/databricks

# Run examples in order
python 01_setup_connection.py
python 02_dataframe_basics.py
python 03_read_write_data.py
python 04_transformations.py
```

## 📖 Databricks Architecture Overview

### Key Components

1. **Control Plane (Databricks Managed)**
   - Web application UI
   - Cluster manager
   - Notebook server
   - Job scheduler

2. **Data Plane (Your Cloud Account)**
   - Spark clusters (Driver + Executors)
   - Storage (DBFS, cloud storage)
   - Compute resources

### Spark Architecture

```
SparkSession
└── SparkContext
    └── Cluster Manager
        └── Worker Nodes
            ├── Executor 1 (Cache, Tasks)
            ├── Executor 2 (Cache, Tasks)
            └── Executor N (Cache, Tasks)
```

**Driver:**
- Runs your application's main() function
- Creates SparkContext
- Converts operations into DAG
- Schedules tasks on executors

**Executors:**
- Run tasks assigned by driver
- Store data for caching
- Report status back to driver

### DataFrames vs RDDs

**DataFrames** (Recommended):
- Structured data with schema
- Optimized execution (Catalyst optimizer)
- Similar to SQL tables
- Best for most use cases

**RDDs** (Lower level):
- Unstructured distributed collections
- More control but less optimization
- Use when DataFrame API is insufficient

## 💡 Best Practices

### Performance
- ✅ Use DataFrames over RDDs when possible
- ✅ Cache frequently used DataFrames
- ✅ Use appropriate file formats (Parquet for analytics)
- ✅ Partition data appropriately
- ✅ Use broadcast joins for small tables
- ✅ Avoid collect() on large datasets

### Development
- ✅ Start with local Spark for development
- ✅ Use show() and explain() to understand operations
- ✅ Test with small data samples first
- ✅ Use DataFrame API over SQL for complex operations
- ✅ Monitor Spark UI for job progress

### Data Operations
- ✅ Prefer Parquet over CSV for large datasets
- ✅ Use compression (snappy, gzip)
- ✅ Partition data by frequently queried columns
- ✅ Avoid small files (combine when possible)
- ✅ Use schema inference cautiously (prefer explicit schemas)

## 🎯 Practice Exercises

After completing the examples, try these exercises:

1. **Exercise 1: Sales Analysis**
   - Create a DataFrame with sales data
   - Calculate total sales by category
   - Find top 10 products by revenue
   - Calculate average order value

2. **Exercise 2: Data Cleaning**
   - Load a dataset with missing values
   - Handle null values (drop, fill, replace)
   - Remove duplicates
   - Standardize column names

3. **Exercise 3: Joins and Aggregations**
   - Create customers and orders DataFrames
   - Join them on customer_id
   - Calculate customer lifetime value
   - Identify top customers

4. **Exercise 4: File Format Comparison**
   - Load same data in CSV, JSON, and Parquet
   - Compare file sizes
   - Compare read performance
   - Analyze differences

## 📚 Additional Resources

### Official Documentation
- [Databricks Documentation](https://docs.databricks.com/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/)
- [DataFrame Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)

### Learning Resources
- [Databricks Academy](https://academy.databricks.com/)
- [Spark by Examples](https://sparkbyexamples.com/)
- [Databricks Quickstarts](https://docs.databricks.com/getting-started/index.html)

### Community
- [Databricks Community](https://community.databricks.com/)
- [Stack Overflow - PySpark](https://stackoverflow.com/questions/tagged/pyspark)
- [Apache Spark Slack](https://apache-spark.slack.com/)

## 🔍 Troubleshooting

### Common Issues

**Issue: Spark Session Won't Start**
```
Solution: Check Java installation (Java 8 or 11 required)
         Verify JAVA_HOME environment variable
```

**Issue: Out of Memory Error**
```
Solution: Increase driver/executor memory
         Process data in smaller batches
         Use repartition() to manage parallelism
```

**Issue: File Not Found**
```
Solution: Check file path (use absolute paths)
         Verify file exists and is accessible
         Check permissions
```

**Issue: Connection to Databricks Failed**
```
Solution: Verify token is correct
         Check cluster is running
         Ensure cluster ID is correct
```

## 🧪 Testing Your Knowledge

### Quick Quiz

1. What is the difference between a transformation and an action?
2. Why is Parquet preferred over CSV for large datasets?
3. What does lazy evaluation mean in Spark?
4. When should you use cache()?
5. What is the purpose of partitioning?

### Hands-On Challenge

Create a complete data pipeline:
1. Load employee and department data
2. Join the datasets
3. Calculate average salary by department
4. Find employees earning above department average
5. Save results to Parquet

## ✅ Completion Checklist

Before moving to intermediate level, ensure you can:

- [ ] Create and configure a Spark session
- [ ] Create DataFrames from lists and files
- [ ] Perform basic transformations (select, filter, etc.)
- [ ] Execute aggregations and grouping
- [ ] Join multiple DataFrames
- [ ] Read and write data in CSV, JSON, and Parquet
- [ ] Execute SQL queries on DataFrames
- [ ] Understand lazy evaluation concept
- [ ] Use Spark UI for monitoring (bonus)

## 🎓 Next Steps

Once you've completed the beginner level:

1. **Review and Practice**
   - Re-run examples with your own data
   - Complete all practice exercises
   - Experiment with different transformations

2. **Move to Intermediate Level**
   - Navigate to `intermediate/databricks/`
   - Learn about Delta Lake
   - Explore Structured Streaming
   - Dive into MLflow

3. **Explore Databricks Features**
   - Create notebooks in Databricks workspace
   - Explore the Data page (DBFS)
   - Try Databricks SQL
   - Experiment with collaborative notebooks

---

**Happy Learning! 🧱**

Ready to move on? Head to the [Intermediate Level](../../intermediate/databricks/README.md)
