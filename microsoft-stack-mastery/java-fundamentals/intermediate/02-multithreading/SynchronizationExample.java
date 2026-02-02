package com.microsoft.java.intermediate.multithreading;

import java.util.concurrent.locks.*;

/**
 * SynchronizationExample demonstrates thread synchronization mechanisms in Java.
 * Covers synchronized methods, synchronized blocks, locks, and race conditions.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class SynchronizationExample {
    
    /**
     * Demonstrates race condition without synchronization.
     */
    public static class UnsafeCounter {
        private int count = 0;
        
        public void increment() {
            count++; // NOT thread-safe (read-modify-write)
        }
        
        public int getCount() {
            return count;
        }
    }
    
    /**
     * Demonstrates synchronized method for thread safety.
     */
    public static class SafeCounter {
        private int count = 0;
        
        public synchronized void increment() {
            count++; // Thread-safe
        }
        
        public synchronized int getCount() {
            return count;
        }
    }
    
    /**
     * Demonstrates synchronized blocks for fine-grained control.
     */
    public static class BankAccount {
        private double balance;
        private final Object balanceLock = new Object();
        
        public BankAccount(double initialBalance) {
            this.balance = initialBalance;
        }
        
        public void deposit(double amount) {
            synchronized (balanceLock) {
                double newBalance = balance + amount;
                // Simulate processing time
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                balance = newBalance;
                System.out.println(Thread.currentThread().getName() + 
                    " deposited " + amount + ", balance: " + balance);
            }
        }
        
        public void withdraw(double amount) {
            synchronized (balanceLock) {
                if (balance >= amount) {
                    balance -= amount;
                    System.out.println(Thread.currentThread().getName() + 
                        " withdrew " + amount + ", balance: " + balance);
                } else {
                    System.out.println(Thread.currentThread().getName() + 
                        " insufficient funds for withdrawal: " + amount);
                }
            }
        }
        
        public synchronized double getBalance() {
            return balance;
        }
    }
    
    /**
     * Demonstrates ReentrantLock for advanced synchronization.
     */
    public static class LockBasedCounter {
        private int count = 0;
        private final ReentrantLock lock = new ReentrantLock();
        
        public void increment() {
            lock.lock();
            try {
                count++;
            } finally {
                lock.unlock(); // Always unlock in finally block
            }
        }
        
        public boolean tryIncrement(long timeoutMs) {
            try {
                if (lock.tryLock(timeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS)) {
                    try {
                        count++;
                        return true;
                    } finally {
                        lock.unlock();
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return false;
        }
        
        public int getCount() {
            lock.lock();
            try {
                return count;
            } finally {
                lock.unlock();
            }
        }
    }
    
    /**
     * Demonstrates ReadWriteLock for optimized read-heavy scenarios.
     */
    public static class ReadWriteCache {
        private String data = "initial";
        private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
        private final Lock readLock = rwLock.readLock();
        private final Lock writeLock = rwLock.writeLock();
        
        public String read() {
            readLock.lock();
            try {
                System.out.println(Thread.currentThread().getName() + " reading: " + data);
                Thread.sleep(100); // Simulate read operation
                return data;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return null;
            } finally {
                readLock.unlock();
            }
        }
        
        public void write(String newData) {
            writeLock.lock();
            try {
                System.out.println(Thread.currentThread().getName() + " writing: " + newData);
                Thread.sleep(200); // Simulate write operation
                data = newData;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                writeLock.unlock();
            }
        }
    }
    
    /**
     * Demonstrates deadlock scenario.
     */
    public static class DeadlockDemo {
        private final Object lock1 = new Object();
        private final Object lock2 = new Object();
        
        public void method1() {
            synchronized (lock1) {
                System.out.println(Thread.currentThread().getName() + " acquired lock1");
                
                try {
                    Thread.sleep(50);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                
                System.out.println(Thread.currentThread().getName() + " waiting for lock2");
                synchronized (lock2) {
                    System.out.println(Thread.currentThread().getName() + " acquired lock2");
                }
            }
        }
        
        public void method2() {
            synchronized (lock2) {
                System.out.println(Thread.currentThread().getName() + " acquired lock2");
                
                try {
                    Thread.sleep(50);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                
                System.out.println(Thread.currentThread().getName() + " waiting for lock1");
                synchronized (lock1) {
                    System.out.println(Thread.currentThread().getName() + " acquired lock1");
                }
            }
        }
    }
    
    /**
     * Demonstrates wait() and notify() for thread communication.
     */
    public static class ProducerConsumer {
        private int value;
        private boolean available = false;
        
        public synchronized void produce(int newValue) {
            while (available) {
                try {
                    wait(); // Wait until consumed
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            
            value = newValue;
            available = true;
            System.out.println("Produced: " + value);
            notify(); // Notify consumer
        }
        
        public synchronized int consume() {
            while (!available) {
                try {
                    wait(); // Wait until produced
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            
            available = false;
            System.out.println("Consumed: " + value);
            notify(); // Notify producer
            return value;
        }
    }
    
    /**
     * Tests race condition without synchronization.
     */
    public static void testRaceCondition() throws InterruptedException {
        System.out.println("=== Race Condition (Unsafe Counter) ===");
        
        UnsafeCounter counter = new UnsafeCounter();
        Thread[] threads = new Thread[5];
        
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.increment();
                }
            });
            threads[i].start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("Expected: 5000, Actual: " + counter.getCount());
    }
    
    /**
     * Tests synchronized method.
     */
    public static void testSynchronizedMethod() throws InterruptedException {
        System.out.println("\n=== Synchronized Method (Safe Counter) ===");
        
        SafeCounter counter = new SafeCounter();
        Thread[] threads = new Thread[5];
        
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.increment();
                }
            });
            threads[i].start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("Expected: 5000, Actual: " + counter.getCount());
    }
    
    /**
     * Tests synchronized block with bank account.
     */
    public static void testSynchronizedBlock() throws InterruptedException {
        System.out.println("\n=== Synchronized Block (Bank Account) ===");
        
        BankAccount account = new BankAccount(1000.0);
        
        Thread depositor1 = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                account.deposit(100.0);
            }
        }, "Depositor-1");
        
        Thread depositor2 = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                account.deposit(50.0);
            }
        }, "Depositor-2");
        
        Thread withdrawer = new Thread(() -> {
            for (int i = 0; i < 3; i++) {
                account.withdraw(150.0);
            }
        }, "Withdrawer");
        
        depositor1.start();
        depositor2.start();
        withdrawer.start();
        
        depositor1.join();
        depositor2.join();
        withdrawer.join();
        
        System.out.println("Final balance: " + account.getBalance());
    }
    
    /**
     * Tests ReentrantLock.
     */
    public static void testReentrantLock() throws InterruptedException {
        System.out.println("\n=== ReentrantLock ===");
        
        LockBasedCounter counter = new LockBasedCounter();
        
        Thread[] threads = new Thread[3];
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 100; j++) {
                    counter.increment();
                }
            });
            threads[i].start();
        }
        
        for (Thread thread : threads) {
            thread.join();
        }
        
        System.out.println("Counter value: " + counter.getCount());
    }
    
    /**
     * Tests ReadWriteLock.
     */
    public static void testReadWriteLock() throws InterruptedException {
        System.out.println("\n=== ReadWriteLock ===");
        
        ReadWriteCache cache = new ReadWriteCache();
        
        // Multiple readers
        Thread reader1 = new Thread(cache::read, "Reader-1");
        Thread reader2 = new Thread(cache::read, "Reader-2");
        Thread reader3 = new Thread(cache::read, "Reader-3");
        
        // One writer
        Thread writer = new Thread(() -> cache.write("updated"), "Writer");
        
        reader1.start();
        reader2.start();
        writer.start();
        reader3.start();
        
        reader1.join();
        reader2.join();
        writer.join();
        reader3.join();
    }
    
    /**
     * Tests producer-consumer pattern.
     */
    public static void testProducerConsumer() throws InterruptedException {
        System.out.println("\n=== Producer-Consumer ===");
        
        ProducerConsumer pc = new ProducerConsumer();
        
        Thread producer = new Thread(() -> {
            for (int i = 1; i <= 5; i++) {
                pc.produce(i);
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }, "Producer");
        
        Thread consumer = new Thread(() -> {
            for (int i = 1; i <= 5; i++) {
                pc.consume();
                try {
                    Thread.sleep(150);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }, "Consumer");
        
        producer.start();
        consumer.start();
        
        producer.join();
        consumer.join();
    }
    
    /**
     * Main method demonstrating synchronization examples.
     */
    public static void main(String[] args) {
        try {
            testRaceCondition();
            testSynchronizedMethod();
            testSynchronizedBlock();
            testReentrantLock();
            testReadWriteLock();
            testProducerConsumer();
            
            System.out.println("\n=== All synchronization examples completed ===");
        } catch (InterruptedException e) {
            System.err.println("Main thread interrupted");
            Thread.currentThread().interrupt();
        }
    }
}
