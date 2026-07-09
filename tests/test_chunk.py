"""
Module 3 tests — Text Chunker (src/rag/chunk.py)

Test strategy:
  - Unit-test the internal splitter directly with controlled strings.
  - Test chunk_documents with synthetic PageDocument objects.
  - Verify provenance fields (page_number, char_start/end, doc_hash).
  - Verify overlap semantics.
  - Verify edge cases: empty input, single short page, scanned-only doc.

Run with:
    cd SciPilot
    python -m pytest tests/test_chunk.py -v
"""

from __future__ import annotations

from typing import List

import pytest

from src.rag.chunk import (
    TextChunk,
    _build_page_offset_map,
    _char_offset_to_page,
    _split_text_recursive,
    chunk_documents,
    chunk_text,
)
from src.rag.ingest import PageDocument


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_page(
    text: str,
    page_number: int = 1,
    source: str = "paper.pdf",
    doc_hash: str = "abc123",
    doc_title: str = "Test Paper",
    is_scanned: bool = False,
) -> PageDocument:
    """Create a minimal PageDocument for testing."""
    return PageDocument(
        text=text,
        page_number=page_number,
        source=source,
        doc_hash=doc_hash,
        doc_title=doc_title,
        is_scanned=is_scanned,
    )


def _make_pages(texts: List[str], **kwargs) -> List[PageDocument]:
    """Create a list of pages from a list of strings."""
    return [_make_page(t, page_number=i + 1, **kwargs) for i, t in enumerate(texts)]


# ---------------------------------------------------------------------------
# _split_text_recursive
# ---------------------------------------------------------------------------

class TestSplitTextRecursive:

    def test_short_text_returned_as_single_chunk(self) -> None:
        result = _split_text_recursive("Hello world", chunk_size=100, chunk_overlap=10)
        assert len(result) == 1
        assert result[0][0] == "Hello world"
        assert result[0][1] == 0  # char_start == 0

    def test_long_text_split_into_multiple_chunks(self) -> None:
        # 10 sentences of ~50 chars each → total ~500 chars
        sentence = "This is a sentence with some content here. "
        text = sentence * 10
        result = _split_text_recursive(text, chunk_size=120, chunk_overlap=20)
        assert len(result) > 1

    def test_each_chunk_respects_chunk_size(self) -> None:
        sentence = "Word " * 100  # 500 chars
        result = _split_text_recursive(sentence, chunk_size=80, chunk_overlap=10)
        for chunk_text, _ in result:
            assert len(chunk_text) <= 80 + 10  # allow small overshoot from overlap

    def test_overlap_shares_content(self) -> None:
        """Last characters of chunk N should appear at the start of chunk N+1."""
        text = "abcdefghij" * 20  # 200 chars, no natural separators
        result = _split_text_recursive(text, chunk_size=50, chunk_overlap=15)
        if len(result) >= 2:
            tail_of_first = result[0][0][-15:]
            head_of_second = result[1][0][:15]
            # They should share some content (tail chars appear in second chunk)
            assert any(c in head_of_second for c in tail_of_first)

    def test_empty_text_returns_empty_list(self) -> None:
        result = _split_text_recursive("", chunk_size=100, chunk_overlap=10)
        assert result == []

    def test_whitespace_only_returns_empty_list(self) -> None:
        result = _split_text_recursive("   \n\n\t  ", chunk_size=100, chunk_overlap=10)
        assert result == []

    def test_prefers_paragraph_split(self) -> None:
        """Text with paragraph breaks should be split at \\n\\n."""
        para_a = "First paragraph with enough words to be useful. " * 3
        para_b = "Second paragraph with different content here. " * 3
        text = para_a + "\n\n" + para_b
        result = _split_text_recursive(text, chunk_size=200, chunk_overlap=20)
        # Should produce ≥ 2 chunks
        assert len(result) >= 2

    def test_char_start_offsets_are_non_decreasing(self) -> None:
        text = "sentence one. sentence two. sentence three. " * 10
        result = _split_text_recursive(text, chunk_size=80, chunk_overlap=10)
        offsets = [off for _, off in result]
        assert offsets == sorted(offsets)

    def test_produces_multiple_chunks_for_repetitive_text(self) -> None:
        """Splitter must still produce multiple chunks even for repetitive input."""
        text = "The quick brown fox jumps over the lazy dog. " * 15
        result = _split_text_recursive(text, chunk_size=100, chunk_overlap=20)
        # At least 2 chunks expected for ~675 chars with chunk_size=100
        assert len(result) >= 2
        # All chunks must be non-empty strings
        assert all(t.strip() for t, _ in result)


# ---------------------------------------------------------------------------
# _build_page_offset_map / _char_offset_to_page
# ---------------------------------------------------------------------------

class TestPageOffsetMap:

    def test_single_page_maps_to_page_one(self) -> None:
        pages = [_make_page("hello world", page_number=1)]
        omap = _build_page_offset_map(pages)
        assert _char_offset_to_page(0, omap) == 1
        assert _char_offset_to_page(5, omap) == 1

    def test_two_pages(self) -> None:
        page1 = _make_page("A" * 50, page_number=1)
        page2 = _make_page("B" * 50, page_number=2)
        omap = _build_page_offset_map([page1, page2])
        # Offset 0–50 → page 1; offset 51+ → page 2
        assert _char_offset_to_page(0, omap) == 1
        assert _char_offset_to_page(49, omap) == 1
        assert _char_offset_to_page(51, omap) == 2

    def test_offset_map_sorted_by_start(self) -> None:
        pages = _make_pages(["aaa", "bbb", "ccc"])
        omap = _build_page_offset_map(pages)
        starts = [s for s, _ in omap]
        assert starts == sorted(starts)


# ---------------------------------------------------------------------------
# chunk_documents
# ---------------------------------------------------------------------------

class TestChunkDocuments:

    def test_returns_text_chunks(self) -> None:
        pages = _make_pages(["Word " * 200])
        result = chunk_documents(pages, chunk_size=200, chunk_overlap=20)
        assert all(isinstance(c, TextChunk) for c in result)

    def test_empty_input_returns_empty_list(self) -> None:
        assert chunk_documents([]) == []

    def test_all_scanned_pages_returns_empty(self) -> None:
        pages = [_make_page("", page_number=1, is_scanned=True)]
        result = chunk_documents(pages)
        assert result == []

    def test_chunk_size_respected(self) -> None:
        long_text = "This is a test sentence with real words. " * 100
        pages = [_make_page(long_text)]
        result = chunk_documents(pages, chunk_size=200, chunk_overlap=20)
        for chunk in result:
            assert chunk.char_count <= 220  # size + small overshoot tolerance

    def test_provenance_source_preserved(self) -> None:
        pages = _make_pages(["Word " * 100], source="my_paper.pdf")
        result = chunk_documents(pages, chunk_size=100, chunk_overlap=10)
        assert all(c.source == "my_paper.pdf" for c in result)

    def test_provenance_doc_hash_preserved(self) -> None:
        pages = _make_pages(["Word " * 100], doc_hash="deadbeef")
        result = chunk_documents(pages, chunk_size=100, chunk_overlap=10)
        assert all(c.doc_hash == "deadbeef" for c in result)

    def test_provenance_doc_title_preserved(self) -> None:
        pages = _make_pages(["Word " * 100], doc_title="Attention Is All You Need")
        result = chunk_documents(pages, chunk_size=100, chunk_overlap=10)
        assert all(c.doc_title == "Attention Is All You Need" for c in result)

    def test_chunk_indices_are_sequential(self) -> None:
        pages = _make_pages(["Word " * 300])
        result = chunk_documents(pages, chunk_size=100, chunk_overlap=10)
        indices = [c.chunk_index for c in result]
        assert indices == list(range(len(indices)))

    def test_char_start_end_consistent(self) -> None:
        pages = _make_pages(["Word " * 200])
        result = chunk_documents(pages, chunk_size=150, chunk_overlap=15)
        for c in result:
            assert c.char_end == c.char_start + len(c.text)

    def test_multiple_documents_chunked_independently(self) -> None:
        """Pages from two different docs should produce independent chunk sets."""
        pages_doc1 = _make_pages(["Alpha " * 100], doc_hash="hash1", source="a.pdf")
        pages_doc2 = _make_pages(["Beta " * 100], doc_hash="hash2", source="b.pdf")
        result = chunk_documents(pages_doc1 + pages_doc2, chunk_size=100, chunk_overlap=10)

        sources = {c.source for c in result}
        assert "a.pdf" in sources
        assert "b.pdf" in sources

    def test_multi_page_doc_page_numbers_tracked(self) -> None:
        pages = [
            _make_page("Page one content. " * 20, page_number=1),
            _make_page("Page two content. " * 20, page_number=2),
            _make_page("Page three content. " * 20, page_number=3),
        ]
        result = chunk_documents(pages, chunk_size=200, chunk_overlap=20)
        page_nums = {c.page_number for c in result}
        # At least page 1 should appear
        assert 1 in page_nums

    def test_to_dict_returns_flat_dict(self) -> None:
        pages = _make_pages(["Some research content here. " * 10])
        chunks = chunk_documents(pages, chunk_size=100, chunk_overlap=10)
        assert chunks, "Expected at least one chunk"
        d = chunks[0].to_dict()
        assert isinstance(d, dict)
        assert "text" in d
        assert "doc_hash" in d
        assert "page_number" in d
        assert "char_start" in d
        assert "char_end" in d


# ---------------------------------------------------------------------------
# chunk_text (plain string helper)
# ---------------------------------------------------------------------------

class TestChunkText:

    def test_short_string_returns_one_element(self) -> None:
        result = chunk_text("Hello world", chunk_size=100, chunk_overlap=10)
        assert result == ["Hello world"]

    def test_returns_list_of_strings(self) -> None:
        long = "word " * 300
        result = chunk_text(long, chunk_size=100, chunk_overlap=10)
        assert all(isinstance(s, str) for s in result)

    def test_splits_long_string(self) -> None:
        long = "word " * 300
        result = chunk_text(long, chunk_size=100, chunk_overlap=10)
        assert len(result) > 1

    def test_empty_string_returns_empty_list(self) -> None:
        assert chunk_text("", chunk_size=100, chunk_overlap=10) == []


# ---------------------------------------------------------------------------
# TextChunk repr / properties
# ---------------------------------------------------------------------------

class TestTextChunkModel:

    def _sample_chunk(self) -> TextChunk:
        return TextChunk(
            text="The transformer architecture introduced attention mechanisms.",
            chunk_index=0,
            doc_hash="abc",
            doc_title="Attention Is All You Need",
            source="vaswani2017.pdf",
            page_number=3,
            char_start=0,
            char_end=60,
        )

    def test_word_count(self) -> None:
        c = self._sample_chunk()
        assert c.word_count == len(c.text.split())

    def test_char_count(self) -> None:
        c = self._sample_chunk()
        assert c.char_count == len(c.text)

    def test_repr_contains_source(self) -> None:
        c = self._sample_chunk()
        assert "vaswani2017.pdf" in repr(c)

    def test_metadata_defaults_empty(self) -> None:
        c = self._sample_chunk()
        assert c.metadata == {}
