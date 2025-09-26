"""
Centralized logging configuration for the full-phased data engineering project
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging(
    service_name: str = "data-engineering",
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_structured: bool = False
) -> logging.Logger:
    """
    Setup centralized logging configuration
    
    Args:
        service_name: Name of the service for log identification
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_structured: Enable structured JSON logging
        
    Returns:
        Logger: Configured logger instance
    """
    
    # Create logs directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file path
    log_file = os.path.join(log_dir, f"{service_name}_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d in %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'structured': {
                '()': StructuredFormatter
            }
        },
        'handlers': {},
        'loggers': {
            '': {
                'handlers': [],
                'level': log_level,
                'propagate': False
            }
        }
    }
    
    # Console handler
    if enable_console:
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'formatter': 'structured' if enable_structured else 'standard',
            'level': log_level,
            'stream': sys.stdout
        }
        config['loggers']['']['handlers'].append('console')
    
    # File handler
    if enable_file:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'formatter': 'structured' if enable_structured else 'detailed',
            'level': 'DEBUG',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        config['loggers']['']['handlers'].append('file')
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get logger
    logger = logging.getLogger(service_name)
    
    # Log startup message
    logger.info(f"Logging initialized for {service_name}")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Console logging: {enable_console}")
    logger.info(f"File logging: {enable_file} ({log_file if enable_file else 'N/A'})")
    logger.info(f"Structured logging: {enable_structured}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling function: {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function {func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Function {func.__name__} failed with error: {str(e)}")
                raise
        return wrapper
    return decorator


def log_performance(logger: logging.Logger):
    """Decorator to log function performance metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Performance: {func.__name__} executed in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Performance: {func.__name__} failed after {execution_time:.4f} seconds with error: {str(e)}")
                raise
        return wrapper
    return decorator


# Environment-based logger configuration
def get_environment_logger(service_name: str = "data-engineering") -> logging.Logger:
    """Get logger configured based on environment variables"""
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_dir = os.getenv('LOG_DIR', 'logs')
    enable_console = os.getenv('LOG_CONSOLE', 'true').lower() == 'true'
    enable_file = os.getenv('LOG_FILE', 'true').lower() == 'true'
    enable_structured = os.getenv('LOG_STRUCTURED', 'false').lower() == 'true'
    
    return setup_logging(
        service_name=service_name,
        log_level=log_level,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_structured=enable_structured
    )