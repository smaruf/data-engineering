package com.microsoft.java.intermediate.exceptions;

/**
 * BasicExceptions demonstrates fundamental exception handling concepts in Java.
 * Covers try-catch-finally blocks, multiple catch blocks, and custom exceptions.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class BasicExceptions {
    
    /**
     * Custom exception class for business logic validation errors.
     */
    public static class InvalidAgeException extends Exception {
        private final int age;
        
        public InvalidAgeException(int age, String message) {
            super(message);
            this.age = age;
        }
        
        public int getAge() {
            return age;
        }
    }
    
    /**
     * Custom runtime exception for insufficient balance scenarios.
     */
    public static class InsufficientBalanceException extends RuntimeException {
        private final double balance;
        private final double requestedAmount;
        
        public InsufficientBalanceException(double balance, double requestedAmount) {
            super(String.format("Insufficient balance. Available: %.2f, Requested: %.2f", 
                balance, requestedAmount));
            this.balance = balance;
            this.requestedAmount = requestedAmount;
        }
        
        public double getBalance() {
            return balance;
        }
        
        public double getRequestedAmount() {
            return requestedAmount;
        }
    }
    
    /**
     * Demonstrates basic try-catch-finally usage.
     * 
     * @param numerator The dividend
     * @param denominator The divisor
     * @return The division result
     */
    public static double basicTryCatch(int numerator, int denominator) {
        double result = 0;
        try {
            System.out.println("Attempting division: " + numerator + "/" + denominator);
            result = numerator / denominator;
            System.out.println("Division successful: " + result);
        } catch (ArithmeticException e) {
            System.err.println("Error: Cannot divide by zero!");
            System.err.println("Exception message: " + e.getMessage());
        } finally {
            System.out.println("Finally block executed - cleanup operations here");
        }
        return result;
    }
    
    /**
     * Demonstrates multiple catch blocks for different exception types.
     * 
     * @param array The array to access
     * @param index The index to retrieve
     * @return The value at the specified index, or null if error occurs
     */
    public static String multipleCatchBlocks(String[] array, int index) {
        String result = null;
        try {
            if (array == null) {
                throw new NullPointerException("Array is null");
            }
            result = array[index];
            int length = Integer.parseInt(result);
            System.out.println("Parsed length: " + length);
        } catch (NullPointerException e) {
            System.err.println("Null pointer error: " + e.getMessage());
        } catch (ArrayIndexOutOfBoundsException e) {
            System.err.println("Invalid index: " + index + " for array length: " + 
                (array != null ? array.length : 0));
        } catch (NumberFormatException e) {
            System.err.println("Cannot parse string to number: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        } finally {
            System.out.println("Cleanup completed");
        }
        return result;
    }
    
    /**
     * Demonstrates custom checked exception usage.
     * 
     * @param age The age to validate
     * @throws InvalidAgeException if age is invalid
     */
    public static void validateAge(int age) throws InvalidAgeException {
        if (age < 0) {
            throw new InvalidAgeException(age, "Age cannot be negative");
        }
        if (age > 150) {
            throw new InvalidAgeException(age, "Age seems unrealistic");
        }
        System.out.println("Age is valid: " + age);
    }
    
    /**
     * Demonstrates custom unchecked exception usage.
     * 
     * @param balance Current account balance
     * @param amount Amount to withdraw
     * @return Remaining balance after withdrawal
     */
    public static double withdraw(double balance, double amount) {
        if (amount > balance) {
            throw new InsufficientBalanceException(balance, amount);
        }
        return balance - amount;
    }
    
    /**
     * Demonstrates exception re-throwing and wrapping.
     * 
     * @param value The value to process
     * @throws Exception if processing fails
     */
    public static void rethrowExample(String value) throws Exception {
        try {
            int parsed = Integer.parseInt(value);
            if (parsed < 0) {
                throw new IllegalArgumentException("Value must be positive");
            }
        } catch (NumberFormatException e) {
            System.err.println("Caught NumberFormatException, re-throwing as Exception");
            throw new Exception("Failed to process value: " + value, e);
        }
    }
    
    /**
     * Main method demonstrating all exception handling examples.
     */
    public static void main(String[] args) {
        System.out.println("=== Basic Try-Catch-Finally ===");
        basicTryCatch(10, 2);
        basicTryCatch(10, 0);
        
        System.out.println("\n=== Multiple Catch Blocks ===");
        String[] testArray = {"apple", "banana", "cherry"};
        multipleCatchBlocks(testArray, 1);
        multipleCatchBlocks(testArray, 10);
        multipleCatchBlocks(null, 0);
        
        System.out.println("\n=== Custom Checked Exception ===");
        try {
            validateAge(25);
            validateAge(-5);
        } catch (InvalidAgeException e) {
            System.err.println("Validation failed: " + e.getMessage());
            System.err.println("Invalid age was: " + e.getAge());
        }
        
        System.out.println("\n=== Custom Unchecked Exception ===");
        try {
            double balance = 1000.0;
            System.out.println("Current balance: " + balance);
            balance = withdraw(balance, 500.0);
            System.out.println("After withdrawal: " + balance);
            balance = withdraw(balance, 1000.0);
        } catch (InsufficientBalanceException e) {
            System.err.println("Withdrawal failed: " + e.getMessage());
            System.err.println("Available: " + e.getBalance());
            System.err.println("Requested: " + e.getRequestedAmount());
        }
        
        System.out.println("\n=== Exception Re-throwing ===");
        try {
            rethrowExample("42");
            rethrowExample("invalid");
        } catch (Exception e) {
            System.err.println("Caught exception: " + e.getMessage());
            if (e.getCause() != null) {
                System.err.println("Caused by: " + e.getCause().getMessage());
            }
        }
    }
}
