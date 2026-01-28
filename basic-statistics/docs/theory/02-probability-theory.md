# Probability Theory: Foundations for Statistics

## Overview

Probability theory provides the mathematical foundation for statistical inference. This chapter covers fundamental probability concepts, theorems, and their applications.

## 1. Basic Probability Concepts

### 1.1 Sample Space and Events

**Definitions**:
- **Sample Space (Ω)**: Set of all possible outcomes
- **Event (A)**: Subset of sample space
- **Probability P(A)**: Measure of likelihood, 0 ≤ P(A) ≤ 1

**Example**:
```
Experiment: Rolling a die
Sample Space: Ω = {1, 2, 3, 4, 5, 6}
Event A (even number): A = {2, 4, 6}
P(A) = 3/6 = 0.5
```

### 1.2 Axioms of Probability (Kolmogorov Axioms)

**Axiom 1**: For any event A, P(A) ≥ 0

**Axiom 2**: P(Ω) = 1 (certainty)

**Axiom 3** (Countable Additivity):
```
For mutually exclusive events A₁, A₂, ...:
P(A₁ ∪ A₂ ∪ ...) = P(A₁) + P(A₂) + ...
```

## 2. Probability Rules and Theorems

### 2.1 Addition Rule

**For any two events**:
```
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
```

**For mutually exclusive events**:
```
If A ∩ B = ∅, then:
P(A ∪ B) = P(A) + P(B)
```

**Proof**:
```
A ∪ B = A ∪ (B - A)
where A and (B - A) are disjoint

P(A ∪ B) = P(A) + P(B - A)
         = P(A) + P(B) - P(A ∩ B)
```

### 2.2 Multiplication Rule

**For independent events**:
```
P(A ∩ B) = P(A) × P(B)
```

**For dependent events**:
```
P(A ∩ B) = P(A) × P(B|A)
         = P(B) × P(A|B)
```

### 2.3 Complement Rule

**Formula**:
```
P(Aᶜ) = 1 - P(A)
```

where Aᶜ is the complement of A.

## 3. Conditional Probability

### 3.1 Definition

**Formula**:
```
P(A|B) = P(A ∩ B) / P(B), if P(B) > 0
```

**Interpretation**: Probability of A given that B has occurred.

### 3.2 Bayes' Theorem

**Theorem 3.1 (Bayes' Theorem)**:
```
P(A|B) = [P(B|A) × P(A)] / P(B)
```

**Extended Form** (with law of total probability):
```
P(A|B) = [P(B|A) × P(A)] / [P(B|A)×P(A) + P(B|Aᶜ)×P(Aᶜ)]
```

**Proof**:
```
From definition: P(A|B) = P(A ∩ B) / P(B)
Also: P(B|A) = P(A ∩ B) / P(A)

Therefore: P(A ∩ B) = P(B|A) × P(A)

Substituting:
P(A|B) = [P(B|A) × P(A)] / P(B)
```

**Applications**:
- Medical diagnosis
- Spam filtering
- Machine learning classification
- Bayesian inference

**Example** (Medical Test):
```
Disease prevalence: P(D) = 0.01
Test sensitivity: P(+|D) = 0.95
Test specificity: P(-|¬D) = 0.90

P(D|+) = [P(+|D) × P(D)] / [P(+|D)×P(D) + P(+|¬D)×P(¬D)]
       = [0.95 × 0.01] / [0.95×0.01 + 0.10×0.99]
       = 0.0095 / 0.1085
       ≈ 0.0876 or 8.76%
```

### 3.3 Law of Total Probability

**Theorem 3.2**:
If {B₁, B₂, ..., Bₙ} is a partition of Ω, then:
```
P(A) = Σ P(A|Bᵢ) × P(Bᵢ)
```

## 4. Independence

### 4.1 Independent Events

**Definition**:
Events A and B are independent if:
```
P(A ∩ B) = P(A) × P(B)
```

**Equivalent conditions**:
```
1. P(A|B) = P(A)
2. P(B|A) = P(B)
3. P(A ∩ B) = P(A) × P(B)
```

### 4.2 Mutually Independent Events

Events A₁, A₂, ..., Aₙ are mutually independent if:
```
For any subset {Aᵢ₁, Aᵢ₂, ..., Aᵢₖ}:
P(Aᵢ₁ ∩ Aᵢ₂ ∩ ... ∩ Aᵢₖ) = P(Aᵢ₁) × P(Aᵢ₂) × ... × P(Aᵢₖ)
```

## 5. Random Variables

### 5.1 Definition

**Random Variable**: Function X: Ω → ℝ that assigns a number to each outcome.

**Types**:
- **Discrete**: Takes countable values
- **Continuous**: Takes values in an interval

### 5.2 Probability Mass Function (PMF) - Discrete

**Definition**:
```
pₓ(x) = P(X = x)
```

**Properties**:
```
1. pₓ(x) ≥ 0 for all x
2. Σ pₓ(x) = 1
```

### 5.3 Probability Density Function (PDF) - Continuous

**Definition**:
```
f(x) such that P(a ≤ X ≤ b) = ∫ₐᵇ f(x)dx
```

**Properties**:
```
1. f(x) ≥ 0 for all x
2. ∫₋∞^∞ f(x)dx = 1
3. P(X = x) = 0 for any specific x
```

### 5.4 Cumulative Distribution Function (CDF)

**Definition**:
```
F(x) = P(X ≤ x)
```

**Properties**:
```
1. 0 ≤ F(x) ≤ 1
2. F is non-decreasing
3. lim(x→-∞) F(x) = 0
4. lim(x→∞) F(x) = 1
5. F is right-continuous
```

**Relationship with PDF**:
```
f(x) = dF(x)/dx
F(x) = ∫₋∞ˣ f(t)dt
```

## 6. Expected Value and Moments

### 6.1 Expected Value (Mean)

**Discrete**:
```
E[X] = μ = Σ x × pₓ(x)
```

**Continuous**:
```
E[X] = μ = ∫₋∞^∞ x × f(x)dx
```

**Properties**:
```
1. E[aX + b] = a×E[X] + b
2. E[X + Y] = E[X] + E[Y]
3. E[XY] = E[X]×E[Y] if X and Y are independent
```

### 6.2 Variance

**Definition**:
```
Var(X) = E[(X - μ)²]
       = E[X²] - (E[X])²
```

**Properties**:
```
1. Var(aX + b) = a²×Var(X)
2. Var(X + Y) = Var(X) + Var(Y) + 2Cov(X,Y)
3. If independent: Var(X + Y) = Var(X) + Var(Y)
```

### 6.3 Higher Moments

**k-th moment**:
```
E[Xᵏ]
```

**k-th central moment**:
```
E[(X - μ)ᵏ]
```

**Moment Generating Function (MGF)**:
```
Mₓ(t) = E[e^(tX)]
```

**Properties of MGF**:
```
1. E[Xᵏ] = M⁽ᵏ⁾(0) (k-th derivative at 0)
2. MGF uniquely determines distribution
3. Sum of independent variables: Mₓ₊ᵧ(t) = Mₓ(t) × Mᵧ(t)
```

## 7. Key Probability Theorems

### Theorem 7.1: Law of Large Numbers (LLN)

**Weak Law**:
For i.i.d. random variables X₁, X₂, ..., Xₙ with mean μ:
```
X̄ₙ = (X₁ + X₂ + ... + Xₙ)/n

P(|X̄ₙ - μ| > ε) → 0 as n → ∞ for any ε > 0
```

**Strong Law**:
```
P(lim(n→∞) X̄ₙ = μ) = 1
```

**Implications**:
- Sample mean converges to population mean
- Foundation for statistical inference
- Justifies using samples to estimate parameters

### Theorem 7.2: Central Limit Theorem (CLT)

For i.i.d. random variables X₁, X₂, ..., Xₙ with mean μ and variance σ²:
```
Z = (X̄ₙ - μ) / (σ/√n) → N(0,1) as n → ∞

Or equivalently:
X̄ₙ ~ N(μ, σ²/n) for large n
```

**Implications**:
- Sampling distributions are approximately normal
- Enables hypothesis testing
- Justifies confidence intervals
- Generally holds for n ≥ 30

**Example**:
```
Rolling a die 100 times:
μ = 3.5, σ² = 35/12

Distribution of sample mean X̄:
X̄ ~ N(3.5, 35/(12×100)) ≈ N(3.5, 0.029)
```

### Theorem 7.3: Chebyshev's Inequality

For any random variable X with mean μ and variance σ²:
```
P(|X - μ| ≥ k×σ) ≤ 1/k²
```

**Applications**:
- Bounds on tail probabilities
- Works for any distribution
- Conservative estimate

## 8. Covariance and Correlation

### 8.1 Covariance

**Definition**:
```
Cov(X, Y) = E[(X - μₓ)(Y - μᵧ)]
          = E[XY] - E[X]×E[Y]
```

**Properties**:
```
1. Cov(X, X) = Var(X)
2. Cov(X, Y) = Cov(Y, X)
3. Cov(aX + b, cY + d) = ac×Cov(X, Y)
4. If independent: Cov(X, Y) = 0
```

### 8.2 Correlation Coefficient

**Pearson's correlation**:
```
ρ = Cov(X, Y) / (σₓ × σᵧ)
```

**Properties**:
```
1. -1 ≤ ρ ≤ 1
2. ρ = ±1 implies perfect linear relationship
3. ρ = 0 implies no linear relationship
4. Dimensionless
```

## 9. Conditional Expectation

**Definition**:
```
E[X|Y] = ∫ x × f(x|y)dx
```

**Law of Iterated Expectations**:
```
E[E[X|Y]] = E[X]
```

**Conditional Variance**:
```
Var(X) = E[Var(X|Y)] + Var(E[X|Y])
```

## 10. Applications

### 10.1 Statistical Inference
- Estimate population parameters
- Test hypotheses
- Build confidence intervals

### 10.2 Machine Learning
- Probabilistic models
- Bayesian learning
- Classification and regression

### 10.3 Risk Analysis
- Financial modeling
- Insurance calculations
- Quality control

## Summary

Key concepts covered:
- Probability axioms and rules
- Conditional probability and Bayes' theorem
- Random variables and distributions
- Expected value and variance
- Fundamental limit theorems (LLN, CLT)
- Covariance and correlation

Next: [Probability Distributions](03-distributions.md)
