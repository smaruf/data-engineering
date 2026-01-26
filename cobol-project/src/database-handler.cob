       IDENTIFICATION DIVISION.
       PROGRAM-ID. DATABASE-HANDLER.
       AUTHOR. MUHAMMAD SHAMSUL MARUF.
       DATE-WRITTEN. 2026-01-26.
      *****************************************************************
      * DATABASE OPERATIONS DEMONSTRATION                             *
      * This program demonstrates:                                    *
      * - Indexed file organization                                   *
      * - Record CRUD operations                                      *
      * - Key-based searching                                         *
      * - Sequential and random access                                *
      *****************************************************************
       
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CUSTOMER-FILE
               ASSIGN TO "../data/output/customers.dat"
               ORGANIZATION IS INDEXED
               ACCESS MODE IS DYNAMIC
               RECORD KEY IS CUSTOMER-ID
               FILE STATUS IS FILE-STATUS.
       
       DATA DIVISION.
       FILE SECTION.
       FD  CUSTOMER-FILE.
       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID         PIC 9(6).
           05  CUSTOMER-NAME       PIC X(40).
           05  CUSTOMER-EMAIL      PIC X(50).
           05  CUSTOMER-PHONE      PIC X(15).
           05  CUSTOMER-BALANCE    PIC 9(8)V99.
       
       WORKING-STORAGE SECTION.
       01  FILE-STATUS             PIC XX.
           88  FILE-OK             VALUE "00".
           88  RECORD-NOT-FOUND    VALUE "23".
           88  DUPLICATE-KEY       VALUE "22".
       
       01  USER-CHOICE             PIC 9.
           88  CHOICE-CREATE       VALUE 1.
           88  CHOICE-READ         VALUE 2.
           88  CHOICE-UPDATE       VALUE 3.
           88  CHOICE-DELETE       VALUE 4.
           88  CHOICE-LIST-ALL     VALUE 5.
           88  CHOICE-EXIT         VALUE 9.
       
       01  SEARCH-ID               PIC 9(6).
       01  CONTINUE-FLAG           PIC X VALUE 'Y'.
       
       01  TEMP-CUSTOMER.
           05  TEMP-ID             PIC 9(6).
           05  TEMP-NAME           PIC X(40).
           05  TEMP-EMAIL          PIC X(50).
           05  TEMP-PHONE          PIC X(15).
           05  TEMP-BALANCE        PIC 9(8)V99.
       
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           PERFORM INITIALIZE-DATABASE
           PERFORM PROCESS-MENU UNTIL CHOICE-EXIT
           PERFORM CLEANUP
           STOP RUN.
       
       INITIALIZE-DATABASE.
           OPEN I-O CUSTOMER-FILE
           
           IF FILE-STATUS = "35"
               CLOSE CUSTOMER-FILE
               OPEN OUTPUT CUSTOMER-FILE
               CLOSE CUSTOMER-FILE
               OPEN I-O CUSTOMER-FILE
           END-IF
           
           IF NOT FILE-OK
               DISPLAY "ERROR: Cannot initialize database"
               DISPLAY "File Status: " FILE-STATUS
               STOP RUN
           END-IF.
       
       PROCESS-MENU.
           PERFORM DISPLAY-MENU
           ACCEPT USER-CHOICE
           
           EVALUATE TRUE
               WHEN CHOICE-CREATE
                   PERFORM CREATE-RECORD
               WHEN CHOICE-READ
                   PERFORM READ-RECORD
               WHEN CHOICE-UPDATE
                   PERFORM UPDATE-RECORD
               WHEN CHOICE-DELETE
                   PERFORM DELETE-RECORD
               WHEN CHOICE-LIST-ALL
                   PERFORM LIST-ALL-RECORDS
               WHEN CHOICE-EXIT
                   DISPLAY "Exiting program..."
               WHEN OTHER
                   DISPLAY "Invalid choice. Please try again."
           END-EVALUATE
           
           DISPLAY " ".
       
       DISPLAY-MENU.
           DISPLAY " "
           DISPLAY "===== CUSTOMER DATABASE SYSTEM ====="
           DISPLAY "1. Create New Customer"
           DISPLAY "2. Read Customer Record"
           DISPLAY "3. Update Customer Record"
           DISPLAY "4. Delete Customer Record"
           DISPLAY "5. List All Customers"
           DISPLAY "9. Exit"
           DISPLAY "==================================="
           DISPLAY "Enter your choice: " WITH NO ADVANCING.
       
       CREATE-RECORD.
           DISPLAY "--- CREATE NEW CUSTOMER ---"
           DISPLAY "Enter Customer ID (6 digits): " WITH NO ADVANCING
           ACCEPT TEMP-ID
           DISPLAY "Enter Customer Name: " WITH NO ADVANCING
           ACCEPT TEMP-NAME
           DISPLAY "Enter Email: " WITH NO ADVANCING
           ACCEPT TEMP-EMAIL
           DISPLAY "Enter Phone: " WITH NO ADVANCING
           ACCEPT TEMP-PHONE
           DISPLAY "Enter Balance: " WITH NO ADVANCING
           ACCEPT TEMP-BALANCE
           
           MOVE TEMP-ID TO CUSTOMER-ID
           MOVE TEMP-NAME TO CUSTOMER-NAME
           MOVE TEMP-EMAIL TO CUSTOMER-EMAIL
           MOVE TEMP-PHONE TO CUSTOMER-PHONE
           MOVE TEMP-BALANCE TO CUSTOMER-BALANCE
           
           WRITE CUSTOMER-RECORD
           
           IF FILE-OK
               DISPLAY "SUCCESS: Customer created successfully!"
           ELSE
               IF DUPLICATE-KEY
                   DISPLAY "ERROR: Customer ID already exists"
               ELSE
                   DISPLAY "ERROR: Failed to create customer"
                   DISPLAY "File Status: " FILE-STATUS
               END-IF
           END-IF.
       
       READ-RECORD.
           DISPLAY "--- READ CUSTOMER RECORD ---"
           DISPLAY "Enter Customer ID to search: " WITH NO ADVANCING
           ACCEPT SEARCH-ID
           
           MOVE SEARCH-ID TO CUSTOMER-ID
           READ CUSTOMER-FILE KEY IS CUSTOMER-ID
           
           IF FILE-OK
               DISPLAY "Customer Found:"
               DISPLAY "  ID:      " CUSTOMER-ID
               DISPLAY "  Name:    " CUSTOMER-NAME
               DISPLAY "  Email:   " CUSTOMER-EMAIL
               DISPLAY "  Phone:   " CUSTOMER-PHONE
               DISPLAY "  Balance: $" CUSTOMER-BALANCE
           ELSE
               IF RECORD-NOT-FOUND
                   DISPLAY "ERROR: Customer not found"
               ELSE
                   DISPLAY "ERROR: Failed to read customer"
                   DISPLAY "File Status: " FILE-STATUS
               END-IF
           END-IF.
       
       UPDATE-RECORD.
           DISPLAY "--- UPDATE CUSTOMER RECORD ---"
           DISPLAY "Enter Customer ID to update: " WITH NO ADVANCING
           ACCEPT SEARCH-ID
           
           MOVE SEARCH-ID TO CUSTOMER-ID
           READ CUSTOMER-FILE KEY IS CUSTOMER-ID
               UPDATE
           
           IF FILE-OK
               DISPLAY "Current Name: " CUSTOMER-NAME
               DISPLAY "Enter New Name (or press Enter to keep): "
                   WITH NO ADVANCING
               ACCEPT TEMP-NAME
               IF TEMP-NAME NOT = SPACES
                   MOVE TEMP-NAME TO CUSTOMER-NAME
               END-IF
               
               DISPLAY "Current Balance: $" CUSTOMER-BALANCE
               DISPLAY "Enter New Balance (0 to keep): "
                   WITH NO ADVANCING
               ACCEPT TEMP-BALANCE
               IF TEMP-BALANCE > 0
                   MOVE TEMP-BALANCE TO CUSTOMER-BALANCE
               END-IF
               
               REWRITE CUSTOMER-RECORD
               
               IF FILE-OK
                   DISPLAY "SUCCESS: Customer updated successfully!"
               ELSE
                   DISPLAY "ERROR: Failed to update customer"
                   DISPLAY "File Status: " FILE-STATUS
               END-IF
           ELSE
               IF RECORD-NOT-FOUND
                   DISPLAY "ERROR: Customer not found"
               ELSE
                   DISPLAY "ERROR: Failed to read customer"
                   DISPLAY "File Status: " FILE-STATUS
               END-IF
           END-IF.
       
       DELETE-RECORD.
           DISPLAY "--- DELETE CUSTOMER RECORD ---"
           DISPLAY "Enter Customer ID to delete: " WITH NO ADVANCING
           ACCEPT SEARCH-ID
           
           MOVE SEARCH-ID TO CUSTOMER-ID
           READ CUSTOMER-FILE KEY IS CUSTOMER-ID
           
           IF FILE-OK
               DISPLAY "Customer to delete: " CUSTOMER-NAME
               DISPLAY "Are you sure? (Y/N): " WITH NO ADVANCING
               ACCEPT CONTINUE-FLAG
               
               IF CONTINUE-FLAG = 'Y' OR CONTINUE-FLAG = 'y'
                   DELETE CUSTOMER-FILE RECORD
                   IF FILE-OK
                       DISPLAY "SUCCESS: Customer deleted successfully!"
                   ELSE
                       DISPLAY "ERROR: Failed to delete customer"
                       DISPLAY "File Status: " FILE-STATUS
                   END-IF
               ELSE
                   DISPLAY "Delete operation cancelled"
               END-IF
           ELSE
               IF RECORD-NOT-FOUND
                   DISPLAY "ERROR: Customer not found"
               ELSE
                   DISPLAY "ERROR: Failed to read customer"
                   DISPLAY "File Status: " FILE-STATUS
               END-IF
           END-IF.
       
       LIST-ALL-RECORDS.
           DISPLAY "--- ALL CUSTOMERS ---"
           DISPLAY "ID     | NAME                    | BALANCE"
           DISPLAY "-------|-------------------------|-------------"
           
           START CUSTOMER-FILE KEY IS >= CUSTOMER-ID
               INVALID KEY
                   DISPLAY "No customers found"
           END-START
           
           IF FILE-OK
               PERFORM READ-NEXT-RECORD
           END-IF.
       
       READ-NEXT-RECORD.
           READ CUSTOMER-FILE NEXT RECORD
               AT END
                   DISPLAY "--- End of List ---"
               NOT AT END
                   DISPLAY CUSTOMER-ID " | " CUSTOMER-NAME
                           " | $" CUSTOMER-BALANCE
                   PERFORM READ-NEXT-RECORD
           END-READ.
       
       CLEANUP.
           CLOSE CUSTOMER-FILE.
       
       END PROGRAM DATABASE-HANDLER.
