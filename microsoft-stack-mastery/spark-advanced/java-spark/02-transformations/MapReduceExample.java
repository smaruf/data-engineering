package com.microsoft.spark.transformations;

import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Encoders;
import scala.Tuple2;
import static org.apache.spark.sql.functions.*;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * MapReduceExample demonstrates map, flatMap, and reduce operations
 * in both RDD and Dataset APIs.
 */
public class MapReduceExample {
    
    public static void main(String[] args) {
        MapReduceExample example = new MapReduceExample();
        
        try {
            example.demonstrateMapOperations();
            example.demonstrateFlatMapOperations();
            example.demonstrateReduceOperations();
            example.wordCountExample();
        } catch (Exception e) {
            System.err.println("Error in MapReduceExample: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Map Operations
     */
    public void demonstrateMapOperations() {
        System.out.println("\n=== Example 1: Map Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Map Operations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // RDD map operations
            System.out.println("\n--- RDD Map Operations ---");
            
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
            JavaRDD<Integer> numbersRDD = sc.parallelize(numbers);
            
            // Simple map: multiply by 2
            JavaRDD<Integer> doubled = numbersRDD.map(x -> x * 2);
            System.out.println("Doubled: " + doubled.collect());
            
            // Map to different type
            JavaRDD<String> strings = numbersRDD.map(x -> "Number: " + x);
            System.out.println("Mapped to strings: " + strings.collect());
            
            // Map with complex transformation
            List<Employee> employees = Arrays.asList(
                new Employee("John", 75000),
                new Employee("Jane", 85000),
                new Employee("Bob", 65000)
            );
            
            JavaRDD<Employee> empRDD = sc.parallelize(employees);
            JavaRDD<EmployeeSummary> summaries = empRDD.map(emp -> 
                new EmployeeSummary(
                    emp.getName(),
                    emp.getSalary(),
                    emp.getSalary() * 0.1,
                    emp.getSalary() > 70000 ? "Senior" : "Junior"
                )
            );
            
            System.out.println("\nEmployee summaries:");
            summaries.collect().forEach(System.out::println);
            
            // Dataset map operations
            System.out.println("\n--- Dataset Map Operations ---");
            
            Dataset<Employee> empDS = spark.createDataset(
                employees,
                Encoders.bean(Employee.class)
            );
            
            Dataset<Double> salaries = empDS.map(
                emp -> emp.getSalary(),
                Encoders.DOUBLE()
            );
            System.out.println("\nSalaries:");
            salaries.show();
            
            // Map with transformation
            Dataset<String> names = empDS.map(
                emp -> emp.getName().toUpperCase(),
                Encoders.STRING()
            );
            System.out.println("\nNames in uppercase:");
            names.show();
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 2: FlatMap Operations
     */
    public void demonstrateFlatMapOperations() {
        System.out.println("\n=== Example 2: FlatMap Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("FlatMap Operations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // RDD flatMap
            System.out.println("\n--- RDD FlatMap ---");
            
            // FlatMap to split strings
            List<String> lines = Arrays.asList(
                "Hello World",
                "Apache Spark",
                "Big Data Processing"
            );
            
            JavaRDD<String> linesRDD = sc.parallelize(lines);
            JavaRDD<String> words = linesRDD.flatMap(line -> 
                Arrays.asList(line.split(" ")).iterator()
            );
            System.out.println("Words: " + words.collect());
            
            // FlatMap to generate multiple values
            List<Integer> numbers = Arrays.asList(1, 2, 3);
            JavaRDD<Integer> numbersRDD = sc.parallelize(numbers);
            JavaRDD<Integer> expanded = numbersRDD.flatMap(x -> 
                Arrays.asList(x, x * 2, x * 3).iterator()
            );
            System.out.println("Expanded: " + expanded.collect());
            
            // FlatMap for one-to-many transformation
            List<Department> departments = Arrays.asList(
                new Department("Engineering", Arrays.asList("John", "Jane", "Bob")),
                new Department("Marketing", Arrays.asList("Alice", "Charlie")),
                new Department("Sales", Arrays.asList("David"))
            );
            
            JavaRDD<Department> deptRDD = sc.parallelize(departments);
            JavaRDD<String> allEmployees = deptRDD.flatMap(dept -> 
                dept.getEmployees().iterator()
            );
            System.out.println("\nAll employees: " + allEmployees.collect());
            
            // Create employee-department pairs
            JavaRDD<Tuple2<String, String>> empDeptPairs = deptRDD.flatMap(dept -> 
                dept.getEmployees().stream()
                    .map(emp -> new Tuple2<>(emp, dept.getName()))
                    .iterator()
            );
            System.out.println("\nEmployee-Department pairs: " + empDeptPairs.collect());
            
            // Dataset flatMap
            System.out.println("\n--- Dataset FlatMap ---");
            
            Dataset<String> linesDS = spark.createDataset(lines, Encoders.STRING());
            Dataset<String> wordsDS = linesDS.flatMap(
                line -> Arrays.asList(line.split(" ")).iterator(),
                Encoders.STRING()
            );
            System.out.println("\nWords from Dataset:");
            wordsDS.show();
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 3: Reduce Operations
     */
    public void demonstrateReduceOperations() {
        System.out.println("\n=== Example 3: Reduce Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Reduce Operations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // RDD reduce
            System.out.println("\n--- RDD Reduce ---");
            
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            JavaRDD<Integer> numbersRDD = sc.parallelize(numbers);
            
            // Sum using reduce
            Integer sum = numbersRDD.reduce((a, b) -> a + b);
            System.out.println("Sum: " + sum);
            
            // Product using reduce
            Integer product = numbersRDD.reduce((a, b) -> a * b);
            System.out.println("Product: " + product);
            
            // Max using reduce
            Integer max = numbersRDD.reduce((a, b) -> Math.max(a, b));
            System.out.println("Max: " + max);
            
            // Min using reduce
            Integer min = numbersRDD.reduce((a, b) -> Math.min(a, b));
            System.out.println("Min: " + min);
            
            // Fold with initial value
            Integer sumWithInitial = numbersRDD.fold(0, (a, b) -> a + b);
            System.out.println("Sum with fold: " + sumWithInitial);
            
            // Aggregate for complex operations
            Tuple2<Integer, Integer> result = numbersRDD.aggregate(
                new Tuple2<>(0, 0),                          // Initial: (sum, count)
                (acc, value) -> new Tuple2<>(acc._1 + value, acc._2 + 1),  // Add value
                (acc1, acc2) -> new Tuple2<>(acc1._1 + acc2._1, acc1._2 + acc2._2)  // Combine
            );
            double average = (double) result._1 / result._2;
            System.out.println("Average using aggregate: " + average);
            
            // ReduceByKey for Pair RDDs
            System.out.println("\n--- ReduceByKey ---");
            
            List<Tuple2<String, Integer>> sales = Arrays.asList(
                new Tuple2<>("Product A", 100),
                new Tuple2<>("Product B", 150),
                new Tuple2<>("Product A", 200),
                new Tuple2<>("Product C", 300),
                new Tuple2<>("Product B", 100),
                new Tuple2<>("Product A", 150)
            );
            
            JavaPairRDD<String, Integer> salesRDD = sc.parallelizePairs(sales);
            JavaPairRDD<String, Integer> totalSales = salesRDD.reduceByKey((a, b) -> a + b);
            System.out.println("Total sales by product: " + totalSales.collect());
            
            // Dataset reduce
            System.out.println("\n--- Dataset Reduce ---");
            
            Dataset<Integer> numbersDS = spark.createDataset(numbers, Encoders.INT());
            Integer dsSum = numbersDS.reduce((a, b) -> a + b);
            System.out.println("Sum using Dataset reduce: " + dsSum);
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 4: Classic Word Count using MapReduce
     */
    public void wordCountExample() {
        System.out.println("\n=== Example 4: Word Count MapReduce ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Word Count")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // Sample text data
            List<String> lines = Arrays.asList(
                "Apache Spark is a unified analytics engine",
                "Spark provides high level APIs in Java Python and Scala",
                "Spark runs on Hadoop YARN Apache Mesos or standalone",
                "Apache Spark includes libraries for SQL streaming machine learning and graph processing"
            );
            
            // RDD approach
            System.out.println("\n--- RDD Word Count ---");
            
            JavaRDD<String> linesRDD = sc.parallelize(lines);
            
            // Step 1: FlatMap to split into words
            JavaRDD<String> words = linesRDD
                .flatMap(line -> Arrays.asList(line.toLowerCase().split("\\s+")).iterator());
            
            // Step 2: Map to (word, 1) pairs
            JavaPairRDD<String, Integer> wordPairs = words
                .mapToPair(word -> new Tuple2<>(word, 1));
            
            // Step 3: ReduceByKey to count
            JavaPairRDD<String, Integer> wordCounts = wordPairs
                .reduceByKey((a, b) -> a + b);
            
            // Step 4: Sort by count descending
            JavaPairRDD<String, Integer> sortedCounts = wordCounts
                .mapToPair(tuple -> new Tuple2<>(tuple._2, tuple._1))
                .sortByKey(false)
                .mapToPair(tuple -> new Tuple2<>(tuple._2, tuple._1));
            
            System.out.println("Word counts (RDD):");
            sortedCounts.take(10).forEach(tuple -> 
                System.out.println(tuple._1 + ": " + tuple._2)
            );
            
            // Dataset approach
            System.out.println("\n--- Dataset Word Count ---");
            
            Dataset<String> linesDS = spark.createDataset(lines, Encoders.STRING());
            
            Dataset<String> wordsDS = linesDS
                .flatMap(line -> Arrays.asList(line.toLowerCase().split("\\s+")).iterator(),
                         Encoders.STRING());
            
            Dataset<Row> wordCountsDF = wordsDS
                .groupBy("value")
                .count()
                .withColumnRenamed("value", "word")
                .orderBy(col("count").desc());
            
            System.out.println("Word counts (Dataset):");
            wordCountsDF.show(10);
            
            // Using SQL
            System.out.println("\n--- SQL Word Count ---");
            
            wordsDS.createOrReplaceTempView("words");
            Dataset<Row> sqlResult = spark.sql(
                "SELECT value as word, COUNT(*) as count " +
                "FROM words " +
                "GROUP BY value " +
                "ORDER BY count DESC"
            );
            
            System.out.println("Word counts (SQL):");
            sqlResult.show(10);
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    // Helper classes
    public static class Employee implements java.io.Serializable {
        private String name;
        private double salary;
        
        public Employee() {}
        
        public Employee(String name, double salary) {
            this.name = name;
            this.salary = salary;
        }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getSalary() { return salary; }
        public void setSalary(double salary) { this.salary = salary; }
    }
    
    public static class EmployeeSummary implements java.io.Serializable {
        private String name;
        private double salary;
        private double bonus;
        private String level;
        
        public EmployeeSummary() {}
        
        public EmployeeSummary(String name, double salary, double bonus, String level) {
            this.name = name;
            this.salary = salary;
            this.bonus = bonus;
            this.level = level;
        }
        
        @Override
        public String toString() {
            return String.format("%s: Salary=%.2f, Bonus=%.2f, Level=%s", 
                name, salary, bonus, level);
        }
    }
    
    public static class Department implements java.io.Serializable {
        private String name;
        private List<String> employees;
        
        public Department() {}
        
        public Department(String name, List<String> employees) {
            this.name = name;
            this.employees = employees;
        }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public List<String> getEmployees() { return employees; }
        public void setEmployees(List<String> employees) { this.employees = employees; }
    }
}
