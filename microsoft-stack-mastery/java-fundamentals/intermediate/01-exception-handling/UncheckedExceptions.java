package com.microsoft.java.intermediate.exceptions;

import java.util.*;

/**
 * UncheckedExceptions demonstrates handling of runtime exceptions in Java.
 * Covers RuntimeException, NullPointerException, IllegalArgumentException, etc.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class UncheckedExceptions {
    
    /**
     * Demonstrates NullPointerException handling and prevention.
     * 
     * @param input The string to process (may be null)
     * @return Processed string or default value
     */
    public static String handleNullPointerException(String input) {
        try {
            // Unsafe operation that may throw NullPointerException
            String result = input.toUpperCase();
            System.out.println("Converted to uppercase: " + result);
            return result;
        } catch (NullPointerException e) {
            System.err.println("Caught NullPointerException: Input was null");
            return "DEFAULT_VALUE";
        }
    }
    
    /**
     * Demonstrates defensive null checking to prevent NullPointerException.
     * 
     * @param input The string to process (may be null)
     * @return Processed string or default value
     */
    public static String preventNullPointerException(String input) {
        // Defensive programming - check for null
        if (input == null) {
            System.out.println("Input is null, using default value");
            return "DEFAULT_VALUE";
        }
        
        // Using Optional (Java 8+)
        String result = Optional.ofNullable(input)
            .map(String::toUpperCase)
            .orElse("DEFAULT_VALUE");
        
        System.out.println("Result: " + result);
        return result;
    }
    
    /**
     * Demonstrates ArrayIndexOutOfBoundsException handling.
     * 
     * @param array The array to access
     * @param index The index to retrieve
     * @return Value at index or null if out of bounds
     */
    public static Integer handleArrayIndexOutOfBounds(int[] array, int index) {
        try {
            int value = array[index];
            System.out.println("Value at index " + index + ": " + value);
            return value;
        } catch (ArrayIndexOutOfBoundsException e) {
            System.err.println("Invalid index: " + index + 
                " (array length: " + array.length + ")");
            return null;
        }
    }
    
    /**
     * Demonstrates safe array access with bounds checking.
     * 
     * @param array The array to access
     * @param index The index to retrieve
     * @return Value at index or null if out of bounds
     */
    public static Integer safeArrayAccess(int[] array, int index) {
        if (array == null) {
            System.err.println("Array is null");
            return null;
        }
        
        if (index < 0 || index >= array.length) {
            System.err.println("Index out of bounds: " + index);
            return null;
        }
        
        return array[index];
    }
    
    /**
     * Demonstrates NumberFormatException handling.
     * 
     * @param input The string to parse
     * @return Parsed integer or default value
     */
    public static int handleNumberFormatException(String input) {
        try {
            int number = Integer.parseInt(input);
            System.out.println("Parsed number: " + number);
            return number;
        } catch (NumberFormatException e) {
            System.err.println("Cannot parse '" + input + "' to integer: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * Demonstrates safe number parsing with validation.
     * 
     * @param input The string to parse
     * @param defaultValue Default value if parsing fails
     * @return Parsed integer or default value
     */
    public static int safeParseInt(String input, int defaultValue) {
        if (input == null || input.trim().isEmpty()) {
            System.out.println("Input is null or empty, using default: " + defaultValue);
            return defaultValue;
        }
        
        try {
            return Integer.parseInt(input.trim());
        } catch (NumberFormatException e) {
            System.err.println("Invalid number format, using default: " + defaultValue);
            return defaultValue;
        }
    }
    
    /**
     * Demonstrates IllegalArgumentException for input validation.
     * 
     * @param age Age to validate
     * @param name Name to validate
     * @throws IllegalArgumentException if validation fails
     */
    public static void validateInput(int age, String name) {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException(
                "Age must be between 0 and 150, got: " + age);
        }
        
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException(
                "Name cannot be null or empty");
        }
        
        if (name.length() < 2) {
            throw new IllegalArgumentException(
                "Name must be at least 2 characters long");
        }
        
        System.out.println("Valid input - Age: " + age + ", Name: " + name);
    }
    
    /**
     * Demonstrates IllegalStateException for object state validation.
     */
    public static class BankAccount {
        private double balance;
        private boolean isActive;
        
        public BankAccount(double initialBalance) {
            this.balance = initialBalance;
            this.isActive = true;
        }
        
        public void withdraw(double amount) {
            if (!isActive) {
                throw new IllegalStateException("Account is not active");
            }
            
            if (amount <= 0) {
                throw new IllegalArgumentException("Amount must be positive");
            }
            
            if (amount > balance) {
                throw new IllegalStateException(
                    String.format("Insufficient balance: %.2f (requested: %.2f)", 
                        balance, amount));
            }
            
            balance -= amount;
            System.out.println(String.format("Withdrew %.2f, remaining: %.2f", 
                amount, balance));
        }
        
        public void closeAccount() {
            isActive = false;
            System.out.println("Account closed");
        }
        
        public double getBalance() {
            return balance;
        }
    }
    
    /**
     * Demonstrates ArithmeticException handling.
     * 
     * @param numerator The dividend
     * @param denominator The divisor
     * @return Division result or null if error occurs
     */
    public static Double handleArithmeticException(int numerator, int denominator) {
        try {
            double result = numerator / denominator;
            System.out.println(numerator + " / " + denominator + " = " + result);
            return result;
        } catch (ArithmeticException e) {
            System.err.println("Arithmetic error: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Demonstrates ClassCastException handling.
     * 
     * @param obj Object to cast
     * @return String representation or error message
     */
    public static String handleClassCastException(Object obj) {
        try {
            String str = (String) obj;
            System.out.println("Successfully cast to String: " + str);
            return str;
        } catch (ClassCastException e) {
            System.err.println("Cannot cast " + obj.getClass().getName() + 
                " to String");
            return obj.toString();
        }
    }
    
    /**
     * Demonstrates safe casting using instanceof.
     * 
     * @param obj Object to cast
     * @return String representation
     */
    public static String safeCast(Object obj) {
        if (obj instanceof String) {
            return (String) obj;
        } else {
            System.out.println("Object is not a String, converting: " + 
                obj.getClass().getSimpleName());
            return obj.toString();
        }
    }
    
    /**
     * Main method demonstrating unchecked exception handling.
     */
    public static void main(String[] args) {
        System.out.println("=== NullPointerException Handling ===");
        handleNullPointerException("hello");
        handleNullPointerException(null);
        
        System.out.println("\n=== NullPointerException Prevention ===");
        preventNullPointerException("world");
        preventNullPointerException(null);
        
        System.out.println("\n=== ArrayIndexOutOfBoundsException ===");
        int[] numbers = {10, 20, 30, 40, 50};
        handleArrayIndexOutOfBounds(numbers, 2);
        handleArrayIndexOutOfBounds(numbers, 10);
        
        System.out.println("\n=== Safe Array Access ===");
        safeArrayAccess(numbers, 3);
        safeArrayAccess(numbers, -1);
        safeArrayAccess(null, 0);
        
        System.out.println("\n=== NumberFormatException ===");
        handleNumberFormatException("42");
        handleNumberFormatException("abc");
        handleNumberFormatException("12.34");
        
        System.out.println("\n=== Safe Number Parsing ===");
        safeParseInt("100", 0);
        safeParseInt("invalid", -1);
        safeParseInt(null, 99);
        
        System.out.println("\n=== IllegalArgumentException ===");
        try {
            validateInput(25, "John Doe");
            validateInput(-5, "Jane");
        } catch (IllegalArgumentException e) {
            System.err.println("Validation failed: " + e.getMessage());
        }
        
        try {
            validateInput(30, "");
        } catch (IllegalArgumentException e) {
            System.err.println("Validation failed: " + e.getMessage());
        }
        
        System.out.println("\n=== IllegalStateException ===");
        BankAccount account = new BankAccount(1000.0);
        try {
            account.withdraw(500.0);
            account.closeAccount();
            account.withdraw(100.0);
        } catch (IllegalStateException e) {
            System.err.println("Operation failed: " + e.getMessage());
        }
        
        System.out.println("\n=== ArithmeticException ===");
        handleArithmeticException(10, 2);
        handleArithmeticException(10, 0);
        
        System.out.println("\n=== ClassCastException ===");
        handleClassCastException("Hello");
        handleClassCastException(123);
        
        System.out.println("\n=== Safe Casting ===");
        safeCast("World");
        safeCast(456);
        safeCast(new ArrayList<>());
    }
}
