package com.microsoft.java.collections;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Iterator;
import java.util.ListIterator;
import java.util.Collections;
import java.util.Comparator;

/**
 * ListExamples - Comprehensive demonstration of Java List interface.
 *
 * <p>This class covers:
 * - ArrayList implementation
 * - LinkedList implementation
 * - List operations (add, remove, get, set)
 * - Iteration techniques
 * - Sorting and searching
 * - List utility methods
 * - Performance considerations
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class ListExamples {

  /**
   * Main method demonstrating List operations.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java List Examples ===\n");

    demonstrateArrayList();
    demonstrateLinkedList();
    demonstrateListOperations();
    demonstrateListIteration();
    demonstrateSortingSearching();
    demonstrateListComparison();
    demonstrateUtilityMethods();
    realWorldExample();
  }

  /**
   * Demonstrates ArrayList basics.
   */
  private static void demonstrateArrayList() {
    System.out.println("--- ArrayList ---");

    // Creating ArrayList
    ArrayList<String> fruits = new ArrayList<>();

    // Adding elements
    fruits.add("Apple");
    fruits.add("Banana");
    fruits.add("Orange");
    fruits.add("Mango");

    System.out.println("ArrayList: " + fruits);
    System.out.println("Size: " + fruits.size());

    // Accessing elements
    System.out.println("First fruit: " + fruits.get(0));
    System.out.println("Last fruit: " + fruits.get(fruits.size() - 1));

    // Modifying elements
    fruits.set(1, "Blueberry");
    System.out.println("After modification: " + fruits);

    // Checking if contains
    System.out.println("Contains 'Orange': " + fruits.contains("Orange"));
    System.out.println("Index of 'Mango': " + fruits.indexOf("Mango"));

    // Removing elements
    fruits.remove("Orange");
    fruits.remove(0); // Remove by index
    System.out.println("After removals: " + fruits);

    System.out.println();
  }

  /**
   * Demonstrates LinkedList basics.
   */
  private static void demonstrateLinkedList() {
    System.out.println("--- LinkedList ---");

    LinkedList<Integer> numbers = new LinkedList<>();

    // Adding elements
    numbers.add(10);
    numbers.add(20);
    numbers.add(30);

    // LinkedList-specific methods
    numbers.addFirst(5);
    numbers.addLast(40);

    System.out.println("LinkedList: " + numbers);

    // Accessing first and last
    System.out.println("First: " + numbers.getFirst());
    System.out.println("Last: " + numbers.getLast());

    // Removing first and last
    numbers.removeFirst();
    numbers.removeLast();
    System.out.println("After removing first and last: " + numbers);

    // Peek operations (without removing)
    System.out.println("Peek first: " + numbers.peekFirst());
    System.out.println("Peek last: " + numbers.peekLast());

    System.out.println();
  }

  /**
   * Demonstrates common List operations.
   */
  private static void demonstrateListOperations() {
    System.out.println("--- List Operations ---");

    List<String> colors = new ArrayList<>();

    // Add operations
    colors.add("Red");
    colors.add("Green");
    colors.add("Blue");
    colors.add(1, "Yellow"); // Insert at index

    System.out.println("After adding: " + colors);

    // Add all from another collection
    List<String> moreColors = List.of("Purple", "Orange", "Pink");
    colors.addAll(moreColors);
    System.out.println("After addAll: " + colors);

    // Remove operations
    colors.remove("Green");
    colors.remove(0);
    System.out.println("After removals: " + colors);

    // Clear list
    List<String> temp = new ArrayList<>(colors);
    temp.clear();
    System.out.println("After clear: " + temp + " (empty: " + temp.isEmpty() + ")");

    // Sublist
    List<String> subList = colors.subList(0, 3);
    System.out.println("Sublist [0-3): " + subList);

    // Contains operations
    System.out.println("Contains 'Blue': " + colors.contains("Blue"));
    System.out.println("Contains all [Blue, Pink]: " 
        + colors.containsAll(List.of("Blue", "Pink")));

    System.out.println();
  }

  /**
   * Demonstrates different iteration techniques.
   */
  private static void demonstrateListIteration() {
    System.out.println("--- List Iteration ---");

    List<String> cities = List.of("New York", "London", "Tokyo", "Paris", "Mumbai");

    // Method 1: For-each loop
    System.out.println("For-each loop:");
    for (String city : cities) {
      System.out.print(city + " ");
    }
    System.out.println();

    // Method 2: Traditional for loop
    System.out.println("\nTraditional for loop:");
    for (int i = 0; i < cities.size(); i++) {
      System.out.print(cities.get(i) + " ");
    }
    System.out.println();

    // Method 3: Iterator
    System.out.println("\nIterator:");
    Iterator<String> iterator = cities.iterator();
    while (iterator.hasNext()) {
      System.out.print(iterator.next() + " ");
    }
    System.out.println();

    // Method 4: ListIterator (bidirectional)
    List<String> mutableCities = new ArrayList<>(cities);
    System.out.println("\nListIterator (forward):");
    ListIterator<String> listIterator = mutableCities.listIterator();
    while (listIterator.hasNext()) {
      System.out.print(listIterator.next() + " ");
    }
    System.out.println();

    System.out.println("ListIterator (backward):");
    while (listIterator.hasPrevious()) {
      System.out.print(listIterator.previous() + " ");
    }
    System.out.println();

    // Method 5: forEach (Java 8)
    System.out.println("\nforEach method:");
    cities.forEach(city -> System.out.print(city + " "));
    System.out.println();

    // Method 6: Stream forEach
    System.out.println("\nStream forEach:");
    cities.stream().forEach(city -> System.out.print(city + " "));
    System.out.println("\n");
  }

  /**
   * Demonstrates sorting and searching.
   */
  private static void demonstrateSortingSearching() {
    System.out.println("--- Sorting and Searching ---");

    List<Integer> numbers = new ArrayList<>(List.of(45, 12, 78, 23, 56, 89, 34));
    System.out.println("Original: " + numbers);

    // Natural sorting
    Collections.sort(numbers);
    System.out.println("Sorted (ascending): " + numbers);

    // Reverse sorting
    Collections.sort(numbers, Collections.reverseOrder());
    System.out.println("Sorted (descending): " + numbers);

    // Binary search (list must be sorted)
    Collections.sort(numbers);
    int index = Collections.binarySearch(numbers, 56);
    System.out.println("\nBinary search for 56: index " + index);

    // Sorting strings
    List<String> names = new ArrayList<>(List.of("Charlie", "Alice", "Bob", "David"));
    System.out.println("\nNames: " + names);

    Collections.sort(names);
    System.out.println("Sorted alphabetically: " + names);

    // Custom comparator - sort by length
    names.sort(Comparator.comparingInt(String::length));
    System.out.println("Sorted by length: " + names);

    // Reverse
    Collections.reverse(names);
    System.out.println("Reversed: " + names);

    // Shuffle
    Collections.shuffle(numbers);
    System.out.println("\nShuffled numbers: " + numbers);

    System.out.println();
  }

  /**
   * Demonstrates ArrayList vs LinkedList performance.
   */
  private static void demonstrateListComparison() {
    System.out.println("--- ArrayList vs LinkedList ---");

    System.out.println("ArrayList:");
    System.out.println("  - Fast random access (O(1))");
    System.out.println("  - Slow insertion/deletion in middle (O(n))");
    System.out.println("  - Good for read-heavy operations");
    System.out.println("  - Uses contiguous memory");

    System.out.println("\nLinkedList:");
    System.out.println("  - Slow random access (O(n))");
    System.out.println("  - Fast insertion/deletion (O(1) if position known)");
    System.out.println("  - Good for frequent insertions/deletions");
    System.out.println("  - Uses non-contiguous memory");

    System.out.println("\nUse ArrayList when:");
    System.out.println("  - You need fast random access");
    System.out.println("  - You add/remove mostly at the end");
    System.out.println("  - Memory is a concern");

    System.out.println("\nUse LinkedList when:");
    System.out.println("  - You frequently insert/remove from beginning/middle");
    System.out.println("  - You need a queue/deque");
    System.out.println("  - Random access is not critical");

    System.out.println();
  }

  /**
   * Demonstrates utility methods from Collections class.
   */
  private static void demonstrateUtilityMethods() {
    System.out.println("--- Collections Utility Methods ---");

    List<Integer> numbers = new ArrayList<>(List.of(3, 7, 1, 9, 4, 2, 8, 5, 6));
    System.out.println("Original: " + numbers);

    // Min and Max
    System.out.println("Min: " + Collections.min(numbers));
    System.out.println("Max: " + Collections.max(numbers));

    // Frequency
    List<String> letters = List.of("A", "B", "A", "C", "A", "B");
    System.out.println("\nLetters: " + letters);
    System.out.println("Frequency of 'A': " + Collections.frequency(letters, "A"));

    // Fill
    List<String> filled = new ArrayList<>(Collections.nCopies(5, "X"));
    System.out.println("\nFilled list: " + filled);

    // Rotate
    List<Integer> rotate = new ArrayList<>(List.of(1, 2, 3, 4, 5));
    Collections.rotate(rotate, 2);
    System.out.println("After rotate by 2: " + rotate);

    // Swap
    List<String> swap = new ArrayList<>(List.of("A", "B", "C", "D"));
    Collections.swap(swap, 0, 3);
    System.out.println("After swapping index 0 and 3: " + swap);

    // Immutable list
    List<String> immutable = List.of("A", "B", "C");
    System.out.println("\nImmutable list: " + immutable);
    // immutable.add("D"); // Would throw UnsupportedOperationException

    // Unmodifiable wrapper
    List<String> modifiable = new ArrayList<>(List.of("X", "Y", "Z"));
    List<String> unmodifiable = Collections.unmodifiableList(modifiable);
    System.out.println("Unmodifiable list: " + unmodifiable);
    // unmodifiable.add("W"); // Would throw UnsupportedOperationException

    System.out.println();
  }

  /**
   * Demonstrates real-world List usage.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Task Manager ---");

    TaskManager taskManager = new TaskManager();

    // Add tasks
    taskManager.addTask(new Task("Write report", Priority.HIGH));
    taskManager.addTask(new Task("Email client", Priority.MEDIUM));
    taskManager.addTask(new Task("Team meeting", Priority.HIGH));
    taskManager.addTask(new Task("Code review", Priority.LOW));
    taskManager.addTask(new Task("Update documentation", Priority.MEDIUM));

    // Display all tasks
    System.out.println("\nAll Tasks:");
    taskManager.displayTasks();

    // Sort by priority
    System.out.println("\nSorted by Priority:");
    taskManager.sortByPriority();
    taskManager.displayTasks();

    // Get high priority tasks
    System.out.println("\nHigh Priority Tasks:");
    List<Task> highPriority = taskManager.getTasksByPriority(Priority.HIGH);
    highPriority.forEach(task -> System.out.println("  " + task));

    // Complete a task
    System.out.println("\nCompleting first task...");
    taskManager.completeTask(0);
    taskManager.displayTasks();

    // Statistics
    System.out.println("\nStatistics:");
    System.out.println("  Total tasks: " + taskManager.getTotalTasks());
    System.out.println("  Completed: " + taskManager.getCompletedTasksCount());
    System.out.println("  Pending: " + taskManager.getPendingTasksCount());

    System.out.println();
  }
}

// ========== Task Manager Example ==========

/**
 * Priority enum for tasks.
 */
enum Priority {
  LOW(1), MEDIUM(2), HIGH(3);

  private final int value;

  Priority(int value) {
    this.value = value;
  }

  public int getValue() {
    return value;
  }
}

/**
 * Task class representing a task item.
 */
class Task {
  private String description;
  private Priority priority;
  private boolean completed;

  public Task(String description, Priority priority) {
    this.description = description;
    this.priority = priority;
    this.completed = false;
  }

  public String getDescription() {
    return description;
  }

  public Priority getPriority() {
    return priority;
  }

  public boolean isCompleted() {
    return completed;
  }

  public void setCompleted(boolean completed) {
    this.completed = completed;
  }

  @Override
  public String toString() {
    String status = completed ? "[✓]" : "[ ]";
    return String.format("%s %s - %s", status, priority, description);
  }
}

/**
 * TaskManager class managing a list of tasks.
 */
class TaskManager {
  private List<Task> tasks;

  public TaskManager() {
    this.tasks = new ArrayList<>();
  }

  public void addTask(Task task) {
    tasks.add(task);
    System.out.println("Task added: " + task.getDescription());
  }

  public void removeTask(int index) {
    if (index >= 0 && index < tasks.size()) {
      Task removed = tasks.remove(index);
      System.out.println("Task removed: " + removed.getDescription());
    }
  }

  public void completeTask(int index) {
    if (index >= 0 && index < tasks.size()) {
      tasks.get(index).setCompleted(true);
    }
  }

  public List<Task> getTasksByPriority(Priority priority) {
    List<Task> filtered = new ArrayList<>();
    for (Task task : tasks) {
      if (task.getPriority() == priority) {
        filtered.add(task);
      }
    }
    return filtered;
  }

  public void sortByPriority() {
    tasks.sort((t1, t2) -> Integer.compare(
        t2.getPriority().getValue(), 
        t1.getPriority().getValue()
    ));
  }

  public void displayTasks() {
    if (tasks.isEmpty()) {
      System.out.println("  No tasks");
      return;
    }

    for (int i = 0; i < tasks.size(); i++) {
      System.out.println("  " + (i + 1) + ". " + tasks.get(i));
    }
  }

  public int getTotalTasks() {
    return tasks.size();
  }

  public int getCompletedTasksCount() {
    int count = 0;
    for (Task task : tasks) {
      if (task.isCompleted()) {
        count++;
      }
    }
    return count;
  }

  public int getPendingTasksCount() {
    return getTotalTasks() - getCompletedTasksCount();
  }
}
