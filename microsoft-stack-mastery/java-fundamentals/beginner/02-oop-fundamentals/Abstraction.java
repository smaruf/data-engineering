package com.microsoft.java.oop;

/**
 * Abstraction - Comprehensive demonstration of abstraction in Java.
 *
 * <p>This class covers:
 * - Abstract classes
 * - Abstract methods
 * - Concrete methods in abstract classes
 * - Abstract class vs Interface
 * - Real-world abstraction examples
 * - Template method pattern
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class Abstraction {

  /**
   * Main method demonstrating abstraction concepts.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Abstraction Demonstration ===\n");

    demonstrateAbstractClasses();
    demonstrateTemplateMethod();
    demonstrateAbstractVsInterface();
    realWorldExample();
  }

  /**
   * Demonstrates basic abstract class usage.
   */
  private static void demonstrateAbstractClasses() {
    System.out.println("--- Abstract Classes ---");

    // Cannot instantiate abstract class
    // Animal animal = new Animal(); // Error!

    // Can create instances of concrete subclasses
    Animal dog = new Dog("Buddy");
    Animal cat = new Cat("Whiskers");
    Animal bird = new Bird("Tweety");

    Animal[] animals = {dog, cat, bird};

    for (Animal animal : animals) {
      System.out.println("\n" + animal.getName() + ":");
      animal.sleep();      // Concrete method from abstract class
      animal.makeSound();  // Abstract method implemented in subclass
      animal.move();       // Abstract method implemented in subclass
    }

    System.out.println();
  }

  /**
   * Demonstrates template method pattern.
   */
  private static void demonstrateTemplateMethod() {
    System.out.println("\n--- Template Method Pattern ---");

    DataProcessor csvProcessor = new CsvDataProcessor();
    DataProcessor jsonProcessor = new JsonDataProcessor();
    DataProcessor xmlProcessor = new XmlDataProcessor();

    System.out.println("Processing CSV data:");
    csvProcessor.process();

    System.out.println("\nProcessing JSON data:");
    jsonProcessor.process();

    System.out.println("\nProcessing XML data:");
    xmlProcessor.process();

    System.out.println();
  }

  /**
   * Demonstrates difference between abstract class and interface.
   */
  private static void demonstrateAbstractVsInterface() {
    System.out.println("--- Abstract Class vs Interface ---");

    System.out.println("Abstract class can have:");
    System.out.println("  - Constructor");
    System.out.println("  - Instance variables");
    System.out.println("  - Concrete methods");
    System.out.println("  - Abstract methods");
    System.out.println("  - Access modifiers (public, protected, private)");

    System.out.println("\nInterface can have:");
    System.out.println("  - No constructor");
    System.out.println("  - Only constants (public static final)");
    System.out.println("  - Abstract methods (implicitly public abstract)");
    System.out.println("  - Default methods (Java 8+)");
    System.out.println("  - Static methods (Java 8+)");
    System.out.println("  - All members are public");

    Vehicle car = new Car();
    car.start();
    car.stop();

    Flyable airplane = new Airplane();
    airplane.fly();
    airplane.land();

    System.out.println();
  }

  /**
   * Demonstrates real-world abstraction examples.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Banking System ---");

    BankAccount savings = new SavingsAccount("SA001", "Alice", 5000, 2.5);
    BankAccount checking = new CheckingAccount("CA001", "Bob", 3000, 500);

    System.out.println("Savings Account:");
    savings.displayInfo();
    savings.deposit(1000);
    savings.withdraw(500);
    savings.applyMonthlyFees();

    System.out.println("\nChecking Account:");
    checking.displayInfo();
    checking.deposit(200);
    checking.withdraw(3500); // Will use overdraft
    checking.applyMonthlyFees();

    System.out.println();
  }
}

// ========== Basic Abstraction Example ==========

/**
 * Abstract Animal class.
 *
 * <p>Demonstrates that abstract classes can have:
 * - Abstract methods (must be implemented by subclasses)
 * - Concrete methods (inherited as-is)
 * - Instance variables
 * - Constructor
 */
abstract class Animal {
  // Instance variable
  protected String name;

  /**
   * Constructor in abstract class.
   */
  public Animal(String name) {
    this.name = name;
  }

  /**
   * Abstract method - subclasses must implement.
   */
  public abstract void makeSound();

  /**
   * Abstract method - subclasses must implement.
   */
  public abstract void move();

  /**
   * Concrete method - inherited by all subclasses.
   */
  public void sleep() {
    System.out.println(name + " is sleeping... Zzz");
  }

  /**
   * Concrete method with implementation.
   */
  public String getName() {
    return name;
  }
}

/**
 * Dog class - concrete implementation of Animal.
 */
class Dog extends Animal {
  public Dog(String name) {
    super(name);
  }

  @Override
  public void makeSound() {
    System.out.println(name + " barks: Woof! Woof!");
  }

  @Override
  public void move() {
    System.out.println(name + " runs on four legs");
  }
}

/**
 * Cat class - concrete implementation of Animal.
 */
class Cat extends Animal {
  public Cat(String name) {
    super(name);
  }

  @Override
  public void makeSound() {
    System.out.println(name + " meows: Meow!");
  }

  @Override
  public void move() {
    System.out.println(name + " walks gracefully");
  }
}

/**
 * Bird class - concrete implementation of Animal.
 */
class Bird extends Animal {
  public Bird(String name) {
    super(name);
  }

  @Override
  public void makeSound() {
    System.out.println(name + " chirps: Chirp! Chirp!");
  }

  @Override
  public void move() {
    System.out.println(name + " flies in the sky");
  }
}

// ========== Template Method Pattern ==========

/**
 * Abstract DataProcessor demonstrating template method pattern.
 *
 * <p>The template method defines the skeleton of an algorithm,
 * delegating some steps to subclasses.
 */
abstract class DataProcessor {
  /**
   * Template method - defines the algorithm structure.
   * This method is final so subclasses cannot override it.
   */
  public final void process() {
    readData();
    validateData();
    processData();
    saveData();
    cleanup();
  }

  /**
   * Abstract method - subclasses must implement.
   */
  protected abstract void readData();

  /**
   * Abstract method - subclasses must implement.
   */
  protected abstract void processData();

  /**
   * Concrete method with default implementation.
   * Subclasses can override if needed.
   */
  protected void validateData() {
    System.out.println("  Validating data...");
  }

  /**
   * Concrete method with default implementation.
   */
  protected void saveData() {
    System.out.println("  Saving processed data...");
  }

  /**
   * Concrete method with default implementation.
   */
  protected void cleanup() {
    System.out.println("  Cleaning up resources...");
  }
}

/**
 * CSV data processor.
 */
class CsvDataProcessor extends DataProcessor {
  @Override
  protected void readData() {
    System.out.println("  Reading CSV file...");
  }

  @Override
  protected void processData() {
    System.out.println("  Processing CSV data...");
    System.out.println("  Parsing comma-separated values...");
  }
}

/**
 * JSON data processor.
 */
class JsonDataProcessor extends DataProcessor {
  @Override
  protected void readData() {
    System.out.println("  Reading JSON file...");
  }

  @Override
  protected void processData() {
    System.out.println("  Processing JSON data...");
    System.out.println("  Parsing JSON objects...");
  }

  @Override
  protected void validateData() {
    System.out.println("  Validating JSON schema...");
  }
}

/**
 * XML data processor.
 */
class XmlDataProcessor extends DataProcessor {
  @Override
  protected void readData() {
    System.out.println("  Reading XML file...");
  }

  @Override
  protected void processData() {
    System.out.println("  Processing XML data...");
    System.out.println("  Parsing XML elements...");
  }

  @Override
  protected void validateData() {
    System.out.println("  Validating XML against XSD...");
  }
}

// ========== Abstract Class vs Interface ==========

/**
 * Abstract Vehicle class.
 */
abstract class Vehicle {
  protected String brand;

  public Vehicle() {
    this.brand = "Generic";
  }

  public abstract void start();
  public abstract void stop();

  public void displayBrand() {
    System.out.println("Brand: " + brand);
  }
}

/**
 * Concrete Car class.
 */
class Car extends Vehicle {
  public Car() {
    this.brand = "Toyota";
  }

  @Override
  public void start() {
    System.out.println("Car engine starting...");
  }

  @Override
  public void stop() {
    System.out.println("Car engine stopping...");
  }
}

/**
 * Flyable interface.
 */
interface Flyable {
  void fly();
  void land();

  // Default method (Java 8+)
  default void checkWeather() {
    System.out.println("Checking weather conditions...");
  }
}

/**
 * Airplane implements Flyable.
 */
class Airplane implements Flyable {
  @Override
  public void fly() {
    System.out.println("Airplane taking off and flying...");
  }

  @Override
  public void land() {
    System.out.println("Airplane landing...");
  }
}

// ========== Real-World Example ==========

/**
 * Abstract BankAccount class.
 */
abstract class BankAccount {
  protected String accountNumber;
  protected String accountHolder;
  protected double balance;

  /**
   * Constructor.
   */
  public BankAccount(String accountNumber, String accountHolder, double initialBalance) {
    this.accountNumber = accountNumber;
    this.accountHolder = accountHolder;
    this.balance = initialBalance;
  }

  /**
   * Concrete method to deposit money.
   */
  public void deposit(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Deposit amount must be positive");
      return;
    }

    balance += amount;
    System.out.printf("Deposited: $%.2f, New balance: $%.2f%n", amount, balance);
  }

  /**
   * Abstract method - each account type has different withdrawal rules.
   */
  public abstract boolean withdraw(double amount);

  /**
   * Abstract method - each account type has different fee structure.
   */
  public abstract void applyMonthlyFees();

  /**
   * Abstract method - each account type calculates interest differently.
   */
  public abstract double calculateInterest();

  /**
   * Concrete method to display account info.
   */
  public void displayInfo() {
    System.out.printf("Account: %s, Holder: %s, Balance: $%.2f%n",
        accountNumber, accountHolder, balance);
  }

  public double getBalance() {
    return balance;
  }
}

/**
 * SavingsAccount - concrete implementation.
 */
class SavingsAccount extends BankAccount {
  private double interestRate;
  private static final double MONTHLY_FEE = 5.00;
  private static final double MINIMUM_BALANCE = 100.00;

  public SavingsAccount(String accountNumber, String accountHolder,
                        double initialBalance, double interestRate) {
    super(accountNumber, accountHolder, initialBalance);
    this.interestRate = interestRate;
  }

  @Override
  public boolean withdraw(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Withdrawal amount must be positive");
      return false;
    }

    double newBalance = balance - amount;

    if (newBalance < MINIMUM_BALANCE) {
      System.out.printf("Error: Withdrawal denied. Minimum balance ($%.2f) required%n",
          MINIMUM_BALANCE);
      return false;
    }

    balance = newBalance;
    System.out.printf("Withdrawn: $%.2f, New balance: $%.2f%n", amount, balance);
    return true;
  }

  @Override
  public void applyMonthlyFees() {
    if (balance < MINIMUM_BALANCE) {
      balance -= MONTHLY_FEE;
      System.out.printf("Monthly fee applied: $%.2f, New balance: $%.2f%n",
          MONTHLY_FEE, balance);
    } else {
      System.out.println("No monthly fee (minimum balance maintained)");
    }
  }

  @Override
  public double calculateInterest() {
    return balance * (interestRate / 100) / 12;
  }
}

/**
 * CheckingAccount - concrete implementation.
 */
class CheckingAccount extends BankAccount {
  private double overdraftLimit;
  private static final double TRANSACTION_FEE = 0.50;

  public CheckingAccount(String accountNumber, String accountHolder,
                         double initialBalance, double overdraftLimit) {
    super(accountNumber, accountHolder, initialBalance);
    this.overdraftLimit = overdraftLimit;
  }

  @Override
  public boolean withdraw(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Withdrawal amount must be positive");
      return false;
    }

    double newBalance = balance - amount - TRANSACTION_FEE;

    if (newBalance < -overdraftLimit) {
      System.out.printf("Error: Overdraft limit ($%.2f) exceeded%n", overdraftLimit);
      return false;
    }

    balance = newBalance;
    System.out.printf("Withdrawn: $%.2f (+ $%.2f fee), New balance: $%.2f%n",
        amount, TRANSACTION_FEE, balance);

    if (balance < 0) {
      System.out.printf("Warning: Using overdraft. Available: $%.2f%n",
          overdraftLimit + balance);
    }

    return true;
  }

  @Override
  public void applyMonthlyFees() {
    double fee = 10.00;
    balance -= fee;
    System.out.printf("Monthly maintenance fee: $%.2f, New balance: $%.2f%n",
        fee, balance);
  }

  @Override
  public double calculateInterest() {
    // Checking accounts typically don't earn interest
    return 0.0;
  }
}
