"""
Dispersion Measures

Implements variance, standard deviation, range, and other measures of spread.
"""

import numpy as np
from typing import Union, List


class Dispersion:
    """Calculate measures of dispersion (spread)."""
    
    @staticmethod
    def range(data: Union[List, np.ndarray]) -> float:
        """
        Calculate range (max - min).
        
        Args:
            data: Input data array or list
            
        Returns:
            Range of the data
            
        Example:
            >>> Dispersion.range([1, 2, 3, 4, 5])
            4.0
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate range of empty data")
        return float(np.max(data) - np.min(data))
    
    @staticmethod
    def variance(data: Union[List, np.ndarray], ddof: int = 1) -> float:
        """
        Calculate variance.
        
        Args:
            data: Input data array or list
            ddof: Delta degrees of freedom (0 for population, 1 for sample)
            
        Returns:
            Variance
            
        Example:
            >>> Dispersion.variance([1, 2, 3, 4, 5])
            2.5
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate variance of empty data")
        return float(np.var(data, ddof=ddof))
    
    @staticmethod
    def std_dev(data: Union[List, np.ndarray], ddof: int = 1) -> float:
        """
        Calculate standard deviation.
        
        Args:
            data: Input data array or list
            ddof: Delta degrees of freedom (0 for population, 1 for sample)
            
        Returns:
            Standard deviation
            
        Example:
            >>> Dispersion.std_dev([1, 2, 3, 4, 5])
            1.5811388300841898
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate standard deviation of empty data")
        return float(np.std(data, ddof=ddof))
    
    @staticmethod
    def mad(data: Union[List, np.ndarray]) -> float:
        """
        Calculate Mean Absolute Deviation (MAD).
        
        More robust to outliers than standard deviation.
        
        Args:
            data: Input data array or list
            
        Returns:
            Mean absolute deviation
            
        Example:
            >>> Dispersion.mad([1, 2, 3, 4, 5])
            1.2
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate MAD of empty data")
        
        data_array = np.array(data)
        return float(np.mean(np.abs(data_array - np.mean(data_array))))
    
    @staticmethod
    def median_absolute_deviation(data: Union[List, np.ndarray]) -> float:
        """
        Calculate Median Absolute Deviation.
        
        Very robust measure of dispersion.
        
        Args:
            data: Input data array or list
            
        Returns:
            Median absolute deviation
            
        Example:
            >>> Dispersion.median_absolute_deviation([1, 2, 3, 4, 5])
            1.0
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate median absolute deviation of empty data")
        
        data_array = np.array(data)
        median = np.median(data_array)
        return float(np.median(np.abs(data_array - median)))
    
    @staticmethod
    def iqr(data: Union[List, np.ndarray]) -> float:
        """
        Calculate Interquartile Range (IQR).
        
        IQR = Q3 - Q1, represents the middle 50% of data.
        
        Args:
            data: Input data array or list
            
        Returns:
            Interquartile range
            
        Example:
            >>> Dispersion.iqr([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            4.5
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate IQR of empty data")
        
        q75, q25 = np.percentile(data, [75, 25])
        return float(q75 - q25)
    
    @staticmethod
    def coefficient_of_variation(data: Union[List, np.ndarray]) -> float:
        """
        Calculate Coefficient of Variation (CV).
        
        CV = (std_dev / mean) * 100%
        Dimensionless measure of relative variability.
        
        Args:
            data: Input data array or list
            
        Returns:
            Coefficient of variation as percentage
            
        Raises:
            ValueError: If mean is zero
            
        Example:
            >>> Dispersion.coefficient_of_variation([10, 12, 14, 16, 18])
            20.0
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate CV of empty data")
        
        mean = np.mean(data)
        if abs(mean) < 1e-10:
            raise ValueError("Mean is zero, CV is undefined")
        
        std = np.std(data, ddof=1)
        return float((std / mean) * 100)
    
    @staticmethod
    def welford_variance(data: Union[List, np.ndarray]) -> float:
        """
        Calculate variance using Welford's online algorithm.
        
        Numerically stable method for computing variance.
        
        Args:
            data: Input data array or list
            
        Returns:
            Variance (sample)
            
        Example:
            >>> Dispersion.welford_variance([1, 2, 3, 4, 5])
            2.5
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate variance of empty data")
        
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
        
        return float(M2 / (n - 1))
