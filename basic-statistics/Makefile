# ============================================================================
# Makefile for Basic Statistics Project
# Builds both Python and Fortran components
# ============================================================================

# Fortran compiler
FC = gfortran
FFLAGS = -O3 -Wall -std=f2008
LDFLAGS = 

# Directories
SRC_DIR = src/fortran
BUILD_DIR = build
BIN_DIR = bin

# Source files
MODULES = $(SRC_DIR)/descriptive_stats.f90 $(SRC_DIR)/probability.f90
MAIN = $(SRC_DIR)/test_stats.f90

# Object files
OBJS = $(patsubst $(SRC_DIR)/%.f90,$(BUILD_DIR)/%.o,$(MODULES))

# Executables
EXEC = $(BIN_DIR)/test_stats

# Python
PYTHON = python3
PIP = pip3

.PHONY: all clean fortran python test install help

# Default target
all: fortran

# ============================================================================
# Fortran Targets
# ============================================================================

fortran: $(EXEC)

$(EXEC): $(OBJS) $(BUILD_DIR)/test_stats.o | $(BIN_DIR)
	$(FC) $(FFLAGS) $(OBJS) $(BUILD_DIR)/test_stats.o -o $(EXEC) $(LDFLAGS)
	@echo "Fortran build complete: $(EXEC)"

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.f90 | $(BUILD_DIR)
	$(FC) $(FFLAGS) -c $< -o $@

# Create directories
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# ============================================================================
# Python Targets
# ============================================================================

python: install

install:
	$(PIP) install -r requirements.txt
	@echo "Python dependencies installed"

# ============================================================================
# Testing
# ============================================================================

test: test-python test-fortran

test-python:
	$(PYTHON) -m pytest tests/python/ -v

test-fortran: $(EXEC)
	@echo "Running Fortran tests..."
	./$(EXEC)

# ============================================================================
# Benchmarks
# ============================================================================

benchmark:
	$(PYTHON) benchmarks/python_vs_fortran.py

# ============================================================================
# Documentation
# ============================================================================

docs:
	@echo "Building documentation..."
	cd docs && make html

# ============================================================================
# Cleanup
# ============================================================================

clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(BIN_DIR)
	rm -f *.mod
	rm -rf __pycache__
	rm -rf src/python/**/__pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete
	@echo "Clean complete"

# ============================================================================
# Help
# ============================================================================

help:
	@echo "Basic Statistics Project - Makefile Help"
	@echo "========================================"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Build everything (default: fortran)"
	@echo "  fortran      - Build Fortran modules and test program"
	@echo "  python       - Install Python dependencies"
	@echo "  install      - Install Python dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-python  - Run Python tests"
	@echo "  test-fortran - Run Fortran test program"
	@echo "  benchmark    - Run performance benchmarks"
	@echo "  docs         - Build documentation"
	@echo "  clean        - Remove build artifacts"
	@echo "  help         - Show this help message"
	@echo ""
