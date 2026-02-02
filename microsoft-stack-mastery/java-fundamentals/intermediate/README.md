# Java Intermediate Level - Complete Guide

This directory contains comprehensive Java intermediate-level examples for the Microsoft Stack Mastery project. All examples are production-ready with JavaDoc documentation, error handling, and working code.

## 📚 Table of Contents

1. [Exception Handling](#01-exception-handling)
2. [Multithreading](#02-multithreading)
3. [File I/O](#03-file-io)
4. [JDBC Database](#04-jdbc-database)

---

## 01. Exception Handling

### Files

#### `BasicExceptions.java`
**Comprehensive exception handling fundamentals**
- Try-catch-finally blocks
- Multiple catch blocks for different exception types
- Custom checked exceptions (`InvalidAgeException`)
- Custom unchecked exceptions (`InsufficientBalanceException`)
- Exception re-throwing and wrapping
- Practical examples: division by zero, array access, age validation, bank withdrawals

**Key Concepts:**
- Exception hierarchy (Throwable → Exception → RuntimeException)
- When to use checked vs unchecked exceptions
- Creating meaningful custom exceptions
- Proper exception message formatting

#### `CheckedExceptions.java`
**Handling checked exceptions**
- IOException with file operations (FileNotFoundException, general IOException)
- SQLException handling (simulated database operations)
- Multiple checked exception handling (URL, network, protocol)
- ClassNotFoundException with reflection
- Exception propagation with throws clause

**Key Concepts:**
- Checked exceptions must be caught or declared
- Proper resource cleanup in finally blocks
- SQLException error codes and states
- Method signature with throws declaration

#### `UncheckedExceptions.java`
**Runtime exception handling and prevention**
- NullPointerException handling and defensive programming
- ArrayIndexOutOfBoundsException with safe array access
- NumberFormatException with safe parsing
- IllegalArgumentException for input validation
- IllegalStateException for object state validation
- ArithmeticException and ClassCastException handling

**Key Concepts:**
- Defensive programming techniques
- Using Optional to prevent null issues
- Input validation before operations
- Safe type casting with instanceof

#### `ExceptionBestPractices.java`
**Modern exception handling patterns**
- Try-with-resources for automatic resource management
- Custom AutoCloseable resources
- Exception chaining to preserve root cause
- Business exception wrapping with context
- Proper exception logging with different levels
- Suppressed exceptions in try-with-resources
- Resource cleanup patterns

**Key Concepts:**
- AutoCloseable interface implementation
- Try-with-resources benefits
- Exception wrapping with business context
- Logging vs throwing (don't do both)

---

## 02. Multithreading

### Files

#### `ThreadBasics.java`
**Threading fundamentals**
- Thread creation by extending Thread class
- Thread creation using Runnable interface
- Lambda expressions for thread creation (Java 8+)
- Thread priority management
- Daemon threads
- Thread interruption and cancellation
- Thread states and lifecycle
- Thread information retrieval

**Key Concepts:**
- Runnable vs Thread extension (prefer Runnable)
- Thread lifecycle states (NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED)
- start() vs run() methods
- join() for thread synchronization
- Daemon threads terminate with main thread

#### `SynchronizationExample.java`
**Thread synchronization mechanisms**
- Race condition demonstration
- Synchronized methods for thread safety
- Synchronized blocks with explicit locks
- ReentrantLock for advanced locking
- ReadWriteLock for read-heavy scenarios
- Deadlock scenario demonstration
- Producer-Consumer with wait() and notify()
- Thread communication patterns

**Key Concepts:**
- Monitor locks and intrinsic locks
- Lock granularity and performance
- Deadlock prevention strategies
- wait()/notify() for inter-thread communication
- Lock fairness and reentrant locks

#### `ExecutorServiceExample.java`
**Thread pool management and task execution**
- FixedThreadPool for controlled parallelism
- CachedThreadPool for dynamic scaling
- SingleThreadExecutor for sequential execution
- Callable and Future for return values
- invokeAll() for batch execution
- invokeAny() for competitive execution
- ScheduledExecutorService for delayed/periodic tasks
- Custom ThreadPoolExecutor configuration
- CompletableFuture for async programming

**Key Concepts:**
- Thread pool benefits (reuse, control, performance)
- Callable vs Runnable (return value capability)
- Future.get() blocking behavior
- Executor shutdown strategies
- Fixed vs cached vs scheduled pools

#### `ConcurrentCollections.java`
**Thread-safe collection classes**
- ConcurrentHashMap for concurrent map operations
- BlockingQueue for producer-consumer patterns
- PriorityBlockingQueue for priority-based processing
- CopyOnWriteArrayList for read-heavy scenarios
- ConcurrentSkipListMap for sorted concurrent access
- AtomicInteger for lock-free operations
- AtomicReference for object references
- CountDownLatch for thread coordination
- CyclicBarrier for synchronization points
- Semaphore for resource access control

**Key Concepts:**
- Lock-free vs blocking collections
- Copy-on-write strategy
- Atomic operations without locks
- Blocking vs non-blocking queues
- Synchronization aids (latch, barrier, semaphore)

---

## 03. File I/O

### Files

#### `FileOperations.java`
**Basic file input/output operations**
- FileWriter and FileReader for character streams
- BufferedWriter and BufferedReader for efficiency
- Appending to existing files
- Binary file operations with DataInputStream/DataOutputStream
- File metadata and properties
- File copying with byte buffers
- Line-by-line file processing
- Directory listing and filtering
- File creation and deletion

**Key Concepts:**
- Character vs byte streams
- Buffered streams for performance
- Try-with-resources for auto-close
- File metadata access
- Binary vs text file handling

#### `NIOExample.java`
**Modern Java NIO (New I/O) operations**
- Path API for file system paths
- Files class for file operations
- Stream-based file reading (Java 8+)
- Directory operations and traversal
- File copying and moving with options
- ByteBuffer for buffer operations
- FileChannel for efficient I/O
- Memory-mapped files for large file access
- WatchService for directory monitoring

**Key Concepts:**
- Path vs File (NIO vs IO)
- Files utility methods
- Stream processing of file lines
- Channel-based I/O performance
- Memory mapping benefits
- Directory watching for file changes

#### `SerializationExample.java`
**Object serialization and deserialization**
- Basic object serialization with Serializable
- Transient fields exclusion
- Static fields exclusion
- Custom serialization with writeObject/readObject
- SerialVersionUID for version control
- Serializing collections and nested objects
- Deep copy using serialization
- Security considerations

**Key Concepts:**
- Serializable marker interface
- Object graph serialization
- transient keyword usage
- Custom serialization control
- serialVersionUID importance
- ObjectInputStream/ObjectOutputStream

#### `CSVProcessing.java`
**CSV file reading and writing**
- CSV parsing with quoted fields
- Writing CSV with proper formatting
- Reading CSV with error handling
- Stream-based CSV processing
- Data filtering and transformation
- Grouping and aggregation
- Data validation
- Merging multiple CSV files
- Handling special characters and delimiters

**Key Concepts:**
- CSV format complications (quotes, commas)
- Robust parsing strategies
- Stream API for data processing
- Error handling in batch processing
- Data validation patterns

---

## 04. JDBC Database

### Files

#### `JDBCConnection.java`
**Database connection management**
- Basic database connection with DriverManager
- Connection with Properties object
- DatabaseMetaData inspection
- Connection validity testing
- Proper connection closing
- Try-with-resources for connections
- Simple connection pool implementation
- Connection error handling
- Connection timeout configuration

**Key Concepts:**
- JDBC driver loading (automatic in JDBC 4.0+)
- Connection string format
- Connection pooling benefits
- Metadata retrieval
- Transaction isolation levels
- Connection lifecycle management

**Note:** Examples use H2 in-memory database. For production:
- HikariCP (recommended)
- Apache DBCP
- C3P0

#### `CRUDOperations.java`
**Create, Read, Update, Delete operations**
- INSERT with PreparedStatement
- Batch INSERT for multiple records
- SELECT by ID (single record)
- SELECT all records
- SELECT with WHERE clause
- SELECT with aggregate functions (COUNT, AVG, MIN, MAX)
- UPDATE single and multiple columns
- DELETE single and multiple records
- ResultSet processing
- Generated key retrieval

**Key Concepts:**
- PreparedStatement benefits
- Batch operations for performance
- ResultSet navigation
- SQL aggregate functions
- Parameterized queries
- Statement vs PreparedStatement

#### `PreparedStatements.java`
**Parameterized queries and batch operations**
- SQL injection prevention
- Parameter binding
- PreparedStatement reuse
- Batch insert operations
- Batch update operations
- Parameterized SELECT queries
- LIKE operator with wildcards
- IN clause with dynamic parameters
- NULL value handling
- ParameterMetaData inspection

**Key Concepts:**
- SQL injection vulnerabilities
- Prepared statement compilation
- Batch processing benefits
- Parameter types and NULL handling
- Statement caching
- Performance optimization

#### `TransactionManagement.java`
**ACID properties and transaction control**
- Auto-commit mode control
- Manual commit and rollback
- Money transfer with transactions
- Savepoints for partial rollback
- Transaction isolation levels
- ACID property demonstrations
- Error handling in transactions
- Transaction best practices

**Key Concepts:**
- ACID properties (Atomicity, Consistency, Isolation, Durability)
- Transaction boundaries
- Rollback strategies
- Savepoint usage
- Isolation level impacts
- Deadlock prevention

---

## 🚀 Getting Started

### Prerequisites

- Java Development Kit (JDK) 8 or higher
- Basic understanding of Java fundamentals
- IDE (IntelliJ IDEA, Eclipse, or VS Code)

### Compilation

Each file can be compiled independently:

```bash
# Compile single file
javac 01-exception-handling/BasicExceptions.java

# Compile all files in a directory
javac 01-exception-handling/*.java
```

### Execution

Run the main method in each file:

```bash
# Run example
java -cp . com.microsoft.java.intermediate.exceptions.BasicExceptions
```

### For JDBC Examples

JDBC examples use H2 in-memory database which doesn't require external setup. For production use, add appropriate JDBC driver dependencies:

**Maven:**
```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <version>2.2.224</version>
</dependency>
```

**Gradle:**
```gradle
implementation 'com.h2database:h2:2.2.224'
```

---

## 📖 Learning Path

### Beginner → Intermediate Journey

1. **Start with Exception Handling** - Master error handling before complex operations
2. **Progress to File I/O** - Learn data persistence and file manipulation
3. **Study Multithreading** - Understand concurrent programming
4. **Finish with JDBC** - Combine all skills with database operations

### Recommended Study Order Per Section

**Exception Handling:**
1. BasicExceptions.java
2. UncheckedExceptions.java
3. CheckedExceptions.java
4. ExceptionBestPractices.java

**Multithreading:**
1. ThreadBasics.java
2. SynchronizationExample.java
3. ExecutorServiceExample.java
4. ConcurrentCollections.java

**File I/O:**
1. FileOperations.java
2. NIOExample.java
3. SerializationExample.java
4. CSVProcessing.java

**JDBC:**
1. JDBCConnection.java
2. CRUDOperations.java
3. PreparedStatements.java
4. TransactionManagement.java

---

## 💡 Best Practices Demonstrated

### Code Quality
✅ Comprehensive JavaDoc documentation  
✅ Proper error handling  
✅ Resource management with try-with-resources  
✅ Meaningful variable and method names  
✅ Clear code organization  

### Performance
✅ Buffered I/O for large files  
✅ PreparedStatement caching  
✅ Batch operations for bulk data  
✅ Thread pooling for concurrency  
✅ NIO for efficient file operations  

### Security
✅ SQL injection prevention  
✅ Proper exception message handling  
✅ Secure resource cleanup  
✅ Transaction rollback on errors  

### Maintainability
✅ Single Responsibility Principle  
✅ DRY (Don't Repeat Yourself)  
✅ Separation of concerns  
✅ Comprehensive examples  

---

## 🎯 Key Takeaways

### Exception Handling
- Always close resources in finally or use try-with-resources
- Create custom exceptions for business logic
- Catch specific exceptions before general ones
- Never swallow exceptions silently
- Log errors at appropriate levels

### Multithreading
- Prefer Runnable over Thread extension
- Use synchronized for simple cases, locks for advanced needs
- Always release locks in finally blocks
- Use concurrent collections for thread-safe operations
- Leverage ExecutorService for thread pooling

### File I/O
- Use NIO for modern file operations
- Buffer streams for better performance
- Handle character encoding explicitly
- Validate data before processing
- Stream API for efficient large file processing

### JDBC
- Always use PreparedStatement (prevent SQL injection)
- Use connection pooling in production
- Manage transactions explicitly for data integrity
- Close resources in correct order (ResultSet → Statement → Connection)
- Batch operations for multiple inserts/updates

---

## 🔗 Additional Resources

- [Official Java Documentation](https://docs.oracle.com/en/java/)
- [Java Concurrency Tutorial](https://docs.oracle.com/javase/tutorial/essential/concurrency/)
- [JDBC Tutorial](https://docs.oracle.com/javase/tutorial/jdbc/)
- [Java NIO Tutorial](https://docs.oracle.com/javase/tutorial/essential/io/fileio.html)

---

## 📝 Notes

- All examples use H2 in-memory database for JDBC operations
- No external database setup required
- Code is self-contained and executable
- Examples demonstrate real-world scenarios
- Production-ready patterns and practices

---

## 🤝 Contributing

Feel free to enhance these examples or add new ones following the established patterns:
- Comprehensive JavaDoc
- Error handling
- Working main() method with demonstrations
- Clear console output
- Real-world scenarios

---

## 📄 License

Part of the Microsoft Stack Mastery project.

---

**Happy Learning! 🚀**

For questions or improvements, please create an issue or pull request.
