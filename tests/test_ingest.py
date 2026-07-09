"""
Module 2 tests — PDF Loader (src/rag/ingest.py)

Test strategy:
  - Unit tests use an in-memory PDF synthesised with PyMuPDF (no real files needed).
  - Integration tests verify the batch directory scanner.
  - Error path tests confirm graceful failures.

Run with:
    cd SciPilot
    python -m pytest tests/test_ingest.py -v
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List
from unittest.mock import patch

import fitz
import pytest

from src.rag.ingest import (
    PageDocument,
    _clean_text,
    _extract_metadata,
    ingest_directory,
    load_pdf_from_bytes,
    load_pdf_from_path,
    save_uploaded_pdf,
)


# ---------------------------------------------------------------------------
# Helpers — build synthetic PDFs in memory
# ---------------------------------------------------------------------------

def _make_pdf_bytes(pages: List[str]) -> bytes:
    """
    Create a minimal PDF with one text block per page.
    Returns the raw PDF bytes (no disk I/O).
    """
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((50, 72), text, fontsize=12)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _make_blank_pdf_bytes() -> bytes:
    """Single page with no text (simulates scanned page)."""
    doc = fitz.open()
    doc.new_page()
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# _clean_text
# ---------------------------------------------------------------------------

class TestCleanText:
    def test_strips_whitespace(self) -> None:
        assert _clean_text("  hello  ") == "hello"

    def test_collapses_whitespace_runs(self) -> None:
        result = _clean_text("foo   \t   bar")
        assert "   " not in result

    def test_removes_null_bytes(self) -> None:
        assert "\x00" not in _clean_text("hello\x00world")

    def test_empty_string(self) -> None:
        assert _clean_text("") == ""


# ---------------------------------------------------------------------------
# load_pdf_from_bytes
# ---------------------------------------------------------------------------

class TestLoadPdfFromBytes:
    def test_returns_page_documents(self) -> None:
        pdf = _make_pdf_bytes(["Hello world page one", "Second page content"])
        pages = load_pdf_from_bytes(pdf, filename="test.pdf")
        assert isinstance(pages, list)
        assert len(pages) == 2
        assert all(isinstance(p, PageDocument) for p in pages)

    def test_page_numbers_are_one_based(self) -> None:
        pdf = _make_pdf_bytes(["A", "B", "C"])
        pages = load_pdf_from_bytes(pdf, "test.pdf")
        assert [p.page_number for p in pages] == [1, 2, 3]

    def test_source_filename_stored(self) -> None:
        pdf = _make_pdf_bytes(["text"])
        pages = load_pdf_from_bytes(pdf, "my_paper.pdf")
        assert pages[0].source == "my_paper.pdf"

    def test_doc_hash_is_deterministic(self) -> None:
        pdf = _make_pdf_bytes(["reproducible content"])
        h1 = load_pdf_from_bytes(pdf, "f.pdf")[0].doc_hash
        h2 = load_pdf_from_bytes(pdf, "f.pdf")[0].doc_hash
        assert h1 == h2

    def test_doc_hash_differs_for_different_content(self) -> None:
        pdf1 = _make_pdf_bytes(["paper A"])
        pdf2 = _make_pdf_bytes(["paper B"])
        h1 = load_pdf_from_bytes(pdf1, "a.pdf")[0].doc_hash
        h2 = load_pdf_from_bytes(pdf2, "b.pdf")[0].doc_hash
        assert h1 != h2

    def test_raises_on_empty_bytes(self) -> None:
        with pytest.raises(ValueError, match="Empty bytes"):
            load_pdf_from_bytes(b"", "empty.pdf")

    def test_raises_on_invalid_pdf(self) -> None:
        with pytest.raises(RuntimeError, match="PyMuPDF could not open"):
            load_pdf_from_bytes(b"NOT A PDF AT ALL", "bad.pdf")

    def test_scanned_page_flagged(self) -> None:
        pdf = _make_blank_pdf_bytes()
        pages = load_pdf_from_bytes(pdf, "scanned.pdf")
        assert pages[0].is_scanned is True

    def test_text_page_not_flagged_as_scanned(self) -> None:
        pdf = _make_pdf_bytes(["This is a real research paper with plenty of words."])
        pages = load_pdf_from_bytes(pdf, "real.pdf")
        assert pages[0].is_scanned is False

    def test_word_count_property(self) -> None:
        pdf = _make_pdf_bytes(["one two three four five"])
        pages = load_pdf_from_bytes(pdf, "t.pdf")
        assert pages[0].word_count == 5

    def test_is_empty_property_on_scanned(self) -> None:
        pdf = _make_blank_pdf_bytes()
        pages = load_pdf_from_bytes(pdf, "s.pdf")
        assert pages[0].is_empty is True


# ---------------------------------------------------------------------------
# load_pdf_from_path
# ---------------------------------------------------------------------------

class TestLoadPdfFromPath:
    def test_loads_from_real_path(self, tmp_path: Path) -> None:
        pdf_bytes = _make_pdf_bytes(["File system test page"])
        pdf_file = tmp_path / "paper.pdf"
        pdf_file.write_bytes(pdf_bytes)

        pages = load_pdf_from_path(pdf_file)
        assert len(pages) == 1
        assert "File system test" in pages[0].text

    def test_raises_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_pdf_from_path(tmp_path / "missing.pdf")

    def test_raises_on_wrong_extension(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "doc.txt"
        txt_file.write_text("not a pdf")
        with pytest.raises(ValueError, match="Expected a .pdf"):
            load_pdf_from_path(txt_file)


# ---------------------------------------------------------------------------
# ingest_directory
# ---------------------------------------------------------------------------

class TestIngestDirectory:
    def test_returns_empty_list_for_empty_dir(self, tmp_path: Path) -> None:
        pages = ingest_directory(tmp_path)
        assert pages == []

    def test_ingests_all_pdfs(self, tmp_path: Path) -> None:
        for name, text in [
            ("alpha.pdf", ["Alpha paper page 1", "Alpha paper page 2"]),
            ("beta.pdf", ["Beta paper only page"]),
        ]:
            (tmp_path / name).write_bytes(_make_pdf_bytes(text))

        pages = ingest_directory(tmp_path)
        assert len(pages) == 3  # 2 + 1

    def test_skips_non_pdf_files(self, tmp_path: Path) -> None:
        (tmp_path / "notes.txt").write_text("ignore me")
        (tmp_path / "real.pdf").write_bytes(_make_pdf_bytes(["keep me"]))

        pages = ingest_directory(tmp_path)
        assert len(pages) == 1

    def test_continues_after_bad_pdf(self, tmp_path: Path) -> None:
        """One corrupt PDF must not abort ingestion of the others."""
        (tmp_path / "good.pdf").write_bytes(_make_pdf_bytes(["good content"]))
        (tmp_path / "bad.pdf").write_bytes(b"CORRUPTED DATA")

        pages = ingest_directory(tmp_path)
        assert len(pages) == 1


# ---------------------------------------------------------------------------
# save_uploaded_pdf
# ---------------------------------------------------------------------------

class TestSaveUploadedPdf:
    def test_saves_file_to_papers_dir(self, tmp_path: Path) -> None:
        pdf_bytes = _make_pdf_bytes(["save test"])

        with patch("src.rag.ingest.settings") as mock_settings:
            mock_settings.papers_dir = tmp_path
            dest = save_uploaded_pdf(pdf_bytes, "My Paper (2024).pdf")

        assert dest.exists()
        assert dest.read_bytes() == pdf_bytes

    def test_sanitises_filename(self, tmp_path: Path) -> None:
        pdf_bytes = _make_pdf_bytes(["x"])

        with patch("src.rag.ingest.settings") as mock_settings:
            mock_settings.papers_dir = tmp_path
            dest = save_uploaded_pdf(pdf_bytes, "Hello World! [v2].pdf")

        # No spaces or special characters in saved filename
        assert " " not in dest.name
        assert "!" not in dest.name


# ---------------------------------------------------------------------------
# PageDocument properties
# ---------------------------------------------------------------------------

class TestPageDocument:
    def test_repr_contains_key_info(self) -> None:
        doc = PageDocument(
            text="hello world test content here",
            page_number=3,
            source="paper.pdf",
            doc_hash="abc123",
            doc_title="Test Paper",
        )
        r = repr(doc)
        assert "paper.pdf" in r
        assert "page=3" in r

    def test_metadata_defaults_to_empty_dict(self) -> None:
        doc = PageDocument(
            text="text",
            page_number=1,
            source="s.pdf",
            doc_hash="h",
            doc_title="T",
        )
        assert doc.metadata == {}
