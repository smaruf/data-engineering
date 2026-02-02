package com.microsoft.spark.basics;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoder;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * DatasetOperations demonstrates strongly-typed Dataset operations
 * with custom encoders and type-safe transformations.
 */
public class DatasetOperations {
    
    public static void main(String[] args) {
        DatasetOperations operations = new DatasetOperations();
        
        try {
            operations.createTypedDatasets();
            operations.typedTransformations();
            operations.workWithEncoders();
            operations.datasetVsDataFrame();
        } catch (Exception e) {
            System.err.println("Error in DatasetOperations: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Creating Typed Datasets
     */
    public void createTypedDatasets() {
        System.out.println("\n=== Example 1: Creating Typed Datasets ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Typed Datasets")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create Dataset from Java objects
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000.0, 5),
                new Employee(2, "Jane Smith", "Marketing", 65000.0, 3),
                new Employee(3, "Bob Johnson", "Engineering", 80000.0, 7),
                new Employee(4, "Alice Williams", "Sales", 70000.0, 4)
            );
            
            // Typed Dataset
            Dataset<Employee> employeeDS = spark.createDataset(
                employees, 
                Encoders.bean(Employee.class)
            );
            
            System.out.println("\nTyped Dataset of Employees:");
            employeeDS.show();
            
            System.out.println("\nSchema:");
            employeeDS.printSchema();
            
            // Dataset of primitives
            Dataset<Integer> numbers = spark.createDataset(
                Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                Encoders.INT()
            );
            
            System.out.println("\nDataset of Integers:");
            numbers.show();
            
            // Dataset of Strings
            Dataset<String> names = spark.createDataset(
                Arrays.asList("Alice", "Bob", "Charlie", "David"),
                Encoders.STRING()
            );
            
            System.out.println("\nDataset of Strings:");
            names.show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: Typed Transformations
     */
    public void typedTransformations() {
        System.out.println("\n=== Example 2: Typed Transformations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Typed Transformations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000.0, 5),
                new Employee(2, "Jane Smith", "Marketing", 65000.0, 3),
                new Employee(3, "Bob Johnson", "Engineering", 80000.0, 7),
                new Employee(4, "Alice Williams", "Sales", 70000.0, 4),
                new Employee(5, "Charlie Brown", "Engineering", 72000.0, 6)
            );
            
            Dataset<Employee> employeeDS = spark.createDataset(
                employees,
                Encoders.bean(Employee.class)
            );
            
            // map: Type-safe transformation
            System.out.println("\nMap to get names:");
            Dataset<String> names = employeeDS.map(
                emp -> emp.getName(),
                Encoders.STRING()
            );
            names.show();
            
            // map: Calculate annual bonus
            System.out.println("\nMap to calculate bonuses:");
            Dataset<Double> bonuses = employeeDS.map(
                emp -> emp.getSalary() * 0.1,
                Encoders.DOUBLE()
            );
            bonuses.show();
            
            // filter: Type-safe filtering
            System.out.println("\nFilter employees in Engineering:");
            Dataset<Employee> engineers = employeeDS.filter(
                emp -> emp.getDepartment().equals("Engineering")
            );
            engineers.show();
            
            // filter: High earners
            System.out.println("\nFilter salary > 72000:");
            Dataset<Employee> highEarners = employeeDS.filter(
                emp -> emp.getSalary() > 72000
            );
            highEarners.show();
            
            // flatMap: Create multiple records
            System.out.println("\nFlatMap to create employee-skill pairs:");
            Dataset<String> skills = employeeDS.flatMap(
                emp -> Arrays.asList(
                    emp.getName() + " - Skill 1",
                    emp.getName() + " - Skill 2"
                ).iterator(),
                Encoders.STRING()
            );
            skills.show();
            
            // mapPartitions: Process partitions
            System.out.println("\nMap partitions to count employees per partition:");
            Dataset<Integer> partitionCounts = employeeDS.mapPartitions(
                iterator -> {
                    int count = 0;
                    while (iterator.hasNext()) {
                        iterator.next();
                        count++;
                    }
                    return Arrays.asList(count).iterator();
                },
                Encoders.INT()
            );
            partitionCounts.show();
            
            // reduce: Aggregate
            System.out.println("\nReduce to find total experience:");
            Integer totalExperience = employeeDS.map(
                emp -> emp.getYearsOfExperience(),
                Encoders.INT()
            ).reduce((a, b) -> a + b);
            System.out.println("Total years of experience: " + totalExperience);
            
            // groupByKey: Group and aggregate
            System.out.println("\nGroup by department:");
            employeeDS.groupByKey(
                emp -> emp.getDepartment(),
                Encoders.STRING()
            ).count().show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: Working with Encoders
     */
    public void workWithEncoders() {
        System.out.println("\n=== Example 3: Working with Encoders ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Encoders")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Primitive encoders
            Encoder<Integer> intEncoder = Encoders.INT();
            Encoder<Long> longEncoder = Encoders.LONG();
            Encoder<Double> doubleEncoder = Encoders.DOUBLE();
            Encoder<String> stringEncoder = Encoders.STRING();
            Encoder<Boolean> booleanEncoder = Encoders.BOOLEAN();
            
            // Bean encoder for custom class
            Encoder<Employee> employeeEncoder = Encoders.bean(Employee.class);
            
            // Tuple encoders
            Encoder<scala.Tuple2<String, Integer>> tuple2Encoder = 
                Encoders.tuple(Encoders.STRING(), Encoders.INT());
            
            // Create Dataset with tuple encoder
            Dataset<scala.Tuple2<String, Integer>> tupleDS = spark.createDataset(
                Arrays.asList(
                    new scala.Tuple2<>("Engineering", 3),
                    new scala.Tuple2<>("Marketing", 2),
                    new scala.Tuple2<>("Sales", 1)
                ),
                tuple2Encoder
            );
            
            System.out.println("\nDataset with Tuple2 encoder:");
            tupleDS.show();
            
            // Complex object with encoder
            List<Product> products = Arrays.asList(
                new Product(1, "Laptop", 1200.0, "Electronics"),
                new Product(2, "Mouse", 25.0, "Electronics"),
                new Product(3, "Desk", 300.0, "Furniture"),
                new Product(4, "Chair", 150.0, "Furniture")
            );
            
            Dataset<Product> productDS = spark.createDataset(
                products,
                Encoders.bean(Product.class)
            );
            
            System.out.println("\nProduct Dataset:");
            productDS.show();
            
            // Transform with type safety
            Dataset<ProductSummary> summaryDS = productDS.map(
                product -> new ProductSummary(
                    product.getName(),
                    product.getCategory(),
                    product.getPrice() > 100 ? "Premium" : "Standard"
                ),
                Encoders.bean(ProductSummary.class)
            );
            
            System.out.println("\nProduct Summary:");
            summaryDS.show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: Dataset vs DataFrame comparison
     */
    public void datasetVsDataFrame() {
        System.out.println("\n=== Example 4: Dataset vs DataFrame ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Dataset vs DataFrame")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000.0, 5),
                new Employee(2, "Jane Smith", "Marketing", 65000.0, 3),
                new Employee(3, "Bob Johnson", "Engineering", 80000.0, 7)
            );
            
            // Typed Dataset
            Dataset<Employee> employeeDS = spark.createDataset(
                employees,
                Encoders.bean(Employee.class)
            );
            
            System.out.println("\n--- Typed Dataset Operations ---");
            
            // Type-safe operations
            Dataset<String> namesDS = employeeDS.map(
                emp -> emp.getName().toUpperCase(),
                Encoders.STRING()
            );
            System.out.println("\nType-safe map to uppercase names:");
            namesDS.show();
            
            // Compile-time type checking
            Dataset<Employee> filteredDS = employeeDS.filter(
                emp -> emp.getSalary() > 70000  // Type-safe
            );
            System.out.println("\nType-safe filter:");
            filteredDS.show();
            
            // Convert to DataFrame (untyped)
            org.apache.spark.sql.Dataset<org.apache.spark.sql.Row> df = employeeDS.toDF();
            
            System.out.println("\n--- DataFrame Operations (Untyped) ---");
            
            // Untyped operations
            df.select("name", "salary")
                .filter(col("salary").gt(70000))
                .show();
            
            // Convert DataFrame back to Dataset
            Dataset<Employee> backToDS = df.as(Encoders.bean(Employee.class));
            
            System.out.println("\nConverted back to Dataset:");
            backToDS.show();
            
            // Performance comparison example
            System.out.println("\n--- Performance Characteristics ---");
            System.out.println("Dataset: Type-safe at compile time, optimized by Catalyst");
            System.out.println("DataFrame: Flexible, optimized by Catalyst, runtime type checking");
            
            // When to use Dataset vs DataFrame
            System.out.println("\n--- Use Cases ---");
            System.out.println("Use Dataset when:");
            System.out.println("  - You need type safety");
            System.out.println("  - Working with domain objects");
            System.out.println("  - Compile-time error detection is important");
            
            System.out.println("\nUse DataFrame when:");
            System.out.println("  - Working with semi-structured data");
            System.out.println("  - Need maximum flexibility");
            System.out.println("  - Using Spark SQL extensively");
            
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
        private int yearsOfExperience;
        
        public Employee() {}
        
        public Employee(int id, String name, String department, double salary, int yearsOfExperience) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
            this.yearsOfExperience = yearsOfExperience;
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
        public int getYearsOfExperience() { return yearsOfExperience; }
        public void setYearsOfExperience(int yearsOfExperience) { this.yearsOfExperience = yearsOfExperience; }
    }
    
    public static class Product implements Serializable {
        private int id;
        private String name;
        private double price;
        private String category;
        
        public Product() {}
        
        public Product(int id, String name, double price, String category) {
            this.id = id;
            this.name = name;
            this.price = price;
            this.category = category;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getPrice() { return price; }
        public void setPrice(double price) { this.price = price; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
    }
    
    public static class ProductSummary implements Serializable {
        private String name;
        private String category;
        private String priceCategory;
        
        public ProductSummary() {}
        
        public ProductSummary(String name, String category, String priceCategory) {
            this.name = name;
            this.category = category;
            this.priceCategory = priceCategory;
        }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        public String getPriceCategory() { return priceCategory; }
        public void setPriceCategory(String priceCategory) { this.priceCategory = priceCategory; }
    }
}
