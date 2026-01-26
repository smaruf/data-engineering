       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO-WORLD.
       AUTHOR. MUHAMMAD SHAMSUL MARUF.
      *****************************************************************
      * SIMPLE HELLO WORLD PROGRAM                                    *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  MESSAGE    PIC X(50) VALUE "Hello, World from COBOL!".
       01  COUNTER    PIC 9(2) VALUE 0.
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY MESSAGE.
           DISPLAY " ".
           
           PERFORM VARYING COUNTER FROM 1 BY 1 UNTIL COUNTER > 5
               DISPLAY "Count: " COUNTER
           END-PERFORM.
           
           DISPLAY " ".
           DISPLAY "Program completed successfully!".
           STOP RUN.
       
       END PROGRAM HELLO-WORLD.
