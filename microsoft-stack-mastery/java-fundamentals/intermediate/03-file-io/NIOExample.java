package com.microsoft.java.intermediate.fileio;

import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.charset.*;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.util.*;
import java.util.stream.*;

/**
 * NIOExample demonstrates Java NIO (New I/O) operations.
 * Covers Path, Files, Channels, Buffers, and modern file operations.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class NIOExample {
    
    private static final String SAMPLE_DIR = "nio-test-dir";
    private static final String SAMPLE_FILE = "nio-sample.txt";
    
    /**
     * Demonstrates Path API for file system paths.
     */
    public static void demonstratePathAPI() {
        System.out.println("=== Path API ===");
        
        // Create paths
        Path path1 = Paths.get("folder", "subfolder", "file.txt");
        Path path2 = Paths.get("/home/user/documents");
        Path path3 = Paths.get(".");
        
        System.out.println("Path 1: " + path1);
        System.out.println("Path 2: " + path2);
        System.out.println("Path 3 (absolute): " + path3.toAbsolutePath());
        
        // Path operations
        System.out.println("\nPath Operations:");
        System.out.println("  File name: " + path1.getFileName());
        System.out.println("  Parent: " + path1.getParent());
        System.out.println("  Root: " + (path1.getRoot() != null ? path1.getRoot() : "null"));
        System.out.println("  Name count: " + path1.getNameCount());
        
        // Normalize path
        Path path4 = Paths.get("/home/user/../user/./documents");
        System.out.println("\nBefore normalize: " + path4);
        System.out.println("After normalize: " + path4.normalize());
        
        // Resolve paths
        Path base = Paths.get("/home/user");
        Path resolved = base.resolve("documents/file.txt");
        System.out.println("Resolved path: " + resolved);
        
        System.out.println();
    }
    
    /**
     * Demonstrates Files class for file operations.
     */
    public static void demonstrateFilesClass() {
        System.out.println("=== Files Class Operations ===");
        
        Path testFile = Paths.get(SAMPLE_FILE);
        
        try {
            // Write to file
            List<String> lines = Arrays.asList(
                "First line using NIO",
                "Second line with Files class",
                "Third line demonstrating modern Java I/O"
            );
            Files.write(testFile, lines, StandardCharsets.UTF_8);
            System.out.println("Written to file: " + testFile);
            
            // Read from file
            List<String> readLines = Files.readAllLines(testFile, StandardCharsets.UTF_8);
            System.out.println("Read " + readLines.size() + " lines:");
            readLines.forEach(line -> System.out.println("  " + line));
            
            // File properties
            System.out.println("\nFile Properties:");
            System.out.println("  Exists: " + Files.exists(testFile));
            System.out.println("  Size: " + Files.size(testFile) + " bytes");
            System.out.println("  Is Regular File: " + Files.isRegularFile(testFile));
            System.out.println("  Is Directory: " + Files.isDirectory(testFile));
            System.out.println("  Is Readable: " + Files.isReadable(testFile));
            System.out.println("  Is Writable: " + Files.isWritable(testFile));
            
            // File attributes
            BasicFileAttributes attrs = Files.readAttributes(testFile, BasicFileAttributes.class);
            System.out.println("\nFile Attributes:");
            System.out.println("  Creation Time: " + attrs.creationTime());
            System.out.println("  Last Modified: " + attrs.lastModifiedTime());
            System.out.println("  Last Access: " + attrs.lastAccessTime());
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates reading files with Streams (Java 8+).
     */
    public static void demonstrateFileStreams() {
        System.out.println("=== File Streams ===");
        
        Path testFile = Paths.get(SAMPLE_FILE);
        
        try {
            // Read all lines as Stream
            System.out.println("Processing lines with Stream:");
            try (Stream<String> lines = Files.lines(testFile)) {
                lines.filter(line -> line.contains("NIO"))
                     .map(String::toUpperCase)
                     .forEach(line -> System.out.println("  " + line));
            }
            
            // Count lines
            long lineCount = Files.lines(testFile).count();
            System.out.println("\nTotal lines: " + lineCount);
            
            // Find specific content
            System.out.println("\nSearching for 'line':");
            try (Stream<String> lines = Files.lines(testFile)) {
                lines.filter(line -> line.toLowerCase().contains("line"))
                     .forEach(line -> System.out.println("  Found: " + line));
            }
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates directory operations.
     */
    public static void demonstrateDirectoryOperations() {
        System.out.println("=== Directory Operations ===");
        
        Path directory = Paths.get(SAMPLE_DIR);
        
        try {
            // Create directory
            if (!Files.exists(directory)) {
                Files.createDirectory(directory);
                System.out.println("Created directory: " + directory);
            }
            
            // Create nested directories
            Path nested = Paths.get(SAMPLE_DIR, "sub1", "sub2");
            Files.createDirectories(nested);
            System.out.println("Created nested directories: " + nested);
            
            // Create files in directory
            Files.write(Paths.get(SAMPLE_DIR, "file1.txt"), 
                Arrays.asList("Content 1"));
            Files.write(Paths.get(SAMPLE_DIR, "file2.txt"), 
                Arrays.asList("Content 2"));
            Files.write(Paths.get(SAMPLE_DIR, "data.dat"), 
                Arrays.asList("Binary data"));
            
            // List directory contents
            System.out.println("\nDirectory contents:");
            try (DirectoryStream<Path> stream = Files.newDirectoryStream(directory)) {
                for (Path entry : stream) {
                    System.out.println("  " + entry.getFileName() + 
                        (Files.isDirectory(entry) ? " [DIR]" : ""));
                }
            }
            
            // List with filter
            System.out.println("\nText files only:");
            try (DirectoryStream<Path> stream = 
                    Files.newDirectoryStream(directory, "*.txt")) {
                stream.forEach(path -> System.out.println("  " + path.getFileName()));
            }
            
            // Walk directory tree
            System.out.println("\nWalking directory tree:");
            Files.walk(directory)
                 .forEach(path -> {
                     int depth = path.getNameCount() - directory.getNameCount();
                     System.out.println("  " + "  ".repeat(depth) + path.getFileName());
                 });
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates file copying and moving.
     */
    public static void demonstrateCopyMove() {
        System.out.println("=== Copy and Move Operations ===");
        
        try {
            Path source = Paths.get(SAMPLE_FILE);
            Path copy = Paths.get("nio-copy.txt");
            Path moved = Paths.get("nio-moved.txt");
            
            // Copy file
            Files.copy(source, copy, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("Copied: " + source + " -> " + copy);
            
            // Move/rename file
            Files.move(copy, moved, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("Moved: " + copy + " -> " + moved);
            
            // Delete file
            Files.deleteIfExists(moved);
            System.out.println("Deleted: " + moved);
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates ByteBuffer operations.
     */
    public static void demonstrateByteBuffer() {
        System.out.println("=== ByteBuffer Operations ===");
        
        // Allocate buffer
        ByteBuffer buffer = ByteBuffer.allocate(48);
        
        System.out.println("Buffer created:");
        System.out.println("  Capacity: " + buffer.capacity());
        System.out.println("  Position: " + buffer.position());
        System.out.println("  Limit: " + buffer.limit());
        
        // Write to buffer
        buffer.putInt(42);
        buffer.putDouble(3.14159);
        buffer.put((byte) 1);
        
        System.out.println("\nAfter writing:");
        System.out.println("  Position: " + buffer.position());
        
        // Flip buffer for reading
        buffer.flip();
        System.out.println("\nAfter flip:");
        System.out.println("  Position: " + buffer.position());
        System.out.println("  Limit: " + buffer.limit());
        
        // Read from buffer
        int intValue = buffer.getInt();
        double doubleValue = buffer.getDouble();
        byte byteValue = buffer.get();
        
        System.out.println("\nRead values:");
        System.out.println("  Int: " + intValue);
        System.out.println("  Double: " + doubleValue);
        System.out.println("  Byte: " + byteValue);
        
        // Clear buffer
        buffer.clear();
        System.out.println("\nAfter clear:");
        System.out.println("  Position: " + buffer.position());
        System.out.println("  Limit: " + buffer.limit());
        
        System.out.println();
    }
    
    /**
     * Demonstrates FileChannel for efficient I/O.
     */
    public static void demonstrateFileChannel() {
        System.out.println("=== FileChannel Operations ===");
        
        Path source = Paths.get(SAMPLE_FILE);
        Path destination = Paths.get("channel-copy.txt");
        
        try (FileChannel sourceChannel = FileChannel.open(source, StandardOpenOption.READ);
             FileChannel destChannel = FileChannel.open(destination, 
                 StandardOpenOption.CREATE, StandardOpenOption.WRITE)) {
            
            // Get channel size
            long size = sourceChannel.size();
            System.out.println("Source file size: " + size + " bytes");
            
            // Transfer data
            long transferred = sourceChannel.transferTo(0, size, destChannel);
            System.out.println("Transferred: " + transferred + " bytes");
            
            System.out.println("File copied using FileChannel");
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        // Cleanup
        try {
            Files.deleteIfExists(destination);
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates memory-mapped files for large file access.
     */
    public static void demonstrateMemoryMappedFile() {
        System.out.println("=== Memory-Mapped File ===");
        
        Path file = Paths.get("memory-mapped.txt");
        
        try {
            // Create and write using memory-mapped buffer
            String content = "This is memory-mapped file content. " +
                "It's very efficient for large files!";
            
            try (RandomAccessFile raf = new RandomAccessFile(file.toFile(), "rw");
                 FileChannel channel = raf.getChannel()) {
                
                MappedByteBuffer buffer = channel.map(
                    FileChannel.MapMode.READ_WRITE, 0, content.length());
                
                buffer.put(content.getBytes(StandardCharsets.UTF_8));
                System.out.println("Written to memory-mapped file");
            }
            
            // Read using memory-mapped buffer
            try (RandomAccessFile raf = new RandomAccessFile(file.toFile(), "r");
                 FileChannel channel = raf.getChannel()) {
                
                MappedByteBuffer buffer = channel.map(
                    FileChannel.MapMode.READ_ONLY, 0, channel.size());
                
                byte[] bytes = new byte[(int) channel.size()];
                buffer.get(bytes);
                String readContent = new String(bytes, StandardCharsets.UTF_8);
                
                System.out.println("Read from memory-mapped file: " + readContent);
            }
            
            // Cleanup
            Files.deleteIfExists(file);
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Demonstrates watching a directory for changes.
     */
    public static void demonstrateWatchService() {
        System.out.println("=== WatchService (Directory Monitoring) ===");
        
        Path directory = Paths.get(SAMPLE_DIR);
        
        try {
            WatchService watchService = FileSystems.getDefault().newWatchService();
            directory.register(watchService, 
                StandardWatchEventKinds.ENTRY_CREATE,
                StandardWatchEventKinds.ENTRY_MODIFY,
                StandardWatchEventKinds.ENTRY_DELETE);
            
            System.out.println("Watching directory: " + directory);
            
            // Create a file to trigger events
            Thread.sleep(100);
            Path testFile = Paths.get(SAMPLE_DIR, "watch-test.txt");
            Files.write(testFile, Arrays.asList("Test content"));
            Files.delete(testFile);
            
            // Poll for events (with timeout)
            WatchKey key = watchService.poll(2, java.util.concurrent.TimeUnit.SECONDS);
            
            if (key != null) {
                for (WatchEvent<?> event : key.pollEvents()) {
                    WatchEvent.Kind<?> kind = event.kind();
                    Path fileName = (Path) event.context();
                    System.out.println("Event: " + kind + " - File: " + fileName);
                }
                key.reset();
            } else {
                System.out.println("No events detected (this is normal in some environments)");
            }
            
            watchService.close();
            
        } catch (IOException | InterruptedException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        System.out.println();
    }
    
    /**
     * Cleanup test files and directories.
     */
    public static void cleanup() {
        System.out.println("=== Cleanup ===");
        
        try {
            // Delete test file
            Files.deleteIfExists(Paths.get(SAMPLE_FILE));
            
            // Delete directory tree
            Path directory = Paths.get(SAMPLE_DIR);
            if (Files.exists(directory)) {
                Files.walk(directory)
                     .sorted(Comparator.reverseOrder())
                     .forEach(path -> {
                         try {
                             Files.delete(path);
                         } catch (IOException e) {
                             System.err.println("Failed to delete: " + path);
                         }
                     });
            }
            
            System.out.println("Cleanup completed");
            
        } catch (IOException e) {
            System.err.println("Cleanup error: " + e.getMessage());
        }
    }
    
    /**
     * Main method demonstrating NIO operations.
     */
    public static void main(String[] args) {
        System.out.println("Java NIO Examples\n");
        
        demonstratePathAPI();
        demonstrateFilesClass();
        demonstrateFileStreams();
        demonstrateDirectoryOperations();
        demonstrateCopyMove();
        demonstrateByteBuffer();
        demonstrateFileChannel();
        demonstrateMemoryMappedFile();
        demonstrateWatchService();
        
        cleanup();
        
        System.out.println("\n=== All NIO examples completed ===");
    }
}
