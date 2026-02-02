package com.microsoft.java.intermediate.fileio;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * FileOperations demonstrates basic file I/O operations in Java.
 * Covers reading/writing files, BufferedReader/Writer, and file handling.
 * 
 * @author Microsoft Stack Mastery
 * @version 1.0
 */
public class FileOperations {
    
    private static final String SAMPLE_FILE = "sample-output.txt";
    private static final String READ_FILE = "sample-read.txt";
    
    /**
     * Demonstrates writing to a file using FileWriter.
     * 
     * @param filename File to write to
     * @param content Content to write
     * @return true if successful, false otherwise
     */
    public static boolean writeWithFileWriter(String filename, String content) {
        System.out.println("=== Writing with FileWriter ===");
        
        FileWriter writer = null;
        try {
            writer = new FileWriter(filename);
            writer.write(content);
            System.out.println("Successfully wrote to: " + filename);
            return true;
        } catch (IOException e) {
            System.err.println("Error writing file: " + e.getMessage());
            return false;
        } finally {
            if (writer != null) {
                try {
                    writer.close();
                } catch (IOException e) {
                    System.err.println("Error closing writer: " + e.getMessage());
                }
            }
        }
    }
    
    /**
     * Demonstrates writing to a file using BufferedWriter (more efficient).
     * 
     * @param filename File to write to
     * @param lines Lines to write
     * @return true if successful, false otherwise
     */
    public static boolean writeWithBufferedWriter(String filename, List<String> lines) {
        System.out.println("\n=== Writing with BufferedWriter ===");
        
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            for (String line : lines) {
                writer.write(line);
                writer.newLine();
            }
            System.out.println("Successfully wrote " + lines.size() + " lines to: " + filename);
            return true;
        } catch (IOException e) {
            System.err.println("Error writing file: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Demonstrates appending to an existing file.
     * 
     * @param filename File to append to
     * @param content Content to append
     * @return true if successful, false otherwise
     */
    public static boolean appendToFile(String filename, String content) {
        System.out.println("\n=== Appending to File ===");
        
        try (BufferedWriter writer = new BufferedWriter(
                new FileWriter(filename, true))) { // true = append mode
            writer.write(content);
            writer.newLine();
            System.out.println("Successfully appended to: " + filename);
            return true;
        } catch (IOException e) {
            System.err.println("Error appending to file: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Demonstrates reading from a file using FileReader.
     * 
     * @param filename File to read from
     * @return File contents or null if error
     */
    public static String readWithFileReader(String filename) {
        System.out.println("\n=== Reading with FileReader ===");
        
        FileReader reader = null;
        try {
            reader = new FileReader(filename);
            StringBuilder content = new StringBuilder();
            int character;
            
            while ((character = reader.read()) != -1) {
                content.append((char) character);
            }
            
            System.out.println("Successfully read file: " + filename);
            return content.toString();
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + filename);
            return null;
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            return null;
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    System.err.println("Error closing reader: " + e.getMessage());
                }
            }
        }
    }
    
    /**
     * Demonstrates reading from a file using BufferedReader (more efficient).
     * 
     * @param filename File to read from
     * @return List of lines or empty list if error
     */
    public static List<String> readWithBufferedReader(String filename) {
        System.out.println("\n=== Reading with BufferedReader ===");
        
        List<String> lines = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
            System.out.println("Successfully read " + lines.size() + " lines from: " + filename);
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + filename);
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
        }
        
        return lines;
    }
    
    /**
     * Demonstrates reading entire file into a String.
     * 
     * @param filename File to read
     * @return File contents
     */
    public static String readEntireFile(String filename) {
        System.out.println("\n=== Reading Entire File ===");
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(filename), StandardCharsets.UTF_8))) {
            
            StringBuilder content = new StringBuilder();
            String line;
            
            while ((line = reader.readLine()) != null) {
                content.append(line).append(System.lineSeparator());
            }
            
            System.out.println("File size: " + content.length() + " characters");
            return content.toString();
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            return "";
        }
    }
    
    /**
     * Demonstrates binary file operations.
     * 
     * @param filename File to write/read
     */
    public static void binaryFileOperations(String filename) {
        System.out.println("\n=== Binary File Operations ===");
        
        // Write binary data
        try (DataOutputStream dos = new DataOutputStream(
                new FileOutputStream(filename))) {
            
            dos.writeInt(42);
            dos.writeDouble(3.14159);
            dos.writeBoolean(true);
            dos.writeUTF("Hello Binary");
            
            System.out.println("Binary data written successfully");
        } catch (IOException e) {
            System.err.println("Error writing binary file: " + e.getMessage());
            return;
        }
        
        // Read binary data
        try (DataInputStream dis = new DataInputStream(
                new FileInputStream(filename))) {
            
            int intValue = dis.readInt();
            double doubleValue = dis.readDouble();
            boolean boolValue = dis.readBoolean();
            String strValue = dis.readUTF();
            
            System.out.println("Read values:");
            System.out.println("  Int: " + intValue);
            System.out.println("  Double: " + doubleValue);
            System.out.println("  Boolean: " + boolValue);
            System.out.println("  String: " + strValue);
        } catch (IOException e) {
            System.err.println("Error reading binary file: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates file metadata and properties.
     * 
     * @param filename File to inspect
     */
    public static void displayFileInfo(String filename) {
        System.out.println("\n=== File Information ===");
        
        File file = new File(filename);
        
        if (file.exists()) {
            System.out.println("File: " + filename);
            System.out.println("  Absolute Path: " + file.getAbsolutePath());
            System.out.println("  Size: " + file.length() + " bytes");
            System.out.println("  Can Read: " + file.canRead());
            System.out.println("  Can Write: " + file.canWrite());
            System.out.println("  Is Directory: " + file.isDirectory());
            System.out.println("  Is Hidden: " + file.isHidden());
            System.out.println("  Last Modified: " + new Date(file.lastModified()));
        } else {
            System.out.println("File does not exist: " + filename);
        }
    }
    
    /**
     * Demonstrates copying a file.
     * 
     * @param source Source file
     * @param destination Destination file
     * @return true if successful, false otherwise
     */
    public static boolean copyFile(String source, String destination) {
        System.out.println("\n=== Copying File ===");
        
        try (BufferedInputStream in = new BufferedInputStream(new FileInputStream(source));
             BufferedOutputStream out = new BufferedOutputStream(new FileOutputStream(destination))) {
            
            byte[] buffer = new byte[8192];
            int bytesRead;
            long totalBytes = 0;
            
            while ((bytesRead = in.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
                totalBytes += bytesRead;
            }
            
            System.out.println("Copied " + totalBytes + " bytes from " + source + 
                " to " + destination);
            return true;
        } catch (IOException e) {
            System.err.println("Error copying file: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Demonstrates line-by-line file processing.
     * 
     * @param filename File to process
     */
    public static void processFileLineByLine(String filename) {
        System.out.println("\n=== Processing File Line by Line ===");
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            int lineNumber = 1;
            int wordCount = 0;
            int charCount = 0;
            
            while ((line = reader.readLine()) != null) {
                String[] words = line.trim().split("\\s+");
                if (!line.trim().isEmpty()) {
                    wordCount += words.length;
                }
                charCount += line.length();
                
                System.out.println("Line " + lineNumber + ": " + line);
                lineNumber++;
            }
            
            System.out.println("\nStatistics:");
            System.out.println("  Total Lines: " + (lineNumber - 1));
            System.out.println("  Total Words: " + wordCount);
            System.out.println("  Total Characters: " + charCount);
            
        } catch (IOException e) {
            System.err.println("Error processing file: " + e.getMessage());
        }
    }
    
    /**
     * Demonstrates finding files in a directory.
     * 
     * @param directory Directory to search
     * @param extension File extension to filter
     */
    public static void listFilesInDirectory(String directory, String extension) {
        System.out.println("\n=== Listing Files in Directory ===");
        
        File dir = new File(directory);
        
        if (!dir.exists() || !dir.isDirectory()) {
            System.out.println("Directory does not exist: " + directory);
            return;
        }
        
        File[] files = dir.listFiles((d, name) -> 
            extension == null || name.toLowerCase().endsWith(extension.toLowerCase()));
        
        if (files == null || files.length == 0) {
            System.out.println("No files found");
            return;
        }
        
        System.out.println("Found " + files.length + " file(s):");
        for (File file : files) {
            System.out.printf("  %s (%d bytes)%n", file.getName(), file.length());
        }
    }
    
    /**
     * Demonstrates creating and deleting files.
     */
    public static void demonstrateFileCreationDeletion() {
        System.out.println("\n=== File Creation and Deletion ===");
        
        String tempFile = "temp-file.txt";
        File file = new File(tempFile);
        
        try {
            // Create new file
            if (file.createNewFile()) {
                System.out.println("Created new file: " + tempFile);
            } else {
                System.out.println("File already exists: " + tempFile);
            }
            
            // Write some content
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(tempFile))) {
                writer.write("Temporary file content");
            }
            
            System.out.println("File exists: " + file.exists());
            
            // Delete file
            if (file.delete()) {
                System.out.println("Deleted file: " + tempFile);
            } else {
                System.out.println("Failed to delete file: " + tempFile);
            }
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
    
    /**
     * Main method demonstrating file operations.
     */
    public static void main(String[] args) {
        System.out.println("Java File Operations Examples\n");
        
        // Write operations
        writeWithFileWriter(SAMPLE_FILE, "Hello from FileWriter!\n");
        
        List<String> lines = Arrays.asList(
            "Line 1: Java File I/O",
            "Line 2: BufferedReader and BufferedWriter",
            "Line 3: Efficient file handling"
        );
        writeWithBufferedWriter(SAMPLE_FILE, lines);
        
        appendToFile(SAMPLE_FILE, "Line 4: Appended content");
        
        // Read operations
        String content = readWithFileReader(SAMPLE_FILE);
        if (content != null) {
            System.out.println("Content preview: " + 
                content.substring(0, Math.min(50, content.length())) + "...");
        }
        
        List<String> readLines = readWithBufferedReader(SAMPLE_FILE);
        System.out.println("Read lines: " + readLines.size());
        
        String fullContent = readEntireFile(SAMPLE_FILE);
        System.out.println("Full content length: " + fullContent.length());
        
        // File info
        displayFileInfo(SAMPLE_FILE);
        
        // Copy file
        copyFile(SAMPLE_FILE, "sample-copy.txt");
        
        // Process line by line
        processFileLineByLine(SAMPLE_FILE);
        
        // Binary operations
        binaryFileOperations("binary-data.dat");
        
        // List files
        listFilesInDirectory(".", ".txt");
        
        // Creation and deletion
        demonstrateFileCreationDeletion();
        
        // Cleanup
        System.out.println("\n=== Cleanup ===");
        new File(SAMPLE_FILE).delete();
        new File("sample-copy.txt").delete();
        new File("binary-data.dat").delete();
        System.out.println("Test files cleaned up");
        
        System.out.println("\n=== All file operation examples completed ===");
    }
}
