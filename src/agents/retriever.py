"""
SciPilot — Retriever Agent  (src/agents/retriever.py)
=======================================================
Sits between the FAISS VectorStore (Module 4) and the Synthesis Agent
(Module 6).  Given a natural-language research question it returns the
most relevant, diverse set of ``TextChunk`` objects to use as LLM context.

Pipeline inside ``RetrieverAgent.retrieve()``:
  1. Pre-process the query (strip, normalise).
  2. Embed the query via IBM watsonx.ai (or accept a pre-computed vector).
  3. Search FAISS for the top ``candidate_k`` nearest chunks (candidate pool
     is larger than ``top_k`` so MMR has enough material to diversify).
  4. Apply optional doc-hash filter (restrict to specific papers).
  5. Apply minimum cosine-similarity threshold (drop irrelevant results).
  6. Re-rank with MMR to maximise relevance AND diversity.
  7. Return final ``top_k`` chunks wrapped in a ``RetrievalResult``.

MMR formula (Carbonell & Goldstein 1998):
  MMR = argmax [ λ · sim(q, dᵢ) - (1-λ) · max_{dⱼ∈S} sim(dᵢ, dⱼ) ]

  where S is the already-selected set, q is the query, λ controls the
  relevance-diversity trade-off (default 0.7 = 70% relevance, 30% diversity).

Dependencies:
  - src.rag.vector_store  (VectorStore)
  - src.rag.embed         (embed_query, EXPECTED_DIMENSIONS)
  - src.rag.chunk         (TextChunk)
  - src.utils.config      (settings)
  - src.utils.logger      (get_logger)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from src.rag.chunk import TextChunk
from src.rag.embed import EXPECTED_DIMENSIONS, embed_query, is_local_mode
from src.rag.vector_store import VectorStore
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CANDIDATE_MULTIPLIER: int = 4   # candidate_k = top_k × this
DEFAULT_MMR_LAMBDA: float = 0.7         # relevance weight (0=diversity, 1=relevance)
DEFAULT_MIN_SCORE: float = 0.20         # cosine similarity threshold


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class RetrievalResult:
    """
    The output of ``RetrieverAgent.retrieve()``.

    Attributes:
        chunks:        Final ranked list of ``TextChunk`` objects.
        scores:        Cosine similarity score for each chunk (parallel list).
        query:         The (pre-processed) query string that was searched.
        total_candidates: How many chunks were in the pool before MMR/filtering.
    """

    chunks: List[TextChunk]
    scores: List[float]
    query: str
    total_candidates: int = 0

    @property
    def is_empty(self) -> bool:
        return len(self.chunks) == 0

    def as_context_string(self, max_chunks: Optional[int] = None) -> str:
        """
        Format the retrieved chunks into a single context string suitable
        for injection into an LLM prompt.

        Each chunk is prefixed with its source file and page number so the
        LLM can produce grounded citations.

        Args:
            max_chunks: Limit the number of chunks included.

        Returns:
            Multi-line string ready to insert into a prompt template.
        """
        selected = self.chunks[:max_chunks] if max_chunks else self.chunks
        parts: List[str] = []
        for i, chunk in enumerate(selected, start=1):
            header = (
                f"[{i}] Source: {chunk.source} | "
                f"Page: {chunk.page_number} | "
                f"Title: {chunk.doc_title}"
            )
            parts.append(f"{header}\n{chunk.text.strip()}")
        return "\n\n---\n\n".join(parts)

    def __repr__(self) -> str:
        return (
            f"RetrievalResult(chunks={len(self.chunks)}, "
            f"candidates={self.total_candidates}, query={self.query!r})"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_MULTI_SPACE = re.compile(r"\s+")


def _preprocess_query(query: str) -> str:
    """
    Light normalisation applied to the raw query string before embedding.

    Steps:
        1. Strip leading/trailing whitespace.
        2. Collapse multiple spaces into one.
        3. Ensure the query ends with a question mark if it looks like a
           question (helps the embedding model understand the intent).

    Args:
        query: Raw user input.

    Returns:
        Cleaned query string.

    Raises:
        ValueError: If the query is blank after stripping.
    """
    cleaned = _MULTI_SPACE.sub(" ", query.strip())
    if not cleaned:
        raise ValueError("Query is empty after pre-processing.")

    # Append '?' if the query starts with a Wh-word and lacks punctuation
    question_starters = ("what", "why", "how", "where", "when", "who", "which")
    if (
        cleaned.lower().split()[0] in question_starters
        and not cleaned[-1] in ".?!"
    ):
        cleaned += "?"

    return cleaned


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two 1-D float32 vectors.

    Vectors are assumed to already be L2-normalised (as they are after
    FAISS normalisation), in which case this reduces to a dot product.

    Args:
        a: 1-D numpy array, dtype float32.
        b: 1-D numpy array, dtype float32.

    Returns:
        Scalar cosine similarity in [-1.0, 1.0].
    """
    return float(np.dot(a, b))


def _mmr_rerank(
    query_vector: np.ndarray,
    candidate_vectors: np.ndarray,
    candidate_chunks: List[TextChunk],
    candidate_scores: List[float],
    top_k: int,
    mmr_lambda: float,
) -> List[Tuple[TextChunk, float]]:
    """
    Re-rank *candidate_chunks* using Maximal Marginal Relevance.

    MMR iteratively selects the chunk that maximises:
        λ · sim(query, chunk) - (1-λ) · max_{selected} sim(chunk, selected)

    This ensures the final set is both relevant to the query AND diverse
    among itself — preventing redundant near-duplicate passages.

    Args:
        query_vector:      Normalised query vector, shape ``(dim,)``.
        candidate_vectors: Normalised candidate vectors, shape ``(n, dim)``.
        candidate_chunks:  Corresponding ``TextChunk`` objects.
        candidate_scores:  Cosine scores from FAISS search.
        top_k:             Number of chunks to select.
        mmr_lambda:        Relevance weight (0–1).  Higher = more relevance,
                           lower = more diversity.

    Returns:
        List of ``(TextChunk, score)`` tuples of length ≤ ``top_k``.
    """
    if not candidate_chunks:
        return []

    n = len(candidate_chunks)
    k = min(top_k, n)

    selected_indices: List[int] = []
    remaining: Set[int] = set(range(n))

    for _ in range(k):
        best_idx = -1
        best_mmr = -float("inf")

        for idx in remaining:
            # Relevance: cosine similarity to query
            relevance = candidate_scores[idx]

            # Redundancy: max similarity to already-selected chunks
            if selected_indices:
                redundancy = max(
                    _cosine_sim(candidate_vectors[idx], candidate_vectors[sel])
                    for sel in selected_indices
                )
            else:
                redundancy = 0.0

            mmr_score = mmr_lambda * relevance - (1.0 - mmr_lambda) * redundancy

            if mmr_score > best_mmr:
                best_mmr = mmr_score
                best_idx = idx

        if best_idx == -1:
            break

        selected_indices.append(best_idx)
        remaining.discard(best_idx)

    return [
        (candidate_chunks[i], candidate_scores[i])
        for i in selected_indices
    ]


# ---------------------------------------------------------------------------
# Retriever Agent
# ---------------------------------------------------------------------------

class RetrieverAgent:
    """
    Semantic retrieval agent that wraps FAISS search with query
    pre-processing, filtering, score thresholding, and MMR diversification.

    Usage:
        store = VectorStore.load()
        agent = RetrieverAgent(store)
        result = agent.retrieve("What is the transformer architecture?", top_k=5)
        context = result.as_context_string()
    """

    def __init__(
        self,
        vector_store: VectorStore,
        mmr_lambda: float = DEFAULT_MMR_LAMBDA,
        min_score: float = DEFAULT_MIN_SCORE,
        candidate_multiplier: int = DEFAULT_CANDIDATE_MULTIPLIER,
    ) -> None:
        """
        Args:
            vector_store:         A populated ``VectorStore`` instance.
            mmr_lambda:           MMR relevance weight (0=diversity, 1=relevance).
            min_score:            Minimum cosine similarity to include a chunk.
            candidate_multiplier: ``candidate_k = top_k × multiplier``.
        """
        self._store = vector_store
        self._mmr_lambda = mmr_lambda
        self._min_score = min_score
        self._candidate_multiplier = candidate_multiplier

        logger.info(
            "RetrieverAgent ready (store size=%d, λ=%.2f, min_score=%.2f).",
            vector_store.size,
            mmr_lambda,
            min_score,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_doc_hashes: Optional[List[str]] = None,
        query_vector: Optional[List[float]] = None,
    ) -> RetrievalResult:
        """
        Retrieve the most relevant and diverse chunks for *query*.

        Args:
            query:             Research question or sub-question.
            top_k:             Desired number of final chunks.  Defaults to
                               ``settings.top_k_retrieval``.
            filter_doc_hashes: If provided, only chunks whose ``doc_hash``
                               is in this list are considered.
            query_vector:      Optional pre-computed embedding (bypasses the
                               IBM API call — used for testing).

        Returns:
            A ``RetrievalResult`` with ranked chunks and metadata.

        Raises:
            ValueError: If the query is blank.
            RuntimeError: If the vector store is empty.
        """
        k = top_k or settings.top_k_retrieval
        clean_query = _preprocess_query(query)

        if self._store.is_empty:
            raise RuntimeError(
                "Vector store is empty. Please ingest documents first."
            )

        # ── Step 1: embed query ───────────────────────────────────────────
        if query_vector is None:
            qvec = embed_query(clean_query)
        else:
            qvec = query_vector

        qvec_np = np.array(qvec, dtype=np.float32)

        # ── Step 2: fetch candidate pool ──────────────────────────────────
        candidate_k = min(
            k * self._candidate_multiplier,
            self._store.size,
        )
        raw_results: List[Tuple[TextChunk, float]] = self._store.search(
            clean_query,
            top_k=candidate_k,
            query_vector=qvec,
        )

        # ── Step 3: metadata filter ────────────────────────────────────────
        if filter_doc_hashes:
            allowed: Set[str] = set(filter_doc_hashes)
            raw_results = [
                (c, s) for c, s in raw_results if c.doc_hash in allowed
            ]

        # ── Step 4: score threshold ────────────────────────────────────────
        effective_min = self._min_score
        if is_local_mode() and self._min_score == DEFAULT_MIN_SCORE:
            effective_min = 0.05

        filtered_results = [
            (c, s) for c, s in raw_results if s >= effective_min
        ]
        # In local mode, if sparse word hashing produced slightly lower scores,
        # fall back to the top available candidates rather than dropping everything.
        if not filtered_results and is_local_mode() and raw_results:
            filtered_results = raw_results[:k]

        raw_results = filtered_results

        total_candidates = len(raw_results)
        logger.debug(
            "Query=%r  candidates=%d  (after filter+threshold)",
            clean_query[:60],
            total_candidates,
        )

        if not raw_results:
            logger.warning(
                "No chunks passed the score threshold (%.2f) for query: %s",
                self._min_score,
                clean_query[:80],
            )
            return RetrievalResult(
                chunks=[],
                scores=[],
                query=clean_query,
                total_candidates=0,
            )

        # ── Step 5: MMR re-rank ────────────────────────────────────────────
        cand_chunks = [c for c, _ in raw_results]
        cand_scores = [s for _, s in raw_results]

        # Build candidate vector matrix from FAISS (re-use stored metadata
        # rather than re-embedding, which would cost an API call).
        # We approximate by using the cosine scores as a proxy for the
        # direction; for full MMR we need the actual vectors.
        # Since FAISS IndexFlatIP stores the actual vectors, we retrieve them.
        cand_vecs = self._get_stored_vectors(cand_chunks)

        if cand_vecs is not None:
            reranked = _mmr_rerank(
                query_vector=qvec_np,
                candidate_vectors=cand_vecs,
                candidate_chunks=cand_chunks,
                candidate_scores=cand_scores,
                top_k=k,
                mmr_lambda=self._mmr_lambda,
            )
        else:
            # Fallback: just take top-k by score
            reranked = list(zip(cand_chunks, cand_scores))[:k]

        final_chunks = [c for c, _ in reranked]
        final_scores = [s for _, s in reranked]

        logger.info(
            "Retrieved %d chunk(s) for query=%r",
            len(final_chunks),
            clean_query[:60],
        )

        return RetrievalResult(
            chunks=final_chunks,
            scores=final_scores,
            query=clean_query,
            total_candidates=total_candidates,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_stored_vectors(
        self, chunks: List[TextChunk]
    ) -> Optional[np.ndarray]:
        """
        Reconstruct the stored float32 vectors for the given chunks by
        re-running the FAISS index's reconstruct method.

        ``IndexFlatIP`` supports ``reconstruct(i)`` which returns the
        original (normalised) vector for row *i*.  We find the row index
        by matching the chunk object reference in ``_store._chunks``.

        Args:
            chunks: Subset of chunks currently in the vector store.

        Returns:
            Float32 array of shape ``(n, dim)``, or ``None`` if
            reconstruction is not possible.
        """
        try:
            chunk_to_idx: Dict[int, int] = {
                id(c): i for i, c in enumerate(self._store._chunks)
            }
            indices = [chunk_to_idx[id(c)] for c in chunks]
            dim = self._store._dim
            vecs = np.zeros((len(indices), dim), dtype=np.float32)
            for row, faiss_idx in enumerate(indices):
                vecs[row] = self._store._index.reconstruct(faiss_idx)  # type: ignore[attr-defined]
            return vecs
        except Exception as exc:  # noqa: BLE001
            logger.debug("Could not reconstruct vectors for MMR: %s", exc)
            return None

    @property
    def store(self) -> VectorStore:
        """Expose the underlying vector store (read-only access)."""
        return self._store
