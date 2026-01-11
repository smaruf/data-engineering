! Linear Regression - Implement simple linear regression from scratch
! Learns the relationship y = mx + b from data
program linear_regression
    implicit none
    
    ! Variables
    integer, parameter :: n_samples = 5
    real, dimension(n_samples) :: x, y
    real :: slope, intercept
    real :: mean_x, mean_y, numerator, denominator
    integer :: i
    
    print *, "=========================================="
    print *, "   Linear Regression from Scratch"
    print *, "=========================================="
    print *
    
    ! Training data: y = 2*x + 1 (with some noise)
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [3.1, 4.9, 7.2, 8.8, 11.1]
    
    print *, "Training Data:"
    do i = 1, n_samples
        print '(A,I1,A,F5.1,A,F5.1)', "  Sample ", i, ": x=", x(i), ", y=", y(i)
    end do
    print *
    
    ! Calculate means
    mean_x = sum(x) / n_samples
    mean_y = sum(y) / n_samples
    
    print *, "Statistics:"
    print *, "  Mean of x:", mean_x
    print *, "  Mean of y:", mean_y
    print *
    
    ! Calculate slope using least squares formula
    ! slope = Σ((x - mean_x) * (y - mean_y)) / Σ((x - mean_x)²)
    numerator = 0.0
    denominator = 0.0
    
    do i = 1, n_samples
        numerator = numerator + (x(i) - mean_x) * (y(i) - mean_y)
        denominator = denominator + (x(i) - mean_x)**2
    end do
    
    slope = numerator / denominator
    
    ! Calculate intercept
    ! intercept = mean_y - slope * mean_x
    intercept = mean_y - slope * mean_x
    
    print *, "Learned Parameters:"
    print *, "  Slope (m):", slope
    print *, "  Intercept (b):", intercept
    print *, "  Equation: y =", slope, "* x +", intercept
    print *
    
    ! Make predictions
    print *, "Predictions vs Actual:"
    print *, "  x    | Predicted | Actual | Error"
    print *, "  -----|-----------|--------|-------"
    do i = 1, n_samples
        print '(2X,F4.1,A,F9.2,A,F7.2,A,F6.2)', &
            x(i), " |", slope * x(i) + intercept, " |", y(i), " |", &
            abs(y(i) - (slope * x(i) + intercept))
    end do
    print *
    
    ! Calculate R-squared (goodness of fit)
    call calculate_r_squared(x, y, slope, intercept)
    
    ! Test on new data
    print *, "Testing on new data:"
    call predict_and_display(6.0, slope, intercept)
    call predict_and_display(7.0, slope, intercept)
    call predict_and_display(10.0, slope, intercept)
    print *
    
contains
    
    subroutine calculate_r_squared(x, y, slope, intercept)
        real, dimension(:), intent(in) :: x, y
        real, intent(in) :: slope, intercept
        real :: ss_tot, ss_res, r_squared, mean_y
        integer :: i
        
        mean_y = sum(y) / size(y)
        
        ss_tot = sum((y - mean_y)**2)
        ss_res = 0.0
        do i = 1, size(y)
            ss_res = ss_res + (y(i) - (slope * x(i) + intercept))**2
        end do
        
        r_squared = 1.0 - (ss_res / ss_tot)
        
        print *, "Model Performance:"
        print *, "  R² Score:", r_squared
        print *, "  (1.0 = perfect fit, 0.0 = no correlation)"
        print *
    end subroutine calculate_r_squared
    
    subroutine predict_and_display(x_new, slope, intercept)
        real, intent(in) :: x_new, slope, intercept
        real :: y_pred
        
        y_pred = slope * x_new + intercept
        print '(A,F5.1,A,F7.2)', "  x = ", x_new, " → y = ", y_pred
    end subroutine predict_and_display
    
end program linear_regression
