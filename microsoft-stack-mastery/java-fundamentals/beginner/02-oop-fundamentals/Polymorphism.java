package com.microsoft.java.oop;

/**
 * Polymorphism - Comprehensive demonstration of polymorphism in Java.
 *
 * <p>This class covers:
 * - Compile-time polymorphism (method overloading)
 * - Runtime polymorphism (method overriding)
 * - Interfaces and polymorphism
 * - Abstract classes and polymorphism
 * - Dynamic method dispatch
 * - Type casting with polymorphism
 *
 * @author Microsoft Stack Mastery
 * @version 1.0
 * @since 2024
 */
public class Polymorphism {

  /**
   * Main method demonstrating polymorphism concepts.
   *
   * @param args command-line arguments (not used)
   */
  public static void main(String[] args) {
    System.out.println("=== Java Polymorphism Demonstration ===\n");

    demonstrateMethodOverloading();
    demonstrateMethodOverriding();
    demonstrateRuntimePolymorphism();
    demonstrateInterfacePolymorphism();
    demonstrateTypeCasting();
    demonstrateInstanceOf();
    realWorldExample();
  }

  /**
   * Demonstrates compile-time polymorphism (method overloading).
   */
  private static void demonstrateMethodOverloading() {
    System.out.println("--- Method Overloading (Compile-Time Polymorphism) ---");

    Calculator calc = new Calculator();

    // Same method name, different parameters
    System.out.println("add(5, 3): " + calc.add(5, 3));
    System.out.println("add(5, 3, 2): " + calc.add(5, 3, 2));
    System.out.println("add(5.5, 3.3): " + calc.add(5.5, 3.3));
    System.out.println("add(\"Hello\", \"World\"): " + calc.add("Hello", "World"));

    Printer printer = new Printer();
    printer.print("Text");
    printer.print(42);
    printer.print(3.14);
    printer.print("Message", 3);

    System.out.println();
  }

  /**
   * Demonstrates runtime polymorphism (method overriding).
   */
  private static void demonstrateMethodOverriding() {
    System.out.println("--- Method Overriding (Runtime Polymorphism) ---");

    // Each class has its own implementation
    Shape shape1 = new Shape();
    shape1.draw();
    System.out.println("Area: " + shape1.calculateArea());

    Shape shape2 = new Circle(5.0);
    shape2.draw(); // Calls Circle's version
    System.out.println("Area: " + shape2.calculateArea());

    Shape shape3 = new Rectangle(4.0, 6.0);
    shape3.draw(); // Calls Rectangle's version
    System.out.println("Area: " + shape3.calculateArea());

    System.out.println();
  }

  /**
   * Demonstrates runtime polymorphism with arrays.
   */
  private static void demonstrateRuntimePolymorphism() {
    System.out.println("--- Runtime Polymorphism with Arrays ---");

    // Parent reference, child objects
    Shape[] shapes = {
        new Circle(3.0),
        new Rectangle(5.0, 4.0),
        new Triangle(6.0, 3.0),
        new Circle(2.5)
    };

    System.out.println("Processing different shapes:");
    for (int i = 0; i < shapes.length; i++) {
      System.out.print((i + 1) + ". ");
      shapes[i].draw();
      System.out.printf("   Area: %.2f%n", shapes[i].calculateArea());
    }

    System.out.println();
  }

  /**
   * Demonstrates polymorphism with interfaces.
   */
  private static void demonstrateInterfacePolymorphism() {
    System.out.println("--- Interface Polymorphism ---");

    // Interface reference, different implementations
    Playable[] playables = {
        new MusicPlayer(),
        new VideoPlayer(),
        new GameConsole()
    };

    System.out.println("Playing different media:");
    for (Playable playable : playables) {
      playable.play();
      playable.pause();
      playable.stop();
      System.out.println();
    }

    // Multiple interfaces
    SmartDevice phone = new SmartPhone();
    phone.turnOn();
    phone.connectToWifi("MyNetwork");
    ((Chargeable) phone).charge(); // Type casting to access Chargeable interface

    System.out.println();
  }

  /**
   * Demonstrates type casting with polymorphism.
   */
  private static void demonstrateTypeCasting() {
    System.out.println("--- Type Casting ---");

    // Upcasting (implicit)
    Shape shape = new Circle(4.0);
    shape.draw();

    // Downcasting (explicit) - to access child-specific methods
    if (shape instanceof Circle) {
      Circle circle = (Circle) shape;
      System.out.println("Radius: " + circle.getRadius());
      System.out.println("Circumference: " + circle.calculateCircumference());
    }

    // Unsafe downcasting example
    Shape rectangle = new Rectangle(5.0, 3.0);
    // Circle wrongCast = (Circle) rectangle; // Would throw ClassCastException at runtime

    System.out.println();
  }

  /**
   * Demonstrates instanceof operator.
   */
  private static void demonstrateInstanceOf() {
    System.out.println("--- instanceof Operator ---");

    Shape[] shapes = {
        new Circle(3.0),
        new Rectangle(4.0, 5.0),
        new Triangle(3.0, 4.0)
    };

    for (Shape shape : shapes) {
      System.out.print("Shape type: ");

      if (shape instanceof Circle) {
        System.out.println("Circle");
        Circle c = (Circle) shape;
        System.out.println("  Radius: " + c.getRadius());
      } else if (shape instanceof Rectangle) {
        System.out.println("Rectangle");
        Rectangle r = (Rectangle) shape;
        System.out.println("  Width: " + r.getWidth() + ", Height: " + r.getHeight());
      } else if (shape instanceof Triangle) {
        System.out.println("Triangle");
        Triangle t = (Triangle) shape;
        System.out.println("  Base: " + t.getBase() + ", Height: " + t.getHeight());
      }
      System.out.println();
    }
  }

  /**
   * Demonstrates real-world polymorphism example.
   */
  private static void realWorldExample() {
    System.out.println("--- Real-World Example: Payment Processing ---");

    PaymentProcessor processor = new PaymentProcessor();

    Payment[] payments = {
        new CreditCardPayment("1234-5678-9012-3456", "John Doe"),
        new PayPalPayment("john@email.com"),
        new CryptoPayment("1A2B3C4D5E6F"),
        new CreditCardPayment("9876-5432-1098-7654", "Jane Smith")
    };

    for (Payment payment : payments) {
      processor.processPayment(payment, 100.00);
      System.out.println();
    }
  }
}

// ========== Method Overloading Example ==========

/**
 * Calculator demonstrating method overloading.
 */
class Calculator {
  /**
   * Adds two integers.
   */
  public int add(int a, int b) {
    return a + b;
  }

  /**
   * Adds three integers (overloaded).
   */
  public int add(int a, int b, int c) {
    return a + b + c;
  }

  /**
   * Adds two doubles (overloaded).
   */
  public double add(double a, double b) {
    return a + b;
  }

  /**
   * Concatenates two strings (overloaded).
   */
  public String add(String a, String b) {
    return a + " " + b;
  }
}

/**
 * Printer demonstrating method overloading.
 */
class Printer {
  public void print(String text) {
    System.out.println("Printing text: " + text);
  }

  public void print(int number) {
    System.out.println("Printing number: " + number);
  }

  public void print(double decimal) {
    System.out.println("Printing decimal: " + decimal);
  }

  public void print(String text, int copies) {
    System.out.println("Printing \"" + text + "\" " + copies + " times");
  }
}

// ========== Method Overriding Example ==========

/**
 * Base Shape class.
 */
class Shape {
  /**
   * Draws the shape (to be overridden).
   */
  public void draw() {
    System.out.println("Drawing a generic shape");
  }

  /**
   * Calculates area (to be overridden).
   */
  public double calculateArea() {
    return 0.0;
  }
}

/**
 * Circle class extends Shape.
 */
class Circle extends Shape {
  private double radius;

  public Circle(double radius) {
    this.radius = radius;
  }

  public double getRadius() {
    return radius;
  }

  @Override
  public void draw() {
    System.out.println("Drawing a circle with radius " + radius);
  }

  @Override
  public double calculateArea() {
    return Math.PI * radius * radius;
  }

  public double calculateCircumference() {
    return 2 * Math.PI * radius;
  }
}

/**
 * Rectangle class extends Shape.
 */
class Rectangle extends Shape {
  private double width;
  private double height;

  public Rectangle(double width, double height) {
    this.width = width;
    this.height = height;
  }

  public double getWidth() {
    return width;
  }

  public double getHeight() {
    return height;
  }

  @Override
  public void draw() {
    System.out.println("Drawing a rectangle " + width + "x" + height);
  }

  @Override
  public double calculateArea() {
    return width * height;
  }
}

/**
 * Triangle class extends Shape.
 */
class Triangle extends Shape {
  private double base;
  private double height;

  public Triangle(double base, double height) {
    this.base = base;
    this.height = height;
  }

  public double getBase() {
    return base;
  }

  public double getHeight() {
    return height;
  }

  @Override
  public void draw() {
    System.out.println("Drawing a triangle with base " + base + " and height " + height);
  }

  @Override
  public double calculateArea() {
    return 0.5 * base * height;
  }
}

// ========== Interface Polymorphism ==========

/**
 * Playable interface.
 */
interface Playable {
  void play();
  void pause();
  void stop();
}

/**
 * MusicPlayer implements Playable.
 */
class MusicPlayer implements Playable {
  @Override
  public void play() {
    System.out.println("MusicPlayer: Playing music...");
  }

  @Override
  public void pause() {
    System.out.println("MusicPlayer: Music paused");
  }

  @Override
  public void stop() {
    System.out.println("MusicPlayer: Music stopped");
  }
}

/**
 * VideoPlayer implements Playable.
 */
class VideoPlayer implements Playable {
  @Override
  public void play() {
    System.out.println("VideoPlayer: Playing video...");
  }

  @Override
  public void pause() {
    System.out.println("VideoPlayer: Video paused");
  }

  @Override
  public void stop() {
    System.out.println("VideoPlayer: Video stopped");
  }
}

/**
 * GameConsole implements Playable.
 */
class GameConsole implements Playable {
  @Override
  public void play() {
    System.out.println("GameConsole: Starting game...");
  }

  @Override
  public void pause() {
    System.out.println("GameConsole: Game paused");
  }

  @Override
  public void stop() {
    System.out.println("GameConsole: Game ended");
  }
}

/**
 * SmartDevice interface.
 */
interface SmartDevice {
  void turnOn();
  void turnOff();
  void connectToWifi(String network);
}

/**
 * Chargeable interface.
 */
interface Chargeable {
  void charge();
  int getBatteryLevel();
}

/**
 * SmartPhone implements multiple interfaces.
 */
class SmartPhone implements SmartDevice, Chargeable {
  private int batteryLevel = 50;

  @Override
  public void turnOn() {
    System.out.println("SmartPhone: Powering on...");
  }

  @Override
  public void turnOff() {
    System.out.println("SmartPhone: Powering off...");
  }

  @Override
  public void connectToWifi(String network) {
    System.out.println("SmartPhone: Connected to " + network);
  }

  @Override
  public void charge() {
    batteryLevel = 100;
    System.out.println("SmartPhone: Fully charged!");
  }

  @Override
  public int getBatteryLevel() {
    return batteryLevel;
  }
}

// ========== Real-World Example ==========

/**
 * Abstract Payment class.
 */
abstract class Payment {
  protected String paymentId;

  public Payment() {
    this.paymentId = generatePaymentId();
  }

  /**
   * Abstract method for processing payment.
   */
  public abstract boolean processTransaction(double amount);

  /**
   * Abstract method for getting payment details.
   */
  public abstract String getPaymentDetails();

  /**
   * Generates a unique payment ID.
   */
  private String generatePaymentId() {
    return "PAY-" + System.currentTimeMillis();
  }

  public String getPaymentId() {
    return paymentId;
  }
}

/**
 * Credit card payment implementation.
 */
class CreditCardPayment extends Payment {
  private String cardNumber;
  private String cardHolder;

  public CreditCardPayment(String cardNumber, String cardHolder) {
    super();
    this.cardNumber = maskCardNumber(cardNumber);
    this.cardHolder = cardHolder;
  }

  @Override
  public boolean processTransaction(double amount) {
    System.out.println("Processing credit card payment...");
    // Simulate payment processing
    return true;
  }

  @Override
  public String getPaymentDetails() {
    return String.format("Credit Card: %s, Holder: %s", cardNumber, cardHolder);
  }

  private String maskCardNumber(String cardNumber) {
    if (cardNumber.length() > 4) {
      return "**** **** **** " + cardNumber.substring(cardNumber.length() - 4);
    }
    return cardNumber;
  }
}

/**
 * PayPal payment implementation.
 */
class PayPalPayment extends Payment {
  private String email;

  public PayPalPayment(String email) {
    super();
    this.email = email;
  }

  @Override
  public boolean processTransaction(double amount) {
    System.out.println("Processing PayPal payment...");
    return true;
  }

  @Override
  public String getPaymentDetails() {
    return "PayPal: " + email;
  }
}

/**
 * Cryptocurrency payment implementation.
 */
class CryptoPayment extends Payment {
  private String walletAddress;

  public CryptoPayment(String walletAddress) {
    super();
    this.walletAddress = walletAddress;
  }

  @Override
  public boolean processTransaction(double amount) {
    System.out.println("Processing cryptocurrency payment...");
    return true;
  }

  @Override
  public String getPaymentDetails() {
    return "Crypto Wallet: " + walletAddress;
  }
}

/**
 * Payment processor using polymorphism.
 */
class PaymentProcessor {
  /**
   * Processes any type of payment polymorphically.
   */
  public void processPayment(Payment payment, double amount) {
    System.out.println("Payment ID: " + payment.getPaymentId());
    System.out.println("Details: " + payment.getPaymentDetails());
    System.out.printf("Amount: $%.2f%n", amount);

    boolean success = payment.processTransaction(amount);

    if (success) {
      System.out.println("Status: SUCCESS");
    } else {
      System.out.println("Status: FAILED");
    }
  }
}
