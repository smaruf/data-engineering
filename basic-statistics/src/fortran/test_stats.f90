! ============================================================================
! PROGRAM: test_stats
! 
! Description:
!   Test program demonstrating the Fortran statistics library
!
! Author: Data Engineering Team
! Date: 2026
! ============================================================================

program test_stats
    use descriptive_stats
    use probability
    implicit none
    
    ! Variables
    integer, parameter :: n = 10
    real(8) :: data(n)
    real(8) :: mean_val, median_val, var_val, std_val
    real(8) :: skew_val, kurt_val, range_val_res, iqr_val
    real(8) :: random_data(100)
    integer :: i
    
    ! Sample data
    data = [23.0d0, 45.0d0, 12.0d0, 67.0d0, 34.0d0, &
            89.0d0, 23.0d0, 45.0d0, 67.0d0, 51.0d0]
    
    ! Print header
    print *, "============================================"
    print *, "  Fortran Statistics Library Test"
    print *, "============================================"
    print *, ""
    
    ! Display data
    print *, "Sample Data:"
    print '(10F8.2)', data
    print *, ""
    
    ! Calculate and display descriptive statistics
    print *, "Descriptive Statistics:"
    print *, "----------------------------------------"
    
    mean_val = mean(data, n)
    print '(A,F10.4)', "  Mean:              ", mean_val
    
    median_val = median(data, n)
    print '(A,F10.4)', "  Median:            ", median_val
    
    var_val = variance(data, n)
    print '(A,F10.4)', "  Variance:          ", var_val
    
    std_val = std_dev(data, n)
    print '(A,F10.4)', "  Std Deviation:     ", std_val
    
    skew_val = skewness(data, n)
    print '(A,F10.4)', "  Skewness:          ", skew_val
    
    kurt_val = kurtosis(data, n)
    print '(A,F10.4)', "  Kurtosis (excess): ", kurt_val
    
    range_val_res = range_val(data, n)
    print '(A,F10.4)', "  Range:             ", range_val_res
    
    iqr_val = iqr(data, n)
    print '(A,F10.4)', "  IQR:               ", iqr_val
    
    print *, ""
    
    ! Test probability functions
    print *, "Probability Distribution Tests:"
    print *, "----------------------------------------"
    print '(A,F10.6)', "  Normal PDF(0, 0, 1):    ", normal_pdf(0.0d0, 0.0d0, 1.0d0)
    print '(A,F10.6)', "  Normal CDF(0, 0, 1):    ", normal_cdf(0.0d0, 0.0d0, 1.0d0)
    print '(A,F10.6)', "  Normal INV_CDF(0.975):  ", normal_inv_cdf(0.975d0, 0.0d0, 1.0d0)
    print *, ""
    
    ! Generate random numbers
    print *, "Random Number Generation:"
    print *, "----------------------------------------"
    call init_random_seed()
    call generate_normal_random(random_data, 100, 0.0d0, 1.0d0)
    
    print '(A,F10.4)', "  Mean of 100 N(0,1):     ", mean(random_data, 100)
    print '(A,F10.4)', "  Std Dev of 100 N(0,1):  ", std_dev(random_data, 100)
    print *, ""
    
    print *, "============================================"
    print *, "  Test Complete!"
    print *, "============================================"

end program test_stats
