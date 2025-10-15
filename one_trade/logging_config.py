"""Logging configuration for One Trade system."""
import logging
import sys
from pathlib import Path
from typing import Optional

import structlog


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, structured: bool = True, console_output: bool = True) -> None:
    """Configure logging for the application. Args: level: Logging level (DEBUG, INFO, WARNING, ERROR). log_file: Optional path to log file. structured: Use structured logging with structlog. console_output: Output logs to console."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers = []
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        if not structured:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(log_level)
        if not structured:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    if structured:
        structlog.configure(processors=[structlog.stdlib.filter_by_level, structlog.stdlib.add_logger_name, structlog.stdlib.add_log_level, structlog.stdlib.PositionalArgumentsFormatter(), structlog.processors.TimeStamper(fmt="iso"), structlog.processors.StackInfoRenderer(), structlog.processors.format_exc_info, structlog.processors.UnicodeDecoder(), structlog.stdlib.ProcessorFormatter.wrap_for_formatter], logger_factory=structlog.stdlib.LoggerFactory(), cache_logger_on_first_use=True)


def get_logger(name: str):
    """Get a logger instance. Args: name: Logger name (usually __name__). Returns: Logger instance."""
    return structlog.get_logger(name)









