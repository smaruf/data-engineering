# Java Spark Examples

Comprehensive Java examples for Apache Spark covering fundamentals, transformations, SQL operations, and performance optimization.

## Contents

### 01-spark-basics/
Foundation of Spark programming with Java.

#### SparkSessionExample.java
- Creating SparkSession with various configurations
- Basic and advanced session setup
- Configuration management
- Working with Spark Context

**Key Concepts:**
```java
SparkSession spark = SparkSession.builder()
    .appName("My Application")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate();
```

#### RDDOperations.java
- RDD transformations: map, flatMap, filter, distinct
- RDD actions: collect, count, reduce, fold
- Pair RDD operations: reduceByKey, groupByKey
- Advanced operations: sample, cartesian, join

**Key Operations:**
- Transformations (lazy): `map()`, `filter()`, `flatMap()`
- Actions (eager): `collect()`, `count()`, `reduce()`
- Pair RDD: `reduceByKey()`, `groupByKey()`, `join()`

#### DataFrameOperations.java
- Creating DataFrames from multiple sources
- DataFrame transformations: select, filter, withColumn
- DataFrame actions: show, count, describe
- Working with schemas and complex types

**Common Patterns:**
```java
df.select("name", "age")
  .filter(col("age").gt(25))
  .orderBy(col("name").asc())
  .show();
```

#### DatasetOperations.java
- Strongly-typed Datasets with encoders
- Type-safe transformations
- Dataset vs DataFrame comparison
- Custom encoders for complex types

**Type Safety:**
```java
Dataset<Employee> ds = spark.createDataset(employees, Encoders.bean(Employee.class));
Dataset<String> names = ds.map(emp -> emp.getName(), Encoders.STRING());
```

### 02-transformations/
Advanced data transformation techniques.

#### MapReduceExample.java
- Classic MapReduce patterns
- Word count implementation
- Map and reduce operations
- FlatMap for one-to-many transformations

**Word Count:**
```java
words.mapToPair(word -> new Tuple2<>(word, 1))
     .reduceByKey((a, b) -> a + b);
```

#### FilterTransform.java
- Basic and complex filtering
- WHERE conditions
- String pattern matching
- NULL handling

**Filter Examples:**
```java
df.filter(col("salary").gt(70000).and(col("department").equalTo("Engineering")))
df.where("age BETWEEN 25 AND 35")
df.filter(col("name").startsWith("J"))
```

#### JoinOperations.java
- Inner, outer, left, right joins
- Cross joins and semi joins
- Self joins
- Multiple join strategies

**Join Types:**
```java
df1.join(df2, joinCondition, "inner")      // Inner join
df1.join(df2, joinCondition, "left")       // Left outer
df1.join(df2, joinCondition, "right")      // Right outer
df1.join(df2, joinCondition, "outer")      // Full outer
```

#### AggregationExample.java
- GroupBy aggregations
- Pivot and unpivot operations
- Rollup and cube
- Window aggregations

**Aggregations:**
```java
df.groupBy("department")
  .agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary"),
    max("salary").alias("max_salary")
  );
```

### 03-spark-sql/
SQL operations and functions.

#### SQLOperations.java
- SQL queries on DataFrames
- Temporary and global views
- Catalog operations
- Complex SQL patterns

**SQL Queries:**
```java
df.createOrReplaceTempView("employees");
spark.sql("SELECT department, AVG(salary) FROM employees GROUP BY department");
```

#### WindowFunctions.java
- Ranking functions: rank, dense_rank, row_number
- Aggregate window functions
- Analytical functions: lag, lead
- Custom window specifications

**Window Operations:**
```java
WindowSpec window = Window.partitionBy("department").orderBy(col("salary").desc());
df.withColumn("rank", rank().over(window));
```

#### UDFExample.java
- User-defined functions (UDFs)
- Single and multiple parameter UDFs
- Complex business logic
- UDF registration and usage

**UDF Definition:**
```java
spark.udf().register("toUpper", (UDF1<String, String>) String::toUpperCase, DataTypes.StringType);
df.withColumn("upper_name", callUDF("toUpper", col("name")));
```

### 04-performance/
Performance optimization techniques.

#### PartitioningStrategies.java
- Repartition vs coalesce
- PartitionBy for specific columns
- Optimal partition sizing
- Custom partitioning strategies

**Partitioning:**
```java
df.repartition(10)                    // With shuffle
df.coalesce(5)                        // Without shuffle
df.repartition(col("department"))     // By column
```

#### CachingExample.java
- Cache and persist operations
- Storage levels
- Memory management
- Unpersist strategies

**Caching:**
```java
df.cache()                                          // MEMORY_ONLY
df.persist(StorageLevel.MEMORY_AND_DISK())         // MEMORY_AND_DISK
df.unpersist()                                      // Remove from cache
```

#### BroadcastJoin.java
- Broadcast variables
- Broadcast joins for small tables
- Auto-broadcast configuration
- SQL broadcast hints

**Broadcast:**
```java
import static org.apache.spark.sql.functions.*;
largeDF.join(broadcast(smallDF), joinCondition);
```

#### SparkTuning.java
- Memory tuning
- Shuffle optimization
- Parallelism configuration
- Best practices and patterns

**Configuration:**
```java
spark.conf().set("spark.sql.shuffle.partitions", "200");
spark.conf().set("spark.sql.adaptive.enabled", "true");
spark.conf().set("spark.serializer", "org.apache.spark.serializer.KryoSerializer");
```

## Running Examples

### Compile and Run
```bash
# Compile
javac -cp "spark-jars/*" com/microsoft/spark/basics/SparkSessionExample.java

# Run
java -cp ".:spark-jars/*" com.microsoft.spark.basics.SparkSessionExample
```

### Using Maven
```bash
mvn clean compile
mvn exec:java -Dexec.mainClass="com.microsoft.spark.basics.SparkSessionExample"
```

### Using spark-submit
```bash
spark-submit \
  --class com.microsoft.spark.basics.SparkSessionExample \
  --master local[4] \
  --conf spark.executor.memory=2g \
  target/spark-examples.jar
```

## Learning Path

1. **Start with Basics** (01-spark-basics)
   - Understand SparkSession
   - Learn RDD operations
   - Master DataFrame API
   - Explore Dataset capabilities

2. **Learn Transformations** (02-transformations)
   - Practice MapReduce patterns
   - Master filtering techniques
   - Understand join strategies
   - Learn aggregation patterns

3. **Master SQL** (03-spark-sql)
   - Write SQL queries
   - Use window functions
   - Create UDFs
   - Optimize queries

4. **Optimize Performance** (04-performance)
   - Implement partitioning
   - Use caching effectively
   - Leverage broadcast joins
   - Tune configurations

## Best Practices

### 1. Use DataFrame/Dataset over RDD
DataFrames and Datasets provide Catalyst optimizer benefits and are easier to use.

### 2. Avoid Collect on Large Datasets
```java
// Bad
List<Row> allData = hugeDF.collect();  // OOM risk

// Good
hugeDF.write().parquet("output");      // Write to storage
```

### 3. Cache Wisely
```java
// Cache after expensive operations, before multiple uses
Dataset<Row> expensive = df.filter(...).join(...).cache();
expensive.count();  // Materialize cache
```

### 4. Use Appropriate Join Strategy
```java
// Small table - use broadcast
largeDF.join(broadcast(smallDF), condition);

// Large tables - ensure proper partitioning
df1.repartition(col("key")).join(df2.repartition(col("key")), "key");
```

### 5. Optimize Shuffle Operations
```java
// Reduce data before shuffle
df.filter(condition).groupBy("key").agg(...)
```

## Common Pitfalls

### 1. Too Many Small Partitions
- Increases task overhead
- **Solution**: Use coalesce or adjust `spark.sql.shuffle.partitions`

### 2. Skewed Data
- Some partitions much larger than others
- **Solution**: Use salting or custom partitioning

### 3. UDF Performance
- UDFs disable Catalyst optimizations
- **Solution**: Use built-in functions when possible

### 4. Memory Issues
- Caching too much data
- **Solution**: Selective caching, increase memory, or use disk

## Quick Reference

### Common Functions
```java
// Column operations
col("name"), lit(5), expr("age + 1")

// Aggregations
count(), sum(), avg(), min(), max()

// String functions
upper(), lower(), concat(), substring()

// Date functions
current_date(), date_add(), year(), month()

// Conditional
when(condition, value).otherwise(default)
```

### Configuration Properties
```properties
# Memory
spark.executor.memory=4g
spark.driver.memory=2g
spark.memory.fraction=0.6

# Shuffle
spark.sql.shuffle.partitions=200
spark.default.parallelism=100

# Optimization
spark.sql.adaptive.enabled=true
spark.sql.autoBroadcastJoinThreshold=10485760

# Serialization
spark.serializer=org.apache.spark.serializer.KryoSerializer
```

## Additional Resources

- [Spark Java API Docs](https://spark.apache.org/docs/latest/api/java/)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Performance Tuning Guide](https://spark.apache.org/docs/latest/tuning.html)

## Next Steps

After completing these examples, explore:
- Structured Streaming for real-time processing
- MLlib for machine learning
- Integration with cloud platforms (Azure, AWS, GCP)
- Advanced optimizations with Adaptive Query Execution
