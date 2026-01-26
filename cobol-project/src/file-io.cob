       IDENTIFICATION DIVISION.
       PROGRAM-ID. FILE-IO-DEMO.
       AUTHOR. MUHAMMAD SHAMSUL MARUF.
       DATE-WRITTEN. 2026-01-26.
      *****************************************************************
      * FILE I/O OPERATIONS DEMONSTRATION                            *
      * This program demonstrates:                                    *
      * - Sequential file reading and writing                         *
      * - Record processing                                           *
      * - File error handling                                         *
      * - Data validation                                             *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT INPUT-FILE
               ASSIGN TO "../data/input/employees.txt"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS INPUT-FILE-STATUS.
           
           SELECT OUTPUT-FILE
               ASSIGN TO "../data/output/processed-employees.txt"
               ORGANIZATION IS LINE SEQUENTIAL
               FILE STATUS IS OUTPUT-FILE-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  INPUT-FILE.
       01  INPUT-RECORD.
           05  EMP-ID              PIC 9(6).
           05  FILLER              PIC X(1).
           05  EMP-NAME            PIC X(30).
           05  FILLER              PIC X(1).
           05  EMP-SALARY          PIC 9(7)V99.
           05  FILLER              PIC X(1).
           05  EMP-DEPARTMENT      PIC X(20).
       
       FD  OUTPUT-FILE.
       01  OUTPUT-RECORD           PIC X(100).
       
       WORKING-STORAGE SECTION.
       01  INPUT-FILE-STATUS       PIC XX.
           88  FILE-OK             VALUE "00".
           88  END-OF-FILE         VALUE "10".
       
       01  OUTPUT-FILE-STATUS      PIC XX.
       
       01  RECORD-COUNTER          PIC 9(6) VALUE ZERO.
       01  ERROR-COUNTER           PIC 9(6) VALUE ZERO.
       01  TOTAL-SALARY            PIC 9(10)V99 VALUE ZERO.
       
       01  FORMATTED-OUTPUT.
           05  OUT-ID              PIC 9(6).
           05  FILLER              PIC X(3) VALUE " | ".
           05  OUT-NAME            PIC X(30).
           05  FILLER              PIC X(3) VALUE " | ".
           05  OUT-SALARY          PIC ZZZ,ZZZ,ZZ9.99.
           05  FILLER              PIC X(3) VALUE " | ".
           05  OUT-DEPT            PIC X(20).
       
       01  HEADER-LINE.
           05  FILLER              PIC X(80) VALUE
               "ID     | NAME                           | SALARY".
           05  FILLER              PIC X(20) VALUE
               "       | DEPARTMENT".
       
       01  SEPARATOR-LINE          PIC X(100) VALUE ALL "-".
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           PERFORM INITIALIZE-FILES
           PERFORM PROCESS-RECORDS
           PERFORM DISPLAY-SUMMARY
           PERFORM CLEANUP
           STOP RUN.
       
       INITIALIZE-FILES.
           OPEN INPUT INPUT-FILE
           IF NOT FILE-OK
               DISPLAY "ERROR: Cannot open input file"
               DISPLAY "File Status: " INPUT-FILE-STATUS
               STOP RUN
           END-IF
           
           OPEN OUTPUT OUTPUT-FILE
           IF OUTPUT-FILE-STATUS NOT = "00"
               DISPLAY "ERROR: Cannot open output file"
               DISPLAY "File Status: " OUTPUT-FILE-STATUS
               CLOSE INPUT-FILE
               STOP RUN
           END-IF
           
           WRITE OUTPUT-RECORD FROM HEADER-LINE
           WRITE OUTPUT-RECORD FROM SEPARATOR-LINE.
       
       PROCESS-RECORDS.
           PERFORM UNTIL END-OF-FILE
               READ INPUT-FILE
                   AT END
                       SET END-OF-FILE TO TRUE
                   NOT AT END
                       PERFORM VALIDATE-AND-WRITE-RECORD
               END-READ
           END-PERFORM.
       
       VALIDATE-AND-WRITE-RECORD.
           IF EMP-ID > 0 AND EMP-SALARY > 0
               ADD 1 TO RECORD-COUNTER
               ADD EMP-SALARY TO TOTAL-SALARY
               MOVE EMP-ID TO OUT-ID
               MOVE EMP-NAME TO OUT-NAME
               MOVE EMP-SALARY TO OUT-SALARY
               MOVE EMP-DEPARTMENT TO OUT-DEPT
               WRITE OUTPUT-RECORD FROM FORMATTED-OUTPUT
           ELSE
               ADD 1 TO ERROR-COUNTER
               DISPLAY "WARNING: Invalid record for employee " EMP-NAME
           END-IF.
       
       DISPLAY-SUMMARY.
           DISPLAY " "
           DISPLAY "===== PROCESSING SUMMARY ====="
           DISPLAY "Records Processed: " RECORD-COUNTER
           DISPLAY "Invalid Records:   " ERROR-COUNTER
           DISPLAY "Total Salary:      $" TOTAL-SALARY
           DISPLAY "=============================="
           DISPLAY " ".
       
       CLEANUP.
           CLOSE INPUT-FILE
           CLOSE OUTPUT-FILE.
       
       END PROGRAM FILE-IO-DEMO.
