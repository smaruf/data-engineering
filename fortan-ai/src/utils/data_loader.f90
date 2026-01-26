! Data Loader Module for Online Feeds
! Supports loading and preprocessing market data
module data_loader
    implicit none
    
    ! Data structure for market data
    type :: MarketData
        real, dimension(:), allocatable :: prices
        real, dimension(:), allocatable :: volumes
        integer :: n_points
    end type MarketData
    
contains
    
    ! Load data from CSV file
    subroutine load_csv_data(filename, data)
        character(len=*), intent(in) :: filename
        type(MarketData), intent(out) :: data
        integer :: unit, ios, n_lines, i
        real :: price, volume
        
        ! Count lines first
        n_lines = 0
        open(newunit=unit, file=filename, status='old', iostat=ios)
        if (ios /= 0) then
            print *, "Warning: Could not open file ", filename
            print *, "Creating sample data instead..."
            call generate_sample_data(data, 100)
            return
        end if
        
        do
            read(unit, *, iostat=ios) price, volume
            if (ios /= 0) exit
            n_lines = n_lines + 1
        end do
        close(unit)
        
        ! Allocate and read data
        data%n_points = n_lines
        allocate(data%prices(n_lines))
        allocate(data%volumes(n_lines))
        
        open(newunit=unit, file=filename, status='old')
        do i = 1, n_lines
            read(unit, *) data%prices(i), data%volumes(i)
        end do
        close(unit)
        
    end subroutine load_csv_data
    
    ! Generate sample market data
    subroutine generate_sample_data(data, n_points)
        type(MarketData), intent(out) :: data
        integer, intent(in) :: n_points
        integer :: i
        real :: trend, noise
        
        data%n_points = n_points
        allocate(data%prices(n_points))
        allocate(data%volumes(n_points))
        
        call random_seed()
        
        ! Generate trending prices with noise
        data%prices(1) = 100.0
        do i = 2, n_points
            call random_number(noise)
            trend = 0.001 * i  ! Upward trend
            data%prices(i) = data%prices(i-1) * (1.0 + trend + 0.02 * (noise - 0.5))
        end do
        
        ! Generate volumes
        do i = 1, n_points
            call random_number(noise)
            data%volumes(i) = 1000.0 + 500.0 * noise
        end do
        
    end subroutine generate_sample_data
    
    ! Normalize data to [0, 1] range
    subroutine normalize_data(data, min_val, max_val)
        real, dimension(:), intent(inout) :: data
        real, intent(out) :: min_val, max_val
        integer :: i
        
        min_val = minval(data)
        max_val = maxval(data)
        
        if (max_val > min_val) then
            do i = 1, size(data)
                data(i) = (data(i) - min_val) / (max_val - min_val)
            end do
        end if
        
    end subroutine normalize_data
    
    ! Create sequences for time series training
    subroutine create_sequences(data, seq_length, X, y)
        real, dimension(:), intent(in) :: data
        integer, intent(in) :: seq_length
        real, dimension(:,:), allocatable, intent(out) :: X
        real, dimension(:), allocatable, intent(out) :: y
        integer :: n_sequences, i, j
        
        n_sequences = size(data) - seq_length
        allocate(X(seq_length, n_sequences))
        allocate(y(n_sequences))
        
        do i = 1, n_sequences
            do j = 1, seq_length
                X(j, i) = data(i + j - 1)
            end do
            y(i) = data(i + seq_length)
        end do
        
    end subroutine create_sequences
    
    ! Calculate simple statistics
    subroutine calculate_stats(data, mean_val, std_val)
        real, dimension(:), intent(in) :: data
        real, intent(out) :: mean_val, std_val
        integer :: n, i
        
        n = size(data)
        mean_val = sum(data) / n
        
        std_val = 0.0
        do i = 1, n
            std_val = std_val + (data(i) - mean_val)**2
        end do
        std_val = sqrt(std_val / n)
        
    end subroutine calculate_stats
    
end module data_loader
