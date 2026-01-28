"""
Example: Probability Distributions
===================================

This example demonstrates various probability distributions
and their properties.
"""

import sys
sys.path.append('../..')

import numpy as np
import matplotlib.pyplot as plt
from src.python.probability import Distributions

def main():
    print("=" * 70)
    print("  Probability Distributions Example")
    print("=" * 70)
    print()
    
    # Normal Distribution
    demonstrate_normal()
    
    # Binomial Distribution
    demonstrate_binomial()
    
    # Poisson Distribution
    demonstrate_poisson()
    
    # Create visualizations
    create_distribution_plots()
    
    print("=" * 70)
    print("  Example Complete!")
    print("=" * 70)


def demonstrate_normal():
    """Demonstrate Normal distribution."""
    print("Normal Distribution N(μ=100, σ=15)")
    print("-" * 50)
    
    mu, sigma = 100, 15
    
    # PDF at specific points
    print(f"PDF at x=100: {Distributions.Normal.pdf(100, mu, sigma):.6f}")
    print(f"PDF at x=115: {Distributions.Normal.pdf(115, mu, sigma):.6f}")
    print()
    
    # CDF (probabilities)
    print(f"P(X ≤ 100): {Distributions.Normal.cdf(100, mu, sigma):.4f}")
    print(f"P(X ≤ 115): {Distributions.Normal.cdf(115, mu, sigma):.4f}")
    print(f"P(85 ≤ X ≤ 115): {Distributions.Normal.cdf(115, mu, sigma) - Distributions.Normal.cdf(85, mu, sigma):.4f}")
    print()
    
    # Critical values
    print(f"95th percentile: {Distributions.Normal.ppf(0.95, mu, sigma):.2f}")
    print(f"99th percentile: {Distributions.Normal.ppf(0.99, mu, sigma):.2f}")
    print()
    
    # Generate random samples
    np.random.seed(42)
    samples = Distributions.Normal.rvs(mu, sigma, size=1000)
    print(f"Generated 1000 samples:")
    print(f"  Sample mean: {np.mean(samples):.2f} (expected {mu})")
    print(f"  Sample std: {np.std(samples, ddof=1):.2f} (expected {sigma})")
    print()


def demonstrate_binomial():
    """Demonstrate Binomial distribution."""
    print("Binomial Distribution B(n=10, p=0.3)")
    print("-" * 50)
    
    n, p = 10, 0.3
    
    print(f"P(X = 3): {Distributions.Binomial.pmf(3, n, p):.4f}")
    print(f"P(X ≤ 3): {Distributions.Binomial.cdf(3, n, p):.4f}")
    print()
    
    print(f"Mean: {Distributions.Binomial.mean(n, p):.2f}")
    print(f"Variance: {Distributions.Binomial.variance(n, p):.2f}")
    print()


def demonstrate_poisson():
    """Demonstrate Poisson distribution."""
    print("Poisson Distribution P(λ=5)")
    print("-" * 50)
    
    lambda_ = 5
    
    print(f"P(X = 5): {Distributions.Poisson.pmf(5, lambda_):.4f}")
    print(f"P(X ≤ 5): {Distributions.Poisson.cdf(5, lambda_):.4f}")
    print()
    
    print(f"Mean: {Distributions.Poisson.mean(lambda_):.2f}")
    print(f"Variance: {Distributions.Poisson.variance(lambda_):.2f}")
    print()


def create_distribution_plots():
    """Create visualizations of distributions."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Normal Distribution
    x = np.linspace(-4, 4, 1000)
    y_normal = Distributions.Normal.pdf(x, mu=0, sigma=1)
    axes[0, 0].plot(x, y_normal, 'b-', linewidth=2)
    axes[0, 0].fill_between(x, y_normal, alpha=0.3)
    axes[0, 0].set_title('Normal Distribution N(0, 1)', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('x')
    axes[0, 0].set_ylabel('PDF')
    axes[0, 0].grid(alpha=0.3)
    
    # Normal CDF
    y_normal_cdf = Distributions.Normal.cdf(x, mu=0, sigma=1)
    axes[0, 1].plot(x, y_normal_cdf, 'b-', linewidth=2)
    axes[0, 1].set_title('Normal CDF N(0, 1)', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('x')
    axes[0, 1].set_ylabel('CDF')
    axes[0, 1].grid(alpha=0.3)
    
    # Binomial Distribution
    k = np.arange(0, 21)
    n, p = 20, 0.3
    pmf_binomial = [Distributions.Binomial.pmf(i, n, p) for i in k]
    axes[1, 0].bar(k, pmf_binomial, alpha=0.7, edgecolor='black')
    axes[1, 0].set_title(f'Binomial Distribution B(n={n}, p={p})', 
                         fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('k (number of successes)')
    axes[1, 0].set_ylabel('PMF')
    axes[1, 0].grid(alpha=0.3)
    
    # Poisson Distribution
    k_poisson = np.arange(0, 20)
    lambda_ = 5
    pmf_poisson = [Distributions.Poisson.pmf(i, lambda_) for i in k_poisson]
    axes[1, 1].bar(k_poisson, pmf_poisson, alpha=0.7, color='green', edgecolor='black')
    axes[1, 1].set_title(f'Poisson Distribution P(λ={lambda_})', 
                         fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('k (number of events)')
    axes[1, 1].set_ylabel('PMF')
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('distributions_example.png', dpi=150)
    print("Visualization saved as 'distributions_example.png'")


if __name__ == "__main__":
    main()
