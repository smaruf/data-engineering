package com.microsoft.spark.performance;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.storage.StorageLevel;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * CachingExample demonstrates caching and persistence strategies
 * for Spark performance optimization.
 */
public class CachingExample {
    
    public static void main(String[] args) {
        CachingExample example = new CachingExample();
        
        try {
            example.demonstrateBasicCaching();
            example.demonstratePersistenceLevels();
            example.demonstrateCachingStrategies();
            example.demonstrateUnpersist();
        } catch (Exception e) {
            System.err.println("Error in CachingExample: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public void demonstrateBasicCaching() {
        System.out.println("\n=== Example 1: Basic Caching ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic Caching")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000),
                new Employee(2, "Jane", "Marketing", 65000),
                new Employee(3, "Bob", "Engineering", 80000),
                new Employee(4, "Alice", "Sales", 70000)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Cache the DataFrame
            empDF.cache();
            
            // First action - loads data into cache
            System.out.println("First count (loads cache): " + empDF.count());
            
            // Second action - uses cached data
            System.out.println("Second count (uses cache): " + empDF.count());
            
            // Check if cached
            System.out.println("Is cached: " + empDF.storageLevel().useMemory());
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstratePersistenceLevels() {
        System.out.println("\n=== Example 2: Persistence Levels ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Persistence Levels")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Product> products = Arrays.asList(
                new Product(1, "Laptop", 1200.0),
                new Product(2, "Mouse", 25.0),
                new Product(3, "Desk", 300.0)
            );
            
            Dataset<Row> df = spark.createDataFrame(products, Product.class);
            
            // MEMORY_ONLY (default for cache())
            Dataset<Row> memoryOnly = df.persist(StorageLevel.MEMORY_ONLY());
            System.out.println("\nMEMORY_ONLY:");
            System.out.println("Count: " + memoryOnly.count());
            memoryOnly.unpersist();
            
            // MEMORY_AND_DISK
            Dataset<Row> memoryAndDisk = df.persist(StorageLevel.MEMORY_AND_DISK());
            System.out.println("\nMEMORY_AND_DISK:");
            System.out.println("Count: " + memoryAndDisk.count());
            memoryAndDisk.unpersist();
            
            // DISK_ONLY
            Dataset<Row> diskOnly = df.persist(StorageLevel.DISK_ONLY());
            System.out.println("\nDISK_ONLY:");
            System.out.println("Count: " + diskOnly.count());
            diskOnly.unpersist();
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateCachingStrategies() {
        System.out.println("\n=== Example 3: Caching Strategies ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Caching Strategies")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000),
                new Employee(2, "Jane", "Marketing", 65000),
                new Employee(3, "Bob", "Engineering", 80000)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Cache after expensive transformations
            Dataset<Row> transformed = empDF
                .filter(col("salary").gt(60000))
                .withColumn("bonus", col("salary").multiply(0.1))
                .cache();
            
            // Multiple actions on cached data
            System.out.println("Count: " + transformed.count());
            System.out.println("Avg salary: " + transformed.agg(avg("salary")).first().getDouble(0));
            transformed.show();
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateUnpersist() {
        System.out.println("\n=== Example 4: Unpersist ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Unpersist")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Product> products = Arrays.asList(
                new Product(1, "Laptop", 1200.0),
                new Product(2, "Mouse", 25.0)
            );
            
            Dataset<Row> df = spark.createDataFrame(products, Product.class);
            
            df.cache();
            df.count();
            
            System.out.println("Before unpersist - cached: " + df.storageLevel().useMemory());
            
            df.unpersist();
            
            System.out.println("After unpersist - cached: " + df.storageLevel().useMemory());
            
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
    
    public static class Product implements Serializable {
        private int id;
        private String name;
        private double price;
        
        public Product() {}
        
        public Product(int id, String name, double price) {
            this.id = id;
            this.name = name;
            this.price = price;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getPrice() { return price; }
        public void setPrice(double price) { this.price = price; }
    }
}
