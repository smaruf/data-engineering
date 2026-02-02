package com.microsoft.spark.transformations;

import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Encoders;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * FilterTransform demonstrates various filtering and selection operations
 * including filter, where, distinct, and dropDuplicates.
 */
public class FilterTransform {
    
    public static void main(String[] args) {
        FilterTransform transform = new FilterTransform();
        
        try {
            transform.demonstrateBasicFiltering();
            transform.demonstrateComplexFiltering();
            transform.demonstrateDistinctOperations();
            transform.demonstrateWhereConditions();
        } catch (Exception e) {
            System.err.println("Error in FilterTransform: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Basic Filtering
     */
    public void demonstrateBasicFiltering() {
        System.out.println("\n=== Example 1: Basic Filtering ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic Filtering")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // RDD filtering
            System.out.println("\n--- RDD Filtering ---");
            
            List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
            JavaRDD<Integer> numbersRDD = sc.parallelize(numbers);
            
            // Filter even numbers
            JavaRDD<Integer> evens = numbersRDD.filter(x -> x % 2 == 0);
            System.out.println("Even numbers: " + evens.collect());
            
            // Filter greater than 5
            JavaRDD<Integer> greaterThan5 = numbersRDD.filter(x -> x > 5);
            System.out.println("Numbers > 5: " + greaterThan5.collect());
            
            // Filter in range
            JavaRDD<Integer> inRange = numbersRDD.filter(x -> x >= 3 && x <= 7);
            System.out.println("Numbers in range [3,7]: " + inRange.collect());
            
            // DataFrame filtering
            System.out.println("\n--- DataFrame Filtering ---");
            
            List<Product> products = Arrays.asList(
                new Product(1, "Laptop", 1200.0, "Electronics", 50),
                new Product(2, "Mouse", 25.0, "Electronics", 200),
                new Product(3, "Desk", 300.0, "Furniture", 30),
                new Product(4, "Chair", 150.0, "Furniture", 75),
                new Product(5, "Monitor", 400.0, "Electronics", 60),
                new Product(6, "Keyboard", 80.0, "Electronics", 150)
            );
            
            Dataset<Row> productsDF = spark.createDataFrame(products, Product.class);
            
            System.out.println("\nOriginal products:");
            productsDF.show();
            
            // Filter by price
            System.out.println("\nProducts with price > 100:");
            productsDF.filter(col("price").gt(100)).show();
            
            // Filter by category
            System.out.println("\nElectronics products:");
            productsDF.filter(col("category").equalTo("Electronics")).show();
            
            // Filter by stock
            System.out.println("\nLow stock products (< 100):");
            productsDF.filter(col("stock").lt(100)).show();
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 2: Complex Filtering
     */
    public void demonstrateComplexFiltering() {
        System.out.println("\n=== Example 2: Complex Filtering ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Complex Filtering")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000, 30, "Manager"),
                new Employee(2, "Jane Smith", "Marketing", 65000, 25, "Associate"),
                new Employee(3, "Bob Johnson", "Engineering", 80000, 35, "Senior"),
                new Employee(4, "Alice Williams", "Sales", 70000, 28, "Manager"),
                new Employee(5, "Charlie Brown", "Engineering", 72000, 32, "Associate"),
                new Employee(6, "Diana Prince", "Marketing", 90000, 40, "Director"),
                new Employee(7, "Eve Davis", "Sales", 68000, 26, "Associate"),
                new Employee(8, "Frank Miller", "Engineering", 95000, 38, "Director")
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            System.out.println("\nOriginal employees:");
            empDF.show();
            
            // Multiple AND conditions
            System.out.println("\nEngineering employees with salary > 75000:");
            empDF.filter(
                col("department").equalTo("Engineering")
                .and(col("salary").gt(75000))
            ).show();
            
            // Multiple OR conditions
            System.out.println("\nManagers OR Directors:");
            empDF.filter(
                col("position").equalTo("Manager")
                .or(col("position").equalTo("Director"))
            ).show();
            
            // Combined AND/OR conditions
            System.out.println("\n(Engineering AND salary > 80000) OR (Position = Director):");
            empDF.filter(
                col("department").equalTo("Engineering")
                    .and(col("salary").gt(80000))
                .or(col("position").equalTo("Director"))
            ).show();
            
            // NOT condition
            System.out.println("\nNon-Engineering employees:");
            empDF.filter(not(col("department").equalTo("Engineering"))).show();
            
            // IN condition
            System.out.println("\nEmployees in Engineering or Marketing:");
            empDF.filter(col("department").isin("Engineering", "Marketing")).show();
            
            // BETWEEN condition
            System.out.println("\nEmployees with age between 28 and 35:");
            empDF.filter(col("age").between(28, 35)).show();
            
            // IS NULL / IS NOT NULL
            empDF = empDF.withColumn("bonus", 
                when(col("salary").gt(80000), col("salary").multiply(0.15))
                .when(col("salary").gt(70000), col("salary").multiply(0.10))
                .otherwise(null)
            );
            
            System.out.println("\nEmployees with bonus:");
            empDF.filter(col("bonus").isNotNull()).show();
            
            System.out.println("\nEmployees without bonus:");
            empDF.filter(col("bonus").isNull()).show();
            
            // String operations in filter
            System.out.println("\nNames starting with 'J':");
            empDF.filter(col("name").startsWith("J")).show();
            
            System.out.println("\nNames containing 'son':");
            empDF.filter(col("name").contains("son")).show();
            
            System.out.println("\nNames ending with 'er':");
            empDF.filter(col("name").endsWith("er")).show();
            
            // LIKE pattern
            System.out.println("\nNames matching pattern:");
            empDF.filter(col("name").like("%o%")).show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: Distinct Operations
     */
    public void demonstrateDistinctOperations() {
        System.out.println("\n=== Example 3: Distinct Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Distinct Operations")
                .master("local[*]")
                .getOrCreate();
        
        JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        
        try {
            // RDD distinct
            System.out.println("\n--- RDD Distinct ---");
            
            List<Integer> numbersWithDuplicates = Arrays.asList(
                1, 2, 3, 2, 4, 3, 5, 1, 6, 4, 7, 5, 8, 6, 9, 7, 10
            );
            
            JavaRDD<Integer> numbersRDD = sc.parallelize(numbersWithDuplicates);
            JavaRDD<Integer> distinctNumbers = numbersRDD.distinct();
            
            System.out.println("Original: " + numbersRDD.collect());
            System.out.println("Distinct: " + distinctNumbers.collect());
            System.out.println("Original count: " + numbersRDD.count());
            System.out.println("Distinct count: " + distinctNumbers.count());
            
            // DataFrame distinct
            System.out.println("\n--- DataFrame Distinct ---");
            
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000, 30, "Manager"),
                new Employee(2, "Jane", "Marketing", 65000, 25, "Associate"),
                new Employee(3, "Bob", "Engineering", 80000, 35, "Senior"),
                new Employee(4, "Alice", "Marketing", 70000, 28, "Manager"),
                new Employee(5, "Charlie", "Engineering", 72000, 32, "Associate")
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Distinct departments
            System.out.println("\nDistinct departments:");
            empDF.select("department").distinct().show();
            
            // Distinct positions
            System.out.println("\nDistinct positions:");
            empDF.select("position").distinct().show();
            
            // Distinct combinations
            System.out.println("\nDistinct department-position combinations:");
            empDF.select("department", "position").distinct().show();
            
            // Count distinct
            System.out.println("\nCount of distinct departments:");
            empDF.select(countDistinct("department").alias("distinct_departments")).show();
            
            // dropDuplicates - same as distinct
            System.out.println("\nDrop duplicates on department:");
            empDF.dropDuplicates("department").show();
            
            // dropDuplicates on multiple columns
            System.out.println("\nDrop duplicates on department and position:");
            empDF.dropDuplicates("department", "position")
                .select("department", "position")
                .show();
            
            // Dataset distinct
            System.out.println("\n--- Dataset Distinct ---");
            
            Dataset<String> departments = empDF.select("department")
                .as(Encoders.STRING());
            
            Dataset<String> distinctDepts = departments.distinct();
            System.out.println("\nDistinct departments (Dataset):");
            distinctDepts.show();
            
        } finally {
            sc.close();
            spark.stop();
        }
    }
    
    /**
     * Example 4: Where Conditions (SQL-style)
     */
    public void demonstrateWhereConditions() {
        System.out.println("\n=== Example 4: Where Conditions ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Where Conditions")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Sale> sales = Arrays.asList(
                new Sale(1, "2024-01-15", "Product A", 1200.0, 2, "Online"),
                new Sale(2, "2024-01-16", "Product B", 800.0, 1, "Store"),
                new Sale(3, "2024-01-17", "Product A", 1500.0, 3, "Online"),
                new Sale(4, "2024-01-18", "Product C", 2000.0, 1, "Online"),
                new Sale(5, "2024-01-19", "Product B", 900.0, 2, "Store"),
                new Sale(6, "2024-01-20", "Product A", 1100.0, 1, "Store")
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, Sale.class);
            
            System.out.println("\nOriginal sales:");
            salesDF.show();
            
            // where with SQL expression
            System.out.println("\nOnline sales:");
            salesDF.where("channel = 'Online'").show();
            
            // where with multiple conditions
            System.out.println("\nOnline sales of Product A:");
            salesDF.where("channel = 'Online' AND product = 'Product A'").show();
            
            // where with comparison operators
            System.out.println("\nHigh-value sales (> 1500):");
            salesDF.where("amount > 1500").show();
            
            // where with IN clause
            System.out.println("\nProduct A or B sales:");
            salesDF.where("product IN ('Product A', 'Product B')").show();
            
            // where with LIKE
            System.out.println("\nProducts starting with 'Product A':");
            salesDF.where("product LIKE 'Product A%'").show();
            
            // Combining filter and where (they're equivalent)
            System.out.println("\nUsing both filter and where:");
            salesDF
                .filter(col("channel").equalTo("Online"))
                .where("amount > 1000")
                .show();
            
            // Add calculated column and filter
            System.out.println("\nTotal sales with discount > 100:");
            salesDF
                .withColumn("total", col("amount").multiply(col("quantity")))
                .withColumn("discount", col("total").multiply(0.1))
                .where("discount > 100")
                .show();
            
            // Complex where with subquery-like logic
            double avgAmount = salesDF.agg(avg("amount")).first().getDouble(0);
            System.out.println("\nSales above average (" + avgAmount + "):");
            salesDF.where(col("amount").gt(avgAmount)).show();
            
        } finally {
            spark.stop();
        }
    }
    
    // Helper classes
    public static class Product implements Serializable {
        private int id;
        private String name;
        private double price;
        private String category;
        private int stock;
        
        public Product() {}
        
        public Product(int id, String name, double price, String category, int stock) {
            this.id = id;
            this.name = name;
            this.price = price;
            this.category = category;
            this.stock = stock;
        }
        
        // Getters and Setters
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getPrice() { return price; }
        public void setPrice(double price) { this.price = price; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        public int getStock() { return stock; }
        public void setStock(int stock) { this.stock = stock; }
    }
    
    public static class Employee implements Serializable {
        private int id;
        private String name;
        private String department;
        private double salary;
        private int age;
        private String position;
        
        public Employee() {}
        
        public Employee(int id, String name, String department, double salary, int age, String position) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
            this.age = age;
            this.position = position;
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
        public int getAge() { return age; }
        public void setAge(int age) { this.age = age; }
        public String getPosition() { return position; }
        public void setPosition(String position) { this.position = position; }
    }
    
    public static class Sale implements Serializable {
        private int id;
        private String date;
        private String product;
        private double amount;
        private int quantity;
        private String channel;
        
        public Sale() {}
        
        public Sale(int id, String date, String product, double amount, int quantity, String channel) {
            this.id = id;
            this.date = date;
            this.product = product;
            this.amount = amount;
            this.quantity = quantity;
            this.channel = channel;
        }
        
        // Getters and Setters
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getDate() { return date; }
        public void setDate(String date) { this.date = date; }
        public String getProduct() { return product; }
        public void setProduct(String product) { this.product = product; }
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }
        public String getChannel() { return channel; }
        public void setChannel(String channel) { this.channel = channel; }
    }
}
