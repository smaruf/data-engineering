# Linear Algebra Foundations for AI

Linear algebra is the mathematical foundation of machine learning and AI. This guide covers essential concepts.

## Table of Contents
- [Why Linear Algebra for AI?](#why-linear-algebra-for-ai)
- [Vectors](#vectors)
- [Matrices](#matrices)
- [Matrix Operations](#matrix-operations)
- [Implementation in Fortran](#implementation-in-fortran)
- [Applications in AI](#applications-in-ai)

## Why Linear Algebra for AI?

Machine learning represents data and transformations using linear algebra:
- **Data**: Stored as vectors and matrices
- **Parameters**: Weights and biases in matrices
- **Operations**: Matrix multiplications and transformations
- **Optimization**: Gradient vectors and Hessian matrices

## Vectors

### Definition
A vector is an ordered list of numbers.

```
v = [v₁, v₂, v₃, ..., vₙ]
```

### Vector Operations

#### Addition
```
a + b = [a₁ + b₁, a₂ + b₂, ..., aₙ + bₙ]
```

#### Scalar Multiplication
```
c · v = [c·v₁, c·v₂, ..., c·vₙ]
```

#### Dot Product
```
a · b = a₁b₁ + a₂b₂ + ... + aₙbₙ
```

#### Magnitude (L2 Norm)
```
||v|| = √(v₁² + v₂² + ... + vₙ²)
```

### Fortran Implementation

```fortran
module vector_ops
    implicit none
contains
    
    ! Vector addition
    function vec_add(a, b) result(c)
        real, dimension(:), intent(in) :: a, b
        real, dimension(size(a)) :: c
        c = a + b  ! Element-wise addition
    end function vec_add
    
    ! Dot product
    real function vec_dot(a, b)
        real, dimension(:), intent(in) :: a, b
        vec_dot = dot_product(a, b)
    end function vec_dot
    
    ! Vector magnitude
    real function vec_magnitude(v)
        real, dimension(:), intent(in) :: v
        vec_magnitude = sqrt(sum(v**2))
    end function vec_magnitude
    
    ! Normalize vector
    function vec_normalize(v) result(v_norm)
        real, dimension(:), intent(in) :: v
        real, dimension(size(v)) :: v_norm
        real :: mag
        mag = vec_magnitude(v)
        if (mag > 0.0) then
            v_norm = v / mag
        else
            v_norm = 0.0
        end if
    end function vec_normalize
    
end module vector_ops
```

## Matrices

### Definition
A matrix is a 2D array of numbers arranged in rows and columns.

```
     ⎡ a₁₁  a₁₂  a₁₃ ⎤
A =  ⎢ a₂₁  a₂₂  a₂₃ ⎥
     ⎣ a₃₁  a₃₂  a₃₃ ⎦
```

### Matrix Dimensions
An m×n matrix has m rows and n columns.

### Special Matrices

#### Identity Matrix
```
     ⎡ 1  0  0 ⎤
I =  ⎢ 0  1  0 ⎥
     ⎣ 0  0  1 ⎦
```

#### Zero Matrix
```
     ⎡ 0  0  0 ⎤
0 =  ⎢ 0  0  0 ⎥
     ⎣ 0  0  0 ⎦
```

## Matrix Operations

### Transpose
Swap rows and columns: A^T

```fortran
function matrix_transpose(A) result(AT)
    real, dimension(:,:), intent(in) :: A
    real, dimension(size(A,2), size(A,1)) :: AT
    integer :: i, j
    
    do i = 1, size(A, 1)
        do j = 1, size(A, 2)
            AT(j, i) = A(i, j)
        end do
    end do
    ! Or simply: AT = transpose(A)
end function matrix_transpose
```

### Matrix Addition
Element-wise addition (matrices must have same dimensions).

```fortran
function matrix_add(A, B) result(C)
    real, dimension(:,:), intent(in) :: A, B
    real, dimension(size(A,1), size(A,2)) :: C
    C = A + B
end function matrix_add
```

### Matrix Multiplication
The fundamental operation in neural networks.

**Rule**: (m×n) × (n×p) = (m×p)

```
C(i,j) = Σ A(i,k) × B(k,j)
         k
```

```fortran
function matrix_multiply(A, B) result(C)
    real, dimension(:,:), intent(in) :: A, B
    real, dimension(size(A,1), size(B,2)) :: C
    integer :: i, j, k
    
    C = 0.0
    do i = 1, size(A, 1)
        do j = 1, size(B, 2)
            do k = 1, size(A, 2)
                C(i,j) = C(i,j) + A(i,k) * B(k,j)
            end do
        end do
    end do
end function matrix_multiply
```

### Optimized Matrix Multiplication

```fortran
! Using built-in matmul (faster, optimized)
function matrix_multiply_fast(A, B) result(C)
    real, dimension(:,:), intent(in) :: A, B
    real, dimension(size(A,1), size(B,2)) :: C
    C = matmul(A, B)
end function matrix_multiply_fast
```

### Element-wise Multiplication (Hadamard Product)
```fortran
function matrix_hadamard(A, B) result(C)
    real, dimension(:,:), intent(in) :: A, B
    real, dimension(size(A,1), size(A,2)) :: C
    C = A * B  ! Element-wise
end function matrix_hadamard
```

## Implementation in Fortran

### Complete Linear Algebra Module

```fortran
module linalg
    implicit none
    private
    public :: dot, matmul_custom, transpose_matrix, identity, &
              element_wise_multiply, outer_product
    
contains
    
    ! Dot product of two vectors
    real function dot(a, b)
        real, dimension(:), intent(in) :: a, b
        dot = sum(a * b)
    end function dot
    
    ! Custom matrix multiplication
    function matmul_custom(A, B) result(C)
        real, dimension(:,:), intent(in) :: A, B
        real, dimension(size(A,1), size(B,2)) :: C
        integer :: i, j, k
        
        do concurrent (i = 1:size(A,1), j = 1:size(B,2))
            C(i,j) = sum(A(i,:) * B(:,j))
        end do
    end function matmul_custom
    
    ! Matrix transpose
    function transpose_matrix(A) result(AT)
        real, dimension(:,:), intent(in) :: A
        real, dimension(size(A,2), size(A,1)) :: AT
        AT = transpose(A)
    end function transpose_matrix
    
    ! Create identity matrix
    function identity(n) result(I)
        integer, intent(in) :: n
        real, dimension(n, n) :: I
        integer :: i
        
        I = 0.0
        do i = 1, n
            I(i, i) = 1.0
        end do
    end function identity
    
    ! Element-wise multiplication
    function element_wise_multiply(A, B) result(C)
        real, dimension(:,:), intent(in) :: A, B
        real, dimension(size(A,1), size(A,2)) :: C
        C = A * B
    end function element_wise_multiply
    
    ! Outer product of two vectors
    function outer_product(a, b) result(C)
        real, dimension(:), intent(in) :: a, b
        real, dimension(size(a), size(b)) :: C
        integer :: i, j
        
        do i = 1, size(a)
            do j = 1, size(b)
                C(i,j) = a(i) * b(j)
            end do
        end do
    end function outer_product
    
end module linalg
```

## Applications in AI

### 1. Linear Regression

**Model**: y = Xw + b

- X: Input features (matrix)
- w: Weights (vector)
- b: Bias (scalar)
- y: Predictions (vector)

```fortran
function linear_regression_predict(X, weights, bias) result(y)
    real, dimension(:,:), intent(in) :: X
    real, dimension(:), intent(in) :: weights
    real, intent(in) :: bias
    real, dimension(size(X,1)) :: y
    
    ! y = X·w + b
    y = matmul(X, weights) + bias
end function linear_regression_predict
```

### 2. Neural Network Forward Pass

**Hidden Layer**: h = σ(Xw₁ + b₁)  
**Output Layer**: y = σ(hw₂ + b₂)

```fortran
function neural_forward(X, w1, b1, w2, b2) result(output)
    real, dimension(:,:), intent(in) :: X
    real, dimension(:,:), intent(in) :: w1, w2
    real, dimension(:), intent(in) :: b1, b2
    real, dimension(size(X,1), size(w2,2)) :: output
    real, dimension(size(X,1), size(w1,2)) :: hidden
    integer :: i, j
    
    ! Forward pass through first layer
    hidden = matmul(X, w1)
    do i = 1, size(hidden, 1)
        hidden(i,:) = hidden(i,:) + b1
        ! Apply activation function (sigmoid)
        do j = 1, size(hidden, 2)
            hidden(i,j) = 1.0 / (1.0 + exp(-hidden(i,j)))
        end do
    end do
    
    ! Forward pass through second layer
    output = matmul(hidden, w2)
    do i = 1, size(output, 1)
        output(i,:) = output(i,:) + b2
        do j = 1, size(output, 2)
            output(i,j) = 1.0 / (1.0 + exp(-output(i,j)))
        end do
    end do
end function neural_forward
```

### 3. Gradient Computation

**Gradient**: ∇w = (1/m) X^T (ŷ - y)

```fortran
function compute_gradient(X, y_true, y_pred) result(gradient)
    real, dimension(:,:), intent(in) :: X
    real, dimension(:), intent(in) :: y_true, y_pred
    real, dimension(size(X,2)) :: gradient
    real, dimension(size(y_true)) :: error
    integer :: m
    
    m = size(y_true)
    error = y_pred - y_true
    gradient = matmul(transpose(X), error) / real(m)
end function compute_gradient
```

## Performance Tips

### 1. Use Built-in Functions
```fortran
! Slow - manual loop
do i = 1, n
    do j = 1, m
        C(i,j) = sum(A(i,:) * B(:,j))
    end do
end do

! Fast - built-in matmul
C = matmul(A, B)
```

### 2. Use DO CONCURRENT for Parallelization
```fortran
! Parallelizable loop
do concurrent (i = 1:n)
    result(i) = expensive_calculation(data(i))
end do
```

### 3. Consider BLAS/LAPACK
For production code, link to optimized libraries:
```bash
gfortran -o program program.f90 -lopenblas
```

## Common Patterns in AI

### Broadcasting
Extending operations across dimensions:
```fortran
! Add vector to each row of matrix
function broadcast_add(matrix, vector) result(output)
    real, dimension(:,:), intent(in) :: matrix
    real, dimension(:), intent(in) :: vector
    real, dimension(size(matrix,1), size(matrix,2)) :: output
    integer :: i
    
    do i = 1, size(matrix, 1)
        output(i,:) = matrix(i,:) + vector
    end do
end function broadcast_add
```

### Batch Operations
Process multiple samples simultaneously:
```fortran
! Process batch of inputs through layer
function batch_forward(X_batch, weights, bias) result(output)
    real, dimension(:,:), intent(in) :: X_batch  ! (batch_size, n_features)
    real, dimension(:), intent(in) :: weights
    real, intent(in) :: bias
    real, dimension(size(X_batch,1)) :: output
    
    output = matmul(X_batch, weights) + bias
end function batch_forward
```

## Exercises

1. Implement matrix determinant calculation
2. Write a function for matrix inversion
3. Create a function for eigenvalue computation
4. Implement QR decomposition
5. Write efficient matrix-vector multiplication

## Next Steps

Now that you understand linear algebra fundamentals, continue to:
- [Neural Networks Theory](04-neural-networks.md)
- Implement beginner examples using these concepts

## References

- **Books**:
  - "Linear Algebra and Its Applications" by Gilbert Strang
  - "Introduction to Linear Algebra for Applied Machine Learning with Python" by JP Uebelacker
  
- **Online**:
  - MIT OCW Linear Algebra course
  - 3Blue1Brown Essence of Linear Algebra series

---

Master these concepts before moving to [Neural Networks](04-neural-networks.md)!
