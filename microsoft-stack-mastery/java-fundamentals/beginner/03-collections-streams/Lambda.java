package com.microsoft.java.collections;

import java.util.Arrays;
import java.util.List;
import java.util.function.*;
import java.util.Comparator;

/**
 * Lambda - Comprehensive demonstration of Lambda expressions in Java.
 *
 * <p>This class covers:
 * - Lambda syntax and basics
 * - Functional interfaces
 * - Built-in functional interfaces (Predicate, Function, Consumer, Supplier)
 * - Method references
 * - Lambda best practices
 * - Real-world use cases
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class Lambda {

  /**
   * Main method demonstrating Lambda expressions.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Lambda Expressions ===\n");

    demonstrateLambdaBasics();
    demonstrateFunctionalInterfaces();
    demonstratePredicate();
    demonstrateFunction();
    demonstrateConsumer();
    demonstrateSupplier();
    demonstrateBiFunction();
    demonstrateMethodReferences();
    demonstrateComparator();
    realWorldExample();
  }

  /**
   * Demonstrates basic lambda syntax.
   */
  private static void demonstrateLambdaBasics() {
    System.out.println("--- Lambda Basics ---");

    // Traditional anonymous class
    Runnable oldWay = new Runnable() {
      @Override
      public void run() {
        System.out.println("Old way: Anonymous class");
      }
    };
    oldWay.run();

    // Lambda expression
    Runnable newWay = () -> System.out.println("New way: Lambda expression");
    newWay.run();

    // Lambda with parameters
    Calculator add = (a, b) -> a + b;
    System.out.println("Addition (5 + 3): " + add.calculate(5, 3));

    // Lambda with multiple statements
    Calculator multiply = (a, b) -> {
      System.out.println("Multiplying " + a + " and " + b);
      return a * b;
    };
    System.out.println("Result: " + multiply.calculate(4, 5));

    // Lambda with single parameter (parentheses optional)
    StringTransformer uppercase = s -> s.toUpperCase();
    System.out.println("Uppercase: " + uppercase.transform("hello"));

    System.out.println();
  }

  /**
   * Demonstrates custom functional interfaces.
   */
  private static void demonstrateFunctionalInterfaces() {
    System.out.println("--- Functional Interfaces ---");

    // Functional interfaces can have only one abstract method
    Greeting englishGreeting = name -> "Hello, " + name + "!";
    Greeting spanishGreeting = name -> "¡Hola, " + name + "!";
    Greeting frenchGreeting = name -> "Bonjour, " + name + "!";

    System.out.println(englishGreeting.greet("Alice"));
    System.out.println(spanishGreeting.greet("Bob"));
    System.out.println(frenchGreeting.greet("Charlie"));

    // Using functional interface with multiple parameters
    MathOperation addition = (a, b) -> a + b;
    MathOperation subtraction = (a, b) -> a - b;
    MathOperation multiplication = (a, b) -> a * b;
    MathOperation division = (a, b) -> b != 0 ? a / b : 0;

    System.out.println("\nMath Operations:");
    System.out.println("10 + 5 = " + operate(10, 5, addition));
    System.out.println("10 - 5 = " + operate(10, 5, subtraction));
    System.out.println("10 * 5 = " + operate(10, 5, multiplication));
    System.out.println("10 / 5 = " + operate(10, 5, division));

    System.out.println();
  }

  /**
   * Helper method for demonstrating functional interfaces.
   */
  private static int operate(int a, int b, MathOperation operation) {
    return operation.execute(a, b);
  }

  /**
   * Demonstrates Predicate functional interface.
   */
  private static void demonstratePredicate() {
    System.out.println("--- Predicate Interface ---");

    // Predicate<T> - takes one argument, returns boolean
    Predicate<Integer> isEven = n -> n % 2 == 0;
    Predicate<Integer> isPositive = n -> n > 0;
    Predicate<String> isLongString = s -> s.length() > 5;

    System.out.println("Is 4 even? " + isEven.test(4));
    System.out.println("Is 7 even? " + isEven.test(7));
    System.out.println("Is 10 positive? " + isPositive.test(10));
    System.out.println("Is -5 positive? " + isPositive.test(-5));
    System.out.println("Is 'Hello' long? " + isLongString.test("Hello"));
    System.out.println("Is 'Hello World' long? " + isLongString.test("Hello World"));

    // Combining predicates
    Predicate<Integer> isEvenAndPositive = isEven.and(isPositive);
    Predicate<Integer> isEvenOrPositive = isEven.or(isPositive);
    Predicate<Integer> isNotEven = isEven.negate();

    System.out.println("\nCombining predicates:");
    System.out.println("Is 4 even AND positive? " + isEvenAndPositive.test(4));
    System.out.println("Is -2 even AND positive? " + isEvenAndPositive.test(-2));
    System.out.println("Is -3 even OR positive? " + isEvenOrPositive.test(-3));
    System.out.println("Is 5 NOT even? " + isNotEven.test(5));

    // Using with collections
    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
    System.out.println("\nFiltering with Predicate:");
    filterAndPrint(numbers, isEven, "Even numbers");
    filterAndPrint(numbers, n -> n > 5, "Greater than 5");

    System.out.println();
  }

  /**
   * Helper method for filtering with predicates.
   */
  private static <T> void filterAndPrint(List<T> list, Predicate<T> predicate, String label) {
    System.out.print(label + ": ");
    list.stream()
        .filter(predicate)
        .forEach(item -> System.out.print(item + " "));
    System.out.println();
  }

  /**
   * Demonstrates Function functional interface.
   */
  private static void demonstrateFunction() {
    System.out.println("--- Function Interface ---");

    // Function<T, R> - takes one argument of type T, returns type R
    Function<String, Integer> stringLength = s -> s.length();
    Function<Integer, Integer> square = n -> n * n;
    Function<String, String> uppercase = String::toUpperCase;

    System.out.println("Length of 'Hello': " + stringLength.apply("Hello"));
    System.out.println("Square of 5: " + square.apply(5));
    System.out.println("Uppercase 'world': " + uppercase.apply("world"));

    // Composing functions
    Function<Integer, Integer> addTwo = n -> n + 2;
    Function<Integer, Integer> multiplyByThree = n -> n * 3;

    // andThen: f.andThen(g) means g(f(x))
    Function<Integer, Integer> addThenMultiply = addTwo.andThen(multiplyByThree);
    System.out.println("\n(5 + 2) * 3 = " + addThenMultiply.apply(5));

    // compose: f.compose(g) means f(g(x))
    Function<Integer, Integer> multiplyThenAdd = addTwo.compose(multiplyByThree);
    System.out.println("(5 * 3) + 2 = " + multiplyThenAdd.apply(5));

    // Chaining multiple functions
    Function<String, Integer> stringToLength = String::length;
    Function<Integer, Integer> lengthSquared = n -> n * n;
    Function<String, Integer> stringToSquaredLength = stringToLength.andThen(lengthSquared);

    System.out.println("Squared length of 'Lambda': " 
        + stringToSquaredLength.apply("Lambda"));

    System.out.println();
  }

  /**
   * Demonstrates Consumer functional interface.
   */
  private static void demonstrateConsumer() {
    System.out.println("--- Consumer Interface ---");

    // Consumer<T> - takes one argument, returns void
    Consumer<String> printUpperCase = s -> System.out.println(s.toUpperCase());
    Consumer<Integer> printSquare = n -> System.out.println(n * n);

    System.out.println("Print uppercase:");
    printUpperCase.accept("hello");

    System.out.println("\nPrint square:");
    printSquare.accept(5);

    // Chaining consumers
    Consumer<String> printLine = System.out::println;
    Consumer<String> printLength = s -> System.out.println("Length: " + s.length());

    Consumer<String> printBoth = printLine.andThen(printLength);
    System.out.println("\nChained consumers:");
    printBoth.accept("Lambda");

    // Using with collections
    List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
    System.out.println("\nProcessing list with Consumer:");
    names.forEach(name -> System.out.println("Hello, " + name));

    System.out.println();
  }

  /**
   * Demonstrates Supplier functional interface.
   */
  private static void demonstrateSupplier() {
    System.out.println("--- Supplier Interface ---");

    // Supplier<T> - takes no arguments, returns type T
    Supplier<Double> randomNumber = () -> Math.random();
    Supplier<String> currentTime = () -> 
        java.time.LocalTime.now().toString();
    Supplier<Integer> constantValue = () -> 42;

    System.out.println("Random number: " + randomNumber.get());
    System.out.println("Current time: " + currentTime.get());
    System.out.println("Constant value: " + constantValue.get());

    // Lazy initialization with Supplier
    Supplier<ExpensiveObject> expensiveSupplier = () -> {
      System.out.println("Creating expensive object...");
      return new ExpensiveObject();
    };

    System.out.println("\nLazy initialization:");
    System.out.println("Supplier created (object not yet created)");
    System.out.println("Now getting object:");
    ExpensiveObject obj = expensiveSupplier.get();
    System.out.println("Object created: " + obj);

    System.out.println();
  }

  /**
   * Demonstrates BiFunction and other Bi- interfaces.
   */
  private static void demonstrateBiFunction() {
    System.out.println("--- BiFunction and Bi- Interfaces ---");

    // BiFunction<T, U, R> - takes two arguments, returns result
    BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
    BiFunction<String, String, String> concat = (s1, s2) -> s1 + " " + s2;

    System.out.println("Add 5 + 3: " + add.apply(5, 3));
    System.out.println("Concat: " + concat.apply("Hello", "World"));

    // BiPredicate<T, U> - takes two arguments, returns boolean
    BiPredicate<String, Integer> isLengthEqual = (s, n) -> s.length() == n;
    System.out.println("\nIs 'Hello' length 5? " + isLengthEqual.test("Hello", 5));

    // BiConsumer<T, U> - takes two arguments, returns void
    BiConsumer<String, Integer> printWithIndex = (s, i) -> 
        System.out.println(i + ": " + s);

    System.out.println("\nBiConsumer example:");
    List<String> items = Arrays.asList("Apple", "Banana", "Cherry");
    for (int i = 0; i < items.size(); i++) {
      printWithIndex.accept(items.get(i), i);
    }

    System.out.println();
  }

  /**
   * Demonstrates method references.
   */
  private static void demonstrateMethodReferences() {
    System.out.println("--- Method References ---");

    List<String> names = Arrays.asList("Charlie", "Alice", "Bob", "Diana");

    // Static method reference
    System.out.println("Static method reference:");
    names.forEach(System.out::println);

    // Instance method reference
    System.out.println("\nInstance method reference (String::toUpperCase):");
    names.stream()
        .map(String::toUpperCase)
        .forEach(System.out::println);

    // Constructor reference
    System.out.println("\nConstructor reference:");
    Function<String, StringBuilder> sbCreator = StringBuilder::new;
    StringBuilder sb = sbCreator.apply("Hello");
    System.out.println("Created: " + sb);

    // Reference to instance method of particular object
    String prefix = "Name: ";
    Consumer<String> printer = prefix::concat;
    // Note: This just creates the string, doesn't print it in this context

    System.out.println("\nMethod reference types:");
    System.out.println("  1. Static method: ClassName::staticMethod");
    System.out.println("  2. Instance method of object: object::instanceMethod");
    System.out.println("  3. Instance method of class: ClassName::instanceMethod");
    System.out.println("  4. Constructor: ClassName::new");

    System.out.println();
  }

  /**
   * Demonstrates lambda with Comparator.
   */
  private static void demonstrateComparator() {
    System.out.println("--- Comparator with Lambda ---");

    List<Product> products = Arrays.asList(
        new Product("Laptop", 999.99),
        new Product("Mouse", 29.99),
        new Product("Keyboard", 79.99),
        new Product("Monitor", 299.99)
    );

    // Sort by price (ascending)
    System.out.println("Sorted by price (ascending):");
    products.stream()
        .sorted(Comparator.comparingDouble(Product::getPrice))
        .forEach(System.out::println);

    // Sort by price (descending)
    System.out.println("\nSorted by price (descending):");
    products.stream()
        .sorted(Comparator.comparingDouble(Product::getPrice).reversed())
        .forEach(System.out::println);

    // Sort by name
    System.out.println("\nSorted by name:");
    products.stream()
        .sorted(Comparator.comparing(Product::getName))
        .forEach(System.out::println);

    // Custom comparator with lambda
    System.out.println("\nSorted by name length:");
    products.stream()
        .sorted((p1, p2) -> Integer.compare(p1.getName().length(), p2.getName().length()))
        .forEach(System.out::println);

    System.out.println();
  }

  /**
   * Demonstrates real-world lambda usage.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Data Processor ---");

    DataProcessor processor = new DataProcessor();

    // Define processing pipeline using lambdas
    processor.setValidator(data -> data != null && !data.isEmpty());
    processor.setTransformer(data -> data.trim().toUpperCase());
    processor.setProcessor(data -> {
      System.out.println("Processing: " + data);
      return "Processed: " + data;
    });
    processor.setErrorHandler(error -> 
      System.err.println("Error occurred: " + error.getMessage())
    );

    // Process valid data
    System.out.println("\nProcessing valid data:");
    String result1 = processor.process("  hello world  ");
    System.out.println("Result: " + result1);

    // Process invalid data
    System.out.println("\nProcessing invalid data:");
    String result2 = processor.process("");

    // Using with different configurations
    System.out.println("\nDifferent configuration:");
    processor.setValidator(data -> data != null && data.length() > 5);
    processor.setTransformer(String::toLowerCase);

    String result3 = processor.process("TESTING");
    System.out.println("Result: " + result3);

    String result4 = processor.process("Hi");
    System.out.println("Result: " + result4);

    System.out.println();
  }
}

// ========== Functional Interfaces ==========

/**
 * Custom functional interface for calculations.
 */
@FunctionalInterface
interface Calculator {
  int calculate(int a, int b);
}

/**
 * Custom functional interface for string transformation.
 */
@FunctionalInterface
interface StringTransformer {
  String transform(String input);
}

/**
 * Custom functional interface for greetings.
 */
@FunctionalInterface
interface Greeting {
  String greet(String name);
}

/**
 * Custom functional interface for math operations.
 */
@FunctionalInterface
interface MathOperation {
  int execute(int a, int b);
}

// ========== Helper Classes ==========

/**
 * Product class for examples.
 */
class Product {
  private String name;
  private double price;

  public Product(String name, double price) {
    this.name = name;
    this.price = price;
  }

  public String getName() {
    return name;
  }

  public double getPrice() {
    return price;
  }

  @Override
  public String toString() {
    return String.format("%s: $%.2f", name, price);
  }
}

/**
 * ExpensiveObject for Supplier example.
 */
class ExpensiveObject {
  public ExpensiveObject() {
    // Simulate expensive initialization
    try {
      Thread.sleep(100);
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
  }

  @Override
  public String toString() {
    return "ExpensiveObject instance";
  }
}

/**
 * DataProcessor demonstrating real-world lambda usage.
 */
class DataProcessor {
  private Predicate<String> validator;
  private Function<String, String> transformer;
  private Function<String, String> processor;
  private Consumer<Exception> errorHandler;

  public void setValidator(Predicate<String> validator) {
    this.validator = validator;
  }

  public void setTransformer(Function<String, String> transformer) {
    this.transformer = transformer;
  }

  public void setProcessor(Function<String, String> processor) {
    this.processor = processor;
  }

  public void setErrorHandler(Consumer<Exception> errorHandler) {
    this.errorHandler = errorHandler;
  }

  public String process(String data) {
    try {
      // Validate
      if (validator != null && !validator.test(data)) {
        throw new IllegalArgumentException("Validation failed");
      }

      // Transform
      String transformed = transformer != null ? transformer.apply(data) : data;

      // Process
      return processor != null ? processor.apply(transformed) : transformed;

    } catch (Exception e) {
      if (errorHandler != null) {
        errorHandler.accept(e);
      }
      return null;
    }
  }
}
