# Data Engineering Interview Preparation Guide

## Table of Contents
1. [Common Data Engineering Interview Questions](#common-interview-questions)
2. [Coding Challenges](#coding-challenges)
3. [System Design Questions](#system-design-questions)
4. [Behavioral Questions](#behavioral-questions)
5. [Mock Interview Scenarios](#mock-interview-scenarios)

---

## Common Interview Questions

### Technical Fundamentals

#### Q1: Explain the difference between batch processing and stream processing. When would you use each?

**Answer:**

**Batch Processing:**
- Processes large volumes of data at scheduled intervals
- Higher latency (minutes to hours)
- More cost-effective for large datasets
- Better for complete, accurate results
- Examples: Daily sales reports, monthly aggregations

**Stream Processing:**
- Processes data in real-time as it arrives
- Low latency (seconds to milliseconds)
- Higher operational cost
- Useful for time-sensitive decisions
- Examples: Fraud detection, real-time dashboards

**When to use:**
- **Batch**: Historical analysis, periodic reports, cost-sensitive workloads
- **Stream**: Real-time alerts, live dashboards, event-driven applications
- **Lambda Architecture**: Both - streaming for speed, batch for accuracy

---

#### Q2: What is the medallion architecture? How would you implement it?

**Answer:**

**Medallion Architecture** organizes data into three layers:

**Bronze Layer (Raw):**
- Ingests raw data as-is from sources
- Append-only, immutable
- Full fidelity and history
- Minimal transformations
```python
# Example
bronze_df = (spark.read.json("raw_events/")
    .withColumn("ingestion_time", current_timestamp())
    .withColumn("source_file", input_file_name()))

bronze_df.write.format("delta").mode("append").save("bronze/events")
```

**Silver Layer (Refined):**
- Cleaned and validated data
- Deduplicated
- Schema enforcement
- Business rules applied
```python
# Example
silver_df = (spark.read.format("delta").load("bronze/events")
    .filter(col("event_id").isNotNull())
    .dropDuplicates(["event_id"])
    .withColumn("processed_date", current_date()))

silver_df.write.format("delta").mode("overwrite").save("silver/events")
```

**Gold Layer (Curated):**
- Business-level aggregates
- Optimized for consumption
- Star schema / dimensional models
```python
# Example
gold_df = (spark.read.format("delta").load("silver/events")
    .groupBy("user_id", "event_date")
    .agg(count("*").alias("event_count")))

gold_df.write.format("delta").mode("overwrite").save("gold/user_daily_activity")
```

**Benefits:**
- Clear data lineage
- Can reprocess from any layer
- Progressive quality improvement
- Supports multiple use cases

---

#### Q3: How do you handle slowly changing dimensions (SCD)?

**Answer:**

**SCD Types:**

**Type 1 (Overwrite):**
- Simply update the record
- No history maintained
- Use when history isn't important
```sql
UPDATE Customer 
SET Address = 'New Address'
WHERE CustomerId = 123;
```

**Type 2 (Add New Row):**
- Add new record with version/dates
- Maintain complete history
- Most common approach
```python
# Implementation with Delta Lake
from delta.tables import DeltaTable

scd2_merge = """
MERGE INTO dim_customer target
USING (
    SELECT *, current_timestamp() as effective_date
    FROM source_customer
) source
ON target.customer_id = source.customer_id 
   AND target.is_current = true
WHEN MATCHED AND (
    target.address != source.address OR 
    target.phone != source.phone
) THEN 
    UPDATE SET is_current = false, end_date = source.effective_date
WHEN NOT MATCHED THEN
    INSERT (customer_id, address, phone, effective_date, is_current)
    VALUES (source.customer_id, source.address, source.phone, 
            source.effective_date, true)
"""

# Then insert new current record for changed rows
spark.sql(scd2_merge)
```

**Type 3 (Add New Column):**
- Store previous value in separate column
- Limited history (usually just one previous value)
```sql
ALTER TABLE Customer ADD PreviousAddress VARCHAR(200);

UPDATE Customer 
SET PreviousAddress = Address, Address = 'New Address'
WHERE CustomerId = 123;
```

**Type 4 (History Table):**
- Separate current and history tables
- Current table has latest, history has all changes

**Type 6 (Hybrid):**
- Combination of Type 1, 2, and 3
- Both current and previous columns plus historical records

---

#### Q4: Explain data partitioning. How do you choose the right partition key?

**Answer:**

**Partitioning** divides large tables into smaller, manageable chunks based on column values.

**Benefits:**
- Faster queries (partition pruning)
- Easier maintenance
- Better parallelism
- Cost reduction (read less data)

**Choosing Partition Key:**

**Good Partition Keys:**
1. **Date/Time columns** (most common)
   - Even distribution over time
   - Natural for time-series queries
   ```python
   df.write.partitionBy("year", "month", "day").parquet("data/")
   ```

2. **Category with moderate cardinality**
   - Region, department, product_category
   - Not too few (< 10) or too many (> 10,000) partitions

3. **Frequently filtered columns**
   - Matches query patterns
   - Enables partition pruning

**Avoid:**
- High cardinality columns (user_id with millions of values)
- Skewed data (one partition much larger)
- Columns rarely used in filters

**Example Decision:**
```python
# E-commerce orders dataset
# Query pattern: Last 30 days, specific regions

# Good partitioning:
df.write.partitionBy("order_date", "region").parquet("orders/")
# Result: orders/order_date=2024-01-15/region=US/data.parquet

# Query with partition pruning:
spark.read.parquet("orders/") \
    .filter((col("order_date") >= "2024-01-01") & 
            (col("region") == "US"))
# Only reads relevant partitions!
```

**Rules of Thumb:**
- Each partition should be 1GB+ (for Spark)
- Aim for 10-1000 partitions (not too few or many)
- Partition by columns used in WHERE clauses

---

#### Q5: How do you optimize Spark job performance?

**Answer:**

**1. Right-Size Cluster:**
```python
# Calculate optimal executor configuration
# Rule: 5 cores per executor, 10-16GB memory

spark.conf.set("spark.executor.instances", "20")
spark.conf.set("spark.executor.cores", "5")
spark.conf.set("spark.executor.memory", "16g")
spark.conf.set("spark.executor.memoryOverhead", "3g")
```

**2. Optimize Partitioning:**
```python
# Default partitions often too high/low
spark.conf.set("spark.sql.shuffle.partitions", "200")  # Adjust based on data size

# Repartition large datasets
df = df.repartition(200)  # For parallel processing

# Coalesce smaller datasets
df_filtered = df.filter(...).coalesce(10)  # Reduce partitions after filter
```

**3. Minimize Shuffles:**
```python
# Use broadcast joins for small tables
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")

# Pre-partition data by join key
df.write.partitionBy("customer_id").parquet("partitioned_data/")

# Reduce before shuffle
df.filter(...).groupBy(...)  # Filter before aggregation
```

**4. Cache Strategically:**
```python
# Cache DataFrames used multiple times
expensive_df = df.join(...).filter(...).cache()

# Use appropriate storage level
from pyspark.storagelevel import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)  # Spill to disk if needed
```

**5. Enable Optimizations:**
```python
# Adaptive Query Execution (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# Whole-stage code generation
spark.conf.set("spark.sql.codegen.wholeStage", "true")
```

**6. Handle Data Skew:**
```python
# Salting for skewed joins
df_salted = df.withColumn("salt", (rand() * 10).cast("int"))
df_salted = df_salted.withColumn("key_salted", 
    concat(col("key"), lit("_"), col("salt")))
```

**7. Use Delta Lake Optimizations:**
```python
# Z-Ordering for multi-column filters
spark.sql("OPTIMIZE table ZORDER BY (col1, col2)")

# Auto-optimize writes
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
```

---

### Azure-Specific Questions

#### Q6: Compare Azure Synapse dedicated SQL pool vs serverless SQL pool. When to use each?

**Answer:**

| Feature | Dedicated SQL Pool | Serverless SQL Pool |
|---------|-------------------|---------------------|
| **Compute Model** | Provisioned, always running | On-demand, pay-per-query |
| **Use Case** | Frequent queries, BI workloads | Ad-hoc queries, exploration |
| **Performance** | Faster (pre-provisioned) | Slower startup (cold start) |
| **Cost** | Fixed monthly cost (DWU) | Pay only for data scanned |
| **Data Storage** | Managed tables in SQL pool | External data (data lake) |
| **Best For** | Production DW, dashboards | Data exploration, ETL validation |

**Decision Matrix:**
- **Dedicated**: High query frequency, predictable workload, need SLAs
- **Serverless**: Infrequent queries, cost-sensitive, data exploration

**Example Use Cases:**
```sql
-- Dedicated SQL Pool: Production data warehouse
CREATE TABLE FactSales
WITH (
    DISTRIBUTION = HASH(CustomerID),
    CLUSTERED COLUMNSTORE INDEX
)
AS SELECT * FROM staging.sales;

-- Serverless SQL Pool: Ad-hoc exploration
SELECT TOP 100 *
FROM OPENROWSET(
    BULK 'https://account.dfs.core.windows.net/container/*.parquet',
    FORMAT = 'PARQUET'
) AS data
WHERE date >= '2024-01-01';
```

---

#### Q7: How do you implement incremental data loading in Azure Data Factory?

**Answer:**

**Pattern: Watermark-Based Incremental Load**

**Components:**
1. Watermark table (stores last successful load timestamp)
2. Lookup activities (get old and new watermarks)
3. Copy activity (load delta)
4. Stored procedure (update watermark)

**Implementation:**

```json
{
  "pipeline": {
    "activities": [
      {
        "name": "LookupOldWatermark",
        "type": "Lookup",
        "typeProperties": {
          "source": {
            "type": "AzureSqlSource",
            "sqlReaderQuery": "SELECT MAX(WatermarkValue) as WatermarkValue FROM watermarktable WHERE TableName = 'Orders'"
          }
        }
      },
      {
        "name": "LookupNewWatermark",
        "type": "Lookup",
        "typeProperties": {
          "source": {
            "type": "AzureSqlSource",
            "sqlReaderQuery": "SELECT MAX(ModifiedDate) as NewWatermark FROM Orders"
          }
        }
      },
      {
        "name": "IncrementalCopy",
        "type": "Copy",
        "dependsOn": [
          {"activity": "LookupOldWatermark"},
          {"activity": "LookupNewWatermark"}
        ],
        "typeProperties": {
          "source": {
            "type": "AzureSqlSource",
            "sqlReaderQuery": {
              "value": "SELECT * FROM Orders WHERE ModifiedDate > '@{activity('LookupOldWatermark').output.firstRow.WatermarkValue}' AND ModifiedDate <= '@{activity('LookupNewWatermark').output.firstRow.NewWatermark}'",
              "type": "Expression"
            }
          },
          "sink": {
            "type": "AzureDataLakeStoreSink"
          }
        }
      },
      {
        "name": "UpdateWatermark",
        "type": "SqlServerStoredProcedure",
        "dependsOn": [
          {"activity": "IncrementalCopy"}
        ],
        "typeProperties": {
          "storedProcedureName": "usp_write_watermark",
          "storedProcedureParameters": {
            "TableName": "Orders",
            "WatermarkValue": "@{activity('LookupNewWatermark').output.firstRow.NewWatermark}"
          }
        }
      }
    ]
  }
}
```

**Alternative: Change Data Capture (CDC)**
```python
# For databases supporting CDC
# Capture only inserts, updates, deletes since last run
# More efficient for large tables with few changes
```

---

## Coding Challenges

### Challenge 1: Find Duplicate Records

**Problem:** Given a DataFrame, find and return duplicate records based on specific columns.

```python
def find_duplicates(df, key_columns):
    """
    Find duplicate records based on key columns
    
    Args:
        df: Input DataFrame
        key_columns: List of column names to check for duplicates
    
    Returns:
        DataFrame with duplicate records
    """
    from pyspark.sql.window import Window
    from pyspark.sql.functions import row_number, count
    
    # Solution 1: Using window function
    window_spec = Window.partitionBy(key_columns).orderBy(key_columns)
    
    duplicates = (df
        .withColumn("row_num", row_number().over(window_spec))
        .withColumn("total_count", count("*").over(Window.partitionBy(key_columns)))
        .filter(col("total_count") > 1)
        .drop("row_num", "total_count"))
    
    return duplicates

# Solution 2: Using groupBy
def find_duplicates_v2(df, key_columns):
    dup_keys = (df.groupBy(key_columns)
        .count()
        .filter(col("count") > 1)
        .select(key_columns))
    
    return df.join(dup_keys, key_columns, "inner")

# Test
data = [
    (1, "Alice", "alice@email.com"),
    (2, "Bob", "bob@email.com"),
    (3, "Alice", "alice@email.com"),  # Duplicate
    (4, "Charlie", "charlie@email.com")
]
df = spark.createDataFrame(data, ["id", "name", "email"])

duplicates = find_duplicates(df, ["name", "email"])
duplicates.show()
# Output: Rows with id 1 and 3
```

---

### Challenge 2: Calculate Moving Average

**Problem:** Calculate 7-day moving average for sales data.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import avg

def calculate_moving_average(df, value_column, date_column, window_days=7):
    """
    Calculate moving average over specified window
    
    Args:
        df: Input DataFrame with date and value columns
        value_column: Column to calculate average for
        date_column: Date column for ordering
        window_days: Size of moving window in days
    
    Returns:
        DataFrame with moving average column
    """
    # Convert window days to seconds (Spark window spec uses seconds)
    window_seconds = window_days * 24 * 60 * 60
    
    # Define window: last N days including current day
    window_spec = (Window
        .orderBy(col(date_column).cast("timestamp").cast("long"))
        .rangeBetween(-window_seconds, 0))
    
    result = df.withColumn(
        f"moving_avg_{window_days}d",
        avg(value_column).over(window_spec)
    )
    
    return result

# Test
from pyspark.sql.functions import expr
sales_data = spark.range(10).select(
    expr("date_sub(current_date(), cast(id as int))").alias("date"),
    (expr("cast(rand() * 100 as int)")).alias("sales")
)

result = calculate_moving_average(sales_data, "sales", "date", 7)
result.orderBy("date").show()
```

---

### Challenge 3: Pivot Data

**Problem:** Transform data from long format to wide format.

```python
def pivot_data(df, index_cols, pivot_col, value_col):
    """
    Pivot DataFrame from long to wide format
    
    Args:
        df: Input DataFrame
        index_cols: Columns to keep as-is
        pivot_col: Column whose values become new columns
        value_col: Values to fill in pivoted columns
    
    Returns:
        Pivoted DataFrame
    """
    # Get distinct values for pivot column (for better performance)
    pivot_values = [row[pivot_col] for row in 
                    df.select(pivot_col).distinct().collect()]
    
    result = (df.groupBy(index_cols)
        .pivot(pivot_col, pivot_values)
        .agg(first(value_col)))
    
    return result

# Test
data = [
    ("2024-01-01", "Product A", 100),
    ("2024-01-01", "Product B", 150),
    ("2024-01-02", "Product A", 120),
    ("2024-01-02", "Product B", 180)
]
df = spark.createDataFrame(data, ["date", "product", "sales"])

pivoted = pivot_data(df, ["date"], "product", "sales")
pivoted.show()
# Output:
# +----------+---------+---------+
# |      date|Product A|Product B|
# +----------+---------+---------+
# |2024-01-01|      100|      150|
# |2024-01-02|      120|      180|
# +----------+---------+---------+
```

---

### Challenge 4: Detect Outliers

**Problem:** Identify outliers using IQR (Interquartile Range) method.

```python
from pyspark.sql.functions import percentile_approx

def detect_outliers_iqr(df, column, multiplier=1.5):
    """
    Detect outliers using IQR method
    
    Args:
        df: Input DataFrame
        column: Numeric column to check for outliers
        multiplier: IQR multiplier (typically 1.5)
    
    Returns:
        DataFrame with outlier indicator column
    """
    # Calculate quartiles
    quartiles = df.approxQuantile(column, [0.25, 0.75], 0.01)
    q1, q3 = quartiles[0], quartiles[1]
    iqr = q3 - q1
    
    lower_bound = q1 - (multiplier * iqr)
    upper_bound = q3 + (multiplier * iqr)
    
    # Mark outliers
    result = df.withColumn(
        "is_outlier",
        when(
            (col(column) < lower_bound) | (col(column) > upper_bound),
            True
        ).otherwise(False)
    )
    
    print(f"Q1: {q1}, Q3: {q3}, IQR: {iqr}")
    print(f"Lower bound: {lower_bound}, Upper bound: {upper_bound}")
    
    return result

# Test
import random
data = [(i, random.gauss(100, 15)) for i in range(1000)]  # Normal distribution
data.extend([(i, random.uniform(200, 300)) for i in range(10)])  # Outliers
df = spark.createDataFrame(data, ["id", "value"])

result = detect_outliers_iqr(df, "value")
result.filter(col("is_outlier") == True).show()
```

---

## System Design Questions

### Design Question 1: Real-Time Analytics Platform

**Problem:** Design a system to process and analyze 1 million events per second from IoT devices.

**Requirements:**
- Real-time dashboards (< 1 second latency)
- Historical analysis (last 2 years)
- Anomaly detection
- 99.9% availability
- Cost-optimized

**Solution Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    IoT Devices (1M devices)              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
           ┌───────────────────────┐
           │   Azure IoT Hub       │
           │ - Device management   │
           │ - Message routing     │
           └──────────┬────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│  Azure Stream   │       │  Azure Event    │
│   Analytics     │       │     Hubs        │
│                 │       │ - Partitions:32 │
│ - Windowing     │       │ - Retention:7d  │
│ - Aggregation   │       └────────┬────────┘
│ - Anomaly det.  │                │
└────────┬────────┘                │
         │                         ▼
         │                ┌─────────────────┐
         │                │  Spark Stream   │
         │                │   Processing    │
         │                │ - Complex CEP   │
         │                └────────┬────────┘
         │                         │
         ▼                         ▼
┌─────────────────────────────────────────┐
│         Delta Lake (ADLS Gen2)          │
│  Bronze: Raw events (1 month)           │
│  Silver: Processed (2 years)            │
│  Gold: Aggregated (2 years)             │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│Power BI  │    │  Synapse SQL │
│Dashboards│    │  Analytics   │
│Real-time │    │  Historical  │
└──────────┘    └──────────────┘
```

**Key Design Decisions:**

1. **Ingestion:**
   - IoT Hub for device management and telemetry
   - Event Hub for high-throughput event streaming
   - 32 partitions for 1M events/sec throughput

2. **Processing:**
   - Azure Stream Analytics for simple aggregations
   - Spark Structured Streaming for complex event processing
   - Both write to Delta Lake for unified storage

3. **Storage:**
   - Bronze: Raw events, 1 month retention (cost optimization)
   - Silver: Processed, 2 years (for analysis)
   - Gold: Aggregated, 2 years (for dashboards)

4. **Serving:**
   - Power BI Direct Lake for real-time dashboards
   - Synapse for ad-hoc analysis and ML

5. **Scaling:**
   - Event Hub auto-inflate for traffic spikes
   - Databricks auto-scaling for Spark
   - Synapse auto-pause for cost optimization

---

### Design Question 2: Multi-Region Data Warehouse

**Problem:** Design a globally distributed data warehouse for a multinational company.

**Requirements:**
- Data from 5 regions (US, EU, APAC, LATAM, Africa)
- Low-latency queries in each region
- Centralized reporting
- GDPR compliance (data residency)
- Cost-optimized

**Solution:**

```
Regional Data Sources
├── US Region
│   ├── SQL Database → ADLS Gen2 (US)
│   └── ERP System → Event Hub (US)
├── EU Region  
│   ├── SQL Database → ADLS Gen2 (EU)
│   └── SAP System → Event Hub (EU)
└── APAC Region
    ├── Oracle DB → ADLS Gen2 (APAC)
    └── Salesforce → Event Hub (APAC)

                  ↓
                  
Regional Processing
├── Fabric Workspace (US)
│   ├── Lakehouse (Bronze/Silver)
│   └── Local Warehouse (Gold)
├── Fabric Workspace (EU)
│   ├── Lakehouse (Bronze/Silver)
│   └── Local Warehouse (Gold)
└── Fabric Workspace (APAC)
    ├── Lakehouse (Bronze/Silver)
    └── Local Warehouse (Gold)

                  ↓
                  
    Aggregated Central Warehouse
    (Fabric Workspace - US Central)
    ├── Global Gold Layer
    ├── Aggregated Metrics Only
    └── Power BI Premium Capacity

                  ↓
                  
      Global Dashboards
      (Power BI Embedded)
```

**Key Design Decisions:**

1. **Data Residency:**
   - Bronze/Silver layers stay in region (GDPR compliance)
   - Only aggregated, anonymized data centralized

2. **Processing:**
   - Regional Fabric workspaces for local processing
   - OneLake shortcuts for cross-region access
   - Central workspace aggregates regional Gold layers

3. **Querying:**
   - Regional users query local warehouses (low latency)
   - Global users query central warehouse (aggregated)
   - Power BI caching for performance

4. **Replication:**
   - Event Hub for real-time replication
   - ADF for batch replication
   - OneLake shortcuts for virtualization

---

## Behavioral Questions

### Q1: Tell me about a time you optimized a slow data pipeline.

**STAR Method Answer:**

**Situation:**
"At my previous company, we had a nightly ETL pipeline processing customer transactions that was taking 8 hours to complete, missing our 6-hour SLA."

**Task:**
"I was tasked with optimizing the pipeline to meet the SLA while maintaining data quality and accuracy."

**Action:**
"I took a systematic approach:
1. First, I profiled the pipeline and identified bottlenecks using Spark UI
2. Found that a Cartesian join was causing massive shuffles
3. Implemented broadcast join for dimension tables (< 100MB)
4. Repartitioned large fact tables by join key before processing
5. Added Z-ordering on frequently queried columns in Delta Lake
6. Enabled adaptive query execution in Spark 3.0
7. Changed from MERGE to INSERT + DELETE for idempotent loads"

**Result:**
"Reduced runtime from 8 hours to 3.5 hours (56% improvement), well within SLA. Also reduced compute costs by 40% by finishing faster and using smaller cluster. Documented optimizations in runbook for team."

**Key Takeaway:**
"I learned the importance of data-driven optimization - profiling before optimizing, and measuring impact."

---

### Q2: Describe a situation where you had to handle a production data incident.

**STAR Answer:**

**Situation:**
"During a Black Friday sale, our real-time inventory system started showing incorrect stock levels, causing overselling."

**Task:**
"As on-call data engineer, I needed to identify and fix the issue immediately to prevent revenue loss and customer dissatisfaction."

**Action:**
"I followed our incident response procedure:
1. Immediately checked recent pipeline runs in ADF monitoring
2. Noticed a new deployment 2 hours prior coincided with issue start
3. Reviewed code changes - found a filter condition was reversed
4. Quick fix: Rolled back deployment to previous version
5. Verified data corrections: Re-ran pipeline for affected time window
6. Root cause analysis: Identified missing test coverage for edge case
7. Preventive measures: Added integration tests and data quality checks"

**Result:**
"Restored correct inventory within 30 minutes. Only 50 orders affected (vs thousands if delayed). Implemented automated data quality monitoring to catch similar issues before production."

---

## Mock Interview Scenarios

### Scenario 1: End-to-End Pipeline Design

**Interviewer:** "Design a data pipeline to ingest sales data from 500 retail stores, process it, and provide insights to executives."

**Your Approach:**

1. **Clarify Requirements:**
   - "What's the data volume per store per day?"
   - "What latency is acceptable for insights?"
   - "What are the key metrics executives need?"
   - "Any compliance requirements (PII, GDPR)?"

2. **Propose Architecture:**
   ```
   Stores (500) → Event Hub → Stream Analytics → Delta Lake
                     ↓             ↓                ↓
                 Real-time      Aggregation    Synapse SQL
                 Dashboard        (5 min)         Batch
                                    ↓               ↓
                                Power BI      Power BI
                               (Real-time)   (Historical)
   ```

3. **Justify Decisions:**
   - Event Hub: Handles 500 streams, auto-scaling
   - Stream Analytics: Simple aggregations, low latency
   - Delta Lake: ACID compliance, time travel for audits
   - Synapse: Complex analytical queries
   - Power BI: Executive dashboards, both real-time and historical

4. **Discuss Trade-offs:**
   - Cost vs latency: Real-time is expensive, batch is cheap
   - Complexity vs flexibility: Serverless is simple, Spark is powerful
   - Storage vs compute: Delta Lake optimizes both

---

## Interview Preparation Checklist

### Technical Skills
- [ ] Can explain batch vs stream processing
- [ ] Know when to use different Azure services
- [ ] Understand Spark optimization techniques
- [ ] Can design data models (star schema, SCD)
- [ ] Know Delta Lake operations (merge, optimize, vacuum)
- [ ] Can write complex SQL queries
- [ ] Understand distributed systems concepts

### Coding
- [ ] Practice PySpark DataFrame operations
- [ ] Write window functions
- [ ] Implement common patterns (dedup, pivot, join)
- [ ] Handle nulls and data quality
- [ ] Optimize queries

### System Design
- [ ] Can design end-to-end pipelines
- [ ] Understand CAP theorem trade-offs
- [ ] Know scaling strategies
- [ ] Design for fault tolerance
- [ ] Cost optimization approaches

### Behavioral
- [ ] Prepare STAR stories for common questions
- [ ] Have examples of: optimization, incident, collaboration, disagreement
- [ ] Show leadership and initiative
- [ ] Demonstrate learning from failures

---

**Final Tips:**
1. **Ask clarifying questions** - shows thoughtfulness
2. **Think out loud** - shows problem-solving process
3. **Start simple, then optimize** - shows pragmatism
4. **Consider trade-offs** - shows experience
5. **Be honest about unknowns** - shows integrity
6. **Follow up with interviewer** - shows interest

Good luck with your interviews! 🚀
