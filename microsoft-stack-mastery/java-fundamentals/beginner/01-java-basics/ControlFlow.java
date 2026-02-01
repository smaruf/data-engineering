package com.microsoft.java.basics;

import java.util.Scanner;

/**
 * ControlFlow - Comprehensive demonstration of control flow statements in Java.
 *
 * <p>This class covers:
 * - Conditional statements (if-else, switch)
 * - Loops (for, while, do-while)
 * - Loop control (break, continue)
 * - Nested control structures
 * - Real-world use cases
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class ControlFlow {

  /**
   * Main method demonstrating various control flow statements.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Control Flow Demonstration ===\n");

    demonstrateIfElse();
    demonstrateSwitchStatement();
    demonstrateSwitchExpression();
    demonstrateForLoop();
    demonstrateWhileLoop();
    demonstrateDoWhileLoop();
    demonstrateBreakContinue();
    demonstrateNestedLoops();
    realWorldExamples();
  }

  /**
   * Demonstrates if-else conditional statements.
   */
  private static void demonstrateIfElse() {
    System.out.println("--- If-Else Statements ---");

    int score = 85;

    // Simple if
    if (score >= 90) {
      System.out.println("Grade: A");
    }

    // If-else
    if (score >= 90) {
      System.out.println("Grade: A (Excellent!)");
    } else {
      System.out.println("Grade: Below A");
    }

    // If-else-if ladder
    if (score >= 90) {
      System.out.println("Grade: A");
    } else if (score >= 80) {
      System.out.println("Grade: B");
    } else if (score >= 70) {
      System.out.println("Grade: C");
    } else if (score >= 60) {
      System.out.println("Grade: D");
    } else {
      System.out.println("Grade: F");
    }

    // Nested if
    boolean isPassed = score >= 60;
    boolean hasBonus = true;

    if (isPassed) {
      System.out.println("Status: Passed");
      if (hasBonus) {
        System.out.println("You earned a bonus!");
      }
    } else {
      System.out.println("Status: Failed");
    }

    // Ternary operator (short if-else)
    String result = (score >= 60) ? "Pass" : "Fail";
    System.out.println("Result using ternary: " + result);

    // Logical operators in conditions
    int age = 25;
    boolean hasLicense = true;

    if (age >= 18 && hasLicense) {
      System.out.println("Can drive: Yes");
    }

    if (age < 18 || !hasLicense) {
      System.out.println("Some driving restriction applies");
    }

    System.out.println();
  }

  /**
   * Demonstrates traditional switch statement.
   */
  private static void demonstrateSwitchStatement() {
    System.out.println("--- Switch Statement (Traditional) ---");

    int dayOfWeek = 3;

    // Traditional switch with break
    switch (dayOfWeek) {
      case 1:
        System.out.println("Monday - Start of work week");
        break;
      case 2:
        System.out.println("Tuesday");
        break;
      case 3:
        System.out.println("Wednesday - Midweek");
        break;
      case 4:
        System.out.println("Thursday");
        break;
      case 5:
        System.out.println("Friday - TGIF!");
        break;
      case 6:
      case 7:
        System.out.println("Weekend!");
        break;
      default:
        System.out.println("Invalid day");
    }

    // Switch with String
    String month = "March";
    int days;

    switch (month) {
      case "January":
      case "March":
      case "May":
      case "July":
      case "August":
      case "October":
      case "December":
        days = 31;
        break;
      case "April":
      case "June":
      case "September":
      case "November":
        days = 30;
        break;
      case "February":
        days = 28; // Not considering leap year
        break;
      default:
        days = 0;
        System.out.println("Invalid month");
    }

    System.out.println(month + " has " + days + " days");

    System.out.println();
  }

  /**
   * Demonstrates switch expression (Java 12+).
   */
  private static void demonstrateSwitchExpression() {
    System.out.println("--- Switch Expression (Java 12+) ---");

    int dayOfWeek = 5;

    // Switch expression with arrow syntax
    String dayType = switch (dayOfWeek) {
      case 1, 2, 3, 4, 5 -> "Weekday";
      case 6, 7 -> "Weekend";
      default -> "Invalid day";
    };

    System.out.println("Day " + dayOfWeek + " is a " + dayType);

    // Switch expression with yield
    String month = "February";
    int days = switch (month) {
      case "January", "March", "May", "July", "August", "October", "December" -> 31;
      case "April", "June", "September", "November" -> 30;
      case "February" -> {
        System.out.println("Checking if leap year...");
        yield 28; // Use yield for block statements
      }
      default -> throw new IllegalArgumentException("Invalid month: " + month);
    };

    System.out.println(month + " has " + days + " days");

    System.out.println();
  }

  /**
   * Demonstrates for loop variations.
   */
  private static void demonstrateForLoop() {
    System.out.println("--- For Loops ---");

    // Traditional for loop
    System.out.println("Counting 1 to 5:");
    for (int i = 1; i <= 5; i++) {
      System.out.print(i + " ");
    }
    System.out.println();

    // Counting backwards
    System.out.println("\nCountdown from 5:");
    for (int i = 5; i >= 1; i--) {
      System.out.print(i + " ");
    }
    System.out.println();

    // Increment by 2
    System.out.println("\nEven numbers 2 to 10:");
    for (int i = 2; i <= 10; i += 2) {
      System.out.print(i + " ");
    }
    System.out.println();

    // Enhanced for loop (for-each)
    System.out.println("\nIterating array with for-each:");
    String[] fruits = {"Apple", "Banana", "Orange", "Grape"};
    for (String fruit : fruits) {
      System.out.println("  - " + fruit);
    }

    // Multiple variables in for loop
    System.out.println("\nMultiple variables:");
    for (int i = 0, j = 10; i < j; i++, j--) {
      System.out.println("  i=" + i + ", j=" + j);
    }

    System.out.println();
  }

  /**
   * Demonstrates while loop.
   */
  private static void demonstrateWhileLoop() {
    System.out.println("--- While Loop ---");

    // Basic while loop
    int count = 1;
    System.out.println("Counting with while loop:");
    while (count <= 5) {
      System.out.print(count + " ");
      count++;
    }
    System.out.println();

    // While loop with condition
    System.out.println("\nSum of numbers until total exceeds 50:");
    int sum = 0;
    int num = 1;
    while (sum <= 50) {
      sum += num;
      System.out.println("  Added " + num + ", total: " + sum);
      num++;
    }

    // Infinite loop (commented out for safety)
    // while (true) {
    //   System.out.println("This runs forever!");
    //   break; // Need break to exit
    // }

    System.out.println();
  }

  /**
   * Demonstrates do-while loop.
   */
  private static void demonstrateDoWhileLoop() {
    System.out.println("--- Do-While Loop ---");

    // Do-while executes at least once
    int count = 1;
    System.out.println("Do-while loop (count 1 to 5):");
    do {
      System.out.print(count + " ");
      count++;
    } while (count <= 5);
    System.out.println();

    // Difference: do-while executes even if condition is false initially
    System.out.println("\nDo-while vs While comparison:");
    int x = 10;

    System.out.println("While loop with x=10, condition x<5:");
    while (x < 5) {
      System.out.println("This won't print");
    }
    System.out.println("  (Loop body never executed)");

    System.out.println("\nDo-While loop with x=10, condition x<5:");
    do {
      System.out.println("  This prints once despite condition being false");
    } while (x < 5);

    System.out.println();
  }

  /**
   * Demonstrates break and continue statements.
   */
  private static void demonstrateBreakContinue() {
    System.out.println("--- Break and Continue ---");

    // Break: exits the loop
    System.out.println("Break example - stop at 5:");
    for (int i = 1; i <= 10; i++) {
      if (i == 5) {
        System.out.println("  Breaking at " + i);
        break;
      }
      System.out.print(i + " ");
    }
    System.out.println();

    // Continue: skips current iteration
    System.out.println("\nContinue example - skip odd numbers:");
    for (int i = 1; i <= 10; i++) {
      if (i % 2 != 0) {
        continue; // Skip odd numbers
      }
      System.out.print(i + " ");
    }
    System.out.println();

    // Labeled break (for nested loops)
    System.out.println("\nLabeled break in nested loop:");
    outerLoop:
    for (int i = 1; i <= 3; i++) {
      for (int j = 1; j <= 3; j++) {
        if (i == 2 && j == 2) {
          System.out.println("  Breaking outer loop at i=" + i + ", j=" + j);
          break outerLoop;
        }
        System.out.println("  i=" + i + ", j=" + j);
      }
    }

    System.out.println();
  }

  /**
   * Demonstrates nested loops.
   */
  private static void demonstrateNestedLoops() {
    System.out.println("--- Nested Loops ---");

    // Multiplication table
    System.out.println("Multiplication table (5x5):");
    for (int i = 1; i <= 5; i++) {
      for (int j = 1; j <= 5; j++) {
        System.out.printf("%4d", i * j);
      }
      System.out.println();
    }

    // Pattern printing
    System.out.println("\nTriangle pattern:");
    for (int i = 1; i <= 5; i++) {
      for (int j = 1; j <= i; j++) {
        System.out.print("* ");
      }
      System.out.println();
    }

    System.out.println("\nInverted triangle:");
    for (int i = 5; i >= 1; i--) {
      for (int j = 1; j <= i; j++) {
        System.out.print("* ");
      }
      System.out.println();
    }

    System.out.println();
  }

  /**
   * Demonstrates real-world use cases of control flow.
   */
  private static void realWorldExamples() {
    System.out.println("--- Real-World Examples ---");

    // Example 1: Validating user input
    validateUserAge(25);
    validateUserAge(150);

    // Example 2: Processing business logic
    calculateShippingCost(45.00);
    calculateShippingCost(125.00);

    // Example 3: Finding prime numbers
    findPrimeNumbers(20);

    // Example 4: Processing array data
    processTemperatures();

    System.out.println();
  }

  /**
   * Validates user age with appropriate messages.
   *
   * @param age the age to validate
   */
  private static void validateUserAge(int age) {
    System.out.println("\nValidating age: " + age);

    if (age < 0 || age > 120) {
      System.out.println("  Error: Invalid age");
      return;
    }

    if (age < 13) {
      System.out.println("  Category: Child");
    } else if (age < 18) {
      System.out.println("  Category: Teenager");
    } else if (age < 65) {
      System.out.println("  Category: Adult");
    } else {
      System.out.println("  Category: Senior");
    }
  }

  /**
   * Calculates shipping cost based on order amount.
   *
   * @param orderAmount the order amount
   */
  private static void calculateShippingCost(double orderAmount) {
    System.out.println("\nOrder amount: $" + orderAmount);

    double shippingCost;
    if (orderAmount >= 100) {
      shippingCost = 0.0; // Free shipping
      System.out.println("  Shipping: FREE (orders over $100)");
    } else if (orderAmount >= 50) {
      shippingCost = 5.99;
      System.out.println("  Shipping: $" + shippingCost);
    } else {
      shippingCost = 9.99;
      System.out.println("  Shipping: $" + shippingCost);
    }

    System.out.printf("  Total: $%.2f%n", orderAmount + shippingCost);
  }

  /**
   * Finds and prints prime numbers up to the given limit.
   *
   * @param limit the upper limit for finding primes
   */
  private static void findPrimeNumbers(int limit) {
    System.out.println("\nPrime numbers up to " + limit + ":");

    for (int num = 2; num <= limit; num++) {
      boolean isPrime = true;

      // Check if num is prime
      for (int i = 2; i <= Math.sqrt(num); i++) {
        if (num % i == 0) {
          isPrime = false;
          break;
        }
      }

      if (isPrime) {
        System.out.print(num + " ");
      }
    }
    System.out.println();
  }

  /**
   * Processes temperature data and calculates statistics.
   */
  private static void processTemperatures() {
    System.out.println("\nProcessing temperature data:");

    double[] temperatures = {72.5, 68.3, 75.8, 71.2, 69.9, 73.4, 70.1};
    double sum = 0;
    double max = temperatures[0];
    double min = temperatures[0];

    for (double temp : temperatures) {
      sum += temp;

      if (temp > max) {
        max = temp;
      }

      if (temp < min) {
        min = temp;
      }
    }

    double average = sum / temperatures.length;

    System.out.printf("  Average: %.2f°F%n", average);
    System.out.printf("  Maximum: %.2f°F%n", max);
    System.out.printf("  Minimum: %.2f°F%n", min);

    // Count days above average
    int daysAboveAverage = 0;
    for (double temp : temperatures) {
      if (temp > average) {
        daysAboveAverage++;
      }
    }

    System.out.println("  Days above average: " + daysAboveAverage);
  }
}
