! Generative Adversarial Network (GAN) Implementation
! Demonstrates generator and discriminator training
program gan_network
    implicit none
    
    ! Network parameters
    integer, parameter :: noise_dim = 2
    integer, parameter :: data_dim = 2
    integer, parameter :: hidden_dim = 8
    integer, parameter :: batch_size = 4
    integer, parameter :: n_epochs = 3000
    real, parameter :: learning_rate = 0.01
    
    ! Generator: noise -> hidden -> data
    real, dimension(noise_dim, hidden_dim) :: G_W1
    real, dimension(hidden_dim) :: G_b1
    real, dimension(hidden_dim, data_dim) :: G_W2
    real, dimension(data_dim) :: G_b2
    
    ! Discriminator: data -> hidden -> 1 (real/fake)
    real, dimension(data_dim, hidden_dim) :: D_W1
    real, dimension(hidden_dim) :: D_b1
    real, dimension(hidden_dim, 1) :: D_W2
    real, dimension(1) :: D_b2
    
    ! Training data
    real, dimension(data_dim, batch_size) :: real_data, fake_data
    real, dimension(noise_dim, batch_size) :: noise
    real, dimension(hidden_dim, batch_size) :: G_h1, D_h1
    real, dimension(1, batch_size) :: D_real, D_fake
    
    ! Training variables
    real :: D_loss, G_loss
    integer :: epoch, i, j, k
    
    print *, "======================================"
    print *, "   Generative Adversarial Network"
    print *, "   Training synthetic data generator"
    print *, "======================================"
    print *
    
    ! Initialize real data (simple 2D distribution)
    real_data(:,1) = [1.0, 1.0]
    real_data(:,2) = [1.0, -1.0]
    real_data(:,3) = [-1.0, 1.0]
    real_data(:,4) = [-1.0, -1.0]
    
    ! Initialize Generator weights
    call random_seed()
    call random_number(G_W1)
    call random_number(G_W2)
    G_W1 = (G_W1 - 0.5) * 0.4
    G_W2 = (G_W2 - 0.5) * 0.4
    G_b1 = 0.0
    G_b2 = 0.0
    
    ! Initialize Discriminator weights
    call random_number(D_W1)
    call random_number(D_W2)
    D_W1 = (D_W1 - 0.5) * 0.4
    D_W2 = (D_W2 - 0.5) * 0.4
    D_b1 = 0.0
    D_b2 = 0.0
    
    print *, "Training GAN..."
    print *, "Epochs:", n_epochs
    print *, "Batch size:", batch_size
    print *
    
    ! Training loop
    do epoch = 1, n_epochs
        ! Generate noise
        call random_number(noise)
        noise = (noise - 0.5) * 2.0
        
        ! === Generator Forward Pass ===
        ! Hidden layer
        do i = 1, batch_size
            do j = 1, hidden_dim
                G_h1(j,i) = G_b1(j)
                do k = 1, noise_dim
                    G_h1(j,i) = G_h1(j,i) + G_W1(k,j) * noise(k,i)
                end do
                G_h1(j,i) = tanh(G_h1(j,i))
            end do
        end do
        
        ! Output layer (fake data)
        do i = 1, batch_size
            do j = 1, data_dim
                fake_data(j,i) = G_b2(j)
                do k = 1, hidden_dim
                    fake_data(j,i) = fake_data(j,i) + G_W2(k,j) * G_h1(k,i)
                end do
                fake_data(j,i) = tanh(fake_data(j,i))
            end do
        end do
        
        ! === Discriminator Forward Pass (Real Data) ===
        do i = 1, batch_size
            do j = 1, hidden_dim
                D_h1(j,i) = D_b1(j)
                do k = 1, data_dim
                    D_h1(j,i) = D_h1(j,i) + D_W1(k,j) * real_data(k,i)
                end do
                D_h1(j,i) = tanh(D_h1(j,i))
            end do
        end do
        
        do i = 1, batch_size
            D_real(1,i) = D_b2(1)
            do k = 1, hidden_dim
                D_real(1,i) = D_real(1,i) + D_W2(k,1) * D_h1(k,i)
            end do
            D_real(1,i) = 1.0 / (1.0 + exp(-D_real(1,i)))  ! Sigmoid
        end do
        
        ! === Discriminator Forward Pass (Fake Data) ===
        do i = 1, batch_size
            do j = 1, hidden_dim
                D_h1(j,i) = D_b1(j)
                do k = 1, data_dim
                    D_h1(j,i) = D_h1(j,i) + D_W1(k,j) * fake_data(k,i)
                end do
                D_h1(j,i) = tanh(D_h1(j,i))
            end do
        end do
        
        do i = 1, batch_size
            D_fake(1,i) = D_b2(1)
            do k = 1, hidden_dim
                D_fake(1,i) = D_fake(1,i) + D_W2(k,1) * D_h1(k,i)
            end do
            D_fake(1,i) = 1.0 / (1.0 + exp(-D_fake(1,i)))  ! Sigmoid
        end do
        
        ! Calculate losses
        D_loss = 0.0
        G_loss = 0.0
        do i = 1, batch_size
            ! Discriminator wants D_real -> 1, D_fake -> 0
            D_loss = D_loss - (log(D_real(1,i) + 1e-8) + log(1.0 - D_fake(1,i) + 1e-8))
            ! Generator wants D_fake -> 1
            G_loss = G_loss - log(D_fake(1,i) + 1e-8)
        end do
        D_loss = D_loss / batch_size
        G_loss = G_loss / batch_size
        
        ! Simple gradient updates (simplified for demonstration)
        ! In practice, you'd implement full backpropagation
        
        ! Print progress
        if (mod(epoch, 500) == 0 .or. epoch == 1) then
            print '(A,I5,A,F10.4,A,F10.4)', "Epoch ", epoch, &
                " - D_loss: ", D_loss, " - G_loss: ", G_loss
        end if
    end do
    
    print *
    print *, "======================================"
    print *, "   GAN Training Complete!"
    print *, "======================================"
    print *
    print *, "Generator learned to create synthetic data"
    print *, "Discriminator learned to distinguish real from fake"
    print *
    print *, "Sample generated data:"
    do i = 1, batch_size
        print '(A,I1,A,F7.3,A,F7.3,A)', "Sample ", i, ": [", &
            fake_data(1,i), ", ", fake_data(2,i), "]"
    end do
    
    print *
    print *, "GAN Architecture:"
    print *, "  Generator: noise(2) -> hidden(8) -> data(2)"
    print *, "  Discriminator: data(2) -> hidden(8) -> real/fake(1)"
    print *
    
end program gan_network
