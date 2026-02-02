package com.microsoft.java.intermediate.jdbc;

import java.sql.*;
import java.util.*;

/**
 * CRUDOperations demonstrates Create, Read, Update, Delete operations with JDBC.
 * Covers INSERT, SELECT, UPDATE, DELETE queries with proper error handling.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class CRUDOperations {
    
    private static final String DB_URL = "jdbc:h2:mem:cruddb";
    private static final String DB_USER = "sa";
    private static final String DB_PASSWORD = "";
    
    /**
     * Employee data model.
     */
    public static class Employee {
        private int id;
        private String name;
        private String email;
        private String department;
        private double salary;
        
        public Employee(int id, String name, String email, String department, double salary) {
            this.id = id;
            this.name = name;
            this.email = email;
            this.department = department;
            this.salary = salary;
        }
        
        public Employee(String name, String email, String department, double salary) {
            this.name = name;
            this.email = email;
            this.department = department;
            this.salary = salary;
        }
        
        @Override
        public String toString() {
            return String.format("Employee{id=%d, name='%s', email='%s', dept='%s', salary=%.2f}",
                id, name, email, department, salary);
        }
        
        // Getters
        public int getId() { return id; }
        public String getName() { return name; }
        public String getEmail() { return email; }
        public String getDepartment() { return department; }
        public double getSalary() { return salary; }
    }
    
    /**
     * Initializes the database with tables.
     * 
     * @param conn Database connection
     */
    public static void initializeDatabase(Connection conn) {
        System.out.println("=== Initializing Database ===");
        
        String createTableSQL = 
            "CREATE TABLE IF NOT EXISTS employees (" +
            "id INT AUTO_INCREMENT PRIMARY KEY, " +
            "name VARCHAR(100) NOT NULL, " +
            "email VARCHAR(100) UNIQUE NOT NULL, " +
            "department VARCHAR(50), " +
            "salary DECIMAL(10,2)" +
            ")";
        
        try (Statement stmt = conn.createStatement()) {
            stmt.execute(createTableSQL);
            System.out.println("Table 'employees' created successfully");
        } catch (SQLException e) {
            System.err.println("Error creating table: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates INSERT operation (CREATE).
     * 
     * @param conn Database connection
     * @param employee Employee to insert
     * @return Generated employee ID or -1 if failed
     */
    public static int insertEmployee(Connection conn, Employee employee) {
        System.out.println("\n=== INSERT Operation ===");
        
        String sql = "INSERT INTO employees (name, email, department, salary) VALUES (?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            pstmt.setString(1, employee.getName());
            pstmt.setString(2, employee.getEmail());
            pstmt.setString(3, employee.getDepartment());
            pstmt.setDouble(4, employee.getSalary());
            
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Rows inserted: " + rowsAffected);
            
            // Get generated key
            ResultSet generatedKeys = pstmt.getGeneratedKeys();
            if (generatedKeys.next()) {
                int id = generatedKeys.getInt(1);
                System.out.println("Generated ID: " + id);
                return id;
            }
        } catch (SQLException e) {
            System.err.println("Insert failed: " + e.getMessage());
        }
        
        return -1;
    }
    
    /**
     * Demonstrates INSERT multiple records.
     * 
     * @param conn Database connection
     * @param employees List of employees to insert
     */
    public static void insertMultipleEmployees(Connection conn, List<Employee> employees) {
        System.out.println("\n=== INSERT Multiple Records ===");
        
        String sql = "INSERT INTO employees (name, email, department, salary) VALUES (?, ?, ?, ?)";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (Employee emp : employees) {
                pstmt.setString(1, emp.getName());
                pstmt.setString(2, emp.getEmail());
                pstmt.setString(3, emp.getDepartment());
                pstmt.setDouble(4, emp.getSalary());
                pstmt.addBatch();
            }
            
            int[] results = pstmt.executeBatch();
            System.out.println("Inserted " + results.length + " records");
        } catch (SQLException e) {
            System.err.println("Batch insert failed: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates SELECT operation (READ) - single record.
     * 
     * @param conn Database connection
     * @param id Employee ID
     * @return Employee or null if not found
     */
    public static Employee selectEmployeeById(Connection conn, int id) {
        System.out.println("\n=== SELECT by ID ===");
        
        String sql = "SELECT * FROM employees WHERE id = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            
            ResultSet rs = pstmt.executeQuery();
            if (rs.next()) {
                Employee emp = new Employee(
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getString("email"),
                    rs.getString("department"),
                    rs.getDouble("salary")
                );
                System.out.println("Found: " + emp);
                return emp;
            } else {
                System.out.println("No employee found with ID: " + id);
            }
        } catch (SQLException e) {
            System.err.println("Select failed: " + e.getMessage());
        }
        
        return null;
    }
    
    /**
     * Demonstrates SELECT all records.
     * 
     * @param conn Database connection
     * @return List of all employees
     */
    public static List<Employee> selectAllEmployees(Connection conn) {
        System.out.println("\n=== SELECT All Employees ===");
        
        List<Employee> employees = new ArrayList<>();
        String sql = "SELECT * FROM employees ORDER BY id";
        
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                Employee emp = new Employee(
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getString("email"),
                    rs.getString("department"),
                    rs.getDouble("salary")
                );
                employees.add(emp);
            }
            
            System.out.println("Found " + employees.size() + " employees");
        } catch (SQLException e) {
            System.err.println("Select all failed: " + e.getMessage());
        }
        
        return employees;
    }
    
    /**
     * Demonstrates SELECT with WHERE clause.
     * 
     * @param conn Database connection
     * @param department Department to filter by
     * @return List of employees in department
     */
    public static List<Employee> selectEmployeesByDepartment(Connection conn, String department) {
        System.out.println("\n=== SELECT by Department ===");
        
        List<Employee> employees = new ArrayList<>();
        String sql = "SELECT * FROM employees WHERE department = ? ORDER BY name";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, department);
            
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                employees.add(new Employee(
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getString("email"),
                    rs.getString("department"),
                    rs.getDouble("salary")
                ));
            }
            
            System.out.println("Found " + employees.size() + " employees in " + department);
        } catch (SQLException e) {
            System.err.println("Select by department failed: " + e.getMessage());
        }
        
        return employees;
    }
    
    /**
     * Demonstrates SELECT with aggregate functions.
     * 
     * @param conn Database connection
     */
    public static void selectAggregates(Connection conn) {
        System.out.println("\n=== SELECT with Aggregates ===");
        
        String sql = 
            "SELECT department, " +
            "COUNT(*) as emp_count, " +
            "AVG(salary) as avg_salary, " +
            "MIN(salary) as min_salary, " +
            "MAX(salary) as max_salary " +
            "FROM employees " +
            "GROUP BY department";
        
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            System.out.println("Department Statistics:");
            while (rs.next()) {
                System.out.printf("  %s: Count=%d, Avg=%.2f, Min=%.2f, Max=%.2f%n",
                    rs.getString("department"),
                    rs.getInt("emp_count"),
                    rs.getDouble("avg_salary"),
                    rs.getDouble("min_salary"),
                    rs.getDouble("max_salary")
                );
            }
        } catch (SQLException e) {
            System.err.println("Aggregate query failed: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates UPDATE operation.
     * 
     * @param conn Database connection
     * @param id Employee ID
     * @param newSalary New salary amount
     * @return Number of rows updated
     */
    public static int updateEmployeeSalary(Connection conn, int id, double newSalary) {
        System.out.println("\n=== UPDATE Operation ===");
        
        String sql = "UPDATE employees SET salary = ? WHERE id = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, newSalary);
            pstmt.setInt(2, id);
            
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Rows updated: " + rowsAffected);
            return rowsAffected;
        } catch (SQLException e) {
            System.err.println("Update failed: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * Demonstrates UPDATE multiple columns.
     * 
     * @param conn Database connection
     * @param id Employee ID
     * @param department New department
     * @param salary New salary
     */
    public static void updateEmployee(Connection conn, int id, String department, double salary) {
        System.out.println("\n=== UPDATE Multiple Columns ===");
        
        String sql = "UPDATE employees SET department = ?, salary = ? WHERE id = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, department);
            pstmt.setDouble(2, salary);
            pstmt.setInt(3, id);
            
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Updated employee ID " + id + ": " + rowsAffected + " rows");
        } catch (SQLException e) {
            System.err.println("Update failed: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates DELETE operation.
     * 
     * @param conn Database connection
     * @param id Employee ID to delete
     * @return Number of rows deleted
     */
    public static int deleteEmployee(Connection conn, int id) {
        System.out.println("\n=== DELETE Operation ===");
        
        String sql = "DELETE FROM employees WHERE id = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Rows deleted: " + rowsAffected);
            return rowsAffected;
        } catch (SQLException e) {
            System.err.println("Delete failed: " + e.getMessage());
            return 0;
        }
    }
    
    /**
     * Demonstrates DELETE with condition.
     * 
     * @param conn Database connection
     * @param department Department to delete
     */
    public static void deleteEmployeesByDepartment(Connection conn, String department) {
        System.out.println("\n=== DELETE by Department ===");
        
        String sql = "DELETE FROM employees WHERE department = ?";
        
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, department);
            
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Deleted " + rowsAffected + " employees from " + department);
        } catch (SQLException e) {
            System.err.println("Delete failed: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates counting records.
     * 
     * @param conn Database connection
     * @return Total number of employees
     */
    public static int countEmployees(Connection conn) {
        System.out.println("\n=== COUNT Records ===");
        
        String sql = "SELECT COUNT(*) as total FROM employees";
        
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            if (rs.next()) {
                int count = rs.getInt("total");
                System.out.println("Total employees: " + count);
                return count;
            }
        } catch (SQLException e) {
            System.err.println("Count failed: " + e.getMessage());
        }
        
        return 0;
    }
    
    /**
     * Main method demonstrating CRUD operations.
     */
    public static void main(String[] args) {
        System.out.println("JDBC CRUD Operations Examples\n");
        
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            
            // Initialize database
            initializeDatabase(conn);
            
            // CREATE - Insert single employee
            Employee emp1 = new Employee("John Doe", "john.doe@example.com", 
                "Engineering", 75000.00);
            int id1 = insertEmployee(conn, emp1);
            
            // CREATE - Insert multiple employees
            List<Employee> employees = Arrays.asList(
                new Employee("Jane Smith", "jane.smith@example.com", "Sales", 65000.00),
                new Employee("Bob Wilson", "bob.wilson@example.com", "Engineering", 80000.00),
                new Employee("Alice Johnson", "alice.j@example.com", "HR", 60000.00),
                new Employee("Charlie Brown", "charlie.b@example.com", "Sales", 70000.00)
            );
            insertMultipleEmployees(conn, employees);
            
            // READ - Select single employee
            selectEmployeeById(conn, id1);
            
            // READ - Select all employees
            List<Employee> allEmployees = selectAllEmployees(conn);
            allEmployees.forEach(System.out::println);
            
            // READ - Select by department
            selectEmployeesByDepartment(conn, "Engineering");
            
            // READ - Aggregates
            selectAggregates(conn);
            
            // UPDATE - Single column
            updateEmployeeSalary(conn, id1, 78000.00);
            selectEmployeeById(conn, id1);
            
            // UPDATE - Multiple columns
            updateEmployee(conn, id1, "Management", 85000.00);
            selectEmployeeById(conn, id1);
            
            // COUNT
            countEmployees(conn);
            
            // DELETE - Single employee
            deleteEmployee(conn, id1);
            
            // DELETE - By department
            deleteEmployeesByDepartment(conn, "Sales");
            
            // Final count
            countEmployees(conn);
            selectAllEmployees(conn);
            
            System.out.println("\n=== All CRUD operations completed ===");
            
        } catch (SQLException e) {
            System.err.println("Database error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
