package com.microsoft.spark.sql;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * SQLOperations demonstrates Spark SQL capabilities including
 * SQL queries, temporary views, and catalog operations.
 */
public class SQLOperations {
    
    public static void main(String[] args) {
        SQLOperations operations = new SQLOperations();
        
        try {
            operations.demonstrateBasicSQL();
            operations.demonstrateTemporaryViews();
            operations.demonstrateComplexSQL();
            operations.demonstrateCatalogOperations();
        } catch (Exception e) {
            System.err.println("Error in SQLOperations: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Basic SQL Queries
     */
    public void demonstrateBasicSQL() {
        System.out.println("\n=== Example 1: Basic SQL Queries ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic SQL")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create sample data
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000, 30),
                new Employee(2, "Jane Smith", "Marketing", 65000, 25),
                new Employee(3, "Bob Johnson", "Engineering", 80000, 35),
                new Employee(4, "Alice Williams", "Sales", 70000, 28),
                new Employee(5, "Charlie Brown", "Engineering", 72000, 32),
                new Employee(6, "Diana Prince", "Marketing", 90000, 40)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            
            // Create temporary view
            empDF.createOrReplaceTempView("employees");
            
            // SELECT query
            System.out.println("\nSELECT all employees:");
            spark.sql("SELECT * FROM employees").show();
            
            // SELECT with WHERE clause
            System.out.println("\nSELECT with WHERE:");
            spark.sql("SELECT name, department, salary FROM employees WHERE salary > 70000").show();
            
            // SELECT with ORDER BY
            System.out.println("\nSELECT with ORDER BY:");
            spark.sql(
                "SELECT name, salary FROM employees ORDER BY salary DESC"
            ).show();
            
            // SELECT with LIMIT
            System.out.println("\nSELECT with LIMIT:");
            spark.sql(
                "SELECT name, department FROM employees LIMIT 3"
            ).show();
            
            // SELECT DISTINCT
            System.out.println("\nSELECT DISTINCT departments:");
            spark.sql("SELECT DISTINCT department FROM employees").show();
            
            // Aggregate functions
            System.out.println("\nAggregate functions:");
            spark.sql(
                "SELECT " +
                "  COUNT(*) as total_employees, " +
                "  AVG(salary) as avg_salary, " +
                "  MIN(salary) as min_salary, " +
                "  MAX(salary) as max_salary " +
                "FROM employees"
            ).show();
            
            // GROUP BY
            System.out.println("\nGROUP BY department:");
            spark.sql(
                "SELECT department, COUNT(*) as count, AVG(salary) as avg_salary " +
                "FROM employees " +
                "GROUP BY department " +
                "ORDER BY avg_salary DESC"
            ).show();
            
            // HAVING clause
            System.out.println("\nGROUP BY with HAVING:");
            spark.sql(
                "SELECT department, COUNT(*) as count " +
                "FROM employees " +
                "GROUP BY department " +
                "HAVING count > 1"
            ).show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: Temporary and Global Temporary Views
     */
    public void demonstrateTemporaryViews() {
        System.out.println("\n=== Example 2: Temporary Views ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Temporary Views")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Product> products = Arrays.asList(
                new Product(1, "Laptop", 1200.0, "Electronics", 50),
                new Product(2, "Mouse", 25.0, "Electronics", 200),
                new Product(3, "Desk", 300.0, "Furniture", 30),
                new Product(4, "Chair", 150.0, "Furniture", 75)
            );
            
            Dataset<Row> productsDF = spark.createDataFrame(products, Product.class);
            
            // Create temporary view
            productsDF.createOrReplaceTempView("products");
            
            System.out.println("\nQuery temporary view:");
            spark.sql("SELECT * FROM products WHERE category = 'Electronics'").show();
            
            // Replace temporary view
            productsDF.filter(col("price").gt(100))
                .createOrReplaceTempView("products");
            
            System.out.println("\nQuery replaced view:");
            spark.sql("SELECT * FROM products").show();
            
            // Create global temporary view (accessible across sessions)
            productsDF.createGlobalTempView("global_products");
            
            System.out.println("\nQuery global temporary view:");
            spark.sql("SELECT * FROM global_temp.global_products").show();
            
            // Create view from SQL query
            spark.sql(
                "CREATE OR REPLACE TEMP VIEW expensive_products AS " +
                "SELECT * FROM products WHERE price > 200"
            );
            
            System.out.println("\nQuery view created from SQL:");
            spark.sql("SELECT * FROM expensive_products").show();
            
            // List all tables
            System.out.println("\nList all tables:");
            spark.sql("SHOW TABLES").show();
            
            // Drop temporary view
            spark.catalog().dropTempView("products");
            System.out.println("\nAfter dropping 'products' view:");
            spark.sql("SHOW TABLES").show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: Complex SQL Queries
     */
    public void demonstrateComplexSQL() {
        System.out.println("\n=== Example 3: Complex SQL Queries ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Complex SQL")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create employees table
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John Doe", "Engineering", 75000, 30),
                new Employee(2, "Jane Smith", "Marketing", 65000, 25),
                new Employee(3, "Bob Johnson", "Engineering", 80000, 35),
                new Employee(4, "Alice Williams", "Sales", 70000, 28)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            empDF.createOrReplaceTempView("employees");
            
            // Create departments table
            List<Department> departments = Arrays.asList(
                new Department(1, "Engineering", "Building A", "John Doe"),
                new Department(2, "Marketing", "Building B", "Jane Smith"),
                new Department(3, "Sales", "Building C", "Alice Williams")
            );
            
            Dataset<Row> deptDF = spark.createDataFrame(departments, Department.class);
            deptDF.createOrReplaceTempView("departments");
            
            // JOIN query
            System.out.println("\nJOIN query:");
            spark.sql(
                "SELECT e.name, e.salary, d.departmentName, d.location " +
                "FROM employees e " +
                "JOIN departments d ON e.department = d.departmentName"
            ).show();
            
            // LEFT JOIN
            System.out.println("\nLEFT JOIN:");
            spark.sql(
                "SELECT e.name, e.department, d.location " +
                "FROM employees e " +
                "LEFT JOIN departments d ON e.department = d.departmentName"
            ).show();
            
            // Subquery
            System.out.println("\nSubquery - employees with above average salary:");
            spark.sql(
                "SELECT name, salary FROM employees " +
                "WHERE salary > (SELECT AVG(salary) FROM employees)"
            ).show();
            
            // CTE (Common Table Expression)
            System.out.println("\nCTE query:");
            spark.sql(
                "WITH dept_stats AS ( " +
                "  SELECT department, AVG(salary) as avg_salary, COUNT(*) as count " +
                "  FROM employees GROUP BY department " +
                ") " +
                "SELECT * FROM dept_stats WHERE count > 1"
            ).show();
            
            // CASE WHEN
            System.out.println("\nCASE WHEN:");
            spark.sql(
                "SELECT name, salary, " +
                "  CASE " +
                "    WHEN salary >= 80000 THEN 'High' " +
                "    WHEN salary >= 70000 THEN 'Medium' " +
                "    ELSE 'Low' " +
                "  END as salary_band " +
                "FROM employees"
            ).show();
            
            // UNION
            List<Employee> newEmployees = Arrays.asList(
                new Employee(5, "Eve Davis", "Engineering", 78000, 29),
                new Employee(6, "Frank Miller", "Sales", 72000, 31)
            );
            
            Dataset<Row> newEmpDF = spark.createDataFrame(newEmployees, Employee.class);
            newEmpDF.createOrReplaceTempView("new_employees");
            
            System.out.println("\nUNION:");
            spark.sql(
                "SELECT name, department FROM employees " +
                "UNION " +
                "SELECT name, department FROM new_employees"
            ).show();
            
            // Window function in SQL
            System.out.println("\nWindow function - rank by salary:");
            spark.sql(
                "SELECT name, department, salary, " +
                "  RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank " +
                "FROM employees"
            ).show();
            
            // String functions
            System.out.println("\nString functions:");
            spark.sql(
                "SELECT " +
                "  UPPER(name) as upper_name, " +
                "  LOWER(department) as lower_dept, " +
                "  CONCAT(name, ' - ', department) as full_info, " +
                "  SUBSTRING(name, 1, 4) as short_name " +
                "FROM employees LIMIT 3"
            ).show(false);
            
            // Date functions
            System.out.println("\nDate functions:");
            spark.sql(
                "SELECT " +
                "  CURRENT_DATE() as today, " +
                "  CURRENT_TIMESTAMP() as now, " +
                "  DATE_ADD(CURRENT_DATE(), 30) as month_later, " +
                "  YEAR(CURRENT_DATE()) as year"
            ).show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: Catalog Operations
     */
    public void demonstrateCatalogOperations() {
        System.out.println("\n=== Example 4: Catalog Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Catalog Operations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create sample data and views
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000, 30),
                new Employee(2, "Jane", "Marketing", 65000, 25)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            empDF.createOrReplaceTempView("employees");
            empDF.createGlobalTempView("global_employees");
            
            // List databases
            System.out.println("\nList databases:");
            spark.catalog().listDatabases().show(false);
            
            // List tables
            System.out.println("\nList tables:");
            spark.catalog().listTables().show(false);
            
            // List columns
            System.out.println("\nList columns in employees:");
            spark.catalog().listColumns("employees").show(false);
            
            // List functions
            System.out.println("\nList some functions:");
            spark.catalog().listFunctions().select("name", "description")
                .filter(col("name").like("avg%"))
                .show(false);
            
            // Get current database
            System.out.println("\nCurrent database: " + spark.catalog().currentDatabase());
            
            // Check if table exists
            boolean exists = spark.catalog().tableExists("employees");
            System.out.println("\nTable 'employees' exists: " + exists);
            
            // Cache table
            spark.catalog().cacheTable("employees");
            System.out.println("\nTable 'employees' cached: " + 
                spark.catalog().isCached("employees"));
            
            // Uncache table
            spark.catalog().uncacheTable("employees");
            System.out.println("Table 'employees' cached after uncaching: " + 
                spark.catalog().isCached("employees"));
            
            // Clear cache
            spark.catalog().clearCache();
            
            // Refresh table
            spark.catalog().refreshTable("employees");
            
            // Using SQL for catalog operations
            System.out.println("\nDESCRIBE table:");
            spark.sql("DESCRIBE employees").show();
            
            System.out.println("\nSHOW COLUMNS:");
            spark.sql("SHOW COLUMNS IN employees").show();
            
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
        private int age;
        
        public Employee() {}
        
        public Employee(int id, String name, String department, double salary, int age) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
            this.age = age;
        }
        
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
    }
    
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
    
    public static class Department implements Serializable {
        private int id;
        private String departmentName;
        private String location;
        private String manager;
        
        public Department() {}
        
        public Department(int id, String departmentName, String location, String manager) {
            this.id = id;
            this.departmentName = departmentName;
            this.location = location;
            this.manager = manager;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getDepartmentName() { return departmentName; }
        public void setDepartmentName(String departmentName) { this.departmentName = departmentName; }
        public String getLocation() { return location; }
        public void setLocation(String location) { this.location = location; }
        public String getManager() { return manager; }
        public void setManager(String manager) { this.manager = manager; }
    }
}
