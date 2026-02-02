package com.microsoft.java.intermediate.multithreading;

/**
 * ThreadBasics demonstrates fundamental thread concepts in Java.
 * Covers thread creation, Runnable interface, thread lifecycle, and basic operations.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class ThreadBasics {
    
    /**
     * Example of extending Thread class.
     */
    public static class CounterThread extends Thread {
        private final String threadName;
        private final int maxCount;
        
        public CounterThread(String threadName, int maxCount) {
            super(threadName);
            this.threadName = threadName;
            this.maxCount = maxCount;
        }
        
        @Override
        public void run() {
            System.out.println(threadName + " started (ID: " + getId() + ")");
            
            for (int i = 1; i <= maxCount; i++) {
                System.out.println(threadName + ": " + i);
                
                try {
                    Thread.sleep(500); // Simulate work
                } catch (InterruptedException e) {
                    System.err.println(threadName + " interrupted");
                    return;
                }
            }
            
            System.out.println(threadName + " completed");
        }
    }
    
    /**
     * Example of implementing Runnable interface (preferred approach).
     */
    public static class Task implements Runnable {
        private final String taskName;
        private final int iterations;
        
        public Task(String taskName, int iterations) {
            this.taskName = taskName;
            this.iterations = iterations;
        }
        
        @Override
        public void run() {
            Thread currentThread = Thread.currentThread();
            System.out.println(taskName + " running on thread: " + 
                currentThread.getName() + " (ID: " + currentThread.getId() + ")");
            
            for (int i = 1; i <= iterations; i++) {
                System.out.println(taskName + " - iteration " + i);
                
                try {
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    System.err.println(taskName + " interrupted");
                    Thread.currentThread().interrupt(); // Restore interrupt status
                    return;
                }
            }
            
            System.out.println(taskName + " finished");
        }
    }
    
    /**
     * Demonstrates thread creation using Thread class.
     */
    public static void demonstrateThreadExtension() {
        System.out.println("=== Thread Extension Example ===");
        
        CounterThread thread1 = new CounterThread("Counter-1", 3);
        CounterThread thread2 = new CounterThread("Counter-2", 3);
        
        System.out.println("Starting threads...");
        thread1.start();
        thread2.start();
        
        try {
            // Wait for threads to complete
            thread1.join();
            thread2.join();
            System.out.println("All threads completed");
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
        }
    }
    
    /**
     * Demonstrates thread creation using Runnable interface.
     */
    public static void demonstrateRunnableInterface() {
        System.out.println("\n=== Runnable Interface Example ===");
        
        Task task1 = new Task("Task-A", 3);
        Task task2 = new Task("Task-B", 3);
        
        Thread thread1 = new Thread(task1);
        Thread thread2 = new Thread(task2);
        
        thread1.start();
        thread2.start();
        
        try {
            thread1.join();
            thread2.join();
            System.out.println("All tasks completed");
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
        }
    }
    
    /**
     * Demonstrates lambda expressions for creating threads (Java 8+).
     */
    public static void demonstrateLambdaThreads() {
        System.out.println("\n=== Lambda Thread Example ===");
        
        // Create thread using lambda expression
        Thread thread = new Thread(() -> {
            String name = Thread.currentThread().getName();
            System.out.println("Lambda thread " + name + " started");
            
            for (int i = 1; i <= 3; i++) {
                System.out.println(name + ": Processing item " + i);
                try {
                    Thread.sleep(400);
                } catch (InterruptedException e) {
                    System.err.println(name + " interrupted");
                    return;
                }
            }
            
            System.out.println("Lambda thread " + name + " completed");
        });
        
        thread.setName("Lambda-Worker");
        thread.start();
        
        try {
            thread.join();
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
        }
    }
    
    /**
     * Demonstrates thread priority.
     */
    public static void demonstrateThreadPriority() {
        System.out.println("\n=== Thread Priority Example ===");
        
        Runnable task = () -> {
            Thread current = Thread.currentThread();
            System.out.println(current.getName() + " priority: " + 
                current.getPriority() + " started");
            
            long sum = 0;
            for (int i = 0; i < 1000000; i++) {
                sum += i;
            }
            
            System.out.println(current.getName() + " completed with sum: " + sum);
        };
        
        Thread lowPriority = new Thread(task, "Low-Priority");
        Thread normalPriority = new Thread(task, "Normal-Priority");
        Thread highPriority = new Thread(task, "High-Priority");
        
        lowPriority.setPriority(Thread.MIN_PRIORITY);
        normalPriority.setPriority(Thread.NORM_PRIORITY);
        highPriority.setPriority(Thread.MAX_PRIORITY);
        
        lowPriority.start();
        normalPriority.start();
        highPriority.start();
        
        try {
            lowPriority.join();
            normalPriority.join();
            highPriority.join();
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
        }
    }
    
    /**
     * Demonstrates daemon threads.
     */
    public static void demonstrateDaemonThreads() {
        System.out.println("\n=== Daemon Thread Example ===");
        
        Thread daemonThread = new Thread(() -> {
            int count = 0;
            while (true) {
                count++;
                System.out.println("Daemon thread running... count: " + count);
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    break;
                }
            }
        });
        
        // Set as daemon thread (will terminate when main thread ends)
        daemonThread.setDaemon(true);
        daemonThread.setName("Background-Daemon");
        daemonThread.start();
        
        // Main thread sleeps for 2 seconds
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("Main thread ending (daemon will terminate)");
    }
    
    /**
     * Demonstrates thread interruption.
     */
    public static void demonstrateThreadInterruption() {
        System.out.println("\n=== Thread Interruption Example ===");
        
        Thread worker = new Thread(() -> {
            System.out.println("Worker thread started");
            
            try {
                for (int i = 1; i <= 10; i++) {
                    if (Thread.currentThread().isInterrupted()) {
                        System.out.println("Worker thread interrupted, exiting...");
                        return;
                    }
                    
                    System.out.println("Working... step " + i);
                    Thread.sleep(500);
                }
            } catch (InterruptedException e) {
                System.out.println("Worker thread sleep interrupted");
            }
            
            System.out.println("Worker thread completed");
        });
        
        worker.setName("Interruptible-Worker");
        worker.start();
        
        try {
            Thread.sleep(1500); // Let it work for a bit
            System.out.println("Main thread interrupting worker...");
            worker.interrupt();
            worker.join();
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
        }
    }
    
    /**
     * Demonstrates thread states and lifecycle.
     */
    public static void demonstrateThreadStates() {
        System.out.println("\n=== Thread States Example ===");
        
        Thread thread = new Thread(() -> {
            System.out.println("Thread running, state: " + Thread.currentThread().getState());
            
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        
        System.out.println("Before start, state: " + thread.getState()); // NEW
        
        thread.start();
        System.out.println("After start, state: " + thread.getState()); // RUNNABLE
        
        try {
            Thread.sleep(100);
            System.out.println("While sleeping, state: " + thread.getState()); // TIMED_WAITING
            
            thread.join();
            System.out.println("After completion, state: " + thread.getState()); // TERMINATED
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
        }
    }
    
    /**
     * Demonstrates thread information.
     */
    public static void demonstrateThreadInfo() {
        System.out.println("\n=== Thread Information ===");
        
        Thread currentThread = Thread.currentThread();
        System.out.println("Current Thread Name: " + currentThread.getName());
        System.out.println("Current Thread ID: " + currentThread.getId());
        System.out.println("Current Thread Priority: " + currentThread.getPriority());
        System.out.println("Current Thread State: " + currentThread.getState());
        System.out.println("Is Daemon: " + currentThread.isDaemon());
        System.out.println("Is Alive: " + currentThread.isAlive());
        System.out.println("Thread Group: " + currentThread.getThreadGroup().getName());
        
        System.out.println("\nActive threads in current group: " + 
            Thread.activeCount());
    }
    
    /**
     * Main method demonstrating all thread basics.
     */
    public static void main(String[] args) {
        System.out.println("Java Thread Basics Examples\n");
        
        demonstrateThreadInfo();
        demonstrateThreadExtension();
        demonstrateRunnableInterface();
        demonstrateLambdaThreads();
        demonstrateThreadPriority();
        demonstrateThreadStates();
        demonstrateThreadInterruption();
        demonstrateDaemonThreads();
        
        System.out.println("\n=== All examples completed ===");
    }
}
