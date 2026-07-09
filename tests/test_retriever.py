"""
Module 5 tests — Retriever Agent  (src/agents/retriever.py)

All IBM API calls are bypassed by passing pre-computed ``query_vector``
arguments.  Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_retriever.py -v
"""

from __future__ import annotations

from typing import List

import numpy as np
import pytest

from src.agents.retriever import (
    DEFAULT_MIN_SCORE,
    RetrievalResult,
    RetrieverAgent,
    _mmr_rerank,
    _preprocess_query,
)
from src.rag.chunk import TextChunk
from src.rag.embed import EXPECTED_DIMENSIONS
from src.rag.vector_store import VectorStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(
    text: str = "research chunk",
    idx: int = 0,
    doc_hash: str = "hash_a",
    source: str = "paper.pdf",
) -> TextChunk:
    return TextChunk(
        text=text,
        chunk_index=idx,
        doc_hash=doc_hash,
        doc_title="Test Paper",
        source=source,
        page_number=1,
        char_start=0,
        char_end=len(text),
    )


def _unit_vec(dim: int = EXPECTED_DIMENSIONS, component: int = 0) -> List[float]:
    """Return a unit vector with 1.0 in position ``component``."""
    v = [0.0] * dim
    v[component] = 1.0
    return v


def _random_vec(seed: int = 0, dim: int = EXPECTED_DIMENSIONS) -> List[float]:
    rng = np.random.default_rng(seed)
    v = rng.random(dim).astype(np.float32)
    v /= np.linalg.norm(v)
    return v.tolist()


def _populated_store(n: int = 6) -> VectorStore:
    """
    Build a VectorStore with n chunks whose embeddings are orthogonal
    unit vectors (component i is hot for chunk i).  This makes search
    results completely predictable.
    """
    store = VectorStore()
    chunks = [
        _make_chunk(f"chunk text {i}", idx=i, doc_hash=f"hash_{i % 2}")
        for i in range(n)
    ]
    vecs = [_unit_vec(component=i % EXPECTED_DIMENSIONS) for i in range(n)]
    store.add_chunks(chunks, embeddings=vecs)
    return store


# ---------------------------------------------------------------------------
# _preprocess_query
# ---------------------------------------------------------------------------

class TestPreprocessQuery:

    def test_strips_whitespace(self) -> None:
        assert _preprocess_query("  hello world  ") == "hello world"

    def test_collapses_spaces(self) -> None:
        result = _preprocess_query("what   is   attention")
        assert "  " not in result

    def test_appends_question_mark_to_wh_query(self) -> None:
        result = _preprocess_query("what is the transformer")
        assert result.endswith("?")

    def test_does_not_double_question_mark(self) -> None:
        result = _preprocess_query("what is this?")
        assert result.count("?") == 1

    def test_non_question_unchanged_punctuation(self) -> None:
        result = _preprocess_query("summarise the abstract.")
        assert result.endswith(".")

    def test_raises_on_blank_query(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            _preprocess_query("   ")


# ---------------------------------------------------------------------------
# _mmr_rerank
# ---------------------------------------------------------------------------

class TestMMRRerank:

    def _make_vecs(self, n: int) -> np.ndarray:
        """n orthogonal unit vectors."""
        vecs = np.zeros((n, EXPECTED_DIMENSIONS), dtype=np.float32)
        for i in range(n):
            vecs[i, i % EXPECTED_DIMENSIONS] = 1.0
        return vecs

    def test_returns_top_k(self) -> None:
        n = 5
        vecs = self._make_vecs(n)
        chunks = [_make_chunk(f"t{i}", i) for i in range(n)]
        scores = [1.0 - i * 0.1 for i in range(n)]  # descending
        qvec = np.array(_unit_vec(component=0), dtype=np.float32)

        result = _mmr_rerank(qvec, vecs, chunks, scores, top_k=3, mmr_lambda=0.7)
        assert len(result) == 3

    def test_empty_candidates_returns_empty(self) -> None:
        qvec = np.array(_unit_vec(), dtype=np.float32)
        result = _mmr_rerank(qvec, np.zeros((0, EXPECTED_DIMENSIONS), dtype=np.float32),
                             [], [], top_k=3, mmr_lambda=0.7)
        assert result == []

    def test_top_k_clamped_to_n_candidates(self) -> None:
        n = 2
        vecs = self._make_vecs(n)
        chunks = [_make_chunk(f"t{i}", i) for i in range(n)]
        scores = [1.0, 0.9]
        qvec = np.array(_unit_vec(component=0), dtype=np.float32)

        result = _mmr_rerank(qvec, vecs, chunks, scores, top_k=10, mmr_lambda=0.7)
        assert len(result) == 2

    def test_lambda_1_picks_highest_score_first(self) -> None:
        """With λ=1 (pure relevance), highest cosine score wins."""
        n = 4
        vecs = self._make_vecs(n)
        chunks = [_make_chunk(f"t{i}", i) for i in range(n)]
        # chunk 2 has the highest score
        scores = [0.5, 0.6, 0.95, 0.4]
        qvec = np.array(_unit_vec(component=2), dtype=np.float32)

        result = _mmr_rerank(qvec, vecs, chunks, scores, top_k=1, mmr_lambda=1.0)
        assert result[0][0].chunk_index == 2

    def test_returns_tuples_of_chunk_and_score(self) -> None:
        n = 3
        vecs = self._make_vecs(n)
        chunks = [_make_chunk(f"t{i}", i) for i in range(n)]
        scores = [0.9, 0.8, 0.7]
        qvec = np.array(_unit_vec(component=0), dtype=np.float32)

        result = _mmr_rerank(qvec, vecs, chunks, scores, top_k=2, mmr_lambda=0.7)
        for item in result:
            assert isinstance(item[0], TextChunk)
            assert isinstance(item[1], float)


# ---------------------------------------------------------------------------
# RetrieverAgent — retrieve
# ---------------------------------------------------------------------------

class TestRetrieverAgent:

    def test_raises_on_empty_store(self) -> None:
        store = VectorStore()
        agent = RetrieverAgent(store)
        with pytest.raises(RuntimeError, match="empty"):
            agent.retrieve("what is this?", query_vector=_unit_vec())

    def test_returns_retrieval_result(self) -> None:
        store = _populated_store()
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve("query", top_k=3, query_vector=_unit_vec(component=0))
        assert isinstance(result, RetrievalResult)

    def test_returns_correct_number_of_chunks(self) -> None:
        store = _populated_store(6)
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve("q", top_k=3, query_vector=_unit_vec(component=0))
        assert len(result.chunks) <= 3

    def test_scores_parallel_to_chunks(self) -> None:
        store = _populated_store()
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve("q", top_k=3, query_vector=_unit_vec(component=0))
        assert len(result.chunks) == len(result.scores)

    def test_query_stored_in_result(self) -> None:
        store = _populated_store()
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve("what is attention?", query_vector=_unit_vec(component=0))
        assert "attention" in result.query

    def test_exact_match_chunk_returned_first(self) -> None:
        """
        Chunk 2 has unit vector at component=2.  Querying with the same
        vector should rank chunk 2 highest with λ=1 (pure relevance).
        """
        store = _populated_store(6)
        agent = RetrieverAgent(store, min_score=0.0, mmr_lambda=1.0)
        result = agent.retrieve(
            "what is this",
            top_k=1,
            query_vector=_unit_vec(component=2),
        )
        assert result.chunks[0].chunk_index == 2

    def test_min_score_filters_low_similarity(self) -> None:
        """Chunks with score < min_score should be dropped."""
        store = _populated_store(4)
        # Query matches component=0; all other chunks have score ≈ 0
        agent = RetrieverAgent(store, min_score=0.99)
        result = agent.retrieve(
            "what is attention",
            top_k=5,
            query_vector=_unit_vec(component=0),
        )
        # Only chunk 0 should survive threshold
        assert len(result.chunks) <= 1
        if result.chunks:
            assert result.chunks[0].chunk_index == 0

    def test_filter_by_doc_hash(self) -> None:
        """Only chunks from the specified doc_hash should be returned."""
        store = _populated_store(6)  # hashes alternate: hash_0, hash_1, ...
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve(
            "query",
            top_k=10,
            query_vector=_random_vec(seed=7),
            filter_doc_hashes=["hash_0"],
        )
        # All returned chunks must have doc_hash == "hash_0"
        for chunk in result.chunks:
            assert chunk.doc_hash == "hash_0"

    def test_empty_result_when_no_candidates_pass_filter(self) -> None:
        store = _populated_store(4)
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve(
            "query",
            top_k=3,
            query_vector=_unit_vec(component=0),
            filter_doc_hashes=["nonexistent_hash"],
        )
        assert result.is_empty

    def test_total_candidates_reported(self) -> None:
        store = _populated_store(6)
        agent = RetrieverAgent(store, min_score=0.0)
        result = agent.retrieve("q", top_k=3, query_vector=_unit_vec(component=0))
        assert result.total_candidates >= len(result.chunks)

    def test_store_property(self) -> None:
        store = _populated_store()
        agent = RetrieverAgent(store)
        assert agent.store is store


# ---------------------------------------------------------------------------
# RetrievalResult helpers
# ---------------------------------------------------------------------------

class TestRetrievalResult:

    def _make_result(self, n: int = 3) -> RetrievalResult:
        chunks = [_make_chunk(f"passage {i}", idx=i) for i in range(n)]
        scores = [0.9 - i * 0.1 for i in range(n)]
        return RetrievalResult(
            chunks=chunks,
            scores=scores,
            query="test query",
            total_candidates=n + 2,
        )

    def test_is_empty_false_when_has_chunks(self) -> None:
        assert not self._make_result(3).is_empty

    def test_is_empty_true_when_no_chunks(self) -> None:
        r = RetrievalResult(chunks=[], scores=[], query="q")
        assert r.is_empty

    def test_as_context_string_contains_source(self) -> None:
        result = self._make_result()
        ctx = result.as_context_string()
        assert "paper.pdf" in ctx

    def test_as_context_string_contains_page(self) -> None:
        result = self._make_result()
        ctx = result.as_context_string()
        assert "Page:" in ctx

    def test_as_context_string_max_chunks_limits(self) -> None:
        result = self._make_result(5)
        ctx = result.as_context_string(max_chunks=2)
        # Should only contain 2 numbered entries
        assert ctx.count("[1]") == 1
        assert ctx.count("[3]") == 0

    def test_repr_contains_query(self) -> None:
        result = self._make_result()
        assert "test query" in repr(result)

    def test_repr_contains_chunk_count(self) -> None:
        result = self._make_result(4)
        assert "chunks=4" in repr(result)
