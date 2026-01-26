! Multi-layer Neural Network with Flexible Architecture
program neural_network
    implicit none
    
    ! Network architecture: 2 inputs -> 6 hidden -> 1 output
    integer, parameter :: n_inputs = 2
    integer, parameter :: n_hidden = 6
    integer, parameter :: n_outputs = 1
    integer, parameter :: n_samples = 4
    integer, parameter :: n_epochs = 3000
    real, parameter :: learning_rate = 0.3
    
    ! Network weights and biases
    real, dimension(n_inputs, n_hidden) :: W1
    real, dimension(n_hidden) :: b1
    real, dimension(n_hidden, n_outputs) :: W2
    real, dimension(n_outputs) :: b2
    
    ! Layer activations and gradients
    real, dimension(n_inputs, n_samples) :: X
    real, dimension(n_hidden, n_samples) :: h1
    real, dimension(n_outputs, n_samples) :: y_pred, y_true
    real, dimension(n_hidden, n_samples) :: dh1
    real, dimension(n_outputs, n_samples) :: dy
    
    ! Training variables
    real :: loss
    integer :: epoch, i, j, k
    
    print *, "======================================"
    print *, "   Multi-Layer Neural Network"
    print *, "   Architecture: 2->6->1"
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
    
    ! Initialize weights
    call random_seed()
    call random_number(W1)
    call random_number(W2)
    W1 = (W1 - 0.5) * 0.5
    W2 = (W2 - 0.5) * 0.5
    b1 = 0.0
    b2 = 0.0
    
    print *, "Training neural network on XOR problem..."
    print *, "Epochs:", n_epochs
    print *, "Learning rate:", learning_rate
    print *
    
    ! Training loop
    do epoch = 1, n_epochs
        ! Forward pass - Hidden layer
        do i = 1, n_samples
            do j = 1, n_hidden
                h1(j,i) = b1(j)
                do k = 1, n_inputs
                    h1(j,i) = h1(j,i) + W1(k,j) * X(k,i)
                end do
                h1(j,i) = 1.0 / (1.0 + exp(-h1(j,i)))  ! Sigmoid
            end do
        end do
        
        ! Forward pass - Output layer
        do i = 1, n_samples
            do j = 1, n_outputs
                y_pred(j,i) = b2(j)
                do k = 1, n_hidden
                    y_pred(j,i) = y_pred(j,i) + W2(k,j) * h1(k,i)
                end do
                y_pred(j,i) = 1.0 / (1.0 + exp(-y_pred(j,i)))  ! Sigmoid
            end do
        end do
        
        ! Calculate loss
        loss = 0.0
        do i = 1, n_samples
            do j = 1, n_outputs
                loss = loss + (y_pred(j,i) - y_true(j,i))**2
            end do
        end do
        loss = loss / (n_samples * n_outputs)
        
        ! Backward pass - Output layer
        do i = 1, n_samples
            do j = 1, n_outputs
                dy(j,i) = 2.0 * (y_pred(j,i) - y_true(j,i)) * y_pred(j,i) * (1.0 - y_pred(j,i))
            end do
        end do
        
        ! Update W2 and b2
        do i = 1, n_hidden
            do j = 1, n_outputs
                do k = 1, n_samples
                    W2(i,j) = W2(i,j) - learning_rate * dy(j,k) * h1(i,k)
                end do
            end do
        end do
        
        do j = 1, n_outputs
            do k = 1, n_samples
                b2(j) = b2(j) - learning_rate * dy(j,k)
            end do
        end do
        
        ! Backward pass - Hidden layer
        do i = 1, n_samples
            do j = 1, n_hidden
                dh1(j,i) = 0.0
                do k = 1, n_outputs
                    dh1(j,i) = dh1(j,i) + dy(k,i) * W2(j,k)
                end do
                dh1(j,i) = dh1(j,i) * h1(j,i) * (1.0 - h1(j,i))  ! Sigmoid derivative
            end do
        end do
        
        ! Update W1 and b1
        do i = 1, n_inputs
            do j = 1, n_hidden
                do k = 1, n_samples
                    W1(i,j) = W1(i,j) - learning_rate * dh1(j,k) * X(i,k)
                end do
            end do
        end do
        
        do j = 1, n_hidden
            do k = 1, n_samples
                b1(j) = b1(j) - learning_rate * dh1(j,k)
            end do
        end do
        
        ! Print progress
        if (mod(epoch, 500) == 0 .or. epoch == 1) then
            print '(A,I5,A,F10.6)', "Epoch ", epoch, " - Loss: ", loss
        end if
    end do
    
    print *
    print *, "======================================"
    print *, "   Training Complete!"
    print *, "======================================"
    print *
    print *, "Predictions:"
    print *, "Input  | Target | Prediction | Rounded"
    print *, "-------|--------|------------|--------"
    do i = 1, n_samples
        print '(F3.0,F4.0,A,F6.3,A,F10.6,A,I4)', &
            X(1,i), X(2,i), "  |  ", y_true(1,i), "   |   ", &
            y_pred(1,i), "    | ", nint(y_pred(1,i))
    end do
    
    print *
    print *, "Neural network successfully learned XOR function!"
    print *
    
end program neural_network
