package com.microsoft.java.intermediate.exceptions;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.logging.*;

/**
 * ExceptionBestPractices demonstrates modern exception handling patterns in Java.
 * Covers try-with-resources, exception chaining, proper logging, and best practices.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class ExceptionBestPractices {
    
    private static final Logger logger = Logger.getLogger(ExceptionBestPractices.class.getName());
    
    /**
     * Demonstrates try-with-resources for automatic resource management.
     * Resources are automatically closed in reverse order of creation.
     * 
     * @param filename File to read
     * @return File contents
     */
    public static String tryWithResourcesSingle(String filename) {
        StringBuilder content = new StringBuilder();
        
        // Try-with-resources: BufferedReader is automatically closed
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
            logger.info("Successfully read file: " + filename);
        } catch (FileNotFoundException e) {
            logger.warning("File not found: " + filename);
            content.append("Error: File not found");
        } catch (IOException e) {
            logger.severe("IO error reading file: " + e.getMessage());
            content.append("Error: IO exception");
        }
        
        return content.toString();
    }
    
    /**
     * Demonstrates try-with-resources with multiple resources.
     * 
     * @param sourceFile Source file to copy from
     * @param targetFile Target file to copy to
     * @return true if successful, false otherwise
     */
    public static boolean tryWithResourcesMultiple(String sourceFile, String targetFile) {
        // Multiple resources separated by semicolons
        try (BufferedReader reader = new BufferedReader(new FileReader(sourceFile));
             BufferedWriter writer = new BufferedWriter(new FileWriter(targetFile))) {
            
            String line;
            int lineCount = 0;
            while ((line = reader.readLine()) != null) {
                writer.write(line);
                writer.newLine();
                lineCount++;
            }
            
            logger.info(String.format("Copied %d lines from %s to %s", 
                lineCount, sourceFile, targetFile));
            return true;
            
        } catch (IOException e) {
            logger.severe("Error copying file: " + e.getMessage());
            return false;
        }
        // Both reader and writer are automatically closed here
    }
    
    /**
     * Custom AutoCloseable resource for demonstration.
     */
    public static class DatabaseConnection implements AutoCloseable {
        private final String connectionId;
        private boolean isOpen;
        
        public DatabaseConnection(String connectionId) throws Exception {
            this.connectionId = connectionId;
            this.isOpen = true;
            logger.info("Opening connection: " + connectionId);
            
            // Simulate connection failure
            if (connectionId.contains("invalid")) {
                throw new Exception("Invalid connection ID");
            }
        }
        
        public void executeQuery(String query) {
            if (!isOpen) {
                throw new IllegalStateException("Connection is closed");
            }
            logger.info("Executing query: " + query);
        }
        
        @Override
        public void close() {
            if (isOpen) {
                logger.info("Closing connection: " + connectionId);
                isOpen = false;
            }
        }
    }
    
    /**
     * Demonstrates try-with-resources with custom AutoCloseable.
     * 
     * @param connectionId Connection identifier
     */
    public static void tryWithCustomResource(String connectionId) {
        try (DatabaseConnection conn = new DatabaseConnection(connectionId)) {
            conn.executeQuery("SELECT * FROM users");
            conn.executeQuery("SELECT * FROM orders");
        } catch (Exception e) {
            logger.severe("Database operation failed: " + e.getMessage());
        }
        // Connection is automatically closed even if exception occurs
    }
    
    /**
     * Demonstrates exception chaining to preserve original cause.
     * 
     * @param data Data to process
     * @throws Exception if processing fails
     */
    public static void exceptionChaining(String data) throws Exception {
        try {
            processData(data);
        } catch (NumberFormatException e) {
            // Chain the original exception as the cause
            throw new Exception("Failed to process data: " + data, e);
        }
    }
    
    private static void processData(String data) {
        int value = Integer.parseInt(data);
        logger.info("Processed value: " + value);
    }
    
    /**
     * Demonstrates proper exception wrapping with business context.
     */
    public static class DataProcessingException extends Exception {
        private final String dataId;
        private final String operation;
        
        public DataProcessingException(String dataId, String operation, 
                                      String message, Throwable cause) {
            super(String.format("Data processing failed [ID: %s, Operation: %s]: %s", 
                dataId, operation, message), cause);
            this.dataId = dataId;
            this.operation = operation;
        }
        
        public String getDataId() {
            return dataId;
        }
        
        public String getOperation() {
            return operation;
        }
    }
    
    /**
     * Demonstrates business exception wrapping.
     * 
     * @param dataId Data identifier
     * @param value Value to process
     * @throws DataProcessingException if processing fails
     */
    public static void businessExceptionWrapping(String dataId, String value) 
            throws DataProcessingException {
        try {
            int numValue = Integer.parseInt(value);
            if (numValue < 0) {
                throw new IllegalArgumentException("Value must be positive");
            }
            logger.info("Processed data " + dataId + ": " + numValue);
        } catch (NumberFormatException e) {
            throw new DataProcessingException(dataId, "PARSE", 
                "Invalid number format", e);
        } catch (IllegalArgumentException e) {
            throw new DataProcessingException(dataId, "VALIDATE", 
                "Validation failed", e);
        }
    }
    
    /**
     * Demonstrates proper exception logging with different levels.
     * 
     * @param operation Operation to perform
     */
    public static void properExceptionLogging(String operation) {
        try {
            if (operation.equals("warn")) {
                logger.warning("This is a warning - recoverable issue");
            } else if (operation.equals("error")) {
                throw new RuntimeException("Critical error occurred");
            } else {
                logger.info("Operation completed: " + operation);
            }
        } catch (RuntimeException e) {
            // Log with stack trace
            logger.log(Level.SEVERE, "Operation failed: " + operation, e);
            
            // Don't log and throw - choose one
            throw e;
        }
    }
    
    /**
     * Demonstrates exception handling best practices.
     * 
     * @param input Input to validate
     * @return Processed result
     */
    public static String bestPracticesExample(String input) {
        // 1. Validate input early
        Objects.requireNonNull(input, "Input cannot be null");
        
        if (input.trim().isEmpty()) {
            throw new IllegalArgumentException("Input cannot be empty");
        }
        
        // 2. Use specific exceptions
        try {
            return processInput(input);
        } catch (NumberFormatException e) {
            // 3. Catch specific exceptions first
            logger.warning("Invalid number format: " + input);
            return "0";
        } catch (IllegalArgumentException e) {
            // 4. Provide context in error messages
            logger.warning("Invalid input '" + input + "': " + e.getMessage());
            return "ERROR";
        } catch (Exception e) {
            // 5. Catch general exceptions last
            logger.severe("Unexpected error: " + e.getMessage());
            return "UNKNOWN_ERROR";
        }
    }
    
    private static String processInput(String input) {
        // Business logic here
        return input.toUpperCase();
    }
    
    /**
     * Demonstrates proper resource cleanup without try-with-resources.
     * 
     * @param filename File to read
     * @return Line count
     */
    public static int manualResourceCleanup(String filename) {
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(new FileReader(filename));
            int count = 0;
            while (reader.readLine() != null) {
                count++;
            }
            return count;
        } catch (IOException e) {
            logger.severe("Error reading file: " + e.getMessage());
            return -1;
        } finally {
            // Always close in finally block
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    logger.warning("Error closing reader: " + e.getMessage());
                }
            }
        }
    }
    
    /**
     * Demonstrates suppressed exceptions with try-with-resources.
     */
    public static class FailingResource implements AutoCloseable {
        private final String name;
        
        public FailingResource(String name) {
            this.name = name;
        }
        
        public void doWork() throws Exception {
            logger.info(name + " doing work");
            throw new Exception("Work failed in " + name);
        }
        
        @Override
        public void close() throws Exception {
            logger.info(name + " closing");
            throw new Exception("Close failed in " + name);
        }
    }
    
    /**
     * Demonstrates suppressed exceptions.
     */
    public static void suppressedExceptionsExample() {
        try (FailingResource resource = new FailingResource("Resource1")) {
            resource.doWork();
        } catch (Exception e) {
            logger.severe("Primary exception: " + e.getMessage());
            
            // Get suppressed exceptions
            Throwable[] suppressed = e.getSuppressed();
            for (Throwable t : suppressed) {
                logger.warning("Suppressed exception: " + t.getMessage());
            }
        }
    }
    
    /**
     * Main method demonstrating exception best practices.
     */
    public static void main(String[] args) {
        // Configure logging
        Logger rootLogger = Logger.getLogger("");
        rootLogger.setLevel(Level.ALL);
        for (Handler handler : rootLogger.getHandlers()) {
            handler.setLevel(Level.ALL);
        }
        
        System.out.println("=== Try-With-Resources - Single ===");
        String content = tryWithResourcesSingle("test.txt");
        System.out.println("Content preview: " + 
            (content.length() > 50 ? content.substring(0, 50) + "..." : content));
        
        System.out.println("\n=== Try-With-Resources - Multiple ===");
        // Create a test file first
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("source.txt"))) {
            writer.write("Line 1\nLine 2\nLine 3\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
        tryWithResourcesMultiple("source.txt", "target.txt");
        
        System.out.println("\n=== Custom AutoCloseable Resource ===");
        tryWithCustomResource("conn-123");
        tryWithCustomResource("invalid-conn");
        
        System.out.println("\n=== Exception Chaining ===");
        try {
            exceptionChaining("42");
            exceptionChaining("invalid");
        } catch (Exception e) {
            System.err.println("Caught: " + e.getMessage());
            if (e.getCause() != null) {
                System.err.println("Caused by: " + e.getCause().getClass().getSimpleName());
            }
        }
        
        System.out.println("\n=== Business Exception Wrapping ===");
        try {
            businessExceptionWrapping("DATA-001", "100");
            businessExceptionWrapping("DATA-002", "abc");
        } catch (DataProcessingException e) {
            System.err.println("Error: " + e.getMessage());
            System.err.println("Data ID: " + e.getDataId());
            System.err.println("Operation: " + e.getOperation());
        }
        
        System.out.println("\n=== Best Practices Example ===");
        bestPracticesExample("hello");
        bestPracticesExample("");
        
        System.out.println("\n=== Suppressed Exceptions ===");
        suppressedExceptionsExample();
        
        // Cleanup
        new File("source.txt").delete();
        new File("target.txt").delete();
    }
}
