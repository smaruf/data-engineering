! Matrix Operations Module
! Common linear algebra operations for AI
module matrix_ops
    implicit none
    private
    public :: matrix_multiply, matrix_transpose, matrix_add, &
              vector_dot, matrix_print, identity_matrix
    
contains
    
    ! Matrix multiplication: C = A × B
    function matrix_multiply(A, B) result(C)
        real, dimension(:,:), intent(in) :: A, B
        real, dimension(size(A,1), size(B,2)) :: C
        integer :: i, j, k
        
        C = 0.0
        do i = 1, size(A, 1)
            do j = 1, size(B, 2)
                do k = 1, size(A, 2)
                    C(i,j) = C(i,j) + A(i,k) * B(k,j)
                end do
            end do
        end do
    end function matrix_multiply
    
    ! Matrix transpose: AT = A^T
    function matrix_transpose(A) result(AT)
        real, dimension(:,:), intent(in) :: A
        real, dimension(size(A,2), size(A,1)) :: AT
        integer :: i, j
        
        do i = 1, size(A, 1)
            do j = 1, size(A, 2)
                AT(j, i) = A(i, j)
            end do
        end do
    end function matrix_transpose
    
    ! Matrix addition: C = A + B
    function matrix_add(A, B) result(C)
        real, dimension(:,:), intent(in) :: A, B
        real, dimension(size(A,1), size(A,2)) :: C
        
        C = A + B
    end function matrix_add
    
    ! Vector dot product
    real function vector_dot(a, b)
        real, dimension(:), intent(in) :: a, b
        
        vector_dot = dot_product(a, b)
    end function vector_dot
    
    ! Print matrix
    subroutine matrix_print(A, name)
        real, dimension(:,:), intent(in) :: A
        character(len=*), intent(in), optional :: name
        integer :: i, j
        
        if (present(name)) then
            print *, trim(name), ":"
        end if
        
        do i = 1, size(A, 1)
            do j = 1, size(A, 2)
                write(*, '(F8.3)', advance='no') A(i, j)
            end do
            print *
        end do
        print *
    end subroutine matrix_print
    
    ! Create identity matrix
    function identity_matrix(n) result(I)
        integer, intent(in) :: n
        real, dimension(n, n) :: I
        integer :: i
        
        I = 0.0
        do i = 1, n
            I(i, i) = 1.0
        end do
    end function identity_matrix
    
end module matrix_ops
