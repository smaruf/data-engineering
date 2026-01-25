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
	$(BINDIR)/linear_regression \
	$(BINDIR)/perceptron \
	$(BINDIR)/logistic_regression

$(BINDIR)/hello_ai: $(SRCDIR)/01-beginner/hello_ai.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: hello_ai"

$(BINDIR)/linear_regression: $(SRCDIR)/01-beginner/linear_regression.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: linear_regression"

$(BINDIR)/perceptron: $(SRCDIR)/01-beginner/perceptron.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: perceptron"

$(BINDIR)/logistic_regression: $(SRCDIR)/01-beginner/logistic_regression.f90
	$(FC) $(FFLAGS) -o $@ $<
	@echo "Built: logistic_regression"

# Intermediate Level (placeholder for now)
intermediate: $(BINDIR)
	@echo "Intermediate examples ready to build"

# Advanced Level (placeholder for now)
advanced: $(BINDIR)
	@echo "Advanced examples ready to build"

# Applications (placeholder for now)
applications: $(BINDIR)
	@echo "Applications ready to build"

# Machine Learning target - builds ML-focused examples
ml: beginner examples
	@echo "Machine Learning examples built successfully!"

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
