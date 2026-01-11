! Perceptron - Single neuron binary classifier
! The building block of neural networks
module perceptron_module
    implicit none
    
    type :: Perceptron
        integer :: n_features
        real, allocatable :: weights(:)
        real :: bias
        real :: learning_rate
    contains
        procedure :: init => perceptron_init
        procedure :: predict => perceptron_predict
        procedure :: train => perceptron_train
        procedure :: display => perceptron_display
    end type Perceptron
    
contains
    
    subroutine perceptron_init(self, n_features, learning_rate)
        class(Perceptron), intent(inout) :: self
        integer, intent(in) :: n_features
        real, intent(in) :: learning_rate
        
        self%n_features = n_features
        self%learning_rate = learning_rate
        
        allocate(self%weights(n_features))
        
        ! Initialize with small random weights
        call random_number(self%weights)
        self%weights = (self%weights - 0.5) * 0.1
        self%bias = 0.0
    end subroutine perceptron_init
    
    real function perceptron_predict(self, inputs)
        class(Perceptron), intent(in) :: self
        real, dimension(:), intent(in) :: inputs
        real :: activation
        
        ! Compute weighted sum
        activation = dot_product(self%weights, inputs) + self%bias
        
        ! Apply step function (activation function)
        if (activation >= 0.0) then
            perceptron_predict = 1.0
        else
            perceptron_predict = 0.0
        end if
    end function perceptron_predict
    
    subroutine perceptron_train(self, X, y, epochs)
        class(Perceptron), intent(inout) :: self
        real, dimension(:,:), intent(in) :: X
        real, dimension(:), intent(in) :: y
        integer, intent(in) :: epochs
        integer :: epoch, i, n_samples
        real :: prediction, error
        
        n_samples = size(y)
        
        print *, "Training perceptron..."
        
        do epoch = 1, epochs
            do i = 1, n_samples
                ! Make prediction
                prediction = self%predict(X(i,:))
                
                ! Calculate error
                error = y(i) - prediction
                
                ! Update weights: w = w + learning_rate * error * x
                self%weights = self%weights + &
                    self%learning_rate * error * X(i,:)
                
                ! Update bias: b = b + learning_rate * error
                self%bias = self%bias + self%learning_rate * error
            end do
            
            if (mod(epoch, 10) == 0 .or. epoch == 1) then
                print '(A,I4)', "  Epoch ", epoch
            end if
        end do
        
        print *, "Training complete!"
        print *
    end subroutine perceptron_train
    
    subroutine perceptron_display(self)
        class(Perceptron), intent(in) :: self
        integer :: i
        
        print *, "Perceptron Parameters:"
        print *, "  Weights:"
        do i = 1, self%n_features
            print '(A,I1,A,F8.4)', "    w", i, " = ", self%weights(i)
        end do
        print *, "  Bias:", self%bias
        print *
    end subroutine perceptron_display
    
end module perceptron_module

program test_perceptron
    use perceptron_module
    implicit none
    
    type(Perceptron) :: neuron
    real, dimension(4,2) :: X_train
    real, dimension(4) :: y_train
    integer :: i
    real :: prediction
    
    print *, "=========================================="
    print *, "   Perceptron Binary Classifier"
    print *, "=========================================="
    print *
    
    ! AND gate training data
    print *, "Learning the AND logic gate:"
    print *, "  0 AND 0 = 0"
    print *, "  0 AND 1 = 0"
    print *, "  1 AND 0 = 0"
    print *, "  1 AND 1 = 1"
    print *
    
    X_train = reshape([0.0, 0.0, &
                       0.0, 1.0, &
                       1.0, 0.0, &
                       1.0, 1.0], [4, 2])
    y_train = [0.0, 0.0, 0.0, 1.0]
    
    ! Initialize perceptron
    call neuron%init(n_features=2, learning_rate=0.1)
    
    print *, "Initial (random) weights:"
    call neuron%display()
    
    ! Train the perceptron
    call neuron%train(X_train, y_train, epochs=100)
    
    print *, "Learned weights:"
    call neuron%display()
    
    ! Test the trained perceptron
    print *, "Testing the learned AND gate:"
    print *, "  Input  | Expected | Predicted"
    print *, "  -------|----------|----------"
    do i = 1, 4
        prediction = neuron%predict(X_train(i,:))
        print '(2X,F3.0,1X,F3.0,A,F8.0,A,F10.0)', &
            X_train(i,1), X_train(i,2), "  |", y_train(i), "     |", prediction
    end do
    print *
    
    print *, "=========================================="
    print *, "   Key Concepts Demonstrated:"
    print *, "=========================================="
    print *, "1. Weights: Adjusted during training"
    print *, "2. Bias: Shifts the decision boundary"
    print *, "3. Activation: Step function for binary output"
    print *, "4. Learning: Perceptron learning rule"
    print *, "5. Linearly Separable: AND gate can be solved"
    print *
    print *, "Note: XOR gate cannot be solved by a single"
    print *, "perceptron (not linearly separable)!"
    print *
    
end program test_perceptron
