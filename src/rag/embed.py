"""
SciPilot — IBM watsonx.ai Embedding Wrapper  (src/rag/embed.py)
================================================================
Converts ``TextChunk`` objects into dense float vectors using the
IBM watsonx.ai Embeddings API (model: ibm/slate-125m-english-rtrvr).

Design goals:
  - Batched requests: the API limits the number of texts per call; we
    split chunks into batches of ``EMBED_BATCH_SIZE`` and concatenate results.
  - Retry with exponential back-off: transient 429 / 5xx errors are retried
    up to ``MAX_RETRIES`` times before raising.
  - Dimension validation: if the API silently changes the vector size we
    detect it immediately rather than silently corrupting the FAISS index.
  - Pure function surface: ``embed_chunks`` and ``embed_texts`` are stateless
    — no side-effects beyond the API call — making them easy to mock in tests.

IBM watsonx.ai SDK reference:
  https://ibm.github.io/watson-machine-learning-py-client/

Dependencies:
  - ibm-watsonx-ai  (``pip install ibm-watsonx-ai``)
  - tenacity        (``pip install tenacity``)
  - src.rag.chunk   (TextChunk)
  - src.utils.config (settings)
  - src.utils.logger (get_logger)
  - src.utils.helpers (chunk_list)
"""

from __future__ import annotations

import os
from typing import List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.rag.chunk import TextChunk
from src.utils.config import settings
from src.utils.helpers import chunk_list
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMBED_BATCH_SIZE: int = 25        # texts per API call (conservative limit)
MAX_RETRIES: int = 4              # total attempts = 1 original + 3 retries
EXPECTED_DIMENSIONS: int = 0     # auto-detected on first embed call (0 = unknown)


# ---------------------------------------------------------------------------
# Lazy client initialisation
# ---------------------------------------------------------------------------

_client = None  # module-level cache; initialised on first use
_detected_dim: int = 0  # auto-detected embedding dimension


def _get_client():
    """
    Return a cached ``ibm_watsonx_ai.foundation_models.Embeddings`` client.

    Lazy initialisation avoids importing the heavy IBM SDK at collection
    time and allows tests to patch ``src.rag.embed._get_client`` cleanly.

    Returns:
        An ``Embeddings`` instance configured from ``settings``.

    Raises:
        ImportError:  If ``ibm-watsonx-ai`` is not installed.
        RuntimeError: If required credentials are missing.
    """
    global _client

    if _client is not None:
        return _client

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import Embeddings
        from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
    except ImportError as exc:
        raise ImportError(
            "ibm-watsonx-ai is not installed. "
            "Run: pip install ibm-watsonx-ai"
        ) from exc

    if not settings.watsonx_api_key or not settings.watsonx_project_id:
        raise RuntimeError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env"
        )

    credentials = Credentials(
        url=settings.watsonx_url,
        api_key=settings.watsonx_api_key,
    )

    _client = Embeddings(
        model_id=settings.granite_embed_model,
        credentials=credentials,
        project_id=settings.watsonx_project_id,
    )

    logger.info(
        "IBM watsonx.ai Embeddings client initialised (model=%s).",
        settings.granite_embed_model,
    )
    return _client


def reset_client() -> None:
    """
    Clear the cached client.  Called by tests that swap credentials.
    """
    global _client, _detected_dim, EXPECTED_DIMENSIONS
    _client = None
    _detected_dim = 0
    EXPECTED_DIMENSIONS = 0


# ---------------------------------------------------------------------------
# Core embedding functions
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(MAX_RETRIES),
    reraise=True,
)
def _embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Embed a single batch of texts via the IBM watsonx.ai API.

    The ``@retry`` decorator automatically retries on any exception with
    exponential back-off (2s → 4s → 8s → 30s) before re-raising.

    Args:
        texts: List of strings, length ≤ ``EMBED_BATCH_SIZE``.

    Returns:
        List of float vectors, one per input text.

    Raises:
        RuntimeError: On dimension mismatch.
        Exception:    After ``MAX_RETRIES`` failed attempts.
    """
    global _detected_dim, EXPECTED_DIMENSIONS
    client = _get_client()
    response = client.embed_documents(texts=texts)

    # ``embed_documents`` returns List[List[float]] directly
    vectors: List[List[float]] = response

    # Auto-detect dimension on first call, then validate consistency
    if vectors:
        actual_dim = len(vectors[0])
        if _detected_dim == 0:
            _detected_dim = actual_dim
            EXPECTED_DIMENSIONS = actual_dim
            logger.info(
                "Auto-detected embedding dimension: %d (model=%s)",
                actual_dim,
                settings.granite_embed_model,
            )
        elif actual_dim != _detected_dim:
            raise RuntimeError(
                f"Embedding dimension changed mid-session: expected {_detected_dim}, "
                f"got {actual_dim}. Restart the app if you changed GRANITE_EMBED_MODEL."
            )

    return vectors


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed an arbitrary list of plain strings, handling batching internally.

    Args:
        texts: Any number of strings to embed.

    Returns:
        List of float vectors in the same order as *texts*.

    Raises:
        ValueError: If *texts* is empty.
    """
    if not texts:
        raise ValueError("embed_texts received an empty list.")

    all_vectors: List[List[float]] = []
    batches = list(chunk_list(texts, EMBED_BATCH_SIZE))

    logger.info(
        "Embedding %d text(s) in %d batch(es) …",
        len(texts),
        len(batches),
    )

    for batch_num, batch in enumerate(batches, start=1):
        logger.debug("  Batch %d/%d (%d texts) …", batch_num, len(batches), len(batch))
        vectors = _embed_batch(batch)
        all_vectors.extend(vectors)

    logger.info("Embedding complete: %d vector(s) produced.", len(all_vectors))
    return all_vectors


def embed_chunks(chunks: List[TextChunk]) -> List[List[float]]:
    """
    Embed a list of ``TextChunk`` objects.

    Extracts the ``.text`` field from each chunk and delegates to
    ``embed_texts``.  This is the function called by ``vector_store.py``.

    Args:
        chunks: Output of ``chunk.chunk_documents()``.

    Returns:
        List of float vectors, one per chunk, in the same order.

    Raises:
        ValueError: If *chunks* is empty.
    """
    if not chunks:
        raise ValueError("embed_chunks received an empty list.")

    texts = [c.text for c in chunks]
    return embed_texts(texts)


def embed_query(query: str) -> List[float]:
    """
    Embed a single query string for similarity search.

    Args:
        query: The research question or search query.

    Returns:
        A single float vector of length ``EXPECTED_DIMENSIONS``.

    Raises:
        ValueError: If *query* is blank.
    """
    query = query.strip()
    if not query:
        raise ValueError("embed_query received a blank query string.")

    vectors = embed_texts([query])
    return vectors[0]
