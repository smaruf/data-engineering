package com.microsoft.java.intermediate.exceptions;

import java.io.*;
import java.sql.*;
import java.net.*;

/**
 * CheckedExceptions demonstrates handling of checked exceptions in Java.
 * Covers IOException, SQLException, and other common checked exceptions.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class CheckedExceptions {
    
    /**
     * Demonstrates IOException handling with file operations.
     * 
     * @param filename The file to read
     * @return File contents or error message
     */
    public static String readFileWithIOException(String filename) {
        StringBuilder content = new StringBuilder();
        BufferedReader reader = null;
        
        try {
            reader = new BufferedReader(new FileReader(filename));
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
            System.out.println("Successfully read file: " + filename);
        } catch (FileNotFoundException e) {
            String error = "File not found: " + filename;
            System.err.println(error);
            content.append(error);
        } catch (IOException e) {
            String error = "Error reading file: " + e.getMessage();
            System.err.println(error);
            content.append(error);
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                    System.out.println("File reader closed");
                } catch (IOException e) {
                    System.err.println("Error closing reader: " + e.getMessage());
                }
            }
        }
        
        return content.toString();
    }
    
    /**
     * Demonstrates writing to a file with proper exception handling.
     * 
     * @param filename The file to write to
     * @param content The content to write
     * @return true if successful, false otherwise
     */
    public static boolean writeFileWithIOException(String filename, String content) {
        BufferedWriter writer = null;
        
        try {
            writer = new BufferedWriter(new FileWriter(filename));
            writer.write(content);
            writer.flush();
            System.out.println("Successfully wrote to file: " + filename);
            return true;
        } catch (IOException e) {
            System.err.println("Error writing to file: " + e.getMessage());
            return false;
        } finally {
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                    System.err.println("Error closing writer: " + e.getMessage());
                }
            }
        }
    }
    
    /**
     * Demonstrates SQLException handling (simulated).
     * In production, this would connect to a real database.
     * 
     * @param url Database URL
     * @param username Database username
     * @param password Database password
     */
    public static void handleSQLException(String url, String username, String password) {
        Connection connection = null;
        Statement statement = null;
        ResultSet resultSet = null;
        
        try {
            // Simulated database connection
            System.out.println("Attempting to connect to database...");
            // connection = DriverManager.getConnection(url, username, password);
            
            // This will throw SQLException in real scenario
            throw new SQLException("Simulated database connection error", "08001", 1001);
            
        } catch (SQLException e) {
            System.err.println("SQL Exception occurred:");
            System.err.println("  Message: " + e.getMessage());
            System.err.println("  SQL State: " + e.getSQLState());
            System.err.println("  Error Code: " + e.getErrorCode());
            
            // Handle specific SQL error codes
            if (e.getErrorCode() == 1001) {
                System.err.println("  → Connection failed. Check network and credentials.");
            }
            
            // Chain of SQL exceptions
            SQLException nextException = e.getNextException();
            while (nextException != null) {
                System.err.println("  Chained Exception: " + nextException.getMessage());
                nextException = nextException.getNextException();
            }
            
        } finally {
            // Close resources in reverse order
            try {
                if (resultSet != null) resultSet.close();
                if (statement != null) statement.close();
                if (connection != null) connection.close();
                System.out.println("Database resources closed");
            } catch (SQLException e) {
                System.err.println("Error closing database resources: " + e.getMessage());
            }
        }
    }
    
    /**
     * Demonstrates handling multiple checked exceptions.
     * 
     * @param urlString The URL to connect to
     * @param outputFile File to write response to
     */
    public static void handleMultipleCheckedExceptions(String urlString, String outputFile) {
        try {
            // URL and network operations
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            
            int responseCode = connection.getResponseCode();
            System.out.println("Response Code: " + responseCode);
            
            if (responseCode == 200) {
                // Read response
                BufferedReader in = new BufferedReader(
                    new InputStreamReader(connection.getInputStream()));
                String inputLine;
                StringBuilder response = new StringBuilder();
                
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine).append("\n");
                }
                in.close();
                
                // Write to file
                writeFileWithIOException(outputFile, response.toString());
            }
            
        } catch (MalformedURLException e) {
            System.err.println("Invalid URL: " + e.getMessage());
        } catch (ProtocolException e) {
            System.err.println("Invalid protocol: " + e.getMessage());
        } catch (SocketTimeoutException e) {
            System.err.println("Connection timeout: " + e.getMessage());
        } catch (IOException e) {
            System.err.println("IO Error: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates exception handling with Class.forName() and reflection.
     * 
     * @param className The class name to load
     */
    public static void handleClassNotFoundException(String className) {
        try {
            Class<?> clazz = Class.forName(className);
            System.out.println("Successfully loaded class: " + clazz.getName());
            
            // Create instance
            Object instance = clazz.getDeclaredConstructor().newInstance();
            System.out.println("Created instance: " + instance.getClass().getSimpleName());
            
        } catch (ClassNotFoundException e) {
            System.err.println("Class not found: " + className);
        } catch (NoSuchMethodException e) {
            System.err.println("No default constructor found for: " + className);
        } catch (InstantiationException e) {
            System.err.println("Cannot instantiate abstract class or interface: " + className);
        } catch (IllegalAccessException e) {
            System.err.println("Cannot access constructor: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates throws clause propagation.
     * 
     * @param filename File to process
     * @throws IOException if file operations fail
     */
    public static void propagateCheckedException(String filename) throws IOException {
        // Method declares IOException, letting caller handle it
        BufferedReader reader = new BufferedReader(new FileReader(filename));
        String line = reader.readLine();
        System.out.println("First line: " + line);
        reader.close();
    }
    
    /**
     * Main method demonstrating checked exception handling.
     */
    public static void main(String[] args) {
        System.out.println("=== IOException Handling - Read File ===");
        readFileWithIOException("test-input.txt");
        
        System.out.println("\n=== IOException Handling - Write File ===");
        writeFileWithIOException("test-output.txt", "Hello from Java!\nThis is a test file.\n");
        
        System.out.println("\n=== SQLException Handling ===");
        handleSQLException("jdbc:mysql://localhost:3306/testdb", "user", "password");
        
        System.out.println("\n=== Multiple Checked Exceptions ===");
        handleMultipleCheckedExceptions("https://httpbin.org/get", "response.txt");
        
        System.out.println("\n=== ClassNotFoundException Handling ===");
        handleClassNotFoundException("java.lang.String");
        handleClassNotFoundException("com.nonexistent.MyClass");
        
        System.out.println("\n=== Exception Propagation ===");
        try {
            propagateCheckedException("nonexistent.txt");
        } catch (IOException e) {
            System.err.println("Caught propagated exception: " + e.getMessage());
        }
        
        System.out.println("\n=== Cleanup Test File ===");
        File testFile = new File("test-output.txt");
        if (testFile.exists()) {
            boolean deleted = testFile.delete();
            System.out.println("Test file deleted: " + deleted);
        }
    }
}
