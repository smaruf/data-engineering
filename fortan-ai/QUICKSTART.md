# Quick Start Guide

Get started with Fortran AI in 5 minutes!

## Prerequisites

You need a Fortran compiler installed. Check if you have it:

```bash
gfortran --version
```

If not installed, install it:

**Ubuntu/Debian:**
```bash
sudo apt-get install gfortran make
```

**macOS:**
```bash
brew install gcc make
```

**Windows:**
Use WSL (Windows Subsystem for Linux) or MinGW-w64

## 5-Minute Quick Start

### Step 1: Navigate to the project
```bash
cd fortan-ai
```

### Step 2: Build all beginner examples
```bash
make beginner
```

### Step 3: Run your first AI program!
```bash
./bin/hello_ai
```

### Step 4: Try other examples

**Linear Regression:**
```bash
./bin/linear_regression
```

**Perceptron (learns AND gate):**
```bash
./bin/perceptron
```

**Logistic Regression:**
```bash
./bin/logistic_regression
```

**Complete Neural Network (XOR problem):**
```bash
make examples
./bin/example_01_simple_nn
```

## What's Next?

### Learn the Theory
Read the documentation in order:
1. `docs/01-introduction.md` - Overview and motivation
2. `docs/02-basics.md` - Fortran refresher
3. `docs/03-linear-algebra.md` - Mathematical foundations
4. `docs/04-neural-networks.md` - Neural network theory
5. `docs/05-optimization.md` - Training algorithms
6. `docs/06-advanced-topics.md` - Advanced techniques

### Explore the Code
1. **Beginner** (`src/01-beginner/`) - Start here
   - `hello_ai.f90` - Basic concepts
   - `linear_regression.f90` - First ML algorithm
   - `perceptron.f90` - Single neuron
   - `logistic_regression.f90` - Classification

2. **Examples** (`examples/`) - Complete implementations
   - `example_01_simple_nn.f90` - Full neural network

3. **Utilities** (`src/utils/`) - Reusable modules
   - `matrix_ops.f90` - Linear algebra
   - `math_utils.f90` - Activation functions

### Customize and Experiment
- Modify the XOR network to solve different problems
- Adjust learning rates and network sizes
- Add more layers to the neural network
- Create your own datasets in `data/`

## Learning Path

**Week 1-2: Foundations**
- Run all beginner examples
- Read docs 01-03
- Understand linear regression and perceptron

**Week 3-4: Neural Networks**
- Study the neural network example
- Read docs 04-05
- Implement your own network from scratch

**Week 5-6: Advanced Topics**
- Read doc 06
- Experiment with different architectures
- Optimize for performance

**Week 7-8: Projects**
- Work with real datasets
- Build a complete classifier
- Share your results!

## Troubleshooting

**Compilation errors?**
- Make sure you have gfortran 9.0+
- Check that all files are in the correct directories

**Programs not running?**
- Build with: `make clean && make all`
- Check permissions: `chmod +x bin/*`

**Want to see all options?**
```bash
make help
```

## Getting Help

- Read the full `README.md` for detailed information
- Check documentation in `docs/` directory
- Review example code for implementation patterns
- Modify examples to learn by experimentation

## Key Commands Summary

```bash
# Build everything
make all

# Build specific level
make beginner

# Run tests
make test

# Clean and rebuild
make clean && make all

# See all options
make help
```

## Your First Modification

Try this: Open `src/01-beginner/hello_ai.f90` and change the house features:

```fortran
features = [2000.0, 4.0, 5.0]  ! Larger house, newer
```

Rebuild and run:
```bash
make clean && make beginner
./bin/hello_ai
```

See how the prediction changes!

---

**Congratulations! You're now ready to explore Fortran AI!** 🎉

Start with the beginner examples and work your way up. Happy coding!
