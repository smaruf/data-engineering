package com.microsoft.java.intermediate.jdbc;

import java.sql.*;
import java.util.*;

/**
 * PreparedStatements demonstrates parameterized queries and batch operations.
 * Covers SQL injection prevention, batch processing, and performance optimization.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class PreparedStatements {
    
    private static final String DB_URL = "jdbc:h2:mem:prepareddb";
    private static final String DB_USER = "sa";
    private static final String DB_PASSWORD = "";
    
    /**
     * Product data model.
     */
    public static class Product {
        private int id;
        private String name;
        private String category;
        private double price;
        private int quantity;
        
        public Product(String name, String category, double price, int quantity) {
            this.name = name;
            this.category = category;
            this.price = price;
            this.quantity = quantity;
        }
        
        public Product(int id, String name, String category, double price, int quantity) {
            this.id = id;
            this.name = name;
            this.category = category;
            this.price = price;
            this.quantity = quantity;
        }
        
        @Override
        public String toString() {
            return String.format("Product{id=%d, name='%s', category='%s', price=%.2f, qty=%d}",
                id, name, category, price, quantity);
        }
    }
    
    /**
     * Initializes database.
     */
    public static void initializeDatabase(Connection conn) throws SQLException {
        String sql = "CREATE TABLE IF NOT EXISTS products (" +
                    "id INT AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(100), " +
                    "category VARCHAR(50), " +
                    "price DECIMAL(10,2), " +
                    "quantity INT)";
        
        try (Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
            System.out.println("Database initialized\n");
        }
    }
    
    /**
     * Demonstrates PreparedStatement vs Statement (SQL Injection risk).
     */
    public static void demonstrateSQLInjectionPrevention(Connection conn) {
        System.out.println("=== SQL Injection Prevention ===");
        
        // UNSAFE: Statement with string concatenation (vulnerable to SQL injection)
        String unsafeCategory = "Electronics'; DROP TABLE products; --";
        System.out.println("Unsafe input: " + unsafeCategory);
        
        // SAFE: PreparedStatement (prevents SQL injection)
        String sql = "SELECT * FROM products WHERE category = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, unsafeCategory);
            
            ResultSet rs = pstmt.executeQuery();
            int count = 0;
            while (rs.next()) {
                count++;
            }
            
            System.out.println("Query executed safely (found " + count + " products)");
            System.out.println("PreparedStatement properly escaped the input");
            
        } catch (SQLException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates basic PreparedStatement usage.
     */
    public static void demonstrateBasicPreparedStatement(Connection conn) {
        System.out.println("=== Basic PreparedStatement ===");
        
        String sql = "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // Set parameters
            pstmt.setString(1, "Laptop");
            pstmt.setString(2, "Electronics");
            pstmt.setDouble(3, 999.99);
            pstmt.setInt(4, 10);
            
            int rows = pstmt.executeUpdate();
            System.out.println("Inserted " + rows + " row(s)");
            
        } catch (SQLException e) {
            System.err.println("Insert failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates reusing PreparedStatement with different parameters.
     */
    public static void demonstrateParameterReuse(Connection conn) {
        System.out.println("=== Parameter Reuse ===");
        
        String sql = "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // First insert
            pstmt.setString(1, "Mouse");
            pstmt.setString(2, "Electronics");
            pstmt.setDouble(3, 25.99);
            pstmt.setInt(4, 50);
            pstmt.executeUpdate();
            System.out.println("Inserted: Mouse");
            
            // Second insert (reusing same PreparedStatement)
            pstmt.setString(1, "Keyboard");
            pstmt.setString(2, "Electronics");
            pstmt.setDouble(3, 49.99);
            pstmt.setInt(4, 30);
            pstmt.executeUpdate();
            System.out.println("Inserted: Keyboard");
            
            System.out.println("Same PreparedStatement reused for multiple inserts");
            
        } catch (SQLException e) {
            System.err.println("Insert failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates batch operations for better performance.
     */
    public static void demonstrateBatchOperations(Connection conn) {
        System.out.println("=== Batch Operations ===");
        
        List<Product> products = Arrays.asList(
            new Product("Chair", "Furniture", 149.99, 20),
            new Product("Desk", "Furniture", 299.99, 15),
            new Product("Monitor", "Electronics", 349.99, 25),
            new Product("Phone", "Electronics", 699.99, 40),
            new Product("Tablet", "Electronics", 499.99, 35)
        );
        
        String sql = "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)";
        
        long startTime = System.currentTimeMillis();
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (Product product : products) {
                pstmt.setString(1, product.name);
                pstmt.setString(2, product.category);
                pstmt.setDouble(3, product.price);
                pstmt.setInt(4, product.quantity);
                pstmt.addBatch(); // Add to batch
            }
            
            int[] results = pstmt.executeBatch(); // Execute all at once
            long endTime = System.currentTimeMillis();
            
            System.out.println("Batch inserted " + results.length + " products");
            System.out.println("Time taken: " + (endTime - startTime) + "ms");
            
            // Check results
            int successCount = 0;
            for (int result : results) {
                if (result >= 0 || result == Statement.SUCCESS_NO_INFO) {
                    successCount++;
                }
            }
            System.out.println("Successful inserts: " + successCount);
            
        } catch (SQLException e) {
            System.err.println("Batch operation failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates batch updates.
     */
    public static void demonstrateBatchUpdates(Connection conn) {
        System.out.println("=== Batch Updates ===");
        
        String sql = "UPDATE products SET price = price * ? WHERE category = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // Apply 10% discount to Electronics
            pstmt.setDouble(1, 0.9);
            pstmt.setString(2, "Electronics");
            pstmt.addBatch();
            
            // Apply 5% discount to Furniture
            pstmt.setDouble(1, 0.95);
            pstmt.setString(2, "Furniture");
            pstmt.addBatch();
            
            int[] results = pstmt.executeBatch();
            System.out.println("Updated " + results.length + " categories");
            
            for (int i = 0; i < results.length; i++) {
                System.out.println("  Batch " + i + ": " + results[i] + " rows affected");
            }
            
        } catch (SQLException e) {
            System.err.println("Batch update failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates parameterized SELECT queries.
     */
    public static void demonstrateParameterizedSelect(Connection conn) {
        System.out.println("=== Parameterized SELECT ===");
        
        String sql = "SELECT * FROM products WHERE price BETWEEN ? AND ? ORDER BY price";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, 100.0);
            pstmt.setDouble(2, 500.0);
            
            ResultSet rs = pstmt.executeQuery();
            System.out.println("Products with price between $100 and $500:");
            
            while (rs.next()) {
                System.out.printf("  %s - $%.2f%n", 
                    rs.getString("name"), 
                    rs.getDouble("price"));
            }
            
        } catch (SQLException e) {
            System.err.println("Select failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates PreparedStatement with LIKE operator.
     */
    public static void demonstrateLikeOperator(Connection conn) {
        System.out.println("=== LIKE Operator with PreparedStatement ===");
        
        String sql = "SELECT * FROM products WHERE name LIKE ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // Search for products starting with 'M'
            pstmt.setString(1, "M%");
            
            ResultSet rs = pstmt.executeQuery();
            System.out.println("Products starting with 'M':");
            
            while (rs.next()) {
                System.out.println("  " + rs.getString("name"));
            }
            
        } catch (SQLException e) {
            System.err.println("Search failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates PreparedStatement with IN clause.
     */
    public static void demonstrateInClause(Connection conn) {
        System.out.println("=== IN Clause with PreparedStatement ===");
        
        List<String> categories = Arrays.asList("Electronics", "Furniture");
        
        // Build placeholders
        String placeholders = String.join(",", 
            Collections.nCopies(categories.size(), "?"));
        String sql = "SELECT category, COUNT(*) as count FROM products " +
                    "WHERE category IN (" + placeholders + ") GROUP BY category";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // Set parameters
            for (int i = 0; i < categories.size(); i++) {
                pstmt.setString(i + 1, categories.get(i));
            }
            
            ResultSet rs = pstmt.executeQuery();
            System.out.println("Product count by category:");
            
            while (rs.next()) {
                System.out.printf("  %s: %d products%n",
                    rs.getString("category"),
                    rs.getInt("count"));
            }
            
        } catch (SQLException e) {
            System.err.println("Query failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates handling NULL values.
     */
    public static void demonstrateNullHandling(Connection conn) {
        System.out.println("=== NULL Handling ===");
        
        String sql = "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, "Unknown Product");
            pstmt.setNull(2, Types.VARCHAR); // Set NULL
            pstmt.setDouble(3, 0.0);
            pstmt.setInt(4, 0);
            
            pstmt.executeUpdate();
            System.out.println("Inserted product with NULL category");
            
        } catch (SQLException e) {
            System.err.println("Insert with NULL failed: " + e.getMessage());
        }
        
        // Query NULL values
        sql = "SELECT * FROM products WHERE category IS NULL";
        
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            System.out.println("Products with NULL category:");
            while (rs.next()) {
                System.out.println("  " + rs.getString("name"));
            }
            
        } catch (SQLException e) {
            System.err.println("Query failed: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates PreparedStatement metadata.
     */
    public static void demonstrateParameterMetadata(Connection conn) {
        System.out.println("=== PreparedStatement Metadata ===");
        
        String sql = "SELECT * FROM products WHERE category = ? AND price > ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            ParameterMetaData pmd = pstmt.getParameterMetaData();
            
            System.out.println("Parameter count: " + pmd.getParameterCount());
            
            for (int i = 1; i <= pmd.getParameterCount(); i++) {
                System.out.println("Parameter " + i + ":");
                System.out.println("  Type: " + pmd.getParameterTypeName(i));
                System.out.println("  Mode: " + getParameterMode(pmd.getParameterMode(i)));
            }
            
        } catch (SQLException e) {
            System.err.println("Metadata error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    private static String getParameterMode(int mode) {
        switch (mode) {
            case ParameterMetaData.parameterModeIn: return "IN";
            case ParameterMetaData.parameterModeOut: return "OUT";
            case ParameterMetaData.parameterModeInOut: return "INOUT";
            default: return "UNKNOWN";
        }
    }
    
    /**
     * Main method demonstrating PreparedStatement examples.
     */
    public static void main(String[] args) {
        System.out.println("JDBC PreparedStatement Examples\n");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            
            initializeDatabase(conn);
            
            demonstrateSQLInjectionPrevention(conn);
            demonstrateBasicPreparedStatement(conn);
            demonstrateParameterReuse(conn);
            demonstrateBatchOperations(conn);
            demonstrateBatchUpdates(conn);
            demonstrateParameterizedSelect(conn);
            demonstrateLikeOperator(conn);
            demonstrateInClause(conn);
            demonstrateNullHandling(conn);
            demonstrateParameterMetadata(conn);
            
            System.out.println("=== All PreparedStatement examples completed ===");
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
