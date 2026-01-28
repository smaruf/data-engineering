"""
A/B Testing Use Case
====================

Real-world example: Testing two website designs to determine
which one performs better.

Scenario:
- Design A (Control): Current website design
- Design B (Treatment): New website design
- Metric: Conversion rate (% of visitors who make a purchase)
- Question: Is Design B significantly better than Design A?
"""

import sys
sys.path.append('../..')

import numpy as np
from scipy import stats
from src.python.descriptive import CentralTendency, Dispersion
from src.python.probability import Distributions

def main():
    print("=" * 70)
    print("  A/B Testing: Website Design Comparison")
    print("=" * 70)
    print()
    
    # Simulate data for two designs
    np.random.seed(42)
    
    # Design A: 5% conversion rate, 1000 visitors
    n_a = 1000
    conversions_a = np.random.binomial(1, 0.05, n_a)
    conversion_rate_a = np.mean(conversions_a)
    
    # Design B: 6.5% conversion rate, 1000 visitors
    n_b = 1000
    conversions_b = np.random.binomial(1, 0.065, n_b)
    conversion_rate_b = np.mean(conversions_b)
    
    print("Data Summary:")
    print("-" * 50)
    print(f"Design A:")
    print(f"  Visitors:     {n_a}")
    print(f"  Conversions:  {np.sum(conversions_a)}")
    print(f"  Conv. Rate:   {conversion_rate_a:.2%}")
    print()
    print(f"Design B:")
    print(f"  Visitors:     {n_b}")
    print(f"  Conversions:  {np.sum(conversions_b)}")
    print(f"  Conv. Rate:   {conversion_rate_b:.2%}")
    print()
    
    # Statistical Test: Two-proportion z-test
    print("Hypothesis Test:")
    print("-" * 50)
    print("H₀: p_A = p_B (no difference in conversion rates)")
    print("H₁: p_A ≠ p_B (there is a difference)")
    print()
    
    # Calculate test statistic
    p_pooled = (np.sum(conversions_a) + np.sum(conversions_b)) / (n_a + n_b)
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b))
    z_stat = (conversion_rate_b - conversion_rate_a) / se
    
    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - Distributions.Normal.cdf(abs(z_stat), 0, 1))
    
    print(f"Pooled proportion: {p_pooled:.4f}")
    print(f"Standard error:    {se:.4f}")
    print(f"Z-statistic:       {z_stat:.4f}")
    print(f"P-value:           {p_value:.4f}")
    print()
    
    # Decision
    alpha = 0.05
    print(f"Significance level (α): {alpha}")
    if p_value < alpha:
        print(f"✓ REJECT H₀: Design B is significantly different from Design A")
        print(f"  The new design has a statistically significant impact.")
    else:
        print(f"✗ FAIL TO REJECT H₀: No significant difference detected")
        print(f"  The new design does not show a significant improvement.")
    print()
    
    # Confidence Interval for difference
    diff = conversion_rate_b - conversion_rate_a
    se_diff = np.sqrt(conversion_rate_a*(1-conversion_rate_a)/n_a + 
                      conversion_rate_b*(1-conversion_rate_b)/n_b)
    ci_lower = diff - 1.96 * se_diff
    ci_upper = diff + 1.96 * se_diff
    
    print("95% Confidence Interval for Difference:")
    print("-" * 50)
    print(f"Difference: {diff:.2%}")
    print(f"95% CI: [{ci_lower:.2%}, {ci_upper:.2%}]")
    print()
    
    # Effect Size (Relative Improvement)
    relative_improvement = (conversion_rate_b - conversion_rate_a) / conversion_rate_a
    print(f"Relative Improvement: {relative_improvement:.1%}")
    print()
    
    # Business Impact
    print("Business Impact Analysis:")
    print("-" * 50)
    avg_order_value = 50  # dollars
    annual_visitors = 100000
    
    additional_conversions = annual_visitors * diff
    additional_revenue = additional_conversions * avg_order_value
    
    print(f"If applied to {annual_visitors:,} annual visitors:")
    print(f"  Additional conversions: {additional_conversions:,.0f}")
    print(f"  Additional revenue (at ${avg_order_value}/order): ${additional_revenue:,.0f}")
    print()
    
    print("=" * 70)
    print("  Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
