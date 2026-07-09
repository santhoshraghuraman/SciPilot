"""
conftest.py — pytest session-wide fixtures and env bootstrapping.

Injects the minimum environment variables required by ``Settings``
before any test module is imported, so the pydantic Settings singleton
does not fail at collection time when no real .env is present.
"""

import os

import pytest


# ---------------------------------------------------------------------------
# Inject stub credentials before collection
# ---------------------------------------------------------------------------

os.environ.setdefault("WATSONX_API_KEY", "test-api-key")
os.environ.setdefault("WATSONX_PROJECT_ID", "test-project-id")
os.environ.setdefault("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")


@pytest.fixture(autouse=False)
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Fixture that ensures IBM credentials are present for any test that
    explicitly requests it.  Tests that import src modules at collection
    time rely on the ``os.environ.setdefault`` calls above instead.
    """
    monkeypatch.setenv("WATSONX_API_KEY", "test-api-key")
    monkeypatch.setenv("WATSONX_PROJECT_ID", "test-project-id")
