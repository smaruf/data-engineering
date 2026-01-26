# Production-Ready COBOL Project

A comprehensive COBOL project demonstrating various COBOL features and bidirectional conversion tools between Python and COBOL.

## 📋 Project Overview

This project includes:
- **Production-ready COBOL programs** showcasing different COBOL features
- **Python to COBOL converter** - Convert Python code to COBOL
- **COBOL to Python converter** - Convert COBOL code to Python
- **Example programs** demonstrating conversion capabilities
- **Documentation** and best practices

## 🏗️ Project Structure

```
cobol-project/
├── src/                        # COBOL source programs
│   ├── file-io.cob            # File I/O operations
│   ├── data-validation.cob    # Data validation routines
│   ├── report-generator.cob   # Report generation
│   ├── database-handler.cob   # Database operations (indexed files)
│   └── string-processor.cob   # String manipulation
├── converters/                 # Conversion tools
│   ├── python2cobol.py        # Python to COBOL converter
│   ├── cobol2python.py        # COBOL to Python converter
│   └── converter_utils.py     # Common utilities
├── examples/                   # Example programs
│   ├── python/                # Python examples
│   └── cobol/                 # COBOL examples
├── data/                      # Data files
│   ├── input/                 # Input data files
│   └── output/                # Output data files
├── scripts/                   # Build and utility scripts
│   ├── compile.sh            # Compile COBOL programs
│   └── run_tests.sh          # Run test programs
├── docs/                      # Documentation
│   ├── COBOL_FEATURES.md     # COBOL features guide
│   └── CONVERSION_GUIDE.md   # Conversion guide
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- **GnuCOBOL** (Open COBOL compiler) - for compiling COBOL programs
- **Python 3.8+** - for conversion tools
- **Bash** - for running scripts

### Installation

1. **Install GnuCOBOL** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install gnucobol
   ```

2. **Verify installation**:
   ```bash
   cobc --version
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 COBOL Programs

### 1. File I/O Program (`file-io.cob`)
Demonstrates:
- Sequential file reading and writing
- Record processing
- File error handling
- Data validation

### 2. Data Validation Program (`data-validation.cob`)
Demonstrates:
- Input validation
- Numeric checks
- Date validation
- Data type validation

### 3. Report Generator (`report-generator.cob`)
Demonstrates:
- Formatted output
- Page headers and footers
- Column alignment
- Summary calculations

### 4. Database Handler (`database-handler.cob`)
Demonstrates:
- Indexed file organization
- Record CRUD operations
- Key-based searching
- Sequential and random access

### 5. String Processor (`string-processor.cob`)
Demonstrates:
- String manipulation functions
- Text parsing
- Pattern matching
- Character operations

## 🔄 Conversion Tools

### Python to COBOL Converter

Convert Python code to COBOL:
```bash
python converters/python2cobol.py examples/python/sample.py -o output.cob
```

**Features:**
- Variable declarations mapping
- Control structures (if, while, for)
- Function to procedure conversion
- Data type mapping
- File I/O operations

### COBOL to Python Converter

Convert COBOL code to Python:
```bash
python converters/cobol2python.py src/file-io.cob -o output.py
```

**Features:**
- Division parsing (IDENTIFICATION, DATA, PROCEDURE)
- Variable definition extraction
- Procedure to function conversion
- COBOL syntax to Python translation
- Data structure mapping

## 🛠️ Usage Examples

### Compiling COBOL Programs

Compile all programs:
```bash
./scripts/compile.sh
```

Compile specific program:
```bash
cobc -x src/file-io.cob -o bin/file-io
```

### Running COBOL Programs

```bash
./bin/file-io
./bin/data-validation
./bin/report-generator
```

### Using Converters

**Convert Python to COBOL:**
```bash
python converters/python2cobol.py examples/python/calculator.py
```

**Convert COBOL to Python:**
```bash
python converters/cobol2python.py src/string-processor.cob
```

## 📝 COBOL Features Demonstrated

1. **Data Division**
   - WORKING-STORAGE SECTION
   - FILE SECTION
   - LINKAGE SECTION

2. **Procedure Division**
   - PERFORM statements
   - CALL statements
   - Conditional logic (IF, EVALUATE)

3. **File Handling**
   - Sequential files
   - Indexed files
   - Line sequential files

4. **Data Manipulation**
   - MOVE statements
   - STRING/UNSTRING
   - INSPECT
   - Arithmetic operations

5. **Program Structure**
   - Paragraphs and sections
   - Subroutines
   - Copy books (potential enhancement)

## 🧪 Testing

Run conversion tests:
```bash
python -m pytest tests/
```

Test individual converters:
```bash
python converters/python2cobol.py --test
python converters/cobol2python.py --test
```

## 📊 Conversion Mapping

### Data Types
| Python | COBOL |
|--------|-------|
| int | PIC 9(n) |
| float | PIC 9(n)V9(m) |
| str | PIC X(n) |
| bool | PIC 9 VALUE 0/1 |
| list | OCCURS clause |

### Control Structures
| Python | COBOL |
|--------|-------|
| if/elif/else | IF/ELSE/END-IF |
| while | PERFORM UNTIL |
| for | PERFORM VARYING |
| def | PARAGRAPH |

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

This project is part of the Data Engineering Learning Journey.

## 📞 Support

For questions and support:
- Create an issue in the repository
- Contact: Muhammad Shamsul Maruf

---

**Built with ❤️ to bridge legacy and modern programming**
