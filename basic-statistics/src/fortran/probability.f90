! ============================================================================
! MODULE: probability
! 
! Description:
!   Fortran implementation of probability distributions and random number
!   generation for statistical computing.
!
! Author: Data Engineering Team
! Date: 2026
! ============================================================================

module probability
    implicit none
    private
    
    ! Public procedures
    public :: normal_pdf, normal_cdf, normal_inv_cdf
    public :: init_random_seed, generate_normal_random
    
    ! Constants
    real(8), parameter :: PI = 3.14159265358979323846d0
    real(8), parameter :: SQRT_2PI = 2.50662827463100050d0
    
contains

    ! ========================================================================
    ! FUNCTION: normal_pdf
    ! Calculate PDF of normal distribution N(mu, sigma^2)
    ! ========================================================================
    real(8) function normal_pdf(x, mu, sigma)
        real(8), intent(in) :: x, mu, sigma
        real(8) :: z
        
        z = (x - mu) / sigma
        normal_pdf = exp(-0.5d0 * z * z) / (sigma * SQRT_2PI)
    end function normal_pdf
    
    ! ========================================================================
    ! FUNCTION: normal_cdf
    ! Calculate CDF of standard normal distribution using error function
    ! ========================================================================
    real(8) function normal_cdf(x, mu, sigma)
        real(8), intent(in) :: x, mu, sigma
        real(8) :: z
        
        z = (x - mu) / (sigma * sqrt(2.0d0))
        normal_cdf = 0.5d0 * (1.0d0 + erf(z))
    end function normal_cdf
    
    ! ========================================================================
    ! FUNCTION: normal_inv_cdf
    ! Approximate inverse CDF (quantile function) for normal distribution
    ! Uses Beasley-Springer-Moro algorithm
    ! ========================================================================
    real(8) function normal_inv_cdf(p, mu, sigma)
        real(8), intent(in) :: p, mu, sigma
        real(8) :: q, r, z
        real(8), parameter :: a0 = 2.50662823884d0
        real(8), parameter :: a1 = -18.61500062529d0
        real(8), parameter :: a2 = 41.39119773534d0
        real(8), parameter :: a3 = -25.44106049637d0
        real(8), parameter :: b0 = -8.47351093090d0
        real(8), parameter :: b1 = 23.08336743743d0
        real(8), parameter :: b2 = -21.06224101826d0
        real(8), parameter :: b3 = 3.13082909833d0
        
        ! Handle edge cases
        if (p <= 0.0d0 .or. p >= 1.0d0) then
            normal_inv_cdf = 0.0d0
            return
        end if
        
        q = p - 0.5d0
        
        if (abs(q) <= 0.42d0) then
            ! Central region
            r = q * q
            z = q * (((a3 * r + a2) * r + a1) * r + a0) / &
                    ((((b3 * r + b2) * r + b1) * r + b0) * r + 1.0d0)
        else
            ! Tail region
            if (q > 0.0d0) then
                r = 1.0d0 - p
            else
                r = p
            end if
            
            r = sqrt(-log(r))
            z = (((a3 * r + a2) * r + a1) * r + a0) / &
                ((((b3 * r + b2) * r + b1) * r + b0) * r + 1.0d0)
            
            if (q < 0.0d0) z = -z
        end if
        
        normal_inv_cdf = mu + sigma * z
    end function normal_inv_cdf
    
    ! ========================================================================
    ! SUBROUTINE: init_random_seed
    ! Initialize random number generator with seed from system clock
    ! ========================================================================
    subroutine init_random_seed()
        integer :: i, n, clock
        integer, dimension(:), allocatable :: seed
        
        call random_seed(size = n)
        allocate(seed(n))
        
        call system_clock(count=clock)
        
        seed = clock + 37 * (/ (i - 1, i = 1, n) /)
        call random_seed(put = seed)
        
        deallocate(seed)
    end subroutine init_random_seed
    
    ! ========================================================================
    ! SUBROUTINE: generate_normal_random
    ! Generate random numbers from normal distribution
    ! Uses Box-Muller transform
    ! ========================================================================
    subroutine generate_normal_random(data, n, mu, sigma)
        integer, intent(in) :: n
        real(8), intent(out) :: data(n)
        real(8), intent(in) :: mu, sigma
        real(8) :: u1, u2, z1, z2
        integer :: i
        
        do i = 1, n, 2
            ! Generate two uniform random numbers
            call random_number(u1)
            call random_number(u2)
            
            ! Box-Muller transform
            z1 = sqrt(-2.0d0 * log(u1)) * cos(2.0d0 * PI * u2)
            z2 = sqrt(-2.0d0 * log(u1)) * sin(2.0d0 * PI * u2)
            
            ! Scale and shift
            data(i) = mu + sigma * z1
            if (i + 1 <= n) then
                data(i + 1) = mu + sigma * z2
            end if
        end do
    end subroutine generate_normal_random

end module probability
