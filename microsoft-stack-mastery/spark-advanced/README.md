# Spark Advanced - Java Examples

This directory contains comprehensive Apache Spark examples in Java, covering core concepts, transformations, SQL operations, and performance optimization techniques.

## Directory Structure

```
spark-advanced/
├── java-spark/                          # Java Spark examples
│   ├── 01-spark-basics/                 # Fundamental Spark concepts
│   ├── 02-transformations/              # Data transformation operations
│   ├── 03-spark-sql/                    # Spark SQL and queries
│   └── 04-performance/                  # Performance optimization
└── README.md
```

## Overview

Apache Spark is a unified analytics engine for large-scale data processing. These examples demonstrate:

- **RDD Operations**: Low-level distributed data operations
- **DataFrame API**: Structured data processing with optimizations
- **Dataset API**: Type-safe data transformations
- **Spark SQL**: SQL queries and table operations
- **Performance Tuning**: Caching, partitioning, and optimization

## Prerequisites

- Java 8 or higher
- Apache Spark 3.x
- Maven or Gradle (for dependency management)

## Maven Dependencies

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.spark</groupId>
        <artifactId>spark-core_2.12</artifactId>
        <version>3.5.0</version>
    </dependency>
    <dependency>
        <groupId>org.apache.spark</groupId>
        <artifactId>spark-sql_2.12</artifactId>
        <version>3.5.0</version>
    </dependency>
</dependencies>
```

## Running Examples

### Local Mode
```bash
# Compile
javac -cp "spark-jars/*" YourExample.java

# Run
java -cp ".:spark-jars/*" com.microsoft.spark.basics.SparkSessionExample
```

### Spark Submit
```bash
spark-submit --class com.microsoft.spark.basics.SparkSessionExample \
  --master local[4] \
  your-application.jar
```

## Key Concepts

### 1. RDD (Resilient Distributed Dataset)
- Immutable distributed collection of objects
- Fault-tolerant through lineage
- Lazy evaluation
- Two types of operations: Transformations and Actions

### 2. DataFrame
- Distributed collection with named columns
- Schema-based optimization
- Catalyst query optimizer
- Similar to relational database table

### 3. Dataset
- Type-safe version of DataFrame
- Combines benefits of RDD and DataFrame
- Compile-time type safety
- Encoder for serialization

### 4. Spark SQL
- SQL queries on distributed data
- Integration with Hive
- Temporary views and catalog operations
- Window functions and aggregations

## Performance Best Practices

### Memory Management
```java
SparkSession spark = SparkSession.builder()
    .config("spark.executor.memory", "4g")
    .config("spark.driver.memory", "2g")
    .config("spark.memory.fraction", "0.6")
    .getOrCreate();
```

### Partitioning
```java
// Repartition for parallel processing
df.repartition(200, col("partition_key"));

// Coalesce to reduce partitions (no shuffle)
df.coalesce(10);
```

### Caching
```java
// Cache frequently accessed data
df.cache();
df.persist(StorageLevel.MEMORY_AND_DISK());

// Unpersist when no longer needed
df.unpersist();
```

### Broadcast Joins
```java
// Broadcast small tables
import static org.apache.spark.sql.functions.*;
largeDF.join(broadcast(smallDF), joinCondition);
```

## Common Patterns

### Word Count
```java
JavaRDD<String> lines = sc.textFile("data.txt");
JavaPairRDD<String, Integer> counts = lines
    .flatMap(line -> Arrays.asList(line.split(" ")).iterator())
    .mapToPair(word -> new Tuple2<>(word, 1))
    .reduceByKey((a, b) -> a + b);
```

### Data Aggregation
```java
df.groupBy("category")
    .agg(
        count("*").alias("count"),
        avg("price").alias("avg_price"),
        sum("quantity").alias("total_quantity")
    );
```

### Window Functions
```java
WindowSpec window = Window
    .partitionBy("department")
    .orderBy(col("salary").desc());
    
df.withColumn("rank", rank().over(window));
```

## Configuration Tips

### Development (Local)
```java
SparkSession spark = SparkSession.builder()
    .appName("Development")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate();
```

### Production (Cluster)
```java
SparkSession spark = SparkSession.builder()
    .appName("Production")
    .master("yarn")
    .config("spark.executor.instances", "10")
    .config("spark.executor.cores", "4")
    .config("spark.executor.memory", "8g")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .getOrCreate();
```

## Troubleshooting

### Out of Memory Errors
- Increase executor/driver memory
- Use more partitions
- Cache selectively
- Use broadcast for small tables

### Slow Performance
- Check partition count (`spark.sql.shuffle.partitions`)
- Enable adaptive query execution
- Use appropriate join strategies
- Avoid UDFs when possible (use built-in functions)

### Shuffle Issues
- Reduce data before shuffle
- Use appropriate partitioning strategy
- Increase shuffle memory
- Enable shuffle service

## Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
- [API Documentation](https://spark.apache.org/docs/latest/api/java/)

## Next Steps

1. Complete all basic examples
2. Experiment with different configurations
3. Profile your applications
4. Learn Spark UI for debugging
5. Explore advanced features (Structured Streaming, MLlib)

## Related Topics

- **Spark Streaming**: Real-time data processing
- **MLlib**: Machine learning library
- **GraphX**: Graph processing
- **Delta Lake**: ACID transactions on data lakes
- **Databricks**: Unified analytics platform
