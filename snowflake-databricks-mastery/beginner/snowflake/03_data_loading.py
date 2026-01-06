"""
Snowflake Data Loading Examples
================================

This script demonstrates:
1. Loading CSV files into Snowflake
2. Loading JSON files
3. Loading Parquet files
4. Using file formats
5. Using internal and external stages
6. COPY INTO command
7. Bulk loading best practices

Prerequisites:
- Completed 01_setup_connection.py and 02_basic_operations.py
- Sample data files in data directory
"""

import os
from dotenv import load_dotenv
import snowflake.connector
from pathlib import Path

# Load environment variables
load_dotenv()


class SnowflakeDataLoader:
    """Manages data loading operations in Snowflake"""
    
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
        
        # Setup database and schema
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS DATA_LOADING_DB")
        self.cursor.execute("USE DATABASE DATA_LOADING_DB")
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS DEMO")
        self.cursor.execute("USE SCHEMA DEMO")
    
    def execute(self, query: str, description: str = ""):
        """Execute a query and print results"""
        try:
            if description:
                print(f"\n📝 {description}")
            
            self.cursor.execute(query)
            
            if self.cursor.description:
                results = self.cursor.fetchall()
                if results:
                    print(f"   ✅ Returned {len(results)} rows")
                    return results
            else:
                print("   ✅ Query executed successfully")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
    
    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()


def example_1_create_file_format():
    """Example 1: Create file formats for different data types"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Create File Formats")
    print("="*60)
    
    loader = SnowflakeDataLoader()
    
    try:
        # CSV file format
        loader.execute(
            """
            CREATE OR REPLACE FILE FORMAT csv_format
            TYPE = 'CSV'
            FIELD_DELIMITER = ','
            SKIP_HEADER = 1
            NULL_IF = ('NULL', 'null', '')
            EMPTY_FIELD_AS_NULL = TRUE
            COMPRESSION = AUTO
            """,
            "Creating CSV file format"
        )
        
        # JSON file format
        loader.execute(
            """
            CREATE OR REPLACE FILE FORMAT json_format
            TYPE = 'JSON'
            COMPRESSION = AUTO
            """,
            "Creating JSON file format"
        )
        
        # Parquet file format
        loader.execute(
            """
            CREATE OR REPLACE FILE FORMAT parquet_format
            TYPE = 'PARQUET'
            COMPRESSION = AUTO
            """,
            "Creating Parquet file format"
        )
        
        # Show file formats
        results = loader.execute(
            "SHOW FILE FORMATS",
            "Listing file formats"
        )
        
        print("\n📊 File formats created successfully!")
        
    finally:
        loader.close()


def example_2_create_stage():
    """Example 2: Create internal stages"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Create Stages")
    print("="*60)
    
    loader = SnowflakeDataLoader()
    
    try:
        # Create internal named stage
        loader.execute(
            """
            CREATE OR REPLACE STAGE my_csv_stage
            FILE_FORMAT = csv_format
            """,
            "Creating CSV stage"
        )
        
        loader.execute(
            """
            CREATE OR REPLACE STAGE my_json_stage
            FILE_FORMAT = json_format
            """,
            "Creating JSON stage"
        )
        
        # Show stages
        results = loader.execute(
            "SHOW STAGES",
            "Listing stages"
        )
        
        print("\n📊 Stages created successfully!")
        
    finally:
        loader.close()


def example_3_load_csv():
    """Example 3: Load CSV file into Snowflake"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Load CSV Data")
    print("="*60)
    
    loader = SnowflakeDataLoader()
    
    try:
        # Create target table
        loader.execute(
            """
            CREATE OR REPLACE TABLE employees (
                id INTEGER,
                name VARCHAR(100),
                department VARCHAR(50),
                salary NUMBER(10, 2),
                hire_date DATE,
                is_active BOOLEAN
            )
            """,
            "Creating employees table"
        )
        
        # Get path to sample CSV file
        csv_file = Path(__file__).parent.parent.parent / "data/sample_csv/employees.csv"
        
        if not csv_file.exists():
            print(f"   ⚠️  Sample file not found: {csv_file}")
            print("   Creating sample data instead...")
            
            # Insert sample data directly
            loader.execute(
                """
                INSERT INTO employees VALUES
                (1, 'John Doe', 'Engineering', 95000.00, '2023-01-15', TRUE),
                (2, 'Jane Smith', 'Engineering', 105000.00, '2023-02-01', TRUE),
                (3, 'Bob Johnson', 'Sales', 75000.00, '2023-03-10', TRUE)
                """,
                "Inserting sample data"
            )
        else:
            # Upload file to stage
            print(f"\n📤 Uploading {csv_file} to stage...")
            loader.execute(
                f"PUT file://{csv_file} @my_csv_stage AUTO_COMPRESS=TRUE",
                "Uploading CSV file to stage"
            )
            
            # Copy data from stage to table
            loader.execute(
                """
                COPY INTO employees
                FROM @my_csv_stage/employees.csv.gz
                FILE_FORMAT = csv_format
                ON_ERROR = 'CONTINUE'
                """,
                "Loading data from stage to table"
            )
        
        # Verify data
        print("\n📊 Loaded Data:")
        results = loader.execute("SELECT * FROM employees LIMIT 5")
        for row in results:
            print(f"   {row}")
        
        # Count rows
        results = loader.execute("SELECT COUNT(*) FROM employees")
        print(f"\n📊 Total rows loaded: {results[0][0]}")
        
    finally:
        loader.close()


def example_4_load_json():
    """Example 4: Load JSON data into Snowflake"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Load JSON Data")
    print("="*60)
    
    loader = SnowflakeDataLoader()
    
    try:
        # Create table with VARIANT column for JSON
        loader.execute(
            """
            CREATE OR REPLACE TABLE products_raw (
                json_data VARIANT
            )
            """,
            "Creating table for raw JSON data"
        )
        
        # Insert sample JSON data directly
        loader.execute(
            """
            INSERT INTO products_raw
            SELECT PARSE_JSON('{
                "product_id": 1,
                "product_name": "Laptop Pro 15",
                "category": "Electronics",
                "price": 1299.99,
                "specifications": {
                    "brand": "TechCorp",
                    "ram": "16GB",
                    "storage": "512GB SSD"
                }
            }')
            """,
            "Inserting sample JSON"
        )
        
        # Query JSON data
        print("\n📊 Querying JSON Data:")
        results = loader.execute(
            """
            SELECT 
                json_data:product_id::INTEGER as product_id,
                json_data:product_name::STRING as product_name,
                json_data:category::STRING as category,
                json_data:price::FLOAT as price,
                json_data:specifications.brand::STRING as brand,
                json_data:specifications.ram::STRING as ram
            FROM products_raw
            """
        )
        for row in results:
            print(f"   {row}")
        
    finally:
        loader.close()


def example_5_bulk_loading():
    """Example 5: Bulk loading with multiple files"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Bulk Loading")
    print("="*60)
    
    loader = SnowflakeDataLoader()
    
    try:
        # Create table for bulk loading
        loader.execute(
            """
            CREATE OR REPLACE TABLE sales_data (
                transaction_id INTEGER,
                customer_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                amount FLOAT,
                transaction_date DATE
            )
            """,
            "Creating sales_data table"
        )
        
        # Insert sample bulk data
        loader.execute(
            """
            INSERT INTO sales_data
            SELECT 
                ROW_NUMBER() OVER (ORDER BY SEQ4()) as transaction_id,
                UNIFORM(1, 1000, RANDOM()) as customer_id,
                UNIFORM(1, 100, RANDOM()) as product_id,
                UNIFORM(1, 10, RANDOM()) as quantity,
                UNIFORM(10, 1000, RANDOM()) as amount,
                DATEADD(day, -UNIFORM(1, 365, RANDOM()), CURRENT_DATE()) as transaction_date
            FROM TABLE(GENERATOR(ROWCOUNT => 1000))
            """,
            "Generating 1000 sample transactions"
        )
        
        # Verify data
        results = loader.execute("SELECT COUNT(*) FROM sales_data")
        print(f"\n📊 Total rows: {results[0][0]}")
        
        # Show sample data
        print("\n📊 Sample Data:")
        results = loader.execute("SELECT * FROM sales_data LIMIT 5")
        for row in results:
            print(f"   {row}")
        
        # Aggregate statistics
        print("\n📊 Sales Statistics:")
        results = loader.execute(
            """
            SELECT 
                COUNT(*) as total_transactions,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_transaction,
                MAX(amount) as max_transaction
            FROM sales_data
            """
        )
        for row in results:
            print(f"   Transactions: {row[0]}")
            print(f"   Total Revenue: ${row[1]:,.2f}")
            print(f"   Avg Transaction: ${row[2]:,.2f}")
            print(f"   Max Transaction: ${row[3]:,.2f}")
        
    finally:
        loader.close()


def example_6_data_validation():
    """Example 6: Data validation after loading"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Data Validation")
    print("="*60)
    
    loader = SnowflakeDataLoader()
    
    try:
        # Check for NULL values
        print("\n📊 Checking for NULL values:")
        results = loader.execute(
            """
            SELECT 
                COUNT(*) as total_rows,
                SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) as null_ids,
                SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END) as null_names,
                SUM(CASE WHEN salary IS NULL THEN 1 ELSE 0 END) as null_salaries
            FROM employees
            """
        )
        for row in results:
            print(f"   Total Rows: {row[0]}")
            print(f"   NULL IDs: {row[1]}")
            print(f"   NULL Names: {row[2]}")
            print(f"   NULL Salaries: {row[3]}")
        
        # Check for duplicates
        print("\n📊 Checking for duplicates:")
        results = loader.execute(
            """
            SELECT id, COUNT(*) as count
            FROM employees
            GROUP BY id
            HAVING COUNT(*) > 1
            """
        )
        if results:
            print("   ⚠️  Found duplicates!")
            for row in results:
                print(f"   ID {row[0]}: {row[1]} occurrences")
        else:
            print("   ✅ No duplicates found")
        
        # Data quality checks
        print("\n📊 Data Quality Checks:")
        results = loader.execute(
            """
            SELECT 
                COUNT(*) as total,
                MIN(salary) as min_salary,
                MAX(salary) as max_salary,
                AVG(salary) as avg_salary
            FROM employees
            WHERE is_active = TRUE
            """
        )
        for row in results:
            print(f"   Active Employees: {row[0]}")
            print(f"   Salary Range: ${row[1]:,.2f} - ${row[2]:,.2f}")
            print(f"   Average Salary: ${row[3]:,.2f}")
        
    finally:
        loader.close()


def cleanup():
    """Cleanup: Drop created objects"""
    print("\n" + "="*60)
    print("CLEANUP (Optional)")
    print("="*60)
    
    response = input("\nDo you want to drop the created database? (yes/no): ")
    
    if response.lower() == 'yes':
        loader = SnowflakeDataLoader()
        try:
            loader.execute(
                "DROP DATABASE IF EXISTS DATA_LOADING_DB",
                "Dropping database"
            )
            print("\n✅ Database dropped successfully!")
        finally:
            loader.close()
    else:
        print("\n📊 Database kept for further exploration")


def main():
    """Run all examples"""
    print("\n🎓 SNOWFLAKE DATA LOADING EXAMPLES")
    print("=" * 60)
    
    try:
        example_1_create_file_format()
        example_2_create_stage()
        example_3_load_csv()
        example_4_load_json()
        example_5_bulk_loading()
        example_6_data_validation()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
        # Optional cleanup
        cleanup()
        
        print("\n📚 Next Steps:")
        print("   1. Practice with your own data files")
        print("   2. Explore 04_simple_queries.py for query examples")
        print("   3. Learn about external stages (S3, Azure, GCS)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
