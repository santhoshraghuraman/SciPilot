"""
Module 4 tests — Embeddings  (src/rag/embed.py)

All IBM watsonx.ai API calls are mocked.  Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_embed.py -v
"""

from __future__ import annotations

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from src.rag.chunk import TextChunk
from src.rag.embed import (
    EMBED_BATCH_SIZE,
    EXPECTED_DIMENSIONS,
    embed_chunks,
    embed_query,
    embed_texts,
    reset_client,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_vectors(n: int, dim: int = EXPECTED_DIMENSIONS) -> List[List[float]]:
    """Return n identical fake float vectors of the correct dimension."""
    return [[0.1] * dim for _ in range(n)]


def _make_chunk(text: str = "sample text", idx: int = 0) -> TextChunk:
    return TextChunk(
        text=text,
        chunk_index=idx,
        doc_hash="hash",
        doc_title="Title",
        source="paper.pdf",
        page_number=1,
        char_start=0,
        char_end=len(text),
    )


def _mock_client(n_texts: int, dim: int = EXPECTED_DIMENSIONS) -> MagicMock:
    """Return a mock client whose embed_documents returns n fake vectors."""
    mock = MagicMock()
    mock.embed_documents.return_value = _fake_vectors(n_texts, dim)
    return mock


# ---------------------------------------------------------------------------
# embed_texts
# ---------------------------------------------------------------------------

class TestEmbedTexts:

    def setup_method(self) -> None:
        reset_client()  # clear cached client before each test

    def test_returns_correct_number_of_vectors(self) -> None:
        texts = ["hello", "world", "foo"]
        with patch("src.rag.embed._get_client", return_value=_mock_client(3)):
            result = embed_texts(texts)
        assert len(result) == 3

    def test_each_vector_has_correct_dimension(self) -> None:
        texts = ["hello"]
        with patch("src.rag.embed._get_client", return_value=_mock_client(1)):
            result = embed_texts(texts)
        assert len(result[0]) == EXPECTED_DIMENSIONS

    def test_raises_on_empty_list(self) -> None:
        with pytest.raises(ValueError, match="empty list"):
            embed_texts([])

    def test_batches_large_input(self) -> None:
        """Should split into multiple batches when len > EMBED_BATCH_SIZE."""
        n = EMBED_BATCH_SIZE + 5
        texts = [f"text {i}" for i in range(n)]

        call_counts = []

        def fake_get_client():
            mock = MagicMock()
            def fake_embed(texts):
                call_counts.append(len(texts))
                return _fake_vectors(len(texts))
            mock.embed_documents.side_effect = fake_embed
            return mock

        with patch("src.rag.embed._get_client", side_effect=fake_get_client):
            result = embed_texts(texts)

        assert len(result) == n
        # First batch should be EMBED_BATCH_SIZE, second batch = remaining
        assert call_counts[0] == EMBED_BATCH_SIZE
        assert call_counts[1] == 5

    def test_raises_on_dimension_mismatch(self) -> None:
        """If API returns wrong dimension, RuntimeError should be raised."""
        with patch("src.rag.embed._get_client", return_value=_mock_client(1, dim=128)):
            with pytest.raises(RuntimeError, match="Unexpected embedding dimension"):
                embed_texts(["hello"])


# ---------------------------------------------------------------------------
# embed_chunks
# ---------------------------------------------------------------------------

class TestEmbedChunks:

    def setup_method(self) -> None:
        reset_client()

    def test_embeds_chunk_texts(self) -> None:
        chunks = [_make_chunk("alpha"), _make_chunk("beta"), _make_chunk("gamma")]
        with patch("src.rag.embed._get_client", return_value=_mock_client(3)):
            result = embed_chunks(chunks)
        assert len(result) == 3

    def test_raises_on_empty_chunks(self) -> None:
        with pytest.raises(ValueError, match="empty list"):
            embed_chunks([])

    def test_uses_chunk_text_field(self) -> None:
        """Verify that the .text attribute of each chunk is what gets embedded."""
        captured = []

        def fake_get_client():
            mock = MagicMock()
            def capture_embed(texts):
                captured.extend(texts)
                return _fake_vectors(len(texts))
            mock.embed_documents.side_effect = capture_embed
            return mock

        chunks = [_make_chunk("first chunk"), _make_chunk("second chunk")]
        with patch("src.rag.embed._get_client", side_effect=fake_get_client):
            embed_chunks(chunks)

        assert "first chunk" in captured
        assert "second chunk" in captured


# ---------------------------------------------------------------------------
# embed_query
# ---------------------------------------------------------------------------

class TestEmbedQuery:

    def setup_method(self) -> None:
        reset_client()

    def test_returns_single_vector(self) -> None:
        with patch("src.rag.embed._get_client", return_value=_mock_client(1)):
            result = embed_query("What is attention?")
        assert isinstance(result, list)
        assert len(result) == EXPECTED_DIMENSIONS

    def test_raises_on_blank_query(self) -> None:
        with pytest.raises(ValueError, match="blank query"):
            embed_query("   ")

    def test_strips_whitespace(self) -> None:
        with patch("src.rag.embed._get_client", return_value=_mock_client(1)):
            result = embed_query("  hello world  ")
        assert len(result) == EXPECTED_DIMENSIONS
