# Modern Fortran Basics for AI

A refresher on modern Fortran features needed for AI implementation.

## Table of Contents
- [Program Structure](#program-structure)
- [Variables and Types](#variables-and-types)
- [Arrays](#arrays)
- [Control Structures](#control-structures)
- [Procedures](#procedures)
- [Modules](#modules)
- [Derived Types](#derived-types)
- [File I/O](#file-io)

## Program Structure

### Basic Program
```fortran
program hello_fortran
    implicit none
    
    ! Variable declarations
    integer :: n
    real :: x
    
    ! Executable statements
    n = 42
    x = 3.14159
    
    print *, "Hello from Fortran!"
    print *, "n =", n, "x =", x
    
end program hello_fortran
```

**Key Points**:
- `implicit none`: Disables implicit typing (best practice)
- Comments start with `!`
- Fortran is case-insensitive (but use lowercase by convention)

## Variables and Types

### Basic Data Types
```fortran
implicit none

! Integer types
integer :: i                    ! Default integer
integer(kind=4) :: i32         ! 32-bit integer
integer(kind=8) :: i64         ! 64-bit integer

! Real (floating-point) types
real :: r                      ! Default real (usually 32-bit)
real(kind=4) :: r32           ! Single precision
real(kind=8) :: r64           ! Double precision

! Complex numbers
complex :: c
c = (1.0, 2.0)                ! 1 + 2i

! Logical (boolean)
logical :: flag
flag = .true.
flag = .false.

! Character strings
character(len=10) :: name
character(len=:), allocatable :: dynamic_str

name = "Fortran"
dynamic_str = "Dynamic length string"
```

### Constants
```fortran
real, parameter :: PI = 3.14159265358979323846
real, parameter :: E = 2.71828182845904523536
integer, parameter :: MAX_ITERATIONS = 1000
```

## Arrays

Arrays are first-class citizens in Fortran and crucial for AI.

### Array Declarations
```fortran
implicit none

! Static arrays
real, dimension(10) :: vector               ! 1D array
real, dimension(3, 3) :: matrix            ! 2D array
real, dimension(2, 3, 4) :: tensor         ! 3D array

! Alternative syntax
real :: vector(10)
real :: matrix(3, 3)

! Custom indexing
real, dimension(0:9) :: zero_based        ! Indices 0-9
real, dimension(-5:5) :: centered         ! Indices -5 to 5

! Dynamic arrays (allocatable)
real, dimension(:), allocatable :: dynamic_vector
real, dimension(:,:), allocatable :: dynamic_matrix

! Allocate memory
allocate(dynamic_vector(100))
allocate(dynamic_matrix(50, 50))

! Deallocate when done
deallocate(dynamic_vector)
deallocate(dynamic_matrix)
```

### Array Operations
```fortran
real, dimension(5) :: a, b, c
real :: scalar

! Initialize arrays
a = [1.0, 2.0, 3.0, 4.0, 5.0]
b = [2.0, 3.0, 4.0, 5.0, 6.0]

! Element-wise operations
c = a + b                      ! Addition
c = a * b                      ! Element-wise multiplication
c = a / b                      ! Element-wise division
c = a ** 2                     ! Squaring each element

! Scalar operations
c = a * 2.0                    ! Multiply all by scalar

! Array functions
scalar = sum(a)                ! Sum of all elements
scalar = product(a)            ! Product of all elements
scalar = maxval(a)             ! Maximum value
scalar = minval(a)             ! Minimum value
scalar = dot_product(a, b)     ! Dot product

! Array inquiry
print *, size(a)               ! Array size
print *, shape(matrix)         ! Array dimensions
```

### Array Slicing
```fortran
real, dimension(10) :: x
real, dimension(3, 3) :: m

! Array sections
x(1:5)                         ! Elements 1 through 5
x(1:10:2)                      ! Every other element
x(:)                           ! All elements

! Matrix slicing
m(1, :)                        ! First row
m(:, 2)                        ! Second column
m(1:2, 1:2)                    ! Top-left 2x2 submatrix
```

## Control Structures

### If Statements
```fortran
real :: x = 5.0

! Simple if
if (x > 0) then
    print *, "Positive"
end if

! If-else
if (x > 0) then
    print *, "Positive"
else
    print *, "Non-positive"
end if

! If-else if-else
if (x > 0) then
    print *, "Positive"
else if (x < 0) then
    print *, "Negative"
else
    print *, "Zero"
end if
```

### Loops

#### Do Loop
```fortran
integer :: i

! Basic do loop
do i = 1, 10
    print *, i
end do

! Do loop with step
do i = 1, 10, 2
    print *, i              ! Prints 1, 3, 5, 7, 9
end do

! While-style loop
i = 1
do while (i <= 10)
    print *, i
    i = i + 1
end do
```

### Select Case
```fortran
integer :: choice

select case (choice)
    case (1)
        print *, "Option 1"
    case (2)
        print *, "Option 2"
    case (3:5)
        print *, "Options 3, 4, or 5"
    case default
        print *, "Other option"
end select
```

## Procedures

### Subroutines
```fortran
! Subroutine definition
subroutine matrix_multiply(A, B, C, n)
    implicit none
    integer, intent(in) :: n
    real, dimension(n,n), intent(in) :: A, B
    real, dimension(n,n), intent(out) :: C
    integer :: i, j, k
    
    C = 0.0
    do i = 1, n
        do j = 1, n
            do k = 1, n
                C(i,j) = C(i,j) + A(i,k) * B(k,j)
            end do
        end do
    end do
end subroutine matrix_multiply

! Usage
program test_multiply
    implicit none
    real, dimension(3,3) :: A, B, C
    
    ! Initialize A and B...
    call matrix_multiply(A, B, C, 3)
end program test_multiply
```

### Functions
```fortran
! Function definition
real function sigmoid(x)
    implicit none
    real, intent(in) :: x
    
    sigmoid = 1.0 / (1.0 + exp(-x))
end function sigmoid

! Using the function
program test_sigmoid
    implicit none
    real :: x, y
    real :: sigmoid  ! Function declaration
    
    x = 0.5
    y = sigmoid(x)
    print *, "sigmoid(", x, ") =", y
end program test_sigmoid
```

### Intent Attributes
```fortran
subroutine process_data(input, output, temp)
    real, intent(in) :: input        ! Read-only
    real, intent(out) :: output      ! Write-only
    real, intent(inout) :: temp      ! Read and write
    
    temp = temp + input
    output = temp * 2.0
end subroutine
```

## Modules

Modules organize code and enable code reuse - essential for larger AI projects.

```fortran
! math_utils.f90
module math_utils
    implicit none
    private
    public :: sigmoid, relu, mean
    
    real, parameter :: PI = 3.14159265358979323846
    
contains
    
    real function sigmoid(x)
        real, intent(in) :: x
        sigmoid = 1.0 / (1.0 + exp(-x))
    end function sigmoid
    
    real function relu(x)
        real, intent(in) :: x
        relu = max(0.0, x)
    end function relu
    
    real function mean(array)
        real, dimension(:), intent(in) :: array
        mean = sum(array) / size(array)
    end function mean
    
end module math_utils

! Using the module
program test_module
    use math_utils
    implicit none
    
    real :: x, y
    real, dimension(5) :: data
    
    x = 0.0
    y = sigmoid(x)
    
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    print *, "Mean:", mean(data)
end program test_module
```

## Derived Types

Object-oriented programming in Fortran - crucial for neural network classes.

```fortran
module neural_layer_module
    implicit none
    
    type :: NeuralLayer
        integer :: n_inputs, n_outputs
        real, allocatable :: weights(:,:)
        real, allocatable :: biases(:)
    contains
        procedure :: init => layer_init
        procedure :: forward => layer_forward
    end type NeuralLayer
    
contains
    
    subroutine layer_init(self, n_in, n_out)
        class(NeuralLayer), intent(inout) :: self
        integer, intent(in) :: n_in, n_out
        
        self%n_inputs = n_in
        self%n_outputs = n_out
        
        allocate(self%weights(n_out, n_in))
        allocate(self%biases(n_out))
        
        ! Initialize with random values
        call random_number(self%weights)
        call random_number(self%biases)
    end subroutine layer_init
    
    function layer_forward(self, input) result(output)
        class(NeuralLayer), intent(in) :: self
        real, dimension(:), intent(in) :: input
        real, dimension(self%n_outputs) :: output
        integer :: i
        
        do i = 1, self%n_outputs
            output(i) = dot_product(self%weights(i,:), input) + self%biases(i)
        end do
    end function layer_forward
    
end module neural_layer_module
```

## File I/O

### Reading Data
```fortran
! Read from file
program read_data
    implicit none
    integer :: i, n, unit_num
    real, allocatable :: data(:)
    
    ! Open file
    open(newunit=unit_num, file='data.txt', status='old', action='read')
    
    ! Read number of data points
    read(unit_num, *) n
    
    ! Allocate array
    allocate(data(n))
    
    ! Read data
    do i = 1, n
        read(unit_num, *) data(i)
    end do
    
    ! Close file
    close(unit_num)
    
    print *, "Read", n, "data points"
end program read_data
```

### Writing Data
```fortran
! Write to file
program write_data
    implicit none
    integer :: i, unit_num
    real, dimension(5) :: results
    
    results = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    open(newunit=unit_num, file='output.txt', status='replace', action='write')
    
    do i = 1, size(results)
        write(unit_num, '(F10.4)') results(i)
    end do
    
    close(unit_num)
end program write_data
```

## Best Practices for AI Code

1. **Always use `implicit none`** - Prevents typos from creating variables
2. **Use allocatable arrays** - Dynamic sizing for flexible data
3. **Use modules** - Organize code into logical units
4. **Use intent attributes** - Document parameter usage
5. **Use meaningful names** - `learning_rate` not `lr`
6. **Add comments** - Explain algorithms and formulas
7. **Use array operations** - More efficient than loops
8. **Check allocations** - Handle memory errors gracefully

## Example: Complete AI Module Skeleton

```fortran
module simple_nn
    implicit none
    private
    public :: Network, train, predict
    
    type :: Network
        integer :: n_inputs, n_hidden, n_outputs
        real, allocatable :: w1(:,:), b1(:)
        real, allocatable :: w2(:,:), b2(:)
    contains
        procedure :: init => network_init
    end type Network
    
contains
    
    subroutine network_init(self, n_in, n_hid, n_out)
        class(Network), intent(inout) :: self
        integer, intent(in) :: n_in, n_hid, n_out
        
        self%n_inputs = n_in
        self%n_hidden = n_hid
        self%n_outputs = n_out
        
        allocate(self%w1(n_hid, n_in))
        allocate(self%b1(n_hid))
        allocate(self%w2(n_out, n_hid))
        allocate(self%b2(n_out))
        
        ! Initialize weights randomly
        call random_number(self%w1)
        call random_number(self%b1)
        call random_number(self%w2)
        call random_number(self%b2)
    end subroutine network_init
    
    subroutine train(net, X, y, epochs)
        type(Network), intent(inout) :: net
        real, dimension(:,:), intent(in) :: X, y
        integer, intent(in) :: epochs
        ! Training implementation...
    end subroutine train
    
    function predict(net, X) result(output)
        type(Network), intent(in) :: net
        real, dimension(:), intent(in) :: X
        real, dimension(net%n_outputs) :: output
        ! Prediction implementation...
    end function predict
    
end module simple_nn
```

## Next Steps

Now that you're comfortable with Fortran basics, move on to:
- [Linear Algebra Foundations](03-linear-algebra.md)
- Start implementing the beginner examples

## Quick Reference

### Compilation
```bash
# Compile single file
gfortran -o program program.f90

# Compile with optimization
gfortran -O3 -o program program.f90

# Compile with debugging
gfortran -g -o program program.f90

# Compile multiple files
gfortran -o program module.f90 program.f90
```

### Common Fortran Extensions
- `.f90`, `.f95`, `.f03`, `.f08` - Free-form Fortran (modern)
- `.f`, `.for` - Fixed-form Fortran (legacy)

---

Ready to learn linear algebra? Continue to [Linear Algebra Foundations](03-linear-algebra.md)!
