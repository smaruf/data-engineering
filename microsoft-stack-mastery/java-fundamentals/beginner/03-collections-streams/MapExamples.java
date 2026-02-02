package com.microsoft.java.collections;

import java.util.HashMap;
import java.util.TreeMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.Collection;

/**
 * MapExamples - Comprehensive demonstration of Java Map interface.
 *
 * <p>This class covers:
 * - HashMap implementation
 * - TreeMap implementation (sorted)
 * - LinkedHashMap implementation (insertion-order)
 * - Map operations (put, get, remove, containsKey, etc.)
 * - Iteration techniques
 * - Real-world use cases
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class MapExamples {

  /**
   * Main method demonstrating Map operations.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Map Examples ===\n");

    demonstrateHashMap();
    demonstrateTreeMap();
    demonstrateLinkedHashMap();
    demonstrateMapOperations();
    demonstrateMapIteration();
    demonstrateMapComparison();
    realWorldExample();
  }

  /**
   * Demonstrates HashMap basics.
   */
  private static void demonstrateHashMap() {
    System.out.println("--- HashMap ---");

    // Creating HashMap
    HashMap<String, Integer> ages = new HashMap<>();

    // Adding key-value pairs
    ages.put("Alice", 30);
    ages.put("Bob", 25);
    ages.put("Charlie", 35);
    ages.put("Diana", 28);

    System.out.println("HashMap: " + ages);
    System.out.println("Size: " + ages.size());

    // Getting values
    System.out.println("Alice's age: " + ages.get("Alice"));
    System.out.println("Eve's age: " + ages.get("Eve")); // null (not found)

    // Checking if key/value exists
    System.out.println("Contains key 'Bob': " + ages.containsKey("Bob"));
    System.out.println("Contains value 30: " + ages.containsValue(30));

    // Updating value
    ages.put("Alice", 31); // Updates existing key
    System.out.println("After update: " + ages);

    // Removing entry
    ages.remove("Bob");
    System.out.println("After removing Bob: " + ages);

    // getOrDefault
    int age = ages.getOrDefault("Eve", 0);
    System.out.println("Eve's age (with default): " + age);

    System.out.println();
  }

  /**
   * Demonstrates TreeMap (sorted by keys).
   */
  private static void demonstrateTreeMap() {
    System.out.println("--- TreeMap (Sorted) ---");

    TreeMap<String, Double> scores = new TreeMap<>();

    // Adding entries
    scores.put("Charlie", 85.5);
    scores.put("Alice", 92.0);
    scores.put("Bob", 78.5);
    scores.put("Diana", 88.0);

    // TreeMap automatically sorts by key
    System.out.println("TreeMap (sorted by key): " + scores);

    // First and last entries
    System.out.println("First key: " + scores.firstKey());
    System.out.println("Last key: " + scores.lastKey());

    // Submap operations
    System.out.println("Submap (Alice to Charlie): " 
        + scores.subMap("Alice", true, "Charlie", true));

    // Floor and ceiling
    System.out.println("Floor key of 'Bob': " + scores.floorKey("Bob"));
    System.out.println("Ceiling key of 'Bob': " + scores.ceilingKey("Bob"));

    System.out.println();
  }

  /**
   * Demonstrates LinkedHashMap (maintains insertion order).
   */
  private static void demonstrateLinkedHashMap() {
    System.out.println("--- LinkedHashMap (Insertion Order) ---");

    LinkedHashMap<String, String> countries = new LinkedHashMap<>();

    // Adding entries
    countries.put("USA", "Washington D.C.");
    countries.put("UK", "London");
    countries.put("Japan", "Tokyo");
    countries.put("India", "New Delhi");
    countries.put("France", "Paris");

    // Maintains insertion order
    System.out.println("LinkedHashMap (insertion order):");
    countries.forEach((country, capital) -> 
        System.out.println("  " + country + " -> " + capital));

    // Access-order LinkedHashMap
    LinkedHashMap<String, Integer> cache = new LinkedHashMap<>(16, 0.75f, true);
    cache.put("A", 1);
    cache.put("B", 2);
    cache.put("C", 3);

    System.out.println("\nAccess-order LinkedHashMap:");
    cache.get("A"); // Access A
    cache.forEach((k, v) -> System.out.print(k + " "));
    System.out.println("(A moved to end)");

    System.out.println();
  }

  /**
   * Demonstrates common Map operations.
   */
  private static void demonstrateMapOperations() {
    System.out.println("--- Map Operations ---");

    Map<String, Integer> inventory = new HashMap<>();

    // putIfAbsent - only adds if key doesn't exist
    inventory.put("Laptop", 10);
    inventory.putIfAbsent("Laptop", 20); // Won't update
    inventory.putIfAbsent("Mouse", 50);  // Will add

    System.out.println("After putIfAbsent: " + inventory);

    // compute - compute new value based on key
    inventory.compute("Laptop", (k, v) -> v + 5);
    System.out.println("After compute: " + inventory);

    // computeIfPresent
    inventory.computeIfPresent("Mouse", (k, v) -> v - 10);
    System.out.println("After computeIfPresent: " + inventory);

    // computeIfAbsent
    inventory.computeIfAbsent("Keyboard", k -> 30);
    System.out.println("After computeIfAbsent: " + inventory);

    // merge - combines values
    inventory.merge("Laptop", 5, Integer::sum);
    System.out.println("After merge: " + inventory);

    // replace
    inventory.replace("Mouse", 40, 45); // Replace if current value is 40
    System.out.println("After replace: " + inventory);

    // replaceAll
    inventory.replaceAll((k, v) -> v * 2);
    System.out.println("After replaceAll (*2): " + inventory);

    System.out.println();
  }

  /**
   * Demonstrates different ways to iterate over maps.
   */
  private static void demonstrateMapIteration() {
    System.out.println("--- Map Iteration ---");

    Map<String, String> phonebook = new HashMap<>();
    phonebook.put("Alice", "555-1234");
    phonebook.put("Bob", "555-5678");
    phonebook.put("Charlie", "555-9012");

    // Method 1: Using entrySet()
    System.out.println("Method 1 - entrySet():");
    for (Map.Entry<String, String> entry : phonebook.entrySet()) {
      System.out.println("  " + entry.getKey() + ": " + entry.getValue());
    }

    // Method 2: Using keySet()
    System.out.println("\nMethod 2 - keySet():");
    for (String name : phonebook.keySet()) {
      System.out.println("  " + name + ": " + phonebook.get(name));
    }

    // Method 3: Using values()
    System.out.println("\nMethod 3 - values():");
    for (String phone : phonebook.values()) {
      System.out.println("  " + phone);
    }

    // Method 4: forEach (Java 8)
    System.out.println("\nMethod 4 - forEach:");
    phonebook.forEach((name, phone) -> 
        System.out.println("  " + name + ": " + phone));

    // Method 5: Stream API
    System.out.println("\nMethod 5 - Stream API:");
    phonebook.entrySet().stream()
        .filter(e -> e.getKey().startsWith("A"))
        .forEach(e -> System.out.println("  " + e.getKey() + ": " + e.getValue()));

    System.out.println();
  }

  /**
   * Demonstrates comparison between different Map implementations.
   */
  private static void demonstrateMapComparison() {
    System.out.println("--- Map Implementation Comparison ---");

    System.out.println("HashMap:");
    System.out.println("  - No ordering guarantee");
    System.out.println("  - O(1) average for get/put");
    System.out.println("  - Allows one null key and multiple null values");
    System.out.println("  - Best for general-purpose use");

    System.out.println("\nTreeMap:");
    System.out.println("  - Sorted by keys (natural order or comparator)");
    System.out.println("  - O(log n) for get/put");
    System.out.println("  - No null keys (throws NullPointerException)");
    System.out.println("  - Best when you need sorted keys");

    System.out.println("\nLinkedHashMap:");
    System.out.println("  - Maintains insertion order (or access order)");
    System.out.println("  - O(1) average for get/put");
    System.out.println("  - Allows one null key and multiple null values");
    System.out.println("  - Best for caching or when order matters");

    System.out.println("\nUse HashMap when:");
    System.out.println("  - Order doesn't matter");
    System.out.println("  - You need fast lookups");

    System.out.println("\nUse TreeMap when:");
    System.out.println("  - You need sorted keys");
    System.out.println("  - You need range queries");

    System.out.println("\nUse LinkedHashMap when:");
    System.out.println("  - You need predictable iteration order");
    System.out.println("  - You're implementing a cache");

    System.out.println();
  }

  /**
   * Demonstrates real-world Map usage.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Student Grade Manager ---");

    StudentGradeManager manager = new StudentGradeManager();

    // Add students with grades
    manager.addGrade("Alice", "Math", 95);
    manager.addGrade("Alice", "Science", 88);
    manager.addGrade("Alice", "English", 92);

    manager.addGrade("Bob", "Math", 78);
    manager.addGrade("Bob", "Science", 85);
    manager.addGrade("Bob", "English", 80);

    manager.addGrade("Charlie", "Math", 92);
    manager.addGrade("Charlie", "Science", 90);
    manager.addGrade("Charlie", "English", 88);

    // Display all grades
    System.out.println("\nAll Student Grades:");
    manager.displayAllGrades();

    // Get specific student's grades
    System.out.println("\nAlice's Grades:");
    manager.displayStudentGrades("Alice");

    // Calculate averages
    System.out.println("\nStudent Averages:");
    manager.displayAverages();

    // Subject statistics
    System.out.println("\nSubject Statistics:");
    manager.displaySubjectStatistics();

    // Top performers
    System.out.println("\nTop Performers (avg >= 90):");
    manager.displayTopPerformers(90.0);

    System.out.println();
  }
}

// ========== Student Grade Manager Example ==========

/**
 * StudentGradeManager managing student grades using nested maps.
 */
class StudentGradeManager {
  // Map<StudentName, Map<Subject, Grade>>
  private Map<String, Map<String, Integer>> studentGrades;

  public StudentGradeManager() {
    this.studentGrades = new HashMap<>();
  }

  /**
   * Adds a grade for a student in a subject.
   */
  public void addGrade(String student, String subject, int grade) {
    studentGrades.putIfAbsent(student, new HashMap<>());
    studentGrades.get(student).put(subject, grade);
    System.out.printf("Added: %s - %s: %d%n", student, subject, grade);
  }

  /**
   * Gets a student's grade in a subject.
   */
  public Integer getGrade(String student, String subject) {
    Map<String, Integer> grades = studentGrades.get(student);
    if (grades != null) {
      return grades.get(subject);
    }
    return null;
  }

  /**
   * Calculates a student's average grade.
   */
  public double calculateAverage(String student) {
    Map<String, Integer> grades = studentGrades.get(student);
    if (grades == null || grades.isEmpty()) {
      return 0.0;
    }

    int sum = 0;
    for (int grade : grades.values()) {
      sum += grade;
    }

    return (double) sum / grades.size();
  }

  /**
   * Displays all grades for all students.
   */
  public void displayAllGrades() {
    if (studentGrades.isEmpty()) {
      System.out.println("  No grades recorded");
      return;
    }

    for (Map.Entry<String, Map<String, Integer>> entry : studentGrades.entrySet()) {
      String student = entry.getKey();
      Map<String, Integer> grades = entry.getValue();

      System.out.println("  " + student + ":");
      grades.forEach((subject, grade) -> 
          System.out.printf("    %s: %d%n", subject, grade));
    }
  }

  /**
   * Displays grades for a specific student.
   */
  public void displayStudentGrades(String student) {
    Map<String, Integer> grades = studentGrades.get(student);

    if (grades == null) {
      System.out.println("  Student not found");
      return;
    }

    grades.forEach((subject, grade) -> 
        System.out.printf("  %s: %d%n", subject, grade));
  }

  /**
   * Displays average grades for all students.
   */
  public void displayAverages() {
    for (String student : studentGrades.keySet()) {
      double avg = calculateAverage(student);
      System.out.printf("  %s: %.2f%n", student, avg);
    }
  }

  /**
   * Displays statistics for each subject.
   */
  public void displaySubjectStatistics() {
    Map<String, java.util.List<Integer>> subjectGrades = new HashMap<>();

    // Collect all grades by subject
    for (Map<String, Integer> grades : studentGrades.values()) {
      for (Map.Entry<String, Integer> entry : grades.entrySet()) {
        String subject = entry.getKey();
        Integer grade = entry.getValue();

        subjectGrades.putIfAbsent(subject, new java.util.ArrayList<>());
        subjectGrades.get(subject).add(grade);
      }
    }

    // Calculate and display statistics
    for (Map.Entry<String, java.util.List<Integer>> entry : subjectGrades.entrySet()) {
      String subject = entry.getKey();
      java.util.List<Integer> grades = entry.getValue();

      int sum = grades.stream().mapToInt(Integer::intValue).sum();
      double avg = (double) sum / grades.size();
      int max = grades.stream().mapToInt(Integer::intValue).max().orElse(0);
      int min = grades.stream().mapToInt(Integer::intValue).min().orElse(0);

      System.out.printf("  %s: avg=%.2f, max=%d, min=%d, count=%d%n",
          subject, avg, max, min, grades.size());
    }
  }

  /**
   * Displays students with average above threshold.
   */
  public void displayTopPerformers(double threshold) {
    for (String student : studentGrades.keySet()) {
      double avg = calculateAverage(student);
      if (avg >= threshold) {
        System.out.printf("  %s: %.2f%n", student, avg);
      }
    }
  }

  /**
   * Gets all students.
   */
  public Set<String> getAllStudents() {
    return studentGrades.keySet();
  }

  /**
   * Gets all subjects for a student.
   */
  public Set<String> getStudentSubjects(String student) {
    Map<String, Integer> grades = studentGrades.get(student);
    return grades != null ? grades.keySet() : Set.of();
  }

  /**
   * Removes a student.
   */
  public void removeStudent(String student) {
    if (studentGrades.remove(student) != null) {
      System.out.println("Removed student: " + student);
    } else {
      System.out.println("Student not found: " + student);
    }
  }

  /**
   * Gets total number of students.
   */
  public int getStudentCount() {
    return studentGrades.size();
  }
}
