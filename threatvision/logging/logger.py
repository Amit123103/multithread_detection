"""Structured logging module for ThreatVision AI."""

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

_console = Console()


def setup_logger(
    name: str = "threatvision", level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """Configure and return a structured rich logger."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove pre-existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    rich_handler = RichHandler(
        console=_console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True,
    )
    rich_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter("%(message)s", datefmt="[%X]")
    rich_handler.setFormatter(formatter)
    logger.addHandler(rich_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
