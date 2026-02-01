"""
Microsoft Fabric Data Exploration Module

This module demonstrates data exploration and visualization techniques
in Fabric notebooks using PySpark, Pandas, and visualization libraries.

Author: Data Engineering Team
License: MIT
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def data_profiling():
    """Data profiling examples."""
    print("=" * 80)
    print("Data Exploration and Visualization in Fabric")
    print("=" * 80)
    
    print("\n1. Data Profiling")
    print("-" * 80)
    print("""
    from pyspark.sql import functions as F
    
    # Basic statistics
    df.describe().show()
    
    # Column statistics
    df.select([
        F.count(F.col(c)).alias(c) 
        for c in df.columns
    ]).show()
    
    # Null value counts
    df.select([
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c)
        for c in df.columns
    ]).show()
    
    # Distinct counts
    df.select([
        F.countDistinct(c).alias(c) 
        for c in df.columns
    ]).show()
    
    # Value distributions
    df.groupBy("category").count().orderBy(F.desc("count")).show()
    
    # Summary statistics
    df.summary("count", "mean", "stddev", "min", "25%", "50%", "75%", "max").show()
    """)


def exploratory_analysis():
    """Exploratory data analysis patterns."""
    print("\n2. Exploratory Data Analysis")
    print("-" * 80)
    print("""
    # Check for duplicates
    total_rows = df.count()
    distinct_rows = df.distinct().count()
    duplicates = total_rows - distinct_rows
    print(f"Duplicate rows: {duplicates}")
    
    # Find duplicate records
    from pyspark.sql.window import Window
    
    window_spec = Window.partitionBy("customer_id", "order_date")
    df_with_count = df.withColumn("row_count", F.count("*").over(window_spec))
    duplicates_df = df_with_count.filter(F.col("row_count") > 1)
    
    # Identify outliers using IQR method
    quantiles = df.approxQuantile("price", [0.25, 0.75], 0.01)
    q1, q3 = quantiles[0], quantiles[1]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = df.filter(
        (F.col("price") < lower_bound) | 
        (F.col("price") > upper_bound)
    )
    
    # Correlation analysis
    from pyspark.ml.stat import Correlation
    from pyspark.ml.feature import VectorAssembler
    
    assembler = VectorAssembler(
        inputCols=["quantity", "price", "total"],
        outputCol="features"
    )
    df_vector = assembler.transform(df)
    
    correlation_matrix = Correlation.corr(df_vector, "features").head()[0]
    print("Correlation Matrix:")
    print(correlation_matrix)
    """)


def data_visualization():
    """Data visualization examples."""
    print("\n3. Data Visualization")
    print("-" * 80)
    print("""
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    
    # Convert to Pandas for visualization
    df_pandas = df.limit(10000).toPandas()
    
    # Distribution plot
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    df_pandas['price'].hist(bins=50)
    plt.title('Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    
    plt.subplot(1, 2, 2)
    df_pandas.boxplot(column='price', by='category')
    plt.title('Price by Category')
    plt.suptitle('')
    plt.show()
    
    # Time series plot
    daily_sales = df_pandas.groupby('order_date')['total_amount'].sum()
    
    plt.figure(figsize=(14, 6))
    daily_sales.plot()
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.grid(True)
    plt.show()
    
    # Bar chart - Top 10 products
    plt.figure(figsize=(12, 6))
    top_products = df_pandas.groupby('product_name')['total_amount'].sum() \\
        .sort_values(ascending=False).head(10)
    top_products.plot(kind='barh')
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Total Revenue')
    plt.tight_layout()
    plt.show()
    
    # Scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df_pandas['quantity'], df_pandas['total_amount'], alpha=0.5)
    plt.title('Quantity vs Total Amount')
    plt.xlabel('Quantity')
    plt.ylabel('Total Amount')
    plt.show()
    
    # Heatmap - Correlation matrix
    plt.figure(figsize=(10, 8))
    numeric_cols = df_pandas.select_dtypes(include=['number']).columns
    correlation = df_pandas[numeric_cols].corr()
    sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()
    """)


def advanced_visualizations():
    """Advanced visualization techniques."""
    print("\n4. Advanced Visualizations")
    print("-" * 80)
    print("""
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Interactive line chart with Plotly
    fig = px.line(
        df_pandas,
        x='order_date',
        y='total_amount',
        color='category',
        title='Sales Trend by Category'
    )
    fig.show()
    
    # Interactive scatter plot
    fig = px.scatter(
        df_pandas,
        x='quantity',
        y='price',
        color='category',
        size='total_amount',
        hover_data=['product_name'],
        title='Product Analysis'
    )
    fig.show()
    
    # Sunburst chart for hierarchical data
    fig = px.sunburst(
        df_pandas,
        path=['region', 'country', 'city'],
        values='total_amount',
        title='Sales by Geographic Hierarchy'
    )
    fig.show()
    
    # Treemap
    fig = px.treemap(
        df_pandas,
        path=['category', 'subcategory', 'product_name'],
        values='total_amount',
        title='Product Category Breakdown'
    )
    fig.show()
    
    # Multiple subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Sales Trend', 'Category Distribution',
                       'Price Distribution', 'Top Products')
    )
    
    fig.add_trace(
        go.Scatter(x=df_pandas['order_date'], y=df_pandas['total_amount']),
        row=1, col=1
    )
    
    category_counts = df_pandas['category'].value_counts()
    fig.add_trace(
        go.Bar(x=category_counts.index, y=category_counts.values),
        row=1, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    fig.show()
    """)


def data_quality_checks():
    """Data quality validation."""
    print("\n5. Data Quality Checks")
    print("-" * 80)
    print("""
    from pyspark.sql import functions as F
    
    # Completeness check
    total_records = df.count()
    
    completeness = df.select([
        (F.count(c) / total_records * 100).alias(c) 
        for c in df.columns
    ])
    
    print("Completeness (% non-null):")
    completeness.show()
    
    # Uniqueness check
    uniqueness = df.select([
        (F.countDistinct(c) / F.count(c) * 100).alias(c)
        for c in df.columns
    ])
    
    print("Uniqueness (% distinct):")
    uniqueness.show()
    
    # Validity checks
    invalid_emails = df.filter(
        ~F.col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    ).count()
    
    invalid_dates = df.filter(
        (F.col("order_date") > F.current_date()) |
        (F.col("order_date") < "2020-01-01")
    ).count()
    
    negative_amounts = df.filter(F.col("total_amount") < 0).count()
    
    print(f"Invalid emails: {invalid_emails}")
    print(f"Invalid dates: {invalid_dates}")
    print(f"Negative amounts: {negative_amounts}")
    
    # Consistency checks
    inconsistent = df.filter(
        F.col("total_amount") != (F.col("quantity") * F.col("unit_price"))
    ).count()
    
    print(f"Inconsistent calculations: {inconsistent}")
    """)


def statistical_analysis():
    """Statistical analysis examples."""
    print("\n6. Statistical Analysis")
    print("-" * 80)
    print("""
    import numpy as np
    from scipy import stats
    
    # Convert to Pandas for statistical tests
    df_pandas = df.toPandas()
    
    # T-test: Compare means between two groups
    group_a = df_pandas[df_pandas['category'] == 'A']['price']
    group_b = df_pandas[df_pandas['category'] == 'B']['price']
    
    t_stat, p_value = stats.ttest_ind(group_a, group_b)
    print(f"T-test: t={t_stat:.4f}, p={p_value:.4f}")
    
    # Chi-square test: Test independence between categorical variables
    contingency_table = pd.crosstab(
        df_pandas['category'],
        df_pandas['region']
    )
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    print(f"Chi-square: χ²={chi2:.4f}, p={p_value:.4f}")
    
    # Normality test
    statistic, p_value = stats.normaltest(df_pandas['price'].dropna())
    print(f"Normality test: p={p_value:.4f}")
    
    # Percentiles
    percentiles = np.percentile(
        df_pandas['total_amount'],
        [10, 25, 50, 75, 90, 95, 99]
    )
    print("Percentiles:", percentiles)
    """)


def interactive_fabric_display():
    """Using Fabric's interactive display."""
    print("\n7. Fabric Interactive Display")
    print("-" * 80)
    print("""
    # Use Fabric's display function for interactive exploration
    
    # Display DataFrame with interactive filters and sorting
    display(df)
    
    # Display summary statistics
    display(df.describe())
    
    # Display chart (Fabric auto-generates visualizations)
    display(df.groupBy("category").sum("total_amount"))
    
    # Custom display with specific chart type
    display(df, summary=True)
    
    # Display multiple DataFrames
    display(df_sales)
    display(df_customers)
    
    # Note: 'display()' provides interactive tables in Fabric notebooks
    # with built-in filtering, sorting, and visualization options
    """)


def machine_learning_prep():
    """Data preparation for machine learning."""
    print("\n8. Data Preparation for ML")
    print("-" * 80)
    print("""
    from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
    from pyspark.ml import Pipeline
    
    # Handle categorical variables
    indexers = [
        StringIndexer(inputCol=col, outputCol=f"{col}_indexed")
        for col in ["category", "region", "product_type"]
    ]
    
    # Assemble features
    feature_cols = ["quantity", "price", "category_indexed", "region_indexed"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    
    # Scale features
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    
    # Create pipeline
    pipeline = Pipeline(stages=indexers + [assembler, scaler])
    
    # Fit and transform
    model = pipeline.fit(df)
    df_transformed = model.transform(df)
    
    # Train-test split
    train_df, test_df = df_transformed.randomSplit([0.8, 0.2], seed=42)
    
    print(f"Training set: {train_df.count()} rows")
    print(f"Test set: {test_df.count()} rows")
    """)


def main():
    """Run all data exploration examples."""
    data_profiling()
    exploratory_analysis()
    data_visualization()
    advanced_visualizations()
    data_quality_checks()
    statistical_analysis()
    interactive_fabric_display()
    machine_learning_prep()
    
    print("\n" + "=" * 80)
    print("Data Exploration Examples Completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
