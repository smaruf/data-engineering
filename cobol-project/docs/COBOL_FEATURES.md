# COBOL Features Guide

This document describes the COBOL features demonstrated in this project.

## Table of Contents
1. [Program Structure](#program-structure)
2. [Data Division](#data-division)
3. [Procedure Division](#procedure-division)
4. [File Handling](#file-handling)
5. [String Operations](#string-operations)
6. [Advanced Features](#advanced-features)

## Program Structure

A COBOL program consists of four main divisions:

### 1. IDENTIFICATION DIVISION
Contains program metadata:
- `PROGRAM-ID`: Unique program identifier
- `AUTHOR`: Program author
- `DATE-WRITTEN`: Creation date

```cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. MY-PROGRAM.
AUTHOR. MUHAMMAD SHAMSUL MARUF.
DATE-WRITTEN. 2026-01-26.
```

### 2. ENVIRONMENT DIVISION
Defines the environment and files:
- `INPUT-OUTPUT SECTION`: File declarations
- `FILE-CONTROL`: File assignments

```cobol
ENVIRONMENT DIVISION.
INPUT-OUTPUT SECTION.
FILE-CONTROL.
    SELECT INPUT-FILE
        ASSIGN TO "input.txt"
        ORGANIZATION IS LINE SEQUENTIAL.
```

### 3. DATA DIVISION
Defines all data structures:
- `FILE SECTION`: File record layouts
- `WORKING-STORAGE SECTION`: Variables
- `LINKAGE SECTION`: Parameters

```cobol
DATA DIVISION.
WORKING-STORAGE SECTION.
01  EMPLOYEE-NAME    PIC X(30).
01  EMPLOYEE-SALARY  PIC 9(7)V99.
```

### 4. PROCEDURE DIVISION
Contains the executable logic:
- Paragraphs and sections
- Statements and commands

```cobol
PROCEDURE DIVISION.
MAIN-PROCEDURE.
    DISPLAY "Hello, World!".
    STOP RUN.
```

## Data Division

### PIC Clauses (Picture Clauses)

Define data types and sizes:

| Type | Description | Example |
|------|-------------|---------|
| `9` | Numeric digit | `PIC 9(5)` = 5 digits |
| `X` | Alphanumeric | `PIC X(20)` = 20 characters |
| `A` | Alphabetic | `PIC A(10)` = 10 letters |
| `V` | Decimal point | `PIC 9(5)V99` = 5 digits + 2 decimals |
| `S` | Signed numeric | `PIC S9(5)` = signed 5 digits |

### Level Numbers

Organize data hierarchically:

```cobol
01  EMPLOYEE-RECORD.
    05  EMP-ID         PIC 9(6).
    05  EMP-NAME       PIC X(30).
    05  EMP-ADDRESS.
        10  STREET     PIC X(40).
        10  CITY       PIC X(20).
        10  ZIP        PIC 9(5).
```

### OCCURS Clause (Arrays)

Define repeating data:

```cobol
01  SALES-TABLE.
    05  SALES-RECORD OCCURS 12 TIMES.
        10  MONTH      PIC X(10).
        10  AMOUNT     PIC 9(8)V99.
```

## Procedure Division

### Basic Statements

#### MOVE
Assign values to variables:

```cobol
MOVE "John Doe" TO EMPLOYEE-NAME.
MOVE 50000 TO SALARY.
MOVE SPACES TO ADDRESS.
MOVE ZERO TO COUNTER.
```

#### DISPLAY
Output to screen:

```cobol
DISPLAY "Hello, World!".
DISPLAY "Name: " EMPLOYEE-NAME.
DISPLAY "Salary: $" SALARY.
```

#### ACCEPT
Read user input:

```cobol
ACCEPT EMPLOYEE-NAME.
ACCEPT USER-CHOICE.
```

### Arithmetic Operations

```cobol
ADD 10 TO COUNTER.
SUBTRACT 5 FROM TOTAL.
MULTIPLY RATE BY HOURS GIVING SALARY.
DIVIDE TOTAL BY COUNT GIVING AVERAGE.
COMPUTE RESULT = (A + B) * C.
```

### Control Structures

#### IF Statement

```cobol
IF AGE >= 18
    DISPLAY "Adult"
ELSE
    DISPLAY "Minor"
END-IF.

IF SALARY > 50000 AND DEPARTMENT = "IT"
    PERFORM GIVE-BONUS
END-IF.
```

#### EVALUATE (Case/Switch)

```cobol
EVALUATE GRADE
    WHEN "A"
        DISPLAY "Excellent"
    WHEN "B"
        DISPLAY "Good"
    WHEN "C"
        DISPLAY "Average"
    WHEN OTHER
        DISPLAY "Needs Improvement"
END-EVALUATE.
```

#### PERFORM (Loops)

```cobol
* Simple loop
PERFORM PROCESS-RECORD 10 TIMES.

* Conditional loop
PERFORM UNTIL END-OF-FILE
    READ INPUT-FILE
    PERFORM PROCESS-RECORD
END-PERFORM.

* Counter loop
PERFORM VARYING COUNTER FROM 1 BY 1 UNTIL COUNTER > 10
    DISPLAY COUNTER
END-PERFORM.
```

## File Handling

### File Organizations

1. **Sequential**: Records in order
2. **Indexed**: Key-based access
3. **Relative**: Record number access

### File Operations

```cobol
* Open files
OPEN INPUT INPUT-FILE.
OPEN OUTPUT OUTPUT-FILE.
OPEN I-O DATABASE-FILE.

* Read from file
READ INPUT-FILE
    AT END
        SET END-OF-FILE TO TRUE
    NOT AT END
        PERFORM PROCESS-RECORD
END-READ.

* Write to file
WRITE OUTPUT-RECORD.

* Update record (indexed files)
REWRITE CUSTOMER-RECORD.

* Delete record
DELETE CUSTOMER-FILE RECORD.

* Close files
CLOSE INPUT-FILE OUTPUT-FILE.
```

## String Operations

### STRING
Concatenate strings:

```cobol
STRING FIRST-NAME DELIMITED BY SPACES
       " " DELIMITED BY SIZE
       LAST-NAME DELIMITED BY SPACES
    INTO FULL-NAME
END-STRING.
```

### UNSTRING
Split strings:

```cobol
UNSTRING EMAIL-ADDRESS DELIMITED BY "@"
    INTO USERNAME
         DOMAIN
END-UNSTRING.
```

### INSPECT
Search and replace:

```cobol
* Count occurrences
INSPECT TEXT TALLYING COUNTER FOR ALL "A".

* Replace characters
INSPECT TEXT REPLACING ALL "A" BY "B".

* Convert case
INSPECT TEXT
    CONVERTING "abcdefghijklmnopqrstuvwxyz"
            TO "ABCDEFGHIJKLMNOPQRSTUVWXYZ".
```

## Advanced Features

### Condition Names (88 Levels)

```cobol
01  FILE-STATUS        PIC XX.
    88  FILE-OK        VALUE "00".
    88  END-OF-FILE    VALUE "10".
    88  RECORD-ERROR   VALUE "23".

* Usage
IF FILE-OK
    PERFORM PROCESS-RECORD
END-IF.
```

### Intrinsic Functions

```cobol
* String functions
MOVE FUNCTION LENGTH(TEXT) TO TEXT-LENGTH.
MOVE FUNCTION TRIM(TEXT) TO TRIMMED-TEXT.
MOVE FUNCTION UPPER-CASE(TEXT) TO UPPERCASE-TEXT.

* Numeric functions
COMPUTE RESULT = FUNCTION MAX(A, B, C).
COMPUTE RESULT = FUNCTION MIN(A, B, C).
COMPUTE RESULT = FUNCTION SQRT(NUMBER).

* Date functions
ACCEPT CURRENT-DATE FROM DATE YYYYMMDD.
```

### File Status Codes

Common file status values:

| Code | Meaning |
|------|---------|
| 00 | Success |
| 10 | End of file |
| 22 | Duplicate key |
| 23 | Record not found |
| 30 | Permanent error |
| 35 | File not found |

## Best Practices

1. **Naming Conventions**
   - Use descriptive names (max 30 characters)
   - Use hyphens, not underscores
   - Use UPPER-CASE for clarity

2. **Code Organization**
   - Group related paragraphs into sections
   - Use meaningful paragraph names
   - Comment complex logic

3. **Error Handling**
   - Always check file status
   - Use AT END for file reading
   - Validate input data

4. **Performance**
   - Use indexed files for large datasets
   - Minimize file I/O operations
   - Use OCCURS for repetitive data

5. **Maintainability**
   - Keep paragraphs focused and small
   - Use COPY books for shared code
   - Document complex algorithms

## Resources

- [GnuCOBOL Documentation](https://gnucobol.sourceforge.io/)
- [IBM COBOL Language Reference](https://www.ibm.com/docs/en/cobol-zos)
- [COBOL Programming Guide](https://open-cobol.sourceforge.io/)

---

**Last Updated**: 2026-01-26
