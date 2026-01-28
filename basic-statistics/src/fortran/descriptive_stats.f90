! ============================================================================
! MODULE: descriptive_stats
! 
! Description:
!   High-performance Fortran implementation of descriptive statistics
!   including measures of central tendency, dispersion, and shape.
!
! Author: Data Engineering Team
! Date: 2026
! ============================================================================

module descriptive_stats
    implicit none
    private
    
    ! Public procedures
    public :: mean, median, variance, std_dev, skewness, kurtosis
    public :: range_val, iqr, percentile
    
contains

    ! ========================================================================
    ! FUNCTION: mean
    ! Calculate arithmetic mean
    ! ========================================================================
    real(8) function mean(data, n)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        integer :: i
        real(8) :: sum_val
        
        sum_val = 0.0d0
        do i = 1, n
            sum_val = sum_val + data(i)
        end do
        
        mean = sum_val / real(n, 8)
    end function mean
    
    ! ========================================================================
    ! FUNCTION: median
    ! Calculate median value (50th percentile)
    ! ========================================================================
    real(8) function median(data, n)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        real(8) :: sorted_data(n)
        integer :: mid
        
        ! Sort data
        sorted_data = data
        call quick_sort(sorted_data, 1, n)
        
        ! Calculate median
        mid = n / 2
        if (mod(n, 2) == 0) then
            median = (sorted_data(mid) + sorted_data(mid + 1)) / 2.0d0
        else
            median = sorted_data(mid + 1)
        end if
    end function median
    
    ! ========================================================================
    ! FUNCTION: variance
    ! Calculate variance using two-pass algorithm for numerical stability
    ! ========================================================================
    real(8) function variance(data, n, sample)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        logical, intent(in), optional :: sample
        real(8) :: mean_val, sum_sq
        integer :: i, denom
        logical :: is_sample
        
        ! Default to sample variance (n-1)
        is_sample = .true.
        if (present(sample)) is_sample = sample
        
        ! Calculate mean
        mean_val = mean(data, n)
        
        ! Calculate sum of squared deviations
        sum_sq = 0.0d0
        do i = 1, n
            sum_sq = sum_sq + (data(i) - mean_val)**2
        end do
        
        ! Divide by n-1 (sample) or n (population)
        if (is_sample) then
            denom = n - 1
        else
            denom = n
        end if
        
        variance = sum_sq / real(denom, 8)
    end function variance
    
    ! ========================================================================
    ! FUNCTION: std_dev
    ! Calculate standard deviation
    ! ========================================================================
    real(8) function std_dev(data, n, sample)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        logical, intent(in), optional :: sample
        
        std_dev = sqrt(variance(data, n, sample))
    end function std_dev
    
    ! ========================================================================
    ! FUNCTION: skewness
    ! Calculate skewness (third standardized moment)
    ! ========================================================================
    real(8) function skewness(data, n)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        real(8) :: mean_val, std_val, sum_cube
        integer :: i
        
        mean_val = mean(data, n)
        std_val = std_dev(data, n)
        
        if (std_val == 0.0d0) then
            skewness = 0.0d0
            return
        end if
        
        sum_cube = 0.0d0
        do i = 1, n
            sum_cube = sum_cube + ((data(i) - mean_val) / std_val)**3
        end do
        
        skewness = sum_cube / real(n, 8)
    end function skewness
    
    ! ========================================================================
    ! FUNCTION: kurtosis
    ! Calculate kurtosis (fourth standardized moment)
    ! Returns excess kurtosis (subtracts 3)
    ! ========================================================================
    real(8) function kurtosis(data, n)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        real(8) :: mean_val, std_val, sum_fourth
        integer :: i
        
        mean_val = mean(data, n)
        std_val = std_dev(data, n)
        
        if (std_val == 0.0d0) then
            kurtosis = 0.0d0
            return
        end if
        
        sum_fourth = 0.0d0
        do i = 1, n
            sum_fourth = sum_fourth + ((data(i) - mean_val) / std_val)**4
        end do
        
        ! Excess kurtosis (subtract 3 for normal distribution)
        kurtosis = (sum_fourth / real(n, 8)) - 3.0d0
    end function kurtosis
    
    ! ========================================================================
    ! FUNCTION: range_val
    ! Calculate range (max - min)
    ! ========================================================================
    real(8) function range_val(data, n)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        
        range_val = maxval(data) - minval(data)
    end function range_val
    
    ! ========================================================================
    ! FUNCTION: iqr
    ! Calculate interquartile range (Q3 - Q1)
    ! ========================================================================
    real(8) function iqr(data, n)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n)
        real(8) :: q1, q3
        
        q1 = percentile(data, n, 25.0d0)
        q3 = percentile(data, n, 75.0d0)
        iqr = q3 - q1
    end function iqr
    
    ! ========================================================================
    ! FUNCTION: percentile
    ! Calculate percentile value
    ! ========================================================================
    real(8) function percentile(data, n, p)
        integer, intent(in) :: n
        real(8), intent(in) :: data(n), p
        real(8) :: sorted_data(n)
        real(8) :: position, fraction
        integer :: lower_idx, upper_idx
        
        ! Sort data
        sorted_data = data
        call quick_sort(sorted_data, 1, n)
        
        ! Calculate position
        position = (p / 100.0d0) * real(n + 1, 8)
        lower_idx = int(position)
        fraction = position - real(lower_idx, 8)
        
        ! Handle edge cases
        if (lower_idx < 1) then
            percentile = sorted_data(1)
        else if (lower_idx >= n) then
            percentile = sorted_data(n)
        else
            upper_idx = lower_idx + 1
            percentile = sorted_data(lower_idx) + &
                        fraction * (sorted_data(upper_idx) - sorted_data(lower_idx))
        end if
    end function percentile
    
    ! ========================================================================
    ! SUBROUTINE: quick_sort
    ! Quick sort algorithm for sorting arrays
    ! ========================================================================
    recursive subroutine quick_sort(array, left, right)
        real(8), intent(inout) :: array(:)
        integer, intent(in) :: left, right
        integer :: i, j
        real(8) :: pivot, temp
        
        if (left < right) then
            pivot = array((left + right) / 2)
            i = left
            j = right
            
            do while (i <= j)
                do while (array(i) < pivot)
                    i = i + 1
                end do
                do while (array(j) > pivot)
                    j = j - 1
                end do
                
                if (i <= j) then
                    temp = array(i)
                    array(i) = array(j)
                    array(j) = temp
                    i = i + 1
                    j = j - 1
                end if
            end do
            
            if (left < j) call quick_sort(array, left, j)
            if (i < right) call quick_sort(array, i, right)
        end if
    end subroutine quick_sort

end module descriptive_stats
