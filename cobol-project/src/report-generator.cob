       IDENTIFICATION DIVISION.
       PROGRAM-ID. REPORT-GENERATOR.
       AUTHOR. MUHAMMAD SHAMSUL MARUF.
       DATE-WRITTEN. 2026-01-26.
      *****************************************************************
      * REPORT GENERATION DEMONSTRATION                               *
      * This program demonstrates:                                    *
      * - Formatted output                                            *
      * - Page headers and footers                                    *
      * - Column alignment                                            *
      * - Summary calculations                                        *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT REPORT-FILE
               ASSIGN TO "../data/output/sales-report.txt"
               ORGANIZATION IS LINE SEQUENTIAL.
       
       DATA DIVISION.
       FILE SECTION.
       FD  REPORT-FILE.
       01  REPORT-LINE             PIC X(132).
       
       WORKING-STORAGE SECTION.
       01  COMPANY-NAME            PIC X(50) VALUE
           "ABC CORPORATION - SALES DEPARTMENT".
       
       01  CURRENT-DATE-FIELDS.
           05  CURR-YEAR           PIC 9(4).
           05  CURR-MONTH          PIC 9(2).
           05  CURR-DAY            PIC 9(2).
       
       01  FORMATTED-DATE          PIC X(10).
       
       01  PAGE-NUMBER             PIC 9(3) VALUE 1.
       01  LINE-COUNT              PIC 9(2) VALUE 0.
       01  LINES-PER-PAGE          PIC 9(2) VALUE 20.
       
       01  HEADER-LINE-1.
           05  FILLER              PIC X(40) VALUE SPACES.
           05  HDR-COMPANY         PIC X(50).
           05  FILLER              PIC X(42) VALUE SPACES.
       
       01  HEADER-LINE-2.
           05  FILLER              PIC X(50) VALUE
               "MONTHLY SALES REPORT".
           05  FILLER              PIC X(20) VALUE SPACES.
           05  FILLER              PIC X(6) VALUE "Date: ".
           05  HDR-DATE            PIC X(10).
           05  FILLER              PIC X(10) VALUE SPACES.
           05  FILLER              PIC X(6) VALUE "Page: ".
           05  HDR-PAGE            PIC ZZ9.
           05  FILLER              PIC X(27) VALUE SPACES.
       
       01  COLUMN-HEADER-1.
           05  FILLER              PIC X(132) VALUE
           "PRODUCT ID | PRODUCT NAME           | QUANTITY | ".
           05  FILLER              PIC X(132) VALUE
           "UNIT PRICE | TOTAL AMOUNT | CATEGORY".
       
       01  SEPARATOR-LINE          PIC X(132) VALUE ALL "-".
       
       01  DETAIL-LINE.
           05  DTL-PRODUCT-ID      PIC X(10).
           05  FILLER              PIC X(3) VALUE " | ".
           05  DTL-PRODUCT-NAME    PIC X(22).
           05  FILLER              PIC X(3) VALUE " | ".
           05  DTL-QUANTITY        PIC ZZZ,ZZ9.
           05  FILLER              PIC X(3) VALUE " | ".
           05  DTL-UNIT-PRICE      PIC ZZ,ZZ9.99.
           05  FILLER              PIC X(3) VALUE " | ".
           05  DTL-TOTAL           PIC ZZZ,ZZ9.99.
           05  FILLER              PIC X(3) VALUE " | ".
           05  DTL-CATEGORY        PIC X(15).
       
       01  FOOTER-LINE.
           05  FILLER              PIC X(60) VALUE SPACES.
           05  FILLER              PIC X(20) VALUE "GRAND TOTAL: $".
           05  FTR-GRAND-TOTAL     PIC ZZZ,ZZZ,ZZ9.99.
           05  FILLER              PIC X(39) VALUE SPACES.
       
       01  SALES-DATA-TABLE.
           05  SALES-RECORD OCCURS 10 TIMES.
               10  PROD-ID         PIC X(10).
               10  PROD-NAME       PIC X(22).
               10  QUANTITY        PIC 9(6).
               10  UNIT-PRICE      PIC 9(5)V99.
               10  TOTAL-AMT       PIC 9(7)V99.
               10  CATEGORY        PIC X(15).
       
       01  GRAND-TOTAL             PIC 9(10)V99 VALUE 0.
       01  RECORD-INDEX            PIC 9(2).
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           PERFORM INITIALIZE-REPORT
           PERFORM LOAD-SAMPLE-DATA
           PERFORM GENERATE-REPORT
           PERFORM FINALIZE-REPORT
           STOP RUN.
       
       INITIALIZE-REPORT.
           ACCEPT CURRENT-DATE-FIELDS FROM DATE YYYYMMDD
           STRING CURR-YEAR "-" CURR-MONTH "-" CURR-DAY
               DELIMITED BY SIZE
               INTO FORMATTED-DATE
           END-STRING
           
           OPEN OUTPUT REPORT-FILE.
       
       LOAD-SAMPLE-DATA.
      *    Sample sales data for demonstration
           MOVE "PROD-001" TO PROD-ID(1)
           MOVE "Laptop Computer" TO PROD-NAME(1)
           MOVE 50 TO QUANTITY(1)
           MOVE 1200.00 TO UNIT-PRICE(1)
           COMPUTE TOTAL-AMT(1) = QUANTITY(1) * UNIT-PRICE(1)
           MOVE "Electronics" TO CATEGORY(1)
           
           MOVE "PROD-002" TO PROD-ID(2)
           MOVE "Office Chair" TO PROD-NAME(2)
           MOVE 100 TO QUANTITY(2)
           MOVE 250.00 TO UNIT-PRICE(2)
           COMPUTE TOTAL-AMT(2) = QUANTITY(2) * UNIT-PRICE(2)
           MOVE "Furniture" TO CATEGORY(2)
           
           MOVE "PROD-003" TO PROD-ID(3)
           MOVE "Wireless Mouse" TO PROD-NAME(3)
           MOVE 200 TO QUANTITY(3)
           MOVE 25.99 TO UNIT-PRICE(3)
           COMPUTE TOTAL-AMT(3) = QUANTITY(3) * UNIT-PRICE(3)
           MOVE "Accessories" TO CATEGORY(3)
           
           MOVE "PROD-004" TO PROD-ID(4)
           MOVE "Monitor 27 inch" TO PROD-NAME(4)
           MOVE 75 TO QUANTITY(4)
           MOVE 350.00 TO UNIT-PRICE(4)
           COMPUTE TOTAL-AMT(4) = QUANTITY(4) * UNIT-PRICE(4)
           MOVE "Electronics" TO CATEGORY(4)
           
           MOVE "PROD-005" TO PROD-ID(5)
           MOVE "Desk Lamp" TO PROD-NAME(5)
           MOVE 150 TO QUANTITY(5)
           MOVE 45.50 TO UNIT-PRICE(5)
           COMPUTE TOTAL-AMT(5) = QUANTITY(5) * UNIT-PRICE(5)
           MOVE "Lighting" TO CATEGORY(5).
       
       GENERATE-REPORT.
           PERFORM PRINT-HEADER
           
           PERFORM VARYING RECORD-INDEX FROM 1 BY 1
               UNTIL RECORD-INDEX > 5
               PERFORM PRINT-DETAIL-LINE
           END-PERFORM
           
           PERFORM PRINT-FOOTER.
       
       PRINT-HEADER.
           MOVE COMPANY-NAME TO HDR-COMPANY
           WRITE REPORT-LINE FROM HEADER-LINE-1
           
           MOVE FORMATTED-DATE TO HDR-DATE
           MOVE PAGE-NUMBER TO HDR-PAGE
           WRITE REPORT-LINE FROM HEADER-LINE-2
           
           WRITE REPORT-LINE FROM SPACES
           WRITE REPORT-LINE FROM COLUMN-HEADER-1
           WRITE REPORT-LINE FROM SEPARATOR-LINE
           MOVE 5 TO LINE-COUNT.
       
       PRINT-DETAIL-LINE.
           MOVE PROD-ID(RECORD-INDEX) TO DTL-PRODUCT-ID
           MOVE PROD-NAME(RECORD-INDEX) TO DTL-PRODUCT-NAME
           MOVE QUANTITY(RECORD-INDEX) TO DTL-QUANTITY
           MOVE UNIT-PRICE(RECORD-INDEX) TO DTL-UNIT-PRICE
           MOVE TOTAL-AMT(RECORD-INDEX) TO DTL-TOTAL
           MOVE CATEGORY(RECORD-INDEX) TO DTL-CATEGORY
           
           WRITE REPORT-LINE FROM DETAIL-LINE
           ADD 1 TO LINE-COUNT
           ADD TOTAL-AMT(RECORD-INDEX) TO GRAND-TOTAL
           
           IF LINE-COUNT >= LINES-PER-PAGE
               PERFORM PRINT-PAGE-BREAK
           END-IF.
       
       PRINT-FOOTER.
           WRITE REPORT-LINE FROM SEPARATOR-LINE
           MOVE GRAND-TOTAL TO FTR-GRAND-TOTAL
           WRITE REPORT-LINE FROM FOOTER-LINE
           WRITE REPORT-LINE FROM SPACES.
       
       PRINT-PAGE-BREAK.
           ADD 1 TO PAGE-NUMBER
           MOVE 0 TO LINE-COUNT
           WRITE REPORT-LINE FROM SPACES
           PERFORM PRINT-HEADER.
       
       FINALIZE-REPORT.
           CLOSE REPORT-FILE
           DISPLAY "Report generated successfully!"
           DISPLAY "Total Sales Amount: $" GRAND-TOTAL
           DISPLAY "Report saved to: ../data/output/sales-report.txt".
       
       END PROGRAM REPORT-GENERATOR.
