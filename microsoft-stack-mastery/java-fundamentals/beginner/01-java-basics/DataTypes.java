package com.microsoft.java.basics;

/**
 * DataTypes - Comprehensive demonstration of Java data types.
 *
 * <p>This class covers:
 * - All 8 primitive data types
 * - Reference types (String)
 * - Type casting (implicit and explicit)
 * - Constants (final keyword)
 * - Wrapper classes
 * - Default values
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class DataTypes {

  // Class-level constants (convention: UPPER_CASE with underscores)
  private static final double PI = 3.14159265359;
  private static final int MAX_USERS = 100;
  private static final String APP_NAME = "Data Types Demo";

  /**
   * Main method demonstrating various data types and operations.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Data Types Demonstration ===\n");

    demonstratePrimitiveTypes();
    demonstrateStrings();
    demonstrateTypeCasting();
    demonstrateConstants();
    demonstrateWrapperClasses();
    demonstrateDefaultValues();
  }

  /**
   * Demonstrates all 8 primitive data types in Java.
   */
  private static void demonstratePrimitiveTypes() {
    System.out.println("--- Primitive Data Types ---");

    // byte: 8-bit signed integer (-128 to 127)
    byte age = 25;
    System.out.println("byte - age: " + age + " (Range: -128 to 127)");

    // short: 16-bit signed integer (-32,768 to 32,767)
    short year = 2024;
    System.out.println("short - year: " + year + " (Range: -32,768 to 32,767)");

    // int: 32-bit signed integer (most commonly used for integers)
    int population = 1000000;
    System.out.println("int - population: " + population);

    // long: 64-bit signed integer (use 'L' suffix for literals)
    long worldPopulation = 8000000000L;
    System.out.println("long - worldPopulation: " + worldPopulation);

    // float: 32-bit floating point (use 'f' suffix for literals)
    float price = 19.99f;
    System.out.println("float - price: $" + price);

    // double: 64-bit floating point (default for decimal numbers)
    double distance = 384400.5;
    System.out.println("double - distance: " + distance + " km");

    // char: 16-bit Unicode character (single quotes)
    char grade = 'A';
    char unicodeChar = '\u0041'; // Unicode for 'A'
    System.out.println("char - grade: " + grade + ", unicode: " + unicodeChar);

    // boolean: true or false
    boolean isJavaFun = true;
    boolean isPythonBetter = false;
    System.out.println("boolean - isJavaFun: " + isJavaFun + ", isPythonBetter: " + isPythonBetter);

    System.out.println();
  }

  /**
   * Demonstrates String operations and characteristics.
   */
  private static void demonstrateStrings() {
    System.out.println("--- String (Reference Type) ---");

    // String is a reference type, not a primitive
    String firstName = "John";
    String lastName = "Doe";
    String fullName = firstName + " " + lastName; // Concatenation

    System.out.println("Full Name: " + fullName);
    System.out.println("Length: " + fullName.length());
    System.out.println("Uppercase: " + fullName.toUpperCase());
    System.out.println("Lowercase: " + fullName.toLowerCase());
    System.out.println("Contains 'John': " + fullName.contains("John"));
    System.out.println("Starts with 'John': " + fullName.startsWith("John"));
    System.out.println("Character at index 0: " + fullName.charAt(0));

    // String formatting
    String formatted = String.format("Name: %s, Age: %d, Salary: $%.2f", 
        fullName, 30, 75000.50);
    System.out.println("Formatted: " + formatted);

    // StringBuilder for efficient string manipulation
    StringBuilder sb = new StringBuilder();
    sb.append("Hello").append(" ").append("World");
    System.out.println("StringBuilder: " + sb.toString());

    System.out.println();
  }

  /**
   * Demonstrates type casting (widening and narrowing).
   */
  private static void demonstrateTypeCasting() {
    System.out.println("--- Type Casting ---");

    // Widening (automatic/implicit) - smaller to larger type
    int intValue = 100;
    long longValue = intValue; // int to long
    double doubleValue = intValue; // int to double

    System.out.println("Widening Casting:");
    System.out.println("  int: " + intValue + " -> long: " + longValue);
    System.out.println("  int: " + intValue + " -> double: " + doubleValue);

    // Narrowing (manual/explicit) - larger to smaller type
    double originalDouble = 9.78;
    int convertedInt = (int) originalDouble; // Explicit cast

    System.out.println("\nNarrowing Casting:");
    System.out.println("  double: " + originalDouble + " -> int: " + convertedInt);
    System.out.println("  Note: Decimal part is truncated, not rounded!");

    // Casting between char and int
    char letter = 'A';
    int asciiValue = letter; // char to int (ASCII value)
    char backToChar = (char) asciiValue; // int to char

    System.out.println("\nChar-Int Conversion:");
    System.out.println("  char '" + letter + "' -> ASCII: " + asciiValue);
    System.out.println("  ASCII " + asciiValue + " -> char: '" + backToChar + "'");

    // Overflow example
    byte smallByte = 127; // Maximum byte value
    // smallByte++; // This would overflow to -128
    System.out.println("\nByte max value: " + smallByte);

    System.out.println();
  }

  /**
   * Demonstrates the use of constants.
   */
  private static void demonstrateConstants() {
    System.out.println("--- Constants (final keyword) ---");

    // Local constants
    final int DAYS_IN_WEEK = 7;
    final double SPEED_OF_LIGHT = 299792458.0; // meters per second

    System.out.println("Application Name: " + APP_NAME);
    System.out.println("PI: " + PI);
    System.out.println("Max Users: " + MAX_USERS);
    System.out.println("Days in Week: " + DAYS_IN_WEEK);
    System.out.println("Speed of Light: " + SPEED_OF_LIGHT + " m/s");

    // Attempting to modify a constant will cause compilation error
    // PI = 3.14; // Error: cannot assign a value to final variable

    // Calculate circle area using constant
    double radius = 5.0;
    double area = PI * radius * radius;
    System.out.printf("Circle area (radius %.1f): %.2f%n", radius, area);

    System.out.println();
  }

  /**
   * Demonstrates wrapper classes for primitive types.
   */
  private static void demonstrateWrapperClasses() {
    System.out.println("--- Wrapper Classes ---");

    // Auto-boxing: primitive to wrapper
    Integer intObject = 100; // Auto-boxing int to Integer
    Double doubleObject = 99.99; // Auto-boxing double to Double
    Boolean boolObject = true; // Auto-boxing boolean to Boolean

    System.out.println("Auto-boxing:");
    System.out.println("  Integer: " + intObject);
    System.out.println("  Double: " + doubleObject);
    System.out.println("  Boolean: " + boolObject);

    // Unboxing: wrapper to primitive
    int primitiveInt = intObject; // Auto-unboxing Integer to int
    double primitiveDouble = doubleObject; // Auto-unboxing Double to double

    System.out.println("\nUnboxing:");
    System.out.println("  int: " + primitiveInt);
    System.out.println("  double: " + primitiveDouble);

    // Wrapper class utility methods
    String numberStr = "12345";
    int parsedInt = Integer.parseInt(numberStr);
    System.out.println("\nParsing string to int: \"" + numberStr + "\" -> " + parsedInt);

    // Useful wrapper methods
    System.out.println("\nWrapper class utilities:");
    System.out.println("  Integer.MAX_VALUE: " + Integer.MAX_VALUE);
    System.out.println("  Integer.MIN_VALUE: " + Integer.MIN_VALUE);
    System.out.println("  Double.MAX_VALUE: " + Double.MAX_VALUE);
    System.out.println("  Compare 10 vs 20: " + Integer.compare(10, 20));
    System.out.println("  Integer to Binary: " + Integer.toBinaryString(42));
    System.out.println("  Integer to Hex: " + Integer.toHexString(255));

    System.out.println();
  }

  /**
   * Demonstrates default values for instance variables.
   */
  private static void demonstrateDefaultValues() {
    System.out.println("--- Default Values ---");

    DefaultValuesDemo demo = new DefaultValuesDemo();
    demo.printDefaultValues();

    System.out.println();
  }

  /**
   * Helper class to demonstrate default values of instance variables.
   */
  private static class DefaultValuesDemo {
    // Instance variables get default values if not initialized
    byte byteVar;
    short shortVar;
    int intVar;
    long longVar;
    float floatVar;
    double doubleVar;
    char charVar;
    boolean booleanVar;
    String stringVar;

    void printDefaultValues() {
      System.out.println("Default values for instance variables:");
      System.out.println("  byte: " + byteVar);
      System.out.println("  short: " + shortVar);
      System.out.println("  int: " + intVar);
      System.out.println("  long: " + longVar);
      System.out.println("  float: " + floatVar);
      System.out.println("  double: " + doubleVar);
      System.out.println("  char: '" + charVar + "' (Unicode: " + (int) charVar + ")");
      System.out.println("  boolean: " + booleanVar);
      System.out.println("  String: " + stringVar);
    }
  }
}
