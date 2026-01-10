# Optimization Algorithms for Neural Networks

Learn advanced optimization techniques to train neural networks more effectively.

## Table of Contents
- [Gradient Descent Variants](#gradient-descent-variants)
- [Momentum](#momentum)
- [AdaGrad](#adagrad)
- [RMSprop](#rmsprop)
- [Adam Optimizer](#adam-optimizer)
- [Learning Rate Scheduling](#learning-rate-scheduling)
- [Implementation in Fortran](#implementation-in-fortran)

## Gradient Descent Variants

### Batch Gradient Descent
Uses entire dataset for each update.

**Advantages**: Stable convergence  
**Disadvantages**: Slow for large datasets

```fortran
subroutine batch_gradient_descent(weights, X, y, learning_rate, epochs)
    real, dimension(:), intent(inout) :: weights
    real, dimension(:,:), intent(in) :: X
    real, dimension(:), intent(in) :: y
    real, intent(in) :: learning_rate
    integer, intent(in) :: epochs
    integer :: epoch, n_samples
    real, dimension(size(weights)) :: gradient
    
    n_samples = size(y)
    
    do epoch = 1, epochs
        ! Compute gradient on entire dataset
        gradient = compute_gradient(weights, X, y)
        
        ! Update weights
        weights = weights - learning_rate * gradient
    end do
end subroutine batch_gradient_descent
```

### Stochastic Gradient Descent (SGD)
Updates weights after each sample.

**Advantages**: Fast, can escape local minima  
**Disadvantages**: Noisy updates

```fortran
subroutine stochastic_gradient_descent(weights, X, y, learning_rate, epochs)
    real, dimension(:), intent(inout) :: weights
    real, dimension(:,:), intent(in) :: X
    real, dimension(:), intent(in) :: y
    real, intent(in) :: learning_rate
    integer, intent(in) :: epochs
    integer :: epoch, i, n_samples
    real, dimension(size(weights)) :: gradient
    
    n_samples = size(y)
    
    do epoch = 1, epochs
        do i = 1, n_samples
            ! Compute gradient for single sample
            gradient = compute_sample_gradient(weights, X(i,:), y(i))
            
            ! Update weights
            weights = weights - learning_rate * gradient
        end do
    end do
end subroutine stochastic_gradient_descent
```

### Mini-Batch Gradient Descent
Compromise between batch and stochastic.

**Advantages**: Balanced speed and stability  
**Batch size**: Typically 32, 64, 128, or 256

```fortran
subroutine minibatch_gradient_descent(weights, X, y, learning_rate, &
                                       epochs, batch_size)
    real, dimension(:), intent(inout) :: weights
    real, dimension(:,:), intent(in) :: X
    real, dimension(:), intent(in) :: y
    real, intent(in) :: learning_rate
    integer, intent(in) :: epochs, batch_size
    integer :: epoch, batch_start, batch_end, n_samples
    real, dimension(size(weights)) :: gradient
    
    n_samples = size(y)
    
    do epoch = 1, epochs
        batch_start = 1
        do while (batch_start <= n_samples)
            batch_end = min(batch_start + batch_size - 1, n_samples)
            
            ! Compute gradient on mini-batch
            gradient = compute_batch_gradient(weights, &
                X(batch_start:batch_end,:), y(batch_start:batch_end))
            
            ! Update weights
            weights = weights - learning_rate * gradient
            
            batch_start = batch_start + batch_size
        end do
    end do
end subroutine minibatch_gradient_descent
```

## Momentum

Accelerates convergence by accumulating past gradients.

### Algorithm
```
v_t = β·v_{t-1} + ∇L
w_t = w_{t-1} - η·v_t
```

Where:
- v: Velocity vector
- β: Momentum coefficient (typically 0.9)
- η: Learning rate

### Implementation

```fortran
module momentum_optimizer
    implicit none
    
    type :: MomentumOptimizer
        real :: learning_rate
        real :: momentum
        real, allocatable :: velocity(:)
    contains
        procedure :: init => momentum_init
        procedure :: update => momentum_update
    end type MomentumOptimizer
    
contains
    
    subroutine momentum_init(self, n_params, lr, beta)
        class(MomentumOptimizer), intent(inout) :: self
        integer, intent(in) :: n_params
        real, intent(in) :: lr, beta
        
        self%learning_rate = lr
        self%momentum = beta
        
        allocate(self%velocity(n_params))
        self%velocity = 0.0
    end subroutine momentum_init
    
    subroutine momentum_update(self, weights, gradient)
        class(MomentumOptimizer), intent(inout) :: self
        real, dimension(:), intent(inout) :: weights
        real, dimension(:), intent(in) :: gradient
        
        ! Update velocity: v = β·v + ∇L
        self%velocity = self%momentum * self%velocity + gradient
        
        ! Update weights: w = w - η·v
        weights = weights - self%learning_rate * self%velocity
    end subroutine momentum_update
    
end module momentum_optimizer
```

### Nesterov Accelerated Gradient (NAG)
Look-ahead variant of momentum.

```fortran
subroutine nesterov_update(weights, gradient, velocity, lr, beta)
    real, dimension(:), intent(inout) :: weights, velocity
    real, dimension(:), intent(in) :: gradient
    real, intent(in) :: lr, beta
    real, dimension(size(weights)) :: look_ahead_gradient
    
    ! Compute gradient at look-ahead position
    look_ahead_gradient = gradient  ! Simplified
    
    ! Update velocity
    velocity = beta * velocity + look_ahead_gradient
    
    ! Update weights
    weights = weights - lr * velocity
end subroutine nesterov_update
```

## AdaGrad

Adapts learning rate for each parameter based on historical gradients.

### Algorithm
```
G_t = G_{t-1} + ∇L²
w_t = w_{t-1} - (η/√(G_t + ε))·∇L
```

### Implementation

```fortran
module adagrad_optimizer
    implicit none
    
    type :: AdaGradOptimizer
        real :: learning_rate
        real :: epsilon
        real, allocatable :: sum_squared_gradients(:)
    contains
        procedure :: init => adagrad_init
        procedure :: update => adagrad_update
    end type AdaGradOptimizer
    
contains
    
    subroutine adagrad_init(self, n_params, lr, eps)
        class(AdaGradOptimizer), intent(inout) :: self
        integer, intent(in) :: n_params
        real, intent(in) :: lr
        real, intent(in), optional :: eps
        
        self%learning_rate = lr
        
        if (present(eps)) then
            self%epsilon = eps
        else
            self%epsilon = 1.0e-8
        end if
        
        allocate(self%sum_squared_gradients(n_params))
        self%sum_squared_gradients = 0.0
    end subroutine adagrad_init
    
    subroutine adagrad_update(self, weights, gradient)
        class(AdaGradOptimizer), intent(inout) :: self
        real, dimension(:), intent(inout) :: weights
        real, dimension(:), intent(in) :: gradient
        
        ! Accumulate squared gradients
        self%sum_squared_gradients = self%sum_squared_gradients + gradient**2
        
        ! Update weights with adaptive learning rate
        weights = weights - (self%learning_rate / &
            sqrt(self%sum_squared_gradients + self%epsilon)) * gradient
    end subroutine adagrad_update
    
end module adagrad_optimizer
```

## RMSprop

Addresses AdaGrad's aggressive learning rate decay.

### Algorithm
```
E[g²]_t = β·E[g²]_{t-1} + (1-β)·∇L²
w_t = w_{t-1} - (η/√(E[g²]_t + ε))·∇L
```

### Implementation

```fortran
module rmsprop_optimizer
    implicit none
    
    type :: RMSpropOptimizer
        real :: learning_rate
        real :: decay_rate
        real :: epsilon
        real, allocatable :: squared_gradients(:)
    contains
        procedure :: init => rmsprop_init
        procedure :: update => rmsprop_update
    end type RMSpropOptimizer
    
contains
    
    subroutine rmsprop_init(self, n_params, lr, decay, eps)
        class(RMSpropOptimizer), intent(inout) :: self
        integer, intent(in) :: n_params
        real, intent(in) :: lr
        real, intent(in), optional :: decay, eps
        
        self%learning_rate = lr
        
        if (present(decay)) then
            self%decay_rate = decay
        else
            self%decay_rate = 0.9
        end if
        
        if (present(eps)) then
            self%epsilon = eps
        else
            self%epsilon = 1.0e-8
        end if
        
        allocate(self%squared_gradients(n_params))
        self%squared_gradients = 0.0
    end subroutine rmsprop_init
    
    subroutine rmsprop_update(self, weights, gradient)
        class(RMSpropOptimizer), intent(inout) :: self
        real, dimension(:), intent(inout) :: weights
        real, dimension(:), intent(in) :: gradient
        
        ! Exponential moving average of squared gradients
        self%squared_gradients = self%decay_rate * self%squared_gradients + &
            (1.0 - self%decay_rate) * gradient**2
        
        ! Update weights
        weights = weights - (self%learning_rate / &
            sqrt(self%squared_gradients + self%epsilon)) * gradient
    end subroutine rmsprop_update
    
end module rmsprop_optimizer
```

## Adam Optimizer

Combines momentum and RMSprop - most popular optimizer in deep learning.

### Algorithm
```
m_t = β₁·m_{t-1} + (1-β₁)·∇L        (First moment)
v_t = β₂·v_{t-1} + (1-β₂)·∇L²       (Second moment)
m̂_t = m_t / (1-β₁^t)                 (Bias correction)
v̂_t = v_t / (1-β₂^t)                 (Bias correction)
w_t = w_{t-1} - η·m̂_t / (√v̂_t + ε)
```

Default parameters:
- β₁ = 0.9
- β₂ = 0.999
- ε = 1e-8

### Implementation

```fortran
module adam_optimizer
    implicit none
    
    type :: AdamOptimizer
        real :: learning_rate
        real :: beta1, beta2
        real :: epsilon
        integer :: t  ! Time step
        real, allocatable :: m(:)  ! First moment
        real, allocatable :: v(:)  ! Second moment
    contains
        procedure :: init => adam_init
        procedure :: update => adam_update
        procedure :: reset => adam_reset
    end type AdamOptimizer
    
contains
    
    subroutine adam_init(self, n_params, lr, beta1, beta2, eps)
        class(AdamOptimizer), intent(inout) :: self
        integer, intent(in) :: n_params
        real, intent(in), optional :: lr, beta1, beta2, eps
        
        ! Set hyperparameters (use defaults if not provided)
        self%learning_rate = 0.001
        if (present(lr)) self%learning_rate = lr
        
        self%beta1 = 0.9
        if (present(beta1)) self%beta1 = beta1
        
        self%beta2 = 0.999
        if (present(beta2)) self%beta2 = beta2
        
        self%epsilon = 1.0e-8
        if (present(eps)) self%epsilon = eps
        
        self%t = 0
        
        ! Initialize moment estimates
        allocate(self%m(n_params))
        allocate(self%v(n_params))
        self%m = 0.0
        self%v = 0.0
    end subroutine adam_init
    
    subroutine adam_update(self, weights, gradient)
        class(AdamOptimizer), intent(inout) :: self
        real, dimension(:), intent(inout) :: weights
        real, dimension(:), intent(in) :: gradient
        real, dimension(size(weights)) :: m_hat, v_hat
        real :: beta1_t, beta2_t
        
        ! Increment time step
        self%t = self%t + 1
        
        ! Update biased first moment estimate
        self%m = self%beta1 * self%m + (1.0 - self%beta1) * gradient
        
        ! Update biased second moment estimate
        self%v = self%beta2 * self%v + (1.0 - self%beta2) * gradient**2
        
        ! Compute bias-corrected first moment
        beta1_t = self%beta1 ** self%t
        m_hat = self%m / (1.0 - beta1_t)
        
        ! Compute bias-corrected second moment
        beta2_t = self%beta2 ** self%t
        v_hat = self%v / (1.0 - beta2_t)
        
        ! Update weights
        weights = weights - self%learning_rate * m_hat / &
            (sqrt(v_hat) + self%epsilon)
    end subroutine adam_update
    
    subroutine adam_reset(self)
        class(AdamOptimizer), intent(inout) :: self
        self%t = 0
        self%m = 0.0
        self%v = 0.0
    end subroutine adam_reset
    
end module adam_optimizer
```

## Learning Rate Scheduling

Adjust learning rate during training for better convergence.

### Step Decay
```fortran
real function step_decay(initial_lr, epoch, drop_rate, epochs_drop)
    real, intent(in) :: initial_lr, drop_rate
    integer, intent(in) :: epoch, epochs_drop
    
    step_decay = initial_lr * (drop_rate ** (epoch / epochs_drop))
end function step_decay
```

### Exponential Decay
```fortran
real function exponential_decay(initial_lr, epoch, decay_rate)
    real, intent(in) :: initial_lr, decay_rate
    integer, intent(in) :: epoch
    
    exponential_decay = initial_lr * exp(-decay_rate * epoch)
end function exponential_decay
```

### Cosine Annealing
```fortran
real function cosine_annealing(initial_lr, epoch, total_epochs)
    real, intent(in) :: initial_lr
    integer, intent(in) :: epoch, total_epochs
    real, parameter :: PI = 3.14159265358979323846
    
    cosine_annealing = initial_lr * 0.5 * &
        (1.0 + cos(PI * epoch / total_epochs))
end function cosine_annealing
```

### Warm Restarts
```fortran
real function cosine_warm_restart(initial_lr, epoch, restart_period)
    real, intent(in) :: initial_lr
    integer, intent(in) :: epoch, restart_period
    real, parameter :: PI = 3.14159265358979323846
    integer :: t_cur
    
    t_cur = mod(epoch, restart_period)
    cosine_warm_restart = initial_lr * 0.5 * &
        (1.0 + cos(PI * t_cur / restart_period))
end function cosine_warm_restart
```

## Comparison of Optimizers

| Optimizer | Pros | Cons | Best For |
|-----------|------|------|----------|
| SGD | Simple, well-understood | Slow convergence | Simple problems |
| Momentum | Faster convergence | Extra hyperparameter | General use |
| AdaGrad | Adaptive rates | Aggressive decay | Sparse data |
| RMSprop | Fixes AdaGrad decay | Needs tuning | RNNs |
| Adam | Fast, robust | Memory overhead | Most problems |

## Implementation in Fortran

### Complete Optimizer Module

```fortran
module optimizers
    use momentum_optimizer
    use adagrad_optimizer
    use rmsprop_optimizer
    use adam_optimizer
    implicit none
    
    ! Generic optimizer interface
    type, abstract :: Optimizer
        real :: learning_rate
    contains
        procedure(update_interface), deferred :: update
    end type Optimizer
    
    abstract interface
        subroutine update_interface(self, weights, gradient)
            import :: Optimizer
            class(Optimizer), intent(inout) :: self
            real, dimension(:), intent(inout) :: weights
            real, dimension(:), intent(in) :: gradient
        end subroutine update_interface
    end interface
    
end module optimizers
```

## Practical Tips

1. **Start with Adam**: Works well for most problems
2. **Tune learning rate**: Most important hyperparameter
3. **Use learning rate schedules**: Improve final performance
4. **Monitor gradients**: Watch for vanishing/exploding gradients
5. **Batch size matters**: Affects gradient noise and memory

## Next Steps

- [Advanced Topics](06-advanced-topics.md)
- Implement optimizers in your neural networks
- Experiment with different optimization strategies

## References

- "Adam: A Method for Stochastic Optimization" (Kingma & Ba, 2014)
- "On the importance of initialization and momentum in deep learning" (Sutskever et al., 2013)
- CS231n lecture notes on optimization

---

Continue to [Advanced Topics](06-advanced-topics.md) for deep learning techniques!
