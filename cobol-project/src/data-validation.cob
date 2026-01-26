       IDENTIFICATION DIVISION.
       PROGRAM-ID. DATA-VALIDATION.
       AUTHOR. MUHAMMAD SHAMSUL MARUF.
       DATE-WRITTEN. 2026-01-26.
      *****************************************************************
      * DATA VALIDATION DEMONSTRATION                                 *
      * This program demonstrates:                                    *
      * - Input validation                                            *
      * - Numeric checks                                              *
      * - Date validation                                             *
      * - Data type validation                                        *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  TEST-DATA.
           05  TEST-NUMBER         PIC 9(5) VALUE 12345.
           05  TEST-DECIMAL        PIC 9(3)V99 VALUE 123.45.
           05  TEST-STRING         PIC X(20) VALUE "HELLO WORLD".
           05  TEST-DATE           PIC 9(8) VALUE 20260126.
       
       01  VALIDATION-RESULTS.
           05  NUMERIC-VALID       PIC 9 VALUE 0.
           05  DECIMAL-VALID       PIC 9 VALUE 0.
           05  STRING-VALID        PIC 9 VALUE 0.
           05  DATE-VALID          PIC 9 VALUE 0.
       
       01  DATE-FIELDS.
           05  YEAR                PIC 9(4).
           05  MONTH               PIC 9(2).
           05  DAY                 PIC 9(2).
       
       01  USER-INPUT              PIC X(50).
       01  NUMERIC-TEST            PIC 9(10).
       01  ALPHA-TEST              PIC A(20).
       
       01  VALIDATION-COUNT        PIC 9(3) VALUE 0.
       01  PASS-COUNT              PIC 9(3) VALUE 0.
       01  FAIL-COUNT              PIC 9(3) VALUE 0.
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY "===== DATA VALIDATION SYSTEM ====="
           DISPLAY " "
           
           PERFORM TEST-NUMERIC-VALIDATION
           PERFORM TEST-DECIMAL-VALIDATION
           PERFORM TEST-STRING-VALIDATION
           PERFORM TEST-DATE-VALIDATION
           PERFORM TEST-RANGE-VALIDATION
           PERFORM TEST-FORMAT-VALIDATION
           
           PERFORM DISPLAY-RESULTS
           STOP RUN.
       
       TEST-NUMERIC-VALIDATION.
           DISPLAY "1. Testing Numeric Validation..."
           ADD 1 TO VALIDATION-COUNT
           
           IF TEST-NUMBER IS NUMERIC
               MOVE 1 TO NUMERIC-VALID
               ADD 1 TO PASS-COUNT
               DISPLAY "   PASS: " TEST-NUMBER " is numeric"
           ELSE
               MOVE 0 TO NUMERIC-VALID
               ADD 1 TO FAIL-COUNT
               DISPLAY "   FAIL: Value is not numeric"
           END-IF
           DISPLAY " ".
       
       TEST-DECIMAL-VALIDATION.
           DISPLAY "2. Testing Decimal Validation..."
           ADD 1 TO VALIDATION-COUNT
           
           IF TEST-DECIMAL IS NUMERIC AND TEST-DECIMAL > 0
               MOVE 1 TO DECIMAL-VALID
               ADD 1 TO PASS-COUNT
               DISPLAY "   PASS: " TEST-DECIMAL " is valid decimal"
           ELSE
               MOVE 0 TO DECIMAL-VALID
               ADD 1 TO FAIL-COUNT
               DISPLAY "   FAIL: Invalid decimal value"
           END-IF
           DISPLAY " ".
       
       TEST-STRING-VALIDATION.
           DISPLAY "3. Testing String Validation..."
           ADD 1 TO VALIDATION-COUNT
           
           IF TEST-STRING NOT = SPACES
               MOVE 1 TO STRING-VALID
               ADD 1 TO PASS-COUNT
               DISPLAY "   PASS: '" TEST-STRING "' is valid string"
           ELSE
               MOVE 0 TO STRING-VALID
               ADD 1 TO FAIL-COUNT
               DISPLAY "   FAIL: String is empty"
           END-IF
           DISPLAY " ".
       
       TEST-DATE-VALIDATION.
           DISPLAY "4. Testing Date Validation..."
           ADD 1 TO VALIDATION-COUNT
           
           MOVE TEST-DATE(1:4) TO YEAR
           MOVE TEST-DATE(5:2) TO MONTH
           MOVE TEST-DATE(7:2) TO DAY
           
           IF YEAR >= 1900 AND YEAR <= 2100
              AND MONTH >= 1 AND MONTH <= 12
              AND DAY >= 1 AND DAY <= 31
               MOVE 1 TO DATE-VALID
               ADD 1 TO PASS-COUNT
               DISPLAY "   PASS: " YEAR "-" MONTH "-" DAY 
                       " is valid date"
           ELSE
               MOVE 0 TO DATE-VALID
               ADD 1 TO FAIL-COUNT
               DISPLAY "   FAIL: Invalid date format"
           END-IF
           DISPLAY " ".
       
       TEST-RANGE-VALIDATION.
           DISPLAY "5. Testing Range Validation..."
           ADD 1 TO VALIDATION-COUNT
           
           IF TEST-NUMBER >= 10000 AND TEST-NUMBER <= 99999
               ADD 1 TO PASS-COUNT
               DISPLAY "   PASS: " TEST-NUMBER 
                       " is within range [10000-99999]"
           ELSE
               ADD 1 TO FAIL-COUNT
               DISPLAY "   FAIL: Value out of range"
           END-IF
           DISPLAY " ".
       
       TEST-FORMAT-VALIDATION.
           DISPLAY "6. Testing Format Validation..."
           ADD 1 TO VALIDATION-COUNT
           
           IF TEST-STRING(1:5) = "HELLO"
               ADD 1 TO PASS-COUNT
               DISPLAY "   PASS: String starts with 'HELLO'"
           ELSE
               ADD 1 TO FAIL-COUNT
               DISPLAY "   FAIL: Format mismatch"
           END-IF
           DISPLAY " ".
       
       DISPLAY-RESULTS.
           DISPLAY "====================================="
           DISPLAY "VALIDATION SUMMARY:"
           DISPLAY "-----------------------------------"
           DISPLAY "Total Tests:    " VALIDATION-COUNT
           DISPLAY "Tests Passed:   " PASS-COUNT
           DISPLAY "Tests Failed:   " FAIL-COUNT
           COMPUTE NUMERIC-TEST = (PASS-COUNT * 100) / VALIDATION-COUNT
           DISPLAY "Success Rate:   " NUMERIC-TEST "%"
           DISPLAY "====================================="
           DISPLAY " ".
       
       END PROGRAM DATA-VALIDATION.
