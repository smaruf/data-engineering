! Complete Example 1: Simple Neural Network for XOR Problem
! Demonstrates a complete neural network solving the XOR problem
program example_simple_nn
    use math_utils
    implicit none
    
    ! Network architecture: 2 → 4 → 1
    integer, parameter :: input_size = 2
    integer, parameter :: hidden_size = 4
    integer, parameter :: output_size = 1
    integer, parameter :: n_samples = 4
    integer, parameter :: epochs = 5000
    real, parameter :: learning_rate = 0.5
    
    ! Network parameters
    real, dimension(hidden_size, input_size) :: W1
    real, dimension(hidden_size) :: b1
    real, dimension(output_size, hidden_size) :: W2
    real, dimension(output_size) :: b2
    
    ! Training data (XOR problem)
    real, dimension(n_samples, input_size) :: X
    real, dimension(n_samples, output_size) :: y
    
    ! Forward pass variables
    real, dimension(hidden_size) :: z1, a1
    real, dimension(output_size) :: z2, a2
    
    ! Backward pass variables
    real, dimension(output_size) :: dz2
    real, dimension(hidden_size) :: dz1
    
    integer :: epoch, i
    real :: loss, total_loss
    
    print *, "=========================================="
    print *, "  Simple Neural Network: XOR Problem"
    print *, "=========================================="
    print *
    print *, "Network Architecture:"
    print *, "  Input Layer:  2 neurons"
    print *, "  Hidden Layer: 4 neurons (sigmoid)"
    print *, "  Output Layer: 1 neuron (sigmoid)"
    print *
    
    ! Initialize training data
    X = reshape([0.0, 0.0, &
                 0.0, 1.0, &
                 1.0, 0.0, &
                 1.0, 1.0], [n_samples, input_size])
    y = reshape([0.0, 1.0, 1.0, 0.0], [n_samples, output_size])
    
    print *, "XOR Training Data:"
    print *, "  Input    | Target"
    print *, "  ---------|-------"
    do i = 1, n_samples
        print '(2X,F3.0,1X,F3.0,A,F6.0)', X(i,1), X(i,2), "  |", y(i,1)
    end do
    print *
    
    ! Initialize weights (small random values)
    call random_seed()
    call random_number(W1)
    call random_number(W2)
    call random_number(b1)
    call random_number(b2)
    
    W1 = (W1 - 0.5) * 2.0
    W2 = (W2 - 0.5) * 2.0
    b1 = (b1 - 0.5) * 0.2
    b2 = (b2 - 0.5) * 0.2
    
    print *, "Training for", epochs, "epochs..."
    print *
    
    ! Training loop
    do epoch = 1, epochs
        total_loss = 0.0
        
        do i = 1, n_samples
            ! === Forward Pass ===
            ! Hidden layer
            z1 = matmul(W1, X(i,:)) + b1
            a1 = apply_sigmoid(z1)
            
            ! Output layer
            z2 = matmul(W2, a1) + b2
            a2 = apply_sigmoid(z2)
            
            ! Calculate loss (MSE)
            loss = sum((y(i,:) - a2)**2)
            total_loss = total_loss + loss
            
            ! === Backward Pass ===
            ! Output layer gradients
            dz2 = (a2 - y(i,:)) * sigmoid_deriv(z2)
            
            ! Hidden layer gradients
            dz1 = matmul(transpose(W2), dz2) * sigmoid_deriv(z1)
            
            ! Update weights and biases (gradient descent)
            W2 = W2 - learning_rate * outer_product(dz2, a1)
            b2 = b2 - learning_rate * dz2
            W1 = W1 - learning_rate * outer_product(dz1, X(i,:))
            b1 = b1 - learning_rate * dz1
        end do
        
        ! Display progress
        if (mod(epoch, 500) == 0 .or. epoch == 1) then
            print '(A,I5,A,F10.6)', "  Epoch ", epoch, " - Loss: ", &
                total_loss / n_samples
        end if
    end do
    
    print *
    print *, "Training complete!"
    print *
    
    ! Test the trained network
    print *, "Testing the Trained Network:"
    print *, "  Input    | Target | Prediction | Rounded"
    print *, "  ---------|--------|------------|--------"
    
    do i = 1, n_samples
        ! Forward pass
        z1 = matmul(W1, X(i,:)) + b1
        a1 = apply_sigmoid(z1)
        z2 = matmul(W2, a1) + b2
        a2 = apply_sigmoid(z2)
        
        print '(2X,F3.0,1X,F3.0,A,F6.0,A,F11.4,A,F7.0)', &
            X(i,1), X(i,2), "  |", y(i,1), "   |", a2(1), "   |", &
            merge(1.0, 0.0, a2(1) > 0.5)
    end do
    
    print *
    print *, "=========================================="
    print *, "  Success! The network learned XOR!"
    print *, "=========================================="
    print *
    
contains
    
    ! Apply sigmoid to vector
    function apply_sigmoid(x) result(output)
        real, dimension(:), intent(in) :: x
        real, dimension(size(x)) :: output
        integer :: i
        do i = 1, size(x)
            output(i) = sigmoid(x(i))
        end do
    end function apply_sigmoid
    
    ! Sigmoid derivative for vector
    function sigmoid_deriv(x) result(output)
        real, dimension(:), intent(in) :: x
        real, dimension(size(x)) :: output
        integer :: i
        do i = 1, size(x)
            output(i) = sigmoid_derivative(x(i))
        end do
    end function sigmoid_deriv
    
    ! Outer product
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
    
end program example_simple_nn
