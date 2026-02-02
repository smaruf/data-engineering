"""
Microsoft Fabric Notebook Basics

This module demonstrates essential operations and patterns for working
with Fabric notebooks programmatically and interactively.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def notebook_environment_info():
    """
    Display information about the Fabric notebook environment.
    """
    print("=" * 80)
    print("Fabric Notebook Environment Information")
    print("=" * 80)
    
    print("\n1. Runtime Environment")
    print("-" * 80)
    print(f"Current Time: {datetime.now()}")
    print(f"Python Version: {sys.version}")
    
    # Check if running in Fabric
    try:
        # Fabric-specific imports
        from notebookutils import mssparkutils
        print("✅ Running in Microsoft Fabric")
        print(f"Notebook Name: {mssparkutils.notebook.name}")
        print(f"Workspace: {mssparkutils.env.getWorkspaceName()}")
    except ImportError:
        print("⚠️  Not running in Fabric environment (local execution)")


def accessing_lakehouse():
    """
    Examples of accessing lakehouse data from notebooks.
    """
    print("\n2. Accessing Lakehouse Data")
    print("-" * 80)
    print("""
    # Access attached lakehouse using file path
    df = spark.read.parquet("/lakehouse/default/Files/raw/sales_data.parquet")
    df.show()
    
    # Access lakehouse tables using SQL
    df = spark.sql("SELECT * FROM my_lakehouse.sales_table")
    df.show()
    
    # Access using OneLake path
    onelake_path = "abfss://workspace@onelake.dfs.fabric.microsoft.com/lakehouse/Files/data"
    df = spark.read.parquet(onelake_path)
    
    # List files in lakehouse
    from notebookutils import mssparkutils
    files = mssparkutils.fs.ls("/lakehouse/default/Files/")
    for file in files:
        print(f"{file.name} - {file.size} bytes")
    """)


def working_with_notebooks():
    """
    Examples of working with notebooks programmatically.
    """
    print("\n3. Notebook Utilities (mssparkutils)")
    print("-" * 80)
    print("""
    from notebookutils import mssparkutils
    
    # File system operations
    mssparkutils.fs.ls("/lakehouse/default/Files/")
    mssparkutils.fs.mkdirs("/lakehouse/default/Files/new_folder")
    mssparkutils.fs.rm("/lakehouse/default/Files/old_file.csv")
    
    # Notebook execution
    result = mssparkutils.notebook.run(
        "AnotherNotebook",
        timeoutSeconds=600,
        arguments={"param1": "value1", "param2": "value2"}
    )
    print(f"Notebook result: {result}")
    
    # Environment variables
    workspace = mssparkutils.env.getWorkspaceName()
    notebook = mssparkutils.env.getNotebookName()
    
    # Credentials and secrets (Key Vault)
    secret = mssparkutils.credentials.getSecret("myKeyVault", "mySecret")
    
    # Exit notebook with value
    mssparkutils.notebook.exit("Notebook completed successfully")
    """)


def data_transformation_patterns():
    """
    Common data transformation patterns in notebooks.
    """
    print("\n4. Data Transformation Patterns")
    print("-" * 80)
    print("""
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    
    # Read data
    df = spark.read.parquet("/lakehouse/default/Files/raw/sales.parquet")
    
    # Add calculated columns
    df_transformed = df.withColumn(
        "total_amount",
        F.col("quantity") * F.col("unit_price")
    ).withColumn(
        "order_year",
        F.year("order_date")
    ).withColumn(
        "order_month",
        F.month("order_date")
    )
    
    # Window functions
    window_spec = Window.partitionBy("customer_id").orderBy("order_date")
    df_windowed = df_transformed.withColumn(
        "running_total",
        F.sum("total_amount").over(window_spec)
    ).withColumn(
        "row_number",
        F.row_number().over(window_spec)
    )
    
    # Aggregations
    summary = df.groupBy("product_category").agg(
        F.count("order_id").alias("order_count"),
        F.sum("total_amount").alias("total_revenue"),
        F.avg("total_amount").alias("avg_order_value")
    )
    
    # Save to lakehouse
    df_transformed.write.mode("overwrite").format("delta").save(
        "/lakehouse/default/Tables/sales_transformed"
    )
    """)


def visualization_examples():
    """
    Visualization examples in Fabric notebooks.
    """
    print("\n5. Data Visualization")
    print("-" * 80)
    print("""
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    
    # Convert Spark DataFrame to Pandas for visualization
    df_pandas = df.toPandas()
    
    # Line chart
    plt.figure(figsize=(12, 6))
    df_pandas.groupby('order_date')['total_amount'].sum().plot()
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.show()
    
    # Bar chart
    plt.figure(figsize=(10, 6))
    category_sales = df_pandas.groupby('category')['total_amount'].sum().sort_values()
    category_sales.plot(kind='barh')
    plt.title('Sales by Category')
    plt.xlabel('Total Sales')
    plt.show()
    
    # Heatmap
    plt.figure(figsize=(10, 8))
    pivot_table = df_pandas.pivot_table(
        values='total_amount',
        index='product',
        columns='month',
        aggfunc='sum'
    )
    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlOrRd')
    plt.title('Sales Heatmap: Product vs Month')
    plt.show()
    
    # Use Fabric's display function
    display(df)  # Interactive table in notebook
    """)


def best_practices():
    """
    Best practices for Fabric notebooks.
    """
    print("\n6. Notebook Best Practices")
    print("-" * 80)
    print("""
    Best Practices for Fabric Notebooks:
    
    1. Organization:
       ✓ Use clear cell structure (imports, config, processing, output)
       ✓ Add markdown cells for documentation
       ✓ Break complex logic into multiple notebooks
       ✓ Use consistent naming conventions
    
    2. Performance:
       ✓ Cache DataFrames when reusing: df.cache()
       ✓ Use broadcast joins for small tables
       ✓ Partition data appropriately
       ✓ Avoid .collect() on large datasets
       ✓ Use .limit() during development
    
    3. Data Management:
       ✓ Write to Delta format for ACID transactions
       ✓ Use partitioning for large tables
       ✓ Clean up temporary data
       ✓ Version control your notebooks (Git integration)
    
    4. Error Handling:
       ✓ Use try-except blocks
       ✓ Log important operations
       ✓ Validate data quality
       ✓ Handle null values explicitly
    
    5. Collaboration:
       ✓ Document parameters and outputs
       ✓ Use parameters for notebook orchestration
       ✓ Share via workspace permissions
       ✓ Use version control
    
    6. Security:
       ✓ Use Key Vault for secrets
       ✓ Don't hardcode credentials
       ✓ Use managed identities
       ✓ Apply row-level security when needed
    """)


def notebook_parameters_example():
    """
    Example of using parameters in notebooks.
    """
    print("\n7. Notebook Parameters")
    print("-" * 80)
    print("""
    # Define parameters in first cell (tagged as 'parameters')
    # These can be overridden when notebook is called
    
    # Parameters cell (tag this cell as 'parameters' in notebook UI)
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    product_category = "Electronics"
    
    # Use parameters in processing
    df = spark.read.table("sales")
    df_filtered = df.filter(
        (F.col("order_date") >= start_date) &
        (F.col("order_date") <= end_date) &
        (F.col("category") == product_category)
    )
    
    # When calling from another notebook:
    from notebookutils import mssparkutils
    
    result = mssparkutils.notebook.run(
        "DataProcessingNotebook",
        timeoutSeconds=600,
        arguments={
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
            "product_category": "Clothing"
        }
    )
    """)


def main():
    """
    Run all notebook basics examples.
    """
    import sys
    
    notebook_environment_info()
    accessing_lakehouse()
    working_with_notebooks()
    data_transformation_patterns()
    visualization_examples()
    best_practices()
    notebook_parameters_example()
    
    print("\n" + "=" * 80)
    print("Fabric Notebook Basics Examples Completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
