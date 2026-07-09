"""
SciPilot — PDF Loader  (src/rag/ingest.py)
============================================
Responsible for reading research papers (PDF format) and converting them
into structured ``PageDocument`` objects that the rest of the RAG pipeline
can consume.

Design goals:
  - Accept both file paths and raw bytes so it integrates with Streamlit
    file-uploader and with command-line batch ingestion equally well.
  - Never crash on a bad PDF — degrade gracefully and log warnings.
  - Deduplicate via SHA-256 so the same paper is never processed twice.
  - Preserve page-level metadata (page number, source file) so citations
    later in the pipeline can reference the exact page.

Dependencies:
  - PyMuPDF  (``pip install PyMuPDF``)  — imported as ``fitz``
  - src.utils.config  (settings singleton)
  - src.utils.logger  (structured logger)
  - src.utils.helpers (hash_text, sanitise_filename, ensure_dir)
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import fitz  # PyMuPDF

from src.utils.config import settings
from src.utils.helpers import ensure_dir, hash_text, sanitise_filename
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class PageDocument:
    """
    Represents a single page extracted from a PDF.

    This is the unit of data passed from the PDF Loader to the Chunker.
    Keeping pages as separate objects lets the chunker respect page
    boundaries and lets the citation generator reference exact pages.

    Attributes:
        text:        Raw extracted text for this page (may be empty for
                     scanned pages).
        page_number: 1-based page number within the source PDF.
        source:      Original file name (not full path — for display).
        doc_hash:    SHA-256 hex digest of the entire PDF file.
        doc_title:   Title extracted from PDF metadata (or filename fallback).
        doc_authors: Authors extracted from PDF metadata (may be empty).
        doc_subject: Subject/keywords from PDF metadata.
        is_scanned:  True when no text could be extracted (image-only page).
        metadata:    Additional arbitrary key-value metadata.
    """

    text: str
    page_number: int
    source: str
    doc_hash: str
    doc_title: str
    doc_authors: str = ""
    doc_subject: str = ""
    is_scanned: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def word_count(self) -> int:
        """Approximate word count of the page text."""
        return len(self.text.split())

    @property
    def is_empty(self) -> bool:
        """True when the page contains no useful text."""
        return self.word_count < 5

    def __repr__(self) -> str:
        return (
            f"PageDocument(source={self.source!r}, "
            f"page={self.page_number}, words={self.word_count}, "
            f"scanned={self.is_scanned})"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s{3,}")  # Three or more consecutive whitespace chars


def _clean_text(raw: str) -> str:
    """
    Light normalisation applied to each page's raw extracted text.

    Steps:
        1. Strip leading/trailing whitespace.
        2. Replace runs of 3+ whitespace characters with a single space
           (PDF text extraction often produces wide gaps between columns).
        3. Remove null bytes that some PDFs embed.

    Args:
        raw: Raw text string from PyMuPDF.

    Returns:
        Cleaned text string.
    """
    text = raw.strip()
    text = text.replace("\x00", "")          # remove null bytes
    text = _WHITESPACE_RE.sub(" ", text)     # collapse whitespace runs
    return text


def _extract_metadata(doc: fitz.Document, filename: str) -> Dict[str, str]:
    """
    Pull structured metadata from the PDF document object.

    PyMuPDF exposes ``doc.metadata`` as a dict with keys like
    ``title``, ``author``, ``subject``, ``keywords``, ``creationDate``.
    All values may be empty strings — we normalise them here.

    Args:
        doc:      Open ``fitz.Document`` object.
        filename: Fallback display name when the PDF title is blank.

    Returns:
        Dict with normalised keys: title, authors, subject, keywords,
        creation_date, page_count.
    """
    raw: Dict[str, str] = doc.metadata or {}

    title = raw.get("title", "").strip() or Path(filename).stem
    authors = raw.get("author", "").strip()
    subject = raw.get("subject", "").strip()
    keywords = raw.get("keywords", "").strip()
    creation_date = raw.get("creationDate", "").strip()

    return {
        "title": title,
        "authors": authors,
        "subject": subject,
        "keywords": keywords,
        "creation_date": creation_date,
        "page_count": str(doc.page_count),
    }


# ---------------------------------------------------------------------------
# Core ingestion functions
# ---------------------------------------------------------------------------

def load_pdf_from_bytes(
    pdf_bytes: bytes,
    filename: str = "document.pdf",
) -> List[PageDocument]:
    """
    Load a PDF from raw bytes and return one ``PageDocument`` per page.

    This is the primary entry point when integrating with Streamlit's
    ``st.file_uploader``, which provides ``UploadedFile.read()`` bytes.

    Args:
        pdf_bytes: Raw PDF file content as bytes.
        filename:  Display name for the document (used in metadata/citations).

    Returns:
        List of ``PageDocument`` objects, one per page.

    Raises:
        ValueError: If pdf_bytes is empty.
        RuntimeError: If PyMuPDF cannot open the bytes as a valid PDF.
    """
    if not pdf_bytes:
        raise ValueError(f"Empty bytes received for '{filename}'.")

    doc_hash = hash_text(pdf_bytes.decode("latin-1", errors="replace"))
    logger.info("Ingesting '%s' (%.1f KB, hash=%s…)", filename,
                len(pdf_bytes) / 1024, doc_hash[:8])

    try:
        doc: fitz.Document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise RuntimeError(f"PyMuPDF could not open '{filename}': {exc}") from exc

    return _extract_pages(doc, filename=filename, doc_hash=doc_hash)


def load_pdf_from_path(pdf_path: Union[str, Path]) -> List[PageDocument]:
    """
    Load a PDF from a file system path and return one ``PageDocument`` per page.

    Used for batch ingestion from the ``research_papers/`` directory.

    Args:
        pdf_path: Absolute or relative path to a ``.pdf`` file.

    Returns:
        List of ``PageDocument`` objects, one per page.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError:        If the file is not a PDF.
        RuntimeError:      If PyMuPDF cannot parse the file.
    """
    path = Path(pdf_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.name}")

    pdf_bytes = path.read_bytes()
    return load_pdf_from_bytes(pdf_bytes, filename=path.name)


def ingest_directory(papers_dir: Optional[Path] = None) -> List[PageDocument]:
    """
    Ingest **all** PDFs found in *papers_dir* (non-recursive).

    Useful for batch ingestion at startup. Skips files that fail to load
    and logs an error for each, so one bad PDF does not abort the batch.

    Args:
        papers_dir: Directory to scan. Defaults to ``settings.papers_dir``.

    Returns:
        Flat list of ``PageDocument`` objects from all successfully
        loaded PDFs, ordered by filename then page number.
    """
    directory = papers_dir or settings.papers_dir
    ensure_dir(Path(directory))

    pdf_files = sorted(Path(directory).glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in '%s'.", directory)
        return []

    logger.info("Found %d PDF file(s) in '%s'.", len(pdf_files), directory)

    all_pages: List[PageDocument] = []
    for pdf_path in pdf_files:
        try:
            pages = load_pdf_from_path(pdf_path)
            all_pages.extend(pages)
            logger.info(
                "  ✓ %s — %d page(s), %d non-empty",
                pdf_path.name,
                len(pages),
                sum(1 for p in pages if not p.is_empty),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("  ✗ Failed to load '%s': %s", pdf_path.name, exc)

    logger.info(
        "Ingestion complete: %d total pages from %d file(s).",
        len(all_pages),
        len(pdf_files),
    )
    return all_pages


# ---------------------------------------------------------------------------
# Private — page extraction
# ---------------------------------------------------------------------------

def _extract_pages(
    doc: fitz.Document,
    filename: str,
    doc_hash: str,
) -> List[PageDocument]:
    """
    Iterate over every page of an open ``fitz.Document`` and build
    ``PageDocument`` objects.

    Args:
        doc:      Open PyMuPDF document (caller owns closing it).
        filename: Display name for log messages and metadata.
        doc_hash: Pre-computed SHA-256 hash of the file bytes.

    Returns:
        List of ``PageDocument``, one per page.
    """
    meta = _extract_metadata(doc, filename)
    pages: List[PageDocument] = []

    scanned_count = 0
    total_pages = doc.page_count  # capture before close

    for page_index in range(total_pages):
        page: fitz.Page = doc.load_page(page_index)
        raw_text: str = page.get_text("text")  # type: ignore[attr-defined]
        cleaned = _clean_text(raw_text)

        is_scanned = len(cleaned.strip()) < 20  # heuristic: fewer than 20 chars
        if is_scanned:
            scanned_count += 1

        page_doc = PageDocument(
            text=cleaned,
            page_number=page_index + 1,  # 1-based
            source=filename,
            doc_hash=doc_hash,
            doc_title=meta["title"],
            doc_authors=meta["authors"],
            doc_subject=meta["subject"],
            is_scanned=is_scanned,
            metadata={
                "keywords": meta["keywords"],
                "creation_date": meta["creation_date"],
                "total_pages": meta["page_count"],
            },
        )
        pages.append(page_doc)

    doc.close()

    if scanned_count:
        logger.warning(
            "'%s' has %d/%d scanned (image-only) page(s). "
            "Text cannot be extracted from those pages.",
            filename,
            scanned_count,
            total_pages,
        )

    return pages


# ---------------------------------------------------------------------------
# Convenience — save uploaded file to disk
# ---------------------------------------------------------------------------

def save_uploaded_pdf(pdf_bytes: bytes, filename: str) -> Path:
    """
    Persist an uploaded PDF to ``settings.papers_dir`` so it is available
    for batch re-ingestion on the next run.

    The file is saved with a sanitised filename to avoid path traversal
    or special-character issues on Windows.

    Args:
        pdf_bytes: Raw PDF bytes from ``st.file_uploader``.
        filename:  Original filename from the uploader.

    Returns:
        The Path where the file was saved.
    """
    ensure_dir(settings.papers_dir)
    safe_name = sanitise_filename(filename)
    if not safe_name.endswith(".pdf"):
        safe_name += ".pdf"

    dest = settings.papers_dir / safe_name
    dest.write_bytes(pdf_bytes)
    logger.info("Saved uploaded PDF to '%s' (%d bytes).", dest, len(pdf_bytes))
    return dest
