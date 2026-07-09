"""
Module 1 smoke tests — verify config, logger, and helpers load correctly.
These tests run without any IBM credentials (they mock the required env vars).
"""

import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    """Unit tests for src/utils/helpers.py"""

    def test_sanitise_filename_basic(self) -> None:
        from src.utils.helpers import sanitise_filename
        result = sanitise_filename("Hello World! (2024)")
        assert " " not in result
        assert "!" not in result
        assert "(" not in result

    def test_sanitise_filename_empty(self) -> None:
        from src.utils.helpers import sanitise_filename
        assert sanitise_filename("") == "unnamed"

    def test_truncate_text_short(self) -> None:
        from src.utils.helpers import truncate_text
        assert truncate_text("short", max_chars=100) == "short"

    def test_truncate_text_long(self) -> None:
        from src.utils.helpers import truncate_text
        result = truncate_text("a" * 300, max_chars=50)
        assert len(result) == 50
        assert result.endswith("…")

    def test_format_file_size(self) -> None:
        from src.utils.helpers import format_file_size
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1_048_576) == "1.0 MB"

    def test_hash_text_deterministic(self) -> None:
        from src.utils.helpers import hash_text
        assert hash_text("hello") == hash_text("hello")
        assert hash_text("hello") != hash_text("world")

    def test_hash_text_length(self) -> None:
        from src.utils.helpers import hash_text
        assert len(hash_text("any text")) == 64

    def test_flatten_list(self) -> None:
        from src.utils.helpers import flatten_list
        assert flatten_list([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]

    def test_chunk_list(self) -> None:
        from src.utils.helpers import chunk_list
        batches = list(chunk_list(list(range(10)), 3))
        assert batches == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    def test_timer_decorator(self) -> None:
        from src.utils.helpers import timer

        @timer
        def slow_add(a: int, b: int) -> int:
            time.sleep(0.01)
            return a + b

        assert slow_add(2, 3) == 5

    def test_ensure_dir(self, tmp_path: Path) -> None:
        from src.utils.helpers import ensure_dir
        target = tmp_path / "a" / "b" / "c"
        result = ensure_dir(target)
        assert result.exists()
        assert result.is_dir()


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class TestLogger:
    """Unit tests for src/utils/logger.py"""

    def test_get_logger_returns_logger(self) -> None:
        from src.utils.logger import get_logger
        import logging
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_idempotent(self) -> None:
        """Calling get_logger twice for the same name must not add duplicate handlers."""
        from src.utils.logger import get_logger
        logger1 = get_logger("test.idempotent")
        count1 = len(logger1.handlers)
        logger2 = get_logger("test.idempotent")
        assert len(logger2.handlers) == count1


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestConfig:
    """Unit tests for src/utils/config.py"""

    def test_settings_has_required_fields(self) -> None:
        """Settings singleton must expose critical attributes."""
        with patch.dict(
            os.environ,
            {
                "WATSONX_API_KEY": "test-key",
                "WATSONX_PROJECT_ID": "test-project",
            },
        ):
            # Re-import inside patch so pydantic reads the mocked env
            import importlib
            import src.utils.config as cfg_module
            importlib.reload(cfg_module)
            s = cfg_module.Settings()
            assert s.watsonx_api_key == "test-key"
            assert s.watsonx_project_id == "test-project"
            assert s.chunk_size == 512
            assert s.top_k_retrieval == 5
