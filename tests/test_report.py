"""
Module 8 tests — Report Generator  (src/agents/report.py)

Pure Python — no IBM API calls.  Tests run 100% offline.
PDF generation is tested with a real fpdf2 call (no mock needed).

Run with:
    cd SciPilot
    python -m pytest tests/test_report.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.agents.citation import CitationAgent, CitationStyle
from src.agents.report import (
    ReportAgent,
    ReportResult,
    build_markdown_report,
    build_pdf_report,
)
from src.agents.synthesis import SynthesisResult
from src.rag.chunk import TextChunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(idx: int = 0, doc_hash: str = "h1") -> TextChunk:
    return TextChunk(
        text="Transformer architecture uses self-attention mechanisms.",
        chunk_index=idx,
        doc_hash=doc_hash,
        doc_title="Attention Is All You Need",
        doc_authors="Vaswani, Ashish; Shazeer, Noam",
        doc_subject="arXiv",
        source="vaswani2017.pdf",
        page_number=idx + 1,
        char_start=0,
        char_end=55,
        metadata={"creation_date": "D:20170612"},
    )


def _make_synthesis(n_chunks: int = 2) -> SynthesisResult:
    chunks = [_make_chunk(i, f"h{i}") for i in range(n_chunks)]
    return SynthesisResult(
        answer="The transformer uses multi-head attention [1] and feed-forward layers [2].",
        cited_indices=[1, 2],
        question="What is the transformer architecture?",
        context_chunks=chunks,
        model_id="ibm/granite-13b-instruct-v2",
        input_tokens=120,
        output_tokens=45,
        latency_s=1.23,
    )


def _make_citation(synthesis: SynthesisResult, style: CitationStyle = CitationStyle.APA) -> object:
    agent = CitationAgent(style)
    return agent.generate(synthesis.cited_chunks, original_positions=synthesis.cited_indices)


# ---------------------------------------------------------------------------
# build_markdown_report
# ---------------------------------------------------------------------------

class TestBuildMarkdownReport:

    def test_returns_string(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_title(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "SciPilot Research Report" in result

    def test_contains_question(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "transformer architecture" in result

    def test_contains_answer(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "multi-head attention" in result

    def test_contains_answer_section_header(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "## Answer" in result

    def test_contains_sources_section(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "## Sources Used" in result

    def test_contains_references_section(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "## References" in result

    def test_contains_metadata_section(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "## Report Metadata" in result

    def test_contains_model_id(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "granite" in result.lower()

    def test_contains_session_id_when_provided(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit, session_id="sess-abc-123")
        assert "sess-abc-123" in result

    def test_source_filename_in_table(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = build_markdown_report(syn, cit)
        assert "vaswani2017.pdf" in result

    def test_citation_style_shown(self) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn, CitationStyle.IEEE)
        result = build_markdown_report(syn, cit)
        assert "IEEE" in result

    def test_no_context_chunks_graceful(self) -> None:
        syn = SynthesisResult(
            answer="No context.",
            cited_indices=[],
            question="Q?",
            context_chunks=[],
        )
        from src.agents.citation import CitationResult
        cit = CitationResult(citations=[], style=CitationStyle.APA)
        result = build_markdown_report(syn, cit)
        assert "SciPilot Research Report" in result


# ---------------------------------------------------------------------------
# build_pdf_report
# ---------------------------------------------------------------------------

class TestBuildPdfReport:

    def test_creates_pdf_file(self, tmp_path: Path) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        md = build_markdown_report(syn, cit)
        pdf_path = tmp_path / "report.pdf"
        result = build_pdf_report(md, pdf_path)
        assert result == pdf_path
        assert pdf_path.exists()

    def test_pdf_has_nonzero_size(self, tmp_path: Path) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        md = build_markdown_report(syn, cit)
        pdf_path = tmp_path / "report.pdf"
        build_pdf_report(md, pdf_path)
        assert pdf_path.stat().st_size > 1024  # at least 1 KB

    def test_pdf_starts_with_pdf_magic(self, tmp_path: Path) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        md = build_markdown_report(syn, cit)
        pdf_path = tmp_path / "report.pdf"
        build_pdf_report(md, pdf_path)
        magic = pdf_path.read_bytes()[:4]
        assert magic == b"%PDF"

    def test_returns_path(self, tmp_path: Path) -> None:
        syn = _make_synthesis()
        cit = _make_citation(syn)
        md = build_markdown_report(syn, cit)
        pdf_path = tmp_path / "out.pdf"
        returned = build_pdf_report(md, pdf_path)
        assert returned == pdf_path


# ---------------------------------------------------------------------------
# ReportAgent.generate
# ---------------------------------------------------------------------------

class TestReportAgentGenerate:

    def test_returns_report_result(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=True, save_pdf=True)
        assert isinstance(result, ReportResult)

    def test_md_content_populated(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert "SciPilot" in result.md_content

    def test_saves_markdown_file(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=True, save_pdf=False)
        assert result.has_markdown
        assert result.md_path.suffix == ".md"

    def test_saves_pdf_file(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=True)
        assert result.has_pdf
        assert result.pdf_path.suffix == ".pdf"

    def test_no_files_when_both_false(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert result.md_path is None
        assert result.pdf_path is None

    def test_question_stored(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert "transformer" in result.question.lower()

    def test_word_count_positive(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert result.word_count > 0

    def test_generated_at_is_datetime_string(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        # Format: YYYY-MM-DD HH:MM:SS
        import re
        assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result.generated_at)

    def test_metadata_contains_citation_style(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert "citation_style" in result.metadata

    def test_session_id_passed_through(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, session_id="xyz-999",
                                save_markdown=False, save_pdf=False)
        assert result.metadata["session_id"] == "xyz-999"

    def test_markdown_filename_has_timestamp(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=True, save_pdf=False)
        assert "scipilot_" in result.md_path.name

    def test_pdf_filename_matches_md_stem(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=True, save_pdf=True)
        assert result.md_path.stem == result.pdf_path.stem


# ---------------------------------------------------------------------------
# ReportAgent.generate_markdown_only
# ---------------------------------------------------------------------------

class TestGenerateMarkdownOnly:

    def test_returns_string(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate_markdown_only(syn, cit)
        assert isinstance(result, str)
        assert "SciPilot" in result

    def test_does_not_create_files(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        agent.generate_markdown_only(syn, cit)
        assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------------------
# ReportResult properties
# ---------------------------------------------------------------------------

class TestReportResult:

    def test_repr_contains_question(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert "transformer" in repr(result).lower()

    def test_repr_contains_word_count(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert "words=" in repr(result)

    def test_has_markdown_false_when_not_saved(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert result.has_markdown is False

    def test_has_pdf_false_when_not_saved(self, tmp_path: Path) -> None:
        agent = ReportAgent(reports_dir=tmp_path)
        syn = _make_synthesis()
        cit = _make_citation(syn)
        result = agent.generate(syn, cit, save_markdown=False, save_pdf=False)
        assert result.has_pdf is False
