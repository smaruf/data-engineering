! Backpropagation Explained - Step-by-Step Learning Process
! This program demonstrates how neural networks learn through backpropagation
program backpropagation_explained
    implicit none
    
    ! Simple 2-layer network: 2 inputs -> 2 hidden -> 1 output
    integer, parameter :: n_inputs = 2
    integer, parameter :: n_hidden = 2
    integer, parameter :: n_outputs = 1
    real, parameter :: learning_rate = 0.5
    
    ! Network parameters
    real, dimension(n_inputs, n_hidden) :: W1  ! Input to hidden weights
    real, dimension(n_hidden) :: b1            ! Hidden layer biases
    real, dimension(n_hidden, n_outputs) :: W2 ! Hidden to output weights
    real, dimension(n_outputs) :: b2           ! Output layer bias
    
    ! Forward pass values
    real, dimension(n_inputs) :: x             ! Input
    real, dimension(n_hidden) :: z1, a1        ! Hidden layer: pre-activation, activation
    real, dimension(n_outputs) :: z2, a2       ! Output layer: pre-activation, activation
    real :: y_true, loss
    
    ! Backward pass gradients
    real, dimension(n_outputs) :: dL_da2, dL_dz2
    real, dimension(n_hidden) :: dL_da1, dL_dz1
    
    integer :: epoch, i, j
    
    print *, "========================================================="
    print *, "   BACKPROPAGATION EXPLAINED: How Neural Networks Learn"
    print *, "========================================================="
    print *
    print *, "CONCEPT: Neural networks learn by adjusting weights to"
    print *, "minimize the difference between predictions and targets."
    print *
    print *, "The learning process has two phases:"
    print *, "1. FORWARD PASS: Input → Hidden → Output (Make prediction)"
    print *, "2. BACKWARD PASS: Compute gradients and update weights"
    print *
    print *, "========================================================="
    print *
    
    ! Initialize a simple example
    x = [1.0, 0.5]  ! Input features
    y_true = 1.0    ! Target output
    
    ! Initialize weights with known values for demonstration
    W1(1,1) = 0.2;  W1(1,2) = 0.3
    W1(2,1) = -0.1; W1(2,2) = 0.4
    b1 = [0.1, -0.2]
    
    W2(1,1) = 0.5
    W2(2,1) = -0.3
    b2 = [0.1]
    
    print *, "Initial Network State:"
    print *, "---------------------"
    print *, "Input: x =", x
    print *, "Target: y =", y_true
    print *, "Weights W1:"
    print *, "  [", W1(1,1), W1(1,2), "]"
    print *, "  [", W1(2,1), W1(2,2), "]"
    print *, "Weights W2:", W2(:,1)
    print *
    
    ! Training loop with detailed explanation
    do epoch = 1, 5
        print *, "========================================"
        print '(A,I1)', "EPOCH ", epoch
        print *, "========================================"
        print *
        
        ! === FORWARD PASS ===
        print *, "STEP 1: FORWARD PASS"
        print *, "--------------------"
        
        ! Hidden layer computation
        print *, "Hidden Layer:"
        do i = 1, n_hidden
            z1(i) = b1(i)
            do j = 1, n_inputs
                z1(i) = z1(i) + W1(j,i) * x(j)
            end do
            print '(A,I1,A,F8.4,A)', "  Neuron ", i, ": z1 = ", z1(i), " (weighted sum)"
            
            ! Sigmoid activation
            a1(i) = 1.0 / (1.0 + exp(-z1(i)))
            print '(A,I1,A,F8.4,A)', "  Neuron ", i, ": a1 = ", a1(i), " (after sigmoid)"
        end do
        print *
        
        ! Output layer computation
        print *, "Output Layer:"
        z2(1) = b2(1)
        do i = 1, n_hidden
            z2(1) = z2(1) + W2(i,1) * a1(i)
        end do
        print '(A,F8.4)', "  z2 (weighted sum) = ", z2(1)
        
        a2(1) = 1.0 / (1.0 + exp(-z2(1)))
        print '(A,F8.4)', "  a2 (prediction) = ", a2(1)
        print *
        
        ! Calculate loss
        loss = (a2(1) - y_true) ** 2
        print '(A,F8.4)', "Loss (prediction error) = ", loss
        print *
        
        ! === BACKWARD PASS ===
        print *, "STEP 2: BACKWARD PASS (Backpropagation)"
        print *, "---------------------------------------"
        print *, "Computing gradients to see how to adjust weights..."
        print *
        
        ! Output layer gradients
        dL_da2(1) = 2.0 * (a2(1) - y_true)
        print '(A,F8.4)', "  Gradient at output: dL/da2 = ", dL_da2(1)
        
        ! Chain rule: dL/dz2 = dL/da2 * da2/dz2
        dL_dz2(1) = dL_da2(1) * a2(1) * (1.0 - a2(1))
        print '(A,F8.4)', "  After sigmoid derivative: dL/dz2 = ", dL_dz2(1)
        print *
        
        ! Hidden layer gradients
        print *, "Propagating error back to hidden layer:"
        do i = 1, n_hidden
            dL_da1(i) = dL_dz2(1) * W2(i,1)
            dL_dz1(i) = dL_da1(i) * a1(i) * (1.0 - a1(i))
            print '(A,I1,A,F8.4)', "  Hidden neuron ", i, ": dL/dz1 = ", dL_dz1(i)
        end do
        print *
        
        ! === WEIGHT UPDATES ===
        print *, "STEP 3: UPDATE WEIGHTS (Learning Step)"
        print *, "---------------------------------------"
        print *, "Rule: new_weight = old_weight - learning_rate * gradient"
        print *
        
        ! Update W2 (hidden to output)
        print *, "Updating output layer weights (W2):"
        do i = 1, n_hidden
            print '(A,I1,A,F7.4,A,F7.4)', "  W2[", i, "]: ", W2(i,1), " → ", &
                W2(i,1) - learning_rate * dL_dz2(1) * a1(i)
            W2(i,1) = W2(i,1) - learning_rate * dL_dz2(1) * a1(i)
        end do
        b2(1) = b2(1) - learning_rate * dL_dz2(1)
        print *
        
        ! Update W1 (input to hidden)
        print *, "Updating hidden layer weights (W1):"
        do i = 1, n_inputs
            do j = 1, n_hidden
                W1(i,j) = W1(i,j) - learning_rate * dL_dz1(j) * x(i)
            end do
        end do
        do i = 1, n_hidden
            b1(i) = b1(i) - learning_rate * dL_dz1(i)
        end do
        print *, "  All W1 weights updated based on gradients"
        print *
        
        print *, "----------------------------------------"
        print '(A,F8.4)', "Prediction after update: ", a2(1)
        print '(A,F8.4)', "Target: ", y_true
        print '(A,F8.4)', "New loss: ", loss
        print *
        
    end do
    
    print *, "========================================================="
    print *, "   LEARNING COMPLETE!"
    print *, "========================================================="
    print *
    print *, "KEY CONCEPTS DEMONSTRATED:"
    print *, "-------------------------"
    print *, "1. FORWARD PASS:"
    print *, "   - Input flows through network layer by layer"
    print *, "   - Each neuron computes weighted sum + bias"
    print *, "   - Activation function (sigmoid) adds non-linearity"
    print *
    print *, "2. LOSS CALCULATION:"
    print *, "   - Measures how wrong the prediction is"
    print *, "   - Loss = (prediction - target)²"
    print *
    print *, "3. BACKPROPAGATION:"
    print *, "   - Calculates how each weight affects the loss"
    print *, "   - Uses chain rule to propagate error backwards"
    print *, "   - Gradient tells us which direction to adjust weights"
    print *
    print *, "4. WEIGHT UPDATE (Learning):"
    print *, "   - Adjust weights in opposite direction of gradient"
    print *, "   - Learning rate controls size of adjustments"
    print *, "   - Gradual improvement over multiple epochs"
    print *
    print *, "This is how AI learns from data!"
    print *, "========================================================="
    print *
    
end program backpropagation_explained
