"""
Shape Measures

Implements skewness, kurtosis, and percentiles.
"""

import numpy as np
from scipy import stats
from typing import Union, List, Tuple


class Shape:
    """Calculate measures of distribution shape."""
    
    @staticmethod
    def skewness(data: Union[List, np.ndarray], bias: bool = True) -> float:
        """
        Calculate skewness (asymmetry measure).
        
        Skewness measures the asymmetry of the distribution:
        - 0: Symmetric
        - > 0: Right-skewed (tail on right)
        - < 0: Left-skewed (tail on left)
        
        Args:
            data: Input data array or list
            bias: If False, calculations are corrected for statistical bias
            
        Returns:
            Skewness coefficient
            
        Example:
            >>> Shape.skewness([1, 2, 3, 4, 5])
            0.0
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate skewness of empty data")
        
        return float(stats.skew(data, bias=bias))
    
    @staticmethod
    def kurtosis(data: Union[List, np.ndarray], fisher: bool = True) -> float:
        """
        Calculate kurtosis (tailedness measure).
        
        Kurtosis measures the "tailedness" of the distribution:
        - Excess Kurtosis = 0: Normal distribution (mesokurtic)
        - > 0: Heavy tails, peaked (leptokurtic)
        - < 0: Light tails, flat (platykurtic)
        
        Args:
            data: Input data array or list
            fisher: If True, return excess kurtosis (subtract 3)
            
        Returns:
            Kurtosis coefficient
            
        Example:
            >>> Shape.kurtosis([1, 2, 3, 4, 5])
            -1.3
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate kurtosis of empty data")
        
        return float(stats.kurtosis(data, fisher=fisher))
    
    @staticmethod
    def percentile(data: Union[List, np.ndarray], p: float) -> float:
        """
        Calculate percentile.
        
        Args:
            data: Input data array or list
            p: Percentile value (0-100)
            
        Returns:
            Value at the given percentile
            
        Raises:
            ValueError: If p is not between 0 and 100
            
        Example:
            >>> Shape.percentile([1, 2, 3, 4, 5], 50)
            3.0
        """
        if not 0 <= p <= 100:
            raise ValueError("Percentile must be between 0 and 100")
        
        if len(data) == 0:
            raise ValueError("Cannot calculate percentile of empty data")
        
        return float(np.percentile(data, p))
    
    @staticmethod
    def quantile(data: Union[List, np.ndarray], q: float) -> float:
        """
        Calculate quantile.
        
        Args:
            data: Input data array or list
            q: Quantile value (0-1)
            
        Returns:
            Value at the given quantile
            
        Raises:
            ValueError: If q is not between 0 and 1
            
        Example:
            >>> Shape.quantile([1, 2, 3, 4, 5], 0.5)
            3.0
        """
        if not 0 <= q <= 1:
            raise ValueError("Quantile must be between 0 and 1")
        
        if len(data) == 0:
            raise ValueError("Cannot calculate quantile of empty data")
        
        return float(np.quantile(data, q))
    
    @staticmethod
    def quartiles(data: Union[List, np.ndarray]) -> Tuple[float, float, float]:
        """
        Calculate quartiles (Q1, Q2/median, Q3).
        
        Args:
            data: Input data array or list
            
        Returns:
            Tuple of (Q1, Q2, Q3)
            
        Example:
            >>> Shape.quartiles([1, 2, 3, 4, 5, 6, 7, 8, 9])
            (2.5, 5.0, 7.5)
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate quartiles of empty data")
        
        q1, q2, q3 = np.percentile(data, [25, 50, 75])
        return (float(q1), float(q2), float(q3))
    
    @staticmethod
    def five_number_summary(data: Union[List, np.ndarray]) -> Tuple[float, float, float, float, float]:
        """
        Calculate five-number summary (min, Q1, median, Q3, max).
        
        Used for box plots and understanding data distribution.
        
        Args:
            data: Input data array or list
            
        Returns:
            Tuple of (min, Q1, median, Q3, max)
            
        Example:
            >>> Shape.five_number_summary([1, 2, 3, 4, 5, 6, 7, 8, 9])
            (1.0, 2.5, 5.0, 7.5, 9.0)
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate five-number summary of empty data")
        
        minimum = float(np.min(data))
        q1, median, q3 = Shape.quartiles(data)
        maximum = float(np.max(data))
        
        return (minimum, q1, median, q3, maximum)
    
    @staticmethod
    def detect_outliers_iqr(data: Union[List, np.ndarray], factor: float = 1.5) -> Tuple[List[int], List[float]]:
        """
        Detect outliers using IQR method.
        
        Outliers are values outside [Q1 - factor*IQR, Q3 + factor*IQR].
        Common factor is 1.5 for outliers, 3.0 for extreme outliers.
        
        Args:
            data: Input data array or list
            factor: IQR multiplier (default 1.5)
            
        Returns:
            Tuple of (outlier_indices, outlier_values)
            
        Example:
            >>> Shape.detect_outliers_iqr([1, 2, 3, 4, 5, 100])
            ([5], [100])
        """
        if len(data) == 0:
            raise ValueError("Cannot detect outliers in empty data")
        
        data_array = np.array(data)
        q1, q3 = np.percentile(data_array, [25, 75])
        iqr = q3 - q1
        
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        
        outlier_mask = (data_array < lower_bound) | (data_array > upper_bound)
        outlier_indices = np.where(outlier_mask)[0].tolist()
        outlier_values = data_array[outlier_mask].tolist()
        
        return (outlier_indices, outlier_values)
    
    @staticmethod
    def z_scores(data: Union[List, np.ndarray]) -> np.ndarray:
        """
        Calculate z-scores (standard scores).
        
        Z-score = (x - mean) / std_dev
        
        Args:
            data: Input data array or list
            
        Returns:
            Array of z-scores
            
        Example:
            >>> Shape.z_scores([1, 2, 3, 4, 5])
            array([-1.41421356, -0.70710678,  0.        ,  0.70710678,  1.41421356])
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate z-scores of empty data")
        
        data_array = np.array(data)
        mean = np.mean(data_array)
        std = np.std(data_array, ddof=1)
        
        if std == 0:
            raise ValueError("Standard deviation is zero, cannot calculate z-scores")
        
        return (data_array - mean) / std
