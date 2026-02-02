# Data Engineering Architecture Patterns

## Table of Contents
1. [Medallion Architecture (Bronze-Silver-Gold)](#medallion-architecture)
2. [Lambda Architecture](#lambda-architecture)
3. [Kappa Architecture](#kappa-architecture)
4. [Data Mesh](#data-mesh)
5. [Lakehouse Architecture](#lakehouse-architecture)
6. [Microservices for Data](#microservices-for-data)
7. [Real-World Examples](#real-world-examples)

---

## Medallion Architecture (Bronze-Silver-Gold)

### Overview
The Medallion Architecture is a data design pattern used to logically organize data in a lakehouse, with the goal of incrementally improving the quality and structure of data as it flows through each layer.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                       GOLD LAYER                             │
│              (Business-Level Aggregates)                     │
│  • Highly curated, business-ready data                       │
│  • Star/snowflake schemas                                    │
│  • Power BI semantic models                                  │
│  • Aggregated metrics                                        │
└──────────────────────▲──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                      SILVER LAYER                            │
│              (Cleaned & Conformed)                           │
│  • Validated and deduplicated                                │
│  • Standardized schemas                                      │
│  • Slowly Changing Dimensions                                │
│  • Data quality rules applied                                │
└──────────────────────▲──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                      BRONZE LAYER                            │
│                (Raw Data Ingestion)                          │
│  • Raw data as-is from source                                │
│  • Append-only                                               │
│  • Full fidelity & history                                   │
│  • Minimal transformation                                    │
└──────────────────────────────────────────────────────────────┘
```

### Bronze Layer (Raw Zone)

**Purpose**: Ingest and store raw data exactly as received from source systems.

**Characteristics**:
- **Append-only**: Never delete data, only append
- **Full fidelity**: Preserve all source data attributes
- **Minimal schema**: Schema-on-read approach
- **Audit trail**: Complete lineage from source
- **Format**: Usually Parquet, Delta Lake, or JSON

**Example Structure**:
```
bronze/
├── orders/
│   ├── source=erp/
│   │   ├── year=2024/
│   │   │   ├── month=01/
│   │   │   │   ├── day=15/
│   │   │   │   │   └── data.parquet
├── customers/
│   ├── source=crm/
│   │   ├── load_date=2024-01-15/
│   │   │   └── snapshot.parquet
└── events/
    ├── source=clickstream/
    │   ├── year=2024/month=01/day=15/hour=10/
    │   │   └── events.json
```

**Implementation Example (PySpark)**:
```python
# Bronze Layer Ingestion
def ingest_to_bronze(source_path, bronze_path, source_name):
    """
    Ingest raw data to bronze layer with metadata
    """
    from pyspark.sql.functions import current_timestamp, lit, input_file_name
    
    df = (spark.read
          .format("json")  # or csv, parquet, etc.
          .option("inferSchema", "true")
          .load(source_path))
    
    # Add metadata columns
    enriched_df = (df
                   .withColumn("_ingestion_timestamp", current_timestamp())
                   .withColumn("_source_system", lit(source_name))
                   .withColumn("_source_file", input_file_name()))
    
    # Write to bronze with partitioning
    (enriched_df.write
     .format("delta")
     .mode("append")
     .partitionBy("_ingestion_date")
     .save(bronze_path))
```

### Silver Layer (Refined Zone)

**Purpose**: Clean, conform, and validate data; apply business rules.

**Characteristics**:
- **Validated**: Data quality checks applied
- **Conformed**: Standardized formats and schemas
- **Deduplicated**: Remove duplicates
- **Type-safe**: Strong schema enforcement
- **Historized**: SCD Type 2 for historical tracking

**Transformations Applied**:
1. Data cleansing (nulls, invalid values)
2. Standardization (date formats, codes)
3. Deduplication
4. Schema enforcement
5. Data quality checks
6. Business rule application

**Example Structure**:
```
silver/
├── dim_customer/
│   └── _delta_log/
│   └── part-*.parquet
├── dim_product/
│   └── _delta_log/
│   └── part-*.parquet
├── fact_orders/
│   ├── order_date=2024-01-15/
│   │   └── part-*.parquet
└── fact_events/
    └── event_type=page_view/
        └── part-*.parquet
```

**Implementation Example**:
```python
# Silver Layer Processing
def bronze_to_silver_customers(bronze_path, silver_path):
    """
    Clean and conform customer data from bronze to silver
    """
    from pyspark.sql.functions import (
        col, regexp_replace, trim, upper, 
        when, to_date, row_number
    )
    from pyspark.sql.window import Window
    
    # Read from bronze
    bronze_df = spark.read.format("delta").load(bronze_path)
    
    # Cleansing and standardization
    cleaned_df = (bronze_df
        # Standardize phone numbers
        .withColumn("phone", regexp_replace(col("phone"), "[^0-9]", ""))
        # Trim and uppercase text fields
        .withColumn("email", lower(trim(col("email"))))
        .withColumn("country", upper(trim(col("country"))))
        # Handle nulls
        .withColumn("status", 
                    when(col("status").isNull(), "UNKNOWN")
                    .otherwise(col("status")))
        # Standardize dates
        .withColumn("birth_date", to_date(col("birth_date"), "yyyy-MM-dd"))
    )
    
    # Deduplication - keep latest record per customer
    window_spec = Window.partitionBy("customer_id").orderBy(col("_ingestion_timestamp").desc())
    
    deduped_df = (cleaned_df
        .withColumn("row_num", row_number().over(window_spec))
        .filter(col("row_num") == 1)
        .drop("row_num"))
    
    # Data quality checks
    valid_df = (deduped_df
        .filter(col("customer_id").isNotNull())
        .filter(col("email").rlike("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$"))
    )
    
    # Write to silver with schema enforcement
    (valid_df.write
     .format("delta")
     .mode("overwrite")
     .option("mergeSchema", "false")  # Enforce schema
     .save(silver_path))
    
    # Data quality metrics
    total_records = bronze_df.count()
    valid_records = valid_df.count()
    quality_score = (valid_records / total_records) * 100
    
    print(f"Data Quality Score: {quality_score:.2f}%")
    print(f"Records processed: {total_records}")
    print(f"Valid records: {valid_records}")
    print(f"Rejected records: {total_records - valid_records}")
```

### Gold Layer (Curated Zone)

**Purpose**: Business-level aggregates optimized for analytics and reporting.

**Characteristics**:
- **Business-focused**: Organized by business domains
- **Highly aggregated**: Pre-calculated metrics
- **Star schema**: Dimensional modeling
- **Optimized**: Query performance optimized
- **Governed**: Strong access controls

**Typical Tables**:
- Dimensional models (star/snowflake schemas)
- Business KPIs and metrics
- Aggregated fact tables
- Materialized views
- Reporting-specific structures

**Example Structure**:
```
gold/
├── sales_analytics/
│   ├── daily_sales_summary/
│   ├── customer_360/
│   └── product_performance/
├── finance/
│   ├── revenue_by_region/
│   └── cost_analysis/
└── operations/
    ├── inventory_levels/
    └── fulfillment_metrics/
```

**Implementation Example**:
```python
# Gold Layer Aggregation
def create_daily_sales_summary(silver_orders_path, silver_customers_path, gold_path):
    """
    Create business-level aggregated metrics
    """
    from pyspark.sql.functions import sum, count, avg, date_trunc
    
    # Read from silver layer
    orders = spark.read.format("delta").load(silver_orders_path)
    customers = spark.read.format("delta").load(silver_customers_path)
    
    # Join and aggregate
    daily_summary = (orders
        .join(customers, "customer_id")
        .withColumn("order_date", date_trunc("day", col("order_timestamp")))
        .groupBy("order_date", "customer_segment", "region")
        .agg(
            sum("order_amount").alias("total_revenue"),
            count("order_id").alias("total_orders"),
            avg("order_amount").alias("avg_order_value"),
            countDistinct("customer_id").alias("unique_customers")
        )
    )
    
    # Write to gold with optimization
    (daily_summary.write
     .format("delta")
     .mode("overwrite")
     .partitionBy("order_date")
     .option("optimizeWrite", "true")
     .option("dataSkippingNumIndexedCols", "5")
     .save(gold_path))
    
    # Optimize for queries
    spark.sql(f"""
        OPTIMIZE delta.`{gold_path}`
        ZORDER BY (customer_segment, region)
    """)
```

### Benefits of Medallion Architecture

1. **Data Quality**: Progressive improvement across layers
2. **Flexibility**: Can reprocess from any layer
3. **Compliance**: Complete audit trail in bronze
4. **Performance**: Optimized for different use cases
5. **Governance**: Clear data lineage and ownership
6. **Cost-effective**: Store raw data cheaply, optimize expensive layers

### Best Practices

1. **Never delete bronze data**: It's your source of truth
2. **Idempotent transformations**: Same input = same output
3. **Schema evolution**: Plan for schema changes
4. **Incremental processing**: Process only new/changed data
5. **Data quality checks**: At every layer transition
6. **Monitoring**: Track data quality metrics
7. **Documentation**: Document transformations and business rules

---

## Lambda Architecture

### Overview
Lambda Architecture is designed to handle massive quantities of data by taking advantage of both batch and stream processing methods.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                            │
│          (IoT, Events, Transactions, Logs, etc.)              │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────┐
│  BATCH LAYER  │         │ SPEED LAYER  │
│               │         │              │
│ • Immutable   │         │ • Real-time  │
│   master      │         │   processing │
│   dataset     │         │ • Mutable    │
│ • Batch       │         │   state      │
│   processing  │         │ • Low        │
│ • Complete    │         │   latency    │
│   accuracy    │         │              │
└───────┬───────┘         └──────┬───────┘
        │                        │
        │   ┌────────────────────┘
        │   │
        ▼   ▼
    ┌────────────┐
    │  SERVING   │
    │   LAYER    │
    │            │
    │ • Merge    │
    │   batch &  │
    │   real-time│
    │ • Query    │
    │   interface│
    └─────┬──────┘
          │
          ▼
    ┌──────────┐
    │  CLIENTS │
    └──────────┘
```

### Components

#### 1. Batch Layer
**Purpose**: Manages the master dataset and pre-computes batch views.

**Characteristics**:
- Immutable, append-only dataset
- Complete and accurate results
- High latency (hours to days)
- Recomputable from source data

**Implementation**:
```python
# Batch Layer - Daily Aggregation
def batch_layer_processing(master_data_path, batch_view_path, processing_date):
    """
    Batch processing for complete, accurate aggregations
    """
    from datetime import datetime, timedelta
    
    # Read master dataset
    master_df = spark.read.format("delta").load(master_data_path)
    
    # Calculate start and end of processing window
    start_date = datetime.strptime(processing_date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=1)
    
    # Batch aggregation - complete recalculation
    batch_view = (master_df
        .filter(
            (col("timestamp") >= start_date) & 
            (col("timestamp") < end_date)
        )
        .groupBy("user_id", "product_id", date_trunc("hour", "timestamp").alias("hour"))
        .agg(
            sum("amount").alias("total_amount"),
            count("*").alias("transaction_count"),
            avg("amount").alias("avg_amount")
        )
    )
    
    # Write batch view
    (batch_view.write
     .format("delta")
     .mode("overwrite")
     .partitionBy("processing_date")
     .save(f"{batch_view_path}/date={processing_date}"))
```

#### 2. Speed Layer
**Purpose**: Provides low-latency updates for recent data.

**Characteristics**:
- Real-time or near real-time processing
- Approximate results (eventual consistency)
- Compensates for batch layer latency
- Incremental algorithms

**Implementation**:
```python
# Speed Layer - Streaming Aggregation
def speed_layer_processing(stream_source, speed_view_path):
    """
    Real-time streaming for low-latency results
    """
    from pyspark.sql.functions import window
    
    # Read streaming source
    stream_df = (spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "transactions")
        .load())
    
    # Parse and process stream
    parsed_df = (stream_df
        .selectExpr("CAST(value AS STRING) as json")
        .select(from_json(col("json"), transaction_schema).alias("data"))
        .select("data.*"))
    
    # Windowed aggregation
    windowed_aggregation = (parsed_df
        .withWatermark("timestamp", "10 minutes")
        .groupBy(
            "user_id", 
            "product_id",
            window("timestamp", "5 minutes", "1 minute")
        )
        .agg(
            sum("amount").alias("recent_total"),
            count("*").alias("recent_count")
        )
    )
    
    # Write to speed layer (in-memory or fast storage)
    query = (windowed_aggregation.writeStream
        .format("delta")
        .outputMode("update")
        .option("checkpointLocation", f"{speed_view_path}/_checkpoint")
        .start(speed_view_path))
    
    return query
```

#### 3. Serving Layer
**Purpose**: Merges batch and speed layer results to answer queries.

**Implementation**:
```python
# Serving Layer - Query Interface
def query_serving_layer(user_id, product_id, batch_view_path, speed_view_path):
    """
    Merge batch and speed layer for complete results
    """
    from datetime import datetime, timedelta
    
    # Get batch layer results (older than 2 hours)
    batch_cutoff = datetime.now() - timedelta(hours=2)
    
    batch_results = (spark.read
        .format("delta")
        .load(batch_view_path)
        .filter(col("hour") < batch_cutoff)
        .filter((col("user_id") == user_id) & (col("product_id") == product_id))
        .agg(
            sum("total_amount").alias("batch_total"),
            sum("transaction_count").alias("batch_count")
        )
        .collect()[0])
    
    # Get speed layer results (last 2 hours)
    speed_results = (spark.read
        .format("delta")
        .load(speed_view_path)
        .filter(col("window.start") >= batch_cutoff)
        .filter((col("user_id") == user_id) & (col("product_id") == product_id))
        .agg(
            sum("recent_total").alias("speed_total"),
            sum("recent_count").alias("speed_count")
        )
        .collect()[0])
    
    # Merge results
    total_amount = batch_results.batch_total + speed_results.speed_total
    total_count = batch_results.batch_count + speed_results.speed_count
    
    return {
        "user_id": user_id,
        "product_id": product_id,
        "total_amount": total_amount,
        "total_transactions": total_count,
        "batch_contribution": batch_results.batch_total,
        "realtime_contribution": speed_results.speed_total
    }
```

### When to Use Lambda Architecture

**Pros**:
- ✅ Handles both real-time and batch processing
- ✅ Fault-tolerant (can recompute from master dataset)
- ✅ Scalable for massive datasets
- ✅ Accurate results from batch layer

**Cons**:
- ❌ Complex to maintain (two processing paths)
- ❌ Code duplication between layers
- ❌ Operational overhead

**Use Cases**:
- Real-time analytics dashboards with historical data
- E-commerce: real-time inventory + historical sales analysis
- IoT: real-time monitoring + long-term trend analysis
- Financial services: real-time fraud detection + historical reporting

---

## Kappa Architecture

### Overview
Kappa Architecture simplifies Lambda by removing the batch layer, using stream processing for everything.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  EVENT LOG    │
                 │  (Kafka/      │
                 │   Event Hub)  │
                 └───────┬───────┘
                         │
                         ▼
                ┌─────────────────┐
                │ STREAM PROCESSING│
                │    LAYER         │
                │                  │
                │ • Real-time      │
                │ • Replayable     │
                │ • Single codebase│
                └────────┬─────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  SERVING DB   │
                 │               │
                 │ • Fast queries│
                 │ • Materialized│
                 │   views       │
                 └───────┬───────┘
                         │
                         ▼
                    ┌─────────┐
                    │ CLIENTS │
                    └─────────┘
```

### Key Principles

1. **Everything is a stream**: Treat all data as streams
2. **Replayable log**: Use event log as source of truth
3. **Single pipeline**: One processing logic for all data
4. **Recomputation**: Re-process by replaying event log

### Implementation Example

```python
# Kappa Architecture - Single Stream Processing Pipeline
class KappaProcessor:
    """
    Unified stream processing for all data
    """
    
    def __init__(self, kafka_servers, checkpoint_location):
        self.kafka_servers = kafka_servers
        self.checkpoint_location = checkpoint_location
    
    def process_stream(self, topic, processing_logic):
        """
        Generic stream processing with replay capability
        """
        # Read from Kafka (can replay from any offset)
        stream_df = (spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.kafka_servers)
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")  # Can replay entire history
            .load())
        
        # Apply processing logic
        processed_df = processing_logic(stream_df)
        
        # Write to serving layer
        query = (processed_df.writeStream
            .format("delta")
            .outputMode("update")
            .option("checkpointLocation", f"{self.checkpoint_location}/{topic}")
            .trigger(processingTime="10 seconds")
            .start())
        
        return query
    
    def user_analytics_logic(self, stream_df):
        """
        Example processing logic for user analytics
        """
        from pyspark.sql.functions import from_json, col, window, count, sum
        
        # Parse events
        parsed = (stream_df
            .selectExpr("CAST(value AS STRING) as json", "timestamp")
            .select(
                from_json(col("json"), event_schema).alias("data"),
                col("timestamp")
            )
            .select("data.*", "timestamp"))
        
        # Aggregate with tumbling window
        aggregated = (parsed
            .withWatermark("timestamp", "1 hour")
            .groupBy(
                "user_id",
                window("timestamp", "1 hour")
            )
            .agg(
                count("event_id").alias("event_count"),
                sum("revenue").alias("total_revenue")
            ))
        
        return aggregated
    
    def reprocess_historical_data(self, topic, start_date, end_date):
        """
        Reprocess historical data by replaying Kafka log
        """
        # Calculate Kafka offsets for date range
        start_offset = self.get_offset_for_timestamp(topic, start_date)
        end_offset = self.get_offset_for_timestamp(topic, end_date)
        
        # Process historical range
        stream_df = (spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.kafka_servers)
            .option("subscribe", topic)
            .option("startingOffsets", f'{{"topic": {{"{topic}": {start_offset}}}}}')
            .option("endingOffsets", f'{{"topic": {{"{topic}": {end_offset}}}}}')
            .load())
        
        return self.process_stream(stream_df)

# Usage
processor = KappaProcessor(
    kafka_servers="localhost:9092",
    checkpoint_location="/mnt/checkpoints"
)

# Process real-time stream
query = processor.process_stream("user_events", processor.user_analytics_logic)

# Reprocess last 30 days (bug fix or logic change)
historical_query = processor.reprocess_historical_data(
    topic="user_events",
    start_date="2024-01-01",
    end_date="2024-01-30"
)
```

### Advantages Over Lambda

1. **Simpler**: Single processing pipeline
2. **Less code**: No duplication between batch and speed layers
3. **Easier maintenance**: One codebase to maintain
4. **Flexibility**: Easy to reprocess data by replaying log

### When to Use Kappa Architecture

**Best for**:
- Stream-first organizations
- Real-time analytics requirements
- Need to frequently reprocess data
- Want to avoid code duplication

**Not ideal for**:
- Truly massive historical computations
- Complex batch algorithms that don't fit streaming model
- When event log retention is cost-prohibitive

---

## Data Mesh

### Overview
Data Mesh is a decentralized sociotechnical approach to data architecture that treats data as a product, organized by business domains.

### Core Principles

```
┌────────────────────────────────────────────────────────────────┐
│                      DATA MESH PRINCIPLES                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Domain-Oriented Ownership                                   │
│     • Domains own their data                                   │
│     • Cross-functional teams                                   │
│                                                                 │
│  2. Data as a Product                                          │
│     • Discoverable, addressable, trustworthy                   │
│     • Self-serve interfaces                                    │
│                                                                 │
│  3. Self-Serve Data Platform                                   │
│     • Infrastructure as a platform                             │
│     • Domain autonomy with platform support                    │
│                                                                 │
│  4. Federated Computational Governance                         │
│     • Global standards, local implementation                   │
│     • Automated compliance                                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              FEDERATED COMPUTATIONAL GOVERNANCE                  │
│  (Standards, Policies, Observability, Discovery)                │
└────────────────────┬────────────────────────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
┌──────▼──────┐ ┌───▼──────┐ ┌───▼──────┐
│   DOMAIN A  │ │ DOMAIN B │ │ DOMAIN C │
│   (Sales)   │ │(Customer)│ │(Product) │
├─────────────┤ ├──────────┤ ├──────────┤
│ Data Product│ │Data Prod │ │Data Prod │
│ • Orders    │ │• Profiles│ │• Catalog │
│ • Quotes    │ │• Events  │ │• Inventory│
│             │ │          │ │          │
│ Team Owns:  │ │Team Owns:│ │Team Owns:│
│ • Pipeline  │ │• Quality │ │• Schema  │
│ • Quality   │ │• SLAs    │ │• APIs    │
│ • SLAs      │ │• Docs    │ │• Docs    │
└─────────────┘ └──────────┘ └──────────┘
       │             │             │
       └─────────────┼─────────────┘
                     │
          ┌──────────▼──────────┐
          │  SELF-SERVE DATA    │
          │     PLATFORM        │
          │                     │
          │ • Compute (Spark)   │
          │ • Storage (Delta)   │
          │ • Catalog           │
          │ • Monitoring        │
          │ • CI/CD             │
          └─────────────────────┘
```

### Implementation in Microsoft Fabric

```python
# Data Mesh Implementation with Fabric

class DataProduct:
    """
    Base class for domain data products
    """
    
    def __init__(self, domain, product_name, workspace):
        self.domain = domain
        self.product_name = product_name
        self.workspace = workspace
        self.metadata = self._register_metadata()
    
    def _register_metadata(self):
        """
        Register data product in catalog
        """
        return {
            "domain": self.domain,
            "name": self.product_name,
            "owner": self.get_owner(),
            "sla": self.get_sla(),
            "schema": self.get_schema(),
            "documentation_url": self.get_docs_url(),
            "data_quality_metrics": self.get_quality_metrics()
        }
    
    def get_owner(self):
        """Return team/person responsible"""
        raise NotImplementedError
    
    def get_sla(self):
        """
        Define SLA for data product
        """
        return {
            "freshness": "< 1 hour",
            "completeness": "> 99%",
            "accuracy": "> 99.9%",
            "availability": "99.9%"
        }
    
    def get_schema(self):
        """Return schema definition"""
        raise NotImplementedError
    
    def publish(self, data_df):
        """
        Publish data with quality checks
        """
        # 1. Validate schema
        if not self._validate_schema(data_df):
            raise ValueError("Schema validation failed")
        
        # 2. Quality checks
        quality_score = self._run_quality_checks(data_df)
        if quality_score < 0.99:
            raise ValueError(f"Quality check failed: {quality_score}")
        
        # 3. Write data
        self._write_data(data_df)
        
        # 4. Update metadata
        self._update_metadata(data_df)
        
        # 5. Notify consumers
        self._notify_consumers()
    
    def _validate_schema(self, df):
        """Validate data against schema"""
        expected_schema = self.get_schema()
        return df.schema == expected_schema
    
    def _run_quality_checks(self, df):
        """
        Run data quality checks
        """
        total_rows = df.count()
        
        # Completeness check
        complete_rows = df.dropna().count()
        completeness = complete_rows / total_rows
        
        # Uniqueness check (if applicable)
        # Validity checks
        # etc.
        
        return completeness
    
    def _write_data(self, df):
        """Write to data product location"""
        path = f"/domains/{self.domain}/{self.product_name}"
        df.write.format("delta").mode("overwrite").save(path)
    
    def _notify_consumers(self):
        """Notify downstream consumers of update"""
        # Publish to event stream, update catalog, etc.
        pass


class CustomerProfileProduct(DataProduct):
    """
    Customer domain data product
    """
    
    def __init__(self):
        super().__init__(
            domain="customer",
            product_name="customer_profiles",
            workspace="customer_workspace"
        )
    
    def get_owner(self):
        return {
            "team": "Customer Analytics Team",
            "email": "customer-analytics@company.com",
            "slack": "#customer-analytics"
        }
    
    def get_schema(self):
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType
        
        return StructType([
            StructField("customer_id", StringType(), False),
            StructField("email", StringType(), False),
            StructField("segment", StringType(), True),
            StructField("lifetime_value", IntegerType(), True),
            StructField("created_date", StringType(), False)
        ])
    
    def get_docs_url(self):
        return "https://wiki.company.com/data-products/customer-profiles"
    
    def get_quality_metrics(self):
        return {
            "last_updated": "2024-01-15T10:00:00Z",
            "row_count": 1000000,
            "completeness": 0.995,
            "accuracy": 0.998
        }


# Usage
customer_product = CustomerProfileProduct()

# Transform and publish data
customer_df = transform_customer_data(source_df)
customer_product.publish(customer_df)
```

### Governance Framework

```python
# Federated Governance Implementation
class DataMeshGovernance:
    """
    Centralized governance policies with federated execution
    """
    
    def __init__(self):
        self.policies = self._load_policies()
        self.standards = self._load_standards()
    
    def _load_policies(self):
        """
        Global policies all domains must follow
        """
        return {
            "data_classification": {
                "public": {"encryption": False, "masking": False},
                "internal": {"encryption": True, "masking": False},
                "confidential": {"encryption": True, "masking": True},
                "restricted": {"encryption": True, "masking": True, "approval_required": True}
            },
            "retention": {
                "raw_data": "7 years",
                "pii_data": "As per GDPR",
                "analytics_data": "2 years"
            },
            "quality_thresholds": {
                "completeness": 0.95,
                "accuracy": 0.99,
                "timeliness": 3600  # seconds
            }
        }
    
    def validate_data_product(self, data_product, data_df):
        """
        Automated policy validation
        """
        validation_results = {
            "schema_compliance": self._check_schema_standards(data_product),
            "quality_thresholds": self._check_quality(data_df),
            "security_compliance": self._check_security(data_product),
            "documentation": self._check_documentation(data_product)
        }
        
        return all(validation_results.values())
    
    def _check_schema_standards(self, data_product):
        """
        Ensure schema follows naming conventions, types, etc.
        """
        schema = data_product.get_schema()
        
        # Check naming conventions
        for field in schema.fields:
            if not field.name.islower():
                return False
            if not re.match(r'^[a-z][a-z0-9_]*$', field.name):
                return False
        
        return True
    
    def _check_quality(self, df):
        """
        Validate against quality thresholds
        """
        total_rows = df.count()
        complete_rows = df.dropna().count()
        completeness = complete_rows / total_rows
        
        return completeness >= self.policies["quality_thresholds"]["completeness"]
```

### When to Use Data Mesh

**Best for**:
- Large organizations with multiple domains
- Need for domain autonomy
- Scaling data teams independently
- Complex data landscape

**Challenges**:
- Requires organizational change
- Platform engineering investment
- Cultural transformation needed
- Governance complexity

---

## Lakehouse Architecture

### Overview
Lakehouse combines the best of data lakes and data warehouses, providing ACID transactions, schema enforcement, and BI performance on data lake storage.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   BUSINESS INTELLIGENCE                       │
│          (Power BI, Tableau, Analytics Tools)                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    SQL Interface
                         │
┌────────────────────────┴─────────────────────────────────────┐
│                    LAKEHOUSE LAYER                            │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        Delta Lake / Iceberg (ACID Transactions)      │    │
│  │  • Schema enforcement • Time travel • ACID           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Compute Engines (Spark, SQL, ML)            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Metadata Layer (Unity Catalog)          │    │
│  │  • Data discovery • Lineage • Access control         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────┴─────────────────────────────────────┐
│                   STORAGE LAYER                               │
│            (ADLS Gen2, S3, Azure Blob)                       │
│                Low-cost object storage                        │
└──────────────────────────────────────────────────────────────┘
```

### Key Features

1. **ACID Transactions**: Delta Lake provides ACID guarantees
2. **Schema Enforcement**: Prevent bad data from entering
3. **Time Travel**: Query historical versions
4. **Unified Batch and Streaming**: Single pipeline for both
5. **BI Performance**: Optimizations rival data warehouses
6. **Open Standards**: Parquet, Delta, Iceberg

### Implementation

```python
# Lakehouse Implementation with Delta Lake
class Lakehouse:
    """
    Lakehouse implementation with Delta Lake
    """
    
    def __init__(self, base_path, catalog_name="main"):
        self.base_path = base_path
        self.catalog_name = catalog_name
        self._setup_catalog()
    
    def _setup_catalog(self):
        """
        Set up Unity Catalog or Hive Metastore
        """
        spark.sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog_name}")
        spark.sql(f"USE CATALOG {self.catalog_name}")
    
    def create_table(self, schema_name, table_name, df, partition_by=None):
        """
        Create Delta table with best practices
        """
        table_path = f"{self.base_path}/{schema_name}/{table_name}"
        
        writer = df.write.format("delta")
        
        if partition_by:
            writer = writer.partitionBy(*partition_by)
        
        # Enable optimizations
        writer = (writer
            .option("delta.autoOptimize.optimizeWrite", "true")
            .option("delta.autoOptimize.autoCompact", "true"))
        
        writer.mode("overwrite").save(table_path)
        
        # Register in catalog
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.catalog_name}.{schema_name}.{table_name}
            USING DELTA
            LOCATION '{table_path}'
        """)
    
    def upsert_data(self, schema_name, table_name, updates_df, merge_key):
        """
        UPSERT operation with Delta Lake MERGE
        """
        table_full_name = f"{self.catalog_name}.{schema_name}.{table_name}"
        
        # Create temporary view
        updates_df.createOrReplaceTempView("updates")
        
        # Perform MERGE
        spark.sql(f"""
            MERGE INTO {table_full_name} target
            USING updates source
            ON target.{merge_key} = source.{merge_key}
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """)
    
    def time_travel_query(self, schema_name, table_name, version=None, timestamp=None):
        """
        Query historical version of data
        """
        table_full_name = f"{self.catalog_name}.{schema_name}.{table_name}"
        
        if version is not None:
            return spark.read.format("delta").option("versionAsOf", version).table(table_full_name)
        elif timestamp is not None:
            return spark.read.format("delta").option("timestampAsOf", timestamp).table(table_full_name)
        else:
            return spark.table(table_full_name)
    
    def optimize_table(self, schema_name, table_name, zorder_columns=None):
        """
        Optimize Delta table for query performance
        """
        table_full_name = f"{self.catalog_name}.{schema_name}.{table_name}"
        
        # Compact small files
        optimize_sql = f"OPTIMIZE {table_full_name}"
        
        if zorder_columns:
            optimize_sql += f" ZORDER BY ({', '.join(zorder_columns)})"
        
        spark.sql(optimize_sql)
        
        # Remove old versions (keep 30 days)
        spark.sql(f"VACUUM {table_full_name} RETAIN 720 HOURS")
    
    def enable_cdf(self, schema_name, table_name):
        """
        Enable Change Data Feed for CDC
        """
        table_full_name = f"{self.catalog_name}.{schema_name}.{table_name}"
        
        spark.sql(f"""
            ALTER TABLE {table_full_name}
            SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
        """)
    
    def read_cdf(self, schema_name, table_name, start_version, end_version=None):
        """
        Read change data feed
        """
        table_full_name = f"{self.catalog_name}.{schema_name}.{table_name}"
        
        reader = (spark.read
            .format("delta")
            .option("readChangeDataFeed", "true")
            .option("startingVersion", start_version))
        
        if end_version:
            reader = reader.option("endingVersion", end_version)
        
        return reader.table(table_full_name)


# Usage Example
lakehouse = Lakehouse(base_path="/mnt/lakehouse")

# Create table
sales_df = spark.read.parquet("/data/sales")
lakehouse.create_table("sales", "orders", sales_df, partition_by=["order_date"])

# Upsert new/updated records
updates_df = spark.read.parquet("/data/sales_updates")
lakehouse.upsert_data("sales", "orders", updates_df, merge_key="order_id")

# Time travel
yesterday_data = lakehouse.time_travel_query(
    "sales", "orders", 
    timestamp="2024-01-14"
)

# Optimize
lakehouse.optimize_table("sales", "orders", zorder_columns=["customer_id", "product_id"])

# Enable and read CDC
lakehouse.enable_cdf("sales", "orders")
changes = lakehouse.read_cdf("sales", "orders", start_version=5, end_version=10)
```

### Benefits

1. **Cost-effective**: Store data on cheap object storage
2. **Performance**: Optimizations rival traditional warehouses
3. **Flexibility**: Support diverse workloads (BI, ML, streaming)
4. **Simplicity**: Single platform instead of multiple systems
5. **Open**: Based on open standards (Parquet, Delta)

---

## Microservices for Data

### Overview
Apply microservices principles to data pipelines and processing.

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      API GATEWAY                            │
│               (Authentication, Rate Limiting)               │
└──────────────────────┬─────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │Ingestion│   │Transform│   │ Serving │
   │ Service │   │ Service │   │ Service │
   │         │   │         │   │         │
   │ • REST  │   │ • Spark │   │ • SQL   │
   │ • Kafka │   │ • Python│   │ • API   │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │              │
        │     ┌───────┴──────┐       │
        │     │              │       │
   ┌────▼─────▼───┐    ┌────▼───────▼────┐
   │   Message     │    │   Data Store    │
   │   Queue       │    │   (Delta Lake)  │
   └───────────────┘    └─────────────────┘
```

### Implementation Principles

```python
# Microservice for Data Ingestion
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

class IngestionMicroservice:
    """
    Microservice for data ingestion
    """
    
    def __init__(self, kafka_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    @app.route('/ingest/events', methods=['POST'])
    def ingest_events(self):
        """
        REST endpoint to ingest events
        """
        try:
            # Validate request
            data = request.get_json()
            if not self._validate(data):
                return jsonify({"error": "Invalid data"}), 400
            
            # Enrich data
            enriched_data = self._enrich(data)
            
            # Send to Kafka
            self.producer.send('events', enriched_data)
            
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def _validate(self, data):
        """Validate incoming data"""
        required_fields = ['event_type', 'user_id', 'timestamp']
        return all(field in data for field in required_fields)
    
    def _enrich(self, data):
        """Add metadata"""
        data['ingestion_timestamp'] = datetime.now().isoformat()
        data['service_version'] = '1.0.0'
        return data


# Microservice for Data Transformation
class TransformationMicroservice:
    """
    Microservice for data transformation
    """
    
    def __init__(self, spark):
        self.spark = spark
    
    def process_batch(self, batch_id, input_path, output_path):
        """
        Transform data batch
        """
        # Read data
        df = self.spark.read.parquet(input_path)
        
        # Apply transformations
        transformed_df = self._transform(df)
        
        # Write output
        transformed_df.write.mode("overwrite").parquet(output_path)
        
        return {
            "batch_id": batch_id,
            "records_processed": df.count(),
            "status": "success"
        }
    
    def _transform(self, df):
        """Business logic transformations"""
        return (df
            .filter(col("event_type").isNotNull())
            .withColumn("processed_date", current_date())
            .dropDuplicates(["event_id"]))


# Microservice for Data Serving
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    user_id: str
    start_date: str
    end_date: str

class ServingMicroservice:
    """
    Microservice for data serving
    """
    
    def __init__(self, spark):
        self.spark = spark
    
    @app.post("/query/user_activity")
    async def query_user_activity(self, query: QueryRequest):
        """
        Query user activity data
        """
        try:
            df = (self.spark.read
                .format("delta")
                .load("/data/user_activity")
                .filter(
                    (col("user_id") == query.user_id) &
                    (col("date") >= query.start_date) &
                    (col("date") <= query.end_date)
                )
                .select("event_type", "timestamp", "properties"))
            
            # Convert to JSON
            results = df.limit(1000).toPandas().to_dict('records')
            
            return {"data": results, "count": len(results)}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

### Benefits of Microservices

1. **Independent scaling**: Scale services independently
2. **Technology diversity**: Use best tool for each job
3. **Fault isolation**: Failures don't cascade
4. **Team autonomy**: Teams own their services
5. **Faster deployment**: Deploy services independently

---

## Real-World Examples

### Example 1: E-Commerce Platform (Lakehouse + Medallion)

```
Architecture:
- Bronze: Raw clickstream, orders, inventory
- Silver: Cleaned user sessions, order facts
- Gold: Daily sales dashboard, customer 360

Technology Stack:
- Storage: Azure Data Lake Gen2
- Processing: Databricks/Fabric
- Format: Delta Lake
- BI: Power BI

Implementation:
- 100M+ events per day
- Real-time and batch processing
- 500+ concurrent users on dashboards
```

### Example 2: IoT Manufacturing (Lambda Architecture)

```
Architecture:
- Batch Layer: Historical sensor data analysis
- Speed Layer: Real-time anomaly detection
- Serving Layer: Combined analytics dashboard

Technology Stack:
- Ingestion: Azure IoT Hub
- Stream: Azure Stream Analytics / Spark Streaming
- Batch: Azure Synapse
- Storage: ADLS Gen2

Scale:
- 10,000 sensors
- 1M events per minute
- < 1 second detection latency
```

### Example 3: Financial Services (Data Mesh)

```
Domains:
- Trading Domain: Trade execution data
- Risk Domain: Risk calculations
- Compliance Domain: Regulatory reporting
- Customer Domain: Customer analytics

Each domain:
- Owns its data products
- Has dedicated team
- Uses shared platform (Fabric)
- Follows global governance

Benefits:
- Domain autonomy
- Faster time to market
- Clear ownership
- Scalable organization
```

---

## Choosing the Right Architecture

| Pattern | Best For | Avoid When |
|---------|----------|------------|
| **Medallion** | Data quality focus, incremental refinement | Simple pipelines |
| **Lambda** | Both real-time and batch, high accuracy | Streaming-only, small team |
| **Kappa** | Stream-first, frequent reprocessing | Complex batch algorithms |
| **Data Mesh** | Large orgs, multiple domains | Small team, simple data |
| **Lakehouse** | Unified analytics, cost-effective | Simple warehousing only |
| **Microservices** | Independent scaling, poly-technology | Monolithic OK, small scale |

---

## Summary

- **Medallion**: Progressive data refinement (Bronze → Silver → Gold)
- **Lambda**: Batch + Stream processing for accuracy + speed
- **Kappa**: Stream-only simplification of Lambda
- **Data Mesh**: Decentralized, domain-oriented data ownership
- **Lakehouse**: Best of data lake + data warehouse
- **Microservices**: Independent, scalable data services

**Hybrid Approach**: Most organizations combine multiple patterns (e.g., Lakehouse + Medallion + Data Mesh principles).
