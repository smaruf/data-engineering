"""
Shared Utilities for Snowflake and Databricks Learning
=======================================================

This module provides common utilities used across examples:
- Connection managers
- Logging configuration
- Data validators
- Helper functions
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with colored output
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Format
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def print_section(title: str, width: int = 60):
    """
    Print a formatted section header
    
    Args:
        title: Section title
        width: Width of the header line
    """
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_success(message: str):
    """Print success message in green"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message in red"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"📊 {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable format
    
    Args:
        bytes_size: Size in bytes
    
    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        str: Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def validate_env_vars(required_vars: list) -> Dict[str, bool]:
    """
    Validate that required environment variables are set
    
    Args:
        required_vars: List of required variable names
    
    Returns:
        dict: Dictionary with validation results
    """
    results = {}
    for var in required_vars:
        value = os.getenv(var)
        results[var] = value is not None and len(value) > 0
    return results


class Timer:
    """Context manager for timing code execution"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        
    def __enter__(self):
        self.start_time = datetime.now()
        print_info(f"{self.name} started at {self.start_time.strftime('%H:%M:%S')}")
        return self
        
    def __exit__(self, *args):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print_success(f"{self.name} completed in {format_duration(duration)}")


# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = setup_logger("utils_test")
    logger.info("Testing utilities...")
    
    # Print formatted sections
    print_section("Testing Utilities")
    print_success("This is a success message")
    print_error("This is an error message")
    print_info("This is an info message")
    print_warning("This is a warning message")
    
    # Test timer
    with Timer("Sample operation"):
        import time
        time.sleep(2)
    
    print("\n✅ All utility tests completed!")
