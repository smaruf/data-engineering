package com.microsoft.java.oop;

/**
 * Inheritance - Comprehensive demonstration of inheritance in Java.
 *
 * <p>This class covers:
 * - Parent-child class relationships
 * - The 'extends' keyword
 * - Method overriding
 * - The 'super' keyword
 * - Inheritance hierarchy
 * - Access modifiers in inheritance
 * - Constructor chaining
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class Inheritance {

  /**
   * Main method demonstrating inheritance concepts.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Inheritance Demonstration ===\n");

    demonstrateBasicInheritance();
    demonstrateMethodOverriding();
    demonstrateSuperKeyword();
    demonstrateInheritanceHierarchy();
    demonstrateAccessModifiers();
    realWorldExample();
  }

  /**
   * Demonstrates basic inheritance relationship.
   */
  private static void demonstrateBasicInheritance() {
    System.out.println("--- Basic Inheritance ---");

    // Parent class object
    Animal animal = new Animal("Generic Animal", 5);
    animal.displayInfo();
    animal.eat();
    animal.sleep();

    System.out.println();

    // Child class object inherits parent's members
    Dog dog = new Dog("Buddy", 3, "Golden Retriever");
    dog.displayInfo(); // Inherited method
    dog.eat();         // Inherited method
    dog.sleep();       // Inherited method
    dog.bark();        // Dog-specific method

    System.out.println();

    Cat cat = new Cat("Whiskers", 2, "Siamese");
    cat.displayInfo();
    cat.eat();
    cat.meow();        // Cat-specific method

    System.out.println();
  }

  /**
   * Demonstrates method overriding.
   */
  private static void demonstrateMethodOverriding() {
    System.out.println("--- Method Overriding ---");

    Animal animal = new Animal("Generic", 1);
    Dog dog = new Dog("Max", 4, "Labrador");
    Cat cat = new Cat("Luna", 3, "Persian");

    // Each class has its own implementation of makeSound()
    System.out.println("Animal sounds:");
    animal.makeSound(); // Parent implementation
    dog.makeSound();    // Overridden in Dog
    cat.makeSound();    // Overridden in Cat

    System.out.println();

    // Polymorphism: parent reference, child object
    System.out.println("Polymorphic behavior:");
    Animal polymorphicDog = new Dog("Rocky", 5, "Bulldog");
    Animal polymorphicCat = new Cat("Mittens", 2, "Tabby");

    polymorphicDog.makeSound(); // Calls Dog's version
    polymorphicCat.makeSound(); // Calls Cat's version

    System.out.println();
  }

  /**
   * Demonstrates the super keyword.
   */
  private static void demonstrateSuperKeyword() {
    System.out.println("--- Super Keyword ---");

    // super used to call parent constructor
    Bird bird = new Bird("Tweety", 1, 0.2);
    bird.displayInfo();

    // super used to call parent method
    System.out.println("\nBird flying:");
    bird.move(); // Calls overridden method which uses super

    System.out.println();
  }

  /**
   * Demonstrates multi-level inheritance hierarchy.
   */
  private static void demonstrateInheritanceHierarchy() {
    System.out.println("--- Inheritance Hierarchy ---");

    // Three-level hierarchy: Vehicle -> Car -> ElectricCar
    Vehicle vehicle = new Vehicle("Generic Vehicle", 2020);
    vehicle.displayInfo();
    vehicle.start();

    System.out.println();

    Car car = new Car("Sedan", 2022, 4);
    car.displayInfo();
    car.start(); // Overridden
    car.drive();

    System.out.println();

    ElectricCar tesla = new ElectricCar("Tesla Model 3", 2024, 4, 75);
    tesla.displayInfo();
    tesla.start();
    tesla.drive();
    tesla.charge();

    System.out.println();
  }

  /**
   * Demonstrates access modifiers in inheritance.
   */
  private static void demonstrateAccessModifiers() {
    System.out.println("--- Access Modifiers in Inheritance ---");

    Parent parent = new Parent();
    parent.publicMethod();
    // parent.privateMethod();  // Error: not accessible
    // parent.protectedMethod(); // Error: not accessible outside package

    System.out.println();

    Child child = new Child();
    child.publicMethod();     // Inherited
    child.demonstrateAccess(); // Shows what child can access

    System.out.println();
  }

  /**
   * Demonstrates real-world inheritance example.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Employee Management ---");

    Employee emp = new Employee("E001", "John Doe", 50000);
    emp.displayInfo();
    System.out.println("Annual salary: $" + emp.calculateAnnualSalary());

    System.out.println();

    Manager mgr = new Manager("M001", "Jane Smith", 80000, 10000);
    mgr.displayInfo();
    System.out.println("Annual salary: $" + mgr.calculateAnnualSalary());
    mgr.conductMeeting();

    System.out.println();

    Developer dev = new Developer("D001", "Bob Johnson", 70000, "Java");
    dev.displayInfo();
    System.out.println("Annual salary: $" + dev.calculateAnnualSalary());
    dev.writeCode();

    System.out.println();
  }
}

// ========== Basic Inheritance Example ==========

/**
 * Parent class representing a generic animal.
 */
class Animal {
  // Protected: accessible in subclasses
  protected String name;
  protected int age;

  /**
   * Constructor.
   *
   * @param name the animal's name
   * @param age the animal's age
   */
  public Animal(String name, int age) {
    this.name = name;
    this.age = age;
  }

  /**
   * Displays animal information.
   */
  public void displayInfo() {
    System.out.println("Name: " + name + ", Age: " + age);
  }

  /**
   * Animal eating behavior.
   */
  public void eat() {
    System.out.println(name + " is eating.");
  }

  /**
   * Animal sleeping behavior.
   */
  public void sleep() {
    System.out.println(name + " is sleeping.");
  }

  /**
   * Generic sound (to be overridden).
   */
  public void makeSound() {
    System.out.println(name + " makes a generic sound.");
  }
}

/**
 * Dog class extends Animal.
 */
class Dog extends Animal {
  private String breed;

  /**
   * Constructor.
   *
   * @param name the dog's name
   * @param age the dog's age
   * @param breed the dog's breed
   */
  public Dog(String name, int age, String breed) {
    super(name, age); // Call parent constructor
    this.breed = breed;
  }

  /**
   * Dog-specific method.
   */
  public void bark() {
    System.out.println(name + " barks: Woof! Woof!");
  }

  /**
   * Overrides parent's makeSound method.
   */
  @Override
  public void makeSound() {
    System.out.println(name + " the dog barks: Woof!");
  }

  /**
   * Overrides displayInfo to include breed.
   */
  @Override
  public void displayInfo() {
    super.displayInfo(); // Call parent's method
    System.out.println("Breed: " + breed);
  }
}

/**
 * Cat class extends Animal.
 */
class Cat extends Animal {
  private String color;

  /**
   * Constructor.
   *
   * @param name the cat's name
   * @param age the cat's age
   * @param color the cat's color
   */
  public Cat(String name, int age, String color) {
    super(name, age);
    this.color = color;
  }

  /**
   * Cat-specific method.
   */
  public void meow() {
    System.out.println(name + " meows: Meow! Meow!");
  }

  /**
   * Overrides parent's makeSound method.
   */
  @Override
  public void makeSound() {
    System.out.println(name + " the cat meows: Meow!");
  }

  /**
   * Overrides displayInfo to include color.
   */
  @Override
  public void displayInfo() {
    super.displayInfo();
    System.out.println("Color: " + color);
  }
}

// ========== Super Keyword Example ==========

/**
 * Bird class demonstrating super keyword usage.
 */
class Bird extends Animal {
  private double wingspan;

  /**
   * Constructor using super to call parent constructor.
   *
   * @param name the bird's name
   * @param age the bird's age
   * @param wingspan the bird's wingspan in meters
   */
  public Bird(String name, int age, double wingspan) {
    super(name, age); // Must be first statement in constructor
    this.wingspan = wingspan;
    System.out.println("Bird constructor called");
  }

  /**
   * Overrides makeSound using super to call parent method.
   */
  @Override
  public void makeSound() {
    super.makeSound(); // Call parent's version first
    System.out.println(name + " also chirps: Chirp! Chirp!");
  }

  /**
   * Bird-specific method.
   */
  public void move() {
    System.out.println(name + " is flying with wingspan " + wingspan + "m");
  }

  /**
   * Overrides displayInfo using super.
   */
  @Override
  public void displayInfo() {
    super.displayInfo();
    System.out.println("Wingspan: " + wingspan + "m");
  }
}

// ========== Multi-Level Inheritance ==========

/**
 * Base class: Vehicle.
 */
class Vehicle {
  protected String type;
  protected int year;

  /**
   * Constructor.
   *
   * @param type the vehicle type
   * @param year the manufacturing year
   */
  public Vehicle(String type, int year) {
    this.type = type;
    this.year = year;
  }

  /**
   * Displays vehicle information.
   */
  public void displayInfo() {
    System.out.println("Vehicle Type: " + type + ", Year: " + year);
  }

  /**
   * Starts the vehicle.
   */
  public void start() {
    System.out.println("Vehicle is starting...");
  }
}

/**
 * Middle class: Car extends Vehicle.
 */
class Car extends Vehicle {
  protected int doors;

  /**
   * Constructor.
   *
   * @param type the car type
   * @param year the manufacturing year
   * @param doors the number of doors
   */
  public Car(String type, int year, int doors) {
    super(type, year);
    this.doors = doors;
  }

  /**
   * Overrides displayInfo.
   */
  @Override
  public void displayInfo() {
    super.displayInfo();
    System.out.println("Doors: " + doors);
  }

  /**
   * Overrides start method.
   */
  @Override
  public void start() {
    System.out.println("Car engine is starting...");
  }

  /**
   * Car-specific method.
   */
  public void drive() {
    System.out.println("Car is driving on the road.");
  }
}

/**
 * Derived class: ElectricCar extends Car.
 */
class ElectricCar extends Car {
  private int batteryCapacity;

  /**
   * Constructor.
   *
   * @param type the car type
   * @param year the manufacturing year
   * @param doors the number of doors
   * @param batteryCapacity the battery capacity in kWh
   */
  public ElectricCar(String type, int year, int doors, int batteryCapacity) {
    super(type, year, doors);
    this.batteryCapacity = batteryCapacity;
  }

  /**
   * Overrides displayInfo.
   */
  @Override
  public void displayInfo() {
    super.displayInfo();
    System.out.println("Battery Capacity: " + batteryCapacity + " kWh");
  }

  /**
   * Overrides start method.
   */
  @Override
  public void start() {
    System.out.println("Electric car is powering on silently...");
  }

  /**
   * ElectricCar-specific method.
   */
  public void charge() {
    System.out.println("Electric car is charging (capacity: " + batteryCapacity + " kWh)");
  }
}

// ========== Access Modifiers Example ==========

/**
 * Parent class demonstrating access modifiers.
 */
class Parent {
  public String publicField = "Public";
  protected String protectedField = "Protected";
  private String privateField = "Private";
  String defaultField = "Default"; // Package-private

  public void publicMethod() {
    System.out.println("Parent: Public method called");
  }

  protected void protectedMethod() {
    System.out.println("Parent: Protected method called");
  }

  private void privateMethod() {
    System.out.println("Parent: Private method called");
  }

  void defaultMethod() {
    System.out.println("Parent: Default method called");
  }
}

/**
 * Child class showing inherited access.
 */
class Child extends Parent {
  /**
   * Demonstrates what the child can access from parent.
   */
  public void demonstrateAccess() {
    System.out.println("Child accessing parent members:");
    System.out.println("  Public field: " + publicField);       // OK
    System.out.println("  Protected field: " + protectedField); // OK
    // System.out.println("  Private field: " + privateField);  // Error!
    System.out.println("  Default field: " + defaultField);     // OK (same package)

    publicMethod();    // OK
    protectedMethod(); // OK
    // privateMethod(); // Error!
    defaultMethod();   // OK (same package)
  }
}

// ========== Real-World Example ==========

/**
 * Base Employee class.
 */
class Employee {
  protected String employeeId;
  protected String name;
  protected double baseSalary;

  /**
   * Constructor.
   *
   * @param employeeId the employee ID
   * @param name the employee name
   * @param baseSalary the base salary
   */
  public Employee(String employeeId, String name, double baseSalary) {
    this.employeeId = employeeId;
    this.name = name;
    this.baseSalary = baseSalary;
  }

  /**
   * Displays employee information.
   */
  public void displayInfo() {
    System.out.printf("ID: %s, Name: %s, Base Salary: $%.2f%n",
        employeeId, name, baseSalary);
  }

  /**
   * Calculates annual salary.
   *
   * @return the annual salary
   */
  public double calculateAnnualSalary() {
    return baseSalary * 12;
  }

  /**
   * Gives a raise.
   *
   * @param percentage the raise percentage
   */
  public void giveRaise(double percentage) {
    baseSalary += baseSalary * (percentage / 100);
    System.out.printf("Raise applied: %.1f%%, New salary: $%.2f%n",
        percentage, baseSalary);
  }
}

/**
 * Manager class extends Employee.
 */
class Manager extends Employee {
  private double bonus;

  /**
   * Constructor.
   *
   * @param employeeId the employee ID
   * @param name the employee name
   * @param baseSalary the base salary
   * @param bonus the annual bonus
   */
  public Manager(String employeeId, String name, double baseSalary, double bonus) {
    super(employeeId, name, baseSalary);
    this.bonus = bonus;
  }

  /**
   * Overrides displayInfo to include bonus.
   */
  @Override
  public void displayInfo() {
    super.displayInfo();
    System.out.printf("Bonus: $%.2f, Role: Manager%n", bonus);
  }

  /**
   * Overrides calculateAnnualSalary to include bonus.
   */
  @Override
  public double calculateAnnualSalary() {
    return super.calculateAnnualSalary() + bonus;
  }

  /**
   * Manager-specific method.
   */
  public void conductMeeting() {
    System.out.println(name + " is conducting a team meeting.");
  }
}

/**
 * Developer class extends Employee.
 */
class Developer extends Employee {
  private String programmingLanguage;

  /**
   * Constructor.
   *
   * @param employeeId the employee ID
   * @param name the employee name
   * @param baseSalary the base salary
   * @param programmingLanguage the primary programming language
   */
  public Developer(String employeeId, String name, double baseSalary,
                   String programmingLanguage) {
    super(employeeId, name, baseSalary);
    this.programmingLanguage = programmingLanguage;
  }

  /**
   * Overrides displayInfo to include programming language.
   */
  @Override
  public void displayInfo() {
    super.displayInfo();
    System.out.printf("Language: %s, Role: Developer%n", programmingLanguage);
  }

  /**
   * Developer-specific method.
   */
  public void writeCode() {
    System.out.println(name + " is writing " + programmingLanguage + " code.");
  }
}
