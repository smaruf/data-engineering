"""
Probability Distributions

Implements common probability distributions with PDF, CDF, and random sampling.
"""

import numpy as np
from scipy import stats
from typing import Union


class Distributions:
    """Common probability distributions."""
    
    class Normal:
        """Normal (Gaussian) distribution N(μ, σ²)."""
        
        @staticmethod
        def pdf(x: Union[float, np.ndarray], mu: float = 0, sigma: float = 1) -> Union[float, np.ndarray]:
            """
            Probability density function.
            
            Args:
                x: Value or array of values
                mu: Mean (default 0)
                sigma: Standard deviation (default 1)
                
            Returns:
                PDF value(s)
                
            Example:
                >>> Distributions.Normal.pdf(0, mu=0, sigma=1)
                0.3989422804014327
            """
            return stats.norm.pdf(x, loc=mu, scale=sigma)
        
        @staticmethod
        def cdf(x: Union[float, np.ndarray], mu: float = 0, sigma: float = 1) -> Union[float, np.ndarray]:
            """
            Cumulative distribution function.
            
            Args:
                x: Value or array of values
                mu: Mean (default 0)
                sigma: Standard deviation (default 1)
                
            Returns:
                CDF value(s)
                
            Example:
                >>> Distributions.Normal.cdf(0, mu=0, sigma=1)
                0.5
            """
            return stats.norm.cdf(x, loc=mu, scale=sigma)
        
        @staticmethod
        def rvs(mu: float = 0, sigma: float = 1, size: int = 1) -> Union[float, np.ndarray]:
            """
            Generate random variables.
            
            Args:
                mu: Mean (default 0)
                sigma: Standard deviation (default 1)
                size: Number of samples
                
            Returns:
                Random sample(s)
                
            Example:
                >>> np.random.seed(42)
                >>> Distributions.Normal.rvs(mu=0, sigma=1, size=3)
                array([ 0.49671415, -0.1382643 ,  0.64768854])
            """
            return stats.norm.rvs(loc=mu, scale=sigma, size=size)
        
        @staticmethod
        def ppf(q: Union[float, np.ndarray], mu: float = 0, sigma: float = 1) -> Union[float, np.ndarray]:
            """
            Percent point function (inverse CDF).
            
            Args:
                q: Quantile value(s) between 0 and 1
                mu: Mean (default 0)
                sigma: Standard deviation (default 1)
                
            Returns:
                Value(s) at quantile(s)
                
            Example:
                >>> Distributions.Normal.ppf(0.975, mu=0, sigma=1)
                1.959963984540054
            """
            return stats.norm.ppf(q, loc=mu, scale=sigma)
    
    class Binomial:
        """Binomial distribution B(n, p)."""
        
        @staticmethod
        def pmf(k: int, n: int, p: float) -> float:
            """
            Probability mass function.
            
            Args:
                k: Number of successes
                n: Number of trials
                p: Probability of success
                
            Returns:
                PMF value
                
            Example:
                >>> Distributions.Binomial.pmf(5, 10, 0.5)
                0.24609375
            """
            return float(stats.binom.pmf(k, n, p))
        
        @staticmethod
        def cdf(k: int, n: int, p: float) -> float:
            """
            Cumulative distribution function.
            
            Args:
                k: Number of successes
                n: Number of trials
                p: Probability of success
                
            Returns:
                CDF value
            """
            return float(stats.binom.cdf(k, n, p))
        
        @staticmethod
        def rvs(n: int, p: float, size: int = 1) -> Union[int, np.ndarray]:
            """
            Generate random variables.
            
            Args:
                n: Number of trials
                p: Probability of success
                size: Number of samples
                
            Returns:
                Random sample(s)
            """
            return stats.binom.rvs(n, p, size=size)
        
        @staticmethod
        def mean(n: int, p: float) -> float:
            """Calculate mean of binomial distribution."""
            return float(n * p)
        
        @staticmethod
        def variance(n: int, p: float) -> float:
            """Calculate variance of binomial distribution."""
            return float(n * p * (1 - p))
    
    class Poisson:
        """Poisson distribution P(λ)."""
        
        @staticmethod
        def pmf(k: int, lambda_: float) -> float:
            """
            Probability mass function.
            
            Args:
                k: Number of events
                lambda_: Rate parameter (mean)
                
            Returns:
                PMF value
                
            Example:
                >>> Distributions.Poisson.pmf(3, 2.5)
                0.21376326978625733
            """
            return float(stats.poisson.pmf(k, lambda_))
        
        @staticmethod
        def cdf(k: int, lambda_: float) -> float:
            """
            Cumulative distribution function.
            
            Args:
                k: Number of events
                lambda_: Rate parameter
                
            Returns:
                CDF value
            """
            return float(stats.poisson.cdf(k, lambda_))
        
        @staticmethod
        def rvs(lambda_: float, size: int = 1) -> Union[int, np.ndarray]:
            """
            Generate random variables.
            
            Args:
                lambda_: Rate parameter
                size: Number of samples
                
            Returns:
                Random sample(s)
            """
            return stats.poisson.rvs(lambda_, size=size)
        
        @staticmethod
        def mean(lambda_: float) -> float:
            """Calculate mean of Poisson distribution."""
            return float(lambda_)
        
        @staticmethod
        def variance(lambda_: float) -> float:
            """Calculate variance of Poisson distribution."""
            return float(lambda_)
    
    class Exponential:
        """Exponential distribution Exp(λ)."""
        
        @staticmethod
        def pdf(x: Union[float, np.ndarray], lambda_: float = 1.0) -> Union[float, np.ndarray]:
            """
            Probability density function.
            
            Args:
                x: Value or array of values
                lambda_: Rate parameter
                
            Returns:
                PDF value(s)
            """
            scale = 1.0 / lambda_
            return stats.expon.pdf(x, scale=scale)
        
        @staticmethod
        def cdf(x: Union[float, np.ndarray], lambda_: float = 1.0) -> Union[float, np.ndarray]:
            """
            Cumulative distribution function.
            
            Args:
                x: Value or array of values
                lambda_: Rate parameter
                
            Returns:
                CDF value(s)
            """
            scale = 1.0 / lambda_
            return stats.expon.cdf(x, scale=scale)
        
        @staticmethod
        def rvs(lambda_: float = 1.0, size: int = 1) -> Union[float, np.ndarray]:
            """
            Generate random variables.
            
            Args:
                lambda_: Rate parameter
                size: Number of samples
                
            Returns:
                Random sample(s)
            """
            scale = 1.0 / lambda_
            return stats.expon.rvs(scale=scale, size=size)
    
    class TDistribution:
        """Student's t-distribution."""
        
        @staticmethod
        def pdf(x: Union[float, np.ndarray], df: int) -> Union[float, np.ndarray]:
            """
            Probability density function.
            
            Args:
                x: Value or array of values
                df: Degrees of freedom
                
            Returns:
                PDF value(s)
            """
            return stats.t.pdf(x, df)
        
        @staticmethod
        def cdf(x: Union[float, np.ndarray], df: int) -> Union[float, np.ndarray]:
            """
            Cumulative distribution function.
            
            Args:
                x: Value or array of values
                df: Degrees of freedom
                
            Returns:
                CDF value(s)
            """
            return stats.t.cdf(x, df)
        
        @staticmethod
        def ppf(q: Union[float, np.ndarray], df: int) -> Union[float, np.ndarray]:
            """
            Percent point function (inverse CDF).
            
            Args:
                q: Quantile value(s)
                df: Degrees of freedom
                
            Returns:
                Value(s) at quantile(s)
                
            Example:
                >>> Distributions.TDistribution.ppf(0.975, df=9)
                2.2621571627409915
            """
            return stats.t.ppf(q, df)
    
    class ChiSquare:
        """Chi-square distribution."""
        
        @staticmethod
        def pdf(x: Union[float, np.ndarray], df: int) -> Union[float, np.ndarray]:
            """Probability density function."""
            return stats.chi2.pdf(x, df)
        
        @staticmethod
        def cdf(x: Union[float, np.ndarray], df: int) -> Union[float, np.ndarray]:
            """Cumulative distribution function."""
            return stats.chi2.cdf(x, df)
        
        @staticmethod
        def ppf(q: Union[float, np.ndarray], df: int) -> Union[float, np.ndarray]:
            """Percent point function (inverse CDF)."""
            return stats.chi2.ppf(q, df)
