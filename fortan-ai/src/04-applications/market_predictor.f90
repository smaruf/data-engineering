! Time Series Prediction with Market Data
! Implements LSTM-like recurrent patterns for sequential data
program market_predictor
    implicit none
    
    ! Network parameters
    integer, parameter :: sequence_length = 10
    integer, parameter :: hidden_size = 8
    integer, parameter :: n_epochs = 1000
    real, parameter :: learning_rate = 0.01
    
    ! Market data (simulated price sequence)
    real, dimension(sequence_length + 5) :: market_prices
    real, dimension(sequence_length) :: input_sequence
    real, dimension(hidden_size) :: hidden_state, cell_state
    real :: prediction, target, loss
    
    ! LSTM-like weights (simplified)
    real, dimension(1, hidden_size) :: W_input
    real, dimension(hidden_size, hidden_size) :: W_hidden
    real, dimension(hidden_size, 1) :: W_output
    real, dimension(hidden_size) :: b_hidden
    real :: b_output
    
    integer :: epoch, t, i, j
    
    print *, "======================================"
    print *, "   Market Data Time Series Predictor"
    print *, "   LSTM-style Recurrent Network"
    print *, "======================================"
    print *
    
    ! Generate synthetic market data (trend + noise)
    call random_seed()
    market_prices(1) = 100.0
    do i = 2, sequence_length + 5
        call random_number(loss)  ! Reuse variable for random
        market_prices(i) = market_prices(i-1) * (1.0 + 0.01 * (loss - 0.5))
    end do
    
    print *, "Market Price History:"
    do i = 1, sequence_length + 5
        print '(A,I2,A,F10.4)', "Day ", i, ": $", market_prices(i)
    end do
    print *
    
    ! Initialize weights
    call random_number(W_input)
    call random_number(W_hidden)
    call random_number(W_output)
    W_input = (W_input - 0.5) * 0.2
    W_hidden = (W_hidden - 0.5) * 0.2
    W_output = (W_output - 0.5) * 0.2
    b_hidden = 0.0
    b_output = 0.0
    
    print *, "Training recurrent network on market data..."
    print *, "Sequence length:", sequence_length
    print *, "Hidden units:", hidden_size
    print *
    
    ! Training loop
    do epoch = 1, n_epochs
        ! Prepare input sequence
        input_sequence = market_prices(1:sequence_length)
        target = market_prices(sequence_length + 1)
        
        ! Initialize hidden state
        hidden_state = 0.0
        cell_state = 0.0
        
        ! Process sequence (forward pass)
        do t = 1, sequence_length
            ! Update hidden state based on input and previous hidden
            do i = 1, hidden_size
                hidden_state(i) = b_hidden(i)
                ! Input contribution
                hidden_state(i) = hidden_state(i) + W_input(1,i) * input_sequence(t)
                ! Previous hidden state contribution
                do j = 1, hidden_size
                    hidden_state(i) = hidden_state(i) + W_hidden(j,i) * cell_state(j)
                end do
                ! Activation
                hidden_state(i) = tanh(hidden_state(i))
            end do
            
            ! Update cell state
            cell_state = hidden_state
        end do
        
        ! Generate prediction
        prediction = b_output
        do i = 1, hidden_size
            prediction = prediction + W_output(i,1) * hidden_state(i)
        end do
        
        ! Calculate loss
        loss = (prediction - target) ** 2
        
        ! Simple gradient descent update (simplified)
        ! In practice, use BPTT (Backpropagation Through Time)
        do i = 1, hidden_size
            W_output(i,1) = W_output(i,1) - learning_rate * 2.0 * (prediction - target) * hidden_state(i)
        end do
        b_output = b_output - learning_rate * 2.0 * (prediction - target)
        
        if (mod(epoch, 200) == 0 .or. epoch == 1) then
            print '(A,I5,A,F10.4,A,F10.4,A,F10.4)', "Epoch ", epoch, &
                " - Loss: ", loss, " - Pred: $", prediction, " - True: $", target
        end if
    end do
    
    print *
    print *, "======================================"
    print *, "   Prediction Results"
    print *, "======================================"
    print *
    print *, "Last known price: $", market_prices(sequence_length)
    print *, "Actual next price: $", target
    print *, "Predicted price: $", prediction
    print *, "Prediction error: $", abs(prediction - target)
    print *
    
    ! Predict next 5 days
    print *, "Future predictions (next 5 days):"
    do i = 1, 5
        ! Reset hidden state for new prediction
        hidden_state = 0.0
        cell_state = 0.0
        
        ! Use updated sequence
        input_sequence(1:sequence_length-1) = input_sequence(2:sequence_length)
        input_sequence(sequence_length) = prediction
        
        ! Process sequence
        do t = 1, sequence_length
            do j = 1, hidden_size
                hidden_state(j) = b_hidden(j)
                hidden_state(j) = hidden_state(j) + W_input(1,j) * input_sequence(t)
                do epoch = 1, hidden_size
                    hidden_state(j) = hidden_state(j) + W_hidden(epoch,j) * cell_state(epoch)
                end do
                hidden_state(j) = tanh(hidden_state(j))
            end do
            cell_state = hidden_state
        end do
        
        prediction = b_output
        do j = 1, hidden_size
            prediction = prediction + W_output(j,1) * hidden_state(j)
        end do
        
        print '(A,I1,A,F10.4,A,F10.4,A)', "Day +", i, ": $", prediction, &
            " (actual: $", market_prices(sequence_length + i), ")"
    end do
    
    print *
    print *, "Time Series Model Features:"
    print *, "  - Recurrent processing of sequences"
    print *, "  - Hidden state memory across time steps"
    print *, "  - Suitable for market data analysis"
    print *, "  - Can be extended for online data feeds"
    print *
    
end program market_predictor
