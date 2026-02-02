package com.microsoft.spark.basics;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.*;
import org.apache.spark.sql.RowFactory;
import static org.apache.spark.sql.functions.*;

import java.util.Arrays;
import java.util.List;

/**
 * DataFrameOperations demonstrates comprehensive DataFrame operations
 * including creation, transformations, and actions.
 */
public class DataFrameOperations {
    
    public static void main(String[] args) {
        DataFrameOperations operations = new DataFrameOperations();
        
        try {
            operations.createDataFrames();
            operations.dataFrameTransformations();
            operations.dataFrameActions();
            operations.workWithSchemas();
        } catch (Exception e) {
            System.err.println("Error in DataFrameOperations: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Different ways to create DataFrames
     */
    public void createDataFrames() {
        System.out.println("\n=== Example 1: Creating DataFrames ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("DataFrame Creation")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Method 1: From Java objects
            List<Person> people = Arrays.asList(
                new Person("John", 30, "Engineering"),
                new Person("Jane", 25, "Marketing"),
                new Person("Bob", 35, "Sales")
            );
            
            Dataset<Row> df1 = spark.createDataFrame(people, Person.class);
            System.out.println("\nDataFrame from Java objects:");
            df1.show();
            
            // Method 2: From Rows with schema
            StructType schema = new StructType(new StructField[]{
                new StructField("name", DataTypes.StringType, false, Metadata.empty()),
                new StructField("age", DataTypes.IntegerType, false, Metadata.empty()),
                new StructField("department", DataTypes.StringType, false, Metadata.empty())
            });
            
            List<Row> rows = Arrays.asList(
                RowFactory.create("Alice", 28, "Engineering"),
                RowFactory.create("Charlie", 32, "Marketing"),
                RowFactory.create("David", 29, "Sales")
            );
            
            Dataset<Row> df2 = spark.createDataFrame(rows, schema);
            System.out.println("\nDataFrame from Rows with schema:");
            df2.show();
            
            // Method 3: From sequence with toDF
            Dataset<Row> df3 = spark.range(1, 11)
                .selectExpr("id", "id * 2 as doubled", "id * id as squared");
            System.out.println("\nDataFrame from range:");
            df3.show();
            
            // Method 4: Read from JSON (sample data)
            Dataset<Row> df4 = spark.read()
                .option("multiLine", true)
                .json(spark.createDataset(Arrays.asList(
                    "{\"name\":\"Emma\",\"age\":27,\"department\":\"HR\"}",
                    "{\"name\":\"Frank\",\"age\":31,\"department\":\"IT\"}"
                ), org.apache.spark.sql.Encoders.STRING()));
            System.out.println("\nDataFrame from JSON:");
            df4.show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: DataFrame Transformations
     */
    public void dataFrameTransformations() {
        System.out.println("\n=== Example 2: DataFrame Transformations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("DataFrame Transformations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Create sample DataFrame
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000, 30),
                new Employee(2, "Jane", "Marketing", 65000, 25),
                new Employee(3, "Bob", "Engineering", 80000, 35),
                new Employee(4, "Alice", "Sales", 70000, 28),
                new Employee(5, "Charlie", "Engineering", 72000, 32),
                new Employee(6, "Diana", "Marketing", 68000, 27)
            );
            
            Dataset<Row> df = spark.createDataFrame(employees, Employee.class);
            
            System.out.println("\nOriginal DataFrame:");
            df.show();
            
            // select: Choose columns
            System.out.println("\nSelect specific columns:");
            df.select("name", "department", "salary").show();
            
            // select with expressions
            System.out.println("\nSelect with expressions:");
            df.select(
                col("name"),
                col("salary").multiply(1.1).alias("new_salary"),
                col("age").plus(1).alias("next_year_age")
            ).show();
            
            // filter/where: Filter rows
            System.out.println("\nFilter salary > 70000:");
            df.filter(col("salary").gt(70000)).show();
            
            System.out.println("\nFilter Engineering department:");
            df.where("department = 'Engineering'").show();
            
            // Multiple conditions
            System.out.println("\nFilter Engineering AND salary > 72000:");
            df.filter(col("department").equalTo("Engineering")
                .and(col("salary").gt(72000))).show();
            
            // withColumn: Add or replace column
            System.out.println("\nAdd bonus column:");
            df.withColumn("bonus", col("salary").multiply(0.1)).show();
            
            // withColumnRenamed: Rename column
            System.out.println("\nRename columns:");
            df.withColumnRenamed("name", "employee_name")
                .withColumnRenamed("salary", "annual_salary")
                .show();
            
            // drop: Remove columns
            System.out.println("\nDrop age column:");
            df.drop("age").show();
            
            // distinct: Remove duplicates
            System.out.println("\nDistinct departments:");
            df.select("department").distinct().show();
            
            // orderBy/sort: Sort data
            System.out.println("\nOrder by salary descending:");
            df.orderBy(col("salary").desc()).show();
            
            System.out.println("\nOrder by department and salary:");
            df.orderBy(col("department").asc(), col("salary").desc()).show();
            
            // limit: Limit rows
            System.out.println("\nLimit to 3 rows:");
            df.limit(3).show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: DataFrame Actions
     */
    public void dataFrameActions() {
        System.out.println("\n=== Example 3: DataFrame Actions ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("DataFrame Actions")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Employee> employees = Arrays.asList(
                new Employee(1, "John", "Engineering", 75000, 30),
                new Employee(2, "Jane", "Marketing", 65000, 25),
                new Employee(3, "Bob", "Engineering", 80000, 35)
            );
            
            Dataset<Row> df = spark.createDataFrame(employees, Employee.class);
            
            // show: Display data
            System.out.println("\nShow data:");
            df.show();
            
            System.out.println("\nShow 2 rows without truncation:");
            df.show(2, false);
            
            // count: Count rows
            long count = df.count();
            System.out.println("\nTotal count: " + count);
            
            // first/head: Get first row
            Row first = df.first();
            System.out.println("\nFirst row: " + first);
            
            // take: Get first n rows
            List<Row> firstTwo = df.take(2);
            System.out.println("\nFirst 2 rows: " + firstTwo);
            
            // collect: Get all rows (use with caution)
            List<Row> allRows = df.collect();
            System.out.println("\nAll rows count: " + allRows.size());
            
            // describe: Statistical summary
            System.out.println("\nStatistical summary:");
            df.describe("salary", "age").show();
            
            // summary: Extended statistics
            System.out.println("\nExtended summary:");
            df.summary().show();
            
            // printSchema: Show schema
            System.out.println("\nSchema:");
            df.printSchema();
            
            // columns: Get column names
            String[] columns = df.columns();
            System.out.println("\nColumn names: " + Arrays.toString(columns));
            
            // dtypes: Get column types
            System.out.println("\nColumn types:");
            Arrays.stream(df.dtypes()).forEach(tuple -> 
                System.out.println("  " + tuple._1 + ": " + tuple._2)
            );
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: Working with Schemas
     */
    public void workWithSchemas() {
        System.out.println("\n=== Example 4: Working with Schemas ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("DataFrame Schemas")
                .master("local[*]")
                .getOrCreate();
        
        try {
            // Define complex schema
            StructType schema = new StructType(new StructField[]{
                new StructField("id", DataTypes.IntegerType, false, Metadata.empty()),
                new StructField("name", DataTypes.StringType, false, Metadata.empty()),
                new StructField("email", DataTypes.StringType, true, Metadata.empty()),
                new StructField("salary", DataTypes.DoubleType, false, Metadata.empty()),
                new StructField("hire_date", DataTypes.DateType, true, Metadata.empty()),
                new StructField("address", new StructType(new StructField[]{
                    new StructField("street", DataTypes.StringType, true, Metadata.empty()),
                    new StructField("city", DataTypes.StringType, true, Metadata.empty()),
                    new StructField("zip", DataTypes.StringType, true, Metadata.empty())
                }), true, Metadata.empty()),
                new StructField("skills", DataTypes.createArrayType(DataTypes.StringType), true, Metadata.empty())
            });
            
            System.out.println("\nDefined Schema:");
            System.out.println(schema.treeString());
            
            // Create DataFrame with schema
            List<Row> data = Arrays.asList(
                RowFactory.create(
                    1, "John Doe", "john@example.com", 75000.0, 
                    java.sql.Date.valueOf("2020-01-15"),
                    RowFactory.create("123 Main St", "Seattle", "98101"),
                    Arrays.asList("Java", "Spark", "SQL")
                ),
                RowFactory.create(
                    2, "Jane Smith", "jane@example.com", 85000.0,
                    java.sql.Date.valueOf("2019-06-20"),
                    RowFactory.create("456 Oak Ave", "Portland", "97201"),
                    Arrays.asList("Python", "Pandas", "ML")
                )
            );
            
            Dataset<Row> df = spark.createDataFrame(data, schema);
            
            System.out.println("\nDataFrame with complex schema:");
            df.show(false);
            
            System.out.println("\nDataFrame schema:");
            df.printSchema();
            
            // Access nested fields
            System.out.println("\nAccess nested address fields:");
            df.select("name", "address.city", "address.zip").show();
            
            // Access array elements
            System.out.println("\nAccess array elements:");
            df.select("name", col("skills").getItem(0).alias("primary_skill")).show();
            
            // Explode array
            System.out.println("\nExplode skills array:");
            df.select("name", explode(col("skills")).alias("skill")).show();
            
        } finally {
            spark.stop();
        }
    }
    
    // Helper classes
    public static class Person implements java.io.Serializable {
        private String name;
        private int age;
        private String department;
        
        public Person() {}
        
        public Person(String name, int age, String department) {
            this.name = name;
            this.age = age;
            this.department = department;
        }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public int getAge() { return age; }
        public void setAge(int age) { this.age = age; }
        public String getDepartment() { return department; }
        public void setDepartment(String department) { this.department = department; }
    }
    
    public static class Employee implements java.io.Serializable {
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
}
