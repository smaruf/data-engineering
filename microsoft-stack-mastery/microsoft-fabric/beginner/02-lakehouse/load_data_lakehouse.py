"""
Microsoft Fabric Lakehouse Data Loading Module

This module demonstrates loading data from various sources into Fabric Lakehouse
including CSV, Parquet, JSON files, and other formats.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import io

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LakehouseDataLoader:
    """
    Data loader for Microsoft Fabric Lakehouse.
    
    Supports loading data from:
    - Local CSV files
    - Local Parquet files
    - Local JSON files
    - Azure Data Lake Storage Gen2
    - Direct DataFrame upload
    """
    
    def __init__(
        self,
        lakehouse_abfss_path: str,
        credential: Optional[Any] = None
    ):
        """
        Initialize Lakehouse Data Loader.
        
        Args:
            lakehouse_abfss_path (str): ABFSS path to lakehouse
                Format: abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files
            credential (optional): Azure credential for authentication
        
        Example:
            >>> loader = LakehouseDataLoader(
            ...     lakehouse_abfss_path="abfss://myworkspace@onelake.dfs.fabric.microsoft.com/mylakehouse/Files"
            ... )
        """
        self.lakehouse_path = lakehouse_abfss_path
        self.credential = credential or DefaultAzureCredential()
        
        # Parse OneLake path
        self._parse_onelake_path()
        
        logger.info(f"Initialized LakehouseDataLoader for {lakehouse_abfss_path}")
    
    def _parse_onelake_path(self):
        """Parse OneLake ABFSS path to extract components."""
        # abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files
        try:
            path_parts = self.lakehouse_path.replace("abfss://", "").split("@")
            self.workspace_name = path_parts[0]
            
            remaining = path_parts[1].split("/")
            self.account_url = f"https://{remaining[0]}"
            self.lakehouse_name = remaining[1] if len(remaining) > 1 else ""
            
            logger.debug(f"Workspace: {self.workspace_name}, Lakehouse: {self.lakehouse_name}")
        except Exception as e:
            logger.error(f"Failed to parse OneLake path: {e}")
            raise ValueError(f"Invalid OneLake path format: {self.lakehouse_path}")
    
    def _get_datalake_client(self) -> DataLakeServiceClient:
        """
        Get Data Lake service client for OneLake.
        
        Returns:
            DataLakeServiceClient: Authenticated client
        """
        return DataLakeServiceClient(
            account_url=self.account_url,
            credential=self.credential
        )
    
    def load_csv(
        self,
        file_path: str,
        target_path: str,
        **pandas_kwargs
    ) -> bool:
        """
        Load CSV file to lakehouse.
        
        Args:
            file_path (str): Local path to CSV file
            target_path (str): Target path in lakehouse (e.g., "raw/sales/data.csv")
            **pandas_kwargs: Additional arguments for pd.read_csv
        
        Returns:
            bool: True if successful
        
        Example:
            >>> loader.load_csv(
            ...     file_path="local_data.csv",
            ...     target_path="raw/sales/2024_data.csv",
            ...     sep=",",
            ...     encoding="utf-8"
            ... )
        """
        logger.info(f"Loading CSV from {file_path} to {target_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path, **pandas_kwargs)
            logger.info(f"Read {len(df)} rows from CSV")
            
            # Convert to Parquet for efficient storage
            parquet_target = target_path.replace('.csv', '.parquet')
            return self.load_dataframe(df, parquet_target, file_format='parquet')
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise
    
    def load_parquet(
        self,
        file_path: str,
        target_path: str
    ) -> bool:
        """
        Load Parquet file to lakehouse.
        
        Args:
            file_path (str): Local path to Parquet file
            target_path (str): Target path in lakehouse
        
        Returns:
            bool: True if successful
        """
        logger.info(f"Loading Parquet from {file_path} to {target_path}")
        
        try:
            # Read Parquet file
            df = pd.read_parquet(file_path)
            logger.info(f"Read {len(df)} rows from Parquet")
            
            return self.load_dataframe(df, target_path, file_format='parquet')
            
        except Exception as e:
            logger.error(f"Failed to load Parquet: {e}")
            raise
    
    def load_json(
        self,
        file_path: str,
        target_path: str,
        **pandas_kwargs
    ) -> bool:
        """
        Load JSON file to lakehouse.
        
        Args:
            file_path (str): Local path to JSON file
            target_path (str): Target path in lakehouse
            **pandas_kwargs: Additional arguments for pd.read_json
        
        Returns:
            bool: True if successful
        """
        logger.info(f"Loading JSON from {file_path} to {target_path}")
        
        try:
            # Read JSON file
            df = pd.read_json(file_path, **pandas_kwargs)
            logger.info(f"Read {len(df)} rows from JSON")
            
            # Convert to Parquet
            parquet_target = target_path.replace('.json', '.parquet')
            return self.load_dataframe(df, parquet_target, file_format='parquet')
            
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            raise
    
    def load_dataframe(
        self,
        df: pd.DataFrame,
        target_path: str,
        file_format: str = 'parquet',
        **format_kwargs
    ) -> bool:
        """
        Load pandas DataFrame to lakehouse.
        
        Args:
            df (pd.DataFrame): DataFrame to load
            target_path (str): Target path in lakehouse
            file_format (str): Output format ('parquet', 'csv', 'json')
            **format_kwargs: Format-specific arguments
        
        Returns:
            bool: True if successful
        
        Example:
            >>> df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
            >>> loader.load_dataframe(df, "processed/data.parquet")
        """
        logger.info(f"Loading DataFrame ({len(df)} rows) to {target_path}")
        
        try:
            client = self._get_datalake_client()
            file_system_client = client.get_file_system_client(self.workspace_name)
            
            # Construct full path
            full_path = f"{self.lakehouse_name}/Files/{target_path}"
            file_client = file_system_client.get_file_client(full_path)
            
            # Convert DataFrame to bytes based on format
            if file_format == 'parquet':
                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False, **format_kwargs)
                data = buffer.getvalue()
            elif file_format == 'csv':
                data = df.to_csv(index=False, **format_kwargs).encode('utf-8')
            elif file_format == 'json':
                data = df.to_json(orient='records', **format_kwargs).encode('utf-8')
            else:
                raise ValueError(f"Unsupported format: {file_format}")
            
            # Upload to OneLake
            file_client.upload_data(data, overwrite=True)
            
            logger.info(f"✅ Successfully loaded {len(df)} rows to {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load DataFrame: {e}")
            raise
    
    def load_bulk_files(
        self,
        source_directory: str,
        target_directory: str,
        file_pattern: str = "*.csv",
        file_format: str = 'parquet'
    ) -> Dict[str, bool]:
        """
        Load multiple files from a directory to lakehouse.
        
        Args:
            source_directory (str): Source directory containing files
            target_directory (str): Target directory in lakehouse
            file_pattern (str): File pattern to match (e.g., "*.csv", "*.parquet")
            file_format (str): Output format
        
        Returns:
            dict: Mapping of file names to success status
        
        Example:
            >>> results = loader.load_bulk_files(
            ...     source_directory="./data/raw/",
            ...     target_directory="raw/sales/",
            ...     file_pattern="*.csv"
            ... )
        """
        import glob
        
        logger.info(f"Loading bulk files from {source_directory} matching {file_pattern}")
        
        results = {}
        files = glob.glob(os.path.join(source_directory, file_pattern))
        
        logger.info(f"Found {len(files)} files to load")
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            target_path = f"{target_directory}/{file_name}"
            
            try:
                if file_pattern.endswith('.csv'):
                    success = self.load_csv(file_path, target_path)
                elif file_pattern.endswith('.parquet'):
                    success = self.load_parquet(file_path, target_path)
                elif file_pattern.endswith('.json'):
                    success = self.load_json(file_path, target_path)
                else:
                    logger.warning(f"Unsupported file type: {file_name}")
                    success = False
                
                results[file_name] = success
                
            except Exception as e:
                logger.error(f"Failed to load {file_name}: {e}")
                results[file_name] = False
        
        successful = sum(1 for v in results.values() if v)
        logger.info(f"✅ Loaded {successful}/{len(files)} files successfully")
        
        return results


def create_sample_data():
    """
    Create sample datasets for demonstration.
    
    Returns:
        dict: Dictionary of sample DataFrames
    """
    logger.info("Creating sample datasets")
    
    # Sample sales data
    sales_data = pd.DataFrame({
        'order_id': range(1, 101),
        'customer_id': [f'CUST{i:04d}' for i in range(1, 101)],
        'product': ['Product A', 'Product B', 'Product C'] * 33 + ['Product A'],
        'quantity': pd.np.random.randint(1, 10, 100),
        'price': pd.np.random.uniform(10.0, 100.0, 100).round(2),
        'order_date': pd.date_range('2024-01-01', periods=100, freq='D')
    })
    
    # Sample customer data
    customer_data = pd.DataFrame({
        'customer_id': [f'CUST{i:04d}' for i in range(1, 51)],
        'name': [f'Customer {i}' for i in range(1, 51)],
        'email': [f'customer{i}@example.com' for i in range(1, 51)],
        'country': ['USA', 'Canada', 'UK', 'Germany', 'France'] * 10,
        'created_date': pd.date_range('2023-01-01', periods=50, freq='W')
    })
    
    # Sample product data
    product_data = pd.DataFrame({
        'product_id': ['PROD001', 'PROD002', 'PROD003'],
        'product_name': ['Product A', 'Product B', 'Product C'],
        'category': ['Electronics', 'Clothing', 'Food'],
        'unit_price': [29.99, 49.99, 9.99],
        'in_stock': [True, True, False]
    })
    
    return {
        'sales': sales_data,
        'customers': customer_data,
        'products': product_data
    }


def main():
    """
    Example usage of Lakehouse Data Loader.
    """
    print("=" * 60)
    print("Microsoft Fabric Lakehouse Data Loading Examples")
    print("=" * 60)
    
    # Configuration
    workspace_name = os.getenv("WORKSPACE_NAME", "myworkspace")
    lakehouse_name = os.getenv("LAKEHOUSE_NAME", "mylakehouse")
    
    lakehouse_path = (
        f"abfss://{workspace_name}@onelake.dfs.fabric.microsoft.com/"
        f"{lakehouse_name}/Files"
    )
    
    try:
        # Initialize loader
        loader = LakehouseDataLoader(lakehouse_path)
        
        # Create sample data
        print("\n1. Creating sample datasets")
        print("-" * 60)
        sample_data = create_sample_data()
        
        for name, df in sample_data.items():
            print(f"✅ Created {name} dataset: {len(df)} rows")
        
        # Example 1: Load sales data as Parquet
        print("\n2. Loading sales data to lakehouse")
        print("-" * 60)
        loader.load_dataframe(
            df=sample_data['sales'],
            target_path="raw/sales/sales_data.parquet",
            file_format='parquet'
        )
        print("✅ Sales data loaded successfully")
        
        # Example 2: Load customer data as CSV
        print("\n3. Loading customer data as CSV")
        print("-" * 60)
        loader.load_dataframe(
            df=sample_data['customers'],
            target_path="raw/customers/customer_data.csv",
            file_format='csv'
        )
        print("✅ Customer data loaded successfully")
        
        # Example 3: Load product data as JSON
        print("\n4. Loading product data as JSON")
        print("-" * 60)
        loader.load_dataframe(
            df=sample_data['products'],
            target_path="raw/products/product_data.json",
            file_format='json'
        )
        print("✅ Product data loaded successfully")
        
        # Example 4: Save sample data locally and load from file
        print("\n5. Loading from local files")
        print("-" * 60)
        
        # Create temp directory
        temp_dir = "temp_data"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save sample data
        sample_data['sales'].to_csv(f"{temp_dir}/sales.csv", index=False)
        sample_data['products'].to_parquet(f"{temp_dir}/products.parquet", index=False)
        
        # Load from files
        loader.load_csv(
            file_path=f"{temp_dir}/sales.csv",
            target_path="raw/sales/sales_from_file.parquet"
        )
        
        loader.load_parquet(
            file_path=f"{temp_dir}/products.parquet",
            target_path="raw/products/products_from_file.parquet"
        )
        
        print("✅ Data loaded from local files")
        
        # Clean up temp files
        import shutil
        shutil.rmtree(temp_dir)
        
        # Example 5: Load partitioned data
        print("\n6. Loading partitioned data")
        print("-" * 60)
        
        # Partition sales data by month
        sales_df = sample_data['sales'].copy()
        sales_df['year'] = sales_df['order_date'].dt.year
        sales_df['month'] = sales_df['order_date'].dt.month
        
        for (year, month), group in sales_df.groupby(['year', 'month']):
            partition_path = f"raw/sales_partitioned/year={year}/month={month:02d}/data.parquet"
            loader.load_dataframe(
                df=group.drop(['year', 'month'], axis=1),
                target_path=partition_path,
                file_format='parquet'
            )
            print(f"   Loaded partition: year={year}, month={month:02d}")
        
        print("✅ Partitioned data loaded successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Detailed error:")
    
    print("\n" + "=" * 60)
    print("Data loading examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
