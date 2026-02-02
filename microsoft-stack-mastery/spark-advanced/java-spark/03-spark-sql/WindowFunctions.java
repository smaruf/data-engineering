package com.microsoft.spark.sql;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.expressions.WindowSpec;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * WindowFunctions demonstrates window functions including
 * ranking, aggregation, and analytical functions over windows.
 */
public class WindowFunctions {
    
    public static void main(String[] args) {
        WindowFunctions functions = new WindowFunctions();
        
        try {
            functions.demonstrateRankingFunctions();
            functions.demonstrateAggregateFunctions();
            functions.demonstrateAnalyticalFunctions();
            functions.demonstrateAdvancedWindows();
        } catch (Exception e) {
            System.err.println("Error in WindowFunctions: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Ranking Window Functions
     */
    public void demonstrateRankingFunctions() {
        System.out.println("\n=== Example 1: Ranking Window Functions ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Ranking Functions")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000, "2020-01-15"),
                new Employee(2, "Jane", "Engineering", 80000, "2019-03-20"),
                new Employee(3, "Bob", "Engineering", 75000, "2021-06-10"),
                new Employee(4, "Alice", "Marketing", 70000, "2020-08-05"),
                new Employee(5, "Charlie", "Marketing", 85000, "2018-11-12"),
                new Employee(6, "Diana", "Sales", 90000, "2019-04-18"),
                new Employee(7, "Eve", "Sales", 65000, "2021-02-22"),
                new Employee(8, "Frank", "Sales", 90000, "2020-09-30")
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Define window spec
            WindowSpec deptWindow = Window.partitionBy("department").orderBy(col("salary").desc());
            
            // row_number() - unique sequential number
            System.out.println("\nrow_number() - unique rank:");
            empDF.withColumn("row_num", row_number().over(deptWindow))
                .select("name", "department", "salary", "row_num")
                .show();
            
            // rank() - same rank for ties, gaps in ranking
            System.out.println("\nrank() - with gaps for ties:");
            empDF.withColumn("rank", rank().over(deptWindow))
                .select("name", "department", "salary", "rank")
                .show();
            
            // dense_rank() - no gaps in ranking
            System.out.println("\ndense_rank() - no gaps:");
            empDF.withColumn("dense_rank", dense_rank().over(deptWindow))
                .select("name", "department", "salary", "dense_rank")
                .show();
            
            // percent_rank() - relative rank
            System.out.println("\npercent_rank():");
            empDF.withColumn("percent_rank", percent_rank().over(deptWindow))
                .select("name", "department", "salary", "percent_rank")
                .show();
            
            // ntile() - divide into buckets
            System.out.println("\nntile(3) - divide into 3 buckets:");
            empDF.withColumn("ntile", ntile(3).over(deptWindow))
                .select("name", "department", "salary", "ntile")
                .show();
            
            // Top N per department
            System.out.println("\nTop 2 earners per department:");
            empDF.withColumn("rank", rank().over(deptWindow))
                .filter(col("rank").leq(2))
                .select("name", "department", "salary", "rank")
                .show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: Aggregate Window Functions
     */
    public void demonstrateAggregateFunctions() {
        System.out.println("\n=== Example 2: Aggregate Window Functions ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Aggregate Window Functions")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Sale> sales = Arrays.asList(
                new Sale(1, "2024-01-01", "Product A", 100, 1000),
                new Sale(2, "2024-01-02", "Product A", 150, 1500),
                new Sale(3, "2024-01-03", "Product A", 120, 1200),
                new Sale(4, "2024-01-01", "Product B", 200, 2000),
                new Sale(5, "2024-01-02", "Product B", 180, 1800),
                new Sale(6, "2024-01-03", "Product B", 220, 2200)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, Sale.class);
            
            // Window for running calculations
            WindowSpec runningWindow = Window.partitionBy("product")
                .orderBy("date")
                .rowsBetween(Window.unboundedPreceding(), Window.currentRow());
            
            // Running sum
            System.out.println("\nRunning sum:");
            salesDF.withColumn("running_total", sum("amount").over(runningWindow))
                .select("date", "product", "amount", "running_total")
                .show();
            
            // Running average
            System.out.println("\nRunning average:");
            salesDF.withColumn("running_avg", avg("amount").over(runningWindow))
                .select("date", "product", "amount", "running_avg")
                .show();
            
            // Cumulative count
            System.out.println("\nCumulative count:");
            salesDF.withColumn("cumulative_count", count("*").over(runningWindow))
                .select("date", "product", "amount", "cumulative_count")
                .show();
            
            // Moving average (last 2 rows)
            WindowSpec movingWindow = Window.partitionBy("product")
                .orderBy("date")
                .rowsBetween(-1, Window.currentRow());
            
            System.out.println("\nMoving average (2 periods):");
            salesDF.withColumn("moving_avg", avg("amount").over(movingWindow))
                .select("date", "product", "amount", "moving_avg")
                .show();
            
            // Difference from average
            WindowSpec productWindow = Window.partitionBy("product");
            
            System.out.println("\nDifference from product average:");
            salesDF.withColumn("product_avg", avg("amount").over(productWindow))
                .withColumn("diff_from_avg", col("amount") - col("product_avg"))
                .select("date", "product", "amount", "product_avg", "diff_from_avg")
                .show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: Analytical Window Functions
     */
    public void demonstrateAnalyticalFunctions() {
        System.out.println("\n=== Example 3: Analytical Window Functions ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Analytical Functions")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Sale> sales = Arrays.asList(
                new Sale(1, "2024-01-01", "Product A", 100, 1000),
                new Sale(2, "2024-01-02", "Product A", 150, 1500),
                new Sale(3, "2024-01-03", "Product A", 120, 1200),
                new Sale(4, "2024-01-04", "Product A", 180, 1800)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, Sale.class);
            
            WindowSpec orderWindow = Window.orderBy("date");
            
            // lag() - previous row value
            System.out.println("\nlag() - previous day amount:");
            salesDF.withColumn("prev_amount", lag("amount", 1).over(orderWindow))
                .withColumn("change", col("amount") - col("prev_amount"))
                .select("date", "amount", "prev_amount", "change")
                .show();
            
            // lead() - next row value
            System.out.println("\nlead() - next day amount:");
            salesDF.withColumn("next_amount", lead("amount", 1).over(orderWindow))
                .select("date", "amount", "next_amount")
                .show();
            
            // first() - first value in window
            WindowSpec unboundedWindow = Window.orderBy("date")
                .rowsBetween(Window.unboundedPreceding(), Window.unboundedFollowing());
            
            System.out.println("\nfirst() and last():");
            salesDF.withColumn("first_amount", first("amount").over(unboundedWindow))
                .withColumn("last_amount", last("amount").over(unboundedWindow))
                .select("date", "amount", "first_amount", "last_amount")
                .show();
            
            // Calculate percentage change
            System.out.println("\nPercentage change from previous day:");
            salesDF.withColumn("prev_amount", lag("amount", 1).over(orderWindow))
                .withColumn("pct_change", 
                    when(col("prev_amount").isNotNull(),
                        ((col("amount") - col("prev_amount")) / col("prev_amount") * 100))
                    .otherwise(null)
                )
                .select("date", "amount", "prev_amount", "pct_change")
                .show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: Advanced Window Operations
     */
    public void demonstrateAdvancedWindows() {
        System.out.println("\n=== Example 4: Advanced Window Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Advanced Windows")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000, "2020-01-15"),
                new Employee(2, "Jane", "Engineering", 80000, "2019-03-20"),
                new Employee(3, "Bob", "Engineering", 70000, "2021-06-10"),
                new Employee(4, "Alice", "Marketing", 85000, "2020-08-05"),
                new Employee(5, "Charlie", "Marketing", 90000, "2018-11-12")
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Multiple window specs
            WindowSpec deptSalaryWindow = Window.partitionBy("department")
                .orderBy(col("salary").desc());
            WindowSpec deptHireDateWindow = Window.partitionBy("department")
                .orderBy("hireDate");
            
            System.out.println("\nMultiple rankings:");
            empDF.withColumn("salary_rank", rank().over(deptSalaryWindow))
                .withColumn("seniority_rank", rank().over(deptHireDateWindow))
                .select("name", "department", "salary", "hireDate", 
                       "salary_rank", "seniority_rank")
                .show();
            
            // Range between
            WindowSpec rangeWindow = Window.partitionBy("department")
                .orderBy("salary")
                .rangeBetween(-5000, 5000);
            
            System.out.println("\nEmployees within $5000 salary range:");
            empDF.withColumn("similar_salary_count", count("*").over(rangeWindow) - 1)
                .select("name", "department", "salary", "similar_salary_count")
                .show();
            
            // Using SQL for window functions
            empDF.createOrReplaceTempView("employees");
            
            System.out.println("\nWindow functions using SQL:");
            spark.sql(
                "SELECT name, department, salary, " +
                "  RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank, " +
                "  DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dense_rank, " +
                "  ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as row_num " +
                "FROM employees"
            ).show();
            
            // Complex window calculation
            WindowSpec deptWindow = Window.partitionBy("department");
            WindowSpec runningWindow = Window.partitionBy("department")
                .orderBy("salary")
                .rowsBetween(Window.unboundedPreceding(), Window.currentRow());
            
            System.out.println("\nComplex window calculations:");
            empDF.withColumn("dept_avg", avg("salary").over(deptWindow))
                .withColumn("diff_from_avg", col("salary") - col("dept_avg"))
                .withColumn("running_sum", sum("salary").over(runningWindow))
                .withColumn("running_avg", avg("salary").over(runningWindow))
                .select("name", "department", "salary", "dept_avg", 
                       "diff_from_avg", "running_sum", "running_avg")
                .show();
            
        } finally {
            spark.stop();
        }
    }
    
    // Helper classes
    public static class Employee implements Serializable {
        private int id;
        private String name;
        private String department;
        private double salary;
        private String hireDate;
        
        public Employee() {}
        
        public Employee(int id, String name, String department, double salary, String hireDate) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
            this.hireDate = hireDate;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getDepartment() { return department; }
        public void setDepartment(String department) { this.department = department; }
        public double getSalary() { return salary; }
        public void setSalary(double salary) { this.salary = salary; }
        public String getHireDate() { return hireDate; }
        public void setHireDate(String hireDate) { this.hireDate = hireDate; }
    }
    
    public static class Sale implements Serializable {
        private int id;
        private String date;
        private String product;
        private int quantity;
        private double amount;
        
        public Sale() {}
        
        public Sale(int id, String date, String product, int quantity, double amount) {
            this.id = id;
            this.date = date;
            this.product = product;
            this.quantity = quantity;
            this.amount = amount;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getDate() { return date; }
        public void setDate(String date) { this.date = date; }
        public String getProduct() { return product; }
        public void setProduct(String product) { this.product = product; }
        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
    }
}
