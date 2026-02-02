package com.microsoft.spark.basics;

import org.apache.spark.SparkConf;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;
import java.util.Arrays;
import java.util.List;

/**
 * SparkSessionExample demonstrates how to create and configure a SparkSession
 * with various configurations and settings.
 * 
 * SparkSession is the entry point for Spark SQL and DataFrame API.
 */
public class SparkSessionExample {
    
    public static void main(String[] args) {
        SparkSessionExample example = new SparkSessionExample();
        
        try {
            // Example 1: Basic SparkSession creation
            example.createBasicSession();
            
            // Example 2: SparkSession with custom configurations
            example.createConfiguredSession();
            
            // Example 3: SparkSession with multiple configurations
            example.createAdvancedSession();
            
            // Example 4: Working with SparkSession
            example.workWithSparkSession();
            
        } catch (Exception e) {
            System.err.println("Error in SparkSessionExample: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Create a basic SparkSession
     */
    public void createBasicSession() {
        System.out.println("\n=== Example 1: Basic SparkSession Creation ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic Spark Application")
                .master("local[*]")  // Use all available cores
                .getOrCreate();
        
        System.out.println("Spark Version: " + spark.version());
        System.out.println("Application Name: " + spark.sparkContext().appName());
        System.out.println("Master: " + spark.sparkContext().master());
        
        spark.stop();
    }
    
    /**
     * Example 2: SparkSession with custom configurations
     */
    public void createConfiguredSession() {
        System.out.println("\n=== Example 2: SparkSession with Custom Configurations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Configured Spark Application")
                .master("local[4]")  // Use 4 cores
                .config("spark.sql.shuffle.partitions", "200")
                .config("spark.executor.memory", "2g")
                .config("spark.driver.memory", "1g")
                .getOrCreate();
        
        // Display configuration
        System.out.println("Shuffle Partitions: " + 
            spark.conf().get("spark.sql.shuffle.partitions"));
        System.out.println("Executor Memory: " + 
            spark.conf().get("spark.executor.memory"));
        
        spark.stop();
    }
    
    /**
     * Example 3: SparkSession with advanced configurations
     */
    public void createAdvancedSession() {
        System.out.println("\n=== Example 3: Advanced SparkSession Configuration ===");
        
        // Create SparkConf for advanced configuration
        SparkConf conf = new SparkConf()
                .setAppName("Advanced Spark Application")
                .setMaster("local[*]")
                .set("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
                .set("spark.sql.shuffle.partitions", "100")
                .set("spark.default.parallelism", "8")
                .set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                .set("spark.sql.adaptive.enabled", "true")
                .set("spark.sql.adaptive.coalescePartitions.enabled", "true");
        
        SparkSession spark = SparkSession.builder()
                .config(conf)
                .enableHiveSupport()  // Enable Hive support
                .getOrCreate();
        
        // Set runtime configuration
        spark.conf().set("spark.sql.autoBroadcastJoinThreshold", "10485760"); // 10MB
        
        // Display all configurations
        System.out.println("All Spark Configurations:");
        spark.conf().getAll().forEach((key, value) -> {
            if (key.startsWith("spark.sql") || key.startsWith("spark.default")) {
                System.out.println(key + " = " + value);
            }
        });
        
        spark.stop();
    }
    
    /**
     * Example 4: Working with SparkSession - Creating DataFrames
     */
    public void workWithSparkSession() {
        System.out.println("\n=== Example 4: Working with SparkSession ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Working with SparkSession")
                .master("local[*]")
                .config("spark.sql.shuffle.partitions", "4")
                .getOrCreate();
        
        try {
            // Create DataFrame from data
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000),
                new Employee(2, "Jane Smith", "Marketing", 65000),
                new Employee(3, "Bob Johnson", "Engineering", 80000),
                new Employee(4, "Alice Williams", "Sales", 70000),
                new Employee(5, "Charlie Brown", "Engineering", 72000)
            );
            
            Dataset<Row> df = spark.createDataFrame(employees, Employee.class);
            
            System.out.println("\nDataFrame Schema:");
            df.printSchema();
            
            System.out.println("\nEmployee Data:");
            df.show();
            
            // Simple SQL query
            df.createOrReplaceTempView("employees");
            Dataset<Row> result = spark.sql(
                "SELECT department, COUNT(*) as count, AVG(salary) as avg_salary " +
                "FROM employees GROUP BY department ORDER BY avg_salary DESC"
            );
            
            System.out.println("\nDepartment Statistics:");
            result.show();
            
            // Access Spark Context
            System.out.println("\nSpark Context Information:");
            System.out.println("Default Parallelism: " + 
                spark.sparkContext().defaultParallelism());
            System.out.println("Application ID: " + 
                spark.sparkContext().applicationId());
            
        } catch (Exception e) {
            System.err.println("Error working with SparkSession: " + e.getMessage());
            e.printStackTrace();
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Employee class for example data
     */
    public static class Employee implements java.io.Serializable {
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
        
        // Getters and Setters
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
