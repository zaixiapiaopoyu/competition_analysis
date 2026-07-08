"""
Logging utility for enterprise competitor analysis system.

Provides structured logging with console and file output, sensitive data redaction,
and agent execution tracking.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import re


class Logger:
    """
    Enterprise logging utility with multiple output streams and sensitive data redaction.
    
    Features:
    - Console output with colored formatting
    - File output with plain text formatting
    - Automatic sensitive data redaction
    - Agent execution tracking
    - Multiple log levels
    """
    
    # ANSI color codes for console output
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m"        # Reset
    }
    
    # Sensitive field patterns (case-insensitive)
    SENSITIVE_PATTERNS = [
        r"api[_-]?key",
        r"password",
        r"token",
        r"secret",
        r"credential",
        r"auth[_-]?token"
    ]
    
    def __init__(
        self,
        name: str,
        log_level: str = "INFO",
        log_dir: Optional[Path] = None,
        enable_console: bool = True,
        enable_file: bool = True
    ):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files (None to disable file logging)
            enable_console: Enable console output
            enable_file: Enable file output
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_dir = log_dir
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.handlers.clear()  # Clear existing handlers
        
        # Add console handler
        if enable_console:
            self._add_console_handler()
        
        # Add file handler
        if enable_file and log_dir:
            self._add_file_handler()
    
    def _add_console_handler(self) -> None:
        """Add colored console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Create colored formatter
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                color = Logger.COLORS.get(record.levelname, Logger.COLORS["RESET"])
                reset = Logger.COLORS["RESET"]
                
                # Format timestamp
                timestamp = self.formatTime(record, self.datefmt)
                
                # Format: [LEVEL] timestamp - message
                formatted = f"{color}[{record.levelname}]{reset} {timestamp} - {record.getMessage()}"
                
                # Add exception info if present
                if record.exc_info:
                    formatted += "\n" + self.formatException(record.exc_info)
                
                return formatted
        
        formatter = ColoredFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self) -> None:
        """Add plain text file handler."""
        try:
            # Create log directory if it doesn't exist
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create log file with date
            log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            
            # Create plain text formatter
            formatter = logging.Formatter(
                fmt="[%(levelname)s] %(asctime)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            # Log error to console only
            self.logger.warning(f"Failed to create file handler: {str(e)}")
    
    def _redact_sensitive_data(self, message: str) -> str:
        """
        Redact sensitive data from log messages.
        
        Args:
            message: Log message
            
        Returns:
            Message with sensitive data redacted
        """
        # Redact common sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            # Match pattern followed by value (key=value or key: value)
            regex = re.compile(
                rf"({pattern})\s*[:=]\s*['\"]?([^'\"\s,}}]+)['\"]?",
                re.IGNORECASE
            )
            message = regex.sub(r"\1=[REDACTED]", message)
        
        return message
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(self._redact_sensitive_data(message))
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(self._redact_sensitive_data(message))
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(self._redact_sensitive_data(message))
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """
        Log error message.
        
        Args:
            message: Error message
            exc_info: Include exception traceback
        """
        self.logger.error(self._redact_sensitive_data(message), exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """
        Log critical message.
        
        Args:
            message: Critical message
            exc_info: Include exception traceback
        """
        self.logger.critical(self._redact_sensitive_data(message), exc_info=exc_info)
    
    def log_agent_execution(
        self,
        agent_name: str,
        start_time: datetime,
        end_time: datetime,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log agent execution metrics.
        
        Args:
            agent_name: Name of the agent
            start_time: Execution start time
            end_time: Execution end time
            status: Execution status (success or failure)
            error_message: Error message if failed
        """
        duration = (end_time - start_time).total_seconds()
        
        log_message = f"Agent: {agent_name} | Duration: {duration:.2f}s | Status: {status}"
        
        if status == "success":
            self.info(log_message)
        else:
            if error_message:
                log_message += f" | Error: {error_message}"
            self.error(log_message)
    
    def log_llm_call(
        self,
        agent_name: str,
        duration: float,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        status: str = "success"
    ) -> None:
        """
        Log LLM API call metrics.
        
        Args:
            agent_name: Name of the agent making the call
            duration: Call duration in seconds
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            status: Call status
        """
        log_message = f"LLM Call | Agent: {agent_name} | Duration: {duration:.2f}s | Status: {status}"
        
        if input_tokens is not None:
            log_message += f" | Input Tokens: {input_tokens}"
        
        if output_tokens is not None:
            log_message += f" | Output Tokens: {output_tokens}"
        
        self.info(log_message)
