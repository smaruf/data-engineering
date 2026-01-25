# Fortran AI: From Zero to Expert

A comprehensive guide to implementing Artificial Intelligence and Machine Learning algorithms using modern Fortran. This project demonstrates the power of Fortran in scientific computing and AI applications.

## 📚 Table of Contents

- [Overview](#overview)
- [Why Fortran for AI?](#why-fortran-for-ai)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Learning Path](#learning-path)
- [Examples](#examples)
- [Documentation](#documentation)
- [Prerequisites](#prerequisites)
- [Building and Running](#building-and-running)
- [Contributing](#contributing)
- [Resources](#resources)

## 🎯 Overview

This project provides a structured approach to learning AI/ML implementation in Fortran, from basic concepts to advanced deep learning techniques. Fortran's performance, array operations, and mathematical capabilities make it an excellent choice for AI computations.

## 💡 Why Fortran for AI?

- **Performance**: Fortran is one of the fastest languages for numerical computations
- **Array Operations**: Native support for multi-dimensional arrays and matrix operations
- **Parallelization**: Built-in support for parallel computing (OpenMP, MPI, Coarrays)
- **Legacy**: Extensive scientific libraries and proven reliability
- **Modern Features**: Fortran 2008/2018 brings object-oriented programming and modern capabilities

## 📁 Project Structure

```
fortan-ai/
├── README.md                          # This file
├── docs/                              # Detailed documentation
│   ├── 01-introduction.md            # Introduction to Fortran for AI
│   ├── 02-basics.md                  # Fortran basics refresher
│   ├── 03-linear-algebra.md          # Linear algebra foundations
│   ├── 04-neural-networks.md         # Neural network theory
│   ├── 05-optimization.md            # Optimization algorithms
│   └── 06-advanced-topics.md         # Advanced AI topics
├── src/                               # Source code
│   ├── 01-beginner/                  # Beginner level examples
│   │   ├── hello_ai.f90              # Hello world AI example
│   │   ├── linear_regression.f90     # Simple linear regression
│   │   ├── perceptron.f90            # Single perceptron
│   │   └── logistic_regression.f90   # Logistic regression
│   ├── 02-intermediate/              # Intermediate level
│   │   ├── neural_network.f90        # Multi-layer neural network
│   │   ├── gradient_descent.f90      # Gradient descent implementation
│   │   ├── backpropagation.f90       # Backpropagation algorithm
│   │   └── activation_functions.f90  # Various activation functions
│   ├── 03-advanced/                  # Advanced level
│   │   ├── deep_neural_network.f90   # Deep learning implementation
│   │   ├── convolutional_nn.f90      # CNN implementation
│   │   ├── optimizer_adam.f90        # ADAM optimizer
│   │   └── batch_normalization.f90   # Batch normalization
│   ├── 04-applications/              # Real-world applications
│   │   ├── mnist_classifier.f90      # MNIST digit classification
│   │   ├── iris_classifier.f90       # Iris dataset classification
│   │   ├── time_series.f90           # Time series prediction
│   │   └── image_processing.f90      # Basic image processing
│   └── utils/                         # Utility modules
│       ├── matrix_ops.f90            # Matrix operations
│       ├── data_loader.f90           # Data loading utilities
│       ├── math_utils.f90            # Mathematical utilities
│       └── visualization.f90         # Data visualization helpers
├── data/                              # Example datasets
│   ├── iris.csv                      # Iris dataset
│   ├── simple_data.csv               # Simple training data
│   └── README.md                     # Dataset descriptions
├── tests/                             # Unit tests
│   ├── test_matrix_ops.f90
│   ├── test_neural_network.f90
│   └── test_regression.f90
├── examples/                          # Complete examples
│   ├── example_01_simple_nn.f90
│   ├── example_02_classification.f90
│   └── example_03_prediction.f90
├── Makefile                           # Build system
└── requirements.txt                   # Required tools and libraries

```

## 🚀 Getting Started

### Prerequisites

- **Fortran Compiler**: gfortran (GCC 9.0+) or ifort (Intel Fortran)
- **Build Tools**: Make
- **Optional**: OpenBLAS or Intel MKL for optimized linear algebra
- **Optional**: gnuplot for visualization

### Installation

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install gfortran make
sudo apt-get install libopenblas-dev  # Optional: for optimized matrix operations
```

#### On macOS:
```bash
brew install gcc make
brew install openblas  # Optional
```

#### On Windows:
- Install MinGW-w64 or use WSL (Windows Subsystem for Linux)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/smaruf/data-engineering.git
cd data-engineering/fortan-ai
```

2. Build all examples:
```bash
make all
```

3. Run your first AI program:
```bash
./bin/hello_ai
```

## 📖 Learning Path

### Level 1: Beginner (Weeks 1-2)
**Goal**: Understand basics of AI in Fortran and simple algorithms

1. **Hello AI** - Introduction to AI concepts in Fortran
2. **Linear Regression** - Implement simple linear regression from scratch
3. **Perceptron** - Build a single perceptron classifier
4. **Logistic Regression** - Binary classification using logistic regression

**Key Concepts**: Variables, arrays, subroutines, basic I/O, matrix operations

### Level 2: Intermediate (Weeks 3-4)
**Goal**: Implement neural networks and understand backpropagation

1. **Neural Network** - Multi-layer perceptron implementation
2. **Gradient Descent** - Optimization algorithms
3. **Backpropagation** - Training neural networks
4. **Activation Functions** - ReLU, Sigmoid, Tanh, Softmax

**Key Concepts**: Modules, derived types, forward/backward propagation, loss functions

### Level 3: Advanced (Weeks 5-6)
**Goal**: Build deep learning models and advanced architectures

1. **Deep Neural Networks** - Networks with multiple hidden layers
2. **Convolutional Neural Networks** - Image processing with CNNs
3. **ADAM Optimizer** - Advanced optimization techniques
4. **Batch Normalization** - Improving training stability

**Key Concepts**: Object-oriented programming, optimization, regularization

### Level 4: Expert (Weeks 7-8)
**Goal**: Apply knowledge to real-world problems and optimize performance

1. **MNIST Classification** - Handwritten digit recognition
2. **Iris Classification** - Multi-class classification
3. **Time Series Prediction** - Sequential data processing
4. **Parallel Computing** - Using OpenMP/MPI for distributed training

**Key Concepts**: Real datasets, performance optimization, parallel programming

## 💻 Examples

### Example 1: Simple Linear Regression

```fortran
program simple_regression
    implicit none
    real, dimension(5) :: x = [1.0, 2.0, 3.0, 4.0, 5.0]
    real, dimension(5) :: y = [2.0, 4.0, 6.0, 8.0, 10.0]
    real :: slope, intercept
    
    call linear_fit(x, y, slope, intercept)
    print *, "Slope: ", slope
    print *, "Intercept: ", intercept
end program simple_regression
```

### Example 2: Neural Network

```fortran
program neural_network_example
    use neural_net_module
    implicit none
    type(NeuralNetwork) :: net
    real, dimension(2, 4) :: X_train
    real, dimension(1, 4) :: y_train
    
    ! Initialize network: 2 inputs, 4 hidden, 1 output
    call net%init([2, 4, 1])
    
    ! Training data (XOR problem)
    X_train = reshape([0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0], [2, 4])
    y_train = reshape([0.0, 1.0, 1.0, 0.0], [1, 4])
    
    ! Train the network
    call net%train(X_train, y_train, epochs=1000, learning_rate=0.1)
    
    ! Make predictions
    call net%predict(X_train)
end program neural_network_example
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

1. **[Introduction](docs/01-introduction.md)** - Overview of AI and Fortran
2. **[Fortran Basics](docs/02-basics.md)** - Modern Fortran refresher
3. **[Linear Algebra](docs/03-linear-algebra.md)** - Mathematical foundations
4. **[Neural Networks](docs/04-neural-networks.md)** - Deep learning theory
5. **[Optimization](docs/05-optimization.md)** - Training algorithms
6. **[Advanced Topics](docs/06-advanced-topics.md)** - CNNs, RNNs, and more

## 🔨 Building and Running

### Build All Examples
```bash
make all
```

### Build Specific Example
```bash
make beginner    # Build beginner examples
make intermediate # Build intermediate examples
make advanced    # Build advanced examples
make ml          # Build machine learning examples
```

### Run Examples
```bash
./bin/linear_regression
./bin/neural_network
./bin/mnist_classifier
```

### Clean Build
```bash
make clean
```

## 🧪 Testing

Run unit tests:
```bash
make test
```

## 🎓 What You'll Learn

By completing this project, you will:

- ✅ Understand AI/ML fundamentals through implementation
- ✅ Master modern Fortran programming techniques
- ✅ Implement neural networks from scratch
- ✅ Apply mathematical concepts (linear algebra, calculus)
- ✅ Optimize code for high performance
- ✅ Work with real datasets and solve practical problems
- ✅ Use parallel programming for large-scale computations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- New examples
- Documentation improvements
- Performance optimizations

## 📖 Resources

### Fortran Resources
- [Modern Fortran Explained](https://global.oup.com/academic/product/modern-fortran-explained-9780198811893)
- [Fortran Wiki](http://fortranwiki.org/)
- [Fortran-lang.org](https://fortran-lang.org/)

### AI/ML Resources
- [Deep Learning Book](https://www.deeplearningbook.org/) by Goodfellow, Bengio, and Courville
- [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/) by Michael Nielsen
- [Stanford CS231n](http://cs231n.stanford.edu/) - Convolutional Neural Networks

### Scientific Computing
- [Numerical Recipes in Fortran](http://numerical.recipes/)
- [LAPACK Documentation](http://www.netlib.org/lapack/)
- [BLAS Reference](http://www.netlib.org/blas/)

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Created as part of the Data Engineering learning journey.

## 🌟 Acknowledgments

- The Fortran community for continued language development
- Scientific computing pioneers who proved Fortran's capabilities
- All contributors to open-source Fortran libraries

---

**Happy Coding! 🚀**

Start your journey from Zero to Expert in Fortran AI today!
