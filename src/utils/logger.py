"""
SciPilot — Structured Logger
==============================
Provides a project-wide logger with:
  - Consistent format across all modules
  - Colour-coded console output (INFO=blue, WARNING=yellow, ERROR=red)
  - Optional file handler writing to logs/scipilot.log
  - Log level controlled by the LOG_LEVEL env variable

Usage:
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Loaded %d chunks", len(chunks))
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# ANSI colour codes — stripped automatically on non-TTY outputs
# ---------------------------------------------------------------------------
_COLOURS = {
    "DEBUG": "\033[36m",    # Cyan
    "INFO": "\033[34m",     # Blue
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",    # Red
    "CRITICAL": "\033[35m", # Magenta
    "RESET": "\033[0m",
}


class _ColouredFormatter(logging.Formatter):
    """
    Custom formatter that prepends ANSI colour codes when writing to a TTY.
    Falls back to plain text for file handlers and CI environments.
    """

    _FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    _DATEFMT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, use_colour: bool = True) -> None:
        super().__init__(fmt=self._FMT, datefmt=self._DATEFMT)
        self._use_colour = use_colour

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        formatted = super().format(record)
        if self._use_colour and sys.stderr.isatty():
            colour = _COLOURS.get(record.levelname, "")
            reset = _COLOURS["RESET"]
            return f"{colour}{formatted}{reset}"
        return formatted


def get_logger(
    name: str,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Return a named logger, configuring it on first call.

    Args:
        name:     Typically ``__name__`` of the calling module.
        log_file: Optional path to write logs to disk.
                  Defaults to ``logs/scipilot.log`` if LOG_LEVEL is DEBUG.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls (e.g. in Streamlit reruns)
    if logger.handlers:
        return logger

    # ── Resolve log level ────────────────────────────────────────────────────
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    # ── Console handler ───────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(_ColouredFormatter(use_colour=True))
    logger.addHandler(console_handler)

    # ── File handler (always on if log_file provided; auto-enabled for DEBUG) ─
    resolved_log_file = log_file or (
        Path("logs/scipilot.log") if level == logging.DEBUG else None
    )
    if resolved_log_file:
        resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(resolved_log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(_ColouredFormatter(use_colour=False))
        logger.addHandler(file_handler)

    # Prevent propagation to the root logger (avoids duplicate lines)
    logger.propagate = False

    return logger
