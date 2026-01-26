! AI Learning Fundamentals - Understanding How AI Learns from Data
! This program explains the core concepts of machine learning
program ai_learning_fundamentals
    implicit none
    
    ! Declare all variables at the beginning
    integer :: number, i
    real :: weight, input_val, target, prediction, error, gradient
    real, parameter :: lr = 0.1
    
    print *, "========================================================="
    print *, "   AI LEARNING FUNDAMENTALS"
    print *, "   Understanding How Machines Learn from Information"
    print *, "========================================================="
    print *
    
    ! === PART 1: What is Learning? ===
    print *, "========================================================="
    print *, "PART 1: WHAT IS LEARNING?"
    print *, "========================================================="
    print *
    print *, "Human Learning:"
    print *, "- See examples (data)"
    print *, "- Find patterns"
    print *, "- Make predictions on new situations"
    print *
    print *, "Machine Learning (AI):"
    print *, "- Same process, but using mathematics!"
    print *, "- Data → Pattern Discovery → Predictions"
    print *
    
    ! Simple example: Learning to recognize even/odd numbers
    print *, "EXAMPLE 1: Learning Even vs Odd Numbers"
    print *, "---------------------------------------"
    print *, "Training data (examples with labels):"
    print *, "  2 → even"
    print *, "  3 → odd"
    print *, "  4 → even"
    print *, "  5 → odd"
    print *
    print *, "Pattern discovered: If (number mod 2 = 0) then even"
    print *
    print *, "Testing on new data:"
    do number = 6, 9
        if (mod(number, 2) == 0) then
            print '(A,I2,A)', "  ", number, " → PREDICTED: even ✓"
        else
            print '(A,I2,A)', "  ", number, " → PREDICTED: odd ✓"
        end if
    end do
    print *
    print *, "This is LEARNING: Generalize from examples to new cases!"
    print *
    
    ! === PART 2: Types of Learning ===
    print *, "========================================================="
    print *, "PART 2: TYPES OF MACHINE LEARNING"
    print *, "========================================================="
    print *
    print *, "1. SUPERVISED LEARNING (Learning with a Teacher)"
    print *, "   - Given: Input + Correct Output"
    print *, "   - Learn: Function that maps input → output"
    print *, "   - Examples: Classification, Regression"
    print *
    print *, "2. UNSUPERVISED LEARNING (Learning Patterns Alone)"
    print *, "   - Given: Only inputs (no labels)"
    print *, "   - Learn: Hidden patterns, groupings"
    print *, "   - Examples: Clustering"
    print *
    print *, "3. REINFORCEMENT LEARNING (Learning from Experience)"
    print *, "   - Given: Actions and rewards"
    print *, "   - Learn: Best actions to maximize reward"
    print *, "   - Examples: Game playing, Robotics"
    print *
    
    ! === PART 3: How Neural Networks Learn ===
    print *, "========================================================="
    print *, "PART 3: HOW NEURAL NETWORKS LEARN FROM DATA"
    print *, "========================================================="
    print *
    print *, "A neural network is a function with adjustable parameters:"
    print *, "  Output = f(Input, Weights)"
    print *
    print *, "Learning Process (Training Loop):"
    print *, "1. Initialize: Start with random weights"
    print *, "2. Forward Pass: Make a prediction"
    print *, "3. Calculate Loss: How wrong is the prediction?"
    print *, "4. Backward Pass: Calculate gradients"
    print *, "5. Update Weights: Adjust to reduce error"
    print *, "6. Repeat steps 2-5 many times (epochs)"
    print *
    
    ! Demonstrate simple learning
    print *, "SIMPLE LEARNING EXAMPLE"
    print *, "Task: Learn w such that w × 2 = 10"
    print *, "Answer: w should be 5"
    print *
    
    weight = 1.0
    input_val = 2.0
    target = 10.0
    
    print *, "Training..."
    do i = 1, 10
        prediction = weight * input_val
        error = prediction - target
        gradient = 2.0 * error * input_val
        weight = weight - lr * gradient
        
        if (i <= 3 .or. i > 7) then
            print '(A,I2,A,F6.3,A,F7.3)', "Epoch ", i, ": w=", weight, &
                ", pred=", prediction
        end if
    end do
    
    print *
    print '(A,F6.3)', "Final weight: ", weight
    print *, "Learned that w ≈ 5 to satisfy 2w = 10"
    print *
    
    print *, "========================================================="
    print *, "   SUMMARY: THE ESSENCE OF AI LEARNING"
    print *, "========================================================="
    print *
    print *, "✓ AI learns by finding patterns in data"
    print *, "✓ Learning = Adjusting parameters to minimize errors"
    print *, "✓ Neural networks process information in layers"
    print *, "✓ Backpropagation calculates how to improve"
    print *, "✓ Gradient descent makes incremental improvements"
    print *, "✓ Goal: Generalize to new, unseen situations"
    print *
    print *, "This is the foundation of modern AI!"
    print *, "========================================================="
    print *
    
end program ai_learning_fundamentals
