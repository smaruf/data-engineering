# Java Fundamentals - Beginner Level

Comprehensive Java learning examples for the Microsoft Stack Mastery project.

## Directory Structure

```
beginner/
├── 01-java-basics/
│   ├── HelloWorld.java         - Basic Hello World, comments, output
│   ├── DataTypes.java          - All primitive types, strings, casting, constants
│   ├── ControlFlow.java        - if-else, switch, loops, break, continue
│   └── ArraysDemo.java         - Arrays, multi-dimensional, operations
│
├── 02-oop-fundamentals/
│   ├── Classes.java            - Classes, constructors, instance vs static
│   ├── Inheritance.java        - Parent-child, super keyword, overriding
│   ├── Polymorphism.java       - Overloading, overriding, interfaces
│   ├── Abstraction.java        - Abstract classes, methods, real-world examples
│   └── Encapsulation.java      - Private fields, getters/setters, data hiding
│
└── 03-collections-streams/
    ├── ListExamples.java       - ArrayList, LinkedList, operations
    ├── MapExamples.java        - HashMap, TreeMap, LinkedHashMap
    ├── StreamAPI.java          - Stream creation, filter, map, reduce, collect
    └── Lambda.java             - Lambda expressions, functional interfaces, method references
```

## How to Compile and Run

### Option 1: Compile and Run Individual Files (Recommended)

Since these files contain multiple classes and helper classes, compile each file individually:

```bash
# Navigate to the directory
cd beginner/01-java-basics

# Compile a single file
javac HelloWorld.java

# Run the class (note: classes are in packages)
java HelloWorld

# Or run with the full package path
java -cp . com.microsoft.java.basics.HelloWorld
```

### Option 2: Create Proper Package Structure

For proper package execution, create the directory structure:

```bash
# From the beginner/ directory
mkdir -p com/microsoft/java/basics
mkdir -p com/microsoft/java/oop
mkdir -p com/microsoft/java/collections

# Copy files to proper package directories
cp 01-java-basics/*.java com/microsoft/java/basics/
cp 02-oop-fundamentals/*.java com/microsoft/java/oop/
cp 03-collections-streams/*.java com/microsoft/java/collections/

# Compile
javac com/microsoft/java/basics/*.java
javac com/microsoft/java/oop/*.java
javac com/microsoft/java/collections/*.java

# Run with full package name
java com.microsoft.java.basics.HelloWorld
java com.microsoft.java.basics.DataTypes
```

### Option 3: Quick Test (Simplified)

To quickly test the examples, you can temporarily remove the package declarations:

```bash
# Edit the Java file and comment out the package line
# package com.microsoft.java.basics;  // Comment this line

javac HelloWorld.java
java HelloWorld
```

## Learning Path

### Phase 1: Java Basics (01-java-basics/)
1. **HelloWorld.java** - Start here to understand basic Java structure
2. **DataTypes.java** - Learn all data types and type operations
3. **ControlFlow.java** - Master control structures and loops
4. **ArraysDemo.java** - Understand arrays and array operations

### Phase 2: OOP Fundamentals (02-oop-fundamentals/)
1. **Classes.java** - Learn classes, objects, constructors
2. **Inheritance.java** - Understand inheritance and code reuse
3. **Polymorphism.java** - Master polymorphism concepts
4. **Abstraction.java** - Learn abstract classes and methods
5. **Encapsulation.java** - Understand data hiding and encapsulation

### Phase 3: Collections & Streams (03-collections-streams/)
1. **ListExamples.java** - Master List interface and implementations
2. **MapExamples.java** - Learn Map interface and operations
3. **Lambda.java** - Understand lambda expressions and functional programming
4. **StreamAPI.java** - Master Stream API for data processing

## Features

All files include:
- ✅ Comprehensive JavaDoc comments
- ✅ Working main() methods with examples
- ✅ Practical, real-world use cases
- ✅ Inline comments explaining concepts
- ✅ Error handling
- ✅ Google Java Style Guide compliance

## Requirements

- Java Development Kit (JDK) 11 or later recommended
- Java 8+ for Lambda and Stream API features

## Compilation Verification

All files have been verified to compile successfully:
- ✅ 01-java-basics: 4 files compile without errors
- ✅ 02-oop-fundamentals: 5 files compile individually
- ✅ 03-collections-streams: 4 files compile without errors

## Notes

- Each file is self-contained with working examples
- OOP files contain multiple helper classes for demonstration
- Files should be compiled individually or with proper package structure
- All examples are production-ready with error handling
- Real-world use cases are included in each file

## Running Examples

Each file demonstrates its concepts when you run it. For example:

```bash
# Compile
javac HelloWorld.java

# Run and see the output
java HelloWorld

# Example output:
# Hello, World!
# Welcome to Java Programming!
# ...
```

## Additional Resources

- Oracle Java Documentation: https://docs.oracle.com/javase/
- Java API Documentation: https://docs.oracle.com/en/java/javase/11/docs/api/
- Google Java Style Guide: https://google.github.io/styleguide/javaguide.html

## License

These examples are provided for educational purposes as part of the Microsoft Stack Mastery project.
