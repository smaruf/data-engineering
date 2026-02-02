"""
Azure SQL Database Connector

This module demonstrates connecting to and working with Azure SQL Database
using Python. Covers connection management, queries, parameterized queries,
and best practices.

Requirements:
    pip install pyodbc azure-identity

Environment Variables:
    AZURE_SQL_SERVER: Azure SQL server name (e.g., myserver.database.windows.net)
    AZURE_SQL_DATABASE: Database name
    AZURE_SQL_USER: SQL authentication username
    AZURE_SQL_PASSWORD: SQL authentication password
    
Note:
    For Windows, you may need to install ODBC Driver:
    https://docs.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import pyodbc
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureSQLConnector:
    """
    Manages connections and operations with Azure SQL Database.
    
    Supports both SQL authentication and Azure AD authentication.
    Includes connection pooling, parameterized queries, and transaction management.
    """
    
    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_azure_ad: bool = False,
        driver: str = "{ODBC Driver 17 for SQL Server}"
    ):
        """
        Initialize Azure SQL connector.
        
        Args:
            server: SQL server name (e.g., myserver.database.windows.net)
            database: Database name
            username: SQL username (not needed for Azure AD auth)
            password: SQL password (not needed for Azure AD auth)
            use_azure_ad: Use Azure AD authentication instead of SQL auth
            driver: ODBC driver name
        """
        self.server = server or os.getenv('AZURE_SQL_SERVER')
        self.database = database or os.getenv('AZURE_SQL_DATABASE')
        self.username = username or os.getenv('AZURE_SQL_USER')
        self.password = password or os.getenv('AZURE_SQL_PASSWORD')
        self.use_azure_ad = use_azure_ad
        self.driver = driver
        
        if not all([self.server, self.database]):
            raise ValueError(
                "Server and database must be provided or set in environment variables: "
                "AZURE_SQL_SERVER, AZURE_SQL_DATABASE"
            )
        
        if not use_azure_ad and not all([self.username, self.password]):
            raise ValueError(
                "Username and password required for SQL authentication. "
                "Set AZURE_SQL_USER and AZURE_SQL_PASSWORD or use use_azure_ad=True"
            )
        
        self.connection_string = self._build_connection_string()
        logger.info(f"Initialized connector for: {self.server}/{self.database}")
        logger.info(f"Authentication method: {'Azure AD' if use_azure_ad else 'SQL'}")
    
    def _build_connection_string(self) -> str:
        """
        Build ODBC connection string.
        
        Returns:
            Connection string
        """
        if self.use_azure_ad:
            # Azure AD authentication
            return (
                f"Driver={self.driver};"
                f"Server=tcp:{self.server},1433;"
                f"Database={self.database};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30;"
                f"Authentication=ActiveDirectoryInteractive"
            )
        else:
            # SQL authentication
            return (
                f"Driver={self.driver};"
                f"Server=tcp:{self.server},1433;"
                f"Database={self.database};"
                f"Uid={self.username};"
                f"Pwd={self.password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
                f"Connection Timeout=30"
            )
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            Database connection
        
        Example:
            with connector.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = None
        try:
            logger.debug("Establishing database connection...")
            conn = pyodbc.connect(self.connection_string)
            logger.debug("Connection established")
            yield conn
        except pyodbc.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Connection closed")
    
    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> Optional[List[Tuple]]:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Optional query parameters for parameterized queries
            fetch: Whether to fetch and return results
        
        Returns:
            List of result rows if fetch=True, None otherwise
        
        Example:
            results = connector.execute_query(
                "SELECT * FROM users WHERE age > ?",
                params=(18,)
            )
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    logger.debug(f"Executing query with params: {query[:100]}...")
                    cursor.execute(query, params)
                else:
                    logger.debug(f"Executing query: {query[:100]}...")
                    cursor.execute(query)
                
                if fetch:
                    results = cursor.fetchall()
                    logger.info(f"Query returned {len(results)} rows")
                    return results
                else:
                    conn.commit()
                    logger.info(f"Query executed, {cursor.rowcount} rows affected")
                    return None
                    
        except pyodbc.Error as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def execute_many(
        self,
        query: str,
        params_list: List[Tuple]
    ) -> int:
        """
        Execute a query multiple times with different parameters.
        
        Useful for bulk inserts.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        
        Returns:
            Number of rows affected
        
        Example:
            connector.execute_many(
                "INSERT INTO users (name, age) VALUES (?, ?)",
                [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
            )
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                logger.debug(f"Executing batch query: {query[:100]}...")
                cursor.executemany(query, params_list)
                conn.commit()
                
                rows_affected = cursor.rowcount
                logger.info(f"Batch executed, {rows_affected} rows affected")
                return rows_affected
                
        except pyodbc.Error as e:
            logger.error(f"Batch execution error: {e}")
            raise
    
    def fetch_as_dict(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Optional query parameters
        
        Returns:
            List of dictionaries with column names as keys
        
        Example:
            results = connector.fetch_as_dict("SELECT id, name FROM users")
            # [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Get column names
                columns = [column[0] for column in cursor.description]
                
                # Convert rows to dictionaries
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                logger.info(f"Query returned {len(results)} rows")
                return results
                
        except pyodbc.Error as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        drop_if_exists: bool = False
    ) -> None:
        """
        Create a table.
        
        Args:
            table_name: Name of the table
            columns: Dictionary of column name -> column definition
            drop_if_exists: Whether to drop table if it exists
        
        Example:
            connector.create_table(
                "users",
                {
                    "id": "INT PRIMARY KEY IDENTITY(1,1)",
                    "name": "NVARCHAR(100) NOT NULL",
                    "email": "NVARCHAR(255) UNIQUE",
                    "created_at": "DATETIME2 DEFAULT GETDATE()"
                }
            )
        """
        try:
            if drop_if_exists:
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                self.execute_query(drop_query, fetch=False)
                logger.info(f"Dropped table if existed: {table_name}")
            
            column_defs = ", ".join([f"{name} {definition}" 
                                    for name, definition in columns.items()])
            
            create_query = f"CREATE TABLE {table_name} ({column_defs})"
            
            self.execute_query(create_query, fetch=False)
            logger.info(f"Created table: {table_name}")
            
        except pyodbc.Error as e:
            logger.error(f"Table creation error: {e}")
            raise
    
    def insert_data(
        self,
        table_name: str,
        data: List[Dict[str, Any]]
    ) -> int:
        """
        Insert multiple rows into a table.
        
        Args:
            table_name: Name of the table
            data: List of dictionaries with column names and values
        
        Returns:
            Number of rows inserted
        
        Example:
            connector.insert_data(
                "users",
                [
                    {"name": "Alice", "email": "alice@example.com"},
                    {"name": "Bob", "email": "bob@example.com"}
                ]
            )
        """
        if not data:
            logger.warning("No data to insert")
            return 0
        
        # Get column names from first row
        columns = list(data[0].keys())
        column_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))
        
        query = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
        
        # Convert dict rows to tuples
        params_list = [tuple(row[col] for col in columns) for row in data]
        
        return self.execute_many(query, params_list)
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table
        
        Returns:
            True if table exists, False otherwise
        """
        query = """
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = ?
        """
        
        result = self.execute_query(query, params=(table_name,))
        return result[0][0] > 0 if result else False
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of column information dictionaries
        """
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """
        
        return self.fetch_as_dict(query, params=(table_name,))


def main():
    """
    Main function demonstrating Azure SQL Database operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure SQL Database Example")
        logger.info("=" * 60)
        
        # Initialize connector
        # Note: Update these with your Azure SQL details
        connector = AzureSQLConnector(
            # server="your-server.database.windows.net",
            # database="your-database",
            # username="your-username",
            # password="your-password"
        )
        
        table_name = "demo_users"
        
        # Create table
        logger.info("\n--- Creating Table ---")
        connector.create_table(
            table_name=table_name,
            columns={
                "id": "INT PRIMARY KEY IDENTITY(1,1)",
                "name": "NVARCHAR(100) NOT NULL",
                "email": "NVARCHAR(255) UNIQUE",
                "age": "INT",
                "created_at": "DATETIME2 DEFAULT GETDATE()"
            },
            drop_if_exists=True
        )
        
        # Insert data
        logger.info("\n--- Inserting Data ---")
        users_data = [
            {"name": "Alice Johnson", "email": "alice@example.com", "age": 30},
            {"name": "Bob Smith", "email": "bob@example.com", "age": 25},
            {"name": "Charlie Brown", "email": "charlie@example.com", "age": 35},
            {"name": "Diana Prince", "email": "diana@example.com", "age": 28}
        ]
        
        rows_inserted = connector.insert_data(table_name, users_data)
        logger.info(f"Inserted {rows_inserted} rows")
        
        # Query data
        logger.info("\n--- Querying Data ---")
        results = connector.fetch_as_dict(f"SELECT * FROM {table_name}")
        for row in results:
            logger.info(f"  {row}")
        
        # Parameterized query
        logger.info("\n--- Parameterized Query ---")
        results = connector.fetch_as_dict(
            f"SELECT * FROM {table_name} WHERE age > ?",
            params=(28,)
        )
        logger.info(f"Users older than 28:")
        for row in results:
            logger.info(f"  {row['name']} - {row['age']} years old")
        
        # Get table schema
        logger.info("\n--- Table Schema ---")
        schema = connector.get_table_schema(table_name)
        for column in schema:
            logger.info(f"  {column}")
        
        # Cleanup (commented out for safety)
        # logger.info("\n--- Cleanup ---")
        # connector.execute_query(f"DROP TABLE {table_name}", fetch=False)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up: DROP TABLE {table_name}")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
