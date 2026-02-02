package com.microsoft.spark.performance;

import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * PartitioningStrategies demonstrates various partitioning techniques
 * including repartition, coalesce, and custom partitioning.
 */
public class PartitioningStrategies {
    
    public static void main(String[] args) {
        PartitioningStrategies strategies = new PartitioningStrategies();
        
        try {
            strategies.demonstrateBasicPartitioning();
            strategies.demonstrateRepartitionVsCoalesce();
            strategies.demonstratePartitionBy();
            strategies.demonstrateOptimalPartitioning();
        } catch (Exception e) {
            System.err.println("Error in PartitioningStrategies: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public void demonstrateBasicPartitioning() {
        System.out.println("\n=== Example 1: Basic Partitioning ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic Partitioning")
                .master("local[*]")
                .config("spark.sql.shuffle.partitions", "8")
                .getOrCreate();
        
        try {
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            Dataset<Row> df = spark.createDataset(numbers, org.apache.spark.sql.Encoders.INT())
                .toDF("value");
            
            System.out.println("Initial partitions: " + df.rdd().getNumPartitions());
            
            // Repartition to increase partitions
            Dataset<Row> repartitioned = df.repartition(5);
            System.out.println("After repartition(5): " + repartitioned.rdd().getNumPartitions());
            
            // Coalesce to decrease partitions
            Dataset<Row> coalesced = repartitioned.coalesce(2);
            System.out.println("After coalesce(2): " + coalesced.rdd().getNumPartitions());
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateRepartitionVsCoalesce() {
        System.out.println("\n=== Example 2: Repartition vs Coalesce ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Repartition vs Coalesce")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            List<Integer> data = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            JavaRDD<Integer> rdd = sc.parallelize(data, 10);
            
            System.out.println("Original partitions: " + rdd.getNumPartitions());
            
            // Coalesce - no shuffle, combines partitions
            JavaRDD<Integer> coalesced = rdd.coalesce(2);
            System.out.println("\nCoalesce to 2 partitions (no shuffle):");
            System.out.println("Partitions: " + coalesced.getNumPartitions());
            
            // Repartition - with shuffle, can increase or decrease
            JavaRDD<Integer> repartitioned = rdd.repartition(3);
            System.out.println("\nRepartition to 3 (with shuffle):");
            System.out.println("Partitions: " + repartitioned.getNumPartitions());
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    public void demonstratePartitionBy() {
        System.out.println("\n=== Example 3: PartitionBy ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("PartitionBy")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000),
                new Employee(2, "Jane", "Marketing", 65000),
                new Employee(3, "Bob", "Engineering", 80000),
                new Employee(4, "Alice", "Sales", 70000),
                new Employee(5, "Charlie", "Engineering", 72000)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Repartition by column
            Dataset<Row> byDept = empDF.repartition(col("department"));
            System.out.println("Partitions by department: " + byDept.rdd().getNumPartitions());
            
            // Repartition by multiple columns
            Dataset<Row> byDeptAndSalary = empDF.repartition(3, col("department"), col("salary"));
            System.out.println("Partitions by dept & salary: " + byDeptAndSalary.rdd().getNumPartitions());
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateOptimalPartitioning() {
        System.out.println("\n=== Example 4: Optimal Partitioning ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Optimal Partitioning")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000),
                new Employee(2, "Jane", "Marketing", 65000),
                new Employee(3, "Bob", "Engineering", 80000)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Repartition before expensive operations
            Dataset<Row> result = empDF
                .repartition(4)
                .groupBy("department")
                .agg(avg("salary").alias("avg_salary"));
            
            result.show();
            
        } finally {
            spark.stop();
        }
    }
    
    public static class Employee implements Serializable {
        private int id;
        private String name;
        private String department;
        private double salary;
        
        public Employee() {}
        
        public Employee(int id, String name, String department, double salary) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getDepartment() { return department; }
        public void setDepartment(String department) { this.department = department; }
        public double getSalary() { return salary; }
        public void setSalary(double salary) { this.salary = salary; }
    }
}
