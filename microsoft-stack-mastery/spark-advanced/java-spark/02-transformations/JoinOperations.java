package com.microsoft.spark.transformations;

import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import scala.Tuple2;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * JoinOperations demonstrates various join types including
 * inner, outer, left, right, cross, and semi joins.
 */
public class JoinOperations {
    
    public static void main(String[] args) {
        JoinOperations operations = new JoinOperations();
        
        try {
            operations.demonstrateBasicJoins();
            operations.demonstrateOuterJoins();
            operations.demonstrateAdvancedJoins();
            operations.demonstrateRDDJoins();
        } catch (Exception e) {
            System.err.println("Error in JoinOperations: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Basic Inner Joins
     */
    public void demonstrateBasicJoins() {
        System.out.println("\n=== Example 1: Basic Inner Joins ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic Joins")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create employee DataFrame
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", 101),
                new Employee(2, "Jane Smith", 102),
                new Employee(3, "Bob Johnson", 101),
                new Employee(4, "Alice Williams", 103),
                new Employee(5, "Charlie Brown", 102)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Create department DataFrame
            List<Department> departments = Arrays.asList(
                new Department(101, "Engineering", "Building A"),
                new Department(102, "Marketing", "Building B"),
                new Department(103, "Sales", "Building C"),
                new Department(104, "HR", "Building D")
            );
            
            Dataset<Row> deptDF = spark.createDataFrame(departments, Department.class);
            
            System.out.println("\nEmployees:");
            empDF.show();
            
            System.out.println("\nDepartments:");
            deptDF.show();
            
            // Inner join - default join type
            System.out.println("\nInner Join (default):");
            Dataset<Row> innerJoin = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")));
            innerJoin.show();
            
            // Inner join - explicit
            System.out.println("\nInner Join (explicit):");
            Dataset<Row> explicitInner = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")), "inner");
            explicitInner.show();
            
            // Join with column selection
            System.out.println("\nJoin with selected columns:");
            empDF.join(deptDF, empDF.col("departmentId").equalTo(deptDF.col("id")))
                .select(empDF.col("name"), deptDF.col("departmentName"), deptDF.col("location"))
                .show();
            
            // Join on column name (when column names match)
            Dataset<Row> empDF2 = empDF.withColumnRenamed("departmentId", "dept_id");
            Dataset<Row> deptDF2 = deptDF.withColumnRenamed("id", "dept_id");
            
            System.out.println("\nJoin on column name:");
            empDF2.join(deptDF2, "dept_id").show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: Outer Joins
     */
    public void demonstrateOuterJoins() {
        System.out.println("\n=== Example 2: Outer Joins ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Outer Joins")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", 101),
                new Employee(2, "Jane Smith", 102),
                new Employee(3, "Bob Johnson", 101),
                new Employee(4, "Alice Williams", 105)  // No matching department
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            List<Department> departments = Arrays.asList(
                new Department(101, "Engineering", "Building A"),
                new Department(102, "Marketing", "Building B"),
                new Department(103, "Sales", "Building C"),      // No employees
                new Department(104, "HR", "Building D")          // No employees
            );
            
            Dataset<Row> deptDF = spark.createDataFrame(departments, Department.class);
            
            // Left Outer Join - all employees, matched departments
            System.out.println("\nLeft Outer Join:");
            Dataset<Row> leftJoin = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")), "left");
            leftJoin.show();
            
            // Right Outer Join - all departments, matched employees
            System.out.println("\nRight Outer Join:");
            Dataset<Row> rightJoin = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")), "right");
            rightJoin.show();
            
            // Full Outer Join - all employees and all departments
            System.out.println("\nFull Outer Join:");
            Dataset<Row> fullJoin = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")), "outer");
            fullJoin.show();
            
            // Finding unmatched records
            System.out.println("\nEmployees without department (from left join):");
            leftJoin.filter(deptDF.col("id").isNull())
                .select(empDF.col("name"), empDF.col("departmentId"))
                .show();
            
            System.out.println("\nDepartments without employees (from right join):");
            rightJoin.filter(empDF.col("id").isNull())
                .select(deptDF.col("departmentName"), deptDF.col("location"))
                .show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: Advanced Joins
     */
    public void demonstrateAdvancedJoins() {
        System.out.println("\n=== Example 3: Advanced Joins ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Advanced Joins")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create sample data
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", 101),
                new Employee(2, "Jane Smith", 102),
                new Employee(3, "Bob Johnson", 101)
            );
            
            List<Department> departments = Arrays.asList(
                new Department(101, "Engineering", "Building A"),
                new Department(102, "Marketing", "Building B")
            );
            
            List<Salary> salaries = Arrays.asList(
                new Salary(1, 75000, "2024-01"),
                new Salary(2, 65000, "2024-01"),
                new Salary(3, 80000, "2024-01")
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            Dataset<Row> deptDF = spark.createDataFrame(departments, Department.class);
            Dataset<Row> salaryDF = spark.createDataFrame(salaries, Salary.class);
            
            // Cross Join (Cartesian Product)
            System.out.println("\nCross Join:");
            Dataset<Row> crossJoin = empDF.crossJoin(deptDF);
            System.out.println("Result count: " + crossJoin.count() + " rows");
            crossJoin.show();
            
            // Semi Join - returns rows from left with match in right
            System.out.println("\nLeft Semi Join:");
            Dataset<Row> semiJoin = empDF.join(deptDF, 
                empDF.col("departmentId").equalTo(deptDF.col("id")), "left_semi");
            semiJoin.show();
            
            // Anti Join - returns rows from left without match in right
            List<Employee> moreEmployees = Arrays.asList(
                new Employee(1, "John Doe", 101),
                new Employee(2, "Jane Smith", 102),
                new Employee(4, "Alice Williams", 999)  // No matching department
            );
            
            Dataset<Row> empDF2 = spark.createDataFrame(moreEmployees, Employee.class);
            
            System.out.println("\nLeft Anti Join (employees without department):");
            Dataset<Row> antiJoin = empDF2.join(deptDF, 
                empDF2.col("departmentId").equalTo(deptDF.col("id")), "left_anti");
            antiJoin.show();
            
            // Multiple joins
            System.out.println("\nMultiple Joins:");
            Dataset<Row> multiJoin = empDF
                .join(deptDF, empDF.col("departmentId").equalTo(deptDF.col("id")))
                .join(salaryDF, empDF.col("id").equalTo(salaryDF.col("employeeId")))
                .select(
                    empDF.col("name"),
                    deptDF.col("departmentName"),
                    salaryDF.col("amount").alias("salary"),
                    salaryDF.col("month")
                );
            multiJoin.show();
            
            // Self Join
            System.out.println("\nSelf Join (find employees in same department):");
            Dataset<Row> emp1 = empDF.alias("emp1");
            Dataset<Row> emp2 = empDF.alias("emp2");
            
            Dataset<Row> selfJoin = emp1.join(emp2, 
                emp1.col("departmentId").equalTo(emp2.col("departmentId"))
                .and(emp1.col("id").lt(emp2.col("id")))
            ).select(
                emp1.col("name").alias("employee1"),
                emp2.col("name").alias("employee2"),
                emp1.col("departmentId")
            );
            selfJoin.show();
            
            // Join with multiple conditions
            System.out.println("\nJoin with multiple conditions:");
            List<Project> projects = Arrays.asList(
                new Project(1, "Project A", 101),
                new Project(2, "Project B", 102),
                new Project(3, "Project C", 101)
            );
            
            Dataset<Row> projectDF = spark.createDataFrame(projects, Project.class);
            
            Dataset<Row> complexJoin = empDF.join(projectDF,
                empDF.col("departmentId").equalTo(projectDF.col("departmentId"))
                .and(empDF.col("id").equalTo(projectDF.col("leadId")))
            );
            complexJoin.show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: RDD Joins
     */
    public void demonstrateRDDJoins() {
        System.out.println("\n=== Example 4: RDD Joins ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("RDD Joins")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // Create Pair RDDs
            List<Tuple2<Integer, String>> employees = Arrays.asList(
                new Tuple2<>(1, "John Doe"),
                new Tuple2<>(2, "Jane Smith"),
                new Tuple2<>(3, "Bob Johnson"),
                new Tuple2<>(4, "Alice Williams")
            );
            
            List<Tuple2<Integer, Double>> salaries = Arrays.asList(
                new Tuple2<>(1, 75000.0),
                new Tuple2<>(2, 65000.0),
                new Tuple2<>(3, 80000.0)
            );
            
            JavaPairRDD<Integer, String> empRDD = sc.parallelizePairs(employees);
            JavaPairRDD<Integer, Double> salaryRDD = sc.parallelizePairs(salaries);
            
            // Inner join
            System.out.println("\nRDD Inner Join:");
            JavaPairRDD<Integer, Tuple2<String, Double>> joined = empRDD.join(salaryRDD);
            joined.collect().forEach(tuple -> 
                System.out.println("ID: " + tuple._1 + ", Name: " + tuple._2._1 + 
                                 ", Salary: " + tuple._2._2)
            );
            
            // Left outer join
            System.out.println("\nRDD Left Outer Join:");
            JavaPairRDD<Integer, Tuple2<String, com.google.common.base.Optional<Double>>> leftJoin = 
                empRDD.leftOuterJoin(salaryRDD);
            leftJoin.collect().forEach(tuple -> 
                System.out.println("ID: " + tuple._1 + ", Name: " + tuple._2._1 + 
                                 ", Salary: " + (tuple._2._2.isPresent() ? tuple._2._2.get() : "N/A"))
            );
            
            // Right outer join
            System.out.println("\nRDD Right Outer Join:");
            JavaPairRDD<Integer, Tuple2<com.google.common.base.Optional<String>, Double>> rightJoin = 
                empRDD.rightOuterJoin(salaryRDD);
            rightJoin.collect().forEach(tuple -> 
                System.out.println("ID: " + tuple._1 + 
                                 ", Name: " + (tuple._2._1.isPresent() ? tuple._2._1.get() : "N/A") +
                                 ", Salary: " + tuple._2._2)
            );
            
            // Full outer join
            System.out.println("\nRDD Full Outer Join:");
            JavaPairRDD<Integer, Tuple2<com.google.common.base.Optional<String>, 
                                       com.google.common.base.Optional<Double>>> fullJoin = 
                empRDD.fullOuterJoin(salaryRDD);
            fullJoin.collect().forEach(tuple -> 
                System.out.println("ID: " + tuple._1 + 
                                 ", Name: " + (tuple._2._1.isPresent() ? tuple._2._1.get() : "N/A") +
                                 ", Salary: " + (tuple._2._2.isPresent() ? tuple._2._2.get() : "N/A"))
            );
            
            // Cartesian product
            System.out.println("\nRDD Cartesian Product:");
            JavaRDD<String> names = sc.parallelize(Arrays.asList("John", "Jane"));
            JavaRDD<String> depts = sc.parallelize(Arrays.asList("Engineering", "Marketing"));
            JavaPairRDD<String, String> cartesian = names.cartesian(depts);
            System.out.println("Cartesian result: " + cartesian.collect());
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    // Helper classes
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
        private String departmentName;
        private String location;
        
        public Department() {}
        
        public Department(int id, String departmentName, String location) {
            this.id = id;
            this.departmentName = departmentName;
            this.location = location;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getDepartmentName() { return departmentName; }
        public void setDepartmentName(String departmentName) { this.departmentName = departmentName; }
        public String getLocation() { return location; }
        public void setLocation(String location) { this.location = location; }
    }
    
    public static class Salary implements Serializable {
        private int employeeId;
        private double amount;
        private String month;
        
        public Salary() {}
        
        public Salary(int employeeId, double amount, String month) {
            this.employeeId = employeeId;
            this.amount = amount;
            this.month = month;
        }
        
        public int getEmployeeId() { return employeeId; }
        public void setEmployeeId(int employeeId) { this.employeeId = employeeId; }
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
        public String getMonth() { return month; }
        public void setMonth(String month) { this.month = month; }
    }
    
    public static class Project implements Serializable {
        private int leadId;
        private String projectName;
        private int departmentId;
        
        public Project() {}
        
        public Project(int leadId, String projectName, int departmentId) {
            this.leadId = leadId;
            this.projectName = projectName;
            this.departmentId = departmentId;
        }
        
        public int getLeadId() { return leadId; }
        public void setLeadId(int leadId) { this.leadId = leadId; }
        public String getProjectName() { return projectName; }
        public void setProjectName(String projectName) { this.projectName = projectName; }
        public int getDepartmentId() { return departmentId; }
        public void setDepartmentId(int departmentId) { this.departmentId = departmentId; }
    }
}
