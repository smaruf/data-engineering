       IDENTIFICATION DIVISION.
       PROGRAM-ID. STRING-PROCESSOR.
       AUTHOR. MUHAMMAD SHAMSUL MARUF.
       DATE-WRITTEN. 2026-01-26.
      *****************************************************************
      * STRING MANIPULATION DEMONSTRATION                             *
      * This program demonstrates:                                    *
      * - String manipulation functions                               *
      * - Text parsing                                                *
      * - Pattern matching                                            *
      * - Character operations                                        *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  SOURCE-STRING           PIC X(100).
       01  TARGET-STRING           PIC X(100).
       01  RESULT-STRING           PIC X(100).
       
       01  SAMPLE-TEXT             PIC X(80) VALUE
           "The quick brown fox jumps over the lazy dog".
       
       01  SEARCH-PATTERN          PIC X(20).
       01  REPLACE-PATTERN         PIC X(20).
       
       01  STRING-LENGTH           PIC 9(3).
       01  CHAR-COUNT              PIC 9(3).
       01  SPACE-COUNT             PIC 9(3) VALUE 0.
       01  WORD-COUNT              PIC 9(3) VALUE 0.
       
       01  CHAR-INDEX              PIC 9(3).
       01  POSITION                PIC 9(3).
       
       01  UPPERCASE-STRING        PIC X(100).
       01  LOWERCASE-STRING        PIC X(100).
       
       01  TEMP-CHAR               PIC X.
       01  IN-WORD                 PIC 9 VALUE 0.
       
       01  FIRST-NAME              PIC X(20) VALUE "MUHAMMAD".
       01  MIDDLE-NAME             PIC X(20) VALUE "SHAMSUL".
       01  LAST-NAME               PIC X(20) VALUE "MARUF".
       01  FULL-NAME               PIC X(62).
       
       01  EMAIL-ADDRESS           PIC X(50).
       01  USERNAME                PIC X(30).
       01  DOMAIN                  PIC X(30).
       01  AT-POSITION             PIC 9(2).
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY "===== STRING PROCESSING SYSTEM ====="
           DISPLAY " "
           
           PERFORM STRING-CONCATENATION
           PERFORM STRING-SPLITTING
           PERFORM STRING-SEARCH
           PERFORM STRING-REPLACE
           PERFORM CASE-CONVERSION
           PERFORM CHARACTER-COUNTING
           PERFORM WORD-COUNTING
           PERFORM STRING-TRIMMING
           PERFORM EMAIL-PARSING
           
           DISPLAY " "
           DISPLAY "===== ALL TESTS COMPLETED ====="
           STOP RUN.
       
       STRING-CONCATENATION.
           DISPLAY "1. STRING CONCATENATION"
           DISPLAY "   First Name:  " FIRST-NAME
           DISPLAY "   Middle Name: " MIDDLE-NAME
           DISPLAY "   Last Name:   " LAST-NAME
           
           STRING FIRST-NAME DELIMITED BY SPACES
                  " " DELIMITED BY SIZE
                  MIDDLE-NAME DELIMITED BY SPACES
                  " " DELIMITED BY SIZE
                  LAST-NAME DELIMITED BY SPACES
               INTO FULL-NAME
           END-STRING
           
           DISPLAY "   Full Name:   " FULL-NAME
           DISPLAY " ".
       
       STRING-SPLITTING.
           DISPLAY "2. STRING SPLITTING"
           MOVE "john.doe@example.com" TO EMAIL-ADDRESS
           DISPLAY "   Email: " EMAIL-ADDRESS
           
           INSPECT EMAIL-ADDRESS
               TALLYING AT-POSITION
               FOR ALL "@"
           
           IF AT-POSITION > 0
               UNSTRING EMAIL-ADDRESS DELIMITED BY "@"
                   INTO USERNAME
                        DOMAIN
               END-UNSTRING
               DISPLAY "   Username: " USERNAME
               DISPLAY "   Domain:   " DOMAIN
           END-IF
           DISPLAY " ".
       
       STRING-SEARCH.
           DISPLAY "3. STRING SEARCH"
           MOVE SAMPLE-TEXT TO SOURCE-STRING
           DISPLAY "   Text: " SOURCE-STRING
           MOVE "fox" TO SEARCH-PATTERN
           DISPLAY "   Searching for: " SEARCH-PATTERN
           
           MOVE 0 TO POSITION
           INSPECT SOURCE-STRING
               TALLYING POSITION
               FOR ALL SEARCH-PATTERN
           
           IF POSITION > 0
               DISPLAY "   Found '" SEARCH-PATTERN "' in text"
           ELSE
               DISPLAY "   Pattern not found"
           END-IF
           DISPLAY " ".
       
       STRING-REPLACE.
           DISPLAY "4. STRING REPLACE"
           MOVE SAMPLE-TEXT TO SOURCE-STRING
           DISPLAY "   Original: " SOURCE-STRING
           
           MOVE SOURCE-STRING TO TARGET-STRING
           INSPECT TARGET-STRING
               REPLACING ALL "fox" BY "cat"
           
           DISPLAY "   Modified: " TARGET-STRING
           DISPLAY " ".
       
       CASE-CONVERSION.
           DISPLAY "5. CASE CONVERSION"
           MOVE "Hello World" TO SOURCE-STRING
           DISPLAY "   Original: " SOURCE-STRING
           
           MOVE SOURCE-STRING TO UPPERCASE-STRING
           INSPECT UPPERCASE-STRING
               CONVERTING "abcdefghijklmnopqrstuvwxyz"
                       TO "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
           DISPLAY "   Uppercase: " UPPERCASE-STRING
           
           MOVE SOURCE-STRING TO LOWERCASE-STRING
           INSPECT LOWERCASE-STRING
               CONVERTING "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       TO "abcdefghijklmnopqrstuvwxyz"
           DISPLAY "   Lowercase: " LOWERCASE-STRING
           DISPLAY " ".
       
       CHARACTER-COUNTING.
           DISPLAY "6. CHARACTER COUNTING"
           MOVE SAMPLE-TEXT TO SOURCE-STRING
           DISPLAY "   Text: " SOURCE-STRING
           
           MOVE 0 TO CHAR-COUNT
           MOVE 0 TO SPACE-COUNT
           
           INSPECT SOURCE-STRING
               TALLYING CHAR-COUNT FOR CHARACTERS
           
           INSPECT SOURCE-STRING
               TALLYING SPACE-COUNT FOR ALL " "
           
           DISPLAY "   Total Characters: " CHAR-COUNT
           DISPLAY "   Spaces: " SPACE-COUNT
           COMPUTE CHAR-COUNT = CHAR-COUNT - SPACE-COUNT
           DISPLAY "   Non-space Characters: " CHAR-COUNT
           DISPLAY " ".
       
       WORD-COUNTING.
           DISPLAY "7. WORD COUNTING"
           MOVE SAMPLE-TEXT TO SOURCE-STRING
           DISPLAY "   Text: " SOURCE-STRING
           
           MOVE 0 TO WORD-COUNT
           MOVE 0 TO IN-WORD
           MOVE FUNCTION LENGTH(SOURCE-STRING) TO STRING-LENGTH
           
           PERFORM VARYING CHAR-INDEX FROM 1 BY 1
               UNTIL CHAR-INDEX > STRING-LENGTH
               MOVE SOURCE-STRING(CHAR-INDEX:1) TO TEMP-CHAR
               
               IF TEMP-CHAR NOT = " " AND TEMP-CHAR NOT = LOW-VALUE
                   IF IN-WORD = 0
                       ADD 1 TO WORD-COUNT
                       MOVE 1 TO IN-WORD
                   END-IF
               ELSE
                   MOVE 0 TO IN-WORD
               END-IF
           END-PERFORM
           
           DISPLAY "   Word Count: " WORD-COUNT
           DISPLAY " ".
       
       STRING-TRIMMING.
           DISPLAY "8. STRING TRIMMING"
           MOVE "   Hello World   " TO SOURCE-STRING
           DISPLAY "   Original: '" SOURCE-STRING "'"
           
           MOVE FUNCTION TRIM(SOURCE-STRING) TO TARGET-STRING
           DISPLAY "   Trimmed:  '" TARGET-STRING "'"
           DISPLAY " ".
       
       EMAIL-PARSING.
           DISPLAY "9. EMAIL PARSING"
           MOVE "user.name@company.domain.com" TO EMAIL-ADDRESS
           DISPLAY "   Email: " EMAIL-ADDRESS
           
           MOVE 0 TO AT-POSITION
           INSPECT EMAIL-ADDRESS
               TALLYING AT-POSITION FOR ALL "@"
           
           IF AT-POSITION = 1
               DISPLAY "   Valid email format detected"
               UNSTRING EMAIL-ADDRESS DELIMITED BY "@"
                   INTO USERNAME
                        DOMAIN
               END-UNSTRING
               DISPLAY "   Local part: " USERNAME
               DISPLAY "   Domain:     " DOMAIN
           ELSE
               DISPLAY "   Invalid email format"
           END-IF
           DISPLAY " ".
       
       END PROGRAM STRING-PROCESSOR.
