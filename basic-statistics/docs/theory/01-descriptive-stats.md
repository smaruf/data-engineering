# Descriptive Statistics: Theory and Theorems

## Overview

Descriptive statistics summarize and describe the main features of a dataset. They provide simple summaries about the sample and measures that help us understand the data distribution.

## 1. Measures of Central Tendency

### 1.1 Mean (Arithmetic Mean)

**Definition**: The average of all values in a dataset.

**Formula**:
```
μ = (Σ xᵢ) / n
```
where:
- μ (mu) = population mean
- x̄ (x-bar) = sample mean
- xᵢ = individual values
- n = number of observations

**Properties**:
- Sensitive to outliers
- Minimizes sum of squared deviations
- Used in many statistical tests

**Theorem 1.1 (Linearity of Mean)**:
```
E[aX + b] = aE[X] + b
```
For any constants a and b.

**Example**:
```
Data: [2, 4, 6, 8, 10]
Mean = (2+4+6+8+10)/5 = 30/5 = 6
```

### 1.2 Median

**Definition**: The middle value when data is ordered.

**Formula**:
- If n is odd: Median = x₍ₙ₊₁₎/₂
- If n is even: Median = (xₙ/₂ + x₍ₙ/₂₎₊₁) / 2

**Properties**:
- Robust to outliers
- 50th percentile
- Better for skewed distributions

**Example**:
```
Data (odd): [1, 3, 5, 7, 9] → Median = 5
Data (even): [1, 3, 5, 7, 9, 11] → Median = (5+7)/2 = 6
```

### 1.3 Mode

**Definition**: The most frequently occurring value.

**Properties**:
- Can have multiple modes (bimodal, multimodal)
- Useful for categorical data
- May not exist for continuous data

**Example**:
```
Data: [1, 2, 2, 3, 4, 4, 4, 5]
Mode = 4 (appears 3 times)
```

## 2. Measures of Dispersion

### 2.1 Range

**Definition**: Difference between maximum and minimum values.

**Formula**:
```
Range = max(X) - min(X)
```

**Properties**:
- Simple but sensitive to outliers
- Limited statistical utility

### 2.2 Variance

**Definition**: Average of squared deviations from the mean.

**Population Variance**:
```
σ² = Σ(xᵢ - μ)² / N
```

**Sample Variance** (Bessel's correction):
```
s² = Σ(xᵢ - x̄)² / (n-1)
```

**Theorem 2.1 (Computational Formula)**:
```
σ² = E[X²] - (E[X])²
    = (Σxᵢ²)/n - μ²
```

**Proof**:
```
Var(X) = E[(X - μ)²]
       = E[X² - 2μX + μ²]
       = E[X²] - 2μE[X] + μ²
       = E[X²] - 2μ² + μ²
       = E[X²] - μ²
```

**Properties**:
- Always non-negative
- Units are squared
- Sensitive to outliers

### 2.3 Standard Deviation

**Definition**: Square root of variance.

**Formula**:
```
σ = √(σ²)
s = √(s²)
```

**Properties**:
- Same units as original data
- Easier to interpret than variance
- Used in many statistical tests

**Theorem 2.2 (Properties of Standard Deviation)**:
```
1. SD(aX + b) = |a| × SD(X)
2. SD(X + Y) = √(Var(X) + Var(Y) + 2Cov(X,Y))
3. If X and Y are independent: SD(X + Y) = √(Var(X) + Var(Y))
```

### 2.4 Coefficient of Variation (CV)

**Definition**: Ratio of standard deviation to mean.

**Formula**:
```
CV = (σ/μ) × 100%
```

**Properties**:
- Dimensionless measure
- Useful for comparing variability across different scales
- Invalid when mean is zero or negative

## 3. Measures of Shape

### 3.1 Skewness

**Definition**: Measure of asymmetry in the distribution.

**Formula** (Pearson's moment coefficient):
```
Skewness = E[(X - μ)³] / σ³
         = (Σ(xᵢ - x̄)³/n) / s³
```

**Interpretation**:
- Skewness = 0: Symmetric distribution
- Skewness > 0: Right-skewed (positive skew)
- Skewness < 0: Left-skewed (negative skew)

**Alternative Formula** (Pearson's mode skewness):
```
Sk = (Mean - Mode) / SD
```

**Properties**:
- Dimensionless
- Values typically between -3 and +3
- Normal distribution has skewness = 0

### 3.2 Kurtosis

**Definition**: Measure of "tailedness" of the distribution.

**Formula**:
```
Kurtosis = E[(X - μ)⁴] / σ⁴
```

**Excess Kurtosis**:
```
Excess Kurtosis = Kurtosis - 3
```

**Interpretation**:
- Excess Kurtosis = 0: Mesokurtic (normal distribution)
- Excess Kurtosis > 0: Leptokurtic (heavy tails, peaked)
- Excess Kurtosis < 0: Platykurtic (light tails, flat)

**Properties**:
- Always ≥ 1
- Normal distribution has kurtosis = 3

## 4. Percentiles and Quantiles

### 4.1 Percentiles

**Definition**: Value below which a percentage of data falls.

**Formula** (linear interpolation):
```
Pₖ = x₍ₙ₊₁₎ₖ/₁₀₀
```

**Common Percentiles**:
- P₂₅: First quartile (Q₁)
- P₅₀: Median (Q₂)
- P₇₅: Third quartile (Q₃)

### 4.2 Interquartile Range (IQR)

**Definition**: Range of middle 50% of data.

**Formula**:
```
IQR = Q₃ - Q₁
```

**Properties**:
- Robust to outliers
- Used in box plots
- Identifies outliers: x < Q₁ - 1.5×IQR or x > Q₃ + 1.5×IQR

## 5. Key Theorems

### Theorem 5.1: Chebyshev's Inequality

For any dataset and any k > 1:
```
P(|X - μ| ≥ kσ) ≤ 1/k²
```

**Interpretation**: At least (1 - 1/k²) of values lie within k standard deviations of the mean.

**Examples**:
- k=2: At least 75% of data within 2σ
- k=3: At least 89% of data within 3σ

**Proof Sketch**:
```
Var(X) = E[(X-μ)²]
       ≥ ∫|x-μ|≥kσ (x-μ)² f(x)dx
       ≥ k²σ² × P(|X-μ| ≥ kσ)

Therefore: P(|X-μ| ≥ kσ) ≤ Var(X)/(k²σ²) = 1/k²
```

### Theorem 5.2: Empirical Rule (68-95-99.7 Rule)

For normal distributions:
```
P(μ - σ ≤ X ≤ μ + σ) ≈ 0.68 (68%)
P(μ - 2σ ≤ X ≤ μ + 2σ) ≈ 0.95 (95%)
P(μ - 3σ ≤ X ≤ μ + 3σ) ≈ 0.997 (99.7%)
```

### Theorem 5.3: Parallel Axis Theorem

For grouped data:
```
σ²ₜₒₜₐₗ = σ²ᵦₑₜwₑₑₙ + σ²wᵢₜₕᵢₙ
```

Total variance equals between-group variance plus within-group variance.

## 6. Practical Applications

### 6.1 Data Quality Assessment
- Check for outliers using IQR
- Assess distribution shape (skewness, kurtosis)
- Identify data entry errors

### 6.2 Reporting and Communication
- Mean and SD for symmetric data
- Median and IQR for skewed data
- Mode for categorical data

### 6.3 Statistical Inference
- Sample statistics estimate population parameters
- Foundation for hypothesis testing
- Input to regression models

## 7. Computational Considerations

### 7.1 Numerical Stability

**Naive variance calculation** (unstable):
```
s² = (Σxᵢ² - (Σxᵢ)²/n) / (n-1)
```

**Welford's algorithm** (stable):
```
M₂,ₙ = M₂,ₙ₋₁ + (xₙ - x̄ₙ₋₁)(xₙ - x̄ₙ)
s² = M₂,ₙ / (n-1)
```

### 7.2 Big Data Considerations
- Use parallel/distributed algorithms
- Compute statistics in chunks
- Welford's algorithm for streaming data

## 8. Summary Table

| Measure | Formula | Properties | When to Use |
|---------|---------|-----------|-------------|
| Mean | Σxᵢ/n | Sensitive to outliers | Symmetric data |
| Median | Middle value | Robust | Skewed data |
| Mode | Most frequent | Simple | Categorical data |
| Variance | Σ(xᵢ-μ)²/N | Squared units | Internal calculations |
| Std Dev | √variance | Original units | Reporting |
| IQR | Q₃ - Q₁ | Robust | Outlier detection |

## Next Steps

Continue to [Probability Theory](02-probability-theory.md) to build on these foundations and understand random variables and distributions.
