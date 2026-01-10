! Logistic Regression - Binary classification with sigmoid activation
program logistic_regression
    implicit none
    
    ! Parameters
    integer, parameter :: n_samples = 6
    integer, parameter :: n_features = 2
    integer, parameter :: epochs = 1000
    real, parameter :: learning_rate = 0.1
    
    ! Variables
    real, dimension(n_samples, n_features) :: X
    real, dimension(n_samples) :: y
    real, dimension(n_features) :: weights
    real :: bias
    integer :: i
    
    print *, "=========================================="
    print *, "   Logistic Regression Classifier"
    print *, "=========================================="
    print *
    
    ! Training data - Simple binary classification
    ! Class 0: Points in lower-left region
    ! Class 1: Points in upper-right region
    X = reshape([1.0, 2.0, &
                 2.0, 3.0, &
                 3.0, 4.0, &
                 5.0, 6.0, &
                 6.0, 7.0, &
                 7.0, 8.0], [n_samples, n_features])
    y = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    
    print *, "Training Data:"
    print *, "  x1   x2  | Class"
    print *, "  ----------|------"
    do i = 1, n_samples
        print '(2X,F4.1,1X,F4.1,A,F5.0)', X(i,1), X(i,2), "  |", y(i)
    end do
    print *
    
    ! Initialize parameters
    call random_number(weights)
    weights = (weights - 0.5) * 0.1
    bias = 0.0
    
    ! Train the model
    call train_logistic_regression(X, y, weights, bias, epochs, learning_rate)
    
    ! Display learned parameters
    print *, "Learned Parameters:"
    print *, "  w1 =", weights(1)
    print *, "  w2 =", weights(2)
    print *, "  b  =", bias
    print *
    
    ! Make predictions
    call evaluate_model(X, y, weights, bias)
    
    ! Test on new data
    print *, "Predictions on new data:"
    call predict_sample([1.5, 2.5], weights, bias)
    call predict_sample([4.0, 5.0], weights, bias)
    call predict_sample([6.5, 7.5], weights, bias)
    print *
    
contains
    
    real function sigmoid(z)
        real, intent(in) :: z
        sigmoid = 1.0 / (1.0 + exp(-z))
    end function sigmoid
    
    subroutine train_logistic_regression(X, y, weights, bias, epochs, lr)
        real, dimension(:,:), intent(in) :: X
        real, dimension(:), intent(in) :: y
        real, dimension(:), intent(inout) :: weights
        real, intent(inout) :: bias
        integer, intent(in) :: epochs
        real, intent(in) :: lr
        
        integer :: epoch, i, n
        real :: z, prediction, error, loss
        real, dimension(size(weights)) :: grad_w
        real :: grad_b
        
        n = size(y)
        
        print *, "Training..."
        
        do epoch = 1, epochs
            ! Initialize gradients
            grad_w = 0.0
            grad_b = 0.0
            loss = 0.0
            
            ! Loop through all samples
            do i = 1, n
                ! Forward pass
                z = dot_product(weights, X(i,:)) + bias
                prediction = sigmoid(z)
                
                ! Calculate error and loss
                error = prediction - y(i)
                loss = loss - (y(i) * log(prediction + 1.0e-8) + &
                              (1.0 - y(i)) * log(1.0 - prediction + 1.0e-8))
                
                ! Accumulate gradients
                grad_w = grad_w + error * X(i,:)
                grad_b = grad_b + error
            end do
            
            ! Average gradients
            grad_w = grad_w / n
            grad_b = grad_b / n
            loss = loss / n
            
            ! Update parameters (gradient descent)
            weights = weights - lr * grad_w
            bias = bias - lr * grad_b
            
            ! Display progress
            if (mod(epoch, 100) == 0 .or. epoch == 1) then
                print '(A,I5,A,F10.6)', "  Epoch ", epoch, " - Loss: ", loss
            end if
        end do
        
        print *, "Training complete!"
        print *
    end subroutine train_logistic_regression
    
    subroutine evaluate_model(X, y, weights, bias)
        real, dimension(:,:), intent(in) :: X
        real, dimension(:), intent(in) :: y
        real, dimension(:), intent(in) :: weights
        real, intent(in) :: bias
        
        integer :: i, correct
        real :: z, prob, prediction
        
        print *, "Evaluation on Training Data:"
        print *, "  x1   x2  | True | Prob  | Pred | Correct?"
        print *, "  ----------|------|-------|------|----------"
        
        correct = 0
        do i = 1, size(y)
            z = dot_product(weights, X(i,:)) + bias
            prob = sigmoid(z)
            
            if (prob >= 0.5) then
                prediction = 1.0
            else
                prediction = 0.0
            end if
            
            if (prediction == y(i)) correct = correct + 1
            
            print '(2X,F4.1,1X,F4.1,A,F5.0,A,F6.3,A,F5.0,A,L1)', &
                X(i,1), X(i,2), "  |", y(i), " |", prob, " |", &
                prediction, "  |", prediction == y(i)
        end do
        
        print *
        print *, "Accuracy:", real(correct) / size(y) * 100.0, "%"
        print *
    end subroutine evaluate_model
    
    subroutine predict_sample(x, weights, bias)
        real, dimension(:), intent(in) :: x
        real, dimension(:), intent(in) :: weights
        real, intent(in) :: bias
        
        real :: z, prob
        
        z = dot_product(weights, x) + bias
        prob = sigmoid(z)
        
        print '(A,F4.1,A,F4.1,A,F6.3,A,I1)', &
            "  x=[", x(1), ",", x(2), "] → Probability: ", prob, &
            " → Class: ", merge(1, 0, prob >= 0.5)
    end subroutine predict_sample
    
end program logistic_regression
