package com.microsoft.java.intermediate.jdbc;

import java.sql.*;
import java.util.Properties;

/**
 * JDBCConnection demonstrates database connection management in Java.
 * Covers connection creation, connection pooling concepts, and best practices.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class JDBCConnection {
    
    // Database configuration (H2 in-memory database for demo)
    private static final String DB_URL = "jdbc:h2:mem:testdb";
    private static final String DB_USER = "sa";
    private static final String DB_PASSWORD = "";
    
    /**
     * Demonstrates basic database connection.
     * 
     * @return Database connection or null if failed
     */
    public static Connection getBasicConnection() {
        System.out.println("=== Basic Database Connection ===");
        
        try {
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            System.out.println("Connection established successfully");
            System.out.println("  Database: " + conn.getMetaData().getDatabaseProductName());
            System.out.println("  Version: " + conn.getMetaData().getDatabaseProductVersion());
            System.out.println("  Driver: " + conn.getMetaData().getDriverName());
            return conn;
        } catch (SQLException e) {
            System.err.println("Connection failed: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Demonstrates connection with properties.
     * 
     * @return Database connection or null if failed
     */
    public static Connection getConnectionWithProperties() {
        System.out.println("\n=== Connection with Properties ===");
        
        Properties props = new Properties();
        props.setProperty("user", DB_USER);
        props.setProperty("password", DB_PASSWORD);
        props.setProperty("ssl", "false");
        
        try {
            Connection conn = DriverManager.getConnection(DB_URL, props);
            System.out.println("Connection established with properties");
            return conn;
        } catch (SQLException e) {
            System.err.println("Connection failed: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Demonstrates connection metadata.
     * 
     * @param conn Database connection
     */
    public static void displayConnectionMetadata(Connection conn) {
        System.out.println("\n=== Connection Metadata ===");
        
        if (conn == null) {
            System.err.println("Connection is null");
            return;
        }
        
        try {
            DatabaseMetaData metaData = conn.getMetaData();
            
            System.out.println("Database Information:");
            System.out.println("  Product Name: " + metaData.getDatabaseProductName());
            System.out.println("  Product Version: " + metaData.getDatabaseProductVersion());
            System.out.println("  Driver Name: " + metaData.getDriverName());
            System.out.println("  Driver Version: " + metaData.getDriverVersion());
            System.out.println("  JDBC Version: " + metaData.getJDBCMajorVersion() + "." + 
                metaData.getJDBCMinorVersion());
            
            System.out.println("\nConnection Properties:");
            System.out.println("  URL: " + metaData.getURL());
            System.out.println("  User: " + metaData.getUserName());
            System.out.println("  Read Only: " + conn.isReadOnly());
            System.out.println("  Auto Commit: " + conn.getAutoCommit());
            System.out.println("  Transaction Isolation: " + 
                getTransactionIsolationName(conn.getTransactionIsolation()));
            
            System.out.println("\nSupported Features:");
            System.out.println("  Transactions: " + metaData.supportsTransactions());
            System.out.println("  Batch Updates: " + metaData.supportsBatchUpdates());
            System.out.println("  Savepoints: " + metaData.supportsSavepoints());
            System.out.println("  Stored Procedures: " + metaData.supportsStoredProcedures());
            
        } catch (SQLException e) {
            System.err.println("Error retrieving metadata: " + e.getMessage());
        }
    }
    
    /**
     * Helper method to get transaction isolation level name.
     * 
     * @param level Isolation level constant
     * @return Name of isolation level
     */
    private static String getTransactionIsolationName(int level) {
        switch (level) {
            case Connection.TRANSACTION_NONE:
                return "NONE";
            case Connection.TRANSACTION_READ_UNCOMMITTED:
                return "READ_UNCOMMITTED";
            case Connection.TRANSACTION_READ_COMMITTED:
                return "READ_COMMITTED";
            case Connection.TRANSACTION_REPEATABLE_READ:
                return "REPEATABLE_READ";
            case Connection.TRANSACTION_SERIALIZABLE:
                return "SERIALIZABLE";
            default:
                return "UNKNOWN";
        }
    }
    
    /**
     * Demonstrates testing connection validity.
     * 
     * @param conn Database connection
     */
    public static void testConnectionValidity(Connection conn) {
        System.out.println("\n=== Testing Connection Validity ===");
        
        if (conn == null) {
            System.err.println("Connection is null");
            return;
        }
        
        try {
            boolean isValid = conn.isValid(5); // 5 second timeout
            System.out.println("Connection is valid: " + isValid);
            
            if (!conn.isClosed()) {
                System.out.println("Connection is open");
            } else {
                System.out.println("Connection is closed");
            }
            
        } catch (SQLException e) {
            System.err.println("Error testing connection: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates proper connection closing.
     * 
     * @param conn Database connection to close
     */
    public static void closeConnection(Connection conn) {
        System.out.println("\n=== Closing Connection ===");
        
        if (conn != null) {
            try {
                if (!conn.isClosed()) {
                    conn.close();
                    System.out.println("Connection closed successfully");
                }
            } catch (SQLException e) {
                System.err.println("Error closing connection: " + e.getMessage());
            }
        }
    }
    
    /**
     * Demonstrates try-with-resources for automatic connection management.
     */
    public static void demonstrateTryWithResources() {
        System.out.println("\n=== Try-With-Resources ===");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            System.out.println("Connection opened (will auto-close)");
            
            // Create a simple table
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("CREATE TABLE IF NOT EXISTS test_table (id INT, name VARCHAR(50))");
                System.out.println("Table created successfully");
            }
            
        } catch (SQLException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println("Connection automatically closed");
    }
    
    /**
     * Simple connection pool implementation for demonstration.
     */
    public static class SimpleConnectionPool {
        private final String url;
        private final String user;
        private final String password;
        private final int maxConnections;
        private final java.util.Queue<Connection> availableConnections;
        private int currentConnections = 0;
        
        public SimpleConnectionPool(String url, String user, String password, int maxConnections) {
            this.url = url;
            this.user = user;
            this.password = password;
            this.maxConnections = maxConnections;
            this.availableConnections = new java.util.concurrent.ConcurrentLinkedQueue<>();
        }
        
        public synchronized Connection getConnection() throws SQLException {
            if (!availableConnections.isEmpty()) {
                Connection conn = availableConnections.poll();
                if (conn != null && conn.isValid(1)) {
                    System.out.println("Reusing connection from pool");
                    return conn;
                }
            }
            
            if (currentConnections < maxConnections) {
                Connection conn = DriverManager.getConnection(url, user, password);
                currentConnections++;
                System.out.println("Created new connection (total: " + currentConnections + ")");
                return conn;
            }
            
            throw new SQLException("Connection pool exhausted");
        }
        
        public synchronized void releaseConnection(Connection conn) {
            if (conn != null) {
                try {
                    if (!conn.isClosed()) {
                        availableConnections.offer(conn);
                        System.out.println("Connection returned to pool");
                    }
                } catch (SQLException e) {
                    System.err.println("Error releasing connection: " + e.getMessage());
                }
            }
        }
        
        public synchronized void shutdown() {
            System.out.println("Shutting down connection pool...");
            for (Connection conn : availableConnections) {
                try {
                    conn.close();
                } catch (SQLException e) {
                    System.err.println("Error closing connection: " + e.getMessage());
                }
            }
            availableConnections.clear();
            currentConnections = 0;
            System.out.println("Connection pool closed");
        }
    }
    
    /**
     * Demonstrates simple connection pooling.
     */
    public static void demonstrateConnectionPooling() {
        System.out.println("\n=== Connection Pooling ===");
        
        SimpleConnectionPool pool = new SimpleConnectionPool(DB_URL, DB_USER, DB_PASSWORD, 3);
        
        try {
            // Get multiple connections
            Connection conn1 = pool.getConnection();
            Connection conn2 = pool.getConnection();
            Connection conn3 = pool.getConnection();
            
            // Release one
            pool.releaseConnection(conn1);
            
            // Get another (should reuse conn1)
            Connection conn4 = pool.getConnection();
            
            // Release all
            pool.releaseConnection(conn2);
            pool.releaseConnection(conn3);
            pool.releaseConnection(conn4);
            
        } catch (SQLException e) {
            System.err.println("Pool error: " + e.getMessage());
        } finally {
            pool.shutdown();
        }
    }
    
    /**
     * Demonstrates handling connection errors.
     */
    public static void demonstrateErrorHandling() {
        System.out.println("\n=== Connection Error Handling ===");
        
        // Try invalid connection
        String invalidUrl = "jdbc:invalid:database";
        
        try {
            Connection conn = DriverManager.getConnection(invalidUrl, "user", "pass");
            conn.close();
        } catch (SQLException e) {
            System.err.println("Expected error occurred:");
            System.err.println("  SQL State: " + e.getSQLState());
            System.err.println("  Error Code: " + e.getErrorCode());
            System.err.println("  Message: " + e.getMessage());
        }
        
        // Connection timeout example
        System.out.println("\nSetting connection timeout:");
        DriverManager.setLoginTimeout(5); // 5 seconds
        System.out.println("Login timeout set to: " + DriverManager.getLoginTimeout() + " seconds");
    }
    
    /**
     * Main method demonstrating JDBC connection examples.
     */
    public static void main(String[] args) {
        System.out.println("JDBC Connection Examples\n");
        
        // Basic connection
        Connection conn1 = getBasicConnection();
        
        // Display metadata
        displayConnectionMetadata(conn1);
        
        // Test validity
        testConnectionValidity(conn1);
        
        // Close connection
        closeConnection(conn1);
        
        // Connection with properties
        Connection conn2 = getConnectionWithProperties();
        closeConnection(conn2);
        
        // Try-with-resources
        demonstrateTryWithResources();
        
        // Connection pooling
        demonstrateConnectionPooling();
        
        // Error handling
        demonstrateErrorHandling();
        
        System.out.println("\n=== All connection examples completed ===");
        System.out.println("\nNote: This example uses H2 in-memory database.");
        System.out.println("For production, use proper connection pools like:");
        System.out.println("  - HikariCP");
        System.out.println("  - Apache DBCP");
        System.out.println("  - C3P0");
    }
}
