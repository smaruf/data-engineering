# Java Coding Standards for Data Engineering

## Table of Contents
1. [Naming Conventions](#naming-conventions)
2. [Code Structure](#code-structure)
3. [Best Practices](#best-practices)
4. [Error Handling](#error-handling)
5. [Performance Guidelines](#performance-guidelines)
6. [Testing Standards](#testing-standards)

---

## Naming Conventions

### Classes and Interfaces

```java
// ✅ GOOD: PascalCase for classes
public class DataPipelineExecutor {
    // Class implementation
}

public class CsvFileReader {
    // Class implementation
}

// ✅ GOOD: Interface names describe behavior
public interface DataSource {
    DataFrame read();
}

public interface DataTransformer {
    DataFrame transform(DataFrame input);
}

// ❌ BAD: Generic names, unclear purpose
public class Manager { }
public class Helper { }
public class Utility { }
```

### Methods and Variables

```java
public class OrderProcessor {
    
    // ✅ GOOD: camelCase for variables and methods
    private int maxRetryAttempts = 3;
    private String connectionString;
    
    public void processOrders(List<Order> orders) {
        for (Order order : orders) {
            validateOrder(order);
            saveToDatabase(order);
        }
    }
    
    private boolean validateOrder(Order order) {
        return order != null && order.getAmount() > 0;
    }
    
    // ❌ BAD: Unclear, abbreviated names
    private int mra;  // What is this?
    public void proc(List<Order> o) { }  // Unclear method name
}
```

### Constants

```java
public class Configuration {
    
    // ✅ GOOD: UPPER_CASE with underscores
    public static final int MAX_RETRY_ATTEMPTS = 3;
    public static final String DEFAULT_DATE_FORMAT = "yyyy-MM-dd";
    public static final long TIMEOUT_MILLISECONDS = 30000L;
    
    // ✅ GOOD: Grouped related constants
    public static final class DatabaseConfig {
        public static final String DRIVER_CLASS = "org.postgresql.Driver";
        public static final int MAX_CONNECTIONS = 10;
        public static final int CONNECTION_TIMEOUT_SECONDS = 30;
    }
    
    // ❌ BAD: Mixed case, unclear names
    private static final int timeout = 30000;
    public static final String fmt = "yyyy-MM-dd";
}
```

---

## Code Structure

### Package Organization

```
com.company.dataengineering/
├── config/                    # Configuration classes
│   ├── DatabaseConfig.java
│   └── SparkConfig.java
├── datasource/               # Data source implementations
│   ├── CsvDataSource.java
│   ├── JdbcDataSource.java
│   └── KafkaDataSource.java
├── transformer/              # Data transformation logic
│   ├── DataCleaner.java
│   └── DataEnricher.java
├── loader/                   # Data loading implementations
│   ├── DatabaseLoader.java
│   └── FileLoader.java
├── model/                    # Data models and DTOs
│   ├── Order.java
│   └── Customer.java
├── util/                     # Utility classes
│   ├── DateUtils.java
│   └── StringUtils.java
└── exception/               # Custom exceptions
    ├── DataSourceException.java
    └── TransformationException.java
```

### Class Structure

```java
/**
 * Processes customer orders from various sources.
 * 
 * This class handles:
 * - Reading orders from multiple sources
 * - Validating order data
 * - Applying business rules
 * - Loading to destination
 * 
 * @author Your Name
 * @since 1.0
 */
public class OrderProcessor {
    
    // 1. Static variables
    private static final Logger LOGGER = LoggerFactory.getLogger(OrderProcessor.class);
    private static final int MAX_BATCH_SIZE = 1000;
    
    // 2. Instance variables
    private final DataSource dataSource;
    private final DataTransformer transformer;
    private final DataLoader loader;
    private final MetricsCollector metricsCollector;
    
    // 3. Constructor(s)
    public OrderProcessor(DataSource dataSource, 
                         DataTransformer transformer,
                         DataLoader loader) {
        this.dataSource = Objects.requireNonNull(dataSource, "dataSource cannot be null");
        this.transformer = Objects.requireNonNull(transformer, "transformer cannot be null");
        this.loader = Objects.requireNonNull(loader, "loader cannot be null");
        this.metricsCollector = new MetricsCollector();
    }
    
    // 4. Public methods
    public ProcessingResult processOrders() {
        LOGGER.info("Starting order processing");
        
        try {
            List<Order> orders = readOrders();
            List<Order> validOrders = validateOrders(orders);
            List<Order> transformedOrders = transformOrders(validOrders);
            loadOrders(transformedOrders);
            
            return ProcessingResult.success(transformedOrders.size());
            
        } catch (Exception e) {
            LOGGER.error("Order processing failed", e);
            return ProcessingResult.failure(e.getMessage());
        }
    }
    
    // 5. Private methods
    private List<Order> readOrders() {
        return dataSource.read();
    }
    
    private List<Order> validateOrders(List<Order> orders) {
        return orders.stream()
            .filter(this::isValidOrder)
            .collect(Collectors.toList());
    }
    
    private boolean isValidOrder(Order order) {
        return order != null && 
               order.getAmount() > 0 &&
               order.getCustomerId() != null;
    }
    
    private List<Order> transformOrders(List<Order> orders) {
        return transformer.transform(orders);
    }
    
    private void loadOrders(List<Order> orders) {
        loader.load(orders);
    }
    
    // 6. Inner classes (if needed)
    public static class ProcessingResult {
        private final boolean success;
        private final int processedCount;
        private final String errorMessage;
        
        private ProcessingResult(boolean success, int processedCount, String errorMessage) {
            this.success = success;
            this.processedCount = processedCount;
            this.errorMessage = errorMessage;
        }
        
        public static ProcessingResult success(int count) {
            return new ProcessingResult(true, count, null);
        }
        
        public static ProcessingResult failure(String errorMessage) {
            return new ProcessingResult(false, 0, errorMessage);
        }
        
        // Getters
        public boolean isSuccess() { return success; }
        public int getProcessedCount() { return processedCount; }
        public String getErrorMessage() { return errorMessage; }
    }
}
```

---

## Best Practices

### Use Builder Pattern for Complex Objects

```java
// ✅ GOOD: Builder pattern for readability
public class DataPipelineConfig {
    private final String sourcePath;
    private final String destinationPath;
    private final int batchSize;
    private final int maxRetries;
    private final boolean enableLogging;
    
    private DataPipelineConfig(Builder builder) {
        this.sourcePath = builder.sourcePath;
        this.destinationPath = builder.destinationPath;
        this.batchSize = builder.batchSize;
        this.maxRetries = builder.maxRetries;
        this.enableLogging = builder.enableLogging;
    }
    
    public static class Builder {
        private String sourcePath;
        private String destinationPath;
        private int batchSize = 1000;  // Default value
        private int maxRetries = 3;    // Default value
        private boolean enableLogging = true;  // Default value
        
        public Builder sourcePath(String sourcePath) {
            this.sourcePath = sourcePath;
            return this;
        }
        
        public Builder destinationPath(String destinationPath) {
            this.destinationPath = destinationPath;
            return this;
        }
        
        public Builder batchSize(int batchSize) {
            this.batchSize = batchSize;
            return this;
        }
        
        public Builder maxRetries(int maxRetries) {
            this.maxRetries = maxRetries;
            return this;
        }
        
        public Builder enableLogging(boolean enableLogging) {
            this.enableLogging = enableLogging;
            return this;
        }
        
        public DataPipelineConfig build() {
            // Validation
            if (sourcePath == null || sourcePath.isEmpty()) {
                throw new IllegalArgumentException("sourcePath is required");
            }
            if (destinationPath == null || destinationPath.isEmpty()) {
                throw new IllegalArgumentException("destinationPath is required");
            }
            return new DataPipelineConfig(this);
        }
    }
    
    // Getters
    public String getSourcePath() { return sourcePath; }
    public String getDestinationPath() { return destinationPath; }
    public int getBatchSize() { return batchSize; }
    public int getMaxRetries() { return maxRetries; }
    public boolean isLoggingEnabled() { return enableLogging; }
}

// Usage
DataPipelineConfig config = new DataPipelineConfig.Builder()
    .sourcePath("/input/data")
    .destinationPath("/output/data")
    .batchSize(5000)
    .maxRetries(5)
    .build();

// ❌ BAD: Constructor with many parameters
public DataPipelineConfig(String sourcePath, String destinationPath, 
                          int batchSize, int maxRetries, boolean enableLogging) {
    // Hard to read, easy to mix up parameters
}
```

### Prefer Immutability

```java
// ✅ GOOD: Immutable class
public final class Order {
    private final String orderId;
    private final String customerId;
    private final BigDecimal amount;
    private final LocalDateTime orderDate;
    
    public Order(String orderId, String customerId, BigDecimal amount, LocalDateTime orderDate) {
        this.orderId = Objects.requireNonNull(orderId);
        this.customerId = Objects.requireNonNull(customerId);
        this.amount = Objects.requireNonNull(amount);
        this.orderDate = Objects.requireNonNull(orderDate);
    }
    
    // Only getters, no setters
    public String getOrderId() { return orderId; }
    public String getCustomerId() { return customerId; }
    public BigDecimal getAmount() { return amount; }
    public LocalDateTime getOrderDate() { return orderDate; }
    
    // Create new instance for modifications
    public Order withAmount(BigDecimal newAmount) {
        return new Order(this.orderId, this.customerId, newAmount, this.orderDate);
    }
}

// ❌ BAD: Mutable class (can lead to bugs in multi-threaded scenarios)
public class Order {
    private String orderId;
    private BigDecimal amount;
    
    public void setAmount(BigDecimal amount) {
        this.amount = amount;  // Dangerous in concurrent scenarios
    }
}
```

### Use Streams Effectively

```java
public class DataProcessor {
    
    // ✅ GOOD: Clear, functional style
    public List<Order> processOrders(List<Order> orders) {
        return orders.stream()
            .filter(order -> order.getAmount().compareTo(BigDecimal.ZERO) > 0)
            .filter(order -> order.getCustomerId() != null)
            .map(this::enrichOrder)
            .sorted(Comparator.comparing(Order::getOrderDate))
            .collect(Collectors.toList());
    }
    
    // ✅ GOOD: Parallel streams for large datasets
    public Map<String, BigDecimal> calculateTotalsByCustomer(List<Order> orders) {
        return orders.parallelStream()
            .collect(Collectors.groupingBy(
                Order::getCustomerId,
                Collectors.reducing(
                    BigDecimal.ZERO,
                    Order::getAmount,
                    BigDecimal::add
                )
            ));
    }
    
    // ❌ BAD: Imperative style (harder to read and maintain)
    public List<Order> processOrdersImperative(List<Order> orders) {
        List<Order> result = new ArrayList<>();
        for (Order order : orders) {
            if (order.getAmount().compareTo(BigDecimal.ZERO) > 0 &&
                order.getCustomerId() != null) {
                Order enriched = enrichOrder(order);
                result.add(enriched);
            }
        }
        result.sort(Comparator.comparing(Order::getOrderDate));
        return result;
    }
    
    private Order enrichOrder(Order order) {
        // Enrichment logic
        return order;
    }
}
```

---

## Error Handling

### Use Specific Exceptions

```java
// ✅ GOOD: Custom, specific exceptions
public class DataSourceException extends RuntimeException {
    public DataSourceException(String message) {
        super(message);
    }
    
    public DataSourceException(String message, Throwable cause) {
        super(message, cause);
    }
}

public class ValidationException extends RuntimeException {
    private final List<String> validationErrors;
    
    public ValidationException(List<String> validationErrors) {
        super("Validation failed: " + String.join(", ", validationErrors));
        this.validationErrors = new ArrayList<>(validationErrors);
    }
    
    public List<String> getValidationErrors() {
        return Collections.unmodifiableList(validationErrors);
    }
}

// Usage
public void readData(String path) {
    try {
        // Read data
    } catch (IOException e) {
        throw new DataSourceException("Failed to read data from " + path, e);
    }
}

// ❌ BAD: Generic exceptions
public void readData(String path) throws Exception {  // Too generic
    // ...
}
```

### Proper Try-With-Resources

```java
// ✅ GOOD: Try-with-resources for automatic cleanup
public List<String> readLines(String filePath) {
    List<String> lines = new ArrayList<>();
    
    try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
        String line;
        while ((line = reader.readLine()) != null) {
            lines.add(line);
        }
    } catch (IOException e) {
        LOGGER.error("Failed to read file: {}", filePath, e);
        throw new DataSourceException("Cannot read file", e);
    }
    
    return lines;
}

// ❌ BAD: Manual resource management
public List<String> readLinesManual(String filePath) {
    BufferedReader reader = null;
    try {
        reader = new BufferedReader(new FileReader(filePath));
        // ...
    } finally {
        if (reader != null) {
            try {
                reader.close();  // Boilerplate code
            } catch (IOException e) {
                // Handle exception
            }
        }
    }
}
```

### Fail Fast Principle

```java
// ✅ GOOD: Validate early
public class OrderValidator {
    
    public void validateOrder(Order order) {
        Objects.requireNonNull(order, "Order cannot be null");
        
        if (order.getOrderId() == null || order.getOrderId().isEmpty()) {
            throw new ValidationException("Order ID is required");
        }
        
        if (order.getAmount() == null || order.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new ValidationException("Order amount must be positive");
        }
        
        if (order.getCustomerId() == null) {
            throw new ValidationException("Customer ID is required");
        }
        
        // Continue processing with valid order
    }
    
    // ❌ BAD: Late validation (wastes resources)
    public void processOrder(Order order) {
        // Do expensive operations first
        String enrichedData = callExternalAPI(order);
        List<Product> products = lookupProducts(order);
        
        // Validate late
        if (order.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new ValidationException("Invalid amount");  // Wasted effort above
        }
    }
}
```

---

## Performance Guidelines

### Efficient Collections

```java
// ✅ GOOD: Use appropriate collection with initial capacity
public class DataAggregator {
    
    public Map<String, List<Order>> groupOrders(List<Order> orders) {
        // HashMap with estimated capacity
        int estimatedSize = orders.size() / 10;  // Estimate 10 orders per customer
        Map<String, List<Order>> grouped = new HashMap<>(estimatedSize);
        
        for (Order order : orders) {
            grouped.computeIfAbsent(order.getCustomerId(), k -> new ArrayList<>())
                   .add(order);
        }
        
        return grouped;
    }
    
    // ✅ GOOD: ArrayList for known size
    public List<String> extractCustomerIds(List<Order> orders) {
        List<String> customerIds = new ArrayList<>(orders.size());
        for (Order order : orders) {
            customerIds.add(order.getCustomerId());
        }
        return customerIds;
    }
    
    // ❌ BAD: Default capacity causes resizing
    public Map<String, List<Order>> groupOrdersBad(List<Order> orders) {
        Map<String, List<Order>> grouped = new HashMap<>();  // Default capacity 16
        // Processing millions of orders will cause many resizes
    }
}
```

### Avoid Unnecessary Object Creation

```java
// ✅ GOOD: Reuse objects
public class DateFormatter {
    private static final DateTimeFormatter DATE_FORMATTER = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd");
    
    public String formatDate(LocalDate date) {
        return date.format(DATE_FORMATTER);  // Reuse formatter
    }
}

// ❌ BAD: Create new formatter each time
public String formatDateBad(LocalDate date) {
    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    return date.format(formatter);  // Creates new object every call
}

// ✅ GOOD: String concatenation with StringBuilder
public String buildLargeString(List<String> parts) {
    StringBuilder sb = new StringBuilder(parts.size() * 20);  // Estimate size
    for (String part : parts) {
        sb.append(part).append(",");
    }
    return sb.toString();
}

// ❌ BAD: String concatenation in loop
public String buildLargeStringBad(List<String> parts) {
    String result = "";
    for (String part : parts) {
        result += part + ",";  // Creates new String object each iteration!
    }
    return result;
}
```

---

## Testing Standards

### Unit Test Structure

```java
public class OrderValidatorTest {
    
    private OrderValidator validator;
    
    @BeforeEach
    void setUp() {
        validator = new OrderValidator();
    }
    
    // ✅ GOOD: Clear test method names
    @Test
    @DisplayName("Should throw ValidationException when order ID is null")
    void shouldThrowException_WhenOrderIdIsNull() {
        // Given
        Order order = new Order(null, "CUST001", new BigDecimal("100.00"), LocalDateTime.now());
        
        // When & Then
        ValidationException exception = assertThrows(
            ValidationException.class,
            () -> validator.validateOrder(order)
        );
        
        assertTrue(exception.getMessage().contains("Order ID is required"));
    }
    
    @Test
    @DisplayName("Should validate successfully when order is valid")
    void shouldValidateSuccessfully_WhenOrderIsValid() {
        // Given
        Order validOrder = new Order(
            "ORD001",
            "CUST001",
            new BigDecimal("100.00"),
            LocalDateTime.now()
        );
        
        // When & Then
        assertDoesNotThrow(() -> validator.validateOrder(validOrder));
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"", "   "})
    @DisplayName("Should throw ValidationException for blank order IDs")
    void shouldThrowException_ForBlankOrderIds(String orderId) {
        // Given
        Order order = new Order(orderId, "CUST001", new BigDecimal("100.00"), LocalDateTime.now());
        
        // When & Then
        assertThrows(ValidationException.class, () -> validator.validateOrder(order));
    }
}
```

### Integration Test Example

```java
@SpringBootTest
@TestPropertySource(locations = "classpath:test.properties")
public class OrderProcessorIntegrationTest {
    
    @Autowired
    private OrderProcessor orderProcessor;
    
    @Autowired
    private DataSource dataSource;
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @BeforeEach
    void setUp() {
        // Clean up test data
        jdbcTemplate.execute("DELETE FROM orders");
    }
    
    @Test
    @DisplayName("Should process orders end-to-end successfully")
    void shouldProcessOrdersEndToEnd() {
        // Given: Insert test data
        jdbcTemplate.execute("INSERT INTO source_orders VALUES ('ORD001', 'CUST001', 100.00)");
        
        // When: Process orders
        ProcessingResult result = orderProcessor.processOrders();
        
        // Then: Verify results
        assertTrue(result.isSuccess());
        assertEquals(1, result.getProcessedCount());
        
        // Verify data in destination
        Integer count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM processed_orders WHERE order_id = 'ORD001'",
            Integer.class
        );
        assertEquals(1, count);
    }
}
```

---

## Documentation Standards

### Javadoc Best Practices

```java
/**
 * Processes customer orders from various data sources.
 * 
 * <p>This processor handles the complete order processing workflow:
 * <ul>
 *   <li>Reading orders from configured data source</li>
 *   <li>Validating order data against business rules</li>
 *   <li>Applying transformations and enrichments</li>
 *   <li>Loading processed orders to destination</li>
 * </ul>
 * 
 * <p>Example usage:
 * <pre>{@code
 * OrderProcessor processor = new OrderProcessor(dataSource, transformer, loader);
 * ProcessingResult result = processor.processOrders();
 * if (result.isSuccess()) {
 *     System.out.println("Processed " + result.getProcessedCount() + " orders");
 * }
 * }</pre>
 * 
 * @author Your Name
 * @since 1.0
 * @see DataSource
 * @see DataTransformer
 */
public class OrderProcessor {
    
    /**
     * Processes all orders from the configured data source.
     * 
     * <p>This method reads orders, validates them, applies transformations,
     * and loads them to the destination. Invalid orders are logged but don't
     * stop processing of other orders.
     * 
     * @return {@link ProcessingResult} containing success status and count of processed orders
     * @throws DataSourceException if unable to read from data source
     * @throws DataLoaderException if unable to write to destination
     */
    public ProcessingResult processOrders() {
        // Implementation
    }
    
    /**
     * Validates an order against business rules.
     * 
     * @param order the order to validate, must not be null
     * @return {@code true} if order is valid, {@code false} otherwise
     * @throws NullPointerException if order is null
     */
    private boolean isValidOrder(Order order) {
        // Implementation
    }
}
```

---

## Summary Checklist

### Code Quality
- [ ] Follow naming conventions (PascalCase, camelCase, UPPER_CASE)
- [ ] Organize code in logical packages
- [ ] Use meaningful names (no abbreviations)
- [ ] Keep methods short (< 30 lines)
- [ ] One responsibility per class/method

### Best Practices
- [ ] Use Builder pattern for complex objects
- [ ] Prefer immutability
- [ ] Use streams for collections
- [ ] Avoid premature optimization
- [ ] Follow SOLID principles

### Error Handling
- [ ] Use specific exceptions
- [ ] Try-with-resources for cleanup
- [ ] Fail fast with validation
- [ ] Log errors appropriately
- [ ] Don't swallow exceptions

### Performance
- [ ] Initialize collections with capacity
- [ ] Reuse objects when possible
- [ ] Use appropriate data structures
- [ ] Profile before optimizing
- [ ] Consider parallel streams for large data

### Testing
- [ ] Write clear test names
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] Test edge cases
- [ ] Aim for 80%+ coverage
- [ ] Write integration tests

### Documentation
- [ ] Javadoc for public APIs
- [ ] Comments for complex logic
- [ ] README for project setup
- [ ] Examples in documentation
- [ ] Keep docs up-to-date

---

**Remember**: Code is read more often than written. Optimize for readability and maintainability.
