"""
Quality Metrics Module

Quality metrics calculation and tracking with support for:
- Data completeness metrics
- Data accuracy metrics
- Data consistency metrics
- Data timeliness metrics
- Aggregate quality scores
- Historical tracking
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from shared.utils.logger import get_logger
from shared.utils.helpers import to_json, get_timestamp

logger = get_logger(__name__)


class MetricType(Enum):
    """Types of quality metrics"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"


@dataclass
class QualityMetric:
    """Individual quality metric"""
    metric_name: str
    metric_type: MetricType
    value: float
    target: Optional[float] = None
    threshold: Optional[float] = None
    status: str = "unknown"  # passed, failed, warning
    dimension: Optional[str] = None
    column: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Calculate status based on thresholds"""
        if self.target is not None and self.threshold is not None:
            if self.value >= self.target:
                self.status = "passed"
            elif self.value >= self.threshold:
                self.status = "warning"
            else:
                self.status = "failed"
    
    @property
    def passed(self) -> bool:
        """Check if metric passed"""
        return self.status == "passed"
    
    @property
    def score_percentage(self) -> float:
        """Get score as percentage"""
        return self.value * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'score_percentage': self.score_percentage,
            'target': self.target,
            'threshold': self.threshold,
            'status': self.status,
            'dimension': self.dimension,
            'column': self.column,
            'details': self.details,
            'timestamp': self.timestamp
        }


@dataclass
class QualityReport:
    """Comprehensive quality report"""
    dataset_name: str
    row_count: int
    column_count: int
    metrics: List[QualityMetric]
    overall_score: float
    dimension_scores: Dict[str, float]
    passed_metrics: int
    failed_metrics: int
    warning_metrics: int
    report_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'dataset_name': self.dataset_name,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'overall_score': self.overall_score,
            'overall_score_percentage': self.overall_score * 100,
            'dimension_scores': self.dimension_scores,
            'passed_metrics': self.passed_metrics,
            'failed_metrics': self.failed_metrics,
            'warning_metrics': self.warning_metrics,
            'total_metrics': len(self.metrics),
            'metrics': [m.to_dict() for m in self.metrics],
            'report_timestamp': self.report_timestamp,
            'metadata': self.metadata
        }
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert to JSON string"""
        return to_json(self.to_dict(), pretty=pretty)


class QualityMetricsCalculator:
    """Calculate quality metrics for DataFrames"""
    
    def __init__(
        self,
        spark: Optional[SparkSession] = None,
        default_target: float = 0.95,
        default_threshold: float = 0.80
    ):
        self.logger = get_logger(__name__)
        self.spark = spark or SparkSession.builder.getOrCreate()
        self.default_target = default_target
        self.default_threshold = default_threshold
    
    def calculate_completeness(
        self,
        df: DataFrame,
        columns: Optional[List[str]] = None,
        target: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> List[QualityMetric]:
        """
        Calculate completeness metrics (non-null rate)
        
        Args:
            df: DataFrame to analyze
            columns: Columns to check (None = all columns)
            target: Target completeness rate
            threshold: Warning threshold
            
        Returns:
            List of QualityMetrics
        """
        try:
            target = target or self.default_target
            threshold = threshold or self.default_threshold
            columns = columns or df.columns
            
            total_count = df.count()
            metrics = []
            
            for col in columns:
                non_null_count = df.filter(F.col(col).isNotNull()).count()
                completeness = non_null_count / total_count if total_count > 0 else 0
                
                metric = QualityMetric(
                    metric_name=f"completeness_{col}",
                    metric_type=MetricType.COMPLETENESS,
                    value=completeness,
                    target=target,
                    threshold=threshold,
                    column=col,
                    details={
                        'non_null_count': non_null_count,
                        'null_count': total_count - non_null_count,
                        'total_count': total_count
                    }
                )
                metrics.append(metric)
            
            # Overall completeness
            overall_completeness = sum(m.value for m in metrics) / len(metrics) if metrics else 0
            metrics.append(QualityMetric(
                metric_name="completeness_overall",
                metric_type=MetricType.COMPLETENESS,
                value=overall_completeness,
                target=target,
                threshold=threshold,
                details={'columns_analyzed': len(columns)}
            ))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating completeness: {e}", exc_info=True)
            raise
    
    def calculate_uniqueness(
        self,
        df: DataFrame,
        columns: List[str],
        target: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> QualityMetric:
        """
        Calculate uniqueness metric
        
        Args:
            df: DataFrame to analyze
            columns: Columns that should be unique
            target: Target uniqueness rate
            threshold: Warning threshold
            
        Returns:
            QualityMetric
        """
        try:
            target = target or self.default_target
            threshold = threshold or self.default_threshold
            
            total_count = df.count()
            distinct_count = df.select(columns).distinct().count()
            uniqueness = distinct_count / total_count if total_count > 0 else 0
            
            return QualityMetric(
                metric_name=f"uniqueness_{'_'.join(columns)}",
                metric_type=MetricType.UNIQUENESS,
                value=uniqueness,
                target=target,
                threshold=threshold,
                column=', '.join(columns),
                details={
                    'total_count': total_count,
                    'distinct_count': distinct_count,
                    'duplicate_count': total_count - distinct_count
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating uniqueness: {e}", exc_info=True)
            raise
    
    def calculate_validity(
        self,
        df: DataFrame,
        column: str,
        valid_condition: str,
        target: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> QualityMetric:
        """
        Calculate validity metric based on condition
        
        Args:
            df: DataFrame to analyze
            column: Column to check
            valid_condition: SQL condition for valid values
            target: Target validity rate
            threshold: Warning threshold
            
        Returns:
            QualityMetric
        """
        try:
            target = target or self.default_target
            threshold = threshold or self.default_threshold
            
            total_count = df.count()
            valid_count = df.filter(valid_condition).count()
            validity = valid_count / total_count if total_count > 0 else 0
            
            return QualityMetric(
                metric_name=f"validity_{column}",
                metric_type=MetricType.VALIDITY,
                value=validity,
                target=target,
                threshold=threshold,
                column=column,
                details={
                    'valid_count': valid_count,
                    'invalid_count': total_count - valid_count,
                    'total_count': total_count,
                    'condition': valid_condition
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating validity: {e}", exc_info=True)
            raise
    
    def calculate_consistency(
        self,
        df: DataFrame,
        check_name: str,
        consistency_condition: str,
        target: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> QualityMetric:
        """
        Calculate consistency metric based on cross-column rules
        
        Args:
            df: DataFrame to analyze
            check_name: Name of the consistency check
            consistency_condition: SQL condition for consistency
            target: Target consistency rate
            threshold: Warning threshold
            
        Returns:
            QualityMetric
        """
        try:
            target = target or self.default_target
            threshold = threshold or self.default_threshold
            
            total_count = df.count()
            consistent_count = df.filter(consistency_condition).count()
            consistency = consistent_count / total_count if total_count > 0 else 0
            
            return QualityMetric(
                metric_name=f"consistency_{check_name}",
                metric_type=MetricType.CONSISTENCY,
                value=consistency,
                target=target,
                threshold=threshold,
                details={
                    'consistent_count': consistent_count,
                    'inconsistent_count': total_count - consistent_count,
                    'total_count': total_count,
                    'condition': consistency_condition
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency: {e}", exc_info=True)
            raise
    
    def calculate_timeliness(
        self,
        df: DataFrame,
        timestamp_column: str,
        max_age_hours: int = 24,
        target: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> QualityMetric:
        """
        Calculate timeliness metric
        
        Args:
            df: DataFrame to analyze
            timestamp_column: Column containing timestamps
            max_age_hours: Maximum acceptable age in hours
            target: Target timeliness rate
            threshold: Warning threshold
            
        Returns:
            QualityMetric
        """
        try:
            target = target or self.default_target
            threshold = threshold or self.default_threshold
            
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            total_count = df.count()
            timely_count = df.filter(
                F.col(timestamp_column) >= F.lit(cutoff_time)
            ).count()
            
            timeliness = timely_count / total_count if total_count > 0 else 0
            
            # Get oldest and newest records
            time_stats = df.select(
                F.min(timestamp_column).alias('oldest'),
                F.max(timestamp_column).alias('newest')
            ).collect()[0]
            
            return QualityMetric(
                metric_name=f"timeliness_{timestamp_column}",
                metric_type=MetricType.TIMELINESS,
                value=timeliness,
                target=target,
                threshold=threshold,
                column=timestamp_column,
                details={
                    'timely_count': timely_count,
                    'stale_count': total_count - timely_count,
                    'total_count': total_count,
                    'max_age_hours': max_age_hours,
                    'oldest_record': str(time_stats['oldest']),
                    'newest_record': str(time_stats['newest'])
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating timeliness: {e}", exc_info=True)
            raise
    
    def calculate_accuracy(
        self,
        df: DataFrame,
        column: str,
        reference_df: DataFrame,
        reference_column: str,
        join_keys: List[str],
        target: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> QualityMetric:
        """
        Calculate accuracy by comparing with reference data
        
        Args:
            df: DataFrame to analyze
            column: Column to check accuracy
            reference_df: Reference DataFrame
            reference_column: Reference column
            join_keys: Keys to join on
            target: Target accuracy rate
            threshold: Warning threshold
            
        Returns:
            QualityMetric
        """
        try:
            target = target or self.default_target
            threshold = threshold or self.default_threshold
            
            # Join with reference data
            joined = df.alias('a').join(
                reference_df.alias('b'),
                on=join_keys,
                how='inner'
            )
            
            total_count = joined.count()
            accurate_count = joined.filter(
                F.col(f'a.{column}') == F.col(f'b.{reference_column}')
            ).count()
            
            accuracy = accurate_count / total_count if total_count > 0 else 0
            
            return QualityMetric(
                metric_name=f"accuracy_{column}",
                metric_type=MetricType.ACCURACY,
                value=accuracy,
                target=target,
                threshold=threshold,
                column=column,
                details={
                    'accurate_count': accurate_count,
                    'inaccurate_count': total_count - accurate_count,
                    'total_count': total_count,
                    'reference_column': reference_column
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating accuracy: {e}", exc_info=True)
            raise
    
    def generate_report(
        self,
        df: DataFrame,
        dataset_name: str,
        metrics: List[QualityMetric],
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityReport:
        """
        Generate comprehensive quality report
        
        Args:
            df: DataFrame analyzed
            dataset_name: Name of the dataset
            metrics: List of calculated metrics
            metadata: Optional metadata
            
        Returns:
            QualityReport
        """
        try:
            row_count = df.count()
            column_count = len(df.columns)
            
            # Calculate status counts
            passed = sum(1 for m in metrics if m.status == "passed")
            failed = sum(1 for m in metrics if m.status == "failed")
            warning = sum(1 for m in metrics if m.status == "warning")
            
            # Calculate overall score
            overall_score = sum(m.value for m in metrics) / len(metrics) if metrics else 0
            
            # Calculate dimension scores
            dimension_scores = {}
            for metric_type in MetricType:
                type_metrics = [m for m in metrics if m.metric_type == metric_type]
                if type_metrics:
                    dimension_scores[metric_type.value] = sum(m.value for m in type_metrics) / len(type_metrics)
            
            return QualityReport(
                dataset_name=dataset_name,
                row_count=row_count,
                column_count=column_count,
                metrics=metrics,
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                passed_metrics=passed,
                failed_metrics=failed,
                warning_metrics=warning,
                metadata=metadata or {}
            )
            
        except Exception as e:
            self.logger.error(f"Error generating quality report: {e}", exc_info=True)
            raise
    
    def calculate_all_metrics(
        self,
        df: DataFrame,
        dataset_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> QualityReport:
        """
        Calculate all standard metrics based on configuration
        
        Args:
            df: DataFrame to analyze
            dataset_name: Name of the dataset
            config: Configuration dictionary with metric specifications
            
        Returns:
            QualityReport
        """
        try:
            config = config or {}
            all_metrics = []
            
            # Completeness metrics
            if config.get('check_completeness', True):
                completeness_cols = config.get('completeness_columns', df.columns)
                all_metrics.extend(self.calculate_completeness(df, completeness_cols))
            
            # Uniqueness metrics
            if 'uniqueness_columns' in config:
                for unique_cols in config['uniqueness_columns']:
                    metric = self.calculate_uniqueness(df, unique_cols)
                    all_metrics.append(metric)
            
            # Validity metrics
            if 'validity_checks' in config:
                for check in config['validity_checks']:
                    metric = self.calculate_validity(
                        df,
                        check['column'],
                        check['condition'],
                        check.get('target'),
                        check.get('threshold')
                    )
                    all_metrics.append(metric)
            
            # Consistency metrics
            if 'consistency_checks' in config:
                for check in config['consistency_checks']:
                    metric = self.calculate_consistency(
                        df,
                        check['name'],
                        check['condition'],
                        check.get('target'),
                        check.get('threshold')
                    )
                    all_metrics.append(metric)
            
            # Timeliness metrics
            if 'timeliness_checks' in config:
                for check in config['timeliness_checks']:
                    metric = self.calculate_timeliness(
                        df,
                        check['column'],
                        check.get('max_age_hours', 24),
                        check.get('target'),
                        check.get('threshold')
                    )
                    all_metrics.append(metric)
            
            return self.generate_report(
                df,
                dataset_name,
                all_metrics,
                metadata={'config': config}
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating all metrics: {e}", exc_info=True)
            raise


class MetricsTracker:
    """Track quality metrics over time"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.storage_path = storage_path
        self.metrics_history: List[Dict[str, Any]] = []
    
    def record_metrics(
        self,
        report: QualityReport,
        run_id: Optional[str] = None
    ) -> None:
        """
        Record quality metrics
        
        Args:
            report: QualityReport to record
            run_id: Optional run identifier
        """
        try:
            run_id = run_id or get_timestamp()
            
            record = {
                'run_id': run_id,
                'dataset_name': report.dataset_name,
                'timestamp': report.report_timestamp,
                'overall_score': report.overall_score,
                'dimension_scores': report.dimension_scores,
                'row_count': report.row_count,
                'passed_metrics': report.passed_metrics,
                'failed_metrics': report.failed_metrics,
                'warning_metrics': report.warning_metrics
            }
            
            self.metrics_history.append(record)
            
            if self.storage_path:
                self._save_to_storage(record)
            
            self.logger.info(f"Recorded metrics for {report.dataset_name}, run: {run_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording metrics: {e}", exc_info=True)
    
    def _save_to_storage(self, record: Dict[str, Any]) -> None:
        """Save metrics to storage"""
        try:
            # Implementation depends on storage backend
            # Could be: Delta Lake, PostgreSQL, MongoDB, etc.
            self.logger.info(f"Saving metrics to {self.storage_path}")
            # TODO: Implement storage-specific logic
        except Exception as e:
            self.logger.error(f"Error saving metrics to storage: {e}", exc_info=True)
    
    def get_trend(
        self,
        dataset_name: str,
        metric_name: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get metric trend over time
        
        Args:
            dataset_name: Dataset to analyze
            metric_name: Metric to track
            days: Number of days to look back
            
        Returns:
            List of historical metric values
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        trend = [
            {
                'timestamp': record['timestamp'],
                'value': record['dimension_scores'].get(metric_name) or record.get(metric_name, 0)
            }
            for record in self.metrics_history
            if record['dataset_name'] == dataset_name
            and datetime.fromisoformat(record['timestamp']) >= cutoff_date
        ]
        
        return sorted(trend, key=lambda x: x['timestamp'])
    
    def get_summary(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get summary statistics for a dataset
        
        Args:
            dataset_name: Dataset to summarize
            
        Returns:
            Summary statistics dictionary
        """
        records = [r for r in self.metrics_history if r['dataset_name'] == dataset_name]
        
        if not records:
            return {'error': 'No records found'}
        
        scores = [r['overall_score'] for r in records]
        
        return {
            'dataset_name': dataset_name,
            'total_runs': len(records),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'latest_score': records[-1]['overall_score'],
            'latest_timestamp': records[-1]['timestamp']
        }
