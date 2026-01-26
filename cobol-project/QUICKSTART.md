# COBOL Project Quick Start Guide

Get started with the COBOL project in 5 minutes!

## Prerequisites

### Required
- **Python 3.8+** - For running converters

### Optional (for compiling COBOL)
- **GnuCOBOL** - Open-source COBOL compiler

## Quick Installation

### Install GnuCOBOL (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install gnucobol
```

### Install GnuCOBOL (macOS)

```bash
brew install gnucobol
```

### Install GnuCOBOL (Windows)

Download from: https://sourceforge.net/projects/gnucobol/

## Quick Test

### 1. Test the Converters

```bash
cd cobol-project/converters

# Test Python to COBOL
python3 python2cobol.py --test

# Test COBOL to Python
python3 cobol2python.py --test
```

### 2. Convert Example Programs

**Python to COBOL:**
```bash
python3 python2cobol.py ../examples/python/calculator.py -o /tmp/calculator.cob
cat /tmp/calculator.cob
```

**COBOL to Python:**
```bash
python3 cobol2python.py ../examples/cobol/hello-world.cob -o /tmp/hello.py
python3 /tmp/hello.py
```

### 3. Run Test Suite

```bash
cd cobol-project/scripts
./run_tests.sh
```

## Compile COBOL Programs (Optional)

If you have GnuCOBOL installed:

```bash
cd cobol-project/scripts
./compile.sh
```

This will compile all COBOL programs in the `src/` directory.

## Run COBOL Programs

After compilation:

```bash
cd cobol-project

# Run data validation
./bin/data-validation

# Run string processor
./bin/string-processor

# Run report generator
./bin/report-generator
```

## Convert Your Own Code

### Python to COBOL

```bash
# Create a Python file
cat > myprogram.py << 'EOL'
name = "John Doe"
age = 30

print(f"Name: {name}")
print(f"Age: {age}")

if age >= 18:
    print("Adult")
EOL

# Convert it
python3 converters/python2cobol.py myprogram.py -o myprogram.cob

# View the result
cat myprogram.cob
```

### COBOL to Python

```bash
# Convert a COBOL program
python3 converters/cobol2python.py src/data-validation.cob -o validation.py

# Run the converted Python code
python3 validation.py
```

## Explore COBOL Programs

The `src/` directory contains 5 production-ready COBOL programs:

1. **file-io.cob** - File I/O operations
2. **data-validation.cob** - Data validation routines
3. **report-generator.cob** - Report generation
4. **database-handler.cob** - Database operations (indexed files)
5. **string-processor.cob** - String manipulation

Each demonstrates different COBOL features!

## Learn More

- Read [README.md](README.md) for complete documentation
- Check [docs/COBOL_FEATURES.md](docs/COBOL_FEATURES.md) for COBOL features guide
- See [docs/CONVERSION_GUIDE.md](docs/CONVERSION_GUIDE.md) for conversion details

## Common Issues

### "cobc: command not found"

GnuCOBOL is not installed. You can still use the converters without compiling COBOL.

### "Permission denied" when running scripts

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### Conversion doesn't work perfectly

The converters are educational tools and may require manual adjustments for complex code.

## Next Steps

1. **Read the documentation** in `docs/`
2. **Modify example programs** in `examples/`
3. **Create your own programs** and test conversions
4. **Explore COBOL features** in `src/` programs

Happy coding! 🚀
