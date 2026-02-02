package com.microsoft.java.oop;

/**
 * Classes - Comprehensive demonstration of class fundamentals in Java.
 *
 * <p>This class covers:
 * - Class definition and structure
 * - Constructors (default, parameterized, overloaded)
 * - Instance variables and methods
 * - Static variables and methods
 * - The 'this' keyword
 * - Object creation and usage
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class Classes {

  /**
   * Main method demonstrating class concepts.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Classes Demonstration ===\n");

    demonstrateBasicClass();
    demonstrateConstructors();
    demonstrateInstanceVsStatic();
    demonstrateThisKeyword();
    demonstrateObjectComparison();
    realWorldExample();
  }

  /**
   * Demonstrates basic class creation and usage.
   */
  private static void demonstrateBasicClass() {
    System.out.println("--- Basic Class Usage ---");

    // Creating objects (instances) of a class
    Person person1 = new Person();
    person1.name = "Alice";
    person1.age = 30;

    Person person2 = new Person();
    person2.name = "Bob";
    person2.age = 25;

    System.out.println("Person 1: " + person1.getInfo());
    System.out.println("Person 2: " + person2.getInfo());

    // Calling instance methods
    person1.celebrateBirthday();
    System.out.println("After birthday: " + person1.getInfo());

    System.out.println();
  }

  /**
   * Demonstrates different types of constructors.
   */
  private static void demonstrateConstructors() {
    System.out.println("--- Constructors ---");

    // Using default constructor
    Car car1 = new Car();
    System.out.println("Car 1 (default): " + car1.getDetails());

    // Using parameterized constructor
    Car car2 = new Car("Toyota", "Camry", 2024);
    System.out.println("Car 2 (parameterized): " + car2.getDetails());

    // Using overloaded constructor
    Car car3 = new Car("Honda", "Accord");
    System.out.println("Car 3 (overloaded): " + car3.getDetails());

    System.out.println();
  }

  /**
   * Demonstrates instance vs static members.
   */
  private static void demonstrateInstanceVsStatic() {
    System.out.println("--- Instance vs Static Members ---");

    // Static members belong to the class
    System.out.println("Total students: " + Student.getTotalStudents());

    // Creating instances
    Student s1 = new Student("Alice", 101);
    Student s2 = new Student("Bob", 102);
    Student s3 = new Student("Charlie", 103);

    System.out.println("After creating 3 students: " + Student.getTotalStudents());

    // Instance members belong to individual objects
    System.out.println("\nStudent 1: " + s1.getInfo());
    System.out.println("Student 2: " + s2.getInfo());

    // Static method can be called on class or instance
    System.out.println("\nSchool name: " + Student.getSchoolName());
    System.out.println("School name via instance: " + s1.getSchoolName());

    // Static variable shared across all instances
    Student.schoolName = "New School Name";
    System.out.println("Changed school name: " + s2.getSchoolName());

    System.out.println();
  }

  /**
   * Demonstrates the 'this' keyword.
   */
  private static void demonstrateThisKeyword() {
    System.out.println("--- The 'this' Keyword ---");

    // 'this' used to resolve naming conflicts
    Rectangle rect1 = new Rectangle(10, 5);
    System.out.println("Rectangle 1: " + rect1.getInfo());

    // 'this' used for constructor chaining
    Rectangle rect2 = new Rectangle(8);
    System.out.println("Rectangle 2 (square): " + rect2.getInfo());

    // 'this' used to return current object
    Rectangle rect3 = new Rectangle(6, 4)
        .setWidth(12)
        .setHeight(8);
    System.out.println("Rectangle 3 (method chaining): " + rect3.getInfo());

    System.out.println();
  }

  /**
   * Demonstrates object comparison.
   */
  private static void demonstrateObjectComparison() {
    System.out.println("--- Object Comparison ---");

    Point p1 = new Point(5, 10);
    Point p2 = new Point(5, 10);
    Point p3 = p1;

    System.out.println("p1: " + p1.getInfo());
    System.out.println("p2: " + p2.getInfo());
    System.out.println("p3: " + p3.getInfo());

    // Reference comparison (==)
    System.out.println("\nReference comparison (==):");
    System.out.println("  p1 == p2: " + (p1 == p2)); // false (different objects)
    System.out.println("  p1 == p3: " + (p1 == p3)); // true (same reference)

    // Value comparison (equals)
    System.out.println("\nValue comparison (equals):");
    System.out.println("  p1.equals(p2): " + p1.equals(p2)); // true (same values)
    System.out.println("  p1.equals(p3): " + p1.equals(p3)); // true (same object)

    System.out.println();
  }

  /**
   * Demonstrates real-world class usage.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Bank Account ---");

    BankAccount account = new BankAccount("123456789", "John Doe", 1000.00);
    System.out.println(account.getAccountInfo());

    account.deposit(500.00);
    account.withdraw(200.00);
    account.withdraw(2000.00); // Should fail

    System.out.println("\nFinal balance: $" + account.getBalance());
    System.out.println("Transaction count: " + account.getTransactionCount());

    System.out.println();
  }
}

/**
 * Simple Person class demonstrating basic class structure.
 */
class Person {
  // Instance variables (fields)
  String name;
  int age;

  /**
   * Instance method that returns person information.
   *
   * @return formatted person information
   */
  String getInfo() {
    return name + " (age: " + age + ")";
  }

  /**
   * Instance method that modifies state.
   */
  void celebrateBirthday() {
    age++;
    System.out.println("Happy birthday, " + name + "!");
  }
}

/**
 * Car class demonstrating constructors.
 */
class Car {
  // Instance variables
  private String make;
  private String model;
  private int year;

  /**
   * Default constructor.
   */
  public Car() {
    this.make = "Unknown";
    this.model = "Unknown";
    this.year = 2024;
  }

  /**
   * Parameterized constructor.
   *
   * @param make the car manufacturer
   * @param model the car model
   * @param year the manufacturing year
   */
  public Car(String make, String model, int year) {
    this.make = make;
    this.model = model;
    this.year = year;
  }

  /**
   * Overloaded constructor (uses current year as default).
   *
   * @param make the car manufacturer
   * @param model the car model
   */
  public Car(String make, String model) {
    this(make, model, 2024); // Constructor chaining
  }

  /**
   * Returns car details.
   *
   * @return formatted car details
   */
  public String getDetails() {
    return year + " " + make + " " + model;
  }
}

/**
 * Student class demonstrating static vs instance members.
 */
class Student {
  // Static variable (class variable) - shared by all instances
  private static int totalStudents = 0;
  static String schoolName = "Java High School";

  // Instance variables - unique to each object
  private String name;
  private int studentId;

  /**
   * Constructor increments the static counter.
   *
   * @param name the student's name
   * @param studentId the student's ID
   */
  public Student(String name, int studentId) {
    this.name = name;
    this.studentId = studentId;
    totalStudents++; // Increment static counter
  }

  /**
   * Instance method.
   *
   * @return student information
   */
  public String getInfo() {
    return "ID: " + studentId + ", Name: " + name;
  }

  /**
   * Static method - can be called without creating an instance.
   *
   * @return the total number of students
   */
  public static int getTotalStudents() {
    return totalStudents;
    // Note: Cannot access instance variables (name, studentId) here
  }

  /**
   * Static method to get school name.
   *
   * @return the school name
   */
  public static String getSchoolName() {
    return schoolName;
  }
}

/**
 * Rectangle class demonstrating the 'this' keyword.
 */
class Rectangle {
  private int width;
  private int height;

  /**
   * Constructor using 'this' to resolve naming conflicts.
   *
   * @param width the rectangle width
   * @param height the rectangle height
   */
  public Rectangle(int width, int height) {
    // 'this' refers to instance variable, parameter name is local
    this.width = width;
    this.height = height;
  }

  /**
   * Constructor for square (using 'this' for constructor chaining).
   *
   * @param side the side length of the square
   */
  public Rectangle(int side) {
    this(side, side); // Call the other constructor
  }

  /**
   * Setter using 'this' for method chaining.
   *
   * @param width the new width
   * @return this Rectangle instance
   */
  public Rectangle setWidth(int width) {
    this.width = width;
    return this; // Return current object for chaining
  }

  /**
   * Setter using 'this' for method chaining.
   *
   * @param height the new height
   * @return this Rectangle instance
   */
  public Rectangle setHeight(int height) {
    this.height = height;
    return this;
  }

  /**
   * Gets rectangle information.
   *
   * @return formatted rectangle information
   */
  public String getInfo() {
    return width + "x" + height + " (area: " + (width * height) + ")";
  }
}

/**
 * Point class demonstrating equals() override.
 */
class Point {
  private int x;
  private int y;

  /**
   * Constructor.
   *
   * @param x the x coordinate
   * @param y the y coordinate
   */
  public Point(int x, int y) {
    this.x = x;
    this.y = y;
  }

  /**
   * Gets point information.
   *
   * @return formatted point information
   */
  public String getInfo() {
    return "(" + x + ", " + y + ")";
  }

  /**
   * Overrides equals() for value-based comparison.
   *
   * @param obj the object to compare
   * @return true if points have same coordinates
   */
  @Override
  public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;

    Point point = (Point) obj;
    return x == point.x && y == point.y;
  }

  /**
   * Overrides hashCode() (should always override with equals).
   *
   * @return hash code based on coordinates
   */
  @Override
  public int hashCode() {
    return 31 * x + y;
  }
}

/**
 * BankAccount class demonstrating real-world class usage.
 */
class BankAccount {
  // Instance variables
  private final String accountNumber; // final = cannot be changed after construction
  private String accountHolder;
  private double balance;
  private int transactionCount;

  /**
   * Constructor.
   *
   * @param accountNumber the account number
   * @param accountHolder the account holder name
   * @param initialBalance the initial balance
   */
  public BankAccount(String accountNumber, String accountHolder, double initialBalance) {
    this.accountNumber = accountNumber;
    this.accountHolder = accountHolder;
    this.balance = initialBalance;
    this.transactionCount = 0;
  }

  /**
   * Deposits money into the account.
   *
   * @param amount the amount to deposit
   * @return true if successful
   */
  public boolean deposit(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Deposit amount must be positive");
      return false;
    }

    balance += amount;
    transactionCount++;
    System.out.printf("Deposited: $%.2f, New balance: $%.2f%n", amount, balance);
    return true;
  }

  /**
   * Withdraws money from the account.
   *
   * @param amount the amount to withdraw
   * @return true if successful
   */
  public boolean withdraw(double amount) {
    if (amount <= 0) {
      System.out.println("Error: Withdrawal amount must be positive");
      return false;
    }

    if (amount > balance) {
      System.out.printf("Error: Insufficient funds (balance: $%.2f, requested: $%.2f)%n",
          balance, amount);
      return false;
    }

    balance -= amount;
    transactionCount++;
    System.out.printf("Withdrawn: $%.2f, New balance: $%.2f%n", amount, balance);
    return true;
  }

  /**
   * Gets current balance.
   *
   * @return the current balance
   */
  public double getBalance() {
    return balance;
  }

  /**
   * Gets transaction count.
   *
   * @return the transaction count
   */
  public int getTransactionCount() {
    return transactionCount;
  }

  /**
   * Gets account information.
   *
   * @return formatted account information
   */
  public String getAccountInfo() {
    return String.format("Account: %s, Holder: %s, Balance: $%.2f",
        accountNumber, accountHolder, balance);
  }
}
