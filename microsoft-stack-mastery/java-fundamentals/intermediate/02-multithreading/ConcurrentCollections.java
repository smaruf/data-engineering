package com.microsoft.java.intermediate.multithreading;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/**
 * ConcurrentCollections demonstrates thread-safe collection classes in Java.
 * Covers ConcurrentHashMap, BlockingQueue, CopyOnWriteArrayList, and atomic variables.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class ConcurrentCollections {
    
    /**
     * Demonstrates ConcurrentHashMap for thread-safe map operations.
     */
    public static void demonstrateConcurrentHashMap() {
        System.out.println("=== ConcurrentHashMap ===");
        
        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
        
        // Multiple threads updating the map
        ExecutorService executor = Executors.newFixedThreadPool(3);
        
        for (int i = 0; i < 5; i++) {
            final int threadNum = i;
            executor.submit(() -> {
                String key = "Thread-" + threadNum;
                map.put(key, threadNum * 10);
                System.out.println(Thread.currentThread().getName() + 
                    " added: " + key + " = " + map.get(key));
            });
        }
        
        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Atomic operations
        map.putIfAbsent("NewKey", 100);
        System.out.println("After putIfAbsent: " + map);
        
        // Compute if absent
        map.computeIfAbsent("ComputedKey", k -> k.length() * 10);
        System.out.println("After computeIfAbsent: ComputedKey = " + map.get("ComputedKey"));
        
        // Merge operation
        map.merge("Thread-0", 5, Integer::sum);
        System.out.println("After merge: Thread-0 = " + map.get("Thread-0"));
        
        System.out.println("Final map: " + map);
        System.out.println();
    }
    
    /**
     * Demonstrates BlockingQueue with producer-consumer pattern.
     */
    public static void demonstrateBlockingQueue() {
        System.out.println("=== BlockingQueue (Producer-Consumer) ===");
        
        BlockingQueue<Integer> queue = new LinkedBlockingQueue<>(5);
        
        // Producer thread
        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 10; i++) {
                    System.out.println("Producing: " + i);
                    queue.put(i); // Blocks if queue is full
                    Thread.sleep(100);
                }
                queue.put(-1); // Poison pill to stop consumer
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "Producer");
        
        // Consumer thread
        Thread consumer = new Thread(() -> {
            try {
                while (true) {
                    Integer item = queue.take(); // Blocks if queue is empty
                    if (item == -1) {
                        System.out.println("Consumer received stop signal");
                        break;
                    }
                    System.out.println("Consuming: " + item);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "Consumer");
        
        producer.start();
        consumer.start();
        
        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates PriorityBlockingQueue.
     */
    public static void demonstratePriorityBlockingQueue() {
        System.out.println("=== PriorityBlockingQueue ===");
        
        PriorityBlockingQueue<Task> queue = new PriorityBlockingQueue<>();
        
        // Add tasks with different priorities
        queue.add(new Task("Low Priority Task", 3));
        queue.add(new Task("High Priority Task", 1));
        queue.add(new Task("Medium Priority Task", 2));
        queue.add(new Task("Critical Task", 0));
        
        // Tasks are processed by priority
        System.out.println("Processing tasks by priority:");
        while (!queue.isEmpty()) {
            try {
                Task task = queue.take();
                System.out.println("Processing: " + task);
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        System.out.println();
    }
    
    /**
     * Task class for priority queue demonstration.
     */
    static class Task implements Comparable<Task> {
        private final String name;
        private final int priority;
        
        public Task(String name, int priority) {
            this.name = name;
            this.priority = priority;
        }
        
        @Override
        public int compareTo(Task other) {
            return Integer.compare(this.priority, other.priority);
        }
        
        @Override
        public String toString() {
            return name + " (Priority: " + priority + ")";
        }
    }
    
    /**
     * Demonstrates CopyOnWriteArrayList.
     */
    public static void demonstrateCopyOnWriteArrayList() {
        System.out.println("=== CopyOnWriteArrayList ===");
        
        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
        
        // Add initial elements
        list.addAll(Arrays.asList("A", "B", "C"));
        
        // Thread that iterates over list
        Thread reader = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                System.out.println("Reading iteration " + (i + 1) + ":");
                for (String item : list) {
                    System.out.println("  " + item);
                    try {
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }
        }, "Reader");
        
        // Thread that modifies list
        Thread writer = new Thread(() -> {
            try {
                Thread.sleep(150);
                list.add("D");
                System.out.println("Writer added: D");
                Thread.sleep(150);
                list.add("E");
                System.out.println("Writer added: E");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "Writer");
        
        reader.start();
        writer.start();
        
        try {
            reader.join();
            writer.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println("Final list: " + list);
        System.out.println();
    }
    
    /**
     * Demonstrates ConcurrentSkipListMap (sorted concurrent map).
     */
    public static void demonstrateConcurrentSkipListMap() {
        System.out.println("=== ConcurrentSkipListMap ===");
        
        ConcurrentSkipListMap<Integer, String> map = new ConcurrentSkipListMap<>();
        
        // Add elements in random order
        map.put(5, "Five");
        map.put(2, "Two");
        map.put(8, "Eight");
        map.put(1, "One");
        map.put(9, "Nine");
        
        System.out.println("Sorted map: " + map);
        System.out.println("First key: " + map.firstKey());
        System.out.println("Last key: " + map.lastKey());
        
        // Range queries
        System.out.println("SubMap (2-8): " + map.subMap(2, 8));
        System.out.println("HeadMap (<5): " + map.headMap(5));
        System.out.println("TailMap (>=5): " + map.tailMap(5));
        
        System.out.println();
    }
    
    /**
     * Demonstrates AtomicInteger for lock-free operations.
     */
    public static void demonstrateAtomicInteger() {
        System.out.println("=== AtomicInteger ===");
        
        AtomicInteger counter = new AtomicInteger(0);
        ExecutorService executor = Executors.newFixedThreadPool(5);
        
        for (int i = 0; i < 5; i++) {
            executor.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.incrementAndGet();
                }
            });
        }
        
        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println("Final counter value: " + counter.get());
        
        // Other atomic operations
        counter.set(10);
        System.out.println("After set(10): " + counter.get());
        
        int previousValue = counter.getAndAdd(5);
        System.out.println("getAndAdd(5) - previous: " + previousValue + 
            ", current: " + counter.get());
        
        boolean updated = counter.compareAndSet(15, 100);
        System.out.println("compareAndSet(15, 100): " + updated + 
            ", value: " + counter.get());
        
        System.out.println();
    }
    
    /**
     * Demonstrates AtomicReference for object references.
     */
    public static void demonstrateAtomicReference() {
        System.out.println("=== AtomicReference ===");
        
        AtomicReference<String> ref = new AtomicReference<>("Initial");
        
        System.out.println("Initial value: " + ref.get());
        
        // Update and get
        String oldValue = ref.getAndSet("Updated");
        System.out.println("Old value: " + oldValue + ", New value: " + ref.get());
        
        // Compare and set
        boolean success = ref.compareAndSet("Updated", "Final");
        System.out.println("CAS success: " + success + ", Value: " + ref.get());
        
        // Update with function
        ref.updateAndGet(s -> s.toUpperCase());
        System.out.println("After updateAndGet: " + ref.get());
        
        System.out.println();
    }
    
    /**
     * Demonstrates CountDownLatch for thread coordination.
     */
    public static void demonstrateCountDownLatch() {
        System.out.println("=== CountDownLatch ===");
        
        int workerCount = 3;
        CountDownLatch latch = new CountDownLatch(workerCount);
        
        for (int i = 1; i <= workerCount; i++) {
            final int workerId = i;
            new Thread(() -> {
                try {
                    System.out.println("Worker " + workerId + " starting...");
                    Thread.sleep(1000 + workerId * 500);
                    System.out.println("Worker " + workerId + " completed");
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    latch.countDown();
                }
            }).start();
        }
        
        try {
            System.out.println("Main thread waiting for workers...");
            latch.await();
            System.out.println("All workers completed!");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates CyclicBarrier for synchronization points.
     */
    public static void demonstrateCyclicBarrier() {
        System.out.println("=== CyclicBarrier ===");
        
        int parties = 3;
        CyclicBarrier barrier = new CyclicBarrier(parties, () -> {
            System.out.println("*** All threads reached barrier ***");
        });
        
        for (int i = 1; i <= parties; i++) {
            final int threadNum = i;
            new Thread(() -> {
                try {
                    System.out.println("Thread " + threadNum + " doing phase 1");
                    Thread.sleep(1000 + threadNum * 200);
                    System.out.println("Thread " + threadNum + " reached barrier");
                    
                    barrier.await();
                    
                    System.out.println("Thread " + threadNum + " doing phase 2");
                    Thread.sleep(500);
                    System.out.println("Thread " + threadNum + " finished");
                    
                } catch (InterruptedException | BrokenBarrierException e) {
                    e.printStackTrace();
                }
            }).start();
        }
        
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates Semaphore for resource access control.
     */
    public static void demonstrateSemaphore() {
        System.out.println("=== Semaphore ===");
        
        Semaphore semaphore = new Semaphore(2); // Only 2 permits
        
        for (int i = 1; i <= 5; i++) {
            final int threadNum = i;
            new Thread(() -> {
                try {
                    System.out.println("Thread " + threadNum + " waiting for permit...");
                    semaphore.acquire();
                    System.out.println("Thread " + threadNum + " acquired permit");
                    
                    Thread.sleep(1000);
                    
                    System.out.println("Thread " + threadNum + " releasing permit");
                    semaphore.release();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
        
        try {
            Thread.sleep(6000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println();
    }
    
    /**
     * Main method demonstrating concurrent collections.
     */
    public static void main(String[] args) {
        System.out.println("Java Concurrent Collections Examples\n");
        
        demonstrateConcurrentHashMap();
        demonstrateBlockingQueue();
        demonstratePriorityBlockingQueue();
        demonstrateCopyOnWriteArrayList();
        demonstrateConcurrentSkipListMap();
        demonstrateAtomicInteger();
        demonstrateAtomicReference();
        demonstrateCountDownLatch();
        demonstrateCyclicBarrier();
        demonstrateSemaphore();
        
        System.out.println("=== All concurrent collection examples completed ===");
    }
}
