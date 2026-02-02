package com.microsoft.java.basics;

/**
 * HelloWorld - Introduction to Java Programming.
 *
 * <p>This class demonstrates the most basic Java program structure including:
 * - Package declaration
 * - Class definition
 * - Main method (entry point)
 * - Comments (single-line, multi-line, and JavaDoc)
 * - Output to console
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class HelloWorld {

  /**
   * Main method - the entry point of any Java application.
   *
   * <p>The JVM looks for this method to start program execution.
   * Method signature must be: public static void main(String[] args)
   *
   * @param args command-line arguments passed to the program
   */
  public static void main(String[] args) {
    // Single-line comment: Print a simple greeting
    System.out.println("Hello, World!");

    /*
     * Multi-line comment:
     * Demonstrating different ways to output to console
     */
    System.out.println("Welcome to Java Programming!");

    // Using System.out.print (no newline)
    System.out.print("This is ");
    System.out.print("printed ");
    System.out.println("on the same line.");

    // Formatted output using printf
    String name = "Developer";
    int year = 2024;
    System.out.printf("Hello, %s! Welcome to Java in %d!%n", name, year);

    // Demonstrating command-line arguments
    if (args.length > 0) {
      System.out.println("\nCommand-line arguments received:");
      for (int i = 0; i < args.length; i++) {
        System.out.printf("  Argument %d: %s%n", i, args[i]);
      }
    } else {
      System.out.println("\nNo command-line arguments provided.");
      System.out.println("Try running: java HelloWorld arg1 arg2 arg3");
    }

    // String concatenation
    String message = "Java" + " is" + " awesome!";
    System.out.println("\n" + message);

    // Special characters
    System.out.println("\nSpecial Characters:");
    System.out.println("Tab:\tText after tab");
    System.out.println("Newline:\nText on new line");
    System.out.println("Quote: \"Hello\"");
    System.out.println("Backslash: \\");
  }
}
