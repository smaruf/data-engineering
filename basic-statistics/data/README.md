# Sample Datasets

This directory contains sample datasets for learning and testing statistical methods.

## Available Datasets

### 1. test_scores.csv
- **Description**: Student test scores from multiple subjects
- **Size**: 100 records
- **Columns**: student_id, math, science, english, history
- **Use Cases**: Descriptive statistics, correlation analysis

### 2. sales_data.csv
- **Description**: Monthly sales data for different products
- **Size**: 1000 records
- **Columns**: date, product_id, category, quantity, revenue
- **Use Cases**: Time series analysis, hypothesis testing

### 3. sensor_readings.csv
- **Description**: IoT sensor temperature readings
- **Size**: 10,000 records
- **Columns**: timestamp, sensor_id, temperature, humidity, pressure
- **Use Cases**: Outlier detection, distribution analysis

### 4. ab_test_results.csv
- **Description**: A/B test results for website conversion
- **Size**: 2,000 records
- **Columns**: user_id, variant (A/B), converted (0/1), time_on_site
- **Use Cases**: Hypothesis testing, proportion tests

### 5. market_data.csv
- **Description**: Stock market price data
- **Size**: 5,000 records
- **Columns**: date, symbol, open, high, low, close, volume
- **Use Cases**: Regression analysis, volatility analysis

## Generating Custom Datasets

You can generate custom datasets using the provided scripts:

```python
python generate_sample_data.py --type sales --size 10000 --output custom_sales.csv
```

## Data Quality

All datasets have been:
- Cleaned and validated
- Checked for missing values
- Standardized formatting
- Documented with metadata

## Usage Example

```python
import pandas as pd

# Load dataset
df = pd.read_csv('data/test_scores.csv')

# Compute statistics
from src.python.descriptive import CentralTendency

mean_math = CentralTendency.mean(df['math'].values)
print(f"Mean math score: {mean_math}")
```

## Citation

If you use these datasets in your research or projects, please cite:
```
Basic Statistics Project
Data Engineering Learning Journey
https://github.com/smaruf/data-engineering
```

## License

These datasets are provided for educational purposes under MIT License.
