"""
Centralized logging configuration for Data Fabric Platform

Provides structured logging with support for:
- JSON and text formats
- File and console output
- Log rotation
- Different log levels per module
"""

import logging
import sys
from typing import Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from shared.utils.config_loader import config


class LoggerFactory:
    """Factory for creating configured loggers"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str, log_level: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger with the specified name
        
        Args:
            name: Logger name (usually __name__)
            log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        
        # Set log level
        level = log_level or config.get_env('LOG_LEVEL', 'INFO')
        logger.setLevel(getattr(logging, level.upper()))
        
        # Avoid duplicate handlers
        if not logger.handlers:
            # Console handler
            console_handler = cls._create_console_handler()
            logger.addHandler(console_handler)
            
            # File handler
            file_handler = cls._create_file_handler()
            if file_handler:
                logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def _create_console_handler(cls) -> logging.Handler:
        """Create console handler"""
        handler = logging.StreamHandler(sys.stdout)
        
        log_format = config.get_env('LOG_FORMAT', 'text')
        if log_format == 'json':
            formatter = jsonlogger.JsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s',
                rename_fields={'levelname': 'level', 'asctime': 'timestamp'}
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    @classmethod
    def _create_file_handler(cls) -> Optional[logging.Handler]:
        """Create rotating file handler"""
        log_file = config.get_env('LOG_FILE_PATH')
        if not log_file:
            return None
        
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Parse rotation size (e.g., "100MB")
        rotation_size_str = config.get_env('LOG_ROTATION_SIZE', '100MB')
        rotation_size = cls._parse_size(rotation_size_str)
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=rotation_size,
            backupCount=5
        )
        
        log_format = config.get_env('LOG_FORMAT', 'text')
        if log_format == 'json':
            formatter = jsonlogger.JsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s',
                rename_fields={'levelname': 'level', 'asctime': 'timestamp'}
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Parse size string like '100MB' to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name (usually __name__)
        log_level: Override log level
        
    Returns:
        Configured logger instance
        
    Example:
        >>> from shared.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting ETL pipeline")
    """
    return LoggerFactory.get_logger(name, log_level)
