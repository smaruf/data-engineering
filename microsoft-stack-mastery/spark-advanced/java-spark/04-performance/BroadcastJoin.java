package com.microsoft.spark.performance;

import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.broadcast.Broadcast;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * BroadcastJoin demonstrates broadcast variables and broadcast joins
 * for optimizing Spark performance with small datasets.
 */
public class BroadcastJoin {
    
    public static void main(String[] args) {
        BroadcastJoin example = new BroadcastJoin();
        
        try {
            example.demonstrateBroadcastVariable();
            example.demonstrateBroadcastJoin();
            example.demonstrateAutoBroadcast();
            example.demonstrateBroadcastHint();
        } catch (Exception e) {
            System.err.println("Error in BroadcastJoin: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    public void demonstrateBroadcastVariable() {
        System.out.println("\n=== Example 1: Broadcast Variable ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Broadcast Variable")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // Create broadcast variable
            Map<String, String> deptMap = new HashMap<>();
            deptMap.put("ENG", "Engineering");
            deptMap.put("MKT", "Marketing");
            deptMap.put("SLS", "Sales");
            
            Broadcast<Map<String, String>> broadcastMap = sc.broadcast(deptMap);
            
            List<String> codes = Arrays.asList("ENG", "MKT", "SLS", "ENG");
            Dataset<Row> df = spark.createDataset(codes, org.apache.spark.sql.Encoders.STRING())
                .toDF("code");
            
            // Use broadcast variable in transformation
            df.show();
            
            // Clean up
            broadcastMap.unpersist();
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    public void demonstrateBroadcastJoin() {
        System.out.println("\n=== Example 2: Broadcast Join ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Broadcast Join")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Large dataset
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", 101),
                new Employee(2, "Jane", 102),
                new Employee(3, "Bob", 101),
                new Employee(4, "Alice", 103)
            );
            
            Dataset<Row> largeDF = spark.createDataFrame(employees, Employee.class);
            
            // Small dataset (good candidate for broadcast)
            List<Department> departments = Arrays.asList(
                new Department(101, "Engineering"),
                new Department(102, "Marketing"),
                new Department(103, "Sales")
            );
            
            Dataset<Row> smallDF = spark.createDataFrame(departments, Department.class);
            
            // Broadcast join
            Dataset<Row> result = largeDF.join(
                broadcast(smallDF),
                largeDF.col("departmentId").equalTo(smallDF.col("id"))
            );
            
            result.show();
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateAutoBroadcast() {
        System.out.println("\n=== Example 3: Auto Broadcast ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Auto Broadcast")
                .master("local[*]")
                .config("spark.sql.autoBroadcastJoinThreshold", "10485760") // 10MB
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", 101),
                new Employee(2, "Jane", 102)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            List<Department> departments = Arrays.asList(
                new Department(101, "Engineering"),
                new Department(102, "Marketing")
            );
            
            Dataset<Row> deptDF = spark.createDataFrame(departments, Department.class);
            
            // Spark will automatically broadcast small table
            Dataset<Row> result = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")));
            
            result.show();
            
        } finally {
            spark.stop();
        }
    }
    
    public void demonstrateBroadcastHint() {
        System.out.println("\n=== Example 4: Broadcast Hint ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Broadcast Hint")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", 101),
                new Employee(2, "Jane", 102)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            empDF.createOrReplaceTempView("employees");
            
            List<Department> departments = Arrays.asList(
                new Department(101, "Engineering"),
                new Department(102, "Marketing")
            );
            
            Dataset<Row> deptDF = spark.createDataFrame(departments, Department.class);
            deptDF.createOrReplaceTempView("departments");
            
            // SQL broadcast hint
            Dataset<Row> result = spark.sql(
                "SELECT /*+ BROADCAST(d) */ e.*, d.name " +
                "FROM employees e JOIN departments d ON e.departmentId = d.id"
            );
            
            result.show();
            
        } finally {
            spark.stop();
        }
    }
    
    public static class Employee implements Serializable {
        private int id;
        private String name;
        private int departmentId;
        
        public Employee() {}
        
        public Employee(int id, String name, int departmentId) {
            this.id = id;
            this.name = name;
            this.departmentId = departmentId;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public int getDepartmentId() { return departmentId; }
        public void setDepartmentId(int departmentId) { this.departmentId = departmentId; }
    }
    
    public static class Department implements Serializable {
        private int id;
        private String name;
        
        public Department() {}
        
        public Department(int id, String name) {
            this.id = id;
            this.name = name;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
    }
}
