"""
Data Profiling Module

Comprehensive data profiling with:
- Statistical profiling (min, max, avg, stddev, percentiles)
- Data distribution analysis
- Missing value analysis
- Duplicate detection
- Pattern detection
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
import re

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    NumericType, StringType, DateType, TimestampType,
    IntegerType, LongType, FloatType, DoubleType
)

from shared.utils.logger import get_logger
from shared.utils.helpers import to_json, get_timestamp

logger = get_logger(__name__)


@dataclass
class ColumnProfile:
    """Profile information for a single column"""
    column_name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    distinct_count: int
    distinct_percentage: float
    
    # Numeric statistics
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean: Optional[float] = None
    stddev: Optional[float] = None
    percentiles: Optional[Dict[str, float]] = None
    
    # String statistics
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    
    # Distribution
    top_values: Optional[List[Tuple[Any, int]]] = None
    histogram: Optional[Dict[str, int]] = None
    
    # Patterns
    detected_patterns: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'column_name': self.column_name,
            'data_type': self.data_type,
            'total_count': self.total_count,
            'null_count': self.null_count,
            'null_percentage': self.null_percentage,
            'distinct_count': self.distinct_count,
            'distinct_percentage': self.distinct_percentage,
            'min_value': str(self.min_value) if self.min_value is not None else None,
            'max_value': str(self.max_value) if self.max_value is not None else None,
            'mean': self.mean,
            'stddev': self.stddev,
            'percentiles': self.percentiles,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'avg_length': self.avg_length,
            'top_values': [(str(v), c) for v, c in self.top_values] if self.top_values else None,
            'detected_patterns': self.detected_patterns
        }


@dataclass
class ProfileReport:
    """Complete profiling report for a DataFrame"""
    table_name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    duplicate_rows: int
    duplicate_percentage: float
    memory_usage_mb: Optional[float] = None
    profiling_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'table_name': self.table_name,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'columns': [col.to_dict() for col in self.columns],
            'duplicate_rows': self.duplicate_rows,
            'duplicate_percentage': self.duplicate_percentage,
            'memory_usage_mb': self.memory_usage_mb,
            'profiling_timestamp': self.profiling_timestamp,
            'metadata': self.metadata
        }
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert to JSON string"""
        return to_json(self.to_dict(), pretty=pretty)


class DataProfiler:
    """Main data profiling engine"""
    
    def __init__(
        self,
        spark: Optional[SparkSession] = None,
        percentiles: Optional[List[float]] = None
    ):
        self.logger = get_logger(__name__)
        self.spark = spark or SparkSession.builder.getOrCreate()
        self.percentiles = percentiles or [0.25, 0.5, 0.75, 0.95, 0.99]
    
    def profile(
        self,
        df: DataFrame,
        table_name: str = "unnamed_table",
        sample_size: Optional[int] = None,
        include_patterns: bool = True,
        top_n_values: int = 10
    ) -> ProfileReport:
        """
        Generate comprehensive profile for DataFrame
        
        Args:
            df: DataFrame to profile
            table_name: Name of the table/dataset
            sample_size: Optional sample size for large datasets
            include_patterns: Whether to detect patterns in string columns
            top_n_values: Number of top values to include per column
            
        Returns:
            ProfileReport
        """
        try:
            self.logger.info(f"Starting profiling for table: {table_name}")
            
            # Sample if requested
            if sample_size and df.count() > sample_size:
                self.logger.info(f"Sampling {sample_size} rows")
                df = df.sample(fraction=sample_size/df.count(), seed=42)
            
            row_count = df.count()
            column_count = len(df.columns)
            
            self.logger.info(f"Profiling {row_count} rows, {column_count} columns")
            
            # Profile each column
            column_profiles = []
            for col_name in df.columns:
                self.logger.info(f"Profiling column: {col_name}")
                profile = self._profile_column(
                    df,
                    col_name,
                    row_count,
                    include_patterns=include_patterns,
                    top_n=top_n_values
                )
                column_profiles.append(profile)
            
            # Detect duplicate rows
            duplicate_rows = row_count - df.distinct().count()
            duplicate_percentage = (duplicate_rows / row_count * 100) if row_count > 0 else 0
            
            report = ProfileReport(
                table_name=table_name,
                row_count=row_count,
                column_count=column_count,
                columns=column_profiles,
                duplicate_rows=duplicate_rows,
                duplicate_percentage=duplicate_percentage
            )
            
            self.logger.info(f"Profiling completed for {table_name}")
            return report
            
        except Exception as e:
            self.logger.error(f"Profiling error: {e}", exc_info=True)
            raise
    
    def _profile_column(
        self,
        df: DataFrame,
        column: str,
        total_count: int,
        include_patterns: bool = True,
        top_n: int = 10
    ) -> ColumnProfile:
        """Profile a single column"""
        try:
            col_type = dict(df.dtypes)[column]
            
            # Basic statistics
            null_count = df.filter(F.col(column).isNull()).count()
            null_percentage = (null_count / total_count * 100) if total_count > 0 else 0
            
            distinct_count = df.select(column).distinct().count()
            distinct_percentage = (distinct_count / total_count * 100) if total_count > 0 else 0
            
            profile = ColumnProfile(
                column_name=column,
                data_type=col_type,
                total_count=total_count,
                null_count=null_count,
                null_percentage=null_percentage,
                distinct_count=distinct_count,
                distinct_percentage=distinct_percentage
            )
            
            # Type-specific profiling
            if self._is_numeric(col_type):
                self._profile_numeric(df, column, profile)
            elif self._is_string(col_type):
                self._profile_string(df, column, profile, include_patterns)
            elif self._is_temporal(col_type):
                self._profile_temporal(df, column, profile)
            
            # Top values
            profile.top_values = self._get_top_values(df, column, top_n)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error profiling column {column}: {e}", exc_info=True)
            raise
    
    def _is_numeric(self, col_type: str) -> bool:
        """Check if column type is numeric"""
        return any(t in col_type.lower() for t in ['int', 'long', 'float', 'double', 'decimal'])
    
    def _is_string(self, col_type: str) -> bool:
        """Check if column type is string"""
        return 'string' in col_type.lower()
    
    def _is_temporal(self, col_type: str) -> bool:
        """Check if column type is temporal"""
        return any(t in col_type.lower() for t in ['date', 'timestamp'])
    
    def _profile_numeric(self, df: DataFrame, column: str, profile: ColumnProfile) -> None:
        """Profile numeric column"""
        try:
            stats = df.select(
                F.min(column).alias('min'),
                F.max(column).alias('max'),
                F.mean(column).alias('mean'),
                F.stddev(column).alias('stddev')
            ).collect()[0]
            
            profile.min_value = stats['min']
            profile.max_value = stats['max']
            profile.mean = float(stats['mean']) if stats['mean'] is not None else None
            profile.stddev = float(stats['stddev']) if stats['stddev'] is not None else None
            
            # Calculate percentiles
            percentile_values = df.select(
                F.expr(f"percentile_approx({column}, array({','.join(map(str, self.percentiles))}))").alias('percentiles')
            ).collect()[0]['percentiles']
            
            if percentile_values:
                profile.percentiles = {
                    f"p{int(p*100)}": float(v) if v is not None else None
                    for p, v in zip(self.percentiles, percentile_values)
                }
                
        except Exception as e:
            self.logger.warning(f"Error profiling numeric column {column}: {e}")
    
    def _profile_string(
        self,
        df: DataFrame,
        column: str,
        profile: ColumnProfile,
        include_patterns: bool = True
    ) -> None:
        """Profile string column"""
        try:
            # String length statistics
            length_stats = df.select(
                F.min(F.length(column)).alias('min_len'),
                F.max(F.length(column)).alias('max_len'),
                F.avg(F.length(column)).alias('avg_len')
            ).collect()[0]
            
            profile.min_length = length_stats['min_len']
            profile.max_length = length_stats['max_len']
            profile.avg_length = float(length_stats['avg_len']) if length_stats['avg_len'] else None
            
            # Pattern detection
            if include_patterns:
                pattern_detector = PatternDetector()
                patterns = pattern_detector.detect_patterns(df, column, sample_size=1000)
                profile.detected_patterns = patterns
                
        except Exception as e:
            self.logger.warning(f"Error profiling string column {column}: {e}")
    
    def _profile_temporal(self, df: DataFrame, column: str, profile: ColumnProfile) -> None:
        """Profile temporal column"""
        try:
            stats = df.select(
                F.min(column).alias('min'),
                F.max(column).alias('max')
            ).collect()[0]
            
            profile.min_value = stats['min']
            profile.max_value = stats['max']
            
        except Exception as e:
            self.logger.warning(f"Error profiling temporal column {column}: {e}")
    
    def _get_top_values(
        self,
        df: DataFrame,
        column: str,
        top_n: int
    ) -> List[Tuple[Any, int]]:
        """Get top N most frequent values"""
        try:
            top_values = (
                df.groupBy(column)
                .count()
                .orderBy(F.desc('count'))
                .limit(top_n)
                .collect()
            )
            
            return [(row[column], row['count']) for row in top_values]
            
        except Exception as e:
            self.logger.warning(f"Error getting top values for {column}: {e}")
            return []
    
    def profile_subset(
        self,
        df: DataFrame,
        columns: List[str],
        table_name: str = "subset"
    ) -> ProfileReport:
        """
        Profile only specified columns
        
        Args:
            df: DataFrame to profile
            columns: List of columns to profile
            table_name: Name of the table/dataset
            
        Returns:
            ProfileReport
        """
        subset_df = df.select(columns)
        return self.profile(subset_df, table_name=table_name)


class DistributionAnalyzer:
    """Analyze data distributions"""
    
    def __init__(self, spark: Optional[SparkSession] = None):
        self.logger = get_logger(__name__)
        self.spark = spark or SparkSession.builder.getOrCreate()
    
    def analyze_numeric_distribution(
        self,
        df: DataFrame,
        column: str,
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze distribution of numeric column
        
        Args:
            df: DataFrame
            column: Numeric column to analyze
            num_bins: Number of histogram bins
            
        Returns:
            Distribution analysis dictionary
        """
        try:
            # Get min and max for binning
            stats = df.select(
                F.min(column).alias('min'),
                F.max(column).alias('max'),
                F.count(column).alias('count')
            ).collect()[0]
            
            min_val = float(stats['min'])
            max_val = float(stats['max'])
            total_count = stats['count']
            
            # Create histogram
            bin_width = (max_val - min_val) / num_bins
            bins = []
            
            for i in range(num_bins):
                bin_start = min_val + i * bin_width
                bin_end = min_val + (i + 1) * bin_width
                
                count = df.filter(
                    (F.col(column) >= bin_start) & (F.col(column) < bin_end)
                ).count()
                
                bins.append({
                    'bin_start': bin_start,
                    'bin_end': bin_end,
                    'count': count,
                    'percentage': (count / total_count * 100) if total_count > 0 else 0
                })
            
            # Calculate skewness and kurtosis
            skewness_val = df.select(F.skewness(column)).collect()[0][0]
            kurtosis_val = df.select(F.kurtosis(column)).collect()[0][0]
            
            return {
                'column': column,
                'histogram': bins,
                'skewness': float(skewness_val) if skewness_val else None,
                'kurtosis': float(kurtosis_val) if kurtosis_val else None,
                'min': min_val,
                'max': max_val
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing distribution for {column}: {e}", exc_info=True)
            raise
    
    def analyze_categorical_distribution(
        self,
        df: DataFrame,
        column: str,
        max_categories: int = 50
    ) -> Dict[str, Any]:
        """
        Analyze distribution of categorical column
        
        Args:
            df: DataFrame
            column: Categorical column to analyze
            max_categories: Maximum categories to include
            
        Returns:
            Distribution analysis dictionary
        """
        try:
            total_count = df.count()
            
            # Get value counts
            value_counts = (
                df.groupBy(column)
                .count()
                .orderBy(F.desc('count'))
                .limit(max_categories)
                .collect()
            )
            
            distribution = []
            for row in value_counts:
                value = row[column]
                count = row['count']
                distribution.append({
                    'value': str(value) if value is not None else 'NULL',
                    'count': count,
                    'percentage': (count / total_count * 100) if total_count > 0 else 0
                })
            
            # Calculate entropy (measure of randomness)
            entropy = self._calculate_entropy(df, column)
            
            return {
                'column': column,
                'distribution': distribution,
                'unique_values': len(value_counts),
                'entropy': entropy,
                'total_count': total_count
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing categorical distribution for {column}: {e}", exc_info=True)
            raise
    
    def _calculate_entropy(self, df: DataFrame, column: str) -> float:
        """Calculate Shannon entropy for a column"""
        try:
            import math
            
            total = df.count()
            if total == 0:
                return 0.0
            
            value_counts = df.groupBy(column).count().collect()
            
            entropy = 0.0
            for row in value_counts:
                p = row['count'] / total
                if p > 0:
                    entropy -= p * math.log2(p)
            
            return entropy
            
        except Exception as e:
            self.logger.warning(f"Error calculating entropy: {e}")
            return 0.0
    
    def detect_outliers(
        self,
        df: DataFrame,
        column: str,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Dict[str, Any]:
        """
        Detect outliers in numeric column
        
        Args:
            df: DataFrame
            column: Numeric column
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Outlier analysis dictionary
        """
        try:
            if method == 'iqr':
                return self._detect_outliers_iqr(df, column, threshold)
            elif method == 'zscore':
                return self._detect_outliers_zscore(df, column, threshold)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            self.logger.error(f"Error detecting outliers in {column}: {e}", exc_info=True)
            raise
    
    def _detect_outliers_iqr(
        self,
        df: DataFrame,
        column: str,
        threshold: float
    ) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        # Calculate Q1, Q3
        quantiles = df.select(
            F.expr(f"percentile_approx({column}, array(0.25, 0.75))").alias('quantiles')
        ).collect()[0]['quantiles']
        
        q1, q3 = quantiles[0], quantiles[1]
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        outliers_df = df.filter(
            (F.col(column) < lower_bound) | (F.col(column) > upper_bound)
        )
        
        outlier_count = outliers_df.count()
        total_count = df.count()
        
        return {
            'column': column,
            'method': 'iqr',
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': outlier_count,
            'outlier_percentage': (outlier_count / total_count * 100) if total_count > 0 else 0,
            'q1': float(q1),
            'q3': float(q3),
            'iqr': float(iqr)
        }
    
    def _detect_outliers_zscore(
        self,
        df: DataFrame,
        column: str,
        threshold: float
    ) -> Dict[str, Any]:
        """Detect outliers using Z-score method"""
        stats = df.select(
            F.mean(column).alias('mean'),
            F.stddev(column).alias('stddev')
        ).collect()[0]
        
        mean_val = float(stats['mean'])
        stddev_val = float(stats['stddev'])
        
        lower_bound = mean_val - threshold * stddev_val
        upper_bound = mean_val + threshold * stddev_val
        
        outliers_df = df.filter(
            (F.col(column) < lower_bound) | (F.col(column) > upper_bound)
        )
        
        outlier_count = outliers_df.count()
        total_count = df.count()
        
        return {
            'column': column,
            'method': 'zscore',
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'outlier_count': outlier_count,
            'outlier_percentage': (outlier_count / total_count * 100) if total_count > 0 else 0,
            'mean': mean_val,
            'stddev': stddev_val
        }


class PatternDetector:
    """Detect patterns in string data"""
    
    # Common patterns
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone_us': r'^\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
        'ssn': r'^\d{3}-\d{2}-\d{4}$',
        'zipcode_us': r'^\d{5}(-\d{4})?$',
        'url': r'^https?://[^\s]+$',
        'ipv4': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
        'date_iso': r'^\d{4}-\d{2}-\d{2}$',
        'date_us': r'^\d{2}/\d{2}/\d{4}$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'credit_card': r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$',
        'alpha': r'^[a-zA-Z]+$',
        'numeric': r'^\d+$',
        'alphanumeric': r'^[a-zA-Z0-9]+$'
    }
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def detect_patterns(
        self,
        df: DataFrame,
        column: str,
        sample_size: int = 1000,
        min_match_rate: float = 0.8
    ) -> List[str]:
        """
        Detect patterns in string column
        
        Args:
            df: DataFrame
            column: String column to analyze
            sample_size: Number of samples to check
            min_match_rate: Minimum match rate to consider pattern detected
            
        Returns:
            List of detected pattern names
        """
        try:
            # Sample data
            sample_data = (
                df.select(column)
                .filter(F.col(column).isNotNull())
                .limit(sample_size)
                .collect()
            )
            
            if not sample_data:
                return []
            
            values = [row[column] for row in sample_data]
            detected = []
            
            for pattern_name, pattern_regex in self.PATTERNS.items():
                matches = sum(1 for v in values if re.match(pattern_regex, str(v)))
                match_rate = matches / len(values)
                
                if match_rate >= min_match_rate:
                    detected.append(pattern_name)
                    self.logger.info(
                        f"Pattern '{pattern_name}' detected in column '{column}' "
                        f"with {match_rate:.1%} match rate"
                    )
            
            return detected
            
        except Exception as e:
            self.logger.error(f"Error detecting patterns in {column}: {e}", exc_info=True)
            return []
    
    def validate_pattern(
        self,
        df: DataFrame,
        column: str,
        pattern_name: str
    ) -> Dict[str, Any]:
        """
        Validate column against specific pattern
        
        Args:
            df: DataFrame
            column: Column to validate
            pattern_name: Name of pattern from PATTERNS dict
            
        Returns:
            Validation results dictionary
        """
        if pattern_name not in self.PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")
        
        pattern = self.PATTERNS[pattern_name]
        total_count = df.filter(F.col(column).isNotNull()).count()
        
        matching_count = df.filter(
            F.col(column).rlike(pattern)
        ).count()
        
        match_rate = (matching_count / total_count) if total_count > 0 else 0
        
        return {
            'column': column,
            'pattern_name': pattern_name,
            'pattern': pattern,
            'total_count': total_count,
            'matching_count': matching_count,
            'match_rate': match_rate,
            'passed': match_rate >= 0.95  # 95% threshold
        }
