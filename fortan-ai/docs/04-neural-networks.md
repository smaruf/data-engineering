# Neural Networks Theory and Implementation

Understanding neural networks from first principles - the foundation of deep learning.

## Table of Contents
- [What are Neural Networks?](#what-are-neural-networks)
- [The Perceptron](#the-perceptron)
- [Activation Functions](#activation-functions)
- [Multi-Layer Networks](#multi-layer-networks)
- [Forward Propagation](#forward-propagation)
- [Loss Functions](#loss-functions)
- [Backpropagation](#backpropagation)
- [Training Process](#training-process)
- [Implementation Guide](#implementation-guide)

## What are Neural Networks?

Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers that transform input data into output predictions.

### Key Characteristics
- **Learn from data**: Adjust parameters through training
- **Non-linear**: Can model complex relationships
- **Hierarchical**: Build increasingly abstract representations
- **General-purpose**: Applicable to various problems

## The Perceptron

The simplest neural network unit.

### Mathematical Model
```
output = activation(Σ(wᵢ × xᵢ) + b)
```

Where:
- x: Input features
- w: Weights
- b: Bias
- activation: Non-linear function

### Fortran Implementation

```fortran
module perceptron_module
    implicit none
    
    type :: Perceptron
        integer :: n_inputs
        real, allocatable :: weights(:)
        real :: bias
        real :: learning_rate
    contains
        procedure :: init => perceptron_init
        procedure :: predict => perceptron_predict
        procedure :: train => perceptron_train
    end type Perceptron
    
contains
    
    subroutine perceptron_init(self, n_inputs, lr)
        class(Perceptron), intent(inout) :: self
        integer, intent(in) :: n_inputs
        real, intent(in) :: lr
        
        self%n_inputs = n_inputs
        self%learning_rate = lr
        
        allocate(self%weights(n_inputs))
        call random_number(self%weights)
        self%weights = self%weights * 0.1  ! Small random values
        call random_number(self%bias)
        self%bias = self%bias * 0.1
    end subroutine perceptron_init
    
    real function perceptron_predict(self, inputs)
        class(Perceptron), intent(in) :: self
        real, dimension(:), intent(in) :: inputs
        real :: weighted_sum
        
        weighted_sum = dot_product(self%weights, inputs) + self%bias
        
        ! Step activation function
        if (weighted_sum > 0.0) then
            perceptron_predict = 1.0
        else
            perceptron_predict = 0.0
        end if
    end function perceptron_predict
    
    subroutine perceptron_train(self, X, y, epochs)
        class(Perceptron), intent(inout) :: self
        real, dimension(:,:), intent(in) :: X
        real, dimension(:), intent(in) :: y
        integer, intent(in) :: epochs
        integer :: epoch, i
        real :: prediction, error
        
        do epoch = 1, epochs
            do i = 1, size(y)
                prediction = self%predict(X(i,:))
                error = y(i) - prediction
                
                ! Update weights: w = w + η * error * x
                self%weights = self%weights + &
                    self%learning_rate * error * X(i,:)
                self%bias = self%bias + self%learning_rate * error
            end do
        end do
    end subroutine perceptron_train
    
end module perceptron_module
```

## Activation Functions

Activation functions introduce non-linearity, enabling networks to learn complex patterns.

### Common Activation Functions

#### 1. Sigmoid
```
σ(x) = 1 / (1 + e^(-x))
```
- Output range: (0, 1)
- Use: Binary classification, output layer

```fortran
real function sigmoid(x)
    real, intent(in) :: x
    sigmoid = 1.0 / (1.0 + exp(-x))
end function sigmoid

real function sigmoid_derivative(x)
    real, intent(in) :: x
    real :: s
    s = sigmoid(x)
    sigmoid_derivative = s * (1.0 - s)
end function sigmoid_derivative
```

#### 2. Tanh (Hyperbolic Tangent)
```
tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))
```
- Output range: (-1, 1)
- Use: Hidden layers, centered around zero

```fortran
real function tanh_activation(x)
    real, intent(in) :: x
    tanh_activation = tanh(x)
end function tanh_activation

real function tanh_derivative(x)
    real, intent(in) :: x
    real :: t
    t = tanh(x)
    tanh_derivative = 1.0 - t**2
end function tanh_derivative
```

#### 3. ReLU (Rectified Linear Unit)
```
ReLU(x) = max(0, x)
```
- Output range: [0, ∞)
- Use: Hidden layers, most common in deep learning

```fortran
real function relu(x)
    real, intent(in) :: x
    relu = max(0.0, x)
end function relu

real function relu_derivative(x)
    real, intent(in) :: x
    if (x > 0.0) then
        relu_derivative = 1.0
    else
        relu_derivative = 0.0
    end if
end function relu_derivative
```

#### 4. Softmax
```
softmax(xᵢ) = e^xᵢ / Σ(e^xⱼ)
```
- Output range: (0, 1), sum = 1
- Use: Multi-class classification output

```fortran
function softmax(x) result(output)
    real, dimension(:), intent(in) :: x
    real, dimension(size(x)) :: output
    real :: max_x, sum_exp
    
    ! Numerical stability: subtract max
    max_x = maxval(x)
    output = exp(x - max_x)
    sum_exp = sum(output)
    output = output / sum_exp
end function softmax
```

### Activation Function Module

```fortran
module activation_functions
    implicit none
contains
    
    ! Apply activation function to array
    function apply_activation(x, activation_type) result(output)
        real, dimension(:), intent(in) :: x
        character(len=*), intent(in) :: activation_type
        real, dimension(size(x)) :: output
        integer :: i
        
        select case (trim(activation_type))
            case ('sigmoid')
                do i = 1, size(x)
                    output(i) = 1.0 / (1.0 + exp(-x(i)))
                end do
            case ('tanh')
                output = tanh(x)
            case ('relu')
                output = max(0.0, x)
            case ('linear')
                output = x
            case default
                output = x
        end select
    end function apply_activation
    
    ! Compute derivative
    function activation_derivative(x, activation_type) result(output)
        real, dimension(:), intent(in) :: x
        character(len=*), intent(in) :: activation_type
        real, dimension(size(x)) :: output
        real :: s
        integer :: i
        
        select case (trim(activation_type))
            case ('sigmoid')
                do i = 1, size(x)
                    s = 1.0 / (1.0 + exp(-x(i)))
                    output(i) = s * (1.0 - s)
                end do
            case ('tanh')
                output = 1.0 - tanh(x)**2
            case ('relu')
                do i = 1, size(x)
                    if (x(i) > 0.0) then
                        output(i) = 1.0
                    else
                        output(i) = 0.0
                    end if
                end do
            case default
                output = 1.0
        end select
    end function activation_derivative
    
end module activation_functions
```

## Multi-Layer Networks

### Architecture
```
Input Layer → Hidden Layer(s) → Output Layer
```

### Network Structure
- **Input Layer**: Receives features
- **Hidden Layers**: Extract patterns
- **Output Layer**: Makes predictions

### Layer Sizes
- Input: Number of features
- Hidden: Hyperparameter (e.g., 16, 32, 64)
- Output: Number of classes/targets

## Forward Propagation

The process of computing output from input through the network.

### Algorithm
1. Initialize input with data
2. For each layer:
   - Compute: z = W·x + b
   - Apply activation: a = σ(z)
   - Pass to next layer
3. Return final output

### Implementation

```fortran
module neural_network
    implicit none
    
    type :: Layer
        integer :: n_inputs, n_outputs
        real, allocatable :: weights(:,:)
        real, allocatable :: biases(:)
        real, allocatable :: activations(:)
        real, allocatable :: z_values(:)
        character(len=20) :: activation_type
    end type Layer
    
    type :: Network
        type(Layer), allocatable :: layers(:)
        integer :: n_layers
        real :: learning_rate
    contains
        procedure :: init => network_init
        procedure :: forward => network_forward
        procedure :: backward => network_backward
        procedure :: train => network_train
    end type Network
    
contains
    
    subroutine network_init(self, layer_sizes, activation, lr)
        class(Network), intent(inout) :: self
        integer, dimension(:), intent(in) :: layer_sizes
        character(len=*), intent(in) :: activation
        real, intent(in) :: lr
        integer :: i, n_in, n_out
        
        self%n_layers = size(layer_sizes) - 1
        self%learning_rate = lr
        
        allocate(self%layers(self%n_layers))
        
        do i = 1, self%n_layers
            n_in = layer_sizes(i)
            n_out = layer_sizes(i+1)
            
            self%layers(i)%n_inputs = n_in
            self%layers(i)%n_outputs = n_out
            self%layers(i)%activation_type = activation
            
            allocate(self%layers(i)%weights(n_out, n_in))
            allocate(self%layers(i)%biases(n_out))
            allocate(self%layers(i)%activations(n_out))
            allocate(self%layers(i)%z_values(n_out))
            
            ! Xavier initialization
            call random_number(self%layers(i)%weights)
            self%layers(i)%weights = (self%layers(i)%weights - 0.5) * &
                sqrt(2.0 / real(n_in))
            self%layers(i)%biases = 0.0
        end do
    end subroutine network_init
    
    function network_forward(self, input) result(output)
        class(Network), intent(inout) :: self
        real, dimension(:), intent(in) :: input
        real, dimension(self%layers(self%n_layers)%n_outputs) :: output
        real, allocatable :: current_input(:)
        integer :: i
        
        allocate(current_input(size(input)))
        current_input = input
        
        do i = 1, self%n_layers
            ! Linear transformation
            self%layers(i)%z_values = matmul(self%layers(i)%weights, &
                                              current_input) + &
                                       self%layers(i)%biases
            
            ! Activation
            if (trim(self%layers(i)%activation_type) == 'sigmoid') then
                self%layers(i)%activations = 1.0 / (1.0 + &
                    exp(-self%layers(i)%z_values))
            else if (trim(self%layers(i)%activation_type) == 'relu') then
                self%layers(i)%activations = max(0.0, &
                    self%layers(i)%z_values)
            else
                self%layers(i)%activations = self%layers(i)%z_values
            end if
            
            ! Update input for next layer
            deallocate(current_input)
            allocate(current_input(self%layers(i)%n_outputs))
            current_input = self%layers(i)%activations
        end do
        
        output = self%layers(self%n_layers)%activations
    end function network_forward
    
end module neural_network
```

## Loss Functions

Measure how well the network performs.

### Mean Squared Error (MSE)
For regression problems:
```
MSE = (1/n) Σ(yᵢ - ŷᵢ)²
```

```fortran
real function mse_loss(y_true, y_pred)
    real, dimension(:), intent(in) :: y_true, y_pred
    mse_loss = sum((y_true - y_pred)**2) / size(y_true)
end function mse_loss
```

### Binary Cross-Entropy
For binary classification:
```
BCE = -(1/n) Σ[y·log(ŷ) + (1-y)·log(1-ŷ)]
```

```fortran
real function binary_crossentropy(y_true, y_pred)
    real, dimension(:), intent(in) :: y_true, y_pred
    real, dimension(size(y_true)) :: epsilon_pred
    real, parameter :: epsilon = 1.0e-7
    
    ! Clip predictions for numerical stability
    epsilon_pred = max(epsilon, min(1.0 - epsilon, y_pred))
    
    binary_crossentropy = -sum(y_true * log(epsilon_pred) + &
        (1.0 - y_true) * log(1.0 - epsilon_pred)) / size(y_true)
end function binary_crossentropy
```

## Backpropagation

The algorithm for training neural networks using gradient descent.

### Algorithm
1. Forward pass: Compute predictions
2. Compute loss
3. Backward pass: Compute gradients
   - Output layer: δ = (ŷ - y) ⊙ σ'(z)
   - Hidden layers: δ = (W^T·δ_{next}) ⊙ σ'(z)
4. Update weights: W = W - η·δ·a^T
5. Update biases: b = b - η·δ

### The Chain Rule
```
∂Loss/∂w = (∂Loss/∂a) · (∂a/∂z) · (∂z/∂w)
```

## Training Process

### Complete Training Algorithm

```fortran
subroutine network_train(self, X, y, epochs, batch_size)
    class(Network), intent(inout) :: self
    real, dimension(:,:), intent(in) :: X  ! (n_samples, n_features)
    real, dimension(:,:), intent(in) :: y  ! (n_samples, n_outputs)
    integer, intent(in) :: epochs, batch_size
    integer :: epoch, i, n_samples
    real :: loss
    real, dimension(size(y,2)) :: prediction, target
    
    n_samples = size(X, 1)
    
    do epoch = 1, epochs
        loss = 0.0
        
        do i = 1, n_samples
            ! Forward pass
            prediction = self%forward(X(i,:))
            target = y(i,:)
            
            ! Compute loss
            loss = loss + sum((target - prediction)**2)
            
            ! Backward pass
            call self%backward(X(i,:), target)
        end do
        
        loss = loss / n_samples
        
        if (mod(epoch, 100) == 0) then
            print '(A,I5,A,F10.6)', 'Epoch ', epoch, ' Loss: ', loss
        end if
    end do
end subroutine network_train
```

## Implementation Guide

### Step-by-Step Process

1. **Define Network Architecture**
```fortran
type(Network) :: net
integer, dimension(3) :: layers = [2, 4, 1]  ! 2 inputs, 4 hidden, 1 output
call net%init(layers, 'sigmoid', 0.1)
```

2. **Prepare Data**
```fortran
real, dimension(4,2) :: X_train
real, dimension(4,1) :: y_train
! XOR problem
X_train = reshape([0.0,0.0, 0.0,1.0, 1.0,0.0, 1.0,1.0], [4,2])
y_train = reshape([0.0, 1.0, 1.0, 0.0], [4,1])
```

3. **Train Network**
```fortran
call net%train(X_train, y_train, epochs=10000, batch_size=4)
```

4. **Make Predictions**
```fortran
real, dimension(1) :: prediction
prediction = net%forward([0.0, 1.0])
print *, "Prediction:", prediction
```

## Best Practices

1. **Weight Initialization**: Use Xavier or He initialization
2. **Learning Rate**: Start with 0.01-0.1, adjust as needed
3. **Activation Functions**: ReLU for hidden, sigmoid/softmax for output
4. **Normalization**: Normalize input features
5. **Regularization**: Add L2 regularization to prevent overfitting

## Next Steps

- [Optimization Algorithms](05-optimization.md)
- [Advanced Topics](06-advanced-topics.md)
- Implement intermediate examples

## References

- "Neural Networks and Deep Learning" by Michael Nielsen
- "Deep Learning" by Goodfellow, Bengio, and Courville
- CS231n Stanford course materials

---

Continue to [Optimization Algorithms](05-optimization.md) to improve training!
