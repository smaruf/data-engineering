"""
Data Validation Module

Comprehensive data validation with support for:
- Schema validation
- Data type validation
- Range checks
- Null checks
- Uniqueness checks
- Custom validation rules
- Great Expectations integration
"""

from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, DataType

try:
    import great_expectations as gx
    from great_expectations.core.batch import RuntimeBatchRequest
    from great_expectations.dataset import SparkDFDataset
    GX_AVAILABLE = True
except ImportError:
    GX_AVAILABLE = False

from shared.utils.logger import get_logger
from shared.utils.helpers import to_json, get_timestamp

logger = get_logger(__name__)


class ValidationStatus(Enum):
    """Validation status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    rule_name: str
    status: ValidationStatus
    message: str
    column: Optional[str] = None
    failed_count: int = 0
    total_count: int = 0
    failed_records: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def passed(self) -> bool:
        """Check if validation passed"""
        return self.status == ValidationStatus.PASSED
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate"""
        if self.total_count == 0:
            return 0.0
        return self.failed_count / self.total_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'rule_name': self.rule_name,
            'status': self.status.value,
            'message': self.message,
            'column': self.column,
            'failed_count': self.failed_count,
            'total_count': self.total_count,
            'failure_rate': self.failure_rate,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


@dataclass
class ValidationRule:
    """Base class for validation rules"""
    name: str
    description: str
    severity: str = "error"  # error, warning
    column: Optional[str] = None
    enabled: bool = True
    
    def validate(self, df: DataFrame) -> ValidationResult:
        """
        Execute validation rule
        
        Args:
            df: PySpark DataFrame to validate
            
        Returns:
            ValidationResult
        """
        raise NotImplementedError("Subclasses must implement validate method")


class SchemaValidator:
    """Schema validation for DataFrames"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def validate_schema(
        self,
        df: DataFrame,
        expected_schema: StructType,
        strict: bool = True
    ) -> ValidationResult:
        """
        Validate DataFrame schema against expected schema
        
        Args:
            df: DataFrame to validate
            expected_schema: Expected schema
            strict: If True, requires exact match; if False, allows extra columns
            
        Returns:
            ValidationResult
        """
        try:
            actual_schema = df.schema
            issues = []
            
            expected_fields = {f.name: f for f in expected_schema.fields}
            actual_fields = {f.name: f for f in actual_schema.fields}
            
            # Check for missing columns
            missing_cols = set(expected_fields.keys()) - set(actual_fields.keys())
            if missing_cols:
                issues.append(f"Missing columns: {', '.join(missing_cols)}")
            
            # Check for extra columns (if strict mode)
            if strict:
                extra_cols = set(actual_fields.keys()) - set(expected_fields.keys())
                if extra_cols:
                    issues.append(f"Extra columns: {', '.join(extra_cols)}")
            
            # Check data types for common columns
            for col_name in set(expected_fields.keys()) & set(actual_fields.keys()):
                expected_type = expected_fields[col_name].dataType
                actual_type = actual_fields[col_name].dataType
                
                if not self._types_match(expected_type, actual_type):
                    issues.append(
                        f"Column '{col_name}': expected {expected_type}, got {actual_type}"
                    )
            
            if issues:
                return ValidationResult(
                    rule_name="schema_validation",
                    status=ValidationStatus.FAILED,
                    message="; ".join(issues),
                    metadata={
                        'expected_schema': str(expected_schema),
                        'actual_schema': str(actual_schema)
                    }
                )
            
            return ValidationResult(
                rule_name="schema_validation",
                status=ValidationStatus.PASSED,
                message="Schema validation passed"
            )
            
        except Exception as e:
            self.logger.error(f"Schema validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name="schema_validation",
                status=ValidationStatus.FAILED,
                message=f"Schema validation error: {str(e)}"
            )
    
    def _types_match(self, expected: DataType, actual: DataType) -> bool:
        """Check if data types match"""
        return type(expected) == type(actual)
    
    def infer_and_validate(
        self,
        df: DataFrame,
        column_types: Dict[str, str]
    ) -> ValidationResult:
        """
        Validate that columns match expected types
        
        Args:
            df: DataFrame to validate
            column_types: Dictionary of column_name -> type_name
            
        Returns:
            ValidationResult
        """
        issues = []
        
        for col_name, expected_type in column_types.items():
            if col_name not in df.columns:
                issues.append(f"Column '{col_name}' not found")
                continue
            
            actual_type = dict(df.dtypes)[col_name]
            if expected_type.lower() not in actual_type.lower():
                issues.append(
                    f"Column '{col_name}': expected type containing '{expected_type}', "
                    f"got '{actual_type}'"
                )
        
        if issues:
            return ValidationResult(
                rule_name="type_validation",
                status=ValidationStatus.FAILED,
                message="; ".join(issues)
            )
        
        return ValidationResult(
            rule_name="type_validation",
            status=ValidationStatus.PASSED,
            message="Type validation passed"
        )


class DataValidator:
    """Main data validation orchestrator"""
    
    def __init__(self, spark: Optional[SparkSession] = None):
        self.logger = get_logger(__name__)
        self.spark = spark or SparkSession.builder.getOrCreate()
        self.schema_validator = SchemaValidator()
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> 'DataValidator':
        """Add a validation rule"""
        self.rules.append(rule)
        return self
    
    def validate_not_null(
        self,
        df: DataFrame,
        columns: List[str],
        threshold: float = 0.0
    ) -> ValidationResult:
        """
        Validate that columns don't have null values
        
        Args:
            df: DataFrame to validate
            columns: Columns to check
            threshold: Maximum acceptable null rate (0.0 = no nulls allowed)
            
        Returns:
            ValidationResult
        """
        try:
            total_count = df.count()
            failures = []
            
            for col in columns:
                if col not in df.columns:
                    failures.append(f"Column '{col}' not found")
                    continue
                
                null_count = df.filter(F.col(col).isNull()).count()
                null_rate = null_count / total_count if total_count > 0 else 0
                
                if null_rate > threshold:
                    failures.append(
                        f"Column '{col}' has {null_count} nulls "
                        f"({null_rate:.2%} > threshold {threshold:.2%})"
                    )
            
            if failures:
                return ValidationResult(
                    rule_name="not_null_validation",
                    status=ValidationStatus.FAILED,
                    message="; ".join(failures),
                    total_count=total_count
                )
            
            return ValidationResult(
                rule_name="not_null_validation",
                status=ValidationStatus.PASSED,
                message=f"All {len(columns)} columns passed null check",
                total_count=total_count
            )
            
        except Exception as e:
            self.logger.error(f"Null validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name="not_null_validation",
                status=ValidationStatus.FAILED,
                message=f"Error during null validation: {str(e)}"
            )
    
    def validate_unique(
        self,
        df: DataFrame,
        columns: Union[str, List[str]],
        sample_duplicates: int = 10
    ) -> ValidationResult:
        """
        Validate uniqueness of column(s)
        
        Args:
            df: DataFrame to validate
            columns: Column or list of columns to check
            sample_duplicates: Number of duplicate samples to collect
            
        Returns:
            ValidationResult
        """
        try:
            if isinstance(columns, str):
                columns = [columns]
            
            total_count = df.count()
            distinct_count = df.select(columns).distinct().count()
            duplicate_count = total_count - distinct_count
            
            if duplicate_count > 0:
                # Get sample duplicates
                duplicates_df = (
                    df.groupBy(columns)
                    .count()
                    .filter(F.col("count") > 1)
                    .orderBy(F.desc("count"))
                    .limit(sample_duplicates)
                )
                
                duplicate_samples = [
                    row.asDict() for row in duplicates_df.collect()
                ]
                
                return ValidationResult(
                    rule_name="uniqueness_validation",
                    status=ValidationStatus.FAILED,
                    message=f"Found {duplicate_count} duplicate records",
                    column=", ".join(columns),
                    failed_count=duplicate_count,
                    total_count=total_count,
                    failed_records=duplicate_samples,
                    metadata={'duplicate_samples': duplicate_samples}
                )
            
            return ValidationResult(
                rule_name="uniqueness_validation",
                status=ValidationStatus.PASSED,
                message="All records are unique",
                column=", ".join(columns),
                total_count=total_count
            )
            
        except Exception as e:
            self.logger.error(f"Uniqueness validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name="uniqueness_validation",
                status=ValidationStatus.FAILED,
                message=f"Error during uniqueness validation: {str(e)}"
            )
    
    def validate_range(
        self,
        df: DataFrame,
        column: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        sample_violations: int = 10
    ) -> ValidationResult:
        """
        Validate that numeric column values are within range
        
        Args:
            df: DataFrame to validate
            column: Column to check
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
            sample_violations: Number of violation samples to collect
            
        Returns:
            ValidationResult
        """
        try:
            if column not in df.columns:
                return ValidationResult(
                    rule_name="range_validation",
                    status=ValidationStatus.FAILED,
                    message=f"Column '{column}' not found",
                    column=column
                )
            
            total_count = df.count()
            violations_filter = None
            
            if min_value is not None and max_value is not None:
                violations_filter = (F.col(column) < min_value) | (F.col(column) > max_value)
                range_desc = f"[{min_value}, {max_value}]"
            elif min_value is not None:
                violations_filter = F.col(column) < min_value
                range_desc = f">= {min_value}"
            elif max_value is not None:
                violations_filter = F.col(column) > max_value
                range_desc = f"<= {max_value}"
            else:
                return ValidationResult(
                    rule_name="range_validation",
                    status=ValidationStatus.SKIPPED,
                    message="No range specified",
                    column=column
                )
            
            violations_df = df.filter(violations_filter)
            violation_count = violations_df.count()
            
            if violation_count > 0:
                samples = [
                    row.asDict() 
                    for row in violations_df.limit(sample_violations).collect()
                ]
                
                return ValidationResult(
                    rule_name="range_validation",
                    status=ValidationStatus.FAILED,
                    message=f"{violation_count} values out of range {range_desc}",
                    column=column,
                    failed_count=violation_count,
                    total_count=total_count,
                    failed_records=samples
                )
            
            return ValidationResult(
                rule_name="range_validation",
                status=ValidationStatus.PASSED,
                message=f"All values within range {range_desc}",
                column=column,
                total_count=total_count
            )
            
        except Exception as e:
            self.logger.error(f"Range validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name="range_validation",
                status=ValidationStatus.FAILED,
                message=f"Error during range validation: {str(e)}",
                column=column
            )
    
    def validate_pattern(
        self,
        df: DataFrame,
        column: str,
        pattern: str,
        sample_violations: int = 10
    ) -> ValidationResult:
        """
        Validate that string column matches regex pattern
        
        Args:
            df: DataFrame to validate
            column: Column to check
            pattern: Regex pattern
            sample_violations: Number of violation samples to collect
            
        Returns:
            ValidationResult
        """
        try:
            if column not in df.columns:
                return ValidationResult(
                    rule_name="pattern_validation",
                    status=ValidationStatus.FAILED,
                    message=f"Column '{column}' not found",
                    column=column
                )
            
            total_count = df.count()
            violations_df = df.filter(~F.col(column).rlike(pattern))
            violation_count = violations_df.count()
            
            if violation_count > 0:
                samples = [
                    row.asDict()
                    for row in violations_df.limit(sample_violations).collect()
                ]
                
                return ValidationResult(
                    rule_name="pattern_validation",
                    status=ValidationStatus.FAILED,
                    message=f"{violation_count} values don't match pattern '{pattern}'",
                    column=column,
                    failed_count=violation_count,
                    total_count=total_count,
                    failed_records=samples
                )
            
            return ValidationResult(
                rule_name="pattern_validation",
                status=ValidationStatus.PASSED,
                message=f"All values match pattern '{pattern}'",
                column=column,
                total_count=total_count
            )
            
        except Exception as e:
            self.logger.error(f"Pattern validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name="pattern_validation",
                status=ValidationStatus.FAILED,
                message=f"Error during pattern validation: {str(e)}",
                column=column
            )
    
    def validate_custom(
        self,
        df: DataFrame,
        rule_name: str,
        condition: str,
        sample_violations: int = 10
    ) -> ValidationResult:
        """
        Validate using custom SQL condition
        
        Args:
            df: DataFrame to validate
            rule_name: Name of the validation rule
            condition: SQL condition (e.g., "age >= 18 AND age <= 100")
            sample_violations: Number of violation samples to collect
            
        Returns:
            ValidationResult
        """
        try:
            total_count = df.count()
            violations_df = df.filter(f"NOT ({condition})")
            violation_count = violations_df.count()
            
            if violation_count > 0:
                samples = [
                    row.asDict()
                    for row in violations_df.limit(sample_violations).collect()
                ]
                
                return ValidationResult(
                    rule_name=rule_name,
                    status=ValidationStatus.FAILED,
                    message=f"{violation_count} records failed condition: {condition}",
                    failed_count=violation_count,
                    total_count=total_count,
                    failed_records=samples
                )
            
            return ValidationResult(
                rule_name=rule_name,
                status=ValidationStatus.PASSED,
                message=f"All records satisfy condition: {condition}",
                total_count=total_count
            )
            
        except Exception as e:
            self.logger.error(f"Custom validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name=rule_name,
                status=ValidationStatus.FAILED,
                message=f"Error during custom validation: {str(e)}"
            )
    
    def validate_all(self, df: DataFrame) -> List[ValidationResult]:
        """
        Execute all configured validation rules
        
        Args:
            df: DataFrame to validate
            
        Returns:
            List of ValidationResults
        """
        results = []
        
        for rule in self.rules:
            if not rule.enabled:
                self.logger.info(f"Skipping disabled rule: {rule.name}")
                continue
            
            self.logger.info(f"Executing validation rule: {rule.name}")
            try:
                result = rule.validate(df)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error executing rule {rule.name}: {e}", exc_info=True)
                results.append(ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.FAILED,
                    message=f"Rule execution error: {str(e)}"
                ))
        
        return results
    
    def get_validation_summary(
        self,
        results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """
        Generate validation summary
        
        Args:
            results: List of validation results
            
        Returns:
            Summary dictionary
        """
        total_rules = len(results)
        passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        skipped = sum(1 for r in results if r.status == ValidationStatus.SKIPPED)
        
        return {
            'total_rules': total_rules,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'skipped': skipped,
            'success_rate': passed / total_rules if total_rules > 0 else 0,
            'results': [r.to_dict() for r in results],
            'timestamp': get_timestamp('%Y-%m-%d %H:%M:%S')
        }


class GreatExpectationsValidator:
    """Integration with Great Expectations for advanced validation"""
    
    def __init__(self, context_root_dir: Optional[str] = None):
        if not GX_AVAILABLE:
            raise ImportError(
                "Great Expectations not available. "
                "Install with: pip install great-expectations"
            )
        
        self.logger = get_logger(__name__)
        self.context = self._setup_context(context_root_dir)
    
    def _setup_context(self, context_root_dir: Optional[str]):
        """Setup Great Expectations context"""
        try:
            if context_root_dir:
                context = gx.get_context(context_root_dir=context_root_dir)
            else:
                context = gx.get_context()
            
            self.logger.info("Great Expectations context initialized")
            return context
        except Exception as e:
            self.logger.error(f"Failed to initialize GX context: {e}")
            raise
    
    def validate_with_suite(
        self,
        df: DataFrame,
        expectation_suite_name: str,
        batch_identifier: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate DataFrame using Great Expectations suite
        
        Args:
            df: DataFrame to validate
            expectation_suite_name: Name of expectation suite
            batch_identifier: Optional batch identifier
            
        Returns:
            ValidationResult
        """
        try:
            batch_identifier = batch_identifier or f"batch_{get_timestamp()}"
            
            # Create batch request
            batch_request = RuntimeBatchRequest(
                datasource_name="spark_datasource",
                data_connector_name="runtime_data_connector",
                data_asset_name=batch_identifier,
                runtime_parameters={"batch_data": df},
                batch_identifiers={"default_identifier_name": batch_identifier}
            )
            
            # Get validator
            validator = self.context.get_validator(
                batch_request=batch_request,
                expectation_suite_name=expectation_suite_name
            )
            
            # Run validation
            results = validator.validate()
            
            success = results.success
            statistics = results.statistics
            
            failed_expectations = [
                exp for exp in results.results
                if not exp.success
            ]
            
            if success:
                return ValidationResult(
                    rule_name=f"gx_suite_{expectation_suite_name}",
                    status=ValidationStatus.PASSED,
                    message=f"Great Expectations suite passed",
                    metadata={
                        'statistics': statistics,
                        'suite_name': expectation_suite_name
                    }
                )
            else:
                return ValidationResult(
                    rule_name=f"gx_suite_{expectation_suite_name}",
                    status=ValidationStatus.FAILED,
                    message=f"{len(failed_expectations)} expectations failed",
                    metadata={
                        'statistics': statistics,
                        'failed_expectations': [
                            {
                                'expectation_type': exp.expectation_config.expectation_type,
                                'kwargs': exp.expectation_config.kwargs
                            }
                            for exp in failed_expectations
                        ]
                    }
                )
                
        except Exception as e:
            self.logger.error(f"Great Expectations validation error: {e}", exc_info=True)
            return ValidationResult(
                rule_name=f"gx_suite_{expectation_suite_name}",
                status=ValidationStatus.FAILED,
                message=f"Validation error: {str(e)}"
            )
    
    def create_expectation_suite(
        self,
        suite_name: str,
        expectations: List[Dict[str, Any]]
    ) -> None:
        """
        Create a new expectation suite
        
        Args:
            suite_name: Name for the suite
            expectations: List of expectation configurations
        """
        try:
            suite = self.context.add_expectation_suite(
                expectation_suite_name=suite_name
            )
            
            for exp_config in expectations:
                suite.add_expectation(**exp_config)
            
            self.context.save_expectation_suite(suite)
            self.logger.info(f"Created expectation suite: {suite_name}")
            
        except Exception as e:
            self.logger.error(f"Error creating expectation suite: {e}", exc_info=True)
            raise
