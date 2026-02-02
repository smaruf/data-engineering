"""
Azure Synapse Analytics Basics

This module demonstrates connecting to Azure Synapse Analytics (formerly SQL DW)
and performing basic operations like creating tables, loading data, and queries.

Requirements:
    pip install pyodbc azure-identity

Environment Variables:
    AZURE_SYNAPSE_SERVER: Synapse workspace SQL endpoint
    AZURE_SYNAPSE_DATABASE: Database name (usually SQL pool name)
    AZURE_SYNAPSE_USER: SQL authentication username
    AZURE_SYNAPSE_PASSWORD: SQL authentication password
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import pyodbc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureSynapseConnector:
    """
    Manages connections and operations with Azure Synapse Analytics.
    
    Synapse Analytics is Azure's analytics service that brings together
    enterprise data warehousing and Big Data analytics.
    """
    
    def __init__(
        self,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "{ODBC Driver 17 for SQL Server}"
    ):
        """
        Initialize Synapse connector.
        
        Args:
            server: Synapse SQL endpoint (e.g., myworkspace-ondemand.sql.azuresynapse.net)
            database: Database/SQL pool name
            username: SQL username
            password: SQL password
            driver: ODBC driver name
        """
        self.server = server or os.getenv('AZURE_SYNAPSE_SERVER')
        self.database = database or os.getenv('AZURE_SYNAPSE_DATABASE')
        self.username = username or os.getenv('AZURE_SYNAPSE_USER')
        self.password = password or os.getenv('AZURE_SYNAPSE_PASSWORD')
        self.driver = driver
        
        if not all([self.server, self.database, self.username, self.password]):
            raise ValueError(
                "Server, database, username, and password must be provided or set in environment: "
                "AZURE_SYNAPSE_SERVER, AZURE_SYNAPSE_DATABASE, AZURE_SYNAPSE_USER, AZURE_SYNAPSE_PASSWORD"
            )
        
        self.connection_string = self._build_connection_string()
        logger.info(f"Initialized connector for: {self.server}/{self.database}")
    
    def _build_connection_string(self) -> str:
        """Build ODBC connection string for Synapse."""
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
        """
        conn = None
        try:
            logger.debug("Establishing Synapse connection...")
            conn = pyodbc.connect(self.connection_string)
            logger.debug("Connection established")
            yield conn
        except pyodbc.Error as e:
            logger.error(f"Connection error: {e}")
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
            params: Optional query parameters
            fetch: Whether to fetch and return results
        
        Returns:
            List of result rows if fetch=True, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
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
    
    def create_table_with_distribution(
        self,
        table_name: str,
        columns: Dict[str, str],
        distribution: str = "ROUND_ROBIN",
        distribution_column: Optional[str] = None,
        clustered_index: Optional[List[str]] = None,
        drop_if_exists: bool = False
    ) -> None:
        """
        Create a table with Synapse-specific distribution options.
        
        Args:
            table_name: Name of the table
            columns: Dictionary of column name -> column definition
            distribution: Distribution type (ROUND_ROBIN, HASH, REPLICATE)
            distribution_column: Column for HASH distribution
            clustered_index: Columns for clustered columnstore index
            drop_if_exists: Whether to drop table if exists
        
        Example:
            connector.create_table_with_distribution(
                "sales_fact",
                {
                    "sale_id": "BIGINT NOT NULL",
                    "product_id": "INT NOT NULL",
                    "sale_date": "DATE",
                    "amount": "DECIMAL(18,2)"
                },
                distribution="HASH",
                distribution_column="sale_id",
                clustered_index=["sale_date"]
            )
        """
        try:
            if drop_if_exists:
                drop_query = f"DROP TABLE IF EXISTS {table_name}"
                self.execute_query(drop_query, fetch=False)
            
            # Build column definitions
            column_defs = ", ".join([f"{name} {definition}" 
                                    for name, definition in columns.items()])
            
            # Build distribution clause
            if distribution == "HASH":
                if not distribution_column:
                    raise ValueError("distribution_column required for HASH distribution")
                dist_clause = f"DISTRIBUTION = HASH({distribution_column})"
            elif distribution == "REPLICATE":
                dist_clause = "DISTRIBUTION = REPLICATE"
            else:  # ROUND_ROBIN
                dist_clause = "DISTRIBUTION = ROUND_ROBIN"
            
            # Build index clause
            if clustered_index:
                index_cols = ", ".join(clustered_index)
                index_clause = f"CLUSTERED COLUMNSTORE INDEX ORDER ({index_cols})"
            else:
                index_clause = "CLUSTERED COLUMNSTORE INDEX"
            
            # Create table
            create_query = f"""
                CREATE TABLE {table_name}
                (
                    {column_defs}
                )
                WITH
                (
                    {dist_clause},
                    {index_clause}
                )
            """
            
            self.execute_query(create_query, fetch=False)
            logger.info(f"Created table: {table_name} with {distribution} distribution")
            
        except pyodbc.Error as e:
            logger.error(f"Table creation error: {e}")
            raise
    
    def load_data_from_blob(
        self,
        table_name: str,
        storage_account: str,
        container: str,
        file_path: str,
        file_format: str = "CSV",
        credential_name: Optional[str] = None
    ) -> None:
        """
        Load data from Azure Blob Storage using COPY command.
        
        Args:
            table_name: Target table name
            storage_account: Storage account name
            container: Container name
            file_path: File path in container
            file_format: File format (CSV, PARQUET, ORC)
            credential_name: Database scoped credential name (if required)
        
        Note:
            You may need to create a database scoped credential first for
            accessing private storage accounts.
        """
        try:
            logger.info(f"Loading data into {table_name} from blob storage")
            
            blob_url = f"https://{storage_account}.blob.core.windows.net/{container}/{file_path}"
            
            # Build COPY command
            if credential_name:
                copy_query = f"""
                    COPY INTO {table_name}
                    FROM '{blob_url}'
                    WITH (
                        FILE_TYPE = '{file_format}',
                        CREDENTIAL = (IDENTITY = '{credential_name}'),
                        FIRSTROW = 2
                    )
                """
            else:
                # Use managed identity or public access
                copy_query = f"""
                    COPY INTO {table_name}
                    FROM '{blob_url}'
                    WITH (
                        FILE_TYPE = '{file_format}',
                        FIRSTROW = 2
                    )
                """
            
            self.execute_query(copy_query, fetch=False)
            logger.info(f"Data loaded successfully into {table_name}")
            
        except pyodbc.Error as e:
            logger.error(f"Data load error: {e}")
            raise
    
    def create_external_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        data_source: str,
        file_format: str,
        location: str
    ) -> None:
        """
        Create an external table for querying data in storage.
        
        Args:
            table_name: External table name
            columns: Column definitions
            data_source: External data source name
            file_format: External file format name
            location: Location in the data source
        
        Note:
            Requires pre-created EXTERNAL DATA SOURCE and EXTERNAL FILE FORMAT
        """
        try:
            logger.info(f"Creating external table: {table_name}")
            
            column_defs = ", ".join([f"{name} {definition}" 
                                    for name, definition in columns.items()])
            
            create_query = f"""
                CREATE EXTERNAL TABLE {table_name}
                (
                    {column_defs}
                )
                WITH
                (
                    LOCATION = '{location}',
                    DATA_SOURCE = {data_source},
                    FILE_FORMAT = {file_format}
                )
            """
            
            self.execute_query(create_query, fetch=False)
            logger.info(f"External table created: {table_name}")
            
        except pyodbc.Error as e:
            logger.error(f"External table creation error: {e}")
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
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                columns = [column[0] for column in cursor.description]
                
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                logger.info(f"Query returned {len(results)} rows")
                return results
                
        except pyodbc.Error as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """
        Get statistics about a table.
        
        Args:
            table_name: Table name
        
        Returns:
            Dictionary with table statistics
        """
        query = f"""
            SELECT 
                COUNT(*) as row_count,
                SUM(CASE WHEN DATALENGTH(*) IS NULL THEN 0 ELSE 1 END) as non_null_rows
            FROM {table_name}
        """
        
        result = self.fetch_as_dict(query)
        return result[0] if result else {}
    
    def analyze_query_plan(self, query: str) -> List[Dict[str, Any]]:
        """
        Get execution plan for a query.
        
        Args:
            query: SQL query to analyze
        
        Returns:
            Execution plan details
        """
        explain_query = f"EXPLAIN {query}"
        return self.fetch_as_dict(explain_query)


def main():
    """
    Main function demonstrating Synapse Analytics operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Synapse Analytics Example")
        logger.info("=" * 60)
        
        # Initialize connector
        # Note: Update with your Synapse workspace details
        synapse_connector = AzureSynapseConnector(
            # server="myworkspace-ondemand.sql.azuresynapse.net",
            # database="mysqlpool",
            # username="sqladmin",
            # password="YourPassword123!"
        )
        
        table_name = "demo_sales"
        
        # Create table with distribution
        logger.info("\n--- Creating Distributed Table ---")
        synapse_connector.create_table_with_distribution(
            table_name=table_name,
            columns={
                "sale_id": "BIGINT NOT NULL",
                "customer_id": "INT NOT NULL",
                "product_id": "INT NOT NULL",
                "sale_date": "DATE",
                "quantity": "INT",
                "amount": "DECIMAL(18,2)"
            },
            distribution="HASH",
            distribution_column="sale_id",
            clustered_index=["sale_date"],
            drop_if_exists=True
        )
        
        # Insert sample data
        logger.info("\n--- Inserting Sample Data ---")
        insert_query = f"""
            INSERT INTO {table_name} (sale_id, customer_id, product_id, sale_date, quantity, amount)
            VALUES 
                (1, 101, 1001, '2024-01-01', 2, 99.98),
                (2, 102, 1002, '2024-01-02', 1, 49.99),
                (3, 101, 1003, '2024-01-03', 3, 149.97)
        """
        synapse_connector.execute_query(insert_query, fetch=False)
        
        # Query data
        logger.info("\n--- Querying Data ---")
        results = synapse_connector.fetch_as_dict(f"SELECT * FROM {table_name}")
        for row in results:
            logger.info(f"  Sale {row['sale_id']}: ${row['amount']}")
        
        # Get table statistics
        logger.info("\n--- Table Statistics ---")
        stats = synapse_connector.get_table_statistics(table_name)
        logger.info(f"  Row count: {stats.get('row_count', 0)}")
        
        # Aggregation query
        logger.info("\n--- Aggregation Query ---")
        agg_query = f"""
            SELECT 
                customer_id,
                COUNT(*) as purchase_count,
                SUM(amount) as total_spent
            FROM {table_name}
            GROUP BY customer_id
            ORDER BY total_spent DESC
        """
        results = synapse_connector.fetch_as_dict(agg_query)
        for row in results:
            logger.info(
                f"  Customer {row['customer_id']}: "
                f"{row['purchase_count']} purchases, ${row['total_spent']}"
            )
        
        # Cleanup (commented out for safety)
        # logger.info("\n--- Cleanup ---")
        # synapse_connector.execute_query(f"DROP TABLE {table_name}", fetch=False)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up: DROP TABLE {table_name}")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
