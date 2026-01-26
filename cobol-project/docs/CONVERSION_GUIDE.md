# Conversion Guide: Python ↔ COBOL

This guide explains how to use the bidirectional conversion tools and understand the mapping between Python and COBOL.

## Table of Contents
1. [Overview](#overview)
2. [Python to COBOL](#python-to-cobol)
3. [COBOL to Python](#cobol-to-python)
4. [Conversion Mappings](#conversion-mappings)
5. [Limitations](#limitations)
6. [Examples](#examples)

## Overview

The conversion tools provide basic translation between Python and COBOL syntax. They are educational tools designed to:
- Help understand COBOL concepts for Python developers
- Help understand Python concepts for COBOL developers
- Facilitate code migration between languages
- Serve as learning aids

**Note**: These tools provide syntactic conversion but may require manual adjustments for production use.

## Python to COBOL

### Usage

```bash
python converters/python2cobol.py <input.py> [-o output.cob]
```

### What Gets Converted

#### 1. Variable Declarations

**Python:**
```python
name = "John Doe"
age = 30
salary = 50000.50
```

**COBOL:**
```cobol
01  NAME        PIC X(20) VALUE 'John Doe'.
01  AGE         PIC 9(2) VALUE 30.
01  SALARY      PIC 9(5)V99 VALUE 50000.50.
```

#### 2. Print Statements

**Python:**
```python
print("Hello, World!")
print(f"Name: {name}")
```

**COBOL:**
```cobol
DISPLAY "Hello, World!".
DISPLAY "Name: " NAME.
```

#### 3. If Statements

**Python:**
```python
if age >= 18:
    print("Adult")
else:
    print("Minor")
```

**COBOL:**
```cobol
IF AGE >= 18
    DISPLAY "Adult"
ELSE
    DISPLAY "Minor"
END-IF.
```

#### 4. While Loops

**Python:**
```python
while count < 10:
    print(count)
    count += 1
```

**COBOL:**
```cobol
PERFORM UNTIL NOT (COUNT < 10)
    DISPLAY COUNT
    ADD 1 TO COUNT
END-PERFORM.
```

#### 5. For Loops

**Python:**
```python
for i in range(1, 11):
    print(i)
```

**COBOL:**
```cobol
PERFORM VARYING I FROM 1 BY 1 UNTIL I > 10
    DISPLAY I
END-PERFORM.
```

#### 6. Functions

**Python:**
```python
def calculate_bonus(salary):
    bonus = salary * 0.10
    return bonus
```

**COBOL:**
```cobol
CALCULATE-BONUS.
    COMPUTE BONUS = SALARY * 0.10.
    EXIT PARAGRAPH.
```

## COBOL to Python

### Usage

```bash
python converters/cobol2python.py <input.cob> [-o output.py]
```

### What Gets Converted

#### 1. Data Definitions

**COBOL:**
```cobol
01  EMPLOYEE-NAME    PIC X(30) VALUE "JOHN DOE".
01  EMPLOYEE-SALARY  PIC 9(7)V99 VALUE 50000.00.
01  COUNTER          PIC 9(3) VALUE 0.
```

**Python:**
```python
employee_name = "JOHN DOE"
employee_salary = 50000.00
counter = 0
```

#### 2. DISPLAY Statements

**COBOL:**
```cobol
DISPLAY "Employee: " EMPLOYEE-NAME.
DISPLAY "Salary: $" EMPLOYEE-SALARY.
```

**Python:**
```python
print(f"Employee: {employee_name}")
print(f"Salary: ${employee_salary}")
```

#### 3. MOVE Statements

**COBOL:**
```cobol
MOVE "NEW NAME" TO EMPLOYEE-NAME.
MOVE 60000 TO SALARY.
MOVE SPACES TO ADDRESS.
```

**Python:**
```python
employee_name = "NEW NAME"
salary = 60000
address = ""
```

#### 4. IF Statements

**COBOL:**
```cobol
IF AGE >= 18
    DISPLAY "Adult"
ELSE
    DISPLAY "Minor"
END-IF.
```

**Python:**
```python
if age >= 18:
    print(f"Adult")
else:
    print(f"Minor")
```

#### 5. PERFORM Statements

**COBOL:**
```cobol
PERFORM VARYING COUNTER FROM 1 BY 1 UNTIL COUNTER > 10
    DISPLAY COUNTER
END-PERFORM.
```

**Python:**
```python
for counter in range(1, 11, 1):
    print(f"{counter}")
```

#### 6. Paragraphs

**COBOL:**
```cobol
CALCULATE-TOTAL.
    ADD PRICE TO TOTAL.
    DISPLAY "Total: " TOTAL.
```

**Python:**
```python
def calculate_total():
    total += price
    print(f"Total: {total}")
```

## Conversion Mappings

### Data Types

| Python Type | COBOL PIC Clause | Notes |
|-------------|------------------|-------|
| `int` | `PIC 9(n)` | Unsigned integer |
| `int` (negative) | `PIC S9(n)` | Signed integer |
| `float` | `PIC 9(n)V9(m)` | n=integer digits, m=decimal |
| `str` | `PIC X(n)` | Alphanumeric string |
| `bool` | `PIC 9 VALUE 0/1` | 0=False, 1=True |
| `list` | `OCCURS n TIMES` | Fixed-size array |

### Operators

| Python | COBOL | Notes |
|--------|-------|-------|
| `==` | `=` | Equality |
| `!=` | `NOT =` | Inequality |
| `and` | `AND` | Logical AND |
| `or` | `OR` | Logical OR |
| `not` | `NOT` | Logical NOT |
| `+` | `ADD ... TO` | Addition |
| `-` | `SUBTRACT ... FROM` | Subtraction |
| `*` | `MULTIPLY ... BY` | Multiplication |
| `/` | `DIVIDE ... BY` | Division |

### Control Structures

| Python | COBOL | Notes |
|--------|-------|-------|
| `if/elif/else` | `IF/ELSE/END-IF` | Conditional |
| `while` | `PERFORM UNTIL` | Loop with condition |
| `for i in range()` | `PERFORM VARYING` | Counter loop |
| `def function()` | `PARAGRAPH.` | Subroutine |
| `return` | `EXIT PARAGRAPH` | Early exit |

### Naming Conventions

| Python | COBOL | Example |
|--------|-------|---------|
| `snake_case` | `KEBAB-CASE` | `my_variable` → `MY-VARIABLE` |
| lowercase | UPPERCASE | `name` → `NAME` |
| `_` (underscore) | `-` (hyphen) | `employee_id` → `EMPLOYEE-ID` |

## Limitations

### Python to COBOL

1. **Complex Data Structures**: Dictionaries, sets, and nested lists are not directly supported
2. **Object-Oriented Features**: Classes and objects cannot be converted
3. **External Libraries**: Only built-in functions are partially supported
4. **Dynamic Typing**: COBOL requires static type declarations
5. **Exception Handling**: Try/except blocks are not converted
6. **List Comprehensions**: Not supported
7. **Lambda Functions**: Not supported

### COBOL to Python

1. **File I/O**: File handling is simplified in Python conversion
2. **COPY Statements**: External COPY books are not processed
3. **Complex PIC Clauses**: Some advanced PIC clauses may not convert perfectly
4. **CALL Statements**: External program calls are not converted
5. **Sections**: COBOL sections are converted to simple functions
6. **Report Writer**: Special report features are not converted
7. **Intrinsic Functions**: Many COBOL intrinsic functions don't have direct Python equivalents

## Examples

### Example 1: Simple Calculator

**Python Input (`calculator.py`):**
```python
num1 = 10
num2 = 5
result = 0

print("Calculator")
result = num1 + num2
print(f"Result: {result}")

if result > 10:
    print("Large number")
```

**COBOL Output:**
```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. CONVERTED-PROGRAM.

DATA DIVISION.
WORKING-STORAGE SECTION.
01  NUM1        PIC 9(2) VALUE 10.
01  NUM2        PIC 9(1) VALUE 5.
01  RESULT      PIC 9(1) VALUE 0.

PROCEDURE DIVISION.
MAIN-PROCEDURE.
    DISPLAY "Calculator".
    COMPUTE RESULT = NUM1 + NUM2.
    DISPLAY "Result: " RESULT.
    IF RESULT > 10
        DISPLAY "Large number"
    END-IF.
    STOP RUN.
```

### Example 2: Employee Report

**COBOL Input:**
```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. EMP-REPORT.

DATA DIVISION.
WORKING-STORAGE SECTION.
01  EMP-NAME     PIC X(30) VALUE "JOHN DOE".
01  EMP-SALARY   PIC 9(7)V99 VALUE 50000.00.
01  BONUS        PIC 9(7)V99.

PROCEDURE DIVISION.
MAIN-PROCEDURE.
    DISPLAY "Employee Report".
    DISPLAY "Name: " EMP-NAME.
    COMPUTE BONUS = EMP-SALARY * 0.10.
    DISPLAY "Bonus: " BONUS.
    STOP RUN.
```

**Python Output:**
```python
#!/usr/bin/env python3

# Data Division - Variable Declarations
emp_name = "JOHN DOE"
emp_salary = 50000.00
bonus = 0.0

# Procedure Division
def main():
    print(f"Employee Report")
    print(f"Name: {emp_name}")
    bonus = emp_salary * 0.10
    print(f"Bonus: {bonus}")

if __name__ == "__main__":
    main()
```

## Testing Conversions

### Test Python to COBOL Converter

```bash
python converters/python2cobol.py --test
```

### Test COBOL to Python Converter

```bash
python converters/cobol2python.py --test
```

### Convert Your Own Code

```bash
# Python to COBOL
python converters/python2cobol.py mycode.py -o mycode.cob

# COBOL to Python
python converters/cobol2python.py mycode.cob -o mycode.py
```

## Best Practices

1. **Start Simple**: Begin with simple programs before converting complex code
2. **Review Output**: Always review and test the converted code
3. **Manual Adjustments**: Be prepared to make manual adjustments
4. **Understand Both Languages**: Familiarize yourself with both Python and COBOL
5. **Test Thoroughly**: Test converted code with various inputs
6. **Comment Your Code**: Add comments to clarify conversion decisions
7. **Incremental Conversion**: Convert and test in small increments

## Tips for Success

### For Python Developers Learning COBOL

- COBOL is verbose but explicit
- Fixed column format matters (columns 1-6 for line numbers, 7 for comments, 8-72 for code)
- COBOL has strict typing
- File handling is very different
- Period (.) is a statement terminator

### For COBOL Developers Learning Python

- Python is concise and implicit
- Indentation defines code blocks
- Python is dynamically typed
- Python has rich built-in data structures
- No statement terminators needed

## Resources

- [Python Official Documentation](https://docs.python.org/)
- [GnuCOBOL Documentation](https://gnucobol.sourceforge.io/)
- [COBOL Standards](https://www.ibm.com/docs/en/cobol-zos)

---

**Last Updated**: 2026-01-26
