#!/usr/bin/env python3
"""
Example: Complete Data Quality Workflow

Demonstrates how to use the data quality framework modules together
for comprehensive data quality assessment.
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from src.quality import (
    DataValidator,
    DataProfiler,
    QualityMetricsCalculator,
    MetricsTracker
)


def main():
    """Run complete data quality workflow example"""
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("DataQualityExample") \
        .master("local[*]") \
        .getOrCreate()
    
    # Create sample data
    print("=" * 70)
    print("Data Quality Framework - Complete Workflow Example")
    print("=" * 70)
    
    data = [
        (1, "Alice Johnson", 28, "alice@example.com", "2024-01-15"),
        (2, "Bob Smith", 35, "bob@example.com", "2024-01-14"),
        (3, "Charlie Brown", None, "charlie@test.com", "2024-01-13"),
        (4, "David Lee", 42, None, "2024-01-12"),
        (5, "Eve Wilson", 29, "eve@example.com", "2024-01-15"),
        (6, "Frank Miller", 31, "frank@example.com", "2024-01-15"),
        (7, "Grace Taylor", 26, "grace@example.com", "2024-01-14"),
        (8, "Henry Davis", 150, "invalid-email", "2024-01-13"),  # Invalid age and email
        (9, "Ivy Chen", 33, "ivy@example.com", "2024-01-15"),
        (10, "Jack Anderson", 28, "jack@example.com", "2024-01-15")
    ]
    
    columns = ["id", "name", "age", "email", "last_updated"]
    df = spark.createDataFrame(data, columns)
    
    print(f"\nSample dataset created: {df.count()} rows")
    df.show(5)
    
    # ========================================================================
    # STEP 1: Data Validation
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 1: Data Validation")
    print("=" * 70)
    
    validator = DataValidator(spark)
    validation_results = []
    
    # Check for nulls
    print("\n1.1 Checking for null values...")
    result = validator.validate_not_null(df, columns=["id", "name"], threshold=0.0)
    print(f"   Result: {result.status.value} - {result.message}")
    validation_results.append(result)
    
    # Check uniqueness
    print("\n1.2 Checking uniqueness...")
    result = validator.validate_unique(df, columns=["id"])
    print(f"   Result: {result.status.value} - {result.message}")
    validation_results.append(result)
    
    # Check age range
    print("\n1.3 Validating age range...")
    result = validator.validate_range(df, column="age", min_value=0, max_value=120)
    print(f"   Result: {result.status.value} - {result.message}")
    if result.failed_count > 0:
        print(f"   Failed records: {result.failed_records}")
    validation_results.append(result)
    
    # Check email pattern
    print("\n1.4 Validating email format...")
    result = validator.validate_pattern(
        df,
        column="email",
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
    )
    print(f"   Result: {result.status.value} - {result.message}")
    if result.failed_count > 0:
        print(f"   Failed records: {result.failed_records}")
    validation_results.append(result)
    
    # Get validation summary
    summary = validator.get_validation_summary(validation_results)
    print(f"\n1.5 Validation Summary:")
    print(f"   Total rules: {summary['total_rules']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Success rate: {summary['success_rate']:.1%}")
    
    # ========================================================================
    # STEP 2: Data Profiling
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Data Profiling")
    print("=" * 70)
    
    profiler = DataProfiler(spark)
    print("\n2.1 Generating data profile...")
    
    profile_report = profiler.profile(
        df,
        table_name="users_dataset",
        include_patterns=True,
        top_n_values=5
    )
    
    print(f"\n2.2 Profile Results:")
    print(f"   Table: {profile_report.table_name}")
    print(f"   Rows: {profile_report.row_count}")
    print(f"   Columns: {profile_report.column_count}")
    print(f"   Duplicate rows: {profile_report.duplicate_rows} ({profile_report.duplicate_percentage:.1f}%)")
    
    print(f"\n2.3 Column Profiles:")
    for col_profile in profile_report.columns:
        print(f"\n   Column: {col_profile.column_name}")
        print(f"      Type: {col_profile.data_type}")
        print(f"      Nulls: {col_profile.null_count} ({col_profile.null_percentage:.1f}%)")
        print(f"      Distinct: {col_profile.distinct_count} ({col_profile.distinct_percentage:.1f}%)")
        
        if col_profile.mean is not None:
            print(f"      Mean: {col_profile.mean:.2f}")
            print(f"      Std Dev: {col_profile.stddev:.2f}")
            print(f"      Min: {col_profile.min_value}, Max: {col_profile.max_value}")
        
        if col_profile.top_values:
            print(f"      Top 3 values: {col_profile.top_values[:3]}")
    
    # ========================================================================
    # STEP 3: Quality Metrics
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 3: Quality Metrics Calculation")
    print("=" * 70)
    
    metrics_calc = QualityMetricsCalculator(
        spark,
        default_target=0.95,
        default_threshold=0.80
    )
    
    print("\n3.1 Calculating quality metrics...")
    
    # Define quality configuration
    quality_config = {
        'check_completeness': True,
        'completeness_columns': ['id', 'name', 'age', 'email'],
        
        'uniqueness_columns': [
            ['id'],
            ['email']
        ],
        
        'validity_checks': [
            {
                'column': 'age',
                'condition': 'age >= 0 AND age <= 120',
                'target': 0.90,
                'threshold': 0.80
            },
            {
                'column': 'email',
                'condition': "email RLIKE '^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'",
                'target': 0.90,
                'threshold': 0.80
            }
        ]
    }
    
    # Calculate all metrics
    quality_report = metrics_calc.calculate_all_metrics(
        df,
        "users_dataset",
        quality_config
    )
    
    print(f"\n3.2 Quality Report:")
    print(f"   Dataset: {quality_report.dataset_name}")
    print(f"   Overall Score: {quality_report.overall_score * 100:.1f}%")
    
    print(f"\n   Dimension Scores:")
    for dimension, score in quality_report.dimension_scores.items():
        print(f"      {dimension.capitalize()}: {score * 100:.1f}%")
    
    print(f"\n   Metrics Status:")
    print(f"      Passed: {quality_report.passed_metrics}")
    print(f"      Failed: {quality_report.failed_metrics}")
    print(f"      Warnings: {quality_report.warning_metrics}")
    
    print(f"\n3.3 Detailed Metrics:")
    for metric in quality_report.metrics:
        status_symbol = "✓" if metric.status == "passed" else "✗"
        print(f"      {status_symbol} {metric.metric_name}: "
              f"{metric.score_percentage:.1f}% ({metric.status})")
    
    # ========================================================================
    # STEP 4: Metrics Tracking
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 4: Metrics Tracking")
    print("=" * 70)
    
    tracker = MetricsTracker()
    
    print("\n4.1 Recording metrics for historical tracking...")
    tracker.record_metrics(quality_report, run_id="example_run_001")
    
    # Simulate additional runs
    tracker.record_metrics(quality_report, run_id="example_run_002")
    
    print("\n4.2 Tracking Summary:")
    summary = tracker.get_summary("users_dataset")
    print(f"   Dataset: {summary['dataset_name']}")
    print(f"   Total Runs: {summary['total_runs']}")
    print(f"   Average Score: {summary['avg_score'] * 100:.1f}%")
    print(f"   Latest Score: {summary['latest_score'] * 100:.1f}%")
    
    # ========================================================================
    # STEP 5: Export Results
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 5: Export Results")
    print("=" * 70)
    
    print("\n5.1 Exporting reports...")
    
    # Export profile report
    profile_json = profile_report.to_json()
    print(f"   Profile report size: {len(profile_json)} characters")
    
    # Export quality report
    quality_json = quality_report.to_json()
    print(f"   Quality report size: {len(quality_json)} characters")
    
    print("\n   Reports can be saved to files:")
    print("      - profile_report.json")
    print("      - quality_report.json")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    print("\nKey Findings:")
    print(f"   • Dataset Quality Score: {quality_report.overall_score * 100:.1f}%")
    print(f"   • Validation Success Rate: {summary['success_rate']:.1%}")
    print(f"   • Completeness: {quality_report.dimension_scores.get('completeness', 0) * 100:.1f}%")
    print(f"   • Validity: {quality_report.dimension_scores.get('validity', 0) * 100:.1f}%")
    print(f"   • Uniqueness: {quality_report.dimension_scores.get('uniqueness', 0) * 100:.1f}%")
    print(f"   • Issues Found: {quality_report.failed_metrics} failed metrics")
    
    print("\nData Quality Framework components used:")
    print("   ✓ DataValidator - Schema and rule validation")
    print("   ✓ DataProfiler - Statistical profiling and analysis")
    print("   ✓ QualityMetricsCalculator - Quality scoring and metrics")
    print("   ✓ MetricsTracker - Historical tracking and trending")
    
    print("\n" + "=" * 70)
    
    spark.stop()


if __name__ == "__main__":
    main()
