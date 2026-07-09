"""
Module 4 tests — FAISS VectorStore  (src/rag/vector_store.py)

All embedding calls are mocked — no IBM API needed.  Tests run offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_vector_store.py -v
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import List
from unittest.mock import patch

import numpy as np
import pytest

from src.rag.chunk import TextChunk
from src.rag.embed import EXPECTED_DIMENSIONS
from src.rag.vector_store import VectorStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(text: str = "chunk text", idx: int = 0, source: str = "paper.pdf") -> TextChunk:
    return TextChunk(
        text=text,
        chunk_index=idx,
        doc_hash="testhash",
        doc_title="Test Doc",
        source=source,
        page_number=1,
        char_start=0,
        char_end=len(text),
    )


def _random_vectors(n: int, dim: int = EXPECTED_DIMENSIONS) -> List[List[float]]:
    """Return n random unit vectors (reproducible via fixed seed)."""
    rng = np.random.default_rng(42)
    vecs = rng.random((n, dim)).astype(np.float32)
    # L2-normalise each row
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    vecs = vecs / norms
    return vecs.tolist()


def _distinct_vectors(n: int, dim: int = EXPECTED_DIMENSIONS) -> List[List[float]]:
    """
    Return n orthogonal-ish vectors where vector[i] has a strong i-th component.
    Useful for predictable search tests.
    """
    vecs = np.zeros((n, dim), dtype=np.float32)
    for i in range(n):
        vecs[i, i % dim] = 1.0
    return vecs.tolist()


# ---------------------------------------------------------------------------
# VectorStore — add_chunks
# ---------------------------------------------------------------------------

class TestVectorStoreAdd:

    def test_empty_store_has_size_zero(self) -> None:
        store = VectorStore()
        assert store.size == 0
        assert store.is_empty

    def test_add_increases_size(self) -> None:
        store = VectorStore()
        chunks = [_make_chunk(f"text {i}") for i in range(5)]
        vecs = _random_vectors(5)
        store.add_chunks(chunks, embeddings=vecs)
        assert store.size == 5

    def test_add_empty_list_is_noop(self) -> None:
        store = VectorStore()
        store.add_chunks([])
        assert store.size == 0

    def test_add_twice_accumulates(self) -> None:
        store = VectorStore()
        chunks_a = [_make_chunk(f"a{i}") for i in range(3)]
        chunks_b = [_make_chunk(f"b{i}") for i in range(4)]
        store.add_chunks(chunks_a, embeddings=_random_vectors(3))
        store.add_chunks(chunks_b, embeddings=_random_vectors(4))
        assert store.size == 7

    def test_raises_on_length_mismatch(self) -> None:
        store = VectorStore()
        chunks = [_make_chunk()]
        vecs = _random_vectors(3)  # wrong length
        with pytest.raises(ValueError, match="Mismatch"):
            store.add_chunks(chunks, embeddings=vecs)


# ---------------------------------------------------------------------------
# VectorStore — search
# ---------------------------------------------------------------------------

class TestVectorStoreSearch:

    def _populated_store(self, n: int = 5) -> VectorStore:
        store = VectorStore()
        chunks = [_make_chunk(f"chunk {i}", idx=i) for i in range(n)]
        store.add_chunks(chunks, embeddings=_random_vectors(n))
        return store

    def test_raises_on_empty_index(self) -> None:
        store = VectorStore()
        with pytest.raises(RuntimeError, match="empty"):
            store.search("query", query_vector=[0.1] * EXPECTED_DIMENSIONS)

    def test_returns_list_of_tuples(self) -> None:
        store = self._populated_store()
        qvec = _random_vectors(1)[0]
        results = store.search("q", query_vector=qvec)
        assert isinstance(results, list)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

    def test_returns_text_chunks(self) -> None:
        store = self._populated_store()
        qvec = _random_vectors(1)[0]
        results = store.search("q", query_vector=qvec)
        assert all(isinstance(chunk, TextChunk) for chunk, _ in results)

    def test_scores_are_floats(self) -> None:
        store = self._populated_store()
        qvec = _random_vectors(1)[0]
        results = store.search("q", query_vector=qvec)
        assert all(isinstance(score, float) for _, score in results)

    def test_top_k_limits_results(self) -> None:
        store = self._populated_store(10)
        qvec = _random_vectors(1)[0]
        results = store.search("q", top_k=3, query_vector=qvec)
        assert len(results) <= 3

    def test_top_k_clamped_to_index_size(self) -> None:
        store = self._populated_store(2)
        qvec = _random_vectors(1)[0]
        results = store.search("q", top_k=100, query_vector=qvec)
        assert len(results) == 2

    def test_exact_match_returns_highest_score(self) -> None:
        """
        If the query vector matches chunk 0 exactly, chunk 0 should have the
        highest cosine similarity score.
        """
        vecs = _distinct_vectors(5)
        store = VectorStore()
        chunks = [_make_chunk(f"text {i}", idx=i) for i in range(5)]
        store.add_chunks(chunks, embeddings=vecs)

        # Query with the exact vector of chunk 2
        result = store.search("q", top_k=5, query_vector=vecs[2])
        top_chunk, top_score = result[0]
        assert top_chunk.chunk_index == 2
        assert top_score > 0.99

    def test_search_chunks_returns_only_chunks(self) -> None:
        store = self._populated_store()
        qvec = _random_vectors(1)[0]
        chunks = store.search_chunks("q", query_vector=qvec)
        assert all(isinstance(c, TextChunk) for c in chunks)


# ---------------------------------------------------------------------------
# VectorStore — persistence
# ---------------------------------------------------------------------------

class TestVectorStorePersistence:

    def test_save_creates_files(self, tmp_path: Path) -> None:
        store = VectorStore()
        chunks = [_make_chunk(f"p{i}") for i in range(3)]
        store.add_chunks(chunks, embeddings=_random_vectors(3))

        base = tmp_path / "test_index"
        store.save(base)

        assert (tmp_path / "test_index.index").exists()
        assert (tmp_path / "test_index.meta").exists()

    def test_load_restores_size(self, tmp_path: Path) -> None:
        store = VectorStore()
        chunks = [_make_chunk(f"q{i}") for i in range(4)]
        store.add_chunks(chunks, embeddings=_random_vectors(4))

        base = tmp_path / "idx"
        store.save(base)

        loaded = VectorStore.load(base)
        assert loaded.size == 4

    def test_load_restores_chunks(self, tmp_path: Path) -> None:
        store = VectorStore()
        chunks = [_make_chunk("hello world", source="doc.pdf")]
        store.add_chunks(chunks, embeddings=_random_vectors(1))

        base = tmp_path / "idx2"
        store.save(base)
        loaded = VectorStore.load(base)

        assert loaded._chunks[0].source == "doc.pdf"
        assert loaded._chunks[0].text == "hello world"

    def test_load_raises_when_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            VectorStore.load(tmp_path / "nonexistent")

    def test_search_works_after_load(self, tmp_path: Path) -> None:
        vecs = _distinct_vectors(3)
        store = VectorStore()
        chunks = [_make_chunk(f"chunk {i}", idx=i) for i in range(3)]
        store.add_chunks(chunks, embeddings=vecs)

        base = tmp_path / "search_test"
        store.save(base)

        loaded = VectorStore.load(base)
        results = loaded.search("q", top_k=1, query_vector=vecs[1])
        assert results[0][0].chunk_index == 1

    def test_load_or_create_returns_fresh_when_missing(self, tmp_path: Path) -> None:
        store = VectorStore.load_or_create(tmp_path / "fresh")
        assert store.is_empty

    def test_load_or_create_loads_existing(self, tmp_path: Path) -> None:
        store = VectorStore()
        store.add_chunks([_make_chunk()], embeddings=_random_vectors(1))
        base = tmp_path / "existing"
        store.save(base)

        loaded = VectorStore.load_or_create(base)
        assert loaded.size == 1


# ---------------------------------------------------------------------------
# VectorStore — repr
# ---------------------------------------------------------------------------

class TestVectorStoreRepr:

    def test_repr_contains_size(self) -> None:
        store = VectorStore()
        assert "size=0" in repr(store)

    def test_repr_contains_dim(self) -> None:
        store = VectorStore(dim=768)
        assert "dim=768" in repr(store)
