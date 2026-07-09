"""
SciPilot — Text Chunker  (src/rag/chunk.py)
=============================================
Converts a list of ``PageDocument`` objects (Module 2) into a list of
overlapping ``TextChunk`` objects that are small enough to be embedded and
stored in FAISS (Module 4).

Design goals:
  - Semantic splitting: always try to cut at paragraph → sentence → word
    boundaries before hard-cutting mid-word.
  - Overlap: consecutive chunks share ``chunk_overlap`` characters so no
    sentence is ever completely cut off between two chunks.
  - Full provenance: every chunk carries source file, page number, doc hash,
    and character offsets so citations can be reconstructed later.
  - Zero external dependencies beyond the standard library (LangChain's
    splitter is replicated here so the chunker is self-contained and testable
    without network access).

Dependencies:
  - src.rag.ingest   (PageDocument data class)
  - src.utils.config (settings singleton)
  - src.utils.logger (structured logger)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.rag.ingest import PageDocument
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TextChunk:
    """
    A single text segment produced by the chunker.

    This is the unit passed to the embedding module (Module 4) and stored
    in the FAISS index.  All fields are intentionally flat (no nesting) so
    the object serialises cleanly to JSON for persistence.

    Attributes:
        text:        The actual text content of the chunk.
        chunk_index: Zero-based position of this chunk within its document.
        doc_hash:    SHA-256 of the source PDF (deduplication key).
        doc_title:   Human-readable document title.
        doc_authors: Author string from PDF metadata.
        source:      Original filename (e.g. ``"attention_is_all_you_need.pdf"``).
        page_number: Page number where this chunk *begins*.
        char_start:  Character offset of the chunk's first character within
                     the full document text stream.
        char_end:    Character offset just past the last character.
        metadata:    Extra key-value pairs (keywords, creation date, etc.)
    """

    text: str
    chunk_index: int
    doc_hash: str
    doc_title: str
    source: str
    page_number: int
    char_start: int
    char_end: int
    doc_authors: str = ""
    doc_subject: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def word_count(self) -> int:
        """Approximate word count."""
        return len(self.text.split())

    @property
    def char_count(self) -> int:
        """Number of characters in this chunk."""
        return len(self.text)

    def to_dict(self) -> Dict[str, object]:
        """
        Serialise to a plain dict for FAISS metadata storage.
        FAISS metadata values must be strings, ints, or floats.
        """
        return {
            "text": self.text,
            "chunk_index": self.chunk_index,
            "doc_hash": self.doc_hash,
            "doc_title": self.doc_title,
            "doc_authors": self.doc_authors,
            "source": self.source,
            "page_number": self.page_number,
            "char_start": self.char_start,
            "char_end": self.char_end,
            **{f"meta_{k}": v for k, v in self.metadata.items()},
        }

    def __repr__(self) -> str:
        return (
            f"TextChunk(source={self.source!r}, page={self.page_number}, "
            f"idx={self.chunk_index}, chars={self.char_count})"
        )


# ---------------------------------------------------------------------------
# Recursive character splitter
# ---------------------------------------------------------------------------

# Priority-ordered list of separators — the splitter tries each in order.
# It falls back to the next separator when a split at the current level
# would produce pieces that are still larger than chunk_size.
_DEFAULT_SEPARATORS: List[str] = [
    "\n\n",   # paragraph boundary (highest preference)
    "\n",     # line boundary
    ". ",     # sentence boundary
    "! ",     # exclamation sentence
    "? ",     # question sentence
    "; ",     # clause boundary
    ", ",     # phrase boundary
    " ",      # word boundary
    "",       # hard cut (last resort — no semantic meaning)
]


def _split_text_recursive(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: Optional[List[str]] = None,
) -> List[Tuple[str, int]]:
    """
    Recursively split *text* into chunks ≤ *chunk_size* characters,
    trying each separator in *separators* from left to right.

    Returns a list of ``(chunk_text, char_start)`` tuples where
    ``char_start`` is the offset of that chunk's first character within
    the original *text*.

    Args:
        text:          Full document text (may be thousands of characters).
        chunk_size:    Maximum characters per chunk.
        chunk_overlap: Characters of overlap between consecutive chunks.
        separators:    Ordered list of separator strings.  Defaults to
                       ``_DEFAULT_SEPARATORS``.

    Returns:
        List of ``(chunk_text, char_start)`` tuples, non-overlapping in
        terms of *content* but with the semantic overlap applied.
    """
    if separators is None:
        separators = _DEFAULT_SEPARATORS

    # ── Base case: text already fits in one chunk ─────────────────────────
    if len(text) <= chunk_size:
        return [(text, 0)] if text.strip() else []

    # ── Find the first separator that produces splits ──────────────────────
    chosen_sep = ""
    remaining_seps = list(separators)

    for sep in separators:
        if sep == "" or sep in text:
            chosen_sep = sep
            remaining_seps = separators[separators.index(sep) + 1 :]
            break

    # ── Split on chosen separator ──────────────────────────────────────────
    if chosen_sep:
        raw_splits = text.split(chosen_sep)
        # Re-attach the separator to each piece (except the last) so that
        # when pieces are merged, the separator is not lost.
        splits_with_sep = []
        for i, piece in enumerate(raw_splits):
            if i < len(raw_splits) - 1:
                splits_with_sep.append(piece + chosen_sep)
            else:
                splits_with_sep.append(piece)
    else:
        # Hard cut at chunk_size
        splits_with_sep = [
            text[i : i + chunk_size] for i in range(0, len(text), chunk_size)
        ]

    # ── Merge small splits into chunks respecting chunk_size ──────────────
    chunks: List[Tuple[str, int]] = []
    current_pieces: List[str] = []
    current_len = 0
    # Track the char offset of the start of current_pieces within `text`
    cursor = 0
    current_start = 0

    for piece in splits_with_sep:
        piece_len = len(piece)

        if current_len + piece_len > chunk_size and current_pieces:
            # Emit the current buffer as a chunk
            chunk_text = "".join(current_pieces).strip()
            if chunk_text:
                chunks.append((chunk_text, current_start))

            # Apply overlap: keep the last `chunk_overlap` characters
            overlap_text = "".join(current_pieces)[-chunk_overlap:]
            # Find the start offset of the overlap within the original text
            overlap_start = cursor - len(overlap_text)
            current_pieces = [overlap_text] if overlap_text.strip() else []
            current_len = len(overlap_text)
            current_start = max(0, overlap_start)

        if piece_len > chunk_size:
            # Single piece is too large — recurse with the next separator
            if current_pieces:
                chunk_text = "".join(current_pieces).strip()
                if chunk_text:
                    chunks.append((chunk_text, current_start))
                current_pieces = []
                current_len = 0
                current_start = cursor

            sub_chunks = _split_text_recursive(
                piece, chunk_size, chunk_overlap, remaining_seps
            )
            # Adjust sub-chunk offsets relative to `text`
            chunks.extend((sc, cursor + off) for sc, off in sub_chunks)
            cursor += piece_len
            current_start = cursor
            continue

        current_pieces.append(piece)
        current_len += piece_len
        cursor += piece_len

    # Flush remaining buffer
    if current_pieces:
        chunk_text = "".join(current_pieces).strip()
        if chunk_text:
            chunks.append((chunk_text, current_start))

    return chunks


# ---------------------------------------------------------------------------
# Page-offset mapping
# ---------------------------------------------------------------------------

def _build_page_offset_map(pages: List[PageDocument]) -> List[Tuple[int, int]]:
    """
    Build a mapping from character offset in the concatenated document stream
    to the corresponding 1-based page number.

    Returns:
        List of ``(start_char, page_number)`` pairs, sorted by start_char.
        Given a char offset ``c``, the page is the ``page_number`` of the
        last entry whose ``start_char <= c``.
    """
    offset_map: List[Tuple[int, int]] = []
    cursor = 0
    for page in pages:
        offset_map.append((cursor, page.page_number))
        cursor += len(page.text) + 1  # +1 for the "\n" join character
    return offset_map


def _char_offset_to_page(offset: int, offset_map: List[Tuple[int, int]]) -> int:
    """
    Binary search the offset map to find the page number for a given
    character offset.

    Args:
        offset:     Character offset in the full document text stream.
        offset_map: Output of ``_build_page_offset_map``.

    Returns:
        1-based page number.
    """
    page_num = offset_map[0][1]  # default: first page
    for start, pnum in offset_map:
        if start <= offset:
            page_num = pnum
        else:
            break
    return page_num


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_documents(
    pages: List[PageDocument],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[TextChunk]:
    """
    Split a list of ``PageDocument`` objects into overlapping ``TextChunk``
    objects.

    This is the primary entry point called by Module 4 (Embeddings).

    Args:
        pages:         Output of ``ingest.load_pdf_from_bytes()`` or
                       ``ingest.ingest_directory()``.
        chunk_size:    Max characters per chunk.  Defaults to
                       ``settings.chunk_size`` (512).
        chunk_overlap: Characters of overlap.  Defaults to
                       ``settings.chunk_overlap`` (64).

    Returns:
        List of ``TextChunk`` objects sorted by (source, chunk_index).
    """
    if not pages:
        logger.warning("chunk_documents received an empty page list.")
        return []

    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap

    # ── Group pages by document (doc_hash) ───────────────────────────────
    from collections import defaultdict
    doc_groups: Dict[str, List[PageDocument]] = defaultdict(list)
    for page in pages:
        doc_groups[page.doc_hash].append(page)

    all_chunks: List[TextChunk] = []

    for doc_hash, doc_pages in doc_groups.items():
        # Sort pages by page_number to guarantee correct order
        doc_pages.sort(key=lambda p: p.page_number)

        # Filter out scanned/empty pages before chunking
        usable = [p for p in doc_pages if not p.is_empty]
        if not usable:
            logger.warning(
                "Document '%s' has no usable text pages — skipping.",
                doc_pages[0].source,
            )
            continue

        doc_chunks = _chunk_single_document(usable, size, overlap)
        all_chunks.extend(doc_chunks)

        logger.info(
            "Chunked '%s': %d page(s) → %d chunk(s) "
            "(chunk_size=%d, overlap=%d)",
            doc_pages[0].source,
            len(usable),
            len(doc_chunks),
            size,
            overlap,
        )

    logger.info(
        "Total: %d chunk(s) from %d document(s).",
        len(all_chunks),
        len(doc_groups),
    )
    return all_chunks


def _chunk_single_document(
    pages: List[PageDocument],
    chunk_size: int,
    chunk_overlap: int,
) -> List[TextChunk]:
    """
    Chunk the pages of a **single** document.

    Steps:
        1. Join all page texts with ``"\\n"`` into one continuous stream.
        2. Build a page-offset map for provenance tracking.
        3. Split using ``_split_text_recursive``.
        4. Wrap each split into a ``TextChunk`` with full metadata.

    Args:
        pages:         Sorted, non-empty ``PageDocument`` list for one document.
        chunk_size:    Max characters per chunk.
        chunk_overlap: Overlap characters.

    Returns:
        List of ``TextChunk`` objects.
    """
    full_text = "\n".join(p.text for p in pages)
    offset_map = _build_page_offset_map(pages)

    # Shared metadata from the first page (all pages of a doc share these)
    first = pages[0]

    raw_chunks = _split_text_recursive(full_text, chunk_size, chunk_overlap)

    text_chunks: List[TextChunk] = []
    for idx, (chunk_text, char_start) in enumerate(raw_chunks):
        if not chunk_text.strip():
            continue  # skip whitespace-only chunks

        char_end = char_start + len(chunk_text)
        page_num = _char_offset_to_page(char_start, offset_map)

        text_chunks.append(
            TextChunk(
                text=chunk_text,
                chunk_index=idx,
                doc_hash=first.doc_hash,
                doc_title=first.doc_title,
                doc_authors=first.doc_authors,
                doc_subject=first.doc_subject,
                source=first.source,
                page_number=page_num,
                char_start=char_start,
                char_end=char_end,
                metadata=first.metadata,
            )
        )

    return text_chunks


# ---------------------------------------------------------------------------
# Utility — chunk a plain string (used by tests and other modules)
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[str]:
    """
    Split a plain string into a list of chunk strings.

    A convenience wrapper around ``_split_text_recursive`` for callers that
    do not have ``PageDocument`` objects (e.g. the VerificationAgent in
    Module 10 chunking a generated answer for cross-checking).

    Args:
        text:          Input string.
        chunk_size:    Max characters per chunk.
        chunk_overlap: Overlap characters.

    Returns:
        List of chunk strings.
    """
    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap
    return [t for t, _ in _split_text_recursive(text, size, overlap)]
