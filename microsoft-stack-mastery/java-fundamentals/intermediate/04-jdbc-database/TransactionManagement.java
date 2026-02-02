package com.microsoft.java.intermediate.jdbc;

import java.sql.*;

/**
 * TransactionManagement demonstrates ACID properties and transaction control in JDBC.
 * Covers commit, rollback, savepoints, and isolation levels.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class TransactionManagement {
    
    private static final String DB_URL = "jdbc:h2:mem:transactiondb";
    private static final String DB_USER = "sa";
    private static final String DB_PASSWORD = "";
    
    /**
     * Initializes database with tables.
     */
    public static void initializeDatabase(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("CREATE TABLE IF NOT EXISTS accounts (" +
                        "id INT PRIMARY KEY, " +
                        "name VARCHAR(100), " +
                        "balance DECIMAL(10,2))");
            
            stmt.execute("CREATE TABLE IF NOT EXISTS transactions (" +
                        "id INT AUTO_INCREMENT PRIMARY KEY, " +
                        "from_account INT, " +
                        "to_account INT, " +
                        "amount DECIMAL(10,2), " +
                        "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)");
            
            System.out.println("Database initialized\n");
        }
    }
    
    /**
     * Demonstrates basic transaction with commit.
     */
    public static void demonstrateBasicTransaction(Connection conn) {
        System.out.println("=== Basic Transaction (Commit) ===");
        
        try {
            // Disable auto-commit
            conn.setAutoCommit(false);
            System.out.println("Auto-commit disabled");
            
            // Insert accounts
            try (PreparedStatement pstmt = conn.prepareStatement(
                    "INSERT INTO accounts (id, name, balance) VALUES (?, ?, ?)")) {
                
                pstmt.setInt(1, 1);
                pstmt.setString(2, "Alice");
                pstmt.setDouble(3, 1000.00);
                pstmt.executeUpdate();
                
                pstmt.setInt(1, 2);
                pstmt.setString(2, "Bob");
                pstmt.setDouble(3, 500.00);
                pstmt.executeUpdate();
                
                System.out.println("Accounts inserted (not yet committed)");
            }
            
            // Commit transaction
            conn.commit();
            System.out.println("Transaction committed successfully");
            
        } catch (SQLException e) {
            System.err.println("Transaction failed: " + e.getMessage());
            try {
                conn.rollback();
                System.out.println("Transaction rolled back");
            } catch (SQLException ex) {
                System.err.println("Rollback failed: " + ex.getMessage());
            }
        } finally {
            try {
                conn.setAutoCommit(true);
                System.out.println("Auto-commit re-enabled\n");
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
    
    /**
     * Demonstrates transaction rollback on error.
     */
    public static void demonstrateRollback(Connection conn) {
        System.out.println("=== Transaction Rollback ===");
        
        try {
            conn.setAutoCommit(false);
            
            // Check initial balances
            double aliceBalance = getBalance(conn, 1);
            double bobBalance = getBalance(conn, 2);
            System.out.println("Before transaction:");
            System.out.println("  Alice: $" + aliceBalance);
            System.out.println("  Bob: $" + bobBalance);
            
            // Attempt transfer
            try (PreparedStatement pstmt = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?")) {
                
                // Deduct from Alice
                pstmt.setDouble(1, -200.00);
                pstmt.setInt(2, 1);
                pstmt.executeUpdate();
                
                // Simulate error before crediting Bob
                throw new SQLException("Simulated error before completing transfer");
                
                // This won't execute due to error above
                // pstmt.setDouble(1, 200.00);
                // pstmt.setInt(2, 2);
                // pstmt.executeUpdate();
            }
            
        } catch (SQLException e) {
            System.err.println("Error occurred: " + e.getMessage());
            try {
                conn.rollback();
                System.out.println("Transaction rolled back - funds restored");
                
                // Verify rollback
                System.out.println("After rollback:");
                System.out.println("  Alice: $" + getBalance(conn, 1));
                System.out.println("  Bob: $" + getBalance(conn, 2));
                
            } catch (SQLException ex) {
                System.err.println("Rollback failed: " + ex.getMessage());
            }
        } finally {
            try {
                conn.setAutoCommit(true);
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates successful money transfer with transactions.
     */
    public static void demonstrateMoneyTransfer(Connection conn, int fromAccount, 
                                                int toAccount, double amount) {
        System.out.println("=== Money Transfer Transaction ===");
        System.out.println("Transferring $" + amount + " from account " + 
            fromAccount + " to account " + toAccount);
        
        try {
            conn.setAutoCommit(false);
            
            // Check sufficient balance
            double fromBalance = getBalance(conn, fromAccount);
            if (fromBalance < amount) {
                throw new SQLException("Insufficient funds in account " + fromAccount);
            }
            
            // Deduct from source
            try (PreparedStatement pstmt = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance - ? WHERE id = ?")) {
                pstmt.setDouble(1, amount);
                pstmt.setInt(2, fromAccount);
                pstmt.executeUpdate();
            }
            
            // Add to destination
            try (PreparedStatement pstmt = conn.prepareStatement(
                    "UPDATE accounts SET balance = balance + ? WHERE id = ?")) {
                pstmt.setDouble(1, amount);
                pstmt.setInt(2, toAccount);
                pstmt.executeUpdate();
            }
            
            // Log transaction
            try (PreparedStatement pstmt = conn.prepareStatement(
                    "INSERT INTO transactions (from_account, to_account, amount) VALUES (?, ?, ?)")) {
                pstmt.setInt(1, fromAccount);
                pstmt.setInt(2, toAccount);
                pstmt.setDouble(3, amount);
                pstmt.executeUpdate();
            }
            
            // Commit all changes
            conn.commit();
            System.out.println("Transfer completed successfully");
            System.out.println("  Account " + fromAccount + " balance: $" + getBalance(conn, fromAccount));
            System.out.println("  Account " + toAccount + " balance: $" + getBalance(conn, toAccount));
            
        } catch (SQLException e) {
            System.err.println("Transfer failed: " + e.getMessage());
            try {
                conn.rollback();
                System.out.println("Transfer rolled back");
            } catch (SQLException ex) {
                System.err.println("Rollback failed: " + ex.getMessage());
            }
        } finally {
            try {
                conn.setAutoCommit(true);
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates savepoints for partial rollback.
     */
    public static void demonstrateSavepoints(Connection conn) {
        System.out.println("=== Savepoints ===");
        
        try {
            conn.setAutoCommit(false);
            
            double initialBalance = getBalance(conn, 1);
            System.out.println("Initial balance (Account 1): $" + initialBalance);
            
            // First update
            updateBalance(conn, 1, -100.00);
            System.out.println("After deduction: $" + getBalance(conn, 1));
            
            // Create savepoint
            Savepoint savepoint1 = conn.setSavepoint("Savepoint1");
            System.out.println("Savepoint created");
            
            // Second update
            updateBalance(conn, 1, -50.00);
            System.out.println("After second deduction: $" + getBalance(conn, 1));
            
            // Rollback to savepoint (undo second deduction only)
            conn.rollback(savepoint1);
            System.out.println("Rolled back to savepoint");
            System.out.println("Balance after rollback: $" + getBalance(conn, 1));
            
            // Commit remaining changes
            conn.commit();
            System.out.println("Transaction committed");
            System.out.println("Final balance: $" + getBalance(conn, 1));
            
        } catch (SQLException e) {
            System.err.println("Savepoint demonstration failed: " + e.getMessage());
            try {
                conn.rollback();
            } catch (SQLException ex) {
                ex.printStackTrace();
            }
        } finally {
            try {
                conn.setAutoCommit(true);
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates transaction isolation levels.
     */
    public static void demonstrateIsolationLevels(Connection conn) {
        System.out.println("=== Transaction Isolation Levels ===");
        
        try {
            // Get current isolation level
            int currentLevel = conn.getTransactionIsolation();
            System.out.println("Current isolation level: " + getIsolationLevelName(currentLevel));
            
            // Set different isolation levels
            System.out.println("\nAvailable isolation levels:");
            
            if (conn.getMetaData().supportsTransactionIsolationLevel(
                    Connection.TRANSACTION_READ_UNCOMMITTED)) {
                System.out.println("  READ_UNCOMMITTED - supported");
            }
            
            if (conn.getMetaData().supportsTransactionIsolationLevel(
                    Connection.TRANSACTION_READ_COMMITTED)) {
                System.out.println("  READ_COMMITTED - supported");
            }
            
            if (conn.getMetaData().supportsTransactionIsolationLevel(
                    Connection.TRANSACTION_REPEATABLE_READ)) {
                System.out.println("  REPEATABLE_READ - supported");
            }
            
            if (conn.getMetaData().supportsTransactionIsolationLevel(
                    Connection.TRANSACTION_SERIALIZABLE)) {
                System.out.println("  SERIALIZABLE - supported");
            }
            
            // Set to SERIALIZABLE
            conn.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
            System.out.println("\nSet isolation level to: " + 
                getIsolationLevelName(conn.getTransactionIsolation()));
            
            // Reset to original
            conn.setTransactionIsolation(currentLevel);
            
        } catch (SQLException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates ACID properties.
     */
    public static void demonstrateACIDProperties() {
        System.out.println("=== ACID Properties ===");
        System.out.println("Atomicity: All operations in a transaction succeed or all fail");
        System.out.println("Consistency: Database remains in valid state before and after transaction");
        System.out.println("Isolation: Concurrent transactions don't interfere with each other");
        System.out.println("Durability: Committed changes are permanently stored");
        System.out.println();
    }
    
    /**
     * Helper method to get account balance.
     */
    private static double getBalance(Connection conn, int accountId) throws SQLException {
        String sql = "SELECT balance FROM accounts WHERE id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, accountId);
            ResultSet rs = pstmt.executeQuery();
            if (rs.next()) {
                return rs.getDouble("balance");
            }
        }
        return 0.0;
    }
    
    /**
     * Helper method to update account balance.
     */
    private static void updateBalance(Connection conn, int accountId, double amount) 
            throws SQLException {
        String sql = "UPDATE accounts SET balance = balance + ? WHERE id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, amount);
            pstmt.setInt(2, accountId);
            pstmt.executeUpdate();
        }
    }
    
    /**
     * Helper method to get isolation level name.
     */
    private static String getIsolationLevelName(int level) {
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
     * Main method demonstrating transaction management.
     */
    public static void main(String[] args) {
        System.out.println("JDBC Transaction Management Examples\n");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            
            initializeDatabase(conn);
            
            demonstrateACIDProperties();
            demonstrateBasicTransaction(conn);
            demonstrateRollback(conn);
            demonstrateMoneyTransfer(conn, 1, 2, 250.00);
            demonstrateSavepoints(conn);
            demonstrateIsolationLevels(conn);
            
            System.out.println("=== All transaction management examples completed ===");
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
