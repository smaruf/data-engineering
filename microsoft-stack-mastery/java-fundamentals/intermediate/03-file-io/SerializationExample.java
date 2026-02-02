package com.microsoft.java.intermediate.fileio;

import java.io.*;

/**
 * SerializationExample demonstrates object serialization and deserialization in Java.
 * Covers Serializable interface, serialization process, and best practices.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class SerializationExample {
    
    /**
     * Simple serializable class.
     */
    public static class Person implements Serializable {
        private static final long serialVersionUID = 1L;
        
        private String name;
        private int age;
        private transient String password; // transient = not serialized
        
        public Person(String name, int age, String password) {
            this.name = name;
            this.age = age;
            this.password = password;
        }
        
        @Override
        public String toString() {
            return String.format("Person{name='%s', age=%d, password='%s'}", 
                name, age, password);
        }
        
        public String getName() { return name; }
        public int getAge() { return age; }
        public String getPassword() { return password; }
    }
    
    /**
     * Complex serializable class with nested objects.
     */
    public static class Employee implements Serializable {
        private static final long serialVersionUID = 2L;
        
        private String employeeId;
        private String name;
        private double salary;
        private Address address;
        private static String company = "Tech Corp"; // static = not serialized
        
        public Employee(String employeeId, String name, double salary, Address address) {
            this.employeeId = employeeId;
            this.name = name;
            this.salary = salary;
            this.address = address;
        }
        
        @Override
        public String toString() {
            return String.format("Employee{id='%s', name='%s', salary=%.2f, address=%s, company='%s'}", 
                employeeId, name, salary, address, company);
        }
    }
    
    /**
     * Serializable address class.
     */
    public static class Address implements Serializable {
        private static final long serialVersionUID = 3L;
        
        private String street;
        private String city;
        private String zipCode;
        
        public Address(String street, String city, String zipCode) {
            this.street = street;
            this.city = city;
            this.zipCode = zipCode;
        }
        
        @Override
        public String toString() {
            return String.format("%s, %s %s", street, city, zipCode);
        }
    }
    
    /**
     * Class with custom serialization logic.
     */
    public static class SecureData implements Serializable {
        private static final long serialVersionUID = 4L;
        
        private String username;
        private transient String sensitiveData;
        
        public SecureData(String username, String sensitiveData) {
            this.username = username;
            this.sensitiveData = sensitiveData;
        }
        
        private void writeObject(ObjectOutputStream out) throws IOException {
            out.defaultWriteObject();
            // Custom encryption logic (simplified for demo)
            String encrypted = encrypt(sensitiveData);
            out.writeObject(encrypted);
        }
        
        private void readObject(ObjectInputStream in) 
                throws IOException, ClassNotFoundException {
            in.defaultReadObject();
            // Custom decryption logic
            String encrypted = (String) in.readObject();
            this.sensitiveData = decrypt(encrypted);
        }
        
        private String encrypt(String data) {
            // Simplified encryption (reverse string)
            return data == null ? null : new StringBuilder(data).reverse().toString();
        }
        
        private String decrypt(String data) {
            // Simplified decryption (reverse string)
            return data == null ? null : new StringBuilder(data).reverse().toString();
        }
        
        @Override
        public String toString() {
            return String.format("SecureData{username='%s', sensitiveData='%s'}", 
                username, sensitiveData);
        }
    }
    
    /**
     * Demonstrates basic serialization.
     * 
     * @param obj Object to serialize
     * @param filename File to serialize to
     */
    public static void serializeObject(Object obj, String filename) {
        System.out.println("=== Serializing Object ===");
        
        try (ObjectOutputStream out = new ObjectOutputStream(
                new FileOutputStream(filename))) {
            
            out.writeObject(obj);
            System.out.println("Object serialized to: " + filename);
            System.out.println("Object: " + obj);
            
        } catch (IOException e) {
            System.err.println("Serialization error: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates basic deserialization.
     * 
     * @param filename File to deserialize from
     * @return Deserialized object
     */
    public static Object deserializeObject(String filename) {
        System.out.println("\n=== Deserializing Object ===");
        
        try (ObjectInputStream in = new ObjectInputStream(
                new FileInputStream(filename))) {
            
            Object obj = in.readObject();
            System.out.println("Object deserialized from: " + filename);
            System.out.println("Object: " + obj);
            return obj;
            
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + filename);
        } catch (IOException e) {
            System.err.println("Deserialization error: " + e.getMessage());
        } catch (ClassNotFoundException e) {
            System.err.println("Class not found: " + e.getMessage());
        }
        
        return null;
    }
    
    /**
     * Demonstrates serializing multiple objects.
     */
    public static void demonstrateMultipleObjects() {
        System.out.println("\n=== Multiple Objects Serialization ===");
        
        String filename = "multiple-objects.ser";
        
        // Serialize multiple objects
        try (ObjectOutputStream out = new ObjectOutputStream(
                new FileOutputStream(filename))) {
            
            out.writeObject(new Person("Alice", 30, "secret123"));
            out.writeObject(new Person("Bob", 25, "password456"));
            out.writeInt(42);
            out.writeUTF("Additional String Data");
            
            System.out.println("Multiple objects serialized");
            
        } catch (IOException e) {
            System.err.println("Serialization error: " + e.getMessage());
        }
        
        // Deserialize multiple objects
        try (ObjectInputStream in = new ObjectInputStream(
                new FileInputStream(filename))) {
            
            Person person1 = (Person) in.readObject();
            Person person2 = (Person) in.readObject();
            int number = in.readInt();
            String text = in.readUTF();
            
            System.out.println("Deserialized objects:");
            System.out.println("  Person 1: " + person1);
            System.out.println("  Person 2: " + person2);
            System.out.println("  Number: " + number);
            System.out.println("  Text: " + text);
            
        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Deserialization error: " + e.getMessage());
        }
        
        // Cleanup
        new File(filename).delete();
    }
    
    /**
     * Demonstrates serialization with inheritance.
     */
    public static void demonstrateInheritanceSerialization() {
        System.out.println("\n=== Inheritance Serialization ===");
        
        String filename = "employee.ser";
        
        Address address = new Address("123 Main St", "Seattle", "98101");
        Employee employee = new Employee("E001", "John Doe", 75000.0, address);
        
        serializeObject(employee, filename);
        
        Employee deserialized = (Employee) deserializeObject(filename);
        
        // Cleanup
        new File(filename).delete();
    }
    
    /**
     * Demonstrates transient fields.
     */
    public static void demonstrateTransientFields() {
        System.out.println("\n=== Transient Fields ===");
        
        String filename = "transient-test.ser";
        
        Person person = new Person("Charlie", 35, "topsecret");
        System.out.println("Before serialization: " + person);
        
        serializeObject(person, filename);
        
        Person deserialized = (Person) deserializeObject(filename);
        System.out.println("Note: password field is null (transient)");
        
        // Cleanup
        new File(filename).delete();
    }
    
    /**
     * Demonstrates custom serialization.
     */
    public static void demonstrateCustomSerialization() {
        System.out.println("\n=== Custom Serialization ===");
        
        String filename = "secure-data.ser";
        
        SecureData data = new SecureData("admin", "VerySecretData");
        System.out.println("Original: " + data);
        
        serializeObject(data, filename);
        
        SecureData deserialized = (SecureData) deserializeObject(filename);
        System.out.println("After custom serialization/deserialization: " + deserialized);
        
        // Cleanup
        new File(filename).delete();
    }
    
    /**
     * Demonstrates serialization with collections.
     */
    public static void demonstrateCollectionSerialization() {
        System.out.println("\n=== Collection Serialization ===");
        
        String filename = "collection.ser";
        
        java.util.List<Person> people = new java.util.ArrayList<>();
        people.add(new Person("Alice", 30, "pass1"));
        people.add(new Person("Bob", 25, "pass2"));
        people.add(new Person("Charlie", 35, "pass3"));
        
        try (ObjectOutputStream out = new ObjectOutputStream(
                new FileOutputStream(filename))) {
            
            out.writeObject(people);
            System.out.println("Serialized list of " + people.size() + " people");
            
        } catch (IOException e) {
            System.err.println("Serialization error: " + e.getMessage());
        }
        
        try (ObjectInputStream in = new ObjectInputStream(
                new FileInputStream(filename))) {
            
            @SuppressWarnings("unchecked")
            java.util.List<Person> deserializedList = 
                (java.util.List<Person>) in.readObject();
            
            System.out.println("Deserialized list:");
            deserializedList.forEach(p -> System.out.println("  " + p));
            
        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Deserialization error: " + e.getMessage());
        }
        
        // Cleanup
        new File(filename).delete();
    }
    
    /**
     * Demonstrates deep copy using serialization.
     */
    public static void demonstrateDeepCopy() {
        System.out.println("\n=== Deep Copy via Serialization ===");
        
        Address address = new Address("456 Oak Ave", "Portland", "97201");
        Employee original = new Employee("E002", "Jane Smith", 80000.0, address);
        
        System.out.println("Original: " + original);
        
        // Deep copy using serialization
        Employee copy = deepCopy(original);
        
        if (copy != null) {
            System.out.println("Deep copy: " + copy);
            System.out.println("Are they the same object? " + (original == copy));
        }
    }
    
    /**
     * Helper method to create deep copy via serialization.
     * 
     * @param obj Object to copy
     * @param <T> Type of object
     * @return Deep copy of object
     */
    @SuppressWarnings("unchecked")
    public static <T extends Serializable> T deepCopy(T obj) {
        try {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            ObjectOutputStream out = new ObjectOutputStream(bos);
            out.writeObject(obj);
            out.flush();
            
            ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
            ObjectInputStream in = new ObjectInputStream(bis);
            
            return (T) in.readObject();
            
        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Deep copy error: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Demonstrates handling serialVersionUID.
     */
    public static void demonstrateSerialVersionUID() {
        System.out.println("\n=== SerialVersionUID ===");
        
        System.out.println("SerialVersionUID is important for version control:");
        System.out.println("  Person serialVersionUID: " + 
            Person.class.getDeclaredFields()[0].getName());
        System.out.println("  If class structure changes, use new serialVersionUID");
        System.out.println("  to prevent InvalidClassException");
    }
    
    /**
     * Main method demonstrating serialization examples.
     */
    public static void main(String[] args) {
        System.out.println("Java Serialization Examples\n");
        
        // Basic serialization
        String filename = "person.ser";
        Person person = new Person("John", 30, "mypassword");
        serializeObject(person, filename);
        deserializeObject(filename);
        new File(filename).delete();
        
        // Advanced examples
        demonstrateMultipleObjects();
        demonstrateInheritanceSerialization();
        demonstrateTransientFields();
        demonstrateCustomSerialization();
        demonstrateCollectionSerialization();
        demonstrateDeepCopy();
        demonstrateSerialVersionUID();
        
        System.out.println("\n=== All serialization examples completed ===");
    }
}
