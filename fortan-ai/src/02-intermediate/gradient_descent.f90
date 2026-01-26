! Gradient Descent Explained - How AI Learns
! This program demonstrates gradient descent optimization
program gradient_descent_explained
    implicit none
    
    ! Declare all variables at the beginning
    real :: x, f_x, gradient
    real, parameter :: learning_rate = 0.1
    integer :: iteration
    real :: w1, w2, grad_w1, grad_w2, loss_2d
    integer :: iter
    
    print *, "========================================================="
    print *, "   GRADIENT DESCENT: The Foundation of AI Learning"
    print *, "========================================================="
    print *
    print *, "PROBLEM: Find the minimum of f(x) = (x - 3)² + 2"
    print *
    print *, "CONCEPT: Gradient descent is like walking downhill"
    print *, "- Start at a random point"
    print *, "- Calculate the slope (gradient)"
    print *, "- Take a step in the downhill direction"
    print *, "- Repeat until you reach the bottom (minimum)"
    print *
    print *, "In neural networks, we minimize the error (loss) instead"
    print *, "of a simple function, but the principle is the same!"
    print *
    print *, "========================================================="
    print *
    
    ! Start at a random point
    x = 0.0
    
    print *, "STARTING GRADIENT DESCENT"
    print *, "-------------------------"
    print '(A,F6.2)', "Initial position: x = ", x
    print '(A,F6.2)', "Learning rate: ", learning_rate
    print *
    
    do iteration = 1, 20
        ! Calculate function value
        f_x = (x - 3.0)**2 + 2.0
        
        ! Calculate gradient (derivative): df/dx = 2(x - 3)
        gradient = 2.0 * (x - 3.0)
        
        ! Print current state
        if (mod(iteration, 2) == 0 .or. iteration <= 5 .or. iteration > 18) then
            print '(A,I2)', "Iteration ", iteration
            print '(A,F8.4,A,F8.4)', "  x = ", x, ",  f(x) = ", f_x
            print '(A,F8.4)', "  Gradient (slope) = ", gradient
            
            if (gradient > 0) then
                print *, "  → Slope is positive, move LEFT (decrease x)"
            else if (gradient < 0) then
                print *, "  → Slope is negative, move RIGHT (increase x)"
            else
                print *, "  → At minimum! Gradient = 0"
            end if
            
            print '(A,F8.4)', "  Step size: ", -learning_rate * gradient
            print *
        end if
        
        ! Update x using gradient descent
        x = x - learning_rate * gradient
        
        ! Check convergence
        if (abs(gradient) < 0.01) then
            print *, "CONVERGED! Gradient is very small."
            exit
        end if
    end do
    
    print *
    print *, "========================================================="
    print *, "   RESULT"
    print *, "========================================================="
    print '(A,F8.4)', "Final x = ", x
    print '(A,F8.4)', "Final f(x) = ", f_x
    print *, "Optimal x = 3.0000"
    print *, "Optimal f(x) = 2.0000"
    print *
    
    print *, "========================================================="
    print *, "   HOW THIS APPLIES TO NEURAL NETWORKS"
    print *, "========================================================="
    print *
    print *, "In neural networks:"
    print *, "- x represents ALL the weights in the network"
    print *, "- f(x) is the LOSS (prediction error)"
    print *, "- Gradient tells us how to adjust each weight"
    print *, "- We want to minimize loss (make better predictions)"
    print *
    print *, "The same process happens in backpropagation:"
    print *, "1. Calculate loss (how wrong we are)"
    print *, "2. Calculate gradients (how to improve)"
    print *, "3. Update weights (take a step toward better predictions)"
    print *, "4. Repeat thousands of times"
    print *
    print *, "Key insights:"
    print *, "- Learning rate too large: we might overshoot"
    print *, "- Learning rate too small: learning is very slow"
    print *, "- Multiple dimensions: same idea, just more complex"
    print *
    print *, "This is the CORE of how AI learns!"
    print *, "========================================================="
    print *
    
    ! Now demonstrate with 2D example
    print *, "========================================================="
    print *, "   2D EXAMPLE: Multiple Parameters"
    print *, "========================================================="
    print *
    print *, "In real neural networks, we optimize many weights at once."
    print *, "Example: f(w1, w2) = w1² + w2²  (minimum at w1=0, w2=0)"
    print *
    
    ! Demonstrate 2D gradient descent
    w1 = 5.0
    w2 = -3.0
    
    print *, "Starting point: w1 =", w1, ", w2 =", w2
    print *
    
    do iter = 1, 10
        ! Calculate loss and gradients
        loss_2d = w1**2 + w2**2
        grad_w1 = 2.0 * w1
        grad_w2 = 2.0 * w2
        
        if (mod(iter, 2) == 1 .or. iter > 8) then
            print '(A,I2,A,F7.3,A,F7.3,A,F8.3)', "Iter ", iter, ": w1=", w1, &
                ", w2=", w2, ", loss=", loss_2d
        end if
        
        ! Update both weights simultaneously
        w1 = w1 - learning_rate * grad_w1
        w2 = w2 - learning_rate * grad_w2
    end do
    
    print *
    print *, "Final: w1 =", w1, ", w2 =", w2, ", loss =", w1**2 + w2**2
    print *, "Both weights converged to near zero!"
    print *
    print *, "========================================================="
    print *, "This is gradient descent with multiple parameters,"
    print *, "exactly what happens in neural network training!"
    print *, "========================================================="
    print *
    
end program gradient_descent_explained
