"""
SciPilot — Shared Helpers
===========================
Utility functions used by multiple modules.

Functions:
    timer               — Decorator that logs execution time of any function.
    sanitise_filename   — Make a string safe for use as a file name.
    truncate_text       — Truncate long strings for display/logging.
    format_file_size    — Human-readable byte sizes (KB, MB, GB).
    ensure_dir          — Create a directory if it does not exist.
    hash_text           — SHA-256 hash of a string (for cache keys).
    flatten_list        — Flatten a list of lists into a single list.
    chunk_list          — Split a list into fixed-size batches.
"""

import hashlib
import re
import time
import unicodedata
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generator, List, TypeVar

from src.utils.logger import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Timing decorator
# ---------------------------------------------------------------------------

def timer(func: F) -> F:
    """
    Decorator that logs the wall-clock execution time of the wrapped function.

    Usage:
        @timer
        def my_slow_function():
            ...
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug("⏱  %s finished in %.3fs", func.__qualname__, elapsed)
        return result

    return wrapper  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------

def sanitise_filename(name: str, max_length: int = 200) -> str:
    """
    Convert an arbitrary string into a safe file system name.

    Steps:
        1. Normalise Unicode to ASCII equivalents.
        2. Replace any character that is not alphanumeric, dash, underscore,
           or dot with an underscore.
        3. Collapse consecutive underscores.
        4. Strip leading/trailing underscores and dots.
        5. Truncate to max_length.

    Args:
        name:       Raw string (e.g. paper title, query text).
        max_length: Maximum length of the result.

    Returns:
        A filesystem-safe string.
    """
    # Normalise Unicode (e.g. é → e)
    normalised = unicodedata.normalize("NFKD", name)
    ascii_str = normalised.encode("ascii", "ignore").decode("ascii")

    # Replace unsafe characters
    safe = re.sub(r"[^\w\-.]", "_", ascii_str)

    # Collapse multiple underscores
    safe = re.sub(r"_+", "_", safe)

    # Strip leading/trailing separators
    safe = safe.strip("_.")

    return safe[:max_length] or "unnamed"


def truncate_text(text: str, max_chars: int = 200, suffix: str = "…") -> str:
    """
    Truncate *text* to *max_chars* characters, appending *suffix* if cut.

    Args:
        text:      Input string.
        max_chars: Maximum number of characters.
        suffix:    String appended when truncation occurs.

    Returns:
        Truncated string.
    """
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


# ---------------------------------------------------------------------------
# File / size helpers
# ---------------------------------------------------------------------------

def format_file_size(num_bytes: int) -> str:
    """
    Convert a byte count into a human-readable string.

    Examples:
        format_file_size(1024)        → "1.0 KB"
        format_file_size(1_048_576)   → "1.0 MB"
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0  # type: ignore[assignment]
    return f"{num_bytes:.1f} PB"


def ensure_dir(path: Path) -> Path:
    """
    Create *path* (and any missing parents) if it does not already exist.

    Args:
        path: Directory path to create.

    Returns:
        The same path, for easy chaining.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def hash_text(text: str) -> str:
    """
    Return the SHA-256 hex digest of *text*.

    Used as a cache key for documents and chunks to avoid re-processing
    files that have already been ingested.

    Args:
        text: Any string (e.g. document content, query).

    Returns:
        64-character hex string.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# List helpers
# ---------------------------------------------------------------------------

def flatten_list(nested: List[List[Any]]) -> List[Any]:
    """
    Flatten a list-of-lists into a single flat list.

    Args:
        nested: e.g. [[1, 2], [3, 4], [5]]

    Returns:
        [1, 2, 3, 4, 5]
    """
    return [item for sublist in nested for item in sublist]


def chunk_list(items: List[Any], batch_size: int) -> Generator[List[Any], None, None]:
    """
    Yield successive fixed-size batches from *items*.

    Useful for batching embedding API calls to avoid rate limits.

    Args:
        items:      Source list.
        batch_size: Maximum items per batch.

    Yields:
        Sublists of length ≤ batch_size.
    """
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]
