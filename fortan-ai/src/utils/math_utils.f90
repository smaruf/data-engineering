! Mathematical Utilities Module
! Common math functions for AI/ML
module math_utils
    implicit none
    private
    public :: sigmoid, sigmoid_derivative, relu, relu_derivative, &
              tanh_activation, tanh_derivative, softmax, &
              mean, variance, normalize
    
contains
    
    ! Sigmoid activation function
    real function sigmoid(x)
        real, intent(in) :: x
        sigmoid = 1.0 / (1.0 + exp(-x))
    end function sigmoid
    
    ! Sigmoid derivative
    real function sigmoid_derivative(x)
        real, intent(in) :: x
        real :: s
        s = sigmoid(x)
        sigmoid_derivative = s * (1.0 - s)
    end function sigmoid_derivative
    
    ! ReLU activation function
    real function relu(x)
        real, intent(in) :: x
        relu = max(0.0, x)
    end function relu
    
    ! ReLU derivative
    real function relu_derivative(x)
        real, intent(in) :: x
        if (x > 0.0) then
            relu_derivative = 1.0
        else
            relu_derivative = 0.0
        end if
    end function relu_derivative
    
    ! Tanh activation function
    real function tanh_activation(x)
        real, intent(in) :: x
        tanh_activation = tanh(x)
    end function tanh_activation
    
    ! Tanh derivative
    real function tanh_derivative(x)
        real, intent(in) :: x
        real :: t
        t = tanh(x)
        tanh_derivative = 1.0 - t**2
    end function tanh_derivative
    
    ! Softmax for array
    function softmax(x) result(output)
        real, dimension(:), intent(in) :: x
        real, dimension(size(x)) :: output
        real :: max_x, sum_exp
        
        ! Numerical stability: subtract max
        max_x = maxval(x)
        output = exp(x - max_x)
        sum_exp = sum(output)
        output = output / sum_exp
    end function softmax
    
    ! Mean of array
    real function mean(x)
        real, dimension(:), intent(in) :: x
        mean = sum(x) / size(x)
    end function mean
    
    ! Variance of array
    real function variance(x)
        real, dimension(:), intent(in) :: x
        real :: m
        m = mean(x)
        variance = sum((x - m)**2) / size(x)
    end function variance
    
    ! Normalize array to [0, 1]
    function normalize(x) result(output)
        real, dimension(:), intent(in) :: x
        real, dimension(size(x)) :: output
        real :: min_x, max_x, range
        
        min_x = minval(x)
        max_x = maxval(x)
        range = max_x - min_x
        
        if (range > 0.0) then
            output = (x - min_x) / range
        else
            output = x
        end if
    end function normalize
    
end module math_utils
