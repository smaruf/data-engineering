# Troubleshooting Guide for Data Engineering

## Table of Contents
1. [Azure Authentication Errors](#azure-authentication-errors)
2. [Spark Out of Memory Errors](#spark-out-of-memory-errors)
3. [Delta Lake Conflicts](#delta-lake-conflicts)
4. [Performance Bottlenecks](#performance-bottlenecks)
5. [Debugging Techniques](#debugging-techniques)

---

## Azure Authentication Errors

### Problem: Authentication Failed / Unauthorized

**Common Error Messages:**
```
AuthorizationFailed: The client does not have authorization to perform action
InvalidAuthenticationTokenTenant: The access token is from the wrong issuer
AADSTS700016: Application not found in the directory
```

#### Solution 1: Service Principal Issues

```python
# Check service principal configuration
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError

def validate_service_principal(tenant_id, client_id, client_secret):
    """
    Validate service principal credentials
    """
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Test authentication
        token = credential.get_token("https://management.azure.com/.default")
        print("✅ Service principal authentication successful")
        print(f"Token expires: {token.expires_on}")
        return True
        
    except ClientAuthenticationError as e:
        print("❌ Authentication failed:")
        print(f"  Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify tenant ID is correct")
        print("2. Check if client ID exists in Azure AD")
        print("3. Confirm client secret is not expired")
        print("4. Ensure service principal has required permissions")
        return False

# Usage
validate_service_principal(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

**Troubleshooting Steps:**

1. **Verify Service Principal Exists:**
```bash
# Azure CLI
az ad sp show --id <client-id>

# Should return service principal details
```

2. **Check Secret Expiration:**
```bash
# List credentials
az ad sp credential list --id <client-id>

# Look for expiration dates
```

3. **Reset Secret if Expired:**
```bash
# Create new secret
az ad sp credential reset --id <client-id>

# Update your application with new secret
```

4. **Verify RBAC Assignments:**
```bash
# Check role assignments
az role assignment list --assignee <client-id>

# Should show required roles (e.g., Contributor, Storage Blob Data Contributor)
```

#### Solution 2: Managed Identity Issues

```python
# Using Managed Identity in Azure
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

def test_managed_identity(storage_account_name):
    """
    Test managed identity authentication
    """
    try:
        # Try DefaultAzureCredential (recommended)
        credential = DefaultAzureCredential()
        
        blob_service = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=credential
        )
        
        # Test by listing containers
        containers = list(blob_service.list_containers())
        print(f"✅ Managed identity working. Found {len(containers)} containers")
        
    except Exception as e:
        print(f"❌ Managed identity failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure managed identity is enabled on the resource")
        print("2. Verify role assignments (e.g., Storage Blob Data Reader)")
        print("3. Check if system-assigned or user-assigned identity")
        print("4. For VMs: Ensure IMDS endpoint is accessible")

# Usage
test_managed_identity("mystorageaccount")
```

**Enable Managed Identity:**

```bash
# For Azure VM
az vm identity assign --name <vm-name> --resource-group <rg-name>

# For Azure Databricks (use Azure Portal)
# Navigate to Databricks workspace > Access control (IAM) > Add role assignment

# Assign role to managed identity
az role assignment create \
    --assignee-object-id <identity-object-id> \
    --role "Storage Blob Data Contributor" \
    --scope "/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>"
```

#### Solution 3: Token Expiration Issues

```python
# Handle token refresh automatically
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
import time

class TokenRefreshWrapper:
    """
    Wrapper to handle automatic token refresh
    """
    def __init__(self, credential):
        self.credential = credential
        self.token = None
        self.token_expiry = 0
    
    def get_token(self, scopes):
        """
        Get token with automatic refresh
        """
        current_time = time.time()
        
        # Refresh if token expired or about to expire (5 min buffer)
        if not self.token or current_time >= (self.token_expiry - 300):
            self.token = self.credential.get_token(scopes)
            self.token_expiry = self.token.expires_on
            print(f"🔄 Token refreshed. Expires: {self.token_expiry}")
        
        return self.token

# Usage
credential = ClientSecretCredential(tenant_id, client_id, client_secret)
token_wrapper = TokenRefreshWrapper(credential)

# Use in long-running processes
blob_service = BlobServiceClient(
    account_url=f"https://{storage_account}.blob.core.windows.net",
    credential=credential  # Credential handles refresh automatically
)
```

---

## Spark Out of Memory Errors

### Problem: Executor Out of Memory

**Error Messages:**
```
java.lang.OutOfMemoryError: Java heap space
Container killed by YARN for exceeding memory limits
ExecutorLostFailure (executor lost)
```

#### Solution 1: Increase Executor Memory

```python
# Calculate memory requirements
def calculate_required_memory(data_size_gb, compression_ratio=3):
    """
    Estimate required executor memory
    
    Rule of thumb: 3x compressed data size for processing
    """
    uncompressed_size_gb = data_size_gb * compression_ratio
    memory_per_executor_gb = uncompressed_size_gb / 10  # Assuming 10 executors
    
    # Add 30% overhead for Spark operations
    recommended_memory = memory_per_executor_gb * 1.3
    
    print(f"Data size (compressed): {data_size_gb} GB")
    print(f"Estimated uncompressed: {uncompressed_size_gb} GB")
    print(f"Recommended executor memory: {recommended_memory:.1f} GB")
    
    return recommended_memory

# Apply configuration
required_memory = calculate_required_memory(data_size_gb=100)

spark.conf.set("spark.executor.memory", f"{int(required_memory)}g")
spark.conf.set("spark.executor.memoryOverhead", f"{int(required_memory * 0.2)}g")
spark.conf.set("spark.driver.memory", f"{int(required_memory)}g")
```

#### Solution 2: Optimize Data Processing to Reduce Memory

```python
# Problem: Loading entire dataset into memory
# ❌ BAD
df = spark.read.parquet("large_dataset.parquet")
df.cache()  # OOM!
result = df.groupBy("category").agg(sum("amount"))

# ✅ GOOD: Process incrementally
def process_in_batches(input_path, output_path, batch_column, batch_values):
    """
    Process large dataset in batches
    """
    for batch_value in batch_values:
        print(f"Processing batch: {batch_value}")
        
        # Process one batch at a time
        batch_df = (spark.read.parquet(input_path)
            .filter(col(batch_column) == batch_value)
            .groupBy("category").agg(sum("amount")))
        
        # Write incrementally
        (batch_df.write
         .mode("append")
         .parquet(f"{output_path}/batch={batch_value}"))
        
        print(f"✅ Batch {batch_value} complete")

# Usage
process_in_batches(
    input_path="large_dataset.parquet",
    output_path="aggregated_output",
    batch_column="date",
    batch_values=["2024-01-01", "2024-01-02", "2024-01-03"]
)
```

#### Solution 3: Spill to Disk Optimization

```python
# Configure spill behavior
spark.conf.set("spark.memory.fraction", "0.8")  # More memory for execution
spark.conf.set("spark.memory.storageFraction", "0.3")  # Less for caching
spark.conf.set("spark.shuffle.spill.compress", "true")  # Compress spilled data
spark.conf.set("spark.shuffle.compress", "true")

# Monitor spill metrics
def check_spill_metrics(spark):
    """
    Check if operations are spilling to disk
    """
    # Get recent query metrics
    last_query = spark.sparkContext.statusTracker().getJobInfo(
        spark.sparkContext.statusTracker().getJobIdsForGroup()[-1]
    )
    
    # Check for spill indicators in logs
    print("Check Spark UI for:")
    print("- Shuffle Spill (Memory)")
    print("- Shuffle Spill (Disk)")
    print("If high, consider:")
    print("1. Increase executor memory")
    print("2. Reduce partition size")
    print("3. Optimize transformations")
```

#### Solution 4: Partition Skew Causing OOM

```python
# Detect and fix partition skew
def analyze_partition_distribution(df, partition_col):
    """
    Analyze partition size distribution
    """
    partition_stats = (df
        .groupBy(partition_col)
        .agg(
            count("*").alias("row_count"),
            approx_count_distinct("*").alias("approx_size")
        )
        .orderBy(col("row_count").desc()))
    
    stats = partition_stats.select(
        max("row_count").alias("max_rows"),
        avg("row_count").alias("avg_rows"),
        min("row_count").alias("min_rows")
    ).collect()[0]
    
    skew_factor = stats.max_rows / stats.avg_rows
    
    print(f"Partition Skew Analysis:")
    print(f"  Max partition: {stats.max_rows:,} rows")
    print(f"  Avg partition: {stats.avg_rows:,.0f} rows")
    print(f"  Min partition: {stats.min_rows:,} rows")
    print(f"  Skew factor: {skew_factor:.2f}x")
    
    if skew_factor > 3:
        print("⚠️ High skew detected! Consider:")
        print("1. Repartition on different column")
        print("2. Use salting technique")
        print("3. Increase executor memory for skewed partitions")
        partition_stats.show(10)
    
    return skew_factor

# Fix skew with salting
def salt_and_repartition(df, skewed_column, salt_factor=10):
    """
    Add salt to distribute skewed data
    """
    from pyspark.sql.functions import rand, floor, concat
    
    salted_df = df.withColumn(
        "salt",
        floor(rand() * salt_factor).cast("int")
    ).withColumn(
        f"salted_{skewed_column}",
        concat(col(skewed_column), lit("_"), col("salt"))
    )
    
    # Repartition on salted column
    return salted_df.repartition(f"salted_{skewed_column}")
```

### Problem: Driver Out of Memory

**Error Messages:**
```
java.lang.OutOfMemoryError: Java heap space (on driver)
Driver OutOfMemoryError
```

#### Solution: Avoid Collecting Large Results

```python
# ❌ BAD: Collect large dataset to driver
large_result = df.collect()  # OOM on driver!
for row in large_result:
    process(row)

# ✅ GOOD: Process distributedly
df.foreach(lambda row: process(row))  # Executed on executors

# ✅ GOOD: Sample before collecting
sample = df.sample(0.01).collect()  # Only 1% of data

# ✅ GOOD: Aggregate before collecting
summary = df.groupBy("category").agg(sum("amount")).collect()  # Much smaller

# ✅ GOOD: Write to storage instead of collecting
df.write.parquet("output_path")

# Increase driver memory if needed
spark.conf.set("spark.driver.memory", "8g")
spark.conf.set("spark.driver.maxResultSize", "4g")
```

---

## Delta Lake Conflicts

### Problem: Concurrent Modification Exceptions

**Error Messages:**
```
ConcurrentAppendException: Files were added to partition
ConcurrentDeleteException: A file was deleted during the operation
ConcurrentTransactionException: Transaction conflict
```

#### Solution 1: Retry Logic

```python
from delta.tables import DeltaTable
from pyspark.sql.utils import ConcurrentAppendException
import time

def write_with_retry(df, path, max_retries=3, retry_delay=5):
    """
    Write to Delta with automatic retry on conflicts
    """
    for attempt in range(max_retries):
        try:
            df.write.format("delta").mode("append").save(path)
            print(f"✅ Write successful on attempt {attempt + 1}")
            return True
            
        except ConcurrentAppendException as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Conflict detected, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"❌ Failed after {max_retries} attempts")
                raise e
    
    return False

# Usage
write_with_retry(new_data_df, "delta_table_path")
```

#### Solution 2: Optimize Concurrency Settings

```python
# Configure Delta for better concurrency
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# Reduce partition conflicts
spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", "true")

# For high concurrency scenarios
def configure_high_concurrency(table_path):
    """
    Configure table for high concurrency
    """
    spark.sql(f"""
        ALTER TABLE delta.`{table_path}`
        SET TBLPROPERTIES (
            'delta.checkpoint.writeStatsAsStruct' = 'true',
            'delta.checkpoint.writeStatsAsJson' = 'false',
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
    """)
    
    print("✅ High concurrency settings applied")

configure_high_concurrency("my_delta_table")
```

#### Solution 3: Use Merge Instead of Append

```python
# Instead of concurrent appends, use MERGE for upserts
from delta.tables import DeltaTable

def upsert_to_delta(updates_df, table_path, merge_key):
    """
    Upsert using MERGE (handles concurrency better)
    """
    delta_table = DeltaTable.forPath(spark, table_path)
    
    (delta_table.alias("target")
     .merge(
         updates_df.alias("source"),
         f"target.{merge_key} = source.{merge_key}"
     )
     .whenMatchedUpdateAll()
     .whenNotMatchedInsertAll()
     .execute())
    
    print("✅ MERGE completed successfully")

# Usage
upsert_to_delta(new_data_df, "delta_table_path", merge_key="id")
```

### Problem: Delta Lake File Not Found

**Error Messages:**
```
FileNotFoundException: File does not exist
AnalysisException: Path does not exist
```

#### Solution: Check and Repair Delta Table

```python
def diagnose_delta_table(table_path):
    """
    Diagnose Delta table issues
    """
    from delta.tables import DeltaTable
    
    try:
        # Try to read table
        df = spark.read.format("delta").load(table_path)
        print(f"✅ Table readable. Row count: {df.count():,}")
        
        # Check table history
        history = spark.sql(f"DESCRIBE HISTORY delta.`{table_path}`").limit(5)
        print("\nRecent operations:")
        history.show(truncate=False)
        
        # Check for issues
        detail = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`").collect()[0]
        print(f"\nTable details:")
        print(f"  Format: {detail.format}")
        print(f"  Files: {detail.numFiles}")
        print(f"  Size: {detail.sizeInBytes / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"❌ Error reading table: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify path exists")
        print("2. Check _delta_log directory exists")
        print("3. Verify permissions")
        print("4. Try FSCK repair")
        
        # Try repair
        try:
            from delta.tables import DeltaTable
            DeltaTable.forPath(spark, table_path).generate("symlink_format_manifest")
            print("✅ Generated manifest, try reading again")
        except:
            print("❌ Repair failed")

# Usage
diagnose_delta_table("suspicious_table_path")
```

---

## Performance Bottlenecks

### Problem: Slow Query Performance

#### Diagnostic Steps

```python
def diagnose_slow_query(df):
    """
    Comprehensive query diagnostics
    """
    print("="*60)
    print("QUERY DIAGNOSTICS")
    print("="*60)
    
    # 1. Explain plan
    print("\n1. EXECUTION PLAN:")
    df.explain(mode="formatted")
    
    # 2. Check for common issues
    plan_str = df._jdf.queryExecution().toString()
    
    issues = []
    
    if "CartesianProduct" in plan_str:
        issues.append("❌ CRITICAL: Cartesian product detected!")
    
    if "BroadcastExchange" not in plan_str and "Join" in plan_str:
        issues.append("⚠️ WARNING: No broadcast join, might be slow")
    
    shuffle_count = plan_str.count("Exchange")
    if shuffle_count > 2:
        issues.append(f"⚠️ WARNING: {shuffle_count} shuffles detected")
    
    if "FileScan" in plan_str:
        # Check partition pruning
        if "PartitionFilters" in plan_str:
            issues.append("✅ Partition pruning enabled")
        else:
            issues.append("⚠️ No partition pruning, scanning all partitions")
    
    # 3. Report issues
    print("\n2. DETECTED ISSUES:")
    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  ✅ No obvious issues detected")
    
    # 4. Statistics
    try:
        row_count = df.count()
        num_partitions = df.rdd.getNumPartitions()
        
        print(f"\n3. STATISTICS:")
        print(f"  Rows: {row_count:,}")
        print(f"  Partitions: {num_partitions}")
        print(f"  Rows per partition: {row_count/num_partitions:,.0f}")
        
        if num_partitions < 10:
            print("  ⚠️ Low partition count, consider repartitioning")
        elif row_count / num_partitions < 10000:
            print("  ⚠️ Small partitions, consider coalescing")
        
    except Exception as e:
        print(f"  ⚠️ Could not collect statistics: {e}")
    
    # 5. Recommendations
    print("\n4. RECOMMENDATIONS:")
    recommendations = []
    
    if shuffle_count > 2:
        recommendations.append("- Reduce shuffles: use broadcast joins, pre-partition data")
    
    if num_partitions > 1000:
        recommendations.append("- Reduce number of partitions with coalesce()")
    
    if "CartesianProduct" in plan_str:
        recommendations.append("- URGENT: Fix Cartesian product by adding join condition")
    
    if recommendations:
        for rec in recommendations:
            print(f"  {rec}")
    else:
        print("  Query looks optimized!")

# Usage
diagnose_slow_query(my_slow_query)
```

### Problem: Data Skew Causing Slow Tasks

```python
def detect_and_visualize_skew(df, partition_key):
    """
    Detect data skew and visualize distribution
    """
    # Analyze partition distribution
    partition_counts = (df
        .groupBy(partition_key)
        .agg(count("*").alias("count"))
        .orderBy(col("count").desc()))
    
    # Collect statistics
    stats = partition_counts.agg(
        max("count").alias("max"),
        avg("count").alias("avg"),
        min("count").alias("min"),
        stddev("count").alias("stddev")
    ).collect()[0]
    
    skew_ratio = stats["max"] / stats["avg"]
    
    print(f"Skew Analysis for {partition_key}:")
    print(f"  Max count: {stats['max']:,}")
    print(f"  Avg count: {stats['avg']:,.0f}")
    print(f"  Min count: {stats['min']:,}")
    print(f"  Std Dev: {stats['stddev']:,.0f}")
    print(f"  Skew Ratio: {skew_ratio:.2f}x")
    
    if skew_ratio > 3:
        print("\n⚠️ SIGNIFICANT SKEW DETECTED!")
        print("\nTop 10 skewed partitions:")
        partition_counts.show(10)
        
        print("\nFix options:")
        print("1. Salting - Add random prefix to skewed keys")
        print("2. Repartition on different column")
        print("3. Adaptive Query Execution (Spark 3.0+)")
        print("4. Increase executor memory")
        
        # Show salt example
        print("\nExample fix with salting:")
        print(f"""
df_salted = df.withColumn("salt", (rand() * 10).cast("int"))
df_salted = df_salted.withColumn(
    "{partition_key}_salted", 
    concat(col("{partition_key}"), lit("_"), col("salt"))
)
df_repartitioned = df_salted.repartition("{partition_key}_salted")
        """)
    else:
        print("\n✅ Partition distribution looks good!")
    
    return skew_ratio

# Usage
detect_and_visualize_skew(df, "customer_id")
```

---

## Debugging Techniques

### Interactive Debugging with PySpark

```python
# 1. Sample data for quick testing
def quick_test(df, sample_fraction=0.01):
    """
    Test transformations on sample before running on full dataset
    """
    sample_df = df.sample(sample_fraction)
    print(f"Sample size: {sample_df.count():,} rows ({sample_fraction*100}%)")
    return sample_df

# Test transformation
sample = quick_test(large_df, 0.01)
result = sample.filter(...).groupBy(...).agg(...)
result.show()  # Fast feedback

# 2. Add debug columns
from pyspark.sql.functions import current_timestamp, monotonically_increasing_id

df_debug = (df
    .withColumn("_debug_timestamp", current_timestamp())
    .withColumn("_debug_row_id", monotonically_increasing_id()))

# 3. Checkpoint intermediate results
df_intermediate = df.transform(complex_transformation)
df_intermediate.write.mode("overwrite").parquet("debug/checkpoint1")
df_checkpoint = spark.read.parquet("debug/checkpoint1")

# Continue from checkpoint
df_final = df_checkpoint.transform(another_transformation)
```

### Logging and Monitoring

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SparkJobMonitor:
    """
    Monitor Spark job execution with detailed logging
    """
    
    def __init__(self, job_name):
        self.job_name = job_name
        self.start_time = None
        self.checkpoints = {}
    
    def start(self):
        """Start monitoring"""
        self.start_time = datetime.now()
        logger.info(f"Starting job: {self.job_name}")
    
    def checkpoint(self, name, df=None):
        """Record checkpoint"""
        checkpoint_time = datetime.now()
        elapsed = (checkpoint_time - self.start_time).total_seconds()
        
        info = {
            "time": checkpoint_time,
            "elapsed_seconds": elapsed
        }
        
        if df is not None:
            try:
                info["row_count"] = df.count()
                info["partitions"] = df.rdd.getNumPartitions()
            except Exception as e:
                logger.warning(f"Could not collect DataFrame info: {e}")
        
        self.checkpoints[name] = info
        logger.info(f"Checkpoint '{name}': {elapsed:.2f}s elapsed")
        
        if df is not None and "row_count" in info:
            logger.info(f"  Rows: {info['row_count']:,}, Partitions: {info['partitions']}")
    
    def end(self):
        """End monitoring and report"""
        end_time = datetime.now()
        total_elapsed = (end_time - self.start_time).total_seconds()
        
        logger.info(f"Job '{self.job_name}' completed in {total_elapsed:.2f}s")
        
        # Report checkpoint timing
        if self.checkpoints:
            logger.info("Checkpoint timing:")
            prev_time = 0
            for name, info in self.checkpoints.items():
                duration = info["elapsed_seconds"] - prev_time
                logger.info(f"  {name}: {duration:.2f}s")
                prev_time = info["elapsed_seconds"]

# Usage
monitor = SparkJobMonitor("ETL Pipeline")
monitor.start()

df = spark.read.parquet("input")
monitor.checkpoint("Read input", df)

df_transformed = df.transform(my_transformation)
monitor.checkpoint("After transformation", df_transformed)

df_transformed.write.parquet("output")
monitor.checkpoint("Write output")

monitor.end()
```

### Debugging Failed Tasks

```python
def analyze_failed_job(spark, app_id=None):
    """
    Analyze failed Spark jobs
    """
    from pyspark import SparkContext
    sc = SparkContext.getOrCreate()
    
    if app_id is None:
        app_id = sc.applicationId
    
    print(f"Analyzing application: {app_id}")
    print("\nCheck Spark UI for details:")
    print(f"  http://<spark-master>:4040/jobs/")
    print(f"  http://<spark-master>:4040/stages/")
    
    print("\nCommon failure causes:")
    print("1. OutOfMemoryError")
    print("   - Increase executor memory")
    print("   - Reduce partition size")
    print("   - Check for data skew")
    print()
    print("2. Task failures due to data issues")
    print("   - Check for corrupt data")
    print("   - Validate schema")
    print("   - Add error handling")
    print()
    print("3. Shuffle failures")
    print("   - Increase shuffle partitions")
    print("   - Check network connectivity")
    print("   - Increase timeouts")
    print()
    print("4. Serialization errors")
    print("   - Use Kryo serializer")
    print("   - Register custom classes")
    print("   - Avoid non-serializable objects")
    
    print("\nDiagnostic commands:")
    print(f"  # View application logs")
    print(f"  yarn logs -applicationId {app_id}")
    print()
    print(f"  # View executor logs")
    print(f"  Check executor stderr/stdout in YARN or Spark UI")

# Usage when job fails
analyze_failed_job(spark)
```

---

## Common Error Patterns and Solutions

### Quick Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `AuthorizationFailed` | Missing RBAC permissions | Add role assignment (Contributor, Storage Blob Data Contributor) |
| `OutOfMemoryError: Java heap space` | Insufficient executor memory | Increase `spark.executor.memory` and `memoryOverhead` |
| `Container killed by YARN` | Memory overhead too small | Set `spark.executor.memoryOverhead` to 20% of executor memory |
| `ConcurrentAppendException` | Multiple writers to Delta | Use MERGE instead of INSERT, implement retry logic |
| `FileNotFoundException` | Vacuum removed files | Increase retention period, check time travel queries |
| `TaskFailedException` | Data skew or corrupt data | Fix skew with salting, add data validation |
| `AnalysisException: Path does not exist` | Wrong path or permissions | Verify path, check SAS tokens/credentials |
| `Py4JJavaError` | Python-Java communication | Check UDF serialization, avoid complex Python objects |
| `QueryExecutionException` | Invalid query | Check SQL syntax, validate schema |

---

## Best Practices for Prevention

1. **Always use retry logic** for cloud operations
2. **Monitor executor memory usage** proactively
3. **Implement data validation** before processing
4. **Use Delta Lake** for ACID transactions
5. **Enable detailed logging** in production
6. **Set up alerts** for common errors
7. **Test with production-sized data** before deploying
8. **Version control** all configurations
9. **Document known issues** and solutions
10. **Regular maintenance** (OPTIMIZE, VACUUM, statistics updates)

---

**Remember**: Most production issues are caused by resource constraints, data quality problems, or configuration errors. Start with diagnostics, then apply targeted fixes.
