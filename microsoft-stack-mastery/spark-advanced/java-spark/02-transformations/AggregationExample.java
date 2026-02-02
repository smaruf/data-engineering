package com.microsoft.spark.transformations;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.RelationalGroupedDataset;
import static org.apache.spark.sql.functions.*;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

/**
 * AggregationExample demonstrates various aggregation operations
 * including groupBy, agg, pivot, rollup, and cube.
 */
public class AggregationExample {
    
    public static void main(String[] args) {
        AggregationExample example = new AggregationExample();
        
        try {
            example.demonstrateBasicAggregations();
            example.demonstrateGroupByOperations();
            example.demonstratePivotOperations();
            example.demonstrateAdvancedAggregations();
        } catch (Exception e) {
            System.err.println("Error in AggregationExample: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Example 1: Basic Aggregations
     */
    public void demonstrateBasicAggregations() {
        System.out.println("\n=== Example 1: Basic Aggregations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Basic Aggregations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Sale> sales = Arrays.asList(
                new Sale(1, "2024-01-15", "Electronics", "Laptop", 1200.0, 2),
                new Sale(2, "2024-01-16", "Electronics", "Mouse", 25.0, 5),
                new Sale(3, "2024-01-17", "Furniture", "Desk", 300.0, 1),
                new Sale(4, "2024-01-18", "Electronics", "Keyboard", 80.0, 3),
                new Sale(5, "2024-01-19", "Furniture", "Chair", 150.0, 4),
                new Sale(6, "2024-01-20", "Electronics", "Monitor", 400.0, 2)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, Sale.class);
            
            System.out.println("\nOriginal data:");
            salesDF.show();
            
            // Basic aggregation functions
            System.out.println("\nBasic Aggregations:");
            salesDF.agg(
                count("*").alias("total_sales"),
                sum("amount").alias("total_revenue"),
                avg("amount").alias("average_sale"),
                min("amount").alias("min_sale"),
                max("amount").alias("max_sale")
            ).show();
            
            // Multiple aggregations
            System.out.println("\nDetailed Statistics:");
            salesDF.agg(
                sum("quantity").alias("total_quantity"),
                avg("quantity").alias("avg_quantity"),
                expr("sum(amount * quantity)").alias("total_value"),
                countDistinct("category").alias("distinct_categories"),
                countDistinct("product").alias("distinct_products")
            ).show();
            
            // describe - statistical summary
            System.out.println("\nStatistical Summary:");
            salesDF.describe("amount", "quantity").show();
            
            // summary - extended statistics
            System.out.println("\nExtended Summary:");
            salesDF.select("amount").summary().show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 2: GroupBy Operations
     */
    public void demonstrateGroupByOperations() {
        System.out.println("\n=== Example 2: GroupBy Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("GroupBy Operations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Sale> sales = Arrays.asList(
                new Sale(1, "2024-01-15", "Electronics", "Laptop", 1200.0, 2),
                new Sale(2, "2024-01-16", "Electronics", "Mouse", 25.0, 5),
                new Sale(3, "2024-01-17", "Furniture", "Desk", 300.0, 1),
                new Sale(4, "2024-01-18", "Electronics", "Keyboard", 80.0, 3),
                new Sale(5, "2024-01-19", "Furniture", "Chair", 150.0, 4),
                new Sale(6, "2024-01-20", "Electronics", "Monitor", 400.0, 2),
                new Sale(7, "2024-01-21", "Furniture", "Table", 500.0, 1),
                new Sale(8, "2024-01-22", "Electronics", "Headphones", 100.0, 6)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, Sale.class);
            
            // Simple groupBy with single aggregation
            System.out.println("\nGroup by category - count:");
            salesDF.groupBy("category").count().show();
            
            // GroupBy with sum
            System.out.println("\nGroup by category - total sales:");
            salesDF.groupBy("category")
                .sum("amount")
                .withColumnRenamed("sum(amount)", "total_amount")
                .show();
            
            // GroupBy with multiple aggregations
            System.out.println("\nGroup by category - multiple aggregations:");
            salesDF.groupBy("category")
                .agg(
                    count("*").alias("num_sales"),
                    sum("amount").alias("total_amount"),
                    avg("amount").alias("avg_amount"),
                    min("amount").alias("min_amount"),
                    max("amount").alias("max_amount"),
                    sum("quantity").alias("total_quantity")
                )
                .orderBy(col("total_amount").desc())
                .show();
            
            // GroupBy with expressions
            System.out.println("\nGroup by category - with expressions:");
            salesDF.groupBy("category")
                .agg(
                    count("*").alias("count"),
                    expr("sum(amount * quantity)").alias("total_value"),
                    expr("avg(amount * quantity)").alias("avg_value")
                )
                .show();
            
            // Multiple column groupBy
            System.out.println("\nGroup by category and product:");
            salesDF.groupBy("category", "product")
                .agg(
                    sum("amount").alias("total_amount"),
                    sum("quantity").alias("total_quantity")
                )
                .show();
            
            // GroupBy with having (filter after aggregation)
            System.out.println("\nGroup by category - with having clause:");
            salesDF.groupBy("category")
                .agg(
                    sum("amount").alias("total_amount"),
                    count("*").alias("count")
                )
                .filter(col("total_amount").gt(500))
                .show();
            
            // Collect list/set
            System.out.println("\nGroup by category - collect products:");
            salesDF.groupBy("category")
                .agg(
                    collect_list("product").alias("products"),
                    collect_set("product").alias("unique_products")
                )
                .show(false);
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 3: Pivot Operations
     */
    public void demonstratePivotOperations() {
        System.out.println("\n=== Example 3: Pivot Operations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Pivot Operations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<MonthlySale> sales = Arrays.asList(
                new MonthlySale("2024-01", "Electronics", "Online", 5000.0),
                new MonthlySale("2024-01", "Electronics", "Store", 3000.0),
                new MonthlySale("2024-01", "Furniture", "Online", 2000.0),
                new MonthlySale("2024-01", "Furniture", "Store", 4000.0),
                new MonthlySale("2024-02", "Electronics", "Online", 5500.0),
                new MonthlySale("2024-02", "Electronics", "Store", 3200.0),
                new MonthlySale("2024-02", "Furniture", "Online", 2200.0),
                new MonthlySale("2024-02", "Furniture", "Store", 4500.0),
                new MonthlySale("2024-03", "Electronics", "Online", 6000.0),
                new MonthlySale("2024-03", "Electronics", "Store", 3500.0),
                new MonthlySale("2024-03", "Furniture", "Online", 2500.0),
                new MonthlySale("2024-03", "Furniture", "Store", 5000.0)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, MonthlySale.class);
            
            System.out.println("\nOriginal data:");
            salesDF.show();
            
            // Basic pivot - channels as columns
            System.out.println("\nPivot by channel:");
            Dataset<Row> pivotByChannel = salesDF.groupBy("month", "category")
                .pivot("channel")
                .sum("amount");
            pivotByChannel.show();
            
            // Pivot with specific values
            System.out.println("\nPivot by channel (specified values):");
            salesDF.groupBy("month", "category")
                .pivot("channel", Arrays.asList("Online", "Store"))
                .sum("amount")
                .show();
            
            // Pivot by month
            System.out.println("\nPivot by month:");
            salesDF.groupBy("category", "channel")
                .pivot("month")
                .agg(sum("amount").alias("total"))
                .show();
            
            // Pivot with multiple aggregations
            System.out.println("\nPivot with multiple aggregations:");
            salesDF.groupBy("category")
                .pivot("channel")
                .agg(
                    sum("amount").alias("total"),
                    avg("amount").alias("average"),
                    count("*").alias("count")
                )
                .show();
            
            // Unpivot (melt) - convert columns to rows
            System.out.println("\nUnpivot example:");
            Dataset<Row> pivoted = salesDF.groupBy("month")
                .pivot("category")
                .sum("amount");
            
            pivoted.show();
            
            // Unpivot using stack
            Dataset<Row> unpivoted = pivoted.selectExpr(
                "month",
                "stack(2, 'Electronics', Electronics, 'Furniture', Furniture) as (category, amount)"
            );
            System.out.println("\nUnpivoted data:");
            unpivoted.show();
            
        } finally {
            spark.stop();
        }
    }
    
    /**
     * Example 4: Advanced Aggregations (Rollup, Cube)
     */
    public void demonstrateAdvancedAggregations() {
        System.out.println("\n=== Example 4: Advanced Aggregations ===");
        
        SparkSession spark = SparkSession.builder()
                .appName("Advanced Aggregations")
                .master("local[*]")
                .getOrCreate();
        
        try {
            List<Sale> sales = Arrays.asList(
                new Sale(1, "2024-01", "Electronics", "Laptop", 1200.0, 2),
                new Sale(2, "2024-01", "Electronics", "Mouse", 25.0, 5),
                new Sale(3, "2024-01", "Furniture", "Desk", 300.0, 1),
                new Sale(4, "2024-02", "Electronics", "Keyboard", 80.0, 3),
                new Sale(5, "2024-02", "Furniture", "Chair", 150.0, 4),
                new Sale(6, "2024-02", "Furniture", "Table", 500.0, 1)
            );
            
            Dataset<Row> salesDF = spark.createDataFrame(sales, Sale.class);
            
            // Rollup - hierarchical aggregation
            System.out.println("\nRollup (date, category):");
            salesDF.rollup("date", "category")
                .agg(
                    sum("amount").alias("total_amount"),
                    count("*").alias("count")
                )
                .orderBy("date", "category")
                .show();
            
            // Cube - all combinations
            System.out.println("\nCube (date, category):");
            salesDF.cube("date", "category")
                .agg(
                    sum("amount").alias("total_amount"),
                    count("*").alias("count")
                )
                .orderBy("date", "category")
                .show();
            
            // Grouping sets equivalent using rollup
            System.out.println("\nGrouping sets using rollup:");
            salesDF.rollup("category", "product")
                .agg(
                    sum("amount").alias("total"),
                    grouping("category").alias("grp_category"),
                    grouping("product").alias("grp_product")
                )
                .orderBy("category", "product")
                .show();
            
            // Window aggregations (previewing for window functions)
            System.out.println("\nRunning total using window function:");
            Dataset<Row> withRunningTotal = salesDF
                .withColumn("running_total", 
                    sum("amount").over(
                        org.apache.spark.sql.expressions.Window
                            .orderBy("id")
                            .rowsBetween(org.apache.spark.sql.expressions.Window.unboundedPreceding(), 0)
                    )
                );
            withRunningTotal.show();
            
            // Percentiles and approximate quantiles
            System.out.println("\nPercentiles:");
            salesDF.stat().approxQuantile("amount", new double[]{0.25, 0.5, 0.75}, 0.0);
            
            salesDF.agg(
                expr("percentile_approx(amount, 0.5)").alias("median"),
                expr("percentile_approx(amount, array(0.25, 0.5, 0.75))").alias("quartiles")
            ).show(false);
            
            // Custom aggregation with map
            System.out.println("\nCustom aggregation:");
            Map<String, String> aggMap = new HashMap<>();
            aggMap.put("amount", "sum");
            aggMap.put("quantity", "avg");
            
            salesDF.groupBy("category").agg(aggMap).show();
            
        } finally {
            spark.stop();
        }
    }
    
    // Helper classes
    public static class Sale implements Serializable {
        private int id;
        private String date;
        private String category;
        private String product;
        private double amount;
        private int quantity;
        
        public Sale() {}
        
        public Sale(int id, String date, String category, String product, double amount, int quantity) {
            this.id = id;
            this.date = date;
            this.category = category;
            this.product = product;
            this.amount = amount;
            this.quantity = quantity;
        }
        
        // Getters and Setters
        public int getId() { return id; }
        public void setId(int id) { this.id = id; }
        public String getDate() { return date; }
        public void setDate(String date) { this.date = date; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        public String getProduct() { return product; }
        public void setProduct(String product) { this.product = product; }
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
        public int getQuantity() { return quantity; }
        public void setQuantity(int quantity) { this.quantity = quantity; }
    }
    
    public static class MonthlySale implements Serializable {
        private String month;
        private String category;
        private String channel;
        private double amount;
        
        public MonthlySale() {}
        
        public MonthlySale(String month, String category, String channel, double amount) {
            this.month = month;
            this.category = category;
            this.channel = channel;
            this.amount = amount;
        }
        
        // Getters and Setters
        public String getMonth() { return month; }
        public void setMonth(String month) { this.month = month; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        public String getChannel() { return channel; }
        public void setChannel(String channel) { this.channel = channel; }
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
    }
}
