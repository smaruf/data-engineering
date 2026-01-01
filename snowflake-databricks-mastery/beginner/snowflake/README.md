# 🌱 Beginner Level - Snowflake

Welcome to the Snowflake beginner level! This section will help you get started with Snowflake from scratch.

## 📚 Learning Objectives

By completing this section, you will:
- ✅ Understand Snowflake architecture and key concepts
- ✅ Set up and connect to Snowflake using Python
- ✅ Perform basic CRUD operations (Create, Read, Update, Delete)
- ✅ Load data from various file formats (CSV, JSON, Parquet)
- ✅ Write and execute SQL queries
- ✅ Understand Snowflake data types and table structures

## 📁 Files in This Section

### 01_setup_connection.py
**What you'll learn:**
- Installing snowflake-connector-python
- Establishing connections to Snowflake
- Understanding connection parameters
- Using context managers for connections
- Proper error handling
- Verifying your connection

**Key Concepts:**
- Account identifier
- Virtual warehouses
- Databases and schemas
- Roles and permissions

### 02_basic_operations.py
**What you'll learn:**
- Creating databases and schemas
- Creating tables with different data types
- Inserting data (single and bulk inserts)
- Querying data with SELECT statements
- Updating existing records
- Deleting records
- Using transactions (BEGIN, COMMIT, ROLLBACK)

**Key Concepts:**
- DDL (Data Definition Language)
- DML (Data Manipulation Language)
- CRUD operations
- Transaction management
- VARIANT data type for JSON

### 03_data_loading.py
**What you'll learn:**
- Loading CSV files into Snowflake
- Loading JSON files
- Loading Parquet files
- Using COPY INTO command
- Creating and using file formats
- Creating and using stages
- Bulk loading strategies

**Key Concepts:**
- Internal stages vs. External stages
- File formats
- COPY INTO command
- Bulk loading best practices

### 04_simple_queries.py
**What you'll learn:**
- Basic SELECT statements
- WHERE clause filtering
- JOIN operations (INNER, LEFT, RIGHT, FULL)
- Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- GROUP BY and HAVING clauses
- ORDER BY and sorting
- Window functions basics

**Key Concepts:**
- SQL query structure
- Filtering and sorting
- Joins and relationships
- Aggregations
- Window functions

## 🚀 Getting Started

### Prerequisites

1. **Snowflake Account**
   - Sign up for free trial: https://signup.snowflake.com/
   - 30-day trial with $400 credits
   - No credit card required for trial

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

1. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

2. **Configure Snowflake credentials in .env**
   ```env
   SNOWFLAKE_ACCOUNT=your_account_identifier
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=DEMO_DB
   SNOWFLAKE_SCHEMA=PUBLIC
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   ```

3. **Find your account identifier**
   - Log into Snowflake web UI
   - Look at the URL: `https://<account_identifier>.snowflakecomputing.com`
   - Use the account identifier (e.g., `xy12345.us-east-1`)

### Running the Examples

Run the examples in order:

```bash
# Navigate to beginner/snowflake directory
cd beginner/snowflake

# Run examples in order
python 01_setup_connection.py
python 02_basic_operations.py
python 03_data_loading.py
python 04_simple_queries.py
```

## 📖 Snowflake Architecture Overview

### Key Components

1. **Cloud Services Layer**
   - Authentication and access control
   - Query parsing and optimization
   - Metadata management

2. **Query Processing Layer (Virtual Warehouses)**
   - Compute resources for query execution
   - Can be resized and suspended
   - Pay only for what you use

3. **Storage Layer**
   - Automatically managed cloud storage
   - Scales independently of compute
   - Data stored in compressed columnar format

### Virtual Warehouses

Virtual warehouses are compute clusters that execute queries:
- **Sizes**: X-Small, Small, Medium, Large, X-Large, 2X-Large, etc.
- **Auto-suspend**: Automatically pause when not in use
- **Auto-resume**: Automatically start when query is submitted
- **Cost**: Billed per second with 60-second minimum

### Databases and Schemas

```
Snowflake Account
└── Database (e.g., DEMO_DB)
    └── Schema (e.g., PUBLIC)
        └── Tables, Views, Stages, etc.
```

## 💡 Best Practices

### Connection Management
- ✅ Use environment variables for credentials
- ✅ Use context managers for automatic cleanup
- ✅ Handle exceptions properly
- ✅ Close connections when done

### Query Performance
- ✅ Use appropriate virtual warehouse sizes
- ✅ Suspend warehouses when not in use
- ✅ Use LIMIT for exploratory queries
- ✅ Select only needed columns

### Data Loading
- ✅ Use COPY INTO for bulk loading
- ✅ Compress files before loading
- ✅ Use appropriate file formats (Parquet is most efficient)
- ✅ Leverage parallel loading with multiple files

### Security
- ✅ Use role-based access control (RBAC)
- ✅ Never hardcode credentials
- ✅ Use least privilege principle
- ✅ Rotate credentials regularly

## 🎯 Practice Exercises

After completing the examples, try these exercises:

1. **Exercise 1: Customer Database**
   - Create a database for customer data
   - Create tables for customers, orders, and products
   - Insert sample data
   - Write queries to find top customers by order value

2. **Exercise 2: Data Loading**
   - Download a public dataset (e.g., from Kaggle)
   - Load it into Snowflake using COPY INTO
   - Perform basic analysis

3. **Exercise 3: Data Transformation**
   - Create a source table with raw data
   - Write queries to transform and clean the data
   - Create a new table with transformed data

4. **Exercise 4: JSON Processing**
   - Create a table with VARIANT column
   - Load JSON data
   - Query nested JSON fields
   - Flatten JSON arrays

## 📚 Additional Resources

### Official Documentation
- [Snowflake Documentation](https://docs.snowflake.com/)
- [Python Connector Guide](https://docs.snowflake.com/en/user-guide/python-connector.html)
- [SQL Reference](https://docs.snowflake.com/en/sql-reference.html)
- [Best Practices](https://docs.snowflake.com/en/user-guide/ui-snowsight-best-practices.html)

### Tutorials and Guides
- [Snowflake Getting Started](https://quickstarts.snowflake.com/)
- [Snowflake University](https://learn.snowflake.com/)
- [Data Loading Guide](https://docs.snowflake.com/en/user-guide-data-load.html)

### Community
- [Snowflake Community](https://community.snowflake.com/)
- [Stack Overflow - Snowflake](https://stackoverflow.com/questions/tagged/snowflake-cloud-data-platform)

## 🔍 Troubleshooting

### Common Issues

**Issue: Connection Timeout**
```
Solution: Check your account identifier, ensure VPN is not blocking connection
```

**Issue: Authentication Failed**
```
Solution: Verify username and password, check if account is active
```

**Issue: Warehouse Not Found**
```
Solution: Create a warehouse or use existing warehouse name (case-sensitive)
```

**Issue: Insufficient Privileges**
```
Solution: Ensure your user has appropriate role and permissions
```

## ✅ Completion Checklist

Before moving to intermediate level, ensure you can:

- [ ] Successfully connect to Snowflake from Python
- [ ] Create databases, schemas, and tables
- [ ] Insert, update, and delete data
- [ ] Write SELECT queries with WHERE, JOIN, and GROUP BY
- [ ] Load data from CSV, JSON, and Parquet files
- [ ] Use transactions (BEGIN, COMMIT, ROLLBACK)
- [ ] Understand Snowflake architecture basics
- [ ] Query JSON data using VARIANT type

## 🎓 Next Steps

Once you've completed the beginner level:

1. **Review and Practice**
   - Go through examples again
   - Modify code and experiment
   - Try the practice exercises

2. **Move to Intermediate Level**
   - Navigate to `intermediate/snowflake/`
   - Learn about Snowpipe, Streams, and Tasks
   - Explore Time Travel and Zero-Copy Cloning

3. **Explore Related Topics**
   - Learn SQL in more depth
   - Study data warehousing concepts
   - Understand cloud computing basics

---

**Happy Learning! ❄️**

Ready to move on? Head to the [Intermediate Level](../../intermediate/snowflake/README.md)
