package com.microsoft.spark.sql;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.api.java.UDF1;
import org.apache.spark.sql.api.java.UDF2;
import org.apache.spark.sql.api.java.UDF3;
import org.apache.spark.sql.types.DataTypes;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

/**
 * UDFExample demonstrates user-defined functions (UDFs) in Spark
 * including scalar UDFs and UDAFs.
 */
public class UDFExample {
    
    public static void main(String[] args) {
        UDFExample example = new UDFExample();
        
        try {
            example.demonstrateBasicUDFs();
            example.demonstrateComplexUDFs();
            example.demonstrateUDFWithSQL();
            example.demonstrateMultipleParameterUDFs();
        } catch (Exception e) {
            System.err.println("Error in UDFExample: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Basic UDFs
     */
    public void demonstrateBasicUDFs() {
        System.out.println("\n=== Example 1: Basic UDFs ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic UDFs")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Register UDF - String to uppercase
            spark.udf().register("toUpper", 
                (UDF1<String, String>) String::toUpperCase, 
                DataTypes.StringType);
            
            // Register UDF - double salary
            spark.udf().register("doubleSalary", 
                (UDF1<Double, Double>) salary -> salary * 2, 
                DataTypes.DoubleType);
            
            // Register UDF - calculate bonus
            spark.udf().register("calculateBonus", 
                (UDF1<Double, Double>) salary -> {
                    if (salary > 80000) return salary * 0.15;
                    else if (salary > 60000) return salary * 0.10;
                    else return salary * 0.05;
                }, 
                DataTypes.DoubleType);
            
            List<Employee> employees = Arrays.asList(
                new Employee(1, "john doe", 75000),
                new Employee(2, "jane smith", 85000),
                new Employee(3, "bob johnson", 55000)
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, Employee.class);
            empDF.createOrReplaceTempView("employees");
            
            // Use UDF in SQL
            System.out.println("\nUsing UDFs in SQL:");
            spark.sql(
                "SELECT " +
                "  id, " +
                "  name, " +
                "  toUpper(name) as upper_name, " +
                "  salary, " +
                "  doubleSalary(salary) as doubled_salary, " +
                "  calculateBonus(salary) as bonus " +
                "FROM employees"
            ).show();
            
            // Use UDF in DataFrame API
            System.out.println("\nUsing UDFs in DataFrame API:");
            empDF.withColumn("upper_name", callUDF("toUpper", col("name")))
                .withColumn("bonus", callUDF("calculateBonus", col("salary")))
                .show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: Complex UDFs
     */
    public void demonstrateComplexUDFs() {
        System.out.println("\n=== Example 2: Complex UDFs ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Complex UDFs")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // UDF to categorize salary
            spark.udf().register("categorizeSalary", 
                (UDF1<Double, String>) salary -> {
                    if (salary >= 100000) return "Executive";
                    else if (salary >= 80000) return "Senior";
                    else if (salary >= 60000) return "Mid-Level";
                    else return "Entry-Level";
                }, 
                DataTypes.StringType);
            
            // UDF to extract domain from email
            spark.udf().register("extractDomain", 
                (UDF1<String, String>) email -> {
                    if (email == null || !email.contains("@")) return "N/A";
                    return email.substring(email.indexOf("@") + 1);
                }, 
                DataTypes.StringType);
            
            // UDF to format phone number
            spark.udf().register("formatPhone", 
                (UDF1<String, String>) phone -> {
                    if (phone == null || phone.length() != 10) return phone;
                    return String.format("(%s) %s-%s", 
                        phone.substring(0, 3),
                        phone.substring(3, 6),
                        phone.substring(6));
                }, 
                DataTypes.StringType);
            
            // UDF to calculate tax
            spark.udf().register("calculateTax", 
                (UDF1<Double, Double>) salary -> {
                    if (salary <= 40000) return salary * 0.15;
                    else if (salary <= 80000) return 40000 * 0.15 + (salary - 40000) * 0.25;
                    else return 40000 * 0.15 + 40000 * 0.25 + (salary - 80000) * 0.35;
                }, 
                DataTypes.DoubleType);
            
            List<EmployeeDetail> employees = Arrays.asList(
                new EmployeeDetail(1, "John", 75000, "john@company.com", "5551234567"),
                new EmployeeDetail(2, "Jane", 95000, "jane@startup.com", "5559876543"),
                new EmployeeDetail(3, "Bob", 55000, "bob@enterprise.net", "5555555555")
            );
            
            Dataset<Row> empDF = spark.createDataFrame(employees, EmployeeDetail.class);
            empDF.createOrReplaceTempView("employees");
            
            System.out.println("\nComplex UDF results:");
            spark.sql(
                "SELECT " +
                "  name, " +
                "  salary, " +
                "  categorizeSalary(salary) as level, " +
                "  calculateTax(salary) as tax, " +
                "  email, " +
                "  extractDomain(email) as domain, " +
                "  phone, " +
                "  formatPhone(phone) as formatted_phone " +
                "FROM employees"
            ).show(false);
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: UDFs with SQL expressions
     */
    public void demonstrateUDFWithSQL() {
        System.out.println("\n=== Example 3: UDFs with SQL ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("UDF with SQL")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // UDF for string manipulation
            spark.udf().register("titleCase", 
                (UDF1<String, String>) str -> {
                    if (str == null) return null;
                    String[] words = str.toLowerCase().split(" ");
                    StringBuilder result = new StringBuilder();
                    for (String word : words) {
                        if (word.length() > 0) {
                            result.append(Character.toUpperCase(word.charAt(0)))
                                  .append(word.substring(1))
                                  .append(" ");
                        }
                    }
                    return result.toString().trim();
                }, 
                DataTypes.StringType);
            
            // UDF for date calculations
            spark.udf().register("yearsSince", 
                (UDF1<String, Integer>) date -> {
                    if (date == null) return null;
                    int year = Integer.parseInt(date.substring(0, 4));
                    return 2024 - year;
                }, 
                DataTypes.IntegerType);
            
            List<Product> products = Arrays.asList(
                new Product(1, "laptop computer", "2022-01-15", 1200.0),
                new Product(2, "wireless mouse", "2023-06-20", 25.0),
                new Product(3, "office desk", "2021-03-10", 300.0)
            );
            
            Dataset<Row> productsDF = spark.createDataFrame(products, Product.class);
            productsDF.createOrReplaceTempView("products");
            
            System.out.println("\nUDF in SQL expressions:");
            spark.sql(
                "SELECT " +
                "  name, " +
                "  titleCase(name) as formatted_name, " +
                "  releaseDate, " +
                "  yearsSince(releaseDate) as years_old, " +
                "  price, " +
                "  CASE WHEN yearsSince(releaseDate) > 2 THEN 'Old' ELSE 'Recent' END as category " +
                "FROM products"
            ).show(false);
            
            // Combining UDFs with aggregations
            System.out.println("\nUDF with aggregations:");
            spark.sql(
                "SELECT " +
                "  CASE WHEN yearsSince(releaseDate) > 2 THEN 'Old' ELSE 'Recent' END as age_category, " +
                "  COUNT(*) as count, " +
                "  AVG(price) as avg_price " +
                "FROM products " +
                "GROUP BY age_category"
            ).show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: Multiple Parameter UDFs
     */
    public void demonstrateMultipleParameterUDFs() {
        System.out.println("\n=== Example 4: Multiple Parameter UDFs ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Multiple Parameter UDFs")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // UDF with 2 parameters
            spark.udf().register("fullName", 
                (UDF2<String, String, String>) (firstName, lastName) -> 
                    firstName + " " + lastName, 
                DataTypes.StringType);
            
            // UDF with 2 parameters - calculate commission
            spark.udf().register("calculateCommission", 
                (UDF2<Double, Double, Double>) (sales, rate) -> 
                    sales * rate, 
                DataTypes.DoubleType);
            
            // UDF with 3 parameters
            spark.udf().register("totalCompensation", 
                (UDF3<Double, Double, Double, Double>) (salary, bonus, commission) -> 
                    salary + bonus + commission, 
                DataTypes.DoubleType);
            
            // UDF with business logic
            spark.udf().register("discountedPrice", 
                (UDF2<Double, String, Double>) (price, customerType) -> {
                    switch (customerType) {
                        case "Premium": return price * 0.80;  // 20% discount
                        case "Regular": return price * 0.90;  // 10% discount
                        default: return price;
                    }
                }, 
                DataTypes.DoubleType);
            
            List<SalesPerson> salesPeople = Arrays.asList(
                new SalesPerson("John", "Doe", 50000, 5000, 0.05),
                new SalesPerson("Jane", "Smith", 60000, 8000, 0.06),
                new SalesPerson("Bob", "Johnson", 55000, 6000, 0.055)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(salesPeople, SalesPerson.class);
            salesDF.createOrReplaceTempView("sales_people");
            
            System.out.println("\nMultiple parameter UDFs:");
            spark.sql(
                "SELECT " +
                "  fullName(firstName, lastName) as name, " +
                "  baseSalary, " +
                "  salesAmount, " +
                "  commissionRate, " +
                "  calculateCommission(salesAmount, commissionRate) as commission, " +
                "  totalCompensation(baseSalary, " +
                "    calculateCommission(salesAmount, commissionRate), " +
                "    0) as total_comp " +
                "FROM sales_people"
            ).show();
            
            // Test discount UDF
            List<Purchase> purchases = Arrays.asList(
                new Purchase(1, "Premium", 1000),
                new Purchase(2, "Regular", 1000),
                new Purchase(3, "Guest", 1000)
            );
            
            Dataset<Row> purchasesDF = spark.createDataFrame(purchases, Purchase.class);
            purchasesDF.createOrReplaceTempView("purchases");
            
            System.out.println("\nDiscounted prices:");
            spark.sql(
                "SELECT " +
                "  id, " +
                "  customerType, " +
                "  originalPrice, " +
                "  discountedPrice(originalPrice, customerType) as final_price, " +
                "  (originalPrice - discountedPrice(originalPrice, customerType)) as savings " +
                "FROM purchases"
            ).show();
            
        } finally {
            spark.stop();
        }
    }
    
    // Helper classes
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
    
    public static class EmployeeDetail implements Serializable {
        private int id;
        private String name;
        private double salary;
        private String email;
        private String phone;
        
        public EmployeeDetail() {}
        
        public EmployeeDetail(int id, String name, double salary, String email, String phone) {
            this.id = id;
            this.name = name;
            this.salary = salary;
            this.email = email;
            this.phone = phone;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public double getSalary() { return salary; }
        public void setSalary(double salary) { this.salary = salary; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getPhone() { return phone; }
        public void setPhone(String phone) { this.phone = phone; }
    }
    
    public static class Product implements Serializable {
        private int id;
        private String name;
        private String releaseDate;
        private double price;
        
        public Product() {}
        
        public Product(int id, String name, String releaseDate, double price) {
            this.id = id;
            this.name = name;
            this.releaseDate = releaseDate;
            this.price = price;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getReleaseDate() { return releaseDate; }
        public void setReleaseDate(String releaseDate) { this.releaseDate = releaseDate; }
        public double getPrice() { return price; }
        public void setPrice(double price) { this.price = price; }
    }
    
    public static class SalesPerson implements Serializable {
        private String firstName;
        private String lastName;
        private double baseSalary;
        private double salesAmount;
        private double commissionRate;
        
        public SalesPerson() {}
        
        public SalesPerson(String firstName, String lastName, double baseSalary, 
                          double salesAmount, double commissionRate) {
            this.firstName = firstName;
            this.lastName = lastName;
            this.baseSalary = baseSalary;
            this.salesAmount = salesAmount;
            this.commissionRate = commissionRate;
        }
        
        public String getFirstName() { return firstName; }
        public void setFirstName(String firstName) { this.firstName = firstName; }
        public String getLastName() { return lastName; }
        public void setLastName(String lastName) { this.lastName = lastName; }
        public double getBaseSalary() { return baseSalary; }
        public void setBaseSalary(double baseSalary) { this.baseSalary = baseSalary; }
        public double getSalesAmount() { return salesAmount; }
        public void setSalesAmount(double salesAmount) { this.salesAmount = salesAmount; }
        public double getCommissionRate() { return commissionRate; }
        public void setCommissionRate(double commissionRate) { this.commissionRate = commissionRate; }
    }
    
    public static class Purchase implements Serializable {
        private int id;
        private String customerType;
        private double originalPrice;
        
        public Purchase() {}
        
        public Purchase(int id, String customerType, double originalPrice) {
            this.id = id;
            this.customerType = customerType;
            this.originalPrice = originalPrice;
        }
        
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getCustomerType() { return customerType; }
        public void setCustomerType(String customerType) { this.customerType = customerType; }
        public double getOriginalPrice() { return originalPrice; }
        public void setOriginalPrice(double originalPrice) { this.originalPrice = originalPrice; }
    }
}
