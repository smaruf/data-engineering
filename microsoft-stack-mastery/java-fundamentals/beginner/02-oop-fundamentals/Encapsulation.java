package com.microsoft.java.oop;

/**
 * Encapsulation - Comprehensive demonstration of encapsulation in Java.
 *
 * <p>This class covers:
 * - Data hiding with private fields
 * - Getters and setters
 * - Access modifiers (private, public, protected, default)
 * - Validation in setters
 * - Immutable classes
 * - Benefits of encapsulation
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class Encapsulation {

  /**
   * Main method demonstrating encapsulation concepts.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Encapsulation Demonstration ===\n");

    demonstrateDataHiding();
    demonstrateGettersSetters();
    demonstrateValidation();
    demonstrateAccessModifiers();
    demonstrateImmutability();
    demonstrateReadOnlyClass();
    realWorldExample();
  }

  /**
   * Demonstrates data hiding with private fields.
   */
  private static void demonstrateDataHiding() {
    System.out.println("--- Data Hiding ---");

    // Without encapsulation (bad practice)
    PersonBad badPerson = new PersonBad();
    badPerson.name = "John";
    badPerson.age = -5; // Invalid age, but no validation!
    badPerson.salary = -1000; // Invalid salary!

    System.out.println("Bad practice (no encapsulation):");
    System.out.println("  Name: " + badPerson.name);
    System.out.println("  Age: " + badPerson.age + " (Invalid!)");
    System.out.println("  Salary: $" + badPerson.salary + " (Invalid!)");

    System.out.println();

    // With encapsulation (good practice)
    PersonGood goodPerson = new PersonGood();
    goodPerson.setName("Alice");
    goodPerson.setAge(30);
    goodPerson.setSalary(75000);

    System.out.println("Good practice (with encapsulation):");
    System.out.println("  Name: " + goodPerson.getName());
    System.out.println("  Age: " + goodPerson.getAge());
    System.out.println("  Salary: $" + goodPerson.getSalary());

    // Try setting invalid values
    System.out.println("\nAttempting to set invalid age:");
    goodPerson.setAge(-5); // Will be rejected

    System.out.println();
  }

  /**
   * Demonstrates proper use of getters and setters.
   */
  private static void demonstrateGettersSetters() {
    System.out.println("--- Getters and Setters ---");

    Product product = new Product("Laptop", 999.99, 10);

    System.out.println("Product created:");
    System.out.println("  Name: " + product.getName());
    System.out.println("  Price: $" + product.getPrice());
    System.out.println("  Stock: " + product.getStock());

    // Using setters to modify
    product.setPrice(899.99);
    product.setStock(15);

    System.out.println("\nAfter updates:");
    System.out.println("  Price: $" + product.getPrice());
    System.out.println("  Stock: " + product.getStock());

    // Derived property (calculated, not stored)
    System.out.println("  Total value: $" + product.getTotalValue());

    System.out.println();
  }

  /**
   * Demonstrates validation in setters.
   */
  private static void demonstrateValidation() {
    System.out.println("--- Validation in Setters ---");

    BankAccount account = new BankAccount("123456", 1000.00);
    account.displayInfo();

    System.out.println("\nValid deposit:");
    account.deposit(500.00);

    System.out.println("\nInvalid deposit (negative):");
    account.deposit(-100.00);

    System.out.println("\nValid withdrawal:");
    account.withdraw(200.00);

    System.out.println("\nInvalid withdrawal (exceeds balance):");
    account.withdraw(2000.00);

    System.out.println();
  }

  /**
   * Demonstrates all access modifiers.
   */
  private static void demonstrateAccessModifiers() {
    System.out.println("--- Access Modifiers ---");

    System.out.println("Java has 4 access levels:");
    System.out.println("  1. private - accessible only within the class");
    System.out.println("  2. default (no modifier) - accessible within the package");
    System.out.println("  3. protected - accessible within package and subclasses");
    System.out.println("  4. public - accessible everywhere");

    AccessModifiersDemo demo = new AccessModifiersDemo();
    demo.publicMethod();
    // demo.privateMethod();   // Error: private
    // demo.protectedMethod(); // Error: protected (different package)
    // demo.defaultMethod();   // Error: default (different package)

    System.out.println();
  }

  /**
   * Demonstrates immutable class design.
   */
  private static void demonstrateImmutability() {
    System.out.println("--- Immutable Class ---");

    ImmutablePerson person = new ImmutablePerson("Bob", 25, "bob@email.com");

    System.out.println("Immutable person:");
    System.out.println("  Name: " + person.getName());
    System.out.println("  Age: " + person.getAge());
    System.out.println("  Email: " + person.getEmail());

    // Cannot modify - no setters!
    // person.setAge(26); // Error: no such method

    System.out.println("\nBenefits of immutability:");
    System.out.println("  - Thread-safe");
    System.out.println("  - Can be cached and reused");
    System.out.println("  - Simpler to understand and use");
    System.out.println("  - Can be used as HashMap keys");

    System.out.println();
  }

  /**
   * Demonstrates read-only class.
   */
  private static void demonstrateReadOnlyClass() {
    System.out.println("--- Read-Only Class ---");

    Configuration config = new Configuration("Production", "localhost", 8080);

    System.out.println("Configuration:");
    System.out.println("  Environment: " + config.getEnvironment());
    System.out.println("  Host: " + config.getHost());
    System.out.println("  Port: " + config.getPort());
    System.out.println("  Connection String: " + config.getConnectionString());

    // Fields are final and cannot be changed
    // No setters provided

    System.out.println();
  }

  /**
   * Demonstrates real-world encapsulation example.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: User Account ---");

    UserAccount user = new UserAccount("alice123", "alice@example.com");

    System.out.println("User account created:");
    user.displayInfo();

    System.out.println("\nSetting password:");
    user.setPassword("weak"); // Too short

    user.setPassword("StrongPass123!"); // Valid

    System.out.println("\nVerifying password:");
    System.out.println("  Correct password: " + user.verifyPassword("StrongPass123!"));
    System.out.println("  Wrong password: " + user.verifyPassword("wrong"));

    System.out.println("\nUpdating email:");
    user.setEmail("invalid-email"); // Invalid
    user.setEmail("alice.new@example.com"); // Valid

    System.out.println("\nUpdating profile:");
    user.setFirstName("Alice");
    user.setLastName("Johnson");
    user.setPhone("+1-555-0123");

    System.out.println("\nFinal account info:");
    user.displayInfo();

    System.out.println();
  }
}

// ========== Bad Practice Example ==========

/**
 * Bad practice - public fields without encapsulation.
 */
class PersonBad {
  public String name;
  public int age;
  public double salary;
  // No validation, no control over data!
}

// ========== Good Practice Example ==========

/**
 * Good practice - private fields with getters and setters.
 */
class PersonGood {
  private String name;
  private int age;
  private double salary;

  public String getName() {
    return name;
  }

  public void setName(String name) {
    if (name != null && !name.trim().isEmpty()) {
      this.name = name;
    } else {
      System.out.println("Error: Name cannot be empty");
    }
  }

  public int getAge() {
    return age;
  }

  public void setAge(int age) {
    if (age >= 0 && age <= 150) {
      this.age = age;
    } else {
      System.out.println("Error: Invalid age (must be 0-150)");
    }
  }

  public double getSalary() {
    return salary;
  }

  public void setSalary(double salary) {
    if (salary >= 0) {
      this.salary = salary;
    } else {
      System.out.println("Error: Salary cannot be negative");
    }
  }
}

// ========== Product Class Example ==========

/**
 * Product class with encapsulation and derived properties.
 */
class Product {
  private String name;
  private double price;
  private int stock;

  public Product(String name, double price, int stock) {
    this.name = name;
    setPrice(price);
    setStock(stock);
  }

  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public double getPrice() {
    return price;
  }

  public void setPrice(double price) {
    if (price >= 0) {
      this.price = price;
    } else {
      System.out.println("Error: Price cannot be negative");
    }
  }

  public int getStock() {
    return stock;
  }

  public void setStock(int stock) {
    if (stock >= 0) {
      this.stock = stock;
    } else {
      System.out.println("Error: Stock cannot be negative");
    }
  }

  /**
   * Derived property - calculated from other fields.
   */
  public double getTotalValue() {
    return price * stock;
  }
}

// ========== BankAccount with Validation ==========

/**
 * BankAccount demonstrating validation in setters.
 */
class BankAccount {
  private final String accountNumber; // Immutable
  private double balance;

  public BankAccount(String accountNumber, double initialBalance) {
    this.accountNumber = accountNumber;
    this.balance = initialBalance;
  }

  public String getAccountNumber() {
    return accountNumber;
  }

  public double getBalance() {
    return balance;
  }

  public void deposit(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Deposit amount must be positive");
      return;
    }

    balance += amount;
    System.out.printf("Deposited: $%.2f, New balance: $%.2f%n", amount, balance);
  }

  public void withdraw(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Withdrawal amount must be positive");
      return;
    }

    if (amount > balance) {
      System.out.printf("Error: Insufficient funds (balance: $%.2f)%n", balance);
      return;
    }

    balance -= amount;
    System.out.printf("Withdrawn: $%.2f, New balance: $%.2f%n", amount, balance);
  }

  public void displayInfo() {
    System.out.printf("Account: %s, Balance: $%.2f%n", accountNumber, balance);
  }
}

// ========== Access Modifiers Example ==========

/**
 * Class demonstrating all access modifiers.
 */
class AccessModifiersDemo {
  private String privateField = "Private";
  String defaultField = "Default";
  protected String protectedField = "Protected";
  public String publicField = "Public";

  public void publicMethod() {
    System.out.println("Public method - accessible everywhere");
  }

  protected void protectedMethod() {
    System.out.println("Protected method - package and subclasses");
  }

  void defaultMethod() {
    System.out.println("Default method - package only");
  }

  private void privateMethod() {
    System.out.println("Private method - class only");
  }
}

// ========== Immutable Class Example ==========

/**
 * Immutable class - all fields are final, no setters.
 */
final class ImmutablePerson {
  private final String name;
  private final int age;
  private final String email;

  public ImmutablePerson(String name, int age, String email) {
    this.name = name;
    this.age = age;
    this.email = email;
  }

  public String getName() {
    return name;
  }

  public int getAge() {
    return age;
  }

  public String getEmail() {
    return email;
  }

  // No setters - object is immutable
}

// ========== Read-Only Class Example ==========

/**
 * Configuration class - read-only after construction.
 */
class Configuration {
  private final String environment;
  private final String host;
  private final int port;

  public Configuration(String environment, String host, int port) {
    this.environment = environment;
    this.host = host;
    this.port = port;
  }

  public String getEnvironment() {
    return environment;
  }

  public String getHost() {
    return host;
  }

  public int getPort() {
    return port;
  }

  public String getConnectionString() {
    return host + ":" + port;
  }
}

// ========== Real-World Example ==========

/**
 * UserAccount demonstrating comprehensive encapsulation.
 */
class UserAccount {
  private final String username; // Immutable
  private String email;
  private String passwordHash; // Never store plain password!
  private String firstName;
  private String lastName;
  private String phone;
  private boolean isActive;
  private long lastLoginTime;

  public UserAccount(String username, String email) {
    this.username = username;
    setEmail(email);
    this.isActive = true;
    this.lastLoginTime = System.currentTimeMillis();
  }

  // Username is immutable - only getter
  public String getUsername() {
    return username;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(String email) {
    if (isValidEmail(email)) {
      this.email = email;
      System.out.println("Email updated successfully");
    } else {
      System.out.println("Error: Invalid email format");
    }
  }

  // Password is never exposed, only verified
  public void setPassword(String password) {
    if (isValidPassword(password)) {
      this.passwordHash = hashPassword(password);
      System.out.println("Password set successfully");
    } else {
      System.out.println("Error: Password must be at least 8 characters");
    }
  }

  public boolean verifyPassword(String password) {
    return hashPassword(password).equals(passwordHash);
  }

  public String getFirstName() {
    return firstName;
  }

  public void setFirstName(String firstName) {
    this.firstName = firstName;
  }

  public String getLastName() {
    return lastName;
  }

  public void setLastName(String lastName) {
    this.lastName = lastName;
  }

  public String getFullName() {
    if (firstName != null && lastName != null) {
      return firstName + " " + lastName;
    }
    return username;
  }

  public String getPhone() {
    return phone;
  }

  public void setPhone(String phone) {
    this.phone = phone;
  }

  public boolean isActive() {
    return isActive;
  }

  public void deactivate() {
    this.isActive = false;
    System.out.println("Account deactivated");
  }

  public void activate() {
    this.isActive = true;
    System.out.println("Account activated");
  }

  public void recordLogin() {
    this.lastLoginTime = System.currentTimeMillis();
  }

  public void displayInfo() {
    System.out.println("Username: " + username);
    System.out.println("Email: " + email);
    System.out.println("Full Name: " + getFullName());
    System.out.println("Phone: " + (phone != null ? phone : "Not set"));
    System.out.println("Status: " + (isActive ? "Active" : "Inactive"));
  }

  // Private helper methods
  private boolean isValidEmail(String email) {
    return email != null && email.contains("@") && email.contains(".");
  }

  private boolean isValidPassword(String password) {
    return password != null && password.length() >= 8;
  }

  private String hashPassword(String password) {
    // Simplified - in real app, use proper hashing (BCrypt, etc.)
    return "HASH:" + password;
  }
}
