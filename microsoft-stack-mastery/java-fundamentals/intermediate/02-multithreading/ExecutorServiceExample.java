package com.microsoft.java.intermediate.multithreading;

import java.util.*;
import java.util.concurrent.*;

/**
 * ExecutorServiceExample demonstrates thread pool management and task execution.
 * Covers ExecutorService, Callable, Future, and various thread pool types.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class ExecutorServiceExample {
    
    /**
     * Simple Runnable task for demonstration.
     */
    public static class SimpleTask implements Runnable {
        private final int taskId;
        
        public SimpleTask(int taskId) {
            this.taskId = taskId;
        }
        
        @Override
        public void run() {
            String threadName = Thread.currentThread().getName();
            System.out.println("Task " + taskId + " started on " + threadName);
            
            try {
                Thread.sleep(1000);
                System.out.println("Task " + taskId + " completed on " + threadName);
            } catch (InterruptedException e) {
                System.err.println("Task " + taskId + " interrupted");
                Thread.currentThread().interrupt();
            }
        }
    }
    
    /**
     * Callable task that returns a result.
     */
    public static class CalculationTask implements Callable<Integer> {
        private final int number;
        
        public CalculationTask(int number) {
            this.number = number;
        }
        
        @Override
        public Integer call() throws Exception {
            String threadName = Thread.currentThread().getName();
            System.out.println("Calculating factorial of " + number + " on " + threadName);
            
            Thread.sleep(500);
            
            int result = factorial(number);
            System.out.println("Factorial of " + number + " = " + result);
            return result;
        }
        
        private int factorial(int n) {
            if (n <= 1) return 1;
            return n * factorial(n - 1);
        }
    }
    
    /**
     * Demonstrates FixedThreadPool.
     */
    public static void demonstrateFixedThreadPool() {
        System.out.println("=== Fixed Thread Pool ===");
        
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        try {
            for (int i = 1; i <= 6; i++) {
                executor.submit(new SimpleTask(i));
            }
            
            System.out.println("All tasks submitted");
            
        } finally {
            executor.shutdown();
            try {
                if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                    executor.shutdownNow();
                }
                System.out.println("Executor shutdown completed\n");
            } catch (InterruptedException e) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
    
    /**
     * Demonstrates CachedThreadPool.
     */
    public static void demonstrateCachedThreadPool() {
        System.out.println("=== Cached Thread Pool ===");
        
        ExecutorService executor = Executors.newCachedThreadPool();
        
        try {
            for (int i = 1; i <= 5; i++) {
                executor.submit(new SimpleTask(i));
                Thread.sleep(200); // Stagger submissions
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            executor.shutdown();
            try {
                executor.awaitTermination(10, TimeUnit.SECONDS);
                System.out.println("Executor shutdown completed\n");
            } catch (InterruptedException e) {
                executor.shutdownNow();
            }
        }
    }
    
    /**
     * Demonstrates SingleThreadExecutor.
     */
    public static void demonstrateSingleThreadExecutor() {
        System.out.println("=== Single Thread Executor ===");
        
        ExecutorService executor = Executors.newSingleThreadExecutor();
        
        try {
            for (int i = 1; i <= 4; i++) {
                final int taskId = i;
                executor.submit(() -> {
                    System.out.println("Sequential task " + taskId + " executing");
                    try {
                        Thread.sleep(500);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                });
            }
            
        } finally {
            executor.shutdown();
            try {
                executor.awaitTermination(10, TimeUnit.SECONDS);
                System.out.println("Executor shutdown completed\n");
            } catch (InterruptedException e) {
                executor.shutdownNow();
            }
        }
    }
    
    /**
     * Demonstrates Callable and Future.
     */
    public static void demonstrateCallableAndFuture() {
        System.out.println("=== Callable and Future ===");
        
        ExecutorService executor = Executors.newFixedThreadPool(3);
        List<Future<Integer>> futures = new ArrayList<>();
        
        try {
            // Submit multiple Callable tasks
            for (int i = 1; i <= 5; i++) {
                Future<Integer> future = executor.submit(new CalculationTask(i));
                futures.add(future);
            }
            
            // Retrieve results
            System.out.println("\nRetrieving results:");
            for (int i = 0; i < futures.size(); i++) {
                try {
                    Integer result = futures.get(i).get(5, TimeUnit.SECONDS);
                    System.out.println("Result " + (i + 1) + ": " + result);
                } catch (ExecutionException e) {
                    System.err.println("Task execution failed: " + e.getCause());
                } catch (TimeoutException e) {
                    System.err.println("Task timed out");
                    futures.get(i).cancel(true);
                }
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            executor.shutdown();
            System.out.println();
        }
    }
    
    /**
     * Demonstrates invokeAll for batch task execution.
     */
    public static void demonstrateInvokeAll() {
        System.out.println("=== InvokeAll ===");
        
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        try {
            List<Callable<String>> tasks = Arrays.asList(
                () -> {
                    Thread.sleep(1000);
                    return "Task 1 result";
                },
                () -> {
                    Thread.sleep(500);
                    return "Task 2 result";
                },
                () -> {
                    Thread.sleep(1500);
                    return "Task 3 result";
                }
            );
            
            System.out.println("Executing all tasks...");
            List<Future<String>> results = executor.invokeAll(tasks, 10, TimeUnit.SECONDS);
            
            for (int i = 0; i < results.size(); i++) {
                Future<String> future = results.get(i);
                if (future.isDone() && !future.isCancelled()) {
                    System.out.println("Result " + (i + 1) + ": " + future.get());
                }
            }
            
        } catch (InterruptedException | ExecutionException e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            executor.shutdown();
            System.out.println();
        }
    }
    
    /**
     * Demonstrates invokeAny for racing tasks.
     */
    public static void demonstrateInvokeAny() {
        System.out.println("=== InvokeAny ===");
        
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        try {
            List<Callable<String>> tasks = Arrays.asList(
                () -> {
                    Thread.sleep(2000);
                    return "Slow task result";
                },
                () -> {
                    Thread.sleep(500);
                    return "Fast task result";
                },
                () -> {
                    Thread.sleep(1000);
                    return "Medium task result";
                }
            );
            
            System.out.println("Racing tasks (first to complete wins)...");
            String result = executor.invokeAny(tasks, 5, TimeUnit.SECONDS);
            System.out.println("Winner result: " + result);
            
        } catch (InterruptedException | ExecutionException | TimeoutException e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            executor.shutdown();
            System.out.println();
        }
    }
    
    /**
     * Demonstrates ScheduledExecutorService.
     */
    public static void demonstrateScheduledExecutor() {
        System.out.println("=== Scheduled Executor ===");
        
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
        
        try {
            // Schedule one-time task with delay
            System.out.println("Scheduling one-time task with 2 second delay");
            scheduler.schedule(() -> {
                System.out.println("One-time task executed at " + 
                    System.currentTimeMillis());
            }, 2, TimeUnit.SECONDS);
            
            // Schedule recurring task at fixed rate
            System.out.println("Scheduling fixed-rate task (every 1 second)");
            ScheduledFuture<?> fixedRate = scheduler.scheduleAtFixedRate(() -> {
                System.out.println("Fixed-rate task executed at " + 
                    System.currentTimeMillis());
            }, 1, 1, TimeUnit.SECONDS);
            
            // Let it run for a while
            Thread.sleep(4000);
            fixedRate.cancel(true);
            
            // Schedule with fixed delay
            System.out.println("Scheduling fixed-delay task");
            ScheduledFuture<?> fixedDelay = scheduler.scheduleWithFixedDelay(() -> {
                System.out.println("Fixed-delay task started");
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("Fixed-delay task completed");
            }, 0, 1, TimeUnit.SECONDS);
            
            Thread.sleep(3000);
            fixedDelay.cancel(true);
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            scheduler.shutdown();
            System.out.println("Scheduler shutdown\n");
        }
    }
    
    /**
     * Demonstrates ThreadPoolExecutor with custom configuration.
     */
    public static void demonstrateCustomThreadPool() {
        System.out.println("=== Custom Thread Pool ===");
        
        ThreadPoolExecutor executor = new ThreadPoolExecutor(
            2,                      // Core pool size
            4,                      // Maximum pool size
            60,                     // Keep alive time
            TimeUnit.SECONDS,       // Time unit
            new LinkedBlockingQueue<>(10),  // Work queue
            new ThreadPoolExecutor.CallerRunsPolicy()  // Rejection policy
        );
        
        try {
            System.out.println("Pool size: " + executor.getPoolSize());
            System.out.println("Active threads: " + executor.getActiveCount());
            
            for (int i = 1; i <= 8; i++) {
                executor.submit(new SimpleTask(i));
            }
            
            Thread.sleep(500);
            System.out.println("Pool size after submission: " + executor.getPoolSize());
            System.out.println("Active threads: " + executor.getActiveCount());
            System.out.println("Queue size: " + executor.getQueue().size());
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            executor.shutdown();
            try {
                executor.awaitTermination(10, TimeUnit.SECONDS);
                System.out.println("Custom executor shutdown\n");
            } catch (InterruptedException e) {
                executor.shutdownNow();
            }
        }
    }
    
    /**
     * Demonstrates CompletableFuture for asynchronous programming.
     */
    public static void demonstrateCompletableFuture() {
        System.out.println("=== CompletableFuture ===");
        
        // Simple async task
        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
            System.out.println("Async task running on " + Thread.currentThread().getName());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "Hello";
        });
        
        // Chain operations
        CompletableFuture<String> future2 = future1
            .thenApply(s -> s + " World")
            .thenApply(String::toUpperCase);
        
        try {
            System.out.println("Result: " + future2.get());
        } catch (InterruptedException | ExecutionException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        // Combine multiple futures
        CompletableFuture<Integer> futureA = CompletableFuture.supplyAsync(() -> 10);
        CompletableFuture<Integer> futureB = CompletableFuture.supplyAsync(() -> 20);
        
        CompletableFuture<Integer> combined = futureA.thenCombine(futureB, (a, b) -> a + b);
        
        try {
            System.out.println("Combined result: " + combined.get());
        } catch (InterruptedException | ExecutionException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Main method demonstrating executor service examples.
     */
    public static void main(String[] args) {
        System.out.println("Java ExecutorService Examples\n");
        
        demonstrateFixedThreadPool();
        demonstrateCachedThreadPool();
        demonstrateSingleThreadExecutor();
        demonstrateCallableAndFuture();
        demonstrateInvokeAll();
        demonstrateInvokeAny();
        demonstrateScheduledExecutor();
        demonstrateCustomThreadPool();
        demonstrateCompletableFuture();
        
        System.out.println("=== All executor examples completed ===");
    }
}
