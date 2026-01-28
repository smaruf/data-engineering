# Python Implementation Guide

## Overview

This guide covers the Python implementation of statistical functions, from basic descriptive statistics to advanced inference methods.

## 1. Project Structure

```
src/python/
├── __init__.py
├── descriptive/
│   ├── __init__.py
│   ├── central_tendency.py
│   ├── dispersion.py
│   └── shape.py
├── probability/
│   ├── __init__.py
│   ├── distributions.py
│   └── random_variables.py
├── inferential/
│   ├── __init__.py
│   ├── hypothesis_tests.py
│   └── confidence_intervals.py
├── regression/
│   ├── __init__.py
│   ├── linear_regression.py
│   └── multiple_regression.py
├── visualization/
│   ├── __init__.py
│   ├── plots.py
│   └── interactive.py
└── big_data/
    ├── __init__.py
    ├── spark_stats.py
    └── dask_stats.py
```

## 2. Implementation Approach

### 2.1 Pure Python (Educational)
```python
def mean_pure_python(data):
    """Calculate mean using pure Python."""
    return sum(data) / len(data)
```

### 2.2 NumPy (Production)
```python
import numpy as np

def mean_numpy(data):
    """Calculate mean using NumPy."""
    return np.mean(data)
```

### 2.3 Numerically Stable Algorithms
```python
def welford_variance(data):
    """Compute variance using Welford's online algorithm."""
    n = 0
    mean = 0.0
    M2 = 0.0
    
    for x in data:
        n += 1
        delta = x - mean
        mean += delta / n
        delta2 = x - mean
        M2 += delta * delta2
    
    if n < 2:
        return 0.0
    return M2 / (n - 1)
```

## 3. Core Modules

### 3.1 Descriptive Statistics

**central_tendency.py**:
```python
import numpy as np
from typing import List, Union
from collections import Counter

class CentralTendency:
    """Calculate measures of central tendency."""
    
    @staticmethod
    def mean(data: Union[List, np.ndarray]) -> float:
        """Calculate arithmetic mean."""
        return np.mean(data)
    
    @staticmethod
    def median(data: Union[List, np.ndarray]) -> float:
        """Calculate median."""
        return np.median(data)
    
    @staticmethod
    def mode(data: Union[List, np.ndarray]) -> Union[float, List[float]]:
        """Calculate mode(s)."""
        counts = Counter(data)
        max_count = max(counts.values())
        modes = [k for k, v in counts.items() if v == max_count]
        return modes[0] if len(modes) == 1 else modes
    
    @staticmethod
    def geometric_mean(data: Union[List, np.ndarray]) -> float:
        """Calculate geometric mean."""
        data_array = np.array(data)
        return np.exp(np.mean(np.log(data_array)))
    
    @staticmethod
    def harmonic_mean(data: Union[List, np.ndarray]) -> float:
        """Calculate harmonic mean."""
        data_array = np.array(data)
        return len(data_array) / np.sum(1 / data_array)
```

**dispersion.py**:
```python
import numpy as np
from typing import Union, List

class Dispersion:
    """Calculate measures of dispersion."""
    
    @staticmethod
    def range(data: Union[List, np.ndarray]) -> float:
        """Calculate range."""
        return np.max(data) - np.min(data)
    
    @staticmethod
    def variance(data: Union[List, np.ndarray], ddof: int = 1) -> float:
        """Calculate variance.
        
        Args:
            data: Input data
            ddof: Delta degrees of freedom (0 for population, 1 for sample)
        """
        return np.var(data, ddof=ddof)
    
    @staticmethod
    def std_dev(data: Union[List, np.ndarray], ddof: int = 1) -> float:
        """Calculate standard deviation."""
        return np.std(data, ddof=ddof)
    
    @staticmethod
    def mad(data: Union[List, np.ndarray]) -> float:
        """Calculate mean absolute deviation."""
        data_array = np.array(data)
        return np.mean(np.abs(data_array - np.mean(data_array)))
    
    @staticmethod
    def iqr(data: Union[List, np.ndarray]) -> float:
        """Calculate interquartile range."""
        q75, q25 = np.percentile(data, [75, 25])
        return q75 - q25
    
    @staticmethod
    def coefficient_of_variation(data: Union[List, np.ndarray]) -> float:
        """Calculate coefficient of variation (CV)."""
        mean = np.mean(data)
        if mean == 0:
            raise ValueError("Mean is zero, CV is undefined")
        return np.std(data, ddof=1) / mean * 100
```

**shape.py**:
```python
import numpy as np
from scipy import stats
from typing import Union, List

class Shape:
    """Calculate measures of distribution shape."""
    
    @staticmethod
    def skewness(data: Union[List, np.ndarray], bias: bool = True) -> float:
        """Calculate skewness.
        
        Args:
            data: Input data
            bias: If False, calculations are corrected for statistical bias
        """
        return stats.skew(data, bias=bias)
    
    @staticmethod
    def kurtosis(data: Union[List, np.ndarray], fisher: bool = True) -> float:
        """Calculate kurtosis.
        
        Args:
            data: Input data
            fisher: If True, return excess kurtosis (subtract 3)
        """
        return stats.kurtosis(data, fisher=fisher)
    
    @staticmethod
    def percentile(data: Union[List, np.ndarray], p: float) -> float:
        """Calculate percentile.
        
        Args:
            data: Input data
            p: Percentile (0-100)
        """
        return np.percentile(data, p)
    
    @staticmethod
    def quantile(data: Union[List, np.ndarray], q: float) -> float:
        """Calculate quantile.
        
        Args:
            data: Input data
            q: Quantile (0-1)
        """
        return np.quantile(data, q)
```

## 4. Probability Distributions

**distributions.py**:
```python
import numpy as np
from scipy import stats
from typing import Union

class Distributions:
    """Common probability distributions."""
    
    class Normal:
        """Normal (Gaussian) distribution."""
        
        @staticmethod
        def pdf(x: Union[float, np.ndarray], mu: float = 0, sigma: float = 1) -> Union[float, np.ndarray]:
            """Probability density function."""
            return stats.norm.pdf(x, loc=mu, scale=sigma)
        
        @staticmethod
        def cdf(x: Union[float, np.ndarray], mu: float = 0, sigma: float = 1) -> Union[float, np.ndarray]:
            """Cumulative distribution function."""
            return stats.norm.cdf(x, loc=mu, scale=sigma)
        
        @staticmethod
        def rvs(mu: float = 0, sigma: float = 1, size: int = 1) -> Union[float, np.ndarray]:
            """Generate random variables."""
            return stats.norm.rvs(loc=mu, scale=sigma, size=size)
        
        @staticmethod
        def ppf(q: Union[float, np.ndarray], mu: float = 0, sigma: float = 1) -> Union[float, np.ndarray]:
            """Percent point function (inverse CDF)."""
            return stats.norm.ppf(q, loc=mu, scale=sigma)
    
    class Binomial:
        """Binomial distribution."""
        
        @staticmethod
        def pmf(k: int, n: int, p: float) -> float:
            """Probability mass function."""
            return stats.binom.pmf(k, n, p)
        
        @staticmethod
        def cdf(k: int, n: int, p: float) -> float:
            """Cumulative distribution function."""
            return stats.binom.cdf(k, n, p)
        
        @staticmethod
        def rvs(n: int, p: float, size: int = 1) -> Union[int, np.ndarray]:
            """Generate random variables."""
            return stats.binom.rvs(n, p, size=size)
    
    class Poisson:
        """Poisson distribution."""
        
        @staticmethod
        def pmf(k: int, lambda_: float) -> float:
            """Probability mass function."""
            return stats.poisson.pmf(k, lambda_)
        
        @staticmethod
        def cdf(k: int, lambda_: float) -> float:
            """Cumulative distribution function."""
            return stats.poisson.cdf(k, lambda_)
        
        @staticmethod
        def rvs(lambda_: float, size: int = 1) -> Union[int, np.ndarray]:
            """Generate random variables."""
            return stats.poisson.rvs(lambda_, size=size)
```

## 5. Best Practices

### 5.1 Type Hints
```python
from typing import Union, List, Tuple
import numpy as np

def calculate_stats(data: Union[List[float], np.ndarray]) -> Tuple[float, float]:
    """Calculate mean and std dev with type hints."""
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return mean, std
```

### 5.2 Error Handling
```python
def safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide, handling edge cases."""
    if denominator == 0:
        raise ValueError("Division by zero")
    if not isinstance(numerator, (int, float)):
        raise TypeError(f"Expected number, got {type(numerator)}")
    return numerator / denominator
```

### 5.3 Documentation
```python
def correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Calculate Pearson correlation coefficient.
    
    Args:
        x: First variable
        y: Second variable
    
    Returns:
        Correlation coefficient between -1 and 1
    
    Raises:
        ValueError: If arrays have different lengths
    
    Examples:
        >>> x = np.array([1, 2, 3, 4, 5])
        >>> y = np.array([2, 4, 6, 8, 10])
        >>> correlation(x, y)
        1.0
    """
    if len(x) != len(y):
        raise ValueError("Arrays must have same length")
    return np.corrcoef(x, y)[0, 1]
```

## 6. Testing

### 6.1 Unit Tests
```python
import unittest
import numpy as np
from src.python.descriptive import CentralTendency

class TestCentralTendency(unittest.TestCase):
    
    def setUp(self):
        self.data = [1, 2, 3, 4, 5]
        self.ct = CentralTendency()
    
    def test_mean(self):
        result = self.ct.mean(self.data)
        self.assertAlmostEqual(result, 3.0)
    
    def test_median(self):
        result = self.ct.median(self.data)
        self.assertEqual(result, 3.0)
    
    def test_empty_data(self):
        with self.assertRaises(ValueError):
            self.ct.mean([])
```

### 6.2 Property-Based Testing
```python
from hypothesis import given
from hypothesis import strategies as st
import numpy as np

@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1))
def test_variance_non_negative(data):
    """Variance should always be non-negative."""
    variance = np.var(data)
    assert variance >= 0
```

## 7. Performance Optimization

### 7.1 Vectorization
```python
# Slow (loop)
def slow_sum_of_squares(data):
    result = 0
    for x in data:
        result += x ** 2
    return result

# Fast (vectorized)
def fast_sum_of_squares(data):
    return np.sum(np.array(data) ** 2)
```

### 7.2 Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> float:
    """Cache results for expensive calculations."""
    # Expensive computation here
    return result
```

## Next Steps

- See [Fortran Implementation Guide](fortran-guide.md) for high-performance implementations
- See [Integration Guide](integration-guide.md) for Python-Fortran integration
