"""
Microsoft Fabric Data Warehouse Tables Module

This module demonstrates creating tables, loading data, and managing
warehouse objects using T-SQL and Python.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from typing import Optional, List, Dict, Any
import pyodbc
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class WarehouseTableManager:
    """
    Manager for Fabric Data Warehouse tables and schemas.
    
    Note: This requires SQL connection via ODBC driver or SQL endpoints.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize Warehouse Table Manager.
        
        Args:
            connection_string (str): SQL connection string
        """
        self.connection_string = connection_string
        logger.info("Initialized WarehouseTableManager")
    
    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> bool:
        """
        Execute SQL statement.
        
        Args:
            sql (str): SQL statement
            params (tuple, optional): Parameters for parameterized query
        
        Returns:
            bool: True if successful
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to execute SQL: {e}")
            raise
    
    def query_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            sql (str): SELECT query
        
        Returns:
            pd.DataFrame: Query results
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                df = pd.read_sql(sql, conn)
            logger.info(f"Query returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Failed to query SQL: {e}")
            raise
    
    def create_schema(self, schema_name: str) -> bool:
        """Create a schema."""
        sql = f"CREATE SCHEMA [{schema_name}]"
        logger.info(f"Creating schema: {schema_name}")
        return self.execute_sql(sql)
    
    def create_table(self, table_name: str, columns: Dict[str, str], schema: str = "dbo") -> bool:
        """
        Create a table.
        
        Args:
            table_name (str): Table name
            columns (dict): Column definitions {col_name: data_type}
            schema (str): Schema name
        
        Example:
            >>> manager.create_table("customers", {
            ...     "customer_id": "INT PRIMARY KEY",
            ...     "name": "NVARCHAR(100)",
            ...     "email": "NVARCHAR(100)"
            ... })
        """
        column_defs = ", ".join([f"[{col}] {dtype}" for col, dtype in columns.items()])
        sql = f"CREATE TABLE [{schema}].[{table_name}] ({column_defs})"
        logger.info(f"Creating table: {schema}.{table_name}")
        return self.execute_sql(sql)
    
    def insert_dataframe(self, df: pd.DataFrame, table_name: str, schema: str = "dbo") -> bool:
        """
        Insert DataFrame into table.
        
        Args:
            df (pd.DataFrame): Data to insert
            table_name (str): Target table
            schema (str): Schema name
        
        Returns:
            bool: True if successful
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Prepare INSERT statement
                columns = ", ".join([f"[{col}]" for col in df.columns])
                placeholders = ", ".join(["?" for _ in df.columns])
                sql = f"INSERT INTO [{schema}].[{table_name}] ({columns}) VALUES ({placeholders})"
                
                # Insert rows
                for _, row in df.iterrows():
                    cursor.execute(sql, tuple(row))
                
                conn.commit()
                logger.info(f"Inserted {len(df)} rows into {schema}.{table_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            raise


def create_sample_warehouse_objects():
    """
    Create sample warehouse objects (schemas, tables, data).
    
    This function demonstrates typical warehouse patterns.
    """
    print("Sample Warehouse Schema Creation")
    print("=" * 60)
    
    # Sample T-SQL scripts
    print("\n1. Create Schemas")
    print("-" * 60)
    print("""
    -- Create schemas for organizing warehouse objects
    CREATE SCHEMA [staging];
    CREATE SCHEMA [dw];
    CREATE SCHEMA [reporting];
    """)
    
    print("\n2. Create Dimension Tables")
    print("-" * 60)
    print("""
    -- Customer Dimension
    CREATE TABLE [dw].[DimCustomer] (
        CustomerKey INT IDENTITY(1,1) PRIMARY KEY,
        CustomerID NVARCHAR(50) NOT NULL,
        CustomerName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(100),
        Country NVARCHAR(50),
        EffectiveDate DATE NOT NULL,
        ExpirationDate DATE,
        IsCurrent BIT NOT NULL,
        CONSTRAINT UQ_Customer UNIQUE (CustomerID, EffectiveDate)
    );
    
    -- Product Dimension
    CREATE TABLE [dw].[DimProduct] (
        ProductKey INT IDENTITY(1,1) PRIMARY KEY,
        ProductID NVARCHAR(50) NOT NULL,
        ProductName NVARCHAR(100) NOT NULL,
        Category NVARCHAR(50),
        SubCategory NVARCHAR(50),
        UnitPrice DECIMAL(10,2),
        CONSTRAINT UQ_Product UNIQUE (ProductID)
    );
    
    -- Date Dimension
    CREATE TABLE [dw].[DimDate] (
        DateKey INT PRIMARY KEY,
        Date DATE NOT NULL,
        Year INT NOT NULL,
        Quarter INT NOT NULL,
        Month INT NOT NULL,
        MonthName NVARCHAR(20),
        Day INT NOT NULL,
        DayOfWeek INT NOT NULL,
        DayName NVARCHAR(20),
        IsWeekend BIT NOT NULL,
        IsHoliday BIT NOT NULL
    );
    """)
    
    print("\n3. Create Fact Tables")
    print("-" * 60)
    print("""
    -- Sales Fact Table
    CREATE TABLE [dw].[FactSales] (
        SalesKey BIGINT IDENTITY(1,1) PRIMARY KEY,
        DateKey INT NOT NULL,
        CustomerKey INT NOT NULL,
        ProductKey INT NOT NULL,
        OrderID NVARCHAR(50) NOT NULL,
        Quantity INT NOT NULL,
        UnitPrice DECIMAL(10,2) NOT NULL,
        TotalAmount DECIMAL(12,2) NOT NULL,
        CONSTRAINT FK_Sales_Date FOREIGN KEY (DateKey) REFERENCES [dw].[DimDate](DateKey),
        CONSTRAINT FK_Sales_Customer FOREIGN KEY (CustomerKey) REFERENCES [dw].[DimCustomer](CustomerKey),
        CONSTRAINT FK_Sales_Product FOREIGN KEY (ProductKey) REFERENCES [dw].[DimProduct](ProductKey)
    );
    
    -- Create columnstore index for analytics performance
    CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales ON [dw].[FactSales];
    """)
    
    print("\n4. Create Views")
    print("-" * 60)
    print("""
    -- Sales summary view
    CREATE VIEW [reporting].[vw_SalesSummary] AS
    SELECT 
        d.Year,
        d.MonthName,
        c.CustomerName,
        p.ProductName,
        p.Category,
        SUM(f.Quantity) AS TotalQuantity,
        SUM(f.TotalAmount) AS TotalRevenue
    FROM [dw].[FactSales] f
    INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
    INNER JOIN [dw].[DimCustomer] c ON f.CustomerKey = c.CustomerKey
    INNER JOIN [dw].[DimProduct] p ON f.ProductKey = p.ProductKey
    WHERE c.IsCurrent = 1
    GROUP BY d.Year, d.MonthName, c.CustomerName, p.ProductName, p.Category;
    """)


def main():
    """
    Example usage of Warehouse Table Manager.
    """
    print("=" * 60)
    print("Microsoft Fabric Data Warehouse Tables Examples")
    print("=" * 60)
    
    # Show sample warehouse patterns
    create_sample_warehouse_objects()
    
    print("\n5. Data Loading Patterns")
    print("-" * 60)
    print("""
    -- Load data from Lakehouse to Warehouse
    INSERT INTO [dw].[FactSales] (DateKey, CustomerKey, ProductKey, OrderID, Quantity, UnitPrice, TotalAmount)
    SELECT 
        CAST(FORMAT(order_date, 'yyyyMMdd') AS INT) AS DateKey,
        c.CustomerKey,
        p.ProductKey,
        s.order_id,
        s.quantity,
        s.price,
        s.quantity * s.price AS TotalAmount
    FROM [lakehouse].[sales_data] s
    INNER JOIN [dw].[DimCustomer] c ON s.customer_id = c.CustomerID AND c.IsCurrent = 1
    INNER JOIN [dw].[DimProduct] p ON s.product_id = p.ProductID;
    """)
    
    print("\n6. Slowly Changing Dimension (SCD Type 2)")
    print("-" * 60)
    print("""
    -- Update existing customer and create new version
    -- Step 1: Expire current record
    UPDATE [dw].[DimCustomer]
    SET ExpirationDate = GETDATE(), IsCurrent = 0
    WHERE CustomerID = 'CUST001' AND IsCurrent = 1;
    
    -- Step 2: Insert new version
    INSERT INTO [dw].[DimCustomer] (CustomerID, CustomerName, Email, Country, EffectiveDate, ExpirationDate, IsCurrent)
    VALUES ('CUST001', 'John Doe Jr.', 'john.jr@example.com', 'USA', GETDATE(), NULL, 1);
    """)
    
    print("\n" + "=" * 60)
    print("Warehouse tables examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
