"""
Example: Descriptive Statistics with Python
============================================

This example demonstrates how to use the basic statistics library
for descriptive analysis.
"""

import sys
sys.path.append('../..')

import numpy as np
import matplotlib.pyplot as plt
from src.python.descriptive import CentralTendency, Dispersion, Shape

def main():
    print("=" * 70)
    print("  Descriptive Statistics Example")
    print("=" * 70)
    print()
    
    # Sample dataset: Test scores
    test_scores = [85, 92, 78, 90, 88, 76, 95, 89, 84, 91, 
                   87, 83, 79, 94, 86, 88, 92, 81, 90, 85]
    
    print("Dataset: Test Scores")
    print(f"Data: {test_scores}")
    print()
    
    # Central Tendency
    print("Measures of Central Tendency:")
    print("-" * 50)
    print(f"Mean:            {CentralTendency.mean(test_scores):.2f}")
    print(f"Median:          {CentralTendency.median(test_scores):.2f}")
    print(f"Mode:            {CentralTendency.mode(test_scores)}")
    print()
    
    # Dispersion
    print("Measures of Dispersion:")
    print("-" * 50)
    print(f"Range:           {Dispersion.range(test_scores):.2f}")
    print(f"Variance:        {Dispersion.variance(test_scores):.2f}")
    print(f"Std Deviation:   {Dispersion.std_dev(test_scores):.2f}")
    print(f"MAD:             {Dispersion.mad(test_scores):.2f}")
    print(f"IQR:             {Dispersion.iqr(test_scores):.2f}")
    print(f"CV:              {Dispersion.coefficient_of_variation(test_scores):.2f}%")
    print()
    
    # Shape
    print("Measures of Shape:")
    print("-" * 50)
    print(f"Skewness:        {Shape.skewness(test_scores):.4f}")
    print(f"Kurtosis:        {Shape.kurtosis(test_scores):.4f}")
    print()
    
    # Five Number Summary
    print("Five Number Summary:")
    print("-" * 50)
    min_val, q1, median, q3, max_val = Shape.five_number_summary(test_scores)
    print(f"Minimum:         {min_val:.2f}")
    print(f"Q1 (25th):       {q1:.2f}")
    print(f"Median (50th):   {median:.2f}")
    print(f"Q3 (75th):       {q3:.2f}")
    print(f"Maximum:         {max_val:.2f}")
    print()
    
    # Outlier Detection
    print("Outlier Detection (IQR Method):")
    print("-" * 50)
    indices, values = Shape.detect_outliers_iqr(test_scores)
    if len(values) > 0:
        print(f"Outliers found: {values}")
        print(f"At indices: {indices}")
    else:
        print("No outliers detected")
    print()
    
    # Visualization
    create_visualizations(test_scores)
    
    print("=" * 70)
    print("  Analysis Complete!")
    print("=" * 70)


def create_visualizations(data):
    """Create visualizations of the data."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Histogram
    axes[0, 0].hist(data, bins=10, edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(CentralTendency.mean(data), color='red', 
                       linestyle='--', label='Mean')
    axes[0, 0].axvline(CentralTendency.median(data), color='green', 
                       linestyle='--', label='Median')
    axes[0, 0].set_title('Histogram with Mean and Median')
    axes[0, 0].set_xlabel('Test Scores')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # Box Plot
    axes[0, 1].boxplot(data, vert=True)
    axes[0, 1].set_title('Box Plot')
    axes[0, 1].set_ylabel('Test Scores')
    axes[0, 1].grid(alpha=0.3)
    
    # Q-Q Plot (approximate)
    sorted_data = np.sort(data)
    theoretical_quantiles = np.linspace(0, 1, len(data))
    axes[1, 0].scatter(theoretical_quantiles, sorted_data)
    axes[1, 0].set_title('Empirical Quantile Plot')
    axes[1, 0].set_xlabel('Theoretical Quantiles')
    axes[1, 0].set_ylabel('Sample Quantiles')
    axes[1, 0].grid(alpha=0.3)
    
    # Distribution summary text
    summary_text = f"""
    Statistics Summary:
    
    Mean: {CentralTendency.mean(data):.2f}
    Median: {CentralTendency.median(data):.2f}
    Std Dev: {Dispersion.std_dev(data):.2f}
    Skewness: {Shape.skewness(data):.4f}
    Kurtosis: {Shape.kurtosis(data):.4f}
    """
    axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, 
                    verticalalignment='center', family='monospace')
    axes[1, 1].axis('off')
    axes[1, 1].set_title('Summary Statistics')
    
    plt.tight_layout()
    plt.savefig('descriptive_stats_example.png', dpi=150)
    print("Visualization saved as 'descriptive_stats_example.png'")


if __name__ == "__main__":
    main()
