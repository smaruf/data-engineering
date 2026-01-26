# Makefile for Fortran AI Project
# Builds all examples from beginner to advanced levels

# Compiler settings
FC = gfortran
FFLAGS = -O2 -Wall -std=f2008
DEBUGFLAGS = -g -fbacktrace -fcheck=all
BINDIR = bin
SRCDIR = src

# Targets
.PHONY: all clean beginner intermediate advanced applications examples help test ml

all: beginner examples

help:
	@echo "Fortran AI Build System"
	@echo "======================="
	@echo "Available targets:"
	@echo "  all          - Build beginner and examples"
	@echo "  beginner     - Build beginner examples"
	@echo "  intermediate - Build intermediate examples"
	@echo "  advanced     - Build advanced examples"
	@echo "  applications - Build real-world applications"
	@echo "  examples     - Build complete examples"
	@echo "  ml           - Build machine learning examples"
	@echo "  clean        - Remove all built files"
	@echo "  test         - Run basic tests"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Usage: make [target]"
	@echo "Example: make beginner"

# Create bin directory
$(BINDIR):
	mkdir -p $(BINDIR)

# Beginner Level
beginner: $(BINDIR) \
	$(BINDIR)/hello_ai \
	$(BINDIR)/ai_learning_fundamentals \
	$(BINDIR)/linear_regression \
	$(BINDIR)/perceptron \
	$(BINDIR)/logistic_regression

$(BINDIR)/hello_ai: $(SRCDIR)/01-beginner/hello_ai.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: hello_ai"

$(BINDIR)/ai_learning_fundamentals: $(SRCDIR)/01-beginner/ai_learning_fundamentals.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: ai_learning_fundamentals"

$(BINDIR)/linear_regression: $(SRCDIR)/01-beginner/linear_regression.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: linear_regression"

$(BINDIR)/perceptron: $(SRCDIR)/01-beginner/perceptron.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: perceptron"

$(BINDIR)/logistic_regression: $(SRCDIR)/01-beginner/logistic_regression.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: logistic_regression"

# Intermediate Level - Neural Networks
intermediate: $(BINDIR) \
	$(BINDIR)/gradient_descent \
	$(BINDIR)/backpropagation \
	$(BINDIR)/neural_network

$(BINDIR)/gradient_descent: $(SRCDIR)/02-intermediate/gradient_descent.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: gradient_descent"

$(BINDIR)/backpropagation: $(SRCDIR)/02-intermediate/backpropagation.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: backpropagation"

$(BINDIR)/neural_network: $(SRCDIR)/02-intermediate/neural_network.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: neural_network"

# Advanced Level - Deep Learning
advanced: $(BINDIR) \
	$(BINDIR)/deep_neural_network \
	$(BINDIR)/gan_network \
	$(BINDIR)/optimizer_adam

$(BINDIR)/deep_neural_network: $(SRCDIR)/03-advanced/deep_neural_network.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: deep_neural_network"

$(BINDIR)/gan_network: $(SRCDIR)/03-advanced/gan_network.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: gan_network"

$(BINDIR)/optimizer_adam: $(SRCDIR)/03-advanced/optimizer_adam.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: optimizer_adam"

# Applications - Real-world ML
applications: $(BINDIR) $(BINDIR)/market_predictor

$(BINDIR)/market_predictor: $(SRCDIR)/04-applications/market_predictor.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: market_predictor"

# Machine Learning target - builds all ML examples including advanced techniques
ml: beginner intermediate advanced applications examples
	@echo "======================================"
	@echo "All Machine Learning examples built!"
	@echo "======================================"
	@echo "Beginner: AI Learning Fundamentals, Linear Regression, Perceptron, Logistic Regression"
	@echo "Intermediate: Gradient Descent, Backpropagation, Neural Networks"
	@echo "Advanced: Deep NN, GAN, ADAM Optimizer"
	@echo "Applications: Market Predictor (Time Series)"
	@echo "======================================"

# Examples
examples: $(BINDIR) $(BINDIR)/example_01_simple_nn

$(BINDIR)/example_01_simple_nn: $(SRCDIR)/utils/math_utils.f90 examples/example_01_simple_nn.f90
	$(FC) $(FFLAGS) -J$(BINDIR) -o $@ $^
	@echo "Built: example_01_simple_nn"

# Clean
clean:
	rm -rf $(BINDIR)
	rm -f *.mod *.o
	@echo "Cleaned build artifacts"

# Test - Run all beginner programs
test: beginner
	@echo "Running beginner tests..."
	@echo "========================="
	@echo ""
	@echo "Test 1: Hello AI"
	@echo "----------------"
	@./$(BINDIR)/hello_ai
	@echo ""
	@echo "Test 2: Linear Regression"
	@echo "-------------------------"
	@./$(BINDIR)/linear_regression
	@echo ""
	@echo "Test 3: Perceptron"
	@echo "------------------"
	@./$(BINDIR)/perceptron
	@echo ""
	@echo "Test 4: Logistic Regression"
	@echo "---------------------------"
	@./$(BINDIR)/logistic_regression
	@echo ""
	@echo "All tests completed successfully!"
