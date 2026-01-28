# Quick Start Guide

Get up and running with the Basic Statistics project in minutes!

## Prerequisites

- **Python 3.8+**
- **gfortran** (GCC Fortran compiler)
- **pip** (Python package manager)
- *Optional*: Docker for containerized deployment

## Installation

### Option 1: Local Installation (Recommended for Learning)

```bash
# Navigate to the project
cd basic-statistics

# Install Python dependencies
pip install -r requirements.txt

# Build Fortran modules
make fortran

# Run tests to verify installation
make test
```

### Option 2: Docker (Recommended for Production)

```bash
# Build and start containers
cd docker
docker-compose up -d

# Access Jupyter Lab
# Open browser: http://localhost:8888

# Access API
# Open browser: http://localhost:8001
```

## Quick Examples

### 1. Python: Descriptive Statistics

```python
from src.python.descriptive import CentralTendency, Dispersion, Shape

# Your data
data = [23, 45, 12, 67, 34, 89, 23, 45, 67]

# Central tendency
print(f"Mean: {CentralTendency.mean(data)}")
print(f"Median: {CentralTendency.median(data)}")

# Dispersion
print(f"Std Dev: {Dispersion.std_dev(data)}")
print(f"IQR: {Dispersion.iqr(data)}")

# Shape
print(f"Skewness: {Shape.skewness(data)}")
print(f"Kurtosis: {Shape.kurtosis(data)}")
```

### 2. Python: Probability Distributions

```python
from src.python.probability import Distributions

# Normal distribution
pdf = Distributions.Normal.pdf(0, mu=0, sigma=1)
cdf = Distributions.Normal.cdf(1.96, mu=0, sigma=1)
print(f"N(0,1) PDF at x=0: {pdf}")
print(f"N(0,1) CDF at x=1.96: {cdf}")

# Generate random samples
samples = Distributions.Normal.rvs(mu=100, sigma=15, size=1000)
print(f"Generated {len(samples)} random samples")
```

### 3. Fortran: High-Performance Computing

```bash
# Compile and run Fortran test
make fortran
./bin/test_stats
```

### 4. Run Examples

```bash
# Descriptive statistics example
cd examples
python descriptive_stats_example.py

# Probability distributions
python distributions_example.py

# A/B testing use case
cd use_cases
python ab_testing.py
```

## Learning Path

### Day 1: Basics
1. Read [Theory: Descriptive Statistics](docs/theory/01-descriptive-stats.md)
2. Run Python example: `descriptive_stats_example.py`
3. Complete exercises in examples/notebooks (if available)

### Day 2: Probability
1. Read [Theory: Probability](docs/theory/02-probability-theory.md)
2. Run: `distributions_example.py`
3. Experiment with different distributions

### Day 3: Real Applications
1. Study A/B testing use case
2. Explore big data examples with Spark
3. Try the API service

### Week 2: Production
1. Learn Docker deployment
2. Explore Fortran performance benefits
3. Build your own statistical application

## Testing Your Installation

### Quick Test
```bash
python -c "
from src.python.descriptive import CentralTendency
print('Mean of [1,2,3,4,5]:', CentralTendency.mean([1,2,3,4,5]))
print('✓ Installation successful!')
"
```

### Full Test Suite
```bash
# Python tests
pytest tests/python/ -v

# Fortran test
./bin/test_stats
```

## Using the API

### Start the API Server
```bash
# Using uvicorn directly
uvicorn api.main:app --reload

# Or using Docker
docker-compose up stats-api
```

### Make API Requests
```bash
# Health check
curl http://localhost:8000/health

# Compute statistics
curl -X POST http://localhost:8000/stats/descriptive \
  -H "Content-Type: application/json" \
  -d '{"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}'

# Compute mean only
curl -X POST http://localhost:8000/stats/mean \
  -H "Content-Type: application/json" \
  -d '{"data": [23, 45, 12, 67, 34]}'
```

## Common Tasks

### Build Everything
```bash
make all
```

### Clean Build Artifacts
```bash
make clean
```

### Run Benchmarks
```bash
make benchmark
```

### Build Documentation
```bash
make docs
```

## Project Structure Quick Reference

```
basic-statistics/
├── src/
│   ├── python/          # Python implementations
│   └── fortran/         # Fortran implementations
├── examples/            # Learning examples
│   ├── *.py            # Standalone examples
│   └── use_cases/      # Real-world scenarios
├── tests/              # Test suites
├── docs/               # Documentation
│   ├── theory/         # Statistical theory
│   ├── implementation/ # How-to guides
│   └── data-engineering/  # Big data integration
├── api/                # REST API service
└── docker/             # Docker deployment
```

## Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: See `examples/` directory
- **Tests**: Look at `tests/` for usage patterns
- **Issues**: Open an issue on GitHub

## Next Steps

1. ✅ Installation complete? → Try running examples
2. 📚 Want to learn? → Read theory docs
3. 🏭 Need production? → Use Docker
4. 🚀 Want speed? → Try Fortran implementation
5. 📊 Big data? → Check Spark examples

## Performance Tips

### For Small Datasets (< 10K records)
- Use Python implementation
- Direct NumPy operations are fine

### For Medium Datasets (10K - 1M records)
- Use Python with NumPy
- Consider Fortran for repeated computations

### For Large Datasets (> 1M records)
- Use Fortran for core computations
- Use Spark for distributed computing
- Consider streaming algorithms

## Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"
```bash
pip install -r requirements.txt
```

### "gfortran: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install gfortran

# macOS
brew install gcc
```

### Fortran build errors
```bash
# Clean and rebuild
make clean
make fortran
```

## What's Next?

- Explore [Big Data Integration](docs/data-engineering/big-data-stats.md)
- Try [A/B Testing Use Case](examples/use_cases/ab_testing.py)
- Build your own statistical application
- Contribute to the project!

---

**Happy Learning! 📊🚀**

Master statistics from theory to production!
