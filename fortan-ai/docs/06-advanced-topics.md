# Advanced Topics in AI with Fortran

Explore advanced concepts in modern AI and deep learning.

## Table of Contents
- [Convolutional Neural Networks](#convolutional-neural-networks)
- [Recurrent Neural Networks](#recurrent-neural-networks)
- [Regularization Techniques](#regularization-techniques)
- [Batch Normalization](#batch-normalization)
- [Transfer Learning](#transfer-learning)
- [Parallel Computing](#parallel-computing)
- [Production Deployment](#production-deployment)

## Convolutional Neural Networks

CNNs are specialized for processing grid-like data such as images.

### Key Concepts

#### 1. Convolution Operation
Apply filters to extract features from input.

```
Output(i,j) = Σ Σ Input(i+m, j+n) × Kernel(m,n)
             m  n
```

#### 2. CNN Layers
- **Convolutional Layer**: Feature extraction
- **Pooling Layer**: Dimensionality reduction
- **Fully Connected Layer**: Classification

### Implementation

```fortran
module cnn_layer
    implicit none
    
    type :: ConvLayer
        integer :: kernel_size, n_filters, stride, padding
        real, allocatable :: kernels(:,:,:,:)  ! (n_filters, channels, h, w)
        real, allocatable :: biases(:)
    contains
        procedure :: init => conv_init
        procedure :: forward => conv_forward
    end type ConvLayer
    
contains
    
    subroutine conv_init(self, n_filters, channels, kernel_size, stride, padding)
        class(ConvLayer), intent(inout) :: self
        integer, intent(in) :: n_filters, channels, kernel_size
        integer, intent(in), optional :: stride, padding
        
        self%n_filters = n_filters
        self%kernel_size = kernel_size
        self%stride = 1
        self%padding = 0
        
        if (present(stride)) self%stride = stride
        if (present(padding)) self%padding = padding
        
        allocate(self%kernels(n_filters, channels, kernel_size, kernel_size))
        allocate(self%biases(n_filters))
        
        ! Xavier initialization
        call random_number(self%kernels)
        self%kernels = (self%kernels - 0.5) * &
            sqrt(2.0 / real(channels * kernel_size * kernel_size))
        self%biases = 0.0
    end subroutine conv_init
    
    function conv_forward(self, input) result(output)
        class(ConvLayer), intent(in) :: self
        real, dimension(:,:,:), intent(in) :: input  ! (channels, height, width)
        real, allocatable :: output(:,:,:)  ! (n_filters, out_h, out_w)
        integer :: out_h, out_w, f, i, j, c, ki, kj
        real :: sum_val
        
        ! Calculate output dimensions
        out_h = (size(input,2) + 2*self%padding - self%kernel_size) / &
                self%stride + 1
        out_w = (size(input,3) + 2*self%padding - self%kernel_size) / &
                self%stride + 1
        
        allocate(output(self%n_filters, out_h, out_w))
        
        ! Perform convolution
        do f = 1, self%n_filters
            do i = 1, out_h
                do j = 1, out_w
                    sum_val = 0.0
                    do c = 1, size(input, 1)
                        do ki = 1, self%kernel_size
                            do kj = 1, self%kernel_size
                                sum_val = sum_val + &
                                    input(c, &
                                          (i-1)*self%stride + ki, &
                                          (j-1)*self%stride + kj) * &
                                    self%kernels(f, c, ki, kj)
                            end do
                        end do
                    end do
                    output(f, i, j) = sum_val + self%biases(f)
                end do
            end do
        end do
    end function conv_forward
    
end module cnn_layer
```

### Pooling Layer

```fortran
function max_pooling(input, pool_size, stride) result(output)
    real, dimension(:,:,:), intent(in) :: input
    integer, intent(in) :: pool_size, stride
    real, allocatable :: output(:,:,:)
    integer :: out_h, out_w, c, i, j, pi, pj
    real :: max_val
    
    out_h = (size(input,2) - pool_size) / stride + 1
    out_w = (size(input,3) - pool_size) / stride + 1
    
    allocate(output(size(input,1), out_h, out_w))
    
    do c = 1, size(input, 1)
        do i = 1, out_h
            do j = 1, out_w
                max_val = -huge(1.0)
                do pi = 1, pool_size
                    do pj = 1, pool_size
                        max_val = max(max_val, &
                            input(c, (i-1)*stride + pi, (j-1)*stride + pj))
                    end do
                end do
                output(c, i, j) = max_val
            end do
        end do
    end do
end function max_pooling
```

## Recurrent Neural Networks

RNNs process sequential data with internal memory.

### Basic RNN Cell

```fortran
module rnn_cell
    implicit none
    
    type :: RNNCell
        integer :: input_size, hidden_size
        real, allocatable :: Wxh(:,:)  ! Input to hidden
        real, allocatable :: Whh(:,:)  ! Hidden to hidden
        real, allocatable :: Why(:,:)  ! Hidden to output
        real, allocatable :: bh(:), by(:)
        real, allocatable :: hidden_state(:)
    contains
        procedure :: init => rnn_init
        procedure :: forward => rnn_forward
    end type RNNCell
    
contains
    
    subroutine rnn_init(self, input_size, hidden_size, output_size)
        class(RNNCell), intent(inout) :: self
        integer, intent(in) :: input_size, hidden_size, output_size
        
        self%input_size = input_size
        self%hidden_size = hidden_size
        
        allocate(self%Wxh(hidden_size, input_size))
        allocate(self%Whh(hidden_size, hidden_size))
        allocate(self%Why(output_size, hidden_size))
        allocate(self%bh(hidden_size))
        allocate(self%by(output_size))
        allocate(self%hidden_state(hidden_size))
        
        ! Initialize weights
        call random_number(self%Wxh)
        call random_number(self%Whh)
        call random_number(self%Why)
        self%Wxh = (self%Wxh - 0.5) * 0.1
        self%Whh = (self%Whh - 0.5) * 0.1
        self%Why = (self%Why - 0.5) * 0.1
        self%bh = 0.0
        self%by = 0.0
        self%hidden_state = 0.0
    end subroutine rnn_init
    
    function rnn_forward(self, input) result(output)
        class(RNNCell), intent(inout) :: self
        real, dimension(:), intent(in) :: input
        real, dimension(size(self%by)) :: output
        
        ! Update hidden state: h_t = tanh(Wxh·x_t + Whh·h_{t-1} + bh)
        self%hidden_state = tanh(matmul(self%Wxh, input) + &
                                  matmul(self%Whh, self%hidden_state) + &
                                  self%bh)
        
        ! Compute output: y_t = Why·h_t + by
        output = matmul(self%Why, self%hidden_state) + self%by
    end function rnn_forward
    
end module rnn_cell
```

### LSTM (Long Short-Term Memory)

```fortran
! LSTM cell with forget, input, and output gates
type :: LSTMCell
    real, allocatable :: Wf(:,:), Wi(:,:), Wo(:,:), Wc(:,:)
    real, allocatable :: bf(:), bi(:), bo(:), bc(:)
    real, allocatable :: hidden_state(:), cell_state(:)
contains
    procedure :: forward => lstm_forward
end type LSTMCell
```

## Regularization Techniques

Prevent overfitting and improve generalization.

### 1. L2 Regularization (Weight Decay)

```fortran
real function l2_regularization(weights, lambda)
    real, dimension(:), intent(in) :: weights
    real, intent(in) :: lambda
    
    l2_regularization = lambda * sum(weights**2) / 2.0
end function l2_regularization

! Update with L2 regularization
subroutine update_weights_l2(weights, gradient, lr, lambda)
    real, dimension(:), intent(inout) :: weights
    real, dimension(:), intent(in) :: gradient
    real, intent(in) :: lr, lambda
    
    weights = weights - lr * (gradient + lambda * weights)
end subroutine update_weights_l2
```

### 2. Dropout

```fortran
function apply_dropout(input, dropout_rate) result(output)
    real, dimension(:), intent(in) :: input
    real, intent(in) :: dropout_rate
    real, dimension(size(input)) :: output, mask
    
    call random_number(mask)
    
    ! Create dropout mask
    where (mask < dropout_rate)
        mask = 0.0
    elsewhere
        mask = 1.0 / (1.0 - dropout_rate)  ! Scale remaining units
    end where
    
    output = input * mask
end function apply_dropout
```

### 3. Early Stopping

```fortran
subroutine train_with_early_stopping(net, X_train, y_train, X_val, y_val, &
                                      patience)
    type(Network), intent(inout) :: net
    real, dimension(:,:), intent(in) :: X_train, y_train, X_val, y_val
    integer, intent(in) :: patience
    integer :: epochs_without_improvement, epoch
    real :: best_val_loss, val_loss
    
    best_val_loss = huge(1.0)
    epochs_without_improvement = 0
    
    do epoch = 1, 10000
        ! Train for one epoch
        call net%train_epoch(X_train, y_train)
        
        ! Validate
        val_loss = net%evaluate(X_val, y_val)
        
        if (val_loss < best_val_loss) then
            best_val_loss = val_loss
            epochs_without_improvement = 0
            ! Save best model
        else
            epochs_without_improvement = epochs_without_improvement + 1
        end if
        
        if (epochs_without_improvement >= patience) then
            print *, "Early stopping at epoch", epoch
            exit
        end if
    end do
end subroutine train_with_early_stopping
```

## Batch Normalization

Normalize layer inputs to improve training stability.

```fortran
module batch_norm
    implicit none
    
    type :: BatchNormLayer
        real :: epsilon, momentum
        real, allocatable :: gamma(:), beta(:)  ! Learnable parameters
        real, allocatable :: running_mean(:), running_var(:)
    contains
        procedure :: init => bn_init
        procedure :: forward => bn_forward
    end type BatchNormLayer
    
contains
    
    subroutine bn_init(self, n_features, momentum, epsilon)
        class(BatchNormLayer), intent(inout) :: self
        integer, intent(in) :: n_features
        real, intent(in), optional :: momentum, epsilon
        
        self%momentum = 0.9
        if (present(momentum)) self%momentum = momentum
        
        self%epsilon = 1.0e-5
        if (present(epsilon)) self%epsilon = epsilon
        
        allocate(self%gamma(n_features))
        allocate(self%beta(n_features))
        allocate(self%running_mean(n_features))
        allocate(self%running_var(n_features))
        
        self%gamma = 1.0
        self%beta = 0.0
        self%running_mean = 0.0
        self%running_var = 1.0
    end subroutine bn_init
    
    function bn_forward(self, input, training) result(output)
        class(BatchNormLayer), intent(inout) :: self
        real, dimension(:,:), intent(in) :: input  ! (batch_size, features)
        logical, intent(in) :: training
        real, dimension(size(input,1), size(input,2)) :: output
        real, dimension(size(input,2)) :: mean, var, std
        integer :: i
        
        if (training) then
            ! Compute batch statistics
            do i = 1, size(input, 2)
                mean(i) = sum(input(:,i)) / size(input, 1)
                var(i) = sum((input(:,i) - mean(i))**2) / size(input, 1)
            end do
            
            ! Update running statistics
            self%running_mean = self%momentum * self%running_mean + &
                                (1.0 - self%momentum) * mean
            self%running_var = self%momentum * self%running_var + &
                               (1.0 - self%momentum) * var
        else
            mean = self%running_mean
            var = self%running_var
        end if
        
        ! Normalize
        std = sqrt(var + self%epsilon)
        do i = 1, size(input, 2)
            output(:,i) = (input(:,i) - mean(i)) / std(i)
            output(:,i) = self%gamma(i) * output(:,i) + self%beta(i)
        end do
    end function bn_forward
    
end module batch_norm
```

## Parallel Computing

Leverage Fortran's parallel capabilities for faster training.

### OpenMP Parallelization

```fortran
subroutine parallel_matrix_multiply(A, B, C)
    real, dimension(:,:), intent(in) :: A, B
    real, dimension(:,:), intent(out) :: C
    integer :: i, j, k
    
    !$OMP PARALLEL DO PRIVATE(i,j,k) SHARED(A,B,C)
    do i = 1, size(A, 1)
        do j = 1, size(B, 2)
            C(i,j) = 0.0
            do k = 1, size(A, 2)
                C(i,j) = C(i,j) + A(i,k) * B(k,j)
            end do
        end do
    end do
    !$OMP END PARALLEL DO
end subroutine parallel_matrix_multiply
```

### Data Parallel Training

```fortran
subroutine parallel_batch_training(net, X, y, n_threads)
    type(Network), intent(inout) :: net
    real, dimension(:,:), intent(in) :: X, y
    integer, intent(in) :: n_threads
    integer :: i, batch_size, thread_id
    
    batch_size = size(X, 1) / n_threads
    
    !$OMP PARALLEL NUM_THREADS(n_threads) PRIVATE(thread_id, i)
    thread_id = omp_get_thread_num()
    
    ! Each thread processes its portion of data
    do i = thread_id * batch_size + 1, (thread_id + 1) * batch_size
        call net%train_sample(X(i,:), y(i,:))
    end do
    !$OMP END PARALLEL
end subroutine parallel_batch_training
```

### Coarrays for Distributed Computing

```fortran
program distributed_training
    implicit none
    real, dimension(100,10) :: X[*]  ! Coarray
    real, dimension(100,1) :: y[*]
    integer :: this_image, num_images
    
    this_image = this_image()
    num_images = num_images()
    
    ! Each image trains on its portion
    print *, "Image", this_image, "of", num_images, "training..."
    
    ! Synchronize between images
    sync all
    
    ! Aggregate results
    ! ...
end program distributed_training
```

## Production Deployment

### Model Serialization

```fortran
subroutine save_model(net, filename)
    type(Network), intent(in) :: net
    character(len=*), intent(in) :: filename
    integer :: unit, i
    
    open(newunit=unit, file=filename, form='unformatted', &
         action='write', status='replace')
    
    write(unit) net%n_layers
    
    do i = 1, net%n_layers
        write(unit) net%layers(i)%weights
        write(unit) net%layers(i)%biases
    end do
    
    close(unit)
end subroutine save_model

subroutine load_model(net, filename)
    type(Network), intent(inout) :: net
    character(len=*), intent(in) :: filename
    integer :: unit, i
    
    open(newunit=unit, file=filename, form='unformatted', &
         action='read', status='old')
    
    read(unit) net%n_layers
    
    do i = 1, net%n_layers
        read(unit) net%layers(i)%weights
        read(unit) net%layers(i)%biases
    end do
    
    close(unit)
end subroutine load_model
```

## Best Practices

1. **Use CNNs** for image data
2. **Use RNNs/LSTMs** for sequential data
3. **Apply regularization** to prevent overfitting
4. **Use batch normalization** for deep networks
5. **Parallelize** for large-scale training
6. **Save checkpoints** during training
7. **Monitor metrics** continuously

## Further Exploration

- Attention mechanisms
- Generative Adversarial Networks (GANs)
- Reinforcement Learning
- AutoML and Neural Architecture Search
- Quantum Machine Learning

## References

- "Deep Learning" by Goodfellow, Bengio, and Courville
- CS231n: Convolutional Neural Networks
- CS224n: Natural Language Processing
- Fortran OpenMP and Coarray documentation

---

Congratulations on completing the Fortran AI journey from zero to expert! 🎉
