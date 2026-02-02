package com.microsoft.spark.performance;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * SparkTuning demonstrates various performance tuning techniques
 * including memory management, shuffle optimization, and configuration tuning.
 */
public class SparkTuning {
    
    public static void main(String[] args) {
        SparkTuning tuning = new SparkTuning();
        
        try {
            tuning.demonstrateMemoryTuning();
            tuning.demonstrateShuffleOptimization();
            tuning.demonstrateParallelismTuning();
            tuning.demonstrateConfigurationBestPractices();
        } catch (Exception e) {
            System.err.println("Error in SparkTuning: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public void demonstrateMemoryTuning() {
        System.out.println("\n=== Example 1: Memory Tuning ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Memory Tuning")
                .master("local[*]")
                .config("spark.executor.memory", "2g")
                .config("spark.driver.memory", "1g")
                .config("spark.memory.fraction", "0.6")
                .config("spark.memory.storageFraction", "0.5")
                .getOrCreate();
        
        try {
            System.out.println("Memory Configuration:");
            System.out.println("Executor Memory: " + spark.conf().get("spark.executor.memory"));
            System.out.println("Driver Memory: " + spark.conf().get("spark.driver.memory"));
            System.out.println("Memory Fraction: " + spark.conf().get("spark.memory.fraction"));
            
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", 75000),
                new Employee(2, "Jane", 85000),
                new Employee(3, "Bob", 65000)
            );
            
            Dataset<Row> df = spark.createDataFrame(employees, Employee.class);
            df.cache();
            df.count();
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateShuffleOptimization() {
        System.out.println("\n=== Example 2: Shuffle Optimization ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Shuffle Optimization")
                .master("local[*]")
                .config("spark.sql.shuffle.partitions", "200")
                .config("spark.default.parallelism", "8")
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                .getOrCreate();
        
        try {
            System.out.println("Shuffle Configuration:");
            System.out.println("Shuffle Partitions: " + spark.conf().get("spark.sql.shuffle.partitions"));
            System.out.println("Adaptive Query: " + spark.conf().get("spark.sql.adaptive.enabled"));
            
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", 75000),
                new Employee(2, "Jane", 85000),
                new Employee(3, "Bob", 65000)
            );
            
            Dataset<Row> df = spark.createDataFrame(employees, Employee.class);
            
            // Operation causing shuffle
            Dataset<Row> aggregated = df.groupBy("salary")
                .agg(count("*").alias("count"));
            
            aggregated.show();
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateParallelismTuning() {
        System.out.println("\n=== Example 3: Parallelism Tuning ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Parallelism Tuning")
                .master("local[4]")
                .config("spark.default.parallelism", "8")
                .getOrCreate();
        
        try {
            System.out.println("Parallelism: " + spark.sparkContext().defaultParallelism());
            
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8);
            Dataset<Row> df = spark.createDataset(numbers, org.apache.spark.sql.Encoders.INT())
                .toDF("value");
            
            Dataset<Row> repartitioned = df.repartition(4);
            System.out.println("Partitions: " + repartitioned.rdd().getNumPartitions());
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateConfigurationBestPractices() {
        System.out.println("\n=== Example 4: Configuration Best Practices ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Configuration Best Practices")
                .master("local[*]")
                // Memory settings
                .config("spark.executor.memory", "4g")
                .config("spark.driver.memory", "2g")
                .config("spark.memory.fraction", "0.6")
                
                // Shuffle settings
                .config("spark.sql.shuffle.partitions", "200")
                .config("spark.shuffle.file.buffer", "64k")
                
                // Serialization
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                
                // Adaptive Query Execution
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                
                // Broadcast
                .config("spark.sql.autoBroadcastJoinThreshold", "10485760")
                
                .getOrCreate();
        
        try {
            System.out.println("\nOptimal Configuration:");
            System.out.println("Serializer: " + spark.conf().get("spark.serializer"));
            System.out.println("Adaptive Query: " + spark.conf().get("spark.sql.adaptive.enabled"));
            System.out.println("Broadcast Threshold: " + spark.conf().get("spark.sql.autoBroadcastJoinThreshold"));
            
        } finally {
            spark.stop();
        }
    }
    
    public static class Employee implements Serializable {
        private int id;
        private String name;
        private double salary;
        
        public Employee() {}
        
        public Employee(int id, String name, double salary) {
            this.id = id;
            this.name = name;
            this.salary = salary;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getSalary() { return salary; }
        public void setSalary(double salary) { this.salary = salary; }
    }
}
