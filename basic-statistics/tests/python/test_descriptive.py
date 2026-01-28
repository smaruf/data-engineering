"""
Unit tests for descriptive statistics module.
"""

import pytest
import numpy as np
from src.python.descriptive import CentralTendency, Dispersion, Shape


class TestCentralTendency:
    """Test central tendency measures."""
    
    def test_mean_simple(self):
        """Test mean with simple data."""
        data = [1, 2, 3, 4, 5]
        result = CentralTendency.mean(data)
        assert result == 3.0
    
    def test_mean_numpy_array(self):
        """Test mean with numpy array."""
        data = np.array([2, 4, 6, 8, 10])
        result = CentralTendency.mean(data)
        assert result == 6.0
    
    def test_mean_empty_raises(self):
        """Test mean with empty data raises ValueError."""
        with pytest.raises(ValueError):
            CentralTendency.mean([])
    
    def test_median_odd(self):
        """Test median with odd number of elements."""
        data = [1, 3, 5, 7, 9]
        result = CentralTendency.median(data)
        assert result == 5.0
    
    def test_median_even(self):
        """Test median with even number of elements."""
        data = [1, 2, 3, 4, 5, 6]
        result = CentralTendency.median(data)
        assert result == 3.5
    
    def test_mode_single(self):
        """Test mode with single mode."""
        data = [1, 2, 2, 3, 4, 4, 4, 5]
        result = CentralTendency.mode(data)
        assert result == 4
    
    def test_geometric_mean(self):
        """Test geometric mean."""
        data = [1, 2, 4, 8]
        result = CentralTendency.geometric_mean(data)
        expected = (1 * 2 * 4 * 8) ** (1/4)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_geometric_mean_negative_raises(self):
        """Test geometric mean with negative values raises ValueError."""
        with pytest.raises(ValueError):
            CentralTendency.geometric_mean([-1, 2, 3])
    
    def test_harmonic_mean(self):
        """Test harmonic mean."""
        data = [1, 2, 4]
        result = CentralTendency.harmonic_mean(data)
        expected = 3 / (1/1 + 1/2 + 1/4)
        assert pytest.approx(result, rel=1e-6) == expected


class TestDispersion:
    """Test dispersion measures."""
    
    def test_range(self):
        """Test range calculation."""
        data = [1, 2, 3, 4, 5]
        result = Dispersion.range(data)
        assert result == 4.0
    
    def test_variance_sample(self):
        """Test sample variance."""
        data = [1, 2, 3, 4, 5]
        result = Dispersion.variance(data, ddof=1)
        expected = np.var(data, ddof=1)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_variance_population(self):
        """Test population variance."""
        data = [1, 2, 3, 4, 5]
        result = Dispersion.variance(data, ddof=0)
        expected = np.var(data, ddof=0)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_std_dev(self):
        """Test standard deviation."""
        data = [1, 2, 3, 4, 5]
        result = Dispersion.std_dev(data)
        expected = np.std(data, ddof=1)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_mad(self):
        """Test mean absolute deviation."""
        data = [1, 2, 3, 4, 5]
        result = Dispersion.mad(data)
        expected = np.mean(np.abs(data - np.mean(data)))
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_iqr(self):
        """Test interquartile range."""
        data = list(range(1, 11))  # 1 to 10
        result = Dispersion.iqr(data)
        q75, q25 = np.percentile(data, [75, 25])
        expected = q75 - q25
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_coefficient_of_variation(self):
        """Test coefficient of variation."""
        data = [10, 12, 14, 16, 18]
        result = Dispersion.coefficient_of_variation(data)
        expected = (np.std(data, ddof=1) / np.mean(data)) * 100
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_cv_zero_mean_raises(self):
        """Test CV with zero mean raises ValueError."""
        data = [-1, 0, 1]
        with pytest.raises(ValueError):
            Dispersion.coefficient_of_variation(data)
    
    def test_welford_variance(self):
        """Test Welford's algorithm for variance."""
        data = [1, 2, 3, 4, 5]
        result = Dispersion.welford_variance(data)
        expected = np.var(data, ddof=1)
        assert pytest.approx(result, rel=1e-6) == expected


class TestShape:
    """Test shape measures."""
    
    def test_skewness_symmetric(self):
        """Test skewness for symmetric data."""
        data = [1, 2, 3, 4, 5]
        result = Shape.skewness(data)
        assert pytest.approx(result, abs=0.1) == 0.0
    
    def test_skewness_right_skewed(self):
        """Test skewness for right-skewed data."""
        data = [1, 2, 3, 4, 100]
        result = Shape.skewness(data)
        assert result > 0
    
    def test_kurtosis_normal(self):
        """Test kurtosis (excess) for approximately normal data."""
        np.random.seed(42)
        data = np.random.normal(0, 1, 1000)
        result = Shape.kurtosis(data)
        # Excess kurtosis should be close to 0 for normal distribution
        assert pytest.approx(result, abs=0.5) == 0.0
    
    def test_percentile(self):
        """Test percentile calculation."""
        data = list(range(1, 11))
        result = Shape.percentile(data, 50)
        assert result == 5.5
    
    def test_percentile_invalid_raises(self):
        """Test percentile with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            Shape.percentile([1, 2, 3], 150)
    
    def test_quantile(self):
        """Test quantile calculation."""
        data = list(range(1, 11))
        result = Shape.quantile(data, 0.5)
        expected = np.quantile(data, 0.5)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_quartiles(self):
        """Test quartiles calculation."""
        data = list(range(1, 10))
        q1, q2, q3 = Shape.quartiles(data)
        assert q2 == 5.0  # Median
        assert q1 < q2 < q3
    
    def test_five_number_summary(self):
        """Test five-number summary."""
        data = list(range(1, 10))
        minimum, q1, median, q3, maximum = Shape.five_number_summary(data)
        assert minimum == 1.0
        assert maximum == 9.0
        assert median == 5.0
        assert q1 < median < q3
    
    def test_detect_outliers_iqr(self):
        """Test outlier detection using IQR method."""
        data = [1, 2, 3, 4, 5, 100]
        indices, values = Shape.detect_outliers_iqr(data)
        assert 100 in values
        assert len(indices) > 0
    
    def test_z_scores(self):
        """Test z-score calculation."""
        data = [1, 2, 3, 4, 5]
        result = Shape.z_scores(data)
        # Z-scores should have mean 0 and std 1
        assert pytest.approx(np.mean(result), abs=1e-10) == 0.0
        assert pytest.approx(np.std(result, ddof=1), abs=1e-10) == 1.0


# Property-based tests
from hypothesis import given
from hypothesis import strategies as st

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6), min_size=2))
def test_variance_non_negative(data):
    """Property: Variance should always be non-negative."""
    result = Dispersion.variance(data)
    assert result >= 0 or np.isnan(result)

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6), min_size=2))
def test_std_dev_non_negative(data):
    """Property: Standard deviation should always be non-negative."""
    result = Dispersion.std_dev(data)
    assert result >= 0 or np.isnan(result)
