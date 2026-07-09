"""
Module 7 tests — Citation Generator  (src/agents/citation.py)

Pure-Python module — no mocking needed.  Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_citation.py -v
"""

from __future__ import annotations

import pytest

from src.agents.citation import (
    Citation,
    CitationAgent,
    CitationResult,
    CitationStyle,
    _extract_year,
    _format_apa,
    _format_ieee,
    _format_single_author_apa,
    _format_single_author_ieee,
    _parse_authors_apa,
    _parse_authors_ieee,
    _source_name_from_chunk,
)
from src.rag.chunk import TextChunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(
    doc_title: str = "Attention Is All You Need",
    doc_authors: str = "Vaswani, Ashish; Shazeer, Noam",
    doc_subject: str = "arXiv",
    source: str = "vaswani2017.pdf",
    doc_hash: str = "hash_a",
    page_number: int = 3,
    creation_date: str = "D:20170612",
) -> TextChunk:
    return TextChunk(
        text="The transformer uses multi-head attention.",
        chunk_index=0,
        doc_hash=doc_hash,
        doc_title=doc_title,
        doc_authors=doc_authors,
        doc_subject=doc_subject,
        source=source,
        page_number=page_number,
        char_start=0,
        char_end=42,
        metadata={"creation_date": creation_date},
    )


# ---------------------------------------------------------------------------
# _extract_year
# ---------------------------------------------------------------------------

class TestExtractYear:

    def test_finds_year_in_string(self) -> None:
        assert _extract_year("Published in 2017.") == "2017"

    def test_finds_year_in_date_string(self) -> None:
        assert _extract_year("D:20170612120000") == "2017"

    def test_returns_nd_when_no_year(self) -> None:
        assert _extract_year("no year here") == "n.d."

    def test_returns_first_year_found(self) -> None:
        assert _extract_year("2015 and 2017") == "2015"

    def test_ignores_three_digit_numbers(self) -> None:
        assert _extract_year("page 123") == "n.d."


# ---------------------------------------------------------------------------
# Author formatting — APA
# ---------------------------------------------------------------------------

class TestParseAuthorsApa:

    def test_single_author_last_first(self) -> None:
        result = _parse_authors_apa("Vaswani, Ashish")
        assert result.startswith("Vaswani")
        assert "A." in result

    def test_single_author_first_last(self) -> None:
        result = _parse_authors_apa("John Smith")
        assert "Smith" in result
        assert "J." in result

    def test_two_authors_joined_with_ampersand(self) -> None:
        result = _parse_authors_apa("John Smith and Jane Doe")
        assert "&" in result

    def test_three_authors_oxford_comma(self) -> None:
        result = _parse_authors_apa("Alice A; Bob B; Carol C")
        assert result.count(",") >= 2

    def test_empty_string_returns_unknown(self) -> None:
        assert _parse_authors_apa("") == "Unknown Author"

    def test_semicolon_delimiter(self) -> None:
        result = _parse_authors_apa("Smith, J.; Doe, J.")
        assert "&" in result


class TestFormatSingleAuthorApa:

    def test_last_first_form(self) -> None:
        result = _format_single_author_apa("Vaswani, Ashish")
        assert result == "Vaswani, A."

    def test_first_last_form(self) -> None:
        result = _format_single_author_apa("Ashish Vaswani")
        assert result == "Vaswani, A."

    def test_single_token(self) -> None:
        result = _format_single_author_apa("Aristotle")
        assert result == "Aristotle"

    def test_middle_name_abbreviated(self) -> None:
        result = _format_single_author_apa("John Michael Smith")
        assert "Smith" in result
        assert "J." in result
        assert "M." in result


# ---------------------------------------------------------------------------
# Author formatting — IEEE
# ---------------------------------------------------------------------------

class TestParseAuthorsIeee:

    def test_single_author(self) -> None:
        result = _parse_authors_ieee("Ashish Vaswani")
        assert "Vaswani" in result
        assert "A." in result

    def test_two_authors_joined_with_and(self) -> None:
        result = _parse_authors_ieee("John Smith and Jane Doe")
        assert " and " in result

    def test_empty_returns_unknown(self) -> None:
        assert _parse_authors_ieee("") == "Unknown Author"


class TestFormatSingleAuthorIeee:

    def test_first_last_form(self) -> None:
        result = _format_single_author_ieee("Ashish Vaswani")
        assert result == "A. Vaswani"

    def test_last_first_form(self) -> None:
        result = _format_single_author_ieee("Vaswani, Ashish")
        assert "Vaswani" in result
        assert "A." in result

    def test_single_token(self) -> None:
        result = _format_single_author_ieee("Aristotle")
        assert result == "Aristotle"


# ---------------------------------------------------------------------------
# _source_name_from_chunk
# ---------------------------------------------------------------------------

class TestSourceNameFromChunk:

    def test_prefers_doc_subject(self) -> None:
        chunk = _make_chunk(doc_subject="NeurIPS 2017")
        assert _source_name_from_chunk(chunk) == "NeurIPS 2017"

    def test_falls_back_to_filename_stem(self) -> None:
        chunk = _make_chunk(doc_subject="")
        name = _source_name_from_chunk(chunk)
        assert "pdf" not in name.lower()
        assert "vaswani2017" in name.lower() or "vaswani" in name.lower()

    def test_underscores_replaced_with_spaces(self) -> None:
        chunk = _make_chunk(doc_subject="", source="my_paper_2024.pdf")
        name = _source_name_from_chunk(chunk)
        assert "_" not in name


# ---------------------------------------------------------------------------
# _format_apa / _format_ieee
# ---------------------------------------------------------------------------

class TestFormatApa:

    def test_contains_author(self) -> None:
        result = _format_apa(1, "Title", "Smith, J.", "2017", "Journal")
        assert "Smith" in result

    def test_contains_year_in_parens(self) -> None:
        result = _format_apa(1, "Title", "Smith, J.", "2017", "Journal")
        assert "(2017)" in result

    def test_title_in_italics_markdown(self) -> None:
        result = _format_apa(1, "My Title", "Smith, J.", "2017", "Journal")
        assert "*My Title*" in result

    def test_source_in_italics_markdown(self) -> None:
        result = _format_apa(1, "Title", "Smith, J.", "2017", "NeurIPS")
        assert "*NeurIPS*" in result

    def test_ends_with_period(self) -> None:
        result = _format_apa(1, "T", "A.", "2017", "J")
        assert result.endswith(".")


class TestFormatIeee:

    def test_starts_with_bracket_index(self) -> None:
        result = _format_ieee(1, "Title", "A. Smith", "2017", "Journal")
        assert result.startswith("[1]")

    def test_title_in_quotes(self) -> None:
        result = _format_ieee(1, "My Title", "A. Smith", "2017", "Journal")
        assert '"My Title,"' in result

    def test_source_in_italics(self) -> None:
        result = _format_ieee(1, "T", "A.", "2017", "NeurIPS")
        assert "*NeurIPS*" in result

    def test_ends_with_period(self) -> None:
        result = _format_ieee(1, "T", "A.", "2017", "J")
        assert result.endswith(".")

    def test_index_increments(self) -> None:
        r1 = _format_ieee(1, "T", "A.", "2017", "J")
        r2 = _format_ieee(2, "T", "A.", "2017", "J")
        assert r1.startswith("[1]")
        assert r2.startswith("[2]")


# ---------------------------------------------------------------------------
# CitationAgent.generate
# ---------------------------------------------------------------------------

class TestCitationAgentGenerate:

    def test_returns_citation_result(self) -> None:
        agent = CitationAgent(CitationStyle.APA)
        result = agent.generate([_make_chunk()])
        assert isinstance(result, CitationResult)

    def test_empty_chunks_returns_empty_result(self) -> None:
        agent = CitationAgent()
        result = agent.generate([])
        assert result.is_empty
        assert result.references_block == ""

    def test_one_chunk_one_citation(self) -> None:
        agent = CitationAgent()
        result = agent.generate([_make_chunk()])
        assert len(result.citations) == 1

    def test_deduplicates_same_doc(self) -> None:
        """Two chunks from the same document → one citation entry."""
        chunk_a = _make_chunk(doc_hash="same_hash", page_number=1)
        chunk_b = _make_chunk(doc_hash="same_hash", page_number=5)
        agent = CitationAgent()
        result = agent.generate([chunk_a, chunk_b])
        assert len(result.citations) == 1

    def test_different_docs_two_citations(self) -> None:
        chunk_a = _make_chunk(doc_hash="hash_a")
        chunk_b = _make_chunk(doc_title="BERT", doc_hash="hash_b", source="bert.pdf")
        agent = CitationAgent()
        result = agent.generate([chunk_a, chunk_b])
        assert len(result.citations) == 2

    def test_apa_style_applied(self) -> None:
        agent = CitationAgent(CitationStyle.APA)
        result = agent.generate([_make_chunk()])
        # APA format has year in parentheses
        assert "(20" in result.citations[0].formatted or "(n.d.)" in result.citations[0].formatted

    def test_ieee_style_applied(self) -> None:
        agent = CitationAgent(CitationStyle.IEEE)
        result = agent.generate([_make_chunk()])
        assert result.citations[0].formatted.startswith("[1]")

    def test_references_block_contains_header(self) -> None:
        agent = CitationAgent()
        result = agent.generate([_make_chunk()])
        assert "## References" in result.references_block

    def test_references_block_contains_citation(self) -> None:
        agent = CitationAgent()
        result = agent.generate([_make_chunk()])
        assert "Vaswani" in result.references_block or "Attention" in result.references_block

    def test_inline_map_populated(self) -> None:
        agent = CitationAgent()
        chunk = _make_chunk(doc_hash="h1")
        result = agent.generate([chunk], original_positions=[1])
        assert 1 in result.inline_map
        assert result.inline_map[1] == 1

    def test_inline_map_dedup_same_doc(self) -> None:
        """Two original positions mapping to the same document → same cite index."""
        chunk_a = _make_chunk(doc_hash="same")
        chunk_b = _make_chunk(doc_hash="same")
        agent = CitationAgent()
        result = agent.generate([chunk_a, chunk_b], original_positions=[1, 3])
        assert result.inline_map[1] == result.inline_map[3]

    def test_citation_year_extracted(self) -> None:
        chunk = _make_chunk(creation_date="D:20170612")
        agent = CitationAgent()
        result = agent.generate([chunk])
        assert result.citations[0].year == "2017"

    def test_citation_missing_author_fallback(self) -> None:
        chunk = _make_chunk(doc_authors="")
        agent = CitationAgent()
        result = agent.generate([chunk])
        assert "Unknown Author" in result.citations[0].authors

    def test_generate_from_synthesis(self) -> None:
        """generate_from_synthesis should call generate with cited_chunks."""
        from src.agents.synthesis import SynthesisResult
        chunks = [_make_chunk(doc_hash="h1"), _make_chunk(doc_hash="h2")]
        synth = SynthesisResult(
            answer="Answer [1] and [2].",
            cited_indices=[1, 2],
            question="Q?",
            context_chunks=chunks,
        )
        agent = CitationAgent(CitationStyle.IEEE)
        result = agent.generate_from_synthesis(synth)
        assert len(result.citations) == 2
        assert result.citations[0].formatted.startswith("[1]")


# ---------------------------------------------------------------------------
# CitationResult helpers
# ---------------------------------------------------------------------------

class TestCitationResult:

    def test_is_empty_false(self) -> None:
        agent = CitationAgent()
        result = agent.generate([_make_chunk()])
        assert not result.is_empty

    def test_repr_contains_count(self) -> None:
        agent = CitationAgent()
        result = agent.generate([_make_chunk()])
        assert "count=1" in repr(result)

    def test_repr_contains_style(self) -> None:
        agent = CitationAgent(CitationStyle.IEEE)
        result = agent.generate([_make_chunk()])
        assert "IEEE" in repr(result)
