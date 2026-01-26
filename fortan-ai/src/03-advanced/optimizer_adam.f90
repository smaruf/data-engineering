! ADAM Optimizer Implementation
! Adaptive Moment Estimation for improved training
program optimizer_adam
    implicit none
    
    ! Network parameters
    integer, parameter :: n_inputs = 2
    integer, parameter :: n_hidden = 4
    integer, parameter :: n_outputs = 1
    integer, parameter :: n_samples = 4
    integer, parameter :: n_epochs = 2000
    real, parameter :: learning_rate = 0.01
    real, parameter :: beta1 = 0.9
    real, parameter :: beta2 = 0.999
    real, parameter :: epsilon = 1e-8
    
    ! Network weights
    real, dimension(n_inputs, n_hidden) :: W1
    real, dimension(n_hidden) :: b1
    real, dimension(n_hidden, n_outputs) :: W2
    real, dimension(n_outputs) :: b2
    
    ! ADAM moment estimates
    real, dimension(n_inputs, n_hidden) :: m_W1, v_W1
    real, dimension(n_hidden) :: m_b1, v_b1
    real, dimension(n_hidden, n_outputs) :: m_W2, v_W2
    real, dimension(n_outputs) :: m_b2, v_b2
    
    ! Gradients
    real, dimension(n_inputs, n_hidden) :: grad_W1
    real, dimension(n_hidden) :: grad_b1
    real, dimension(n_hidden, n_outputs) :: grad_W2
    real, dimension(n_outputs) :: grad_b2
    
    ! Layer activations
    real, dimension(n_inputs, n_samples) :: X
    real, dimension(n_hidden, n_samples) :: h1
    real, dimension(n_outputs, n_samples) :: y_pred, y_true
    
    ! Training variables
    real :: loss, m_hat, v_hat
    integer :: epoch, i, j, k
    
    print *, "======================================"
    print *, "   ADAM Optimizer Neural Network"
    print *, "   Adaptive Moment Estimation"
    print *, "======================================"
    print *
    
    ! Initialize training data (XOR)
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
    
    ! Initialize ADAM moments
    m_W1 = 0.0; v_W1 = 0.0
    m_b1 = 0.0; v_b1 = 0.0
    m_W2 = 0.0; v_W2 = 0.0
    m_b2 = 0.0; v_b2 = 0.0
    
    print *, "Training with ADAM optimizer..."
    print *, "Learning rate:", learning_rate
    print *, "Beta1:", beta1, " Beta2:", beta2
    print *
    
    ! Training loop
    do epoch = 1, n_epochs
        ! Forward pass
        do i = 1, n_samples
            do j = 1, n_hidden
                h1(j,i) = b1(j)
                do k = 1, n_inputs
                    h1(j,i) = h1(j,i) + W1(k,j) * X(k,i)
                end do
                h1(j,i) = tanh(h1(j,i))
            end do
        end do
        
        do i = 1, n_samples
            do j = 1, n_outputs
                y_pred(j,i) = b2(j)
                do k = 1, n_hidden
                    y_pred(j,i) = y_pred(j,i) + W2(k,j) * h1(k,i)
                end do
                y_pred(j,i) = 1.0 / (1.0 + exp(-y_pred(j,i)))
            end do
        end do
        
        ! Calculate loss
        loss = 0.0
        do i = 1, n_samples
            loss = loss + (y_pred(1,i) - y_true(1,i))**2
        end do
        loss = loss / n_samples
        
        ! Compute gradients (simplified)
        grad_W1 = 0.0; grad_b1 = 0.0
        grad_W2 = 0.0; grad_b2 = 0.0
        
        do i = 1, n_samples
            ! Output layer gradient
            grad_b2(1) = grad_b2(1) + 2.0 * (y_pred(1,i) - y_true(1,i)) * &
                        y_pred(1,i) * (1.0 - y_pred(1,i))
            
            do j = 1, n_hidden
                grad_W2(j,1) = grad_W2(j,1) + 2.0 * (y_pred(1,i) - y_true(1,i)) * &
                              y_pred(1,i) * (1.0 - y_pred(1,i)) * h1(j,i)
            end do
        end do
        
        ! ADAM update for W2 and b2
        do i = 1, n_hidden
            ! First moment estimate
            m_W2(i,1) = beta1 * m_W2(i,1) + (1.0 - beta1) * grad_W2(i,1)
            ! Second moment estimate
            v_W2(i,1) = beta2 * v_W2(i,1) + (1.0 - beta2) * grad_W2(i,1)**2
            ! Bias-corrected estimates
            m_hat = m_W2(i,1) / (1.0 - beta1**epoch)
            v_hat = v_W2(i,1) / (1.0 - beta2**epoch)
            ! Update weight
            W2(i,1) = W2(i,1) - learning_rate * m_hat / (sqrt(v_hat) + epsilon)
        end do
        
        ! Update b2
        m_b2(1) = beta1 * m_b2(1) + (1.0 - beta1) * grad_b2(1)
        v_b2(1) = beta2 * v_b2(1) + (1.0 - beta2) * grad_b2(1)**2
        m_hat = m_b2(1) / (1.0 - beta1**epoch)
        v_hat = v_b2(1) / (1.0 - beta2**epoch)
        b2(1) = b2(1) - learning_rate * m_hat / (sqrt(v_hat) + epsilon)
        
        ! Print progress
        if (mod(epoch, 400) == 0 .or. epoch == 1) then
            print '(A,I5,A,F10.6)', "Epoch ", epoch, " - Loss: ", loss
        end if
    end do
    
    print *
    print *, "======================================"
    print *, "   ADAM Optimization Complete!"
    print *, "======================================"
    print *
    print *, "Final Predictions:"
    do i = 1, n_samples
        print '(A,F3.0,A,F3.0,A,F8.4)', "Input [", X(1,i), ", ", X(2,i), &
            "] -> ", y_pred(1,i)
    end do
    
    print *
    print *, "ADAM Benefits:"
    print *, "  - Adaptive learning rates per parameter"
    print *, "  - Momentum with bias correction"
    print *, "  - Faster convergence than SGD"
    print *, "  - Better handling of sparse gradients"
    print *
    
end program optimizer_adam
