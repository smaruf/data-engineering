"""
Unit tests for probability distributions.
"""

import pytest
import numpy as np
from scipy import stats
from src.python.probability import Distributions


class TestNormalDistribution:
    """Test Normal distribution."""
    
    def test_pdf_standard_normal(self):
        """Test PDF of standard normal at x=0."""
        result = Distributions.Normal.pdf(0, mu=0, sigma=1)
        expected = 1 / np.sqrt(2 * np.pi)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_cdf_standard_normal(self):
        """Test CDF of standard normal at x=0."""
        result = Distributions.Normal.cdf(0, mu=0, sigma=1)
        assert pytest.approx(result, rel=1e-6) == 0.5
    
    def test_ppf_standard_normal(self):
        """Test inverse CDF (ppf) for standard normal."""
        result = Distributions.Normal.ppf(0.975, mu=0, sigma=1)
        expected = stats.norm.ppf(0.975)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_rvs_shape(self):
        """Test random variates generation shape."""
        np.random.seed(42)
        result = Distributions.Normal.rvs(mu=0, sigma=1, size=100)
        assert len(result) == 100
    
    def test_rvs_mean_std(self):
        """Test random variates have approximately correct mean and std."""
        np.random.seed(42)
        mu, sigma = 5, 2
        result = Distributions.Normal.rvs(mu=mu, sigma=sigma, size=10000)
        assert pytest.approx(np.mean(result), abs=0.1) == mu
        assert pytest.approx(np.std(result), abs=0.1) == sigma


class TestBinomialDistribution:
    """Test Binomial distribution."""
    
    def test_pmf(self):
        """Test PMF of binomial distribution."""
        result = Distributions.Binomial.pmf(5, 10, 0.5)
        expected = stats.binom.pmf(5, 10, 0.5)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_cdf(self):
        """Test CDF of binomial distribution."""
        result = Distributions.Binomial.cdf(5, 10, 0.5)
        expected = stats.binom.cdf(5, 10, 0.5)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_mean(self):
        """Test mean of binomial distribution."""
        result = Distributions.Binomial.mean(10, 0.3)
        expected = 10 * 0.3
        assert result == expected
    
    def test_variance(self):
        """Test variance of binomial distribution."""
        result = Distributions.Binomial.variance(10, 0.3)
        expected = 10 * 0.3 * 0.7
        assert result == expected


class TestPoissonDistribution:
    """Test Poisson distribution."""
    
    def test_pmf(self):
        """Test PMF of Poisson distribution."""
        result = Distributions.Poisson.pmf(3, 2.5)
        expected = stats.poisson.pmf(3, 2.5)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_cdf(self):
        """Test CDF of Poisson distribution."""
        result = Distributions.Poisson.cdf(3, 2.5)
        expected = stats.poisson.cdf(3, 2.5)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_mean(self):
        """Test mean of Poisson distribution."""
        lambda_ = 4.5
        result = Distributions.Poisson.mean(lambda_)
        assert result == lambda_
    
    def test_variance(self):
        """Test variance of Poisson distribution."""
        lambda_ = 4.5
        result = Distributions.Poisson.variance(lambda_)
        assert result == lambda_


class TestExponentialDistribution:
    """Test Exponential distribution."""
    
    def test_pdf(self):
        """Test PDF of exponential distribution."""
        result = Distributions.Exponential.pdf(1.0, lambda_=2.0)
        expected = stats.expon.pdf(1.0, scale=0.5)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_cdf(self):
        """Test CDF of exponential distribution."""
        result = Distributions.Exponential.cdf(1.0, lambda_=2.0)
        expected = stats.expon.cdf(1.0, scale=0.5)
        assert pytest.approx(result, rel=1e-6) == expected


class TestTDistribution:
    """Test Student's t-distribution."""
    
    def test_pdf(self):
        """Test PDF of t-distribution."""
        result = Distributions.TDistribution.pdf(0, df=10)
        expected = stats.t.pdf(0, 10)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_ppf(self):
        """Test inverse CDF of t-distribution."""
        result = Distributions.TDistribution.ppf(0.975, df=9)
        expected = stats.t.ppf(0.975, 9)
        assert pytest.approx(result, rel=1e-6) == expected


class TestChiSquareDistribution:
    """Test Chi-square distribution."""
    
    def test_pdf(self):
        """Test PDF of chi-square distribution."""
        result = Distributions.ChiSquare.pdf(5, df=3)
        expected = stats.chi2.pdf(5, 3)
        assert pytest.approx(result, rel=1e-6) == expected
    
    def test_cdf(self):
        """Test CDF of chi-square distribution."""
        result = Distributions.ChiSquare.cdf(5, df=3)
        expected = stats.chi2.cdf(5, 3)
        assert pytest.approx(result, rel=1e-6) == expected
