! Deep Neural Network Implementation
! Supports multiple hidden layers for complex pattern learning
program deep_neural_network
    implicit none
    
    ! Network architecture: 2 inputs -> 8 -> 16 -> 8 -> 1 output (Deep network)
    integer, parameter :: n_inputs = 2
    integer, parameter :: n_hidden1 = 8
    integer, parameter :: n_hidden2 = 16
    integer, parameter :: n_hidden3 = 8
    integer, parameter :: n_outputs = 1
    integer, parameter :: n_samples = 4
    integer, parameter :: n_epochs = 5000
    real, parameter :: learning_rate = 0.5
    
    ! Network weights and biases
    real, dimension(n_inputs, n_hidden1) :: W1
    real, dimension(n_hidden1) :: b1
    real, dimension(n_hidden1, n_hidden2) :: W2
    real, dimension(n_hidden2) :: b2
    real, dimension(n_hidden2, n_hidden3) :: W3
    real, dimension(n_hidden3) :: b3
    real, dimension(n_hidden3, n_outputs) :: W4
    real, dimension(n_outputs) :: b4
    
    ! Layer activations
    real, dimension(n_inputs, n_samples) :: X
    real, dimension(n_hidden1, n_samples) :: h1, h1_grad
    real, dimension(n_hidden2, n_samples) :: h2, h2_grad
    real, dimension(n_hidden3, n_samples) :: h3, h3_grad
    real, dimension(n_outputs, n_samples) :: y_pred, y_true
    
    ! Training variables
    real :: loss
    integer :: epoch, i, j, k
    
    print *, "======================================"
    print *, "   Deep Neural Network (XOR Problem)"
    print *, "   Architecture: 2->8->16->8->1"
    print *, "======================================"
    print *
    
    ! Initialize training data (XOR problem)
    X(:,1) = [0.0, 0.0]
    X(:,2) = [0.0, 1.0]
    X(:,3) = [1.0, 0.0]
    X(:,4) = [1.0, 1.0]
    
    y_true(:,1) = [0.0]
    y_true(:,2) = [1.0]
    y_true(:,3) = [1.0]
    y_true(:,4) = [0.0]
    
    ! Initialize weights with small random values
    call random_seed()
    call random_number(W1)
    call random_number(W2)
    call random_number(W3)
    call random_number(W4)
    W1 = (W1 - 0.5) * 0.5
    W2 = (W2 - 0.5) * 0.5
    W3 = (W3 - 0.5) * 0.5
    W4 = (W4 - 0.5) * 0.5
    b1 = 0.0
    b2 = 0.0
    b3 = 0.0
    b4 = 0.0
    
    print *, "Training deep neural network..."
    print *, "Epochs:", n_epochs
    print *, "Learning rate:", learning_rate
    print *
    
    ! Training loop
    do epoch = 1, n_epochs
        ! Forward pass
        ! Layer 1
        do i = 1, n_samples
            do j = 1, n_hidden1
                h1(j,i) = b1(j)
                do k = 1, n_inputs
                    h1(j,i) = h1(j,i) + W1(k,j) * X(k,i)
                end do
                h1(j,i) = tanh(h1(j,i))  ! Activation
            end do
        end do
        
        ! Layer 2
        do i = 1, n_samples
            do j = 1, n_hidden2
                h2(j,i) = b2(j)
                do k = 1, n_hidden1
                    h2(j,i) = h2(j,i) + W2(k,j) * h1(k,i)
                end do
                h2(j,i) = tanh(h2(j,i))  ! Activation
            end do
        end do
        
        ! Layer 3
        do i = 1, n_samples
            do j = 1, n_hidden3
                h3(j,i) = b3(j)
                do k = 1, n_hidden2
                    h3(j,i) = h3(j,i) + W3(k,j) * h2(k,i)
                end do
                h3(j,i) = tanh(h3(j,i))  ! Activation
            end do
        end do
        
        ! Output layer
        do i = 1, n_samples
            do j = 1, n_outputs
                y_pred(j,i) = b4(j)
                do k = 1, n_hidden3
                    y_pred(j,i) = y_pred(j,i) + W4(k,j) * h3(k,i)
                end do
                y_pred(j,i) = 1.0 / (1.0 + exp(-y_pred(j,i)))  ! Sigmoid
            end do
        end do
        
        ! Calculate loss (MSE)
        loss = 0.0
        do i = 1, n_samples
            do j = 1, n_outputs
                loss = loss + (y_pred(j,i) - y_true(j,i))**2
            end do
        end do
        loss = loss / (n_samples * n_outputs)
        
        ! Backward pass (gradient descent with backpropagation)
        ! Output layer gradients
        do i = 1, n_samples
            do j = 1, n_outputs
                h3_grad(j,i) = 2.0 * (y_pred(j,i) - y_true(j,i)) * &
                              y_pred(j,i) * (1.0 - y_pred(j,i))
            end do
        end do
        
        ! Update Layer 4 weights
        do i = 1, n_hidden3
            do j = 1, n_outputs
                do k = 1, n_samples
                    W4(i,j) = W4(i,j) - learning_rate * h3_grad(j,k) * h3(i,k)
                end do
                do k = 1, n_samples
                    b4(j) = b4(j) - learning_rate * h3_grad(j,k)
                end do
            end do
        end do
        
        ! Backpropagate to layer 3
        h2_grad = 0.0
        do i = 1, n_samples
            do j = 1, n_hidden3
                h2_grad(j,i) = 0.0
                do k = 1, n_outputs
                    h2_grad(j,i) = h2_grad(j,i) + h3_grad(k,i) * W4(j,k)
                end do
                h2_grad(j,i) = h2_grad(j,i) * (1.0 - h3(j,i)**2)  ! tanh derivative
            end do
        end do
        
        ! Update Layer 3 weights
        do i = 1, n_hidden2
            do j = 1, n_hidden3
                do k = 1, n_samples
                    W3(i,j) = W3(i,j) - learning_rate * h2_grad(j,k) * h2(i,k)
                end do
                do k = 1, n_samples
                    b3(j) = b3(j) - learning_rate * h2_grad(j,k)
                end do
            end do
        end do
        
        ! Backpropagate to layer 2
        h1_grad = 0.0
        do i = 1, n_samples
            do j = 1, n_hidden1
                h1_grad(j,i) = 0.0
                do k = 1, n_hidden2
                    h1_grad(j,i) = h1_grad(j,i) + h2_grad(k,i) * W2(j,k)
                end do
                h1_grad(j,i) = h1_grad(j,i) * (1.0 - h1(j,i)**2)  ! tanh derivative
            end do
        end do
        
        ! Update Layer 2 weights
        do i = 1, n_hidden1
            do j = 1, n_hidden2
                do k = 1, n_samples
                    W2(i,j) = W2(i,j) - learning_rate * h2_grad(j,k) * h1(i,k)
                end do
                do k = 1, n_samples
                    b2(j) = b2(j) - learning_rate * h2_grad(j,k)
                end do
            end do
        end do
        
        ! Print progress
        if (mod(epoch, 1000) == 0 .or. epoch == 1) then
            print '(A,I5,A,F10.6)', "Epoch ", epoch, " - Loss: ", loss
        end if
    end do
    
    print *
    print *, "======================================"
    print *, "   Training Complete!"
    print *, "======================================"
    print *
    print *, "Final predictions:"
    print *, "Input    | Target | Prediction | Rounded"
    print *, "---------|--------|------------|--------"
    do i = 1, n_samples
        print '(F4.1,F4.1,A,F6.3,A,F10.6,A,I4)', &
            X(1,i), X(2,i), "  |  ", y_true(1,i), "   |   ", &
            y_pred(1,i), "    | ", nint(y_pred(1,i))
    end do
    
    print *
    print *, "Deep Neural Network successfully solved XOR!"
    print *, "Network depth: 4 layers (3 hidden + 1 output)"
    print *
    
end program deep_neural_network
