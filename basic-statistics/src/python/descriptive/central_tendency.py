"""
Central Tendency Measures

Implements mean, median, mode, and other measures of central tendency.
"""

import numpy as np
from typing import List, Union
from collections import Counter


class CentralTendency:
    """Calculate measures of central tendency."""
    
    @staticmethod
    def mean(data: Union[List, np.ndarray]) -> float:
        """
        Calculate arithmetic mean.
        
        Args:
            data: Input data array or list
            
        Returns:
            Arithmetic mean of the data
            
        Example:
            >>> CentralTendency.mean([1, 2, 3, 4, 5])
            3.0
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate mean of empty data")
        return float(np.mean(data))
    
    @staticmethod
    def median(data: Union[List, np.ndarray]) -> float:
        """
        Calculate median (50th percentile).
        
        Args:
            data: Input data array or list
            
        Returns:
            Median value
            
        Example:
            >>> CentralTendency.median([1, 2, 3, 4, 5])
            3.0
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate median of empty data")
        return float(np.median(data))
    
    @staticmethod
    def mode(data: Union[List, np.ndarray]) -> Union[float, List[float]]:
        """
        Calculate mode(s) - most frequent value(s).
        
        Args:
            data: Input data array or list
            
        Returns:
            Mode value or list of modes if multimodal
            
        Example:
            >>> CentralTendency.mode([1, 2, 2, 3, 3, 3])
            3
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate mode of empty data")
        
        counts = Counter(data)
        max_count = max(counts.values())
        modes = [k for k, v in counts.items() if v == max_count]
        
        return modes[0] if len(modes) == 1 else modes
    
    @staticmethod
    def geometric_mean(data: Union[List, np.ndarray]) -> float:
        """
        Calculate geometric mean.
        
        Useful for rates of change, ratios, and multiplicative processes.
        
        Args:
            data: Input data array or list (must be positive)
            
        Returns:
            Geometric mean
            
        Raises:
            ValueError: If any value is non-positive
            
        Example:
            >>> CentralTendency.geometric_mean([1, 2, 4, 8])
            2.8284271247461903
        """
        data_array = np.array(data)
        
        if len(data_array) == 0:
            raise ValueError("Cannot calculate geometric mean of empty data")
        if np.any(data_array <= 0):
            raise ValueError("All values must be positive for geometric mean")
            
        return float(np.exp(np.mean(np.log(data_array))))
    
    @staticmethod
    def harmonic_mean(data: Union[List, np.ndarray]) -> float:
        """
        Calculate harmonic mean.
        
        Useful for rates and ratios (e.g., average speed).
        
        Args:
            data: Input data array or list (must be non-zero)
            
        Returns:
            Harmonic mean
            
        Raises:
            ValueError: If any value is zero
            
        Example:
            >>> CentralTendency.harmonic_mean([1, 2, 4])
            1.7142857142857142
        """
        data_array = np.array(data)
        
        if len(data_array) == 0:
            raise ValueError("Cannot calculate harmonic mean of empty data")
        if np.any(data_array == 0):
            raise ValueError("Cannot have zero values for harmonic mean")
            
        return float(len(data_array) / np.sum(1.0 / data_array))
    
    @staticmethod
    def trimmed_mean(data: Union[List, np.ndarray], proportion: float = 0.1) -> float:
        """
        Calculate trimmed mean (excluding extreme values).
        
        Args:
            data: Input data array or list
            proportion: Proportion to trim from each end (0 to 0.5)
            
        Returns:
            Trimmed mean
            
        Raises:
            ValueError: If proportion is not between 0 and 0.5
            
        Example:
            >>> CentralTendency.trimmed_mean([1, 2, 3, 4, 100], proportion=0.2)
            3.0
        """
        if not 0 <= proportion < 0.5:
            raise ValueError("Proportion must be between 0 and 0.5")
        
        if len(data) == 0:
            raise ValueError("Cannot calculate trimmed mean of empty data")
        
        from scipy import stats
        return float(stats.trim_mean(data, proportion))
