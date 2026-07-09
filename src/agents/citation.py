"""
SciPilot — Citation Generator  (src/agents/citation.py)
=========================================================
Converts ``TextChunk`` metadata into properly formatted academic citations
in APA 7th edition and IEEE styles.

Supported styles:
  APA   — Author, A. B., & Author, C. D. (Year). Title. *Source Name*.
  IEEE  — [N] A. B. Author and C. D. Author, "Title," *Source Name*, Year.

Design:
  - Pure Python — no external APIs, no network calls.
  - Graceful degradation: every field has a sensible fallback string.
  - Deduplication: the same document (identified by doc_hash) produces
    exactly one reference entry, regardless of how many chunks are cited.
  - The ``CitationAgent`` can be called directly with a list of chunks,
    making it easy to use from both the Orchestrator and the Dashboard.

Dependencies:
  - src.rag.chunk   (TextChunk)
  - src.utils.logger (get_logger)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from src.rag.chunk import TextChunk
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Citation style enum
# ---------------------------------------------------------------------------

class CitationStyle(str, Enum):
    """Supported citation formatting styles."""
    APA = "APA"
    IEEE = "IEEE"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Citation:
    """
    A single formatted citation for one document.

    Attributes:
        index:        1-based position in the references list.
        doc_hash:     SHA-256 of the source document (deduplication key).
        title:        Paper title.
        authors:      Formatted author string.
        year:         Publication year (string, e.g. "2017").
        source_name:  Journal / conference / filename.
        page_number:  Page first cited in the answer.
        formatted:    The fully formatted citation string.
        style:        ``CitationStyle.APA`` or ``CitationStyle.IEEE``.
    """
    index: int
    doc_hash: str
    title: str
    authors: str
    year: str
    source_name: str
    page_number: int
    formatted: str
    style: CitationStyle


@dataclass
class CitationResult:
    """
    Output of ``CitationAgent.generate()``.

    Attributes:
        citations:        List of ``Citation`` objects, one per unique document.
        style:            The style used.
        references_block: A formatted ``## References`` section (Markdown).
        inline_map:       Maps original 1-based chunk position → citation index,
                          for updating inline markers in the answer text.
    """
    citations: List[Citation]
    style: CitationStyle
    references_block: str = ""
    inline_map: Dict[int, int] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return len(self.citations) == 0

    def __repr__(self) -> str:
        return (
            f"CitationResult(count={len(self.citations)}, "
            f"style={self.style.value})"
        )


# ---------------------------------------------------------------------------
# Metadata extraction helpers
# ---------------------------------------------------------------------------

_YEAR_RE = re.compile(r"(19|20)\d{2}")            # matches 4-digit years 1900–2099 (no word-boundary needed)
_DOI_RE  = re.compile(r"10\.\d{4,}/\S+")          # matches DOI strings


def _extract_year(text: str) -> str:
    """
    Extract the first 4-digit year found in *text*.

    Searches the document title, author string, creation_date metadata,
    and source filename in that order.

    Args:
        text: Any string that may contain a year.

    Returns:
        Year as a 4-character string, or ``"n.d."`` (no date) if not found.
    """
    m = _YEAR_RE.search(text)
    return m.group(0) if m else "n.d."


def _parse_authors_apa(raw_authors: str) -> str:
    """
    Convert a raw author string to APA last-name-first format.

    Handles common delimiters: semicolons, " and ", " & ", commas.

    Examples:
        "Vaswani, A.; Shazeer, N."   → "Vaswani, A., & Shazeer, N."
        "John Smith and Jane Doe"    → "Smith, J., & Doe, J."
        ""                           → "Unknown Author"

    Args:
        raw_authors: Raw author string from PDF metadata.

    Returns:
        APA-formatted author string.
    """
    if not raw_authors.strip():
        return "Unknown Author"

    # Split on semicolon, " and ", " & ", or comma-separated full names
    parts = re.split(r";| and | & ", raw_authors)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        return "Unknown Author"

    formatted: List[str] = []
    for part in parts:
        formatted.append(_format_single_author_apa(part))

    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]}, & {formatted[1]}"
    # 3+ authors
    return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def _format_single_author_apa(name: str) -> str:
    """
    Format a single author name in APA style: ``Last, F. M.``

    If the name is already in "Last, First" form it is kept as-is (with
    initials abbreviated). If it is in "First Last" form it is reversed.

    Args:
        name: A single author name string.

    Returns:
        APA-formatted single author name.
    """
    name = name.strip()
    if not name:
        return "Unknown Author"

    # Already "Last, First" form (contains comma)
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]
        last = parts[0]
        first_parts = parts[1].split() if len(parts) > 1 else []
        initials = ". ".join(w[0].upper() for w in first_parts if w) + "." if first_parts else ""
        return f"{last}, {initials}" if initials else last

    # "First [Middle] Last" form
    tokens = name.split()
    if len(tokens) == 1:
        return tokens[0]

    last = tokens[-1]
    initials = ". ".join(t[0].upper() for t in tokens[:-1]) + "."
    return f"{last}, {initials}"


def _parse_authors_ieee(raw_authors: str) -> str:
    """
    Convert a raw author string to IEEE abbreviated-first-name format.

    Example:
        "Ashish Vaswani and Noam Shazeer" → "A. Vaswani and N. Shazeer"

    Args:
        raw_authors: Raw author string from PDF metadata.

    Returns:
        IEEE-formatted author string.
    """
    if not raw_authors.strip():
        return "Unknown Author"

    parts = re.split(r";| and | & ", raw_authors)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        return "Unknown Author"

    formatted: List[str] = []
    for part in parts:
        formatted.append(_format_single_author_ieee(part))

    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"


def _format_single_author_ieee(name: str) -> str:
    """
    Format a single author name for IEEE: ``F. M. Last``

    Args:
        name: Single author name.

    Returns:
        IEEE-formatted name string.
    """
    name = name.strip()
    if not name:
        return "Unknown"

    # "Last, First" form
    if "," in name:
        parts = [p.strip() for p in name.split(",", 1)]
        last = parts[0]
        first_parts = parts[1].split() if len(parts) > 1 else []
        initials = " ".join(f"{t[0].upper()}." for t in first_parts if t) if first_parts else ""
        return f"{initials} {last}".strip()

    # "First Last" form
    tokens = name.split()
    if len(tokens) == 1:
        return tokens[0]
    last = tokens[-1]
    initials = " ".join(f"{t[0].upper()}." for t in tokens[:-1])
    return f"{initials} {last}"


def _source_name_from_chunk(chunk: TextChunk) -> str:
    """
    Derive a human-readable source name from a ``TextChunk``.

    Priority:
        1. ``doc_subject`` (journal/conference from PDF metadata)
        2. ``source`` filename without extension
        3. ``"Unknown Source"``

    Args:
        chunk: Any ``TextChunk``.

    Returns:
        Source name string.
    """
    if chunk.doc_subject and chunk.doc_subject.strip():
        return chunk.doc_subject.strip()
    stem = re.sub(r"\.pdf$", "", chunk.source, flags=re.IGNORECASE)
    return stem.replace("_", " ").replace("-", " ").strip() or "Unknown Source"


def _extract_year_from_chunk(chunk: TextChunk) -> str:
    """
    Try to find a year in the chunk's metadata fields.

    Args:
        chunk: TextChunk with metadata dict.

    Returns:
        4-digit year string or ``"n.d."``.
    """
    creation_date = chunk.metadata.get("creation_date", "")
    year = _extract_year(creation_date)
    if year != "n.d.":
        return year
    # Fallback: look in the title or source filename
    year = _extract_year(chunk.doc_title + " " + chunk.source)
    return year


# ---------------------------------------------------------------------------
# Citation formatters
# ---------------------------------------------------------------------------

def _format_apa(
    index: int,
    title: str,
    authors: str,
    year: str,
    source_name: str,
) -> str:
    """
    Format a single APA 7th edition citation.

    Pattern:
        Author, A. B., & Author, C. D. (Year). *Title*. *Source Name*.

    Args:
        index:       1-based citation number (not used in APA body but kept
                     for reference list numbering parity with IEEE).
        title:       Paper title.
        authors:     APA-formatted author string.
        year:        Publication year or "n.d.".
        source_name: Journal / conference / filename.

    Returns:
        Formatted APA citation string.
    """
    return f"{authors} ({year}). *{title}*. *{source_name}*."


def _format_ieee(
    index: int,
    title: str,
    authors: str,
    year: str,
    source_name: str,
) -> str:
    """
    Format a single IEEE citation.

    Pattern:
        [N] A. B. Author and C. D. Author, "Title," *Source Name*, Year.

    Args:
        index:       1-based position in the references list.
        title:       Paper title.
        authors:     IEEE-formatted author string.
        year:        Publication year or "n.d.".
        source_name: Journal / conference / filename.

    Returns:
        Formatted IEEE citation string.
    """
    return f"[{index}] {authors}, \"{title},\" *{source_name}*, {year}."


# ---------------------------------------------------------------------------
# Citation Agent
# ---------------------------------------------------------------------------

class CitationAgent:
    """
    Generates APA or IEEE citations from a list of ``TextChunk`` objects.

    Usage:
        agent = CitationAgent(style=CitationStyle.APA)
        result = agent.generate(synthesis_result.cited_chunks)
        print(result.references_block)
    """

    def __init__(self, style: CitationStyle = CitationStyle.APA) -> None:
        """
        Args:
            style: ``CitationStyle.APA`` (default) or ``CitationStyle.IEEE``.
        """
        self._style = style
        logger.info("CitationAgent initialised (style=%s).", style.value)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        chunks: List[TextChunk],
        original_positions: Optional[List[int]] = None,
    ) -> CitationResult:
        """
        Generate a ``CitationResult`` for all unique documents in *chunks*.

        Deduplication: if multiple chunks come from the same document
        (same ``doc_hash``), only one citation entry is produced.

        Args:
            chunks:             List of cited ``TextChunk`` objects.
                                Typically ``SynthesisResult.cited_chunks``.
            original_positions: 1-based positions of these chunks in the
                                original retrieval list (used to build
                                ``inline_map``).  If omitted, positions are
                                inferred as 1, 2, 3 …

        Returns:
            A ``CitationResult`` with formatted citations and a references block.
        """
        if not chunks:
            logger.warning("CitationAgent.generate called with empty chunk list.")
            return CitationResult(
                citations=[],
                style=self._style,
                references_block="",
                inline_map={},
            )

        positions = original_positions or list(range(1, len(chunks) + 1))

        # ── Deduplicate by doc_hash ────────────────────────────────────────
        seen_hashes: Dict[str, int] = {}   # doc_hash → citation index
        citations: List[Citation] = []
        inline_map: Dict[int, int] = {}    # original position → citation index

        for original_pos, chunk in zip(positions, chunks):
            if chunk.doc_hash in seen_hashes:
                inline_map[original_pos] = seen_hashes[chunk.doc_hash]
                continue

            cite_index = len(citations) + 1
            seen_hashes[chunk.doc_hash] = cite_index

            citation = self._build_citation(chunk, cite_index)
            citations.append(citation)
            inline_map[original_pos] = cite_index

        references_block = self._build_references_block(citations)

        logger.info(
            "Generated %d citation(s) (%s style) from %d chunk(s).",
            len(citations),
            self._style.value,
            len(chunks),
        )

        return CitationResult(
            citations=citations,
            style=self._style,
            references_block=references_block,
            inline_map=inline_map,
        )

    def generate_from_synthesis(self, synthesis_result) -> CitationResult:
        """
        Convenience wrapper: generate citations from a ``SynthesisResult``.

        Args:
            synthesis_result: A ``SynthesisResult`` from Module 6.

        Returns:
            A ``CitationResult``.
        """
        cited_chunks = synthesis_result.cited_chunks
        cited_indices = synthesis_result.cited_indices
        return self.generate(cited_chunks, original_positions=cited_indices)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_citation(self, chunk: TextChunk, index: int) -> Citation:
        """
        Build a single ``Citation`` object from a ``TextChunk``.

        Args:
            chunk: Source chunk.
            index: 1-based citation number.

        Returns:
            Populated ``Citation``.
        """
        title = chunk.doc_title or Path_stem(chunk.source)
        year = _extract_year_from_chunk(chunk)
        source_name = _source_name_from_chunk(chunk)

        if self._style == CitationStyle.APA:
            authors = _parse_authors_apa(chunk.doc_authors)
            formatted = _format_apa(index, title, authors, year, source_name)
        else:  # IEEE
            authors = _parse_authors_ieee(chunk.doc_authors)
            formatted = _format_ieee(index, title, authors, year, source_name)

        return Citation(
            index=index,
            doc_hash=chunk.doc_hash,
            title=title,
            authors=authors,
            year=year,
            source_name=source_name,
            page_number=chunk.page_number,
            formatted=formatted,
            style=self._style,
        )

    def _build_references_block(self, citations: List[Citation]) -> str:
        """
        Build a Markdown ``## References`` section from a list of citations.

        APA example:
            ## References

            Vaswani, A., & Shazeer, N. (2017). *Attention Is All You Need*. *arXiv*.

        IEEE example:
            ## References

            [1] A. Vaswani and N. Shazeer, "Attention Is All You Need," *arXiv*, 2017.

        Args:
            citations: Ordered list of ``Citation`` objects.

        Returns:
            Formatted Markdown string.
        """
        if not citations:
            return ""

        lines = ["## References", ""]
        for cite in citations:
            lines.append(cite.formatted)
            lines.append("")  # blank line between entries

        return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Tiny helper (avoids importing pathlib at top for a one-liner)
# ---------------------------------------------------------------------------

def Path_stem(filename: str) -> str:
    """Return the filename stem (without extension)."""
    import os
    return os.path.splitext(filename)[0]
