"""
Logging utilities for the ETL pipeline
"""

import logging
import logging.config
import os
from datetime import datetime


def setup_logger(name: str, log_level: str = 'INFO') -> logging.Logger:
    """Setup structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file path
    log_file = os.path.join(log_dir, f'etl_pipeline_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': log_level
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': log_file,
                'formatter': 'detailed',
                'level': 'DEBUG'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    return logging.getLogger(name)