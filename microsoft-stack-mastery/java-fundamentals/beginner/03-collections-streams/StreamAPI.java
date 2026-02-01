package com.microsoft.java.collections;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.IntStream;
import java.util.Optional;
import java.util.Map;

/**
 * StreamAPI - Comprehensive demonstration of Java Stream API.
 *
 * <p>This class covers:
 * - Stream creation from various sources
 * - Intermediate operations (filter, map, flatMap, distinct, sorted, etc.)
 * - Terminal operations (collect, forEach, reduce, count, etc.)
 * - Parallel streams
 * - Stream best practices
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class StreamAPI {

  /**
   * Main method demonstrating Stream API operations.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Stream API Demonstration ===\n");

    demonstrateStreamCreation();
    demonstrateFilterOperation();
    demonstrateMapOperation();
    demonstrateFlatMapOperation();
    demonstrateDistinctAndSorted();
    demonstrateLimitAndSkip();
    demonstrateCollectOperation();
    demonstrateReduceOperation();
    demonstrateMatchingOperations();
    demonstrateFindOperations();
    demonstrateNumericStreams();
    demonstrateGroupingAndPartitioning();
    demonstrateParallelStreams();
    realWorldExample();
  }

  /**
   * Demonstrates different ways to create streams.
   */
  private static void demonstrateStreamCreation() {
    System.out.println("--- Stream Creation ---");

    // From collection
    List<String> list = Arrays.asList("A", "B", "C");
    Stream<String> stream1 = list.stream();
    System.out.println("From list: " + stream1.collect(Collectors.toList()));

    // From array
    String[] array = {"X", "Y", "Z"};
    Stream<String> stream2 = Arrays.stream(array);
    System.out.println("From array: " + stream2.collect(Collectors.toList()));

    // Using Stream.of()
    Stream<Integer> stream3 = Stream.of(1, 2, 3, 4, 5);
    System.out.println("Using Stream.of: " + stream3.collect(Collectors.toList()));

    // Infinite stream with limit
    Stream<Integer> infiniteStream = Stream.iterate(0, n -> n + 2).limit(5);
    System.out.println("Infinite stream (limited): " 
        + infiniteStream.collect(Collectors.toList()));

    // Generate stream
    Stream<Double> randomStream = Stream.generate(Math::random).limit(3);
    System.out.println("Generated stream: " + randomStream.collect(Collectors.toList()));

    // Empty stream
    Stream<String> emptyStream = Stream.empty();
    System.out.println("Empty stream count: " + emptyStream.count());

    // Range streams
    IntStream range = IntStream.range(1, 6); // Exclusive end
    System.out.println("IntStream range: " + range.boxed().collect(Collectors.toList()));

    IntStream rangeClosed = IntStream.rangeClosed(1, 5); // Inclusive end
    System.out.println("IntStream rangeClosed: " 
        + rangeClosed.boxed().collect(Collectors.toList()));

    System.out.println();
  }

  /**
   * Demonstrates filter operation.
   */
  private static void demonstrateFilterOperation() {
    System.out.println("--- Filter Operation ---");

    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

    // Filter even numbers
    List<Integer> evenNumbers = numbers.stream()
        .filter(n -> n % 2 == 0)
        .collect(Collectors.toList());
    System.out.println("Even numbers: " + evenNumbers);

    // Filter odd numbers
    List<Integer> oddNumbers = numbers.stream()
        .filter(n -> n % 2 != 0)
        .collect(Collectors.toList());
    System.out.println("Odd numbers: " + oddNumbers);

    // Multiple filters (chained)
    List<Integer> filtered = numbers.stream()
        .filter(n -> n > 3)
        .filter(n -> n < 8)
        .filter(n -> n % 2 == 0)
        .collect(Collectors.toList());
    System.out.println("Multiple filters (>3, <8, even): " + filtered);

    // Filter with complex condition
    List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve");
    List<String> filteredNames = names.stream()
        .filter(name -> name.length() > 3 && name.startsWith("A"))
        .collect(Collectors.toList());
    System.out.println("Names (length>3 and starts with A): " + filteredNames);

    System.out.println();
  }

  /**
   * Demonstrates map operation.
   */
  private static void demonstrateMapOperation() {
    System.out.println("--- Map Operation ---");

    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

    // Square each number
    List<Integer> squared = numbers.stream()
        .map(n -> n * n)
        .collect(Collectors.toList());
    System.out.println("Squared: " + squared);

    // String transformation
    List<String> names = Arrays.asList("alice", "bob", "charlie");
    List<String> uppercase = names.stream()
        .map(String::toUpperCase)
        .collect(Collectors.toList());
    System.out.println("Uppercase: " + uppercase);

    // String length
    List<Integer> nameLengths = names.stream()
        .map(String::length)
        .collect(Collectors.toList());
    System.out.println("Name lengths: " + nameLengths);

    // Object transformation
    List<Person> people = Arrays.asList(
        new Person("Alice", 30),
        new Person("Bob", 25),
        new Person("Charlie", 35)
    );

    List<String> personNames = people.stream()
        .map(Person::getName)
        .collect(Collectors.toList());
    System.out.println("Person names: " + personNames);

    System.out.println();
  }

  /**
   * Demonstrates flatMap operation.
   */
  private static void demonstrateFlatMapOperation() {
    System.out.println("--- FlatMap Operation ---");

    // Flattening list of lists
    List<List<Integer>> listOfLists = Arrays.asList(
        Arrays.asList(1, 2, 3),
        Arrays.asList(4, 5),
        Arrays.asList(6, 7, 8, 9)
    );

    List<Integer> flattened = listOfLists.stream()
        .flatMap(List::stream)
        .collect(Collectors.toList());
    System.out.println("Flattened: " + flattened);

    // Splitting strings into words
    List<String> sentences = Arrays.asList(
        "Hello World",
        "Java Streams",
        "Are Powerful"
    );

    List<String> words = sentences.stream()
        .flatMap(sentence -> Arrays.stream(sentence.split(" ")))
        .collect(Collectors.toList());
    System.out.println("Words: " + words);

    // Flattening arrays
    String[][] arrays = {{"A", "B"}, {"C", "D"}, {"E", "F"}};
    List<String> flatArray = Arrays.stream(arrays)
        .flatMap(Arrays::stream)
        .collect(Collectors.toList());
    System.out.println("Flat array: " + flatArray);

    System.out.println();
  }

  /**
   * Demonstrates distinct and sorted operations.
   */
  private static void demonstrateDistinctAndSorted() {
    System.out.println("--- Distinct and Sorted ---");

    List<Integer> numbers = Arrays.asList(5, 2, 8, 2, 9, 1, 5, 3, 8);

    // Distinct
    List<Integer> distinct = numbers.stream()
        .distinct()
        .collect(Collectors.toList());
    System.out.println("Distinct: " + distinct);

    // Sorted (natural order)
    List<Integer> sorted = numbers.stream()
        .sorted()
        .collect(Collectors.toList());
    System.out.println("Sorted: " + sorted);

    // Sorted (reverse order)
    List<Integer> sortedReverse = numbers.stream()
        .sorted((a, b) -> b - a)
        .collect(Collectors.toList());
    System.out.println("Sorted (reverse): " + sortedReverse);

    // Distinct and sorted
    List<Integer> distinctSorted = numbers.stream()
        .distinct()
        .sorted()
        .collect(Collectors.toList());
    System.out.println("Distinct and sorted: " + distinctSorted);

    // Sort strings by length
    List<String> words = Arrays.asList("banana", "apple", "cherry", "date");
    List<String> sortedByLength = words.stream()
        .sorted((a, b) -> Integer.compare(a.length(), b.length()))
        .collect(Collectors.toList());
    System.out.println("Sorted by length: " + sortedByLength);

    System.out.println();
  }

  /**
   * Demonstrates limit and skip operations.
   */
  private static void demonstrateLimitAndSkip() {
    System.out.println("--- Limit and Skip ---");

    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

    // Limit - take first n elements
    List<Integer> firstFive = numbers.stream()
        .limit(5)
        .collect(Collectors.toList());
    System.out.println("First 5: " + firstFive);

    // Skip - skip first n elements
    List<Integer> skipFive = numbers.stream()
        .skip(5)
        .collect(Collectors.toList());
    System.out.println("Skip first 5: " + skipFive);

    // Pagination: skip and limit
    int pageSize = 3;
    int pageNumber = 2; // Zero-indexed

    List<Integer> page = numbers.stream()
        .skip(pageNumber * pageSize)
        .limit(pageSize)
        .collect(Collectors.toList());
    System.out.println("Page 2 (size 3): " + page);

    System.out.println();
  }

  /**
   * Demonstrates collect operation.
   */
  private static void demonstrateCollectOperation() {
    System.out.println("--- Collect Operation ---");

    List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David", "Eve");

    // Collect to List
    List<String> list = names.stream()
        .filter(n -> n.length() > 3)
        .collect(Collectors.toList());
    System.out.println("To List: " + list);

    // Collect to Set
    List<Integer> numbers = Arrays.asList(1, 2, 2, 3, 3, 4, 5);
    var set = numbers.stream().collect(Collectors.toSet());
    System.out.println("To Set: " + set);

    // Joining strings
    String joined = names.stream()
        .collect(Collectors.joining(", "));
    System.out.println("Joined: " + joined);

    // Joining with prefix and suffix
    String formatted = names.stream()
        .collect(Collectors.joining(", ", "[", "]"));
    System.out.println("Formatted: " + formatted);

    // Collecting to Map
    List<Person> people = Arrays.asList(
        new Person("Alice", 30),
        new Person("Bob", 25)
    );

    Map<String, Integer> nameAgeMap = people.stream()
        .collect(Collectors.toMap(Person::getName, Person::getAge));
    System.out.println("To Map: " + nameAgeMap);

    System.out.println();
  }

  /**
   * Demonstrates reduce operation.
   */
  private static void demonstrateReduceOperation() {
    System.out.println("--- Reduce Operation ---");

    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

    // Sum using reduce
    int sum = numbers.stream()
        .reduce(0, Integer::sum);
    System.out.println("Sum: " + sum);

    // Product using reduce
    int product = numbers.stream()
        .reduce(1, (a, b) -> a * b);
    System.out.println("Product: " + product);

    // Max using reduce
    Optional<Integer> max = numbers.stream()
        .reduce(Integer::max);
    System.out.println("Max: " + max.orElse(0));

    // Min using reduce
    Optional<Integer> min = numbers.stream()
        .reduce(Integer::min);
    System.out.println("Min: " + min.orElse(0));

    // Concatenating strings
    List<String> words = Arrays.asList("Java", "Stream", "API");
    String concatenated = words.stream()
        .reduce("", (a, b) -> a + " " + b).trim();
    System.out.println("Concatenated: " + concatenated);

    System.out.println();
  }

  /**
   * Demonstrates matching operations.
   */
  private static void demonstrateMatchingOperations() {
    System.out.println("--- Matching Operations ---");

    List<Integer> numbers = Arrays.asList(2, 4, 6, 8, 10);

    // allMatch - all elements match predicate
    boolean allEven = numbers.stream()
        .allMatch(n -> n % 2 == 0);
    System.out.println("All even: " + allEven);

    // anyMatch - at least one element matches
    boolean anyGreaterThan5 = numbers.stream()
        .anyMatch(n -> n > 5);
    System.out.println("Any greater than 5: " + anyGreaterThan5);

    // noneMatch - no elements match
    boolean noneOdd = numbers.stream()
        .noneMatch(n -> n % 2 != 0);
    System.out.println("None odd: " + noneOdd);

    System.out.println();
  }

  /**
   * Demonstrates find operations.
   */
  private static void demonstrateFindOperations() {
    System.out.println("--- Find Operations ---");

    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8);

    // findFirst
    Optional<Integer> first = numbers.stream()
        .filter(n -> n > 3)
        .findFirst();
    System.out.println("First > 3: " + first.orElse(-1));

    // findAny (useful in parallel streams)
    Optional<Integer> any = numbers.stream()
        .filter(n -> n > 5)
        .findAny();
    System.out.println("Any > 5: " + any.orElse(-1));

    // count
    long count = numbers.stream()
        .filter(n -> n % 2 == 0)
        .count();
    System.out.println("Count of even numbers: " + count);

    System.out.println();
  }

  /**
   * Demonstrates numeric stream operations.
   */
  private static void demonstrateNumericStreams() {
    System.out.println("--- Numeric Streams ---");

    // IntStream statistics
    IntStream intStream = IntStream.rangeClosed(1, 10);
    var stats = intStream.summaryStatistics();

    System.out.println("IntStream statistics:");
    System.out.println("  Count: " + stats.getCount());
    System.out.println("  Sum: " + stats.getSum());
    System.out.println("  Min: " + stats.getMin());
    System.out.println("  Max: " + stats.getMax());
    System.out.println("  Average: " + stats.getAverage());

    // Sum
    int sum = IntStream.range(1, 11).sum();
    System.out.println("\nSum of 1-10: " + sum);

    // Average
    double avg = IntStream.range(1, 11).average().orElse(0.0);
    System.out.println("Average of 1-10: " + avg);

    System.out.println();
  }

  /**
   * Demonstrates grouping and partitioning.
   */
  private static void demonstrateGroupingAndPartitioning() {
    System.out.println("--- Grouping and Partitioning ---");

    List<Person> people = Arrays.asList(
        new Person("Alice", 30),
        new Person("Bob", 25),
        new Person("Charlie", 30),
        new Person("Diana", 35),
        new Person("Eve", 25)
    );

    // Group by age
    Map<Integer, List<Person>> byAge = people.stream()
        .collect(Collectors.groupingBy(Person::getAge));
    System.out.println("Grouped by age:");
    byAge.forEach((age, group) -> 
        System.out.println("  " + age + ": " + group));

    // Partition by age > 30
    Map<Boolean, List<Person>> partitioned = people.stream()
        .collect(Collectors.partitioningBy(p -> p.getAge() > 30));
    System.out.println("\nPartitioned (age > 30):");
    System.out.println("  True: " + partitioned.get(true));
    System.out.println("  False: " + partitioned.get(false));

    // Count by age
    Map<Integer, Long> countByAge = people.stream()
        .collect(Collectors.groupingBy(Person::getAge, Collectors.counting()));
    System.out.println("\nCount by age: " + countByAge);

    System.out.println();
  }

  /**
   * Demonstrates parallel streams.
   */
  private static void demonstrateParallelStreams() {
    System.out.println("--- Parallel Streams ---");

    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

    // Sequential stream
    long startSeq = System.currentTimeMillis();
    int sumSeq = numbers.stream()
        .map(n -> n * n)
        .reduce(0, Integer::sum);
    long endSeq = System.currentTimeMillis();
    System.out.println("Sequential sum: " + sumSeq + " (time: " + (endSeq - startSeq) + "ms)");

    // Parallel stream
    long startPar = System.currentTimeMillis();
    int sumPar = numbers.parallelStream()
        .map(n -> n * n)
        .reduce(0, Integer::sum);
    long endPar = System.currentTimeMillis();
    System.out.println("Parallel sum: " + sumPar + " (time: " + (endPar - startPar) + "ms)");

    System.out.println("\nNote: Parallel streams are beneficial for:");
    System.out.println("  - Large datasets");
    System.out.println("  - CPU-intensive operations");
    System.out.println("  - Independent operations");

    System.out.println();
  }

  /**
   * Demonstrates real-world Stream API usage.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: E-commerce Analytics ---");

    List<Order> orders = Arrays.asList(
        new Order("ORD001", "Alice", 250.00, "Electronics"),
        new Order("ORD002", "Bob", 50.00, "Books"),
        new Order("ORD003", "Alice", 120.00, "Clothing"),
        new Order("ORD004", "Charlie", 300.00, "Electronics"),
        new Order("ORD005", "Bob", 80.00, "Books"),
        new Order("ORD006", "Diana", 450.00, "Electronics"),
        new Order("ORD007", "Alice", 90.00, "Books")
    );

    // Total revenue
    double totalRevenue = orders.stream()
        .mapToDouble(Order::getAmount)
        .sum();
    System.out.printf("Total Revenue: $%.2f%n", totalRevenue);

    // Average order value
    double avgOrderValue = orders.stream()
        .mapToDouble(Order::getAmount)
        .average()
        .orElse(0.0);
    System.out.printf("Average Order Value: $%.2f%n", avgOrderValue);

    // Revenue by category
    System.out.println("\nRevenue by Category:");
    orders.stream()
        .collect(Collectors.groupingBy(
            Order::getCategory,
            Collectors.summingDouble(Order::getAmount)
        ))
        .forEach((category, revenue) -> 
            System.out.printf("  %s: $%.2f%n", category, revenue));

    // Top customers by total spending
    System.out.println("\nTop Customers:");
    orders.stream()
        .collect(Collectors.groupingBy(
            Order::getCustomer,
            Collectors.summingDouble(Order::getAmount)
        ))
        .entrySet().stream()
        .sorted((e1, e2) -> Double.compare(e2.getValue(), e1.getValue()))
        .limit(3)
        .forEach(entry -> 
            System.out.printf("  %s: $%.2f%n", entry.getKey(), entry.getValue()));

    // High-value orders (>$200)
    System.out.println("\nHigh-Value Orders (>$200):");
    orders.stream()
        .filter(order -> order.getAmount() > 200)
        .forEach(order -> System.out.println("  " + order));

    // Count orders by customer
    System.out.println("\nOrders per Customer:");
    orders.stream()
        .collect(Collectors.groupingBy(Order::getCustomer, Collectors.counting()))
        .forEach((customer, count) -> 
            System.out.printf("  %s: %d orders%n", customer, count));

    System.out.println();
  }
}

// ========== Helper Classes ==========

/**
 * Person class for examples.
 */
class Person {
  private String name;
  private int age;

  public Person(String name, int age) {
    this.name = name;
    this.age = age;
  }

  public String getName() {
    return name;
  }

  public int getAge() {
    return age;
  }

  @Override
  public String toString() {
    return name + "(" + age + ")";
  }
}

/**
 * Order class for real-world example.
 */
class Order {
  private String orderId;
  private String customer;
  private double amount;
  private String category;

  public Order(String orderId, String customer, double amount, String category) {
    this.orderId = orderId;
    this.customer = customer;
    this.amount = amount;
    this.category = category;
  }

  public String getOrderId() {
    return orderId;
  }

  public String getCustomer() {
    return customer;
  }

  public double getAmount() {
    return amount;
  }

  public String getCategory() {
    return category;
  }

  @Override
  public String toString() {
    return String.format("%s: %s - $%.2f (%s)", orderId, customer, amount, category);
  }
}
