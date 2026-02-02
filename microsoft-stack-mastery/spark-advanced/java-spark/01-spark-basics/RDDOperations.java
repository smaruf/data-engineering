package com.microsoft.spark.basics;

import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.SparkSession;
import scala.Tuple2;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * RDDOperations demonstrates core RDD (Resilient Distributed Dataset) operations
 * including transformations and actions.
 * 
 * RDD is the fundamental data structure of Apache Spark.
 */
public class RDDOperations {
    
    public static void main(String[] args) {
        RDDOperations operations = new RDDOperations();
        
        try {
            operations.demonstrateBasicTransformations();
            operations.demonstrateActions();
            operations.demonstratePairRDDOperations();
            operations.demonstrateAdvancedOperations();
        } catch (Exception e) {
            System.err.println("Error in RDDOperations: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Basic RDD Transformations
     */
    public void demonstrateBasicTransformations() {
        System.out.println("\n=== Example 1: Basic RDD Transformations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("RDD Basic Transformations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // Create RDD from collection
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            JavaRDD<Integer> rdd = sc.parallelize(numbers);
            
            // map: Transform each element
            JavaRDD<Integer> squared = rdd.map(x -> x * x);
            System.out.println("Squared numbers: " + squared.collect());
            
            // filter: Keep only elements that match predicate
            JavaRDD<Integer> evenNumbers = rdd.filter(x -> x % 2 == 0);
            System.out.println("Even numbers: " + evenNumbers.collect());
            
            // flatMap: Transform and flatten
            JavaRDD<Integer> flatMapped = rdd.flatMap(x -> 
                Arrays.asList(x, x * 2, x * 3).iterator()
            );
            System.out.println("FlatMapped (first 10): " + flatMapped.take(10));
            
            // distinct: Remove duplicates
            List<Integer> withDuplicates = Arrays.asList(1, 2, 2, 3, 3, 3, 4, 4, 4, 4);
            JavaRDD<Integer> duplicatesRDD = sc.parallelize(withDuplicates);
            JavaRDD<Integer> distinct = duplicatesRDD.distinct();
            System.out.println("Distinct numbers: " + distinct.collect());
            
            // union: Combine two RDDs
            JavaRDD<Integer> rdd1 = sc.parallelize(Arrays.asList(1, 2, 3));
            JavaRDD<Integer> rdd2 = sc.parallelize(Arrays.asList(4, 5, 6));
            JavaRDD<Integer> union = rdd1.union(rdd2);
            System.out.println("Union: " + union.collect());
            
            // intersection: Common elements
            JavaRDD<Integer> rdd3 = sc.parallelize(Arrays.asList(2, 3, 4));
            JavaRDD<Integer> intersection = rdd1.intersection(rdd3);
            System.out.println("Intersection: " + intersection.collect());
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 2: RDD Actions
     */
    public void demonstrateActions() {
        System.out.println("\n=== Example 2: RDD Actions ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("RDD Actions")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            JavaRDD<Integer> rdd = sc.parallelize(numbers);
            
            // collect: Return all elements
            List<Integer> collected = rdd.collect();
            System.out.println("Collected: " + collected);
            
            // count: Count elements
            long count = rdd.count();
            System.out.println("Count: " + count);
            
            // first: Get first element
            Integer first = rdd.first();
            System.out.println("First element: " + first);
            
            // take: Get first n elements
            List<Integer> firstThree = rdd.take(3);
            System.out.println("First 3 elements: " + firstThree);
            
            // reduce: Aggregate elements
            Integer sum = rdd.reduce((a, b) -> a + b);
            System.out.println("Sum (using reduce): " + sum);
            
            // fold: Like reduce but with initial value
            Integer sumWithInitial = rdd.fold(0, (a, b) -> a + b);
            System.out.println("Sum (using fold): " + sumWithInitial);
            
            // aggregate: More flexible aggregation
            Integer product = rdd.aggregate(
                1,                              // Initial value
                (acc, value) -> acc * value,    // Sequential operation
                (acc1, acc2) -> acc1 * acc2     // Combine operation
            );
            System.out.println("Product (using aggregate): " + product);
            
            // foreach: Apply function to each element (action)
            System.out.print("Elements (foreach): ");
            rdd.foreach(x -> System.out.print(x + " "));
            System.out.println();
            
            // countByValue: Count occurrences of each value
            List<Integer> withDuplicates = Arrays.asList(1, 2, 2, 3, 3, 3, 4, 4, 4, 4);
            JavaRDD<Integer> duplicatesRDD = sc.parallelize(withDuplicates);
            Map<Integer, Long> valueCounts = duplicatesRDD.countByValue();
            System.out.println("Count by value: " + valueCounts);
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 3: Pair RDD Operations
     */
    public void demonstratePairRDDOperations() {
        System.out.println("\n=== Example 3: Pair RDD Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Pair RDD Operations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // Create Pair RDD
            List<Tuple2<String, Integer>> data = Arrays.asList(
                new Tuple2<>("apple", 5),
                new Tuple2<>("banana", 3),
                new Tuple2<>("apple", 2),
                new Tuple2<>("orange", 4),
                new Tuple2<>("banana", 1),
                new Tuple2<>("apple", 3)
            );
            
            JavaPairRDD<String, Integer> pairRDD = sc.parallelizePairs(data);
            
            // reduceByKey: Reduce values for each key
            JavaPairRDD<String, Integer> totalByKey = pairRDD.reduceByKey((a, b) -> a + b);
            System.out.println("Total by key: " + totalByKey.collect());
            
            // groupByKey: Group values for each key
            JavaPairRDD<String, Iterable<Integer>> grouped = pairRDD.groupByKey();
            System.out.println("Grouped by key:");
            grouped.collect().forEach(tuple -> 
                System.out.println("  " + tuple._1 + ": " + tuple._2)
            );
            
            // mapValues: Transform only values
            JavaPairRDD<String, Integer> doubled = pairRDD.mapValues(v -> v * 2);
            System.out.println("Values doubled: " + doubled.collect());
            
            // keys and values
            JavaRDD<String> keys = pairRDD.keys();
            System.out.println("All keys: " + keys.collect());
            
            JavaRDD<Integer> values = pairRDD.values();
            System.out.println("All values: " + values.collect());
            
            // countByKey: Count values for each key
            Map<String, Long> counts = pairRDD.countByKey();
            System.out.println("Count by key: " + counts);
            
            // sortByKey: Sort by keys
            JavaPairRDD<String, Integer> sorted = pairRDD.sortByKey();
            System.out.println("Sorted by key: " + sorted.collect());
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 4: Advanced RDD Operations
     */
    public void demonstrateAdvancedOperations() {
        System.out.println("\n=== Example 4: Advanced RDD Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Advanced RDD Operations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // sample: Random sample of RDD
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            JavaRDD<Integer> rdd = sc.parallelize(numbers);
            JavaRDD<Integer> sampled = rdd.sample(false, 0.5, 42L);
            System.out.println("Sampled (50%): " + sampled.collect());
            
            // cartesian: Cartesian product
            JavaRDD<Integer> rdd1 = sc.parallelize(Arrays.asList(1, 2, 3));
            JavaRDD<String> rdd2 = sc.parallelize(Arrays.asList("a", "b"));
            JavaPairRDD<Integer, String> cartesian = rdd1.cartesian(rdd2);
            System.out.println("Cartesian product: " + cartesian.collect());
            
            // coalesce and repartition
            JavaRDD<Integer> manyPartitions = sc.parallelize(numbers, 10);
            System.out.println("Original partitions: " + manyPartitions.getNumPartitions());
            
            JavaRDD<Integer> coalesced = manyPartitions.coalesce(2);
            System.out.println("After coalesce: " + coalesced.getNumPartitions());
            
            JavaRDD<Integer> repartitioned = manyPartitions.repartition(5);
            System.out.println("After repartition: " + repartitioned.getNumPartitions());
            
            // glom: Convert each partition to array
            JavaRDD<List<Integer>> partitionArrays = rdd.glom();
            System.out.println("Partition arrays: " + partitionArrays.collect());
            
            // Pair RDD join operations
            List<Tuple2<String, Integer>> employees = Arrays.asList(
                new Tuple2<>("John", 1),
                new Tuple2<>("Jane", 2),
                new Tuple2<>("Bob", 3)
            );
            
            List<Tuple2<Integer, String>> departments = Arrays.asList(
                new Tuple2<>(1, "Engineering"),
                new Tuple2<>(2, "Marketing"),
                new Tuple2<>(4, "Sales")
            );
            
            JavaPairRDD<String, Integer> empRDD = sc.parallelizePairs(employees);
            JavaPairRDD<Integer, String> deptRDD = sc.parallelizePairs(departments);
            
            // Need to swap key-value for join
            JavaPairRDD<Integer, String> empByDeptId = empRDD.mapToPair(t -> 
                new Tuple2<>(t._2, t._1)
            );
            
            JavaPairRDD<Integer, Tuple2<String, String>> joined = empByDeptId.join(deptRDD);
            System.out.println("Inner join: " + joined.collect());
            
            JavaPairRDD<Integer, Tuple2<String, com.google.common.base.Optional<String>>> leftJoin = 
                empByDeptId.leftOuterJoin(deptRDD);
            System.out.println("Left outer join: " + leftJoin.collect());
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
}
