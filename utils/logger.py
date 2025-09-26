"""
Logging utility for Mobile Automation Framework
Provides configurable logging with thread-safe implementation.
"""

import os
import logging
import threading
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler

from config.config_manager import config_manager


class LoggerManager:
    """Thread-safe logger manager for the automation framework."""
    
    _loggers = {}
    _lock = threading.Lock()
    _initialized = False
    
    @classmethod
    def _initialize_logging(cls):
        """Initialize logging configuration."""
        if cls._initialized:
            return
            
        with cls._lock:
            if cls._initialized:
                return
                
            # Get logging configuration
            log_config = config_manager.get_logging_config()
            log_level = getattr(logging, log_config['log_level'].upper(), logging.INFO)
            log_file = log_config['log_file']
            
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Configure root logger
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger instance."""
        cls._initialize_logging()
        
        if name not in cls._loggers:
            with cls._lock:
                if name not in cls._loggers:
                    logger = logging.getLogger(name)
                    
                    # Get logging configuration
                    log_config = config_manager.get_logging_config()
                    log_level = getattr(logging, log_config['log_level'].upper(), logging.INFO)
                    log_file = log_config['log_file']
                    
                    # Set logger level
                    logger.setLevel(log_level)
                    
                    # Remove existing handlers to avoid duplicates
                    for handler in logger.handlers[:]:
                        logger.removeHandler(handler)
                    
                    # Create console handler
                    console_handler = logging.StreamHandler()
                    console_handler.setLevel(log_level)
                    console_formatter = logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                    )
                    console_handler.setFormatter(console_formatter)
                    logger.addHandler(console_handler)
                    
                    # Create file handler with rotation
                    if log_file:
                        file_handler = RotatingFileHandler(
                            log_file,
                            maxBytes=10*1024*1024,  # 10MB
                            backupCount=5
                        )
                        file_handler.setLevel(log_level)
                        file_formatter = logging.Formatter(
                            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S'
                        )
                        file_handler.setFormatter(file_formatter)
                        logger.addHandler(file_handler)
                    
                    # Prevent propagation to root logger
                    logger.propagate = False
                    
                    cls._loggers[name] = logger
        
        return cls._loggers[name]


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger instance."""
    return LoggerManager.get_logger(name)


class TestLogger:
    """Test-specific logger with additional functionality."""
    
    def __init__(self, test_name: str):
        """Initialize test logger."""
        self.test_name = test_name
        self.logger = get_logger(f"TEST.{test_name}")
        self.start_time = datetime.now()
    
    def test_start(self, description: str = ""):
        """Log test start."""
        self.start_time = datetime.now()
        message = f"TEST STARTED: {self.test_name}"
        if description:
            message += f" - {description}"
        self.logger.info("=" * 80)
        self.logger.info(message)
        self.logger.info("=" * 80)
    
    def test_end(self, status: str = "COMPLETED"):
        """Log test end with duration."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.logger.info("-" * 80)
        self.logger.info(f"TEST {status}: {self.test_name}")
        self.logger.info(f"Duration: {duration}")
        self.logger.info("-" * 80)
    
    def step(self, step_description: str):
        """Log test step."""
        self.logger.info(f"STEP: {step_description}")
    
    def assertion(self, description: str, result: bool):
        """Log assertion result."""
        status = "PASS" if result else "FAIL"
        self.logger.info(f"ASSERTION [{status}]: {description}")
    
    def screenshot(self, screenshot_path: str, description: str = ""):
        """Log screenshot capture."""
        message = f"SCREENSHOT: {screenshot_path}"
        if description:
            message += f" - {description}"
        self.logger.info(message)
    
    def error(self, error_message: str, exception: Optional[Exception] = None):
        """Log error with optional exception details."""
        self.logger.error(f"ERROR: {error_message}")
        if exception:
            self.logger.error(f"Exception: {str(exception)}", exc_info=True)
    
    def warning(self, warning_message: str):
        """Log warning message."""
        self.logger.warning(f"WARNING: {warning_message}")
    
    def debug(self, debug_message: str):
        """Log debug message."""
        self.logger.debug(f"DEBUG: {debug_message}")


def create_test_logger(test_name: str) -> TestLogger:
    """Create a test-specific logger instance."""
    return TestLogger(test_name)