"""
SciPilot — FAISS Vector Store  (src/rag/vector_store.py)
=========================================================
Manages the FAISS index that stores embeddings for all ingested chunks,
and provides semantic search over those embeddings.

Architecture:
  - FAISS ``IndexFlatIP`` (inner product) on L2-normalised vectors is
    mathematically equivalent to cosine similarity search, which is the
    standard metric for semantic text retrieval.
  - Chunk metadata (text, provenance) is stored in a parallel Python list
    (``_chunks``) that mirrors the FAISS row order 1-to-1.  FAISS only
    stores vectors, not arbitrary metadata.
  - The index and metadata list are serialised together in a single
    ``pickle`` file so they are always in sync.

Persistence layout (``settings.faiss_index_path``):
  <faiss_index_path>.index   ← FAISS binary index
  <faiss_index_path>.meta    ← pickle of List[TextChunk]

Dependencies:
  - faiss-cpu  (``pip install faiss-cpu``)
  - src.rag.chunk    (TextChunk)
  - src.rag.embed    (embed_chunks, embed_query, EXPECTED_DIMENSIONS)
  - src.utils.config (settings)
  - src.utils.logger (get_logger)
  - src.utils.helpers (ensure_dir)
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np

from src.rag.chunk import TextChunk
from src.rag.embed import EXPECTED_DIMENSIONS, embed_chunks, embed_query
from src.utils.config import settings
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _index_path(base: Path) -> Path:
    """Return the path of the FAISS binary index file."""
    return base.with_suffix(".index")


def _meta_path(base: Path) -> Path:
    """Return the path of the metadata pickle file."""
    return base.with_suffix(".meta")


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------

class VectorStore:
    """
    A thin wrapper around a FAISS index with metadata management.

    Typical lifecycle:
        # First run — build the index
        store = VectorStore()
        store.add_chunks(chunks)   # embeds + indexes
        store.save()

        # Subsequent runs — load from disk
        store = VectorStore.load()

        # Query
        results = store.search("What is attention mechanism?", top_k=5)

    Attributes:
        _index:  The underlying ``faiss.Index`` object.
        _chunks: Parallel list of ``TextChunk`` objects matching FAISS rows.
        _dim:    Embedding dimensionality (set from EXPECTED_DIMENSIONS).
    """

    def __init__(self, dim: int = EXPECTED_DIMENSIONS) -> None:
        """
        Initialise an **empty** vector store.

        The FAISS index is lazily created on the first ``add_chunks`` call so
        that the correct embedding dimension is used regardless of the model.

        Args:
            dim: Embedding dimensionality hint. Set to 0 to auto-detect.
        """
        self._dim = dim
        # Defer index creation until we know the actual dimension
        self._index: Optional[faiss.Index] = None if dim == 0 else self._new_index(dim)
        self._chunks: List[TextChunk] = []
        logger.debug("VectorStore created (dim=%s).", dim if dim else 'auto')

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _new_index(dim: int) -> faiss.Index:
        """
        Create a new ``IndexFlatIP`` (inner product / cosine similarity).

        We use ``IndexFlatIP`` rather than ``IndexFlatL2`` because we
        L2-normalise all vectors before adding/querying, making inner
        product equivalent to cosine similarity.

        Args:
            dim: Vector dimensionality.

        Returns:
            A fresh, empty FAISS index.
        """
        return faiss.IndexFlatIP(dim)

    @staticmethod
    def _normalise(vectors: np.ndarray) -> np.ndarray:
        """
        L2-normalise a 2D float32 array row-wise (in-place).

        After normalisation each vector has unit length, so inner-product
        search is equivalent to cosine similarity.

        Args:
            vectors: Shape ``(n, dim)``, dtype float32.

        Returns:
            The same array, normalised in-place.
        """
        faiss.normalize_L2(vectors)
        return vectors

    # ------------------------------------------------------------------
    # Public — write
    # ------------------------------------------------------------------

    def add_chunks(
        self,
        chunks: List[TextChunk],
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """
        Embed *chunks* and add them to the FAISS index.

        If *embeddings* are provided (pre-computed) they are used directly,
        which is useful for testing without hitting the IBM API.

        Args:
            chunks:     List of ``TextChunk`` objects to index.
            embeddings: Optional pre-computed vectors.  If ``None``,
                        ``embed_chunks()`` is called automatically.

        Raises:
            ValueError: If chunks / embeddings lists have mismatched lengths.
        """
        if not chunks:
            logger.warning("add_chunks called with empty list — nothing to do.")
            return

        if embeddings is None:
            logger.info("Computing embeddings for %d chunk(s) …", len(chunks))
            embeddings = embed_chunks(chunks)

        if len(embeddings) != len(chunks):
            raise ValueError(
                f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings."
            )

        # Convert to float32 numpy array and normalise
        vectors = np.array(embeddings, dtype=np.float32)
        self._normalise(vectors)

        # Lazily create the FAISS index with the correct dimension on first use
        actual_dim = vectors.shape[1]
        if self._index is None:
            self._dim = actual_dim
            self._index = self._new_index(actual_dim)
            logger.info("FAISS index created with auto-detected dim=%d.", actual_dim)
        elif actual_dim != self._dim:
            raise ValueError(
                f"Embedding dimension mismatch: index has dim={self._dim}, "
                f"but new vectors have dim={actual_dim}. "
                f"Delete the existing index or use a consistent model."
            )

        # Add to FAISS
        self._index.add(vectors)  # type: ignore[attr-defined]
        self._chunks.extend(chunks)

        logger.info(
            "Added %d chunk(s) to FAISS index (total: %d).",
            len(chunks),
            self._index.ntotal,  # type: ignore[attr-defined]
        )

    # ------------------------------------------------------------------
    # Public — read / search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        query_vector: Optional[List[float]] = None,
    ) -> List[Tuple[TextChunk, float]]:
        """
        Retrieve the *top_k* most similar chunks to *query*.

        Args:
            query:        Natural language question to search for.
                          Ignored if *query_vector* is provided.
            top_k:        Number of results to return.  Defaults to
                          ``settings.top_k_retrieval``.
            query_vector: Optional pre-computed query embedding (for tests).

        Returns:
            List of ``(TextChunk, score)`` tuples sorted by descending
            cosine similarity score.  Scores are in ``[0.0, 1.0]``
            for normalised vectors.

        Raises:
            RuntimeError: If the index is empty.
        """
        if self._index is None or self._index.ntotal == 0:  # type: ignore[attr-defined]
            raise RuntimeError(
                "FAISS index is empty. Ingest some documents first."
            )

        k = min(top_k or settings.top_k_retrieval, self._index.ntotal)  # type: ignore[attr-defined]

        # Embed the query
        if query_vector is None:
            vec = embed_query(query)
        else:
            vec = query_vector

        q = np.array([vec], dtype=np.float32)
        self._normalise(q)

        # Search
        scores, indices = self._index.search(q, k)  # type: ignore[attr-defined]

        results: List[Tuple[TextChunk, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue  # FAISS returns -1 for padded results
            results.append((self._chunks[idx], float(score)))

        logger.debug("search returned %d result(s) for query=%r", len(results), query[:60])
        return results

    def search_chunks(
        self,
        query: str,
        top_k: Optional[int] = None,
        query_vector: Optional[List[float]] = None,
    ) -> List[TextChunk]:
        """
        Convenience wrapper — returns only ``TextChunk`` objects (no scores).

        Args:
            query:        Search query string.
            top_k:        Number of chunks to return.
            query_vector: Optional pre-computed embedding.

        Returns:
            List of ``TextChunk`` objects, most relevant first.
        """
        return [chunk for chunk, _ in self.search(query, top_k, query_vector)]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        """Number of vectors currently stored in the index."""
        if self._index is None:
            return 0
        return self._index.ntotal  # type: ignore[attr-defined]

    @property
    def is_empty(self) -> bool:
        """True when no chunks have been indexed yet."""
        return self.size == 0

    # ------------------------------------------------------------------
    # Public — persistence
    # ------------------------------------------------------------------

    def save(self, base_path: Optional[Path] = None) -> None:
        """
        Persist the FAISS index and chunk metadata to disk.

        Two files are written:
          - ``<base_path>.index`` — FAISS binary format
          - ``<base_path>.meta``  — pickled ``List[TextChunk]``

        Args:
            base_path: Base path (without extension).  Defaults to
                       ``settings.faiss_index_path``.
        """
        path = base_path or settings.faiss_index_path
        ensure_dir(Path(path).parent)

        idx_file = str(_index_path(Path(path)))
        meta_file = _meta_path(Path(path))

        faiss.write_index(self._index, idx_file)
        meta_file.write_bytes(pickle.dumps(self._chunks))

        logger.info(
            "VectorStore saved: %d vector(s) → %s",
            self.size,
            idx_file,
        )

    @classmethod
    def load(cls, base_path: Optional[Path] = None) -> "VectorStore":
        """
        Load a previously saved ``VectorStore`` from disk.

        Args:
            base_path: Base path used when ``save()`` was called.  Defaults
                       to ``settings.faiss_index_path``.

        Returns:
            A fully populated ``VectorStore`` instance.

        Raises:
            FileNotFoundError: If either the .index or .meta file is missing.
        """
        path = base_path or settings.faiss_index_path
        idx_file = _index_path(Path(path))
        meta_file = _meta_path(Path(path))

        if not idx_file.exists():
            raise FileNotFoundError(f"FAISS index not found: {idx_file}")
        if not meta_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {meta_file}")

        store = cls.__new__(cls)
        store._index = faiss.read_index(str(idx_file))
        store._chunks = pickle.loads(meta_file.read_bytes())
        store._dim = store._index.d  # type: ignore[attr-defined]

        logger.info(
            "VectorStore loaded: %d vector(s) from %s",
            store.size,
            idx_file,
        )
        return store

    @classmethod
    def load_or_create(cls, base_path: Optional[Path] = None) -> "VectorStore":
        """
        Load from disk if the index exists, otherwise create a fresh store.

        This is the recommended entry point for the application: it avoids
        a try/except at call sites.

        Args:
            base_path: Base path for persistence files.

        Returns:
            A ``VectorStore`` instance (possibly empty).
        """
        path = base_path or settings.faiss_index_path
        if _index_path(Path(path)).exists():
            try:
                return cls.load(path)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to load existing index (%s). Creating fresh store.", exc
                )
        return cls()

    def __repr__(self) -> str:
        return f"VectorStore(size={self.size}, dim={self._dim})"
