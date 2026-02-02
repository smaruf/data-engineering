# Data Quality Framework

Comprehensive data quality framework for the Data Fabric Platform with support for PySpark DataFrames.

## Overview

The Data Quality Framework provides production-ready modules for:
- **Data Validation**: Schema validation, type checking, range validation, null checks, uniqueness validation
- **Data Profiling**: Statistical profiling, distribution analysis, pattern detection
- **Quality Metrics**: Completeness, accuracy, consistency, timeliness, and validity metrics
- **Metrics Tracking**: Historical quality metrics tracking and trending

## Modules

### 1. `validators.py`
Comprehensive data validation module with support for:

#### Features
- **Schema Validation**: Validate DataFrames against expected schemas
- **Type Validation**: Verify column data types
- **Null Checks**: Detect and report null values
- **Uniqueness Validation**: Check for duplicate records
- **Range Validation**: Validate numeric values are within acceptable ranges
- **Pattern Validation**: Validate string patterns using regex
- **Custom Validation**: Define custom validation rules using SQL conditions
- **Great Expectations Integration**: Advanced validation with Great Expectations

#### Usage Example

```python
from pyspark.sql import SparkSession
from src.quality.validators import DataValidator, SchemaValidator

spark = SparkSession.builder.appName("QualityValidation").getOrCreate()
validator = DataValidator(spark)

# Load your data
df = spark.read.parquet("path/to/data")

# Validate not null
result = validator.validate_not_null(df, columns=["user_id", "email"])
print(f"Status: {result.status.value}, Message: {result.message}")

# Validate uniqueness
result = validator.validate_unique(df, columns=["user_id"])

# Validate range
result = validator.validate_range(df, column="age", min_value=0, max_value=120)

# Validate pattern (e.g., email format)
result = validator.validate_pattern(df, column="email", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Custom validation
result = validator.validate_custom(
    df,
    rule_name="age_consistency",
    condition="age >= 18 OR account_type = 'minor'"
)

# Get summary of all validations
results = [result1, result2, result3]
summary = validator.get_validation_summary(results)
print(f"Overall success rate: {summary['success_rate']:.1%}")
```

#### Schema Validation

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from src.quality.validators import SchemaValidator

schema_validator = SchemaValidator()

expected_schema = StructType([
    StructField("user_id", IntegerType(), nullable=False),
    StructField("name", StringType(), nullable=False),
    StructField("email", StringType(), nullable=True)
])

result = schema_validator.validate_schema(df, expected_schema, strict=True)
```

#### Great Expectations Integration

```python
from src.quality.validators import GreatExpectationsValidator

gx_validator = GreatExpectationsValidator(context_root_dir="/path/to/gx")

# Create expectation suite
expectations = [
    {
        "expectation_type": "expect_column_values_to_not_be_null",
        "kwargs": {"column": "user_id"}
    },
    {
        "expectation_type": "expect_column_values_to_be_between",
        "kwargs": {"column": "age", "min_value": 0, "max_value": 120}
    }
]
gx_validator.create_expectation_suite("user_suite", expectations)

# Validate using suite
result = gx_validator.validate_with_suite(df, "user_suite")
```

### 2. `profiling.py`
Data profiling module for comprehensive data analysis.

#### Features
- **Statistical Profiling**: Min, max, mean, stddev, percentiles for numeric columns
- **String Analysis**: Length statistics, top values
- **Temporal Analysis**: Date/timestamp range analysis
- **Distribution Analysis**: Histograms, skewness, kurtosis
- **Missing Value Analysis**: Null counts and percentages
- **Duplicate Detection**: Identify duplicate records
- **Pattern Detection**: Detect common patterns (email, phone, URLs, etc.)
- **Outlier Detection**: IQR and Z-score based outlier detection

#### Usage Example

```python
from src.quality.profiling import DataProfiler, DistributionAnalyzer, PatternDetector

# Basic profiling
profiler = DataProfiler(spark)
report = profiler.profile(
    df,
    table_name="users_table",
    sample_size=10000,  # Optional: sample for large datasets
    include_patterns=True,
    top_n_values=10
)

# Access profile information
print(f"Table: {report.table_name}")
print(f"Rows: {report.row_count}")
print(f"Duplicates: {report.duplicate_rows} ({report.duplicate_percentage:.1f}%)")

for col_profile in report.columns:
    print(f"\nColumn: {col_profile.column_name}")
    print(f"  Type: {col_profile.data_type}")
    print(f"  Null %: {col_profile.null_percentage:.1f}%")
    print(f"  Distinct: {col_profile.distinct_count}")
    
    if col_profile.mean is not None:
        print(f"  Mean: {col_profile.mean:.2f}")
        print(f"  Std Dev: {col_profile.stddev:.2f}")
        print(f"  Percentiles: {col_profile.percentiles}")
    
    if col_profile.top_values:
        print(f"  Top values: {col_profile.top_values[:3]}")

# Save report as JSON
with open("profile_report.json", "w") as f:
    f.write(report.to_json())
```

#### Distribution Analysis

```python
from src.quality.profiling import DistributionAnalyzer

analyzer = DistributionAnalyzer(spark)

# Analyze numeric distribution
dist = analyzer.analyze_numeric_distribution(df, column="age", num_bins=10)
print(f"Skewness: {dist['skewness']:.2f}")
print(f"Kurtosis: {dist['kurtosis']:.2f}")

for bin_info in dist['histogram']:
    print(f"  {bin_info['bin_start']:.1f} - {bin_info['bin_end']:.1f}: "
          f"{bin_info['count']} ({bin_info['percentage']:.1f}%)")

# Analyze categorical distribution
cat_dist = analyzer.analyze_categorical_distribution(df, column="country")
print(f"Unique values: {cat_dist['unique_values']}")
print(f"Entropy: {cat_dist['entropy']:.2f}")

# Detect outliers
outliers = analyzer.detect_outliers(df, column="salary", method="iqr", threshold=1.5)
print(f"Outliers: {outliers['outlier_count']} ({outliers['outlier_percentage']:.1f}%)")
print(f"Bounds: [{outliers['lower_bound']:.2f}, {outliers['upper_bound']:.2f}]")
```

#### Pattern Detection

```python
from src.quality.profiling import PatternDetector

detector = PatternDetector()

# Detect patterns in a column
patterns = detector.detect_patterns(df, column="email", min_match_rate=0.8)
print(f"Detected patterns: {patterns}")  # e.g., ['email']

# Validate specific pattern
validation = detector.validate_pattern(df, column="phone", pattern_name="phone_us")
print(f"Match rate: {validation['match_rate']:.1%}")
print(f"Passed: {validation['passed']}")
```

### 3. `quality_metrics.py`
Quality metrics calculation and tracking.

#### Features
- **Completeness Metrics**: Measure non-null rates
- **Accuracy Metrics**: Compare against reference data
- **Consistency Metrics**: Cross-column validation
- **Timeliness Metrics**: Data freshness checks
- **Validity Metrics**: Rule-based validation
- **Uniqueness Metrics**: Duplicate detection
- **Overall Quality Scores**: Aggregate metrics
- **Historical Tracking**: Track metrics over time

#### Usage Example

```python
from src.quality.quality_metrics import QualityMetricsCalculator, MetricsTracker

metrics_calc = QualityMetricsCalculator(
    spark,
    default_target=0.95,      # 95% target
    default_threshold=0.80     # 80% warning threshold
)

# Calculate completeness
completeness_metrics = metrics_calc.calculate_completeness(
    df,
    columns=["user_id", "email", "age"],
    target=0.98,
    threshold=0.90
)

# Calculate uniqueness
uniqueness_metric = metrics_calc.calculate_uniqueness(
    df,
    columns=["user_id"],
    target=1.0,
    threshold=0.99
)

# Calculate validity
validity_metric = metrics_calc.calculate_validity(
    df,
    column="age",
    valid_condition="age >= 0 AND age <= 120"
)

# Calculate consistency
consistency_metric = metrics_calc.calculate_consistency(
    df,
    check_name="age_registration_date",
    consistency_condition="registration_date <= current_date()"
)

# Calculate timeliness
timeliness_metric = metrics_calc.calculate_timeliness(
    df,
    timestamp_column="last_updated",
    max_age_hours=24
)

# Generate comprehensive report
all_metrics = completeness_metrics + [uniqueness_metric, validity_metric]
report = metrics_calc.generate_report(df, "users_dataset", all_metrics)

print(f"Overall Quality Score: {report.overall_score * 100:.1f}%")
print(f"Dimension Scores:")
for dimension, score in report.dimension_scores.items():
    print(f"  {dimension}: {score * 100:.1f}%")

print(f"\nMetrics Status:")
print(f"  Passed: {report.passed_metrics}")
print(f"  Failed: {report.failed_metrics}")
print(f"  Warnings: {report.warning_metrics}")

# Save report
with open("quality_report.json", "w") as f:
    f.write(report.to_json())
```

#### Configuration-Based Metrics

```python
# Define quality checks in configuration
config = {
    'check_completeness': True,
    'completeness_columns': ['user_id', 'email', 'name'],
    
    'uniqueness_columns': [
        ['user_id'],
        ['email']
    ],
    
    'validity_checks': [
        {
            'column': 'age',
            'condition': 'age >= 0 AND age <= 120',
            'target': 0.99,
            'threshold': 0.95
        },
        {
            'column': 'email',
            'condition': "email RLIKE '^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'",
            'target': 0.98
        }
    ],
    
    'consistency_checks': [
        {
            'name': 'date_order',
            'condition': 'created_date <= updated_date',
            'target': 1.0
        }
    ],
    
    'timeliness_checks': [
        {
            'column': 'last_updated',
            'max_age_hours': 24,
            'target': 0.90
        }
    ]
}

# Calculate all metrics based on config
report = metrics_calc.calculate_all_metrics(df, "users_dataset", config)
```

#### Metrics Tracking

```python
from src.quality.quality_metrics import MetricsTracker

# Initialize tracker
tracker = MetricsTracker(storage_path="/path/to/metrics/storage")

# Record metrics from multiple runs
tracker.record_metrics(report, run_id="run_2024_01_15_001")
tracker.record_metrics(report2, run_id="run_2024_01_16_001")

# Get trend analysis
trend = tracker.get_trend(
    dataset_name="users_dataset",
    metric_name="completeness",
    days=30
)

for point in trend:
    print(f"{point['timestamp']}: {point['value'] * 100:.1f}%")

# Get summary statistics
summary = tracker.get_summary("users_dataset")
print(f"Total runs: {summary['total_runs']}")
print(f"Average score: {summary['avg_score'] * 100:.1f}%")
print(f"Min score: {summary['min_score'] * 100:.1f}%")
print(f"Max score: {summary['max_score'] * 100:.1f}%")
print(f"Latest score: {summary['latest_score'] * 100:.1f}%")
```

## Integration with Shared Utils

All modules use the shared utilities from `shared.utils`:

```python
from shared.utils.logger import get_logger
from shared.utils.helpers import to_json, get_timestamp
from shared.utils.config_loader import config
```

## Production Best Practices

### 1. Error Handling
All modules include comprehensive error handling with logging:

```python
try:
    result = validator.validate_not_null(df, columns)
except Exception as e:
    logger.error(f"Validation failed: {e}", exc_info=True)
    # Handle error appropriately
```

### 2. Performance Optimization
- Use sampling for large datasets during profiling
- Leverage Spark's distributed processing
- Cache DataFrames when running multiple validations

```python
# Sample large datasets
report = profiler.profile(df, sample_size=100000)

# Cache for multiple validations
df.cache()
result1 = validator.validate_not_null(df, cols1)
result2 = validator.validate_unique(df, cols2)
df.unpersist()
```

### 3. Logging
All operations are logged with appropriate levels:

```python
from shared.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Starting data validation")
logger.warning("Found null values in critical column")
logger.error("Validation failed", exc_info=True)
```

### 4. Configuration Management
Use configuration files for validation rules:

```yaml
# quality_config.yaml
quality_checks:
  completeness:
    target: 0.95
    threshold: 0.85
    columns:
      - user_id
      - email
      
  uniqueness:
    - columns: [user_id]
      target: 1.0
      
  validity:
    - column: age
      condition: "age >= 0 AND age <= 120"
      target: 0.99
```

## Testing

Run the test suite to verify installation:

```bash
cd /path/to/data-fabric-platform
python3 test_quality_framework.py
```

## Requirements

- PySpark >= 3.5.0
- Python >= 3.8
- Great Expectations >= 0.18.8 (optional, for GX integration)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Architecture

```
src/quality/
├── __init__.py              # Package initialization
├── validators.py            # Data validation module
├── profiling.py            # Data profiling module
└── quality_metrics.py      # Quality metrics and tracking
```

## Contributing

When adding new quality checks or metrics:

1. Follow the existing patterns for error handling and logging
2. Include comprehensive docstrings
3. Add unit tests
4. Update this README with usage examples
5. Ensure compatibility with PySpark DataFrames

## License

Part of the Data Fabric Platform - Internal Use
