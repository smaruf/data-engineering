! Hello AI - Introduction to AI concepts in Fortran
! This program demonstrates basic AI concepts: data, weights, and simple prediction
program hello_ai
    implicit none
    
    ! Variables
    real, dimension(3) :: features
    real, dimension(3) :: weights
    real :: bias, prediction
    integer :: i
    
    print *, "======================================"
    print *, "   Welcome to Fortran AI!"
    print *, "======================================"
    print *
    
    ! Initialize input features (e.g., house: size, bedrooms, age)
    features = [1500.0, 3.0, 10.0]
    print *, "Input Features (House):"
    print *, "  Size (sq ft):", features(1)
    print *, "  Bedrooms:", features(2)
    print *, "  Age (years):", features(3)
    print *
    
    ! Initialize weights (learned parameters)
    weights = [0.1, 50.0, -2.0]
    bias = 100.0
    
    print *, "Model Parameters:"
    print *, "  Weight for size:", weights(1)
    print *, "  Weight for bedrooms:", weights(2)
    print *, "  Weight for age:", weights(3)
    print *, "  Bias:", bias
    print *
    
    ! Make prediction using weighted sum
    ! This is the fundamental operation in neural networks!
    prediction = bias
    do i = 1, 3
        prediction = prediction + weights(i) * features(i)
    end do
    
    ! Alternatively using dot_product (more efficient)
    ! prediction = dot_product(weights, features) + bias
    
    print *, "Prediction Process:"
    print *, "  prediction = bias + Σ(weight_i × feature_i)"
    print *, "  prediction =", bias, "+ (", weights(1), "×", features(1), &
             ") + (", weights(2), "×", features(2), ") + (", weights(3), &
             "×", features(3), ")"
    print *
    print *, "Predicted House Price: $", prediction * 1000.0
    print *
    
    print *, "======================================"
    print *, "   Key AI Concepts Demonstrated:"
    print *, "======================================"
    print *, "1. Features: Input data (size, bedrooms, age)"
    print *, "2. Weights: Learned parameters (importance of each feature)"
    print *, "3. Bias: Baseline prediction"
    print *, "4. Prediction: Weighted sum of inputs"
    print *
    print *, "This is the foundation of all neural networks!"
    print *, "In real AI, we learn the weights from data."
    print *
    
end program hello_ai
