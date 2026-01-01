"""
Snowflake Setup and First Connection
=====================================

This script demonstrates:
1. How to install and setup Snowflake connector
2. How to establish a connection to Snowflake
3. How to execute basic queries
4. How to close connections properly

Prerequisites:
- Snowflake account (free trial available)
- Python 3.8+
- snowflake-connector-python installed
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector import SnowflakeConnection
from snowflake.connector.cursor import SnowflakeCursor

# Load environment variables
load_dotenv()


class SnowflakeConnectionManager:
    """Manages Snowflake database connections"""
    
    def __init__(self):
        """Initialize connection manager with credentials from environment"""
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
        self.database = os.getenv('SNOWFLAKE_DATABASE', 'DEMO_DB')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
        self.role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        self.connection: Optional[SnowflakeConnection] = None
        
    def connect(self) -> SnowflakeConnection:
        """
        Establish connection to Snowflake
        
        Returns:
            SnowflakeConnection: Active Snowflake connection
        """
        try:
            print("🔌 Connecting to Snowflake...")
            
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                role=self.role
            )
            
            print("✅ Successfully connected to Snowflake!")
            print(f"   Account: {self.account}")
            print(f"   Database: {self.database}")
            print(f"   Schema: {self.schema}")
            print(f"   Warehouse: {self.warehouse}")
            
            return self.connection
            
        except Exception as e:
            print(f"❌ Error connecting to Snowflake: {e}")
            raise
    
    def execute_query(self, query: str) -> list:
        """
        Execute a SQL query and return results
        
        Args:
            query: SQL query string
            
        Returns:
            list: Query results
        """
        if not self.connection:
            raise Exception("No active connection. Call connect() first.")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            raise
    
    def close(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Connection closed.")


def example_1_basic_connection():
    """Example 1: Establish a basic connection"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Connection")
    print("="*60)
    
    conn_manager = SnowflakeConnectionManager()
    
    try:
        # Connect to Snowflake
        conn = conn_manager.connect()
        
        # Verify connection
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()
        print(f"\n📊 Snowflake Version: {version[0]}")
        cursor.close()
        
    finally:
        conn_manager.close()


def example_2_check_current_context():
    """Example 2: Check current context (database, schema, warehouse)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Check Current Context")
    print("="*60)
    
    conn_manager = SnowflakeConnectionManager()
    
    try:
        conn_manager.connect()
        
        # Check current database
        result = conn_manager.execute_query("SELECT CURRENT_DATABASE()")
        print(f"\n📊 Current Database: {result[0][0]}")
        
        # Check current schema
        result = conn_manager.execute_query("SELECT CURRENT_SCHEMA()")
        print(f"📊 Current Schema: {result[0][0]}")
        
        # Check current warehouse
        result = conn_manager.execute_query("SELECT CURRENT_WAREHOUSE()")
        print(f"📊 Current Warehouse: {result[0][0]}")
        
        # Check current role
        result = conn_manager.execute_query("SELECT CURRENT_ROLE()")
        print(f"📊 Current Role: {result[0][0]}")
        
        # Check current user
        result = conn_manager.execute_query("SELECT CURRENT_USER()")
        print(f"📊 Current User: {result[0][0]}")
        
    finally:
        conn_manager.close()


def example_3_context_manager():
    """Example 3: Using context manager for automatic connection handling"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Using Context Manager")
    print("="*60)
    
    try:
        # Using context manager (preferred method)
        with snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        ) as conn:
            print("✅ Connected using context manager")
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 'Hello from Snowflake!' as message")
                result = cursor.fetchone()
                print(f"\n📊 Message: {result[0]}")
        
        print("🔌 Connection automatically closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_4_connection_parameters():
    """Example 4: Advanced connection parameters"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Advanced Connection Parameters")
    print("="*60)
    
    try:
        # Connection with additional parameters
        conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA'),
            # Additional parameters
            client_session_keep_alive=True,  # Keep session alive
            autocommit=True,  # Auto-commit transactions
            network_timeout=60,  # Network timeout in seconds
        )
        
        print("✅ Connected with advanced parameters")
        print("   - Session keep-alive: enabled")
        print("   - Autocommit: enabled")
        print("   - Network timeout: 60s")
        
        # Get session info
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                CURRENT_SESSION() as session_id,
                CURRENT_TIMESTAMP() as current_time
        """)
        result = cursor.fetchone()
        print(f"\n📊 Session ID: {result[0]}")
        print(f"📊 Current Time: {result[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_5_error_handling():
    """Example 5: Proper error handling"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Error Handling")
    print("="*60)
    
    conn_manager = SnowflakeConnectionManager()
    
    try:
        conn_manager.connect()
        
        # Try to execute a query with intentional error
        try:
            conn_manager.execute_query("SELECT * FROM non_existent_table")
        except snowflake.connector.errors.ProgrammingError as e:
            print(f"⚠️  Caught expected error: {e}")
            print("   This demonstrates proper error handling")
        
        # Execute a valid query
        result = conn_manager.execute_query("SELECT 1 as test")
        print(f"\n✅ Valid query executed successfully: {result[0][0]}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    finally:
        conn_manager.close()


def verify_environment():
    """Verify that environment variables are set"""
    print("\n" + "="*60)
    print("ENVIRONMENT VERIFICATION")
    print("="*60)
    
    required_vars = [
        'SNOWFLAKE_ACCOUNT',
        'SNOWFLAKE_USER',
        'SNOWFLAKE_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password
            display_value = "****" if 'PASSWORD' in var else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print("\n⚠️  Missing required environment variables!")
        print("   Please set them in your .env file or environment")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True


def main():
    """Run all examples"""
    print("\n" + "🎓 SNOWFLAKE SETUP AND CONNECTION EXAMPLES")
    print("=" * 60)
    
    # Verify environment
    if not verify_environment():
        print("\n❌ Please configure your environment variables before continuing.")
        print("   Copy .env.example to .env and fill in your Snowflake credentials.")
        sys.exit(1)
    
    # Run examples
    try:
        example_1_basic_connection()
        example_2_check_current_context()
        example_3_context_manager()
        example_4_connection_parameters()
        example_5_error_handling()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
        print("\n📚 Next Steps:")
        print("   1. Explore 02_basic_operations.py for CRUD operations")
        print("   2. Learn about data loading in 03_data_loading.py")
        print("   3. Practice SQL queries in 04_simple_queries.py")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
