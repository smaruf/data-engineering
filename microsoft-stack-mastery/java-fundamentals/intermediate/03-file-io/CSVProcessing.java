package com.microsoft.java.intermediate.fileio;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

/**
 * CSVProcessing demonstrates CSV file reading and writing in Java.
 * Covers parsing, validation, error handling, and data transformation.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class CSVProcessing {
    
    /**
     * Represents a CSV record for employee data.
     */
    public static class Employee {
        private String id;
        private String name;
        private String department;
        private double salary;
        
        public Employee(String id, String name, String department, double salary) {
            this.id = id;
            this.name = name;
            this.department = department;
            this.salary = salary;
        }
        
        public static Employee fromCSV(String csvLine) throws IllegalArgumentException {
            String[] fields = parseCSVLine(csvLine);
            
            if (fields.length != 4) {
                throw new IllegalArgumentException(
                    "Invalid CSV format. Expected 4 fields, got " + fields.length);
            }
            
            try {
                return new Employee(
                    fields[0].trim(),
                    fields[1].trim(),
                    fields[2].trim(),
                    Double.parseDouble(fields[3].trim())
                );
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Invalid salary format: " + fields[3], e);
            }
        }
        
        public String toCSV() {
            return String.format("%s,%s,%s,%.2f", id, name, department, salary);
        }
        
        @Override
        public String toString() {
            return String.format("Employee{id='%s', name='%s', dept='%s', salary=%.2f}",
                id, name, department, salary);
        }
        
        public String getId() { return id; }
        public String getName() { return name; }
        public String getDepartment() { return department; }
        public double getSalary() { return salary; }
    }
    
    /**
     * Parses a CSV line handling quoted fields.
     * 
     * @param line CSV line to parse
     * @return Array of fields
     */
    public static String[] parseCSVLine(String line) {
        List<String> fields = new ArrayList<>();
        StringBuilder currentField = new StringBuilder();
        boolean inQuotes = false;
        
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                fields.add(currentField.toString());
                currentField = new StringBuilder();
            } else {
                currentField.append(c);
            }
        }
        
        fields.add(currentField.toString());
        return fields.toArray(new String[0]);
    }
    
    /**
     * Writes employees to CSV file.
     * 
     * @param filename Output file name
     * @param employees List of employees
     * @return true if successful
     */
    public static boolean writeCSV(String filename, List<Employee> employees) {
        System.out.println("=== Writing CSV File ===");
        
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            // Write header
            writer.write("ID,Name,Department,Salary");
            writer.newLine();
            
            // Write data
            for (Employee emp : employees) {
                writer.write(emp.toCSV());
                writer.newLine();
            }
            
            System.out.println("Successfully wrote " + employees.size() + 
                " records to " + filename);
            return true;
            
        } catch (IOException e) {
            System.err.println("Error writing CSV: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Reads employees from CSV file.
     * 
     * @param filename Input file name
     * @return List of employees
     */
    public static List<Employee> readCSV(String filename) {
        System.out.println("\n=== Reading CSV File ===");
        
        List<Employee> employees = new ArrayList<>();
        int lineNumber = 0;
        int errorCount = 0;
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            
            // Skip header
            line = reader.readLine();
            lineNumber++;
            
            if (line != null) {
                System.out.println("Header: " + line);
            }
            
            // Read data
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                
                if (line.trim().isEmpty()) {
                    continue; // Skip empty lines
                }
                
                try {
                    Employee emp = Employee.fromCSV(line);
                    employees.add(emp);
                } catch (IllegalArgumentException e) {
                    System.err.println("Error on line " + lineNumber + ": " + e.getMessage());
                    errorCount++;
                }
            }
            
            System.out.println("Successfully read " + employees.size() + " valid records");
            if (errorCount > 0) {
                System.out.println("Skipped " + errorCount + " invalid records");
            }
            
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + filename);
        } catch (IOException e) {
            System.err.println("Error reading CSV: " + e.getMessage());
        }
        
        return employees;
    }
    
    /**
     * Reads CSV using Java 8 Streams.
     * 
     * @param filename Input file name
     * @return List of employees
     */
    public static List<Employee> readCSVWithStreams(String filename) {
        System.out.println("\n=== Reading CSV with Streams ===");
        
        try {
            List<Employee> employees = Files.lines(Paths.get(filename))
                .skip(1) // Skip header
                .filter(line -> !line.trim().isEmpty())
                .map(line -> {
                    try {
                        return Employee.fromCSV(line);
                    } catch (IllegalArgumentException e) {
                        System.err.println("Invalid record: " + e.getMessage());
                        return null;
                    }
                })
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
            
            System.out.println("Read " + employees.size() + " records using streams");
            return employees;
            
        } catch (IOException e) {
            System.err.println("Error reading CSV: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Demonstrates CSV data filtering.
     * 
     * @param employees List of employees
     * @param minSalary Minimum salary filter
     */
    public static void filterEmployees(List<Employee> employees, double minSalary) {
        System.out.println("\n=== Filtering Employees (Salary >= " + minSalary + ") ===");
        
        List<Employee> filtered = employees.stream()
            .filter(emp -> emp.getSalary() >= minSalary)
            .collect(Collectors.toList());
        
        System.out.println("Found " + filtered.size() + " employees:");
        filtered.forEach(System.out::println);
    }
    
    /**
     * Demonstrates CSV data grouping.
     * 
     * @param employees List of employees
     */
    public static void groupByDepartment(List<Employee> employees) {
        System.out.println("\n=== Grouping by Department ===");
        
        Map<String, List<Employee>> byDepartment = employees.stream()
            .collect(Collectors.groupingBy(Employee::getDepartment));
        
        byDepartment.forEach((dept, empList) -> {
            System.out.println(dept + " (" + empList.size() + " employees):");
            empList.forEach(emp -> System.out.println("  " + emp));
        });
    }
    
    /**
     * Demonstrates CSV aggregation.
     * 
     * @param employees List of employees
     */
    public static void calculateStatistics(List<Employee> employees) {
        System.out.println("\n=== Salary Statistics ===");
        
        DoubleSummaryStatistics stats = employees.stream()
            .mapToDouble(Employee::getSalary)
            .summaryStatistics();
        
        System.out.println("Count: " + stats.getCount());
        System.out.println("Sum: $" + String.format("%.2f", stats.getSum()));
        System.out.println("Average: $" + String.format("%.2f", stats.getAverage()));
        System.out.println("Min: $" + String.format("%.2f", stats.getMin()));
        System.out.println("Max: $" + String.format("%.2f", stats.getMax()));
    }
    
    /**
     * Demonstrates CSV transformation and export.
     * 
     * @param inputFile Input CSV file
     * @param outputFile Output CSV file
     */
    public static void transformAndExport(String inputFile, String outputFile) {
        System.out.println("\n=== Transform and Export ===");
        
        List<Employee> employees = readCSV(inputFile);
        
        // Transform: give 10% raise to all employees
        List<Employee> transformed = employees.stream()
            .map(emp -> new Employee(
                emp.getId(),
                emp.getName(),
                emp.getDepartment(),
                emp.getSalary() * 1.10
            ))
            .collect(Collectors.toList());
        
        writeCSV(outputFile, transformed);
    }
    
    /**
     * Demonstrates handling CSV with quoted fields.
     */
    public static void demonstrateQuotedFields() {
        System.out.println("\n=== Handling Quoted Fields ===");
        
        String filename = "quoted-test.csv";
        
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            writer.write("ID,Name,Department,Salary\n");
            writer.write("E001,\"Smith, John\",Engineering,75000\n");
            writer.write("E002,\"Doe, Jane\",\"Sales & Marketing\",65000\n");
            writer.write("E003,Bob Wilson,IT,70000\n");
        } catch (IOException e) {
            System.err.println("Error creating test file: " + e.getMessage());
            return;
        }
        
        System.out.println("Parsing CSV with quoted fields:");
        String[] testLines = {
            "E001,\"Smith, John\",Engineering,75000",
            "E002,\"Doe, Jane\",\"Sales & Marketing\",65000"
        };
        
        for (String line : testLines) {
            String[] fields = parseCSVLine(line);
            System.out.println("Parsed: " + Arrays.toString(fields));
        }
        
        // Cleanup
        new File(filename).delete();
    }
    
    /**
     * Demonstrates CSV validation.
     * 
     * @param employees List of employees to validate
     */
    public static void validateData(List<Employee> employees) {
        System.out.println("\n=== Data Validation ===");
        
        int validCount = 0;
        int invalidCount = 0;
        
        for (Employee emp : employees) {
            List<String> errors = new ArrayList<>();
            
            // Validation rules
            if (emp.getId() == null || emp.getId().isEmpty()) {
                errors.add("Missing ID");
            }
            if (emp.getName() == null || emp.getName().isEmpty()) {
                errors.add("Missing name");
            }
            if (emp.getSalary() < 0) {
                errors.add("Negative salary");
            }
            if (emp.getSalary() > 1000000) {
                errors.add("Unrealistic salary");
            }
            
            if (errors.isEmpty()) {
                validCount++;
            } else {
                invalidCount++;
                System.out.println("Invalid: " + emp + " - " + 
                    String.join(", ", errors));
            }
        }
        
        System.out.println("\nValidation Summary:");
        System.out.println("  Valid records: " + validCount);
        System.out.println("  Invalid records: " + invalidCount);
    }
    
    /**
     * Demonstrates merging multiple CSV files.
     * 
     * @param inputFiles Array of input file names
     * @param outputFile Output file name
     */
    public static void mergeCSVFiles(String[] inputFiles, String outputFile) {
        System.out.println("\n=== Merging CSV Files ===");
        
        List<Employee> allEmployees = new ArrayList<>();
        
        for (String file : inputFiles) {
            List<Employee> employees = readCSV(file);
            allEmployees.addAll(employees);
        }
        
        writeCSV(outputFile, allEmployees);
        System.out.println("Merged " + inputFiles.length + " files into " + outputFile);
    }
    
    /**
     * Main method demonstrating CSV processing.
     */
    public static void main(String[] args) {
        System.out.println("Java CSV Processing Examples\n");
        
        String csvFile = "employees.csv";
        String transformedFile = "employees-raised.csv";
        
        // Create sample data
        List<Employee> sampleEmployees = Arrays.asList(
            new Employee("E001", "John Smith", "Engineering", 75000.00),
            new Employee("E002", "Jane Doe", "Sales", 65000.00),
            new Employee("E003", "Bob Wilson", "Engineering", 80000.00),
            new Employee("E004", "Alice Johnson", "HR", 60000.00),
            new Employee("E005", "Charlie Brown", "Sales", 70000.00)
        );
        
        // Write CSV
        writeCSV(csvFile, sampleEmployees);
        
        // Read CSV
        List<Employee> employees = readCSV(csvFile);
        
        // Read with streams
        List<Employee> streamEmployees = readCSVWithStreams(csvFile);
        
        // Filter data
        filterEmployees(employees, 70000);
        
        // Group data
        groupByDepartment(employees);
        
        // Calculate statistics
        calculateStatistics(employees);
        
        // Transform and export
        transformAndExport(csvFile, transformedFile);
        
        // Validate data
        validateData(employees);
        
        // Quoted fields
        demonstrateQuotedFields();
        
        // Cleanup
        System.out.println("\n=== Cleanup ===");
        new File(csvFile).delete();
        new File(transformedFile).delete();
        System.out.println("Test files cleaned up");
        
        System.out.println("\n=== All CSV processing examples completed ===");
    }
}
