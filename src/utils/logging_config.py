"""Logging configuration for the NLP Agentic AI system."""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

import colorlog


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            str: JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredFormatter(colorlog.ColoredFormatter):
    """Colored formatter for console output."""

    def __init__(self):
        super().__init__(
            fmt="%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    max_file_size: int = 10485760,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ("json" or "text")
        log_file: Path to log file. If None, only console logging is used
        max_file_size: Maximum size of log file before rotation (bytes)
        backup_count: Number of backup log files to keep

    Returns:
        logging.Logger: Configured root logger
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if log_format.lower() == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())

    logger.addHandler(console_handler)

    # File handler with rotation if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_with_extra(
    logger: logging.Logger,
    level: str,
    message: str,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log message with extra fields.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        extra_fields: Additional fields to include in log
    """
    log_func = getattr(logger, level.lower())

    if extra_fields:
        # Create a LogRecord with extra fields
        record = logging.LogRecord(
            name=logger.name,
            level=getattr(logging, level.upper()),
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        record.extra_fields = extra_fields
        logger.handle(record)
    else:
        log_func(message)


# Context manager for logging execution time
class LogExecutionTime:
    """Context manager to log execution time of code blocks."""

    def __init__(self, logger: logging.Logger, operation: str):
        """
        Initialize execution timer.

        Args:
            logger: Logger instance
            operation: Name of operation being timed
        """
        self.logger = logger
        self.operation = operation
        self.start_time: Optional[datetime] = None

    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.utcnow()
        self.logger.info(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            log_with_extra(
                self.logger,
                "info",
                f"Completed: {self.operation}",
                {"duration_seconds": duration, "operation": self.operation},
            )

        if exc_type:
            self.logger.error(
                f"Failed: {self.operation}",
                exc_info=(exc_type, exc_val, exc_tb),
            )
