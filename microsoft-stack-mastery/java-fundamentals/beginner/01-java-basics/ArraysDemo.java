package com.microsoft.java.basics;

import java.util.Comparator;

/**
 * ArraysDemo - Comprehensive demonstration of Java arrays.
 *
 * <p>This class covers:
 * - Array declaration and initialization
 * - Single-dimensional arrays
 * - Multi-dimensional arrays
 * - Array iteration techniques
 * - Array manipulation using Arrays class
 * - Common array operations
 * - Real-world use cases
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class ArraysDemo {

  /**
   * Main method demonstrating various array operations.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Arrays Demonstration ===\n");

    demonstrateArrayDeclaration();
    demonstrateArrayInitialization();
    demonstrateArrayIteration();
    demonstrateArrayMethods();
    demonstrateMultiDimensionalArrays();
    demonstrateJaggedArrays();
    demonstrateArrayCopying();
    demonstrateArraySearchingSorting();
    realWorldExamples();
  }

  /**
   * Demonstrates different ways to declare arrays.
   */
  private static void demonstrateArrayDeclaration() {
    System.out.println("--- Array Declaration ---");

    // Declaration syntax variations (all are valid)
    int[] numbers1;           // Preferred style
    int numbers2[];           // C-style (less common in Java)
    String[] names;
    double[] prices;

    // Array of objects
    String[] fruits;
    Object[] objects;

    System.out.println("Arrays can be declared with type[] name or type name[]");
    System.out.println("Arrays are reference types, not primitives");

    System.out.println();
  }

  /**
   * Demonstrates various array initialization techniques.
   */
  private static void demonstrateArrayInitialization() {
    System.out.println("--- Array Initialization ---");

    // Method 1: Declare and allocate size
    int[] numbers = new int[5]; // Creates array of 5 integers (default: 0)
    System.out.println("Method 1 - new int[5]: " + java.util.Arrays.toString(numbers));

    // Method 2: Declare with values (array initializer)
    int[] scores = {95, 87, 92, 78, 88};
    System.out.println("Method 2 - {values}: " + java.util.Arrays.toString(scores));

    // Method 3: Anonymous array
    String[] fruits = new String[]{"Apple", "Banana", "Orange"};
    System.out.println("Method 3 - new String[]{values}: " + java.util.Arrays.toString(fruits));

    // Array length
    System.out.println("\nArray length:");
    System.out.println("  scores.length = " + scores.length);
    System.out.println("  fruits.length = " + fruits.length);

    // Default values for different types
    int[] intArray = new int[3];
    double[] doubleArray = new double[3];
    boolean[] boolArray = new boolean[3];
    String[] stringArray = new String[3];

    System.out.println("\nDefault values:");
    System.out.println("  int[]: " + java.util.Arrays.toString(intArray));
    System.out.println("  double[]: " + java.util.Arrays.toString(doubleArray));
    System.out.println("  boolean[]: " + java.util.Arrays.toString(boolArray));
    System.out.println("  String[]: " + java.util.Arrays.toString(stringArray));

    System.out.println();
  }

  /**
   * Demonstrates different ways to iterate through arrays.
   */
  private static void demonstrateArrayIteration() {
    System.out.println("--- Array Iteration ---");

    String[] cities = {"New York", "London", "Tokyo", "Paris", "Sydney"};

    // Method 1: Traditional for loop with index
    System.out.println("Method 1 - Traditional for loop:");
    for (int i = 0; i < cities.length; i++) {
      System.out.println("  [" + i + "] " + cities[i]);
    }

    // Method 2: Enhanced for loop (for-each)
    System.out.println("\nMethod 2 - Enhanced for loop:");
    for (String city : cities) {
      System.out.println("  - " + city);
    }

    // Method 3: While loop
    System.out.println("\nMethod 3 - While loop:");
    int index = 0;
    while (index < cities.length) {
      System.out.println("  " + (index + 1) + ". " + cities[index]);
      index++;
    }

    // Method 4: Java 8 Streams
    System.out.println("\nMethod 4 - Java 8 Streams:");
    java.util.Arrays.stream(cities)
        .forEach(city -> System.out.println("  * " + city));

    // Iterating backwards
    System.out.println("\nIterating backwards:");
    for (int i = cities.length - 1; i >= 0; i--) {
      System.out.println("  " + cities[i]);
    }

    System.out.println();
  }

  /**
   * Demonstrates utility methods from the Arrays class.
   */
  private static void demonstrateArrayMethods() {
    System.out.println("--- Arrays Class Methods ---");

    int[] numbers = {5, 2, 8, 1, 9, 3, 7};
    System.out.println("Original array: " + java.util.Arrays.toString(numbers));

    // Sort array
    int[] sortedNumbers = numbers.clone();
    java.util.Arrays.sort(sortedNumbers);
    System.out.println("After sorting: " + java.util.Arrays.toString(sortedNumbers));

    // Binary search (array must be sorted first)
    int searchValue = 7;
    int index = java.util.Arrays.binarySearch(sortedNumbers, searchValue);
    System.out.println("Binary search for " + searchValue + ": found at index " + index);

    // Fill array
    int[] filledArray = new int[5];
    java.util.Arrays.fill(filledArray, 42);
    System.out.println("Filled with 42: " + java.util.Arrays.toString(filledArray));

    // Compare arrays
    int[] array1 = {1, 2, 3};
    int[] array2 = {1, 2, 3};
    int[] array3 = {1, 2, 4};

    System.out.println("\nArray comparison:");
    System.out.println("  array1 equals array2: " + java.util.Arrays.equals(array1, array2));
    System.out.println("  array1 equals array3: " + java.util.Arrays.equals(array1, array3));

    // Copy arrays
    int[] copiedArray = java.util.Arrays.copyOf(numbers, numbers.length);
    System.out.println("\nCopied array: " + java.util.Arrays.toString(copiedArray));

    int[] partialCopy = java.util.Arrays.copyOfRange(numbers, 2, 5);
    System.out.println("Partial copy [2-5): " + java.util.Arrays.toString(partialCopy));

    // Convert to String
    String arrayString = java.util.Arrays.toString(numbers);
    System.out.println("\nArray as string: " + arrayString);

    // Custom sorting with Comparator
    String[] words = {"banana", "apple", "cherry", "date"};
    java.util.Arrays.sort(words, Comparator.reverseOrder());
    System.out.println("\nReverse sorted strings: " + java.util.Arrays.toString(words));

    System.out.println();
  }

  /**
   * Demonstrates multi-dimensional arrays.
   */
  private static void demonstrateMultiDimensionalArrays() {
    System.out.println("--- Multi-Dimensional Arrays ---");

    // 2D array declaration and initialization
    int[][] matrix = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    System.out.println("2D Array (3x3 matrix):");
    for (int i = 0; i < matrix.length; i++) {
      for (int j = 0; j < matrix[i].length; j++) {
        System.out.printf("%4d", matrix[i][j]);
      }
      System.out.println();
    }

    // Alternative initialization
    int[][] grid = new int[3][4]; // 3 rows, 4 columns
    int value = 1;
    for (int i = 0; i < grid.length; i++) {
      for (int j = 0; j < grid[i].length; j++) {
        grid[i][j] = value++;
      }
    }

    System.out.println("\nGrid (3x4):");
    for (int[] row : grid) {
      System.out.println("  " + java.util.Arrays.toString(row));
    }

    // 3D array
    int[][][] cube = new int[2][3][4];
    System.out.println("\n3D Array dimensions: " + cube.length + "x" 
        + cube[0].length + "x" + cube[0][0].length);

    // Practical example: Student grades
    String[] students = {"Alice", "Bob", "Charlie"};
    String[] subjects = {"Math", "Science", "English"};
    int[][] grades = {
        {95, 87, 92}, // Alice's grades
        {78, 85, 88}, // Bob's grades
        {92, 90, 94}  // Charlie's grades
    };

    System.out.println("\nStudent Grades:");
    System.out.printf("%-10s", "Student");
    for (String subject : subjects) {
      System.out.printf("%10s", subject);
    }
    System.out.println();
    System.out.println("-".repeat(40));

    for (int i = 0; i < students.length; i++) {
      System.out.printf("%-10s", students[i]);
      for (int j = 0; j < grades[i].length; j++) {
        System.out.printf("%10d", grades[i][j]);
      }
      System.out.println();
    }

    System.out.println();
  }

  /**
   * Demonstrates jagged arrays (arrays with different row lengths).
   */
  private static void demonstrateJaggedArrays() {
    System.out.println("--- Jagged Arrays ---");

    // Jagged array: rows can have different lengths
    int[][] jaggedArray = {
        {1},
        {2, 3},
        {4, 5, 6},
        {7, 8, 9, 10}
    };

    System.out.println("Jagged array (triangle shape):");
    for (int i = 0; i < jaggedArray.length; i++) {
      System.out.print("  Row " + i + ": ");
      for (int j = 0; j < jaggedArray[i].length; j++) {
        System.out.print(jaggedArray[i][j] + " ");
      }
      System.out.println();
    }

    // Manual jagged array creation
    int[][] pyramid = new int[4][];
    for (int i = 0; i < pyramid.length; i++) {
      pyramid[i] = new int[i + 1];
      java.util.Arrays.fill(pyramid[i], i + 1);
    }

    System.out.println("\nPyramid pattern:");
    for (int[] row : pyramid) {
      System.out.println("  " + java.util.Arrays.toString(row));
    }

    System.out.println();
  }

  /**
   * Demonstrates different ways to copy arrays.
   */
  private static void demonstrateArrayCopying() {
    System.out.println("--- Array Copying ---");

    int[] original = {10, 20, 30, 40, 50};
    System.out.println("Original: " + java.util.Arrays.toString(original));

    // Method 1: clone()
    int[] copy1 = original.clone();
    System.out.println("Clone: " + java.util.Arrays.toString(copy1));

    // Method 2: Arrays.copyOf()
    int[] copy2 = java.util.Arrays.copyOf(original, original.length);
    System.out.println("copyOf: " + java.util.Arrays.toString(copy2));

    // Method 3: System.arraycopy()
    int[] copy3 = new int[original.length];
    System.arraycopy(original, 0, copy3, 0, original.length);
    System.out.println("System.arraycopy: " + java.util.Arrays.toString(copy3));

    // Method 4: Manual copy
    int[] copy4 = new int[original.length];
    for (int i = 0; i < original.length; i++) {
      copy4[i] = original[i];
    }
    System.out.println("Manual copy: " + java.util.Arrays.toString(copy4));

    // Shallow vs Deep copy for object arrays
    System.out.println("\nShallow vs Deep copy:");
    String[] names = {"Alice", "Bob", "Charlie"};
    String[] shallowCopy = names.clone();

    System.out.println("Original: " + java.util.Arrays.toString(names));
    System.out.println("Shallow copy: " + java.util.Arrays.toString(shallowCopy));
    System.out.println("Are they the same object? " + (names == shallowCopy));
    System.out.println("Do they have same content? " + java.util.Arrays.equals(names, shallowCopy));

    System.out.println();
  }

  /**
   * Demonstrates array searching and sorting.
   */
  private static void demonstrateArraySearchingSorting() {
    System.out.println("--- Searching and Sorting ---");

    int[] numbers = {64, 34, 25, 12, 22, 11, 90};
    System.out.println("Original: " + java.util.Arrays.toString(numbers));

    // Linear search
    int target = 22;
    int linearSearchResult = linearSearch(numbers, target);
    System.out.println("\nLinear search for " + target + ": " 
        + (linearSearchResult != -1 ? "found at index " + linearSearchResult : "not found"));

    // Sort and binary search
    int[] sortedNumbers = numbers.clone();
    java.util.Arrays.sort(sortedNumbers);
    System.out.println("Sorted: " + java.util.Arrays.toString(sortedNumbers));

    int binarySearchResult = java.util.Arrays.binarySearch(sortedNumbers, target);
    System.out.println("Binary search for " + target + ": found at index " + binarySearchResult);

    // Finding min and max
    int min = findMin(numbers);
    int max = findMax(numbers);
    System.out.println("\nMin: " + min + ", Max: " + max);

    // Sorting strings
    String[] fruits = {"Orange", "Apple", "Banana", "Grape", "Cherry"};
    System.out.println("\nOriginal fruits: " + java.util.Arrays.toString(fruits));

    java.util.Arrays.sort(fruits);
    System.out.println("Sorted fruits: " + java.util.Arrays.toString(fruits));

    // Custom sorting
    java.util.Arrays.sort(fruits, (a, b) -> b.compareTo(a)); // Reverse order
    System.out.println("Reverse sorted: " + java.util.Arrays.toString(fruits));

    System.out.println();
  }

  /**
   * Performs linear search on an array.
   *
   * @param array the array to search
   * @param target the value to find
   * @return the index of the target, or -1 if not found
   */
  private static int linearSearch(int[] array, int target) {
    for (int i = 0; i < array.length; i++) {
      if (array[i] == target) {
        return i;
      }
    }
    return -1;
  }

  /**
   * Finds the minimum value in an array.
   *
   * @param array the array to search
   * @return the minimum value
   */
  private static int findMin(int[] array) {
    if (array == null || array.length == 0) {
      throw new IllegalArgumentException("Array is empty");
    }

    int min = array[0];
    for (int i = 1; i < array.length; i++) {
      if (array[i] < min) {
        min = array[i];
      }
    }
    return min;
  }

  /**
   * Finds the maximum value in an array.
   *
   * @param array the array to search
   * @return the maximum value
   */
  private static int findMax(int[] array) {
    if (array == null || array.length == 0) {
      throw new IllegalArgumentException("Array is empty");
    }

    int max = array[0];
    for (int i = 1; i < array.length; i++) {
      if (array[i] > max) {
        max = array[i];
      }
    }
    return max;
  }

  /**
   * Demonstrates real-world use cases of arrays.
   */
  private static void realWorldExamples() {
    System.out.println("--- Real-World Examples ---");

    // Example 1: Sales data analysis
    analyzeSalesData();

    // Example 2: Image processing (2D array as pixels)
    processImage();

    // Example 3: Student grade statistics
    calculateGradeStatistics();

    System.out.println();
  }

  /**
   * Analyzes sales data using arrays.
   */
  private static void analyzeSalesData() {
    System.out.println("\nSales Data Analysis:");

    String[] months = {"Jan", "Feb", "Mar", "Apr", "May", "Jun"};
    double[] sales = {12500.50, 15200.75, 13800.25, 16500.00, 14900.50, 17200.25};

    double totalSales = 0;
    double maxSales = sales[0];
    String maxMonth = months[0];

    for (int i = 0; i < sales.length; i++) {
      totalSales += sales[i];
      if (sales[i] > maxSales) {
        maxSales = sales[i];
        maxMonth = months[i];
      }
    }

    double avgSales = totalSales / sales.length;

    System.out.printf("  Total Sales: $%.2f%n", totalSales);
    System.out.printf("  Average Sales: $%.2f%n", avgSales);
    System.out.printf("  Best Month: %s ($%.2f)%n", maxMonth, maxSales);
  }

  /**
   * Simulates simple image processing using 2D array.
   */
  private static void processImage() {
    System.out.println("\nImage Processing (Grayscale 5x5):");

    // Simulate grayscale image (0-255 values)
    int[][] image = {
        {100, 120, 130, 125, 110},
        {115, 140, 150, 145, 120},
        {125, 145, 160, 155, 130},
        {120, 135, 145, 140, 125},
        {110, 125, 135, 130, 115}
    };

    // Calculate average brightness
    int total = 0;
    int pixelCount = image.length * image[0].length;

    for (int[] row : image) {
      for (int pixel : row) {
        total += pixel;
      }
    }

    double avgBrightness = (double) total / pixelCount;
    System.out.printf("  Average Brightness: %.2f%n", avgBrightness);

    // Apply brightness adjustment
    int adjustment = 20;
    System.out.println("  Applying brightness +20...");

    for (int i = 0; i < image.length; i++) {
      for (int j = 0; j < image[i].length; j++) {
        image[i][j] = Math.min(255, image[i][j] + adjustment);
      }
    }

    System.out.println("  Image processing complete!");
  }

  /**
   * Calculates statistics for student grades.
   */
  private static void calculateGradeStatistics() {
    System.out.println("\nGrade Statistics:");

    int[] grades = {85, 92, 78, 95, 88, 76, 90, 84, 91, 87};

    // Calculate statistics
    double sum = 0;
    int max = grades[0];
    int min = grades[0];

    for (int grade : grades) {
      sum += grade;
      if (grade > max) max = grade;
      if (grade < min) min = grade;
    }

    double average = sum / grades.length;

    // Count letter grades
    int countA = 0, countB = 0, countC = 0, countD = 0, countF = 0;

    for (int grade : grades) {
      if (grade >= 90) countA++;
      else if (grade >= 80) countB++;
      else if (grade >= 70) countC++;
      else if (grade >= 60) countD++;
      else countF++;
    }

    System.out.printf("  Average: %.2f%n", average);
    System.out.println("  Highest: " + max);
    System.out.println("  Lowest: " + min);
    System.out.println("  Grade Distribution:");
    System.out.println("    A's: " + countA);
    System.out.println("    B's: " + countB);
    System.out.println("    C's: " + countC);
    System.out.println("    D's: " + countD);
    System.out.println("    F's: " + countF);
  }
}
