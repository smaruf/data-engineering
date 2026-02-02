"""
Data Quality Framework for Data Fabric Platform

Provides comprehensive data quality validation, profiling, and metrics tracking
with support for PySpark DataFrames and integration with Great Expectations.

Modules:
    validators: Data validation rules and schema validation
    profiling: Statistical profiling and data analysis
    quality_metrics: Quality metrics calculation and tracking
"""

from src.quality.validators import (
    DataValidator,
    SchemaValidator,
    ValidationRule,
    ValidationResult,
    GreatExpectationsValidator
)
from src.quality.profiling import (
    DataProfiler,
    ProfileReport,
    DistributionAnalyzer,
    PatternDetector
)
from src.quality.quality_metrics import (
    QualityMetricsCalculator,
    QualityMetric,
    QualityReport,
    MetricsTracker
)

__all__ = [
    'DataValidator',
    'SchemaValidator',
    'ValidationRule',
    'ValidationResult',
    'GreatExpectationsValidator',
    'DataProfiler',
    'ProfileReport',
    'DistributionAnalyzer',
    'PatternDetector',
    'QualityMetricsCalculator',
    'QualityMetric',
    'QualityReport',
    'MetricsTracker'
]

__version__ = '1.0.0'
