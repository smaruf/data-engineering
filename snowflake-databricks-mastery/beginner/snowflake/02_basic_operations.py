"""
Snowflake Basic Operations (CRUD)
==================================

This script demonstrates:
1. Creating databases, schemas, and tables
2. Inserting data (CREATE)
3. Reading data (READ)
4. Updating data (UPDATE)
5. Deleting data (DELETE)
6. Best practices for DDL/DML operations

Prerequisites:
- Completed 01_setup_connection.py
- Active Snowflake account
"""

import os
from dotenv import load_dotenv
import snowflake.connector
from datetime import datetime

# Load environment variables
load_dotenv()


class SnowflakeBasicOperations:
    """Demonstrates basic CRUD operations in Snowflake"""
    
    def __init__(self):
        """Initialize connection"""
        self.conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        )
        self.cursor = self.conn.cursor()
    
    def execute(self, query: str, description: str = ""):
        """Execute a query and print results"""
        try:
            if description:
                print(f"\n📝 {description}")
            print(f"   SQL: {query[:100]}...")
            
            self.cursor.execute(query)
            
            # Check if query returns results
            if self.cursor.description:
                results = self.cursor.fetchall()
                if results:
                    print(f"   ✅ Returned {len(results)} rows")
                    return results
                else:
                    print("   ✅ Query executed (no rows returned)")
            else:
                print("   ✅ Query executed successfully")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
    
    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def example_1_create_database_schema():
    """Example 1: Create database and schema"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Create Database and Schema")
    print("="*60)
    
    ops = SnowflakeBasicOperations()
    
    try:
        # Create database
        ops.execute(
            "CREATE DATABASE IF NOT EXISTS LEARNING_DB",
            "Creating database"
        )
        
        # Use database
        ops.execute(
            "USE DATABASE LEARNING_DB",
            "Switching to database"
        )
        
        # Create schema
        ops.execute(
            "CREATE SCHEMA IF NOT EXISTS DEMO_SCHEMA",
            "Creating schema"
        )
        
        # Use schema
        ops.execute(
            "USE SCHEMA DEMO_SCHEMA",
            "Switching to schema"
        )
        
        # List databases
        results = ops.execute(
            "SHOW DATABASES LIKE 'LEARNING_DB'",
            "Listing databases"
        )
        
        print("\n📊 Database created successfully!")
        
    finally:
        ops.close()


def example_2_create_table():
    """Example 2: Create tables with different data types"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Create Tables")
    print("="*60)
    
    ops = SnowflakeBasicOperations()
    
    try:
        # Use database and schema
        ops.execute("USE DATABASE LEARNING_DB")
        ops.execute("USE SCHEMA DEMO_SCHEMA")
        
        # Create a simple table
        ops.execute(
            """
            CREATE OR REPLACE TABLE employees (
                employee_id INTEGER AUTOINCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                department VARCHAR(50),
                salary NUMBER(10, 2),
                hire_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
                PRIMARY KEY (employee_id)
            )
            """,
            "Creating employees table"
        )
        
        # Create a table with variant (JSON) column
        ops.execute(
            """
            CREATE OR REPLACE TABLE products (
                product_id INTEGER AUTOINCREMENT,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                price NUMBER(10, 2),
                specifications VARIANT,  -- For JSON data
                created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
                PRIMARY KEY (product_id)
            )
            """,
            "Creating products table with VARIANT column"
        )
        
        # Show tables
        results = ops.execute(
            "SHOW TABLES",
            "Listing tables"
        )
        
        print("\n📊 Tables created successfully!")
        
    finally:
        ops.close()


def example_3_insert_data():
    """Example 3: Insert data into tables"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Insert Data (CREATE)")
    print("="*60)
    
    ops = SnowflakeBasicOperations()
    
    try:
        ops.execute("USE DATABASE LEARNING_DB")
        ops.execute("USE SCHEMA DEMO_SCHEMA")
        
        # Insert single row
        ops.execute(
            """
            INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
            VALUES ('John', 'Doe', 'john.doe@example.com', 'Engineering', 95000.00, '2023-01-15')
            """,
            "Inserting single employee"
        )
        
        # Insert multiple rows
        ops.execute(
            """
            INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
            VALUES 
                ('Jane', 'Smith', 'jane.smith@example.com', 'Engineering', 105000.00, '2023-02-01'),
                ('Bob', 'Johnson', 'bob.johnson@example.com', 'Sales', 75000.00, '2023-03-10'),
                ('Alice', 'Williams', 'alice.williams@example.com', 'Marketing', 80000.00, '2023-04-05'),
                ('Charlie', 'Brown', 'charlie.brown@example.com', 'Engineering', 92000.00, '2023-05-20')
            """,
            "Inserting multiple employees"
        )
        
        # Insert products with JSON data
        ops.execute(
            """
            INSERT INTO products (product_name, category, price, specifications)
            SELECT 
                'Laptop Pro 15',
                'Electronics',
                1299.99,
                PARSE_JSON('{
                    "brand": "TechCorp",
                    "ram": "16GB",
                    "storage": "512GB SSD",
                    "screen": "15.6 inch"
                }')
            """,
            "Inserting product with JSON specifications"
        )
        
        ops.execute(
            """
            INSERT INTO products (product_name, category, price, specifications)
            SELECT 
                'Wireless Mouse',
                'Accessories',
                29.99,
                PARSE_JSON('{
                    "brand": "TechCorp",
                    "wireless": true,
                    "battery": "AA batteries"
                }')
            """,
            "Inserting another product"
        )
        
        print("\n📊 Data inserted successfully!")
        
    finally:
        ops.close()


def example_4_read_data():
    """Example 4: Read and query data (READ)"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Read Data (SELECT)")
    print("="*60)
    
    ops = SnowflakeBasicOperations()
    
    try:
        ops.execute("USE DATABASE LEARNING_DB")
        ops.execute("USE SCHEMA DEMO_SCHEMA")
        
        # Select all employees
        print("\n📊 All Employees:")
        results = ops.execute("SELECT * FROM employees")
        for row in results:
            print(f"   {row[0]}: {row[1]} {row[2]} - {row[4]} (${row[5]:,.2f})")
        
        # Select with WHERE clause
        print("\n📊 Engineering Department:")
        results = ops.execute(
            "SELECT first_name, last_name, salary FROM employees WHERE department = 'Engineering'"
        )
        for row in results:
            print(f"   {row[0]} {row[1]}: ${row[2]:,.2f}")
        
        # Select with ORDER BY
        print("\n📊 Employees by Salary (Highest to Lowest):")
        results = ops.execute(
            """
            SELECT first_name, last_name, department, salary 
            FROM employees 
            ORDER BY salary DESC
            """
        )
        for row in results:
            print(f"   {row[0]} {row[1]} ({row[2]}): ${row[3]:,.2f}")
        
        # Aggregate functions
        print("\n📊 Department Statistics:")
        results = ops.execute(
            """
            SELECT 
                department,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary,
                MIN(salary) as min_salary,
                MAX(salary) as max_salary
            FROM employees
            GROUP BY department
            ORDER BY avg_salary DESC
            """
        )
        for row in results:
            print(f"   {row[0]}: {row[1]} employees, Avg: ${row[2]:,.2f}")
        
        # Query JSON data
        print("\n📊 Products with Specifications:")
        results = ops.execute(
            """
            SELECT 
                product_name,
                category,
                price,
                specifications:brand::STRING as brand,
                specifications
            FROM products
            """
        )
        for row in results:
            print(f"   {row[0]} ({row[1]}): ${row[2]} - Brand: {row[3]}")
        
    finally:
        ops.close()


def example_5_update_data():
    """Example 5: Update existing data (UPDATE)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Update Data (UPDATE)")
    print("="*60)
    
    ops = SnowflakeBasicOperations()
    
    try:
        ops.execute("USE DATABASE LEARNING_DB")
        ops.execute("USE SCHEMA DEMO_SCHEMA")
        
        # Update single record
        ops.execute(
            """
            UPDATE employees 
            SET salary = 100000.00 
            WHERE email = 'john.doe@example.com'
            """,
            "Updating John Doe's salary"
        )
        
        # Update multiple records
        ops.execute(
            """
            UPDATE employees 
            SET salary = salary * 1.05 
            WHERE department = 'Engineering'
            """,
            "Giving 5% raise to Engineering department"
        )
        
        # Verify updates
        print("\n📊 Updated Salaries:")
        results = ops.execute(
            "SELECT first_name, last_name, department, salary FROM employees ORDER BY salary DESC"
        )
        for row in results:
            print(f"   {row[0]} {row[1]} ({row[2]}): ${row[3]:,.2f}")
        
    finally:
        ops.close()


def example_6_delete_data():
    """Example 6: Delete data (DELETE)"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Delete Data (DELETE)")
    print("="*60)
    
    ops = SnowflakeBasicOperations()
    
    try:
        ops.execute("USE DATABASE LEARNING_DB")
        ops.execute("USE SCHEMA DEMO_SCHEMA")
        
        # Show count before delete
        results = ops.execute(
            "SELECT COUNT(*) FROM employees",
            "Counting employees before delete"
        )
        print(f"   Total employees: {results[0][0]}")
        
        # Delete with WHERE clause
        ops.execute(
            """
            DELETE FROM employees 
            WHERE department = 'Sales'
            """,
            "Deleting Sales department employees"
        )
        
        # Show count after delete
        results = ops.execute(
            "SELECT COUNT(*) FROM employees",
            "Counting employees after delete"
        )
        print(f"   Total employees: {results[0][0]}")
        
        # Show remaining employees
        print("\n📊 Remaining Employees:")
        results = ops.execute("SELECT first_name, last_name, department FROM employees")
        for row in results:
            print(f"   {row[0]} {row[1]} ({row[2]})")
        
    finally:
        ops.close()


def example_7_transactions():
    """Example 7: Using transactions"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Transactions")
    print("="*60)
    
    conn = snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        autocommit=False  # Disable autocommit for transaction control
    )
    
    try:
        cursor = conn.cursor()
        cursor.execute("USE DATABASE LEARNING_DB")
        cursor.execute("USE SCHEMA DEMO_SCHEMA")
        
        # Begin transaction
        print("\n📝 Starting transaction...")
        cursor.execute("BEGIN TRANSACTION")
        
        # Insert new employee
        cursor.execute(
            """
            INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
            VALUES ('Test', 'User', 'test.user@example.com', 'IT', 70000.00, CURRENT_DATE())
            """
        )
        print("   ✅ Inserted test employee")
        
        # Commit transaction
        conn.commit()
        print("   ✅ Transaction committed")
        
        # Try a rollback example
        print("\n📝 Starting rollback example...")
        cursor.execute("BEGIN TRANSACTION")
        
        cursor.execute(
            """
            INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
            VALUES ('Rollback', 'User', 'rollback.user@example.com', 'IT', 70000.00, CURRENT_DATE())
            """
        )
        print("   ✅ Inserted rollback employee")
        
        # Rollback
        conn.rollback()
        print("   ⏪ Transaction rolled back")
        
        # Verify rollback worked
        cursor.execute("SELECT COUNT(*) FROM employees WHERE last_name = 'User'")
        count = cursor.fetchone()[0]
        print(f"\n📊 Employees with last name 'User': {count}")
        print("   (Should be 1 - Test User only, Rollback User was rolled back)")
        
        cursor.close()
        
    finally:
        conn.close()


def cleanup():
    """Cleanup: Drop created objects (optional)"""
    print("\n" + "="*60)
    print("CLEANUP (Optional)")
    print("="*60)
    
    response = input("\nDo you want to drop the created database? (yes/no): ")
    
    if response.lower() == 'yes':
        ops = SnowflakeBasicOperations()
        try:
            ops.execute(
                "DROP DATABASE IF EXISTS LEARNING_DB",
                "Dropping database"
            )
            print("\n✅ Database dropped successfully!")
        finally:
            ops.close()
    else:
        print("\n📊 Database kept for further exploration")


def main():
    """Run all examples"""
    print("\n🎓 SNOWFLAKE BASIC OPERATIONS (CRUD)")
    print("=" * 60)
    
    try:
        example_1_create_database_schema()
        example_2_create_table()
        example_3_insert_data()
        example_4_read_data()
        example_5_update_data()
        example_6_delete_data()
        example_7_transactions()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
        # Optional cleanup
        cleanup()
        
        print("\n📚 Next Steps:")
        print("   1. Explore data loading in 03_data_loading.py")
        print("   2. Practice complex queries in 04_simple_queries.py")
        print("   3. Learn about Snowflake data types and constraints")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
