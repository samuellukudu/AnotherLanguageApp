import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file="app.log", max_size=10*1024*1024, backup_count=3):
    """
    Configure application-wide logging with both console and file handlers.
    
    Args:
        log_level: The logging level (default: INFO)
        log_file: Path to the log file (default: app.log)
        max_size: Maximum size of log file before rotation in bytes (default: 10MB)
        backup_count: Number of backup log files to keep (default: 3)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file_path = log_dir / log_file
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:  
        root_logger.removeHandler(handler)
    
    # Create formatters
    verbose_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Console handler (simple format for readability)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (verbose format for debugging)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_size,
        backupCount=backup_count
    )
    file_handler.setFormatter(verbose_formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific log levels for noisy modules
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(f"Logging configured. Log file: {log_file_path}")
    
    return root_logger

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)