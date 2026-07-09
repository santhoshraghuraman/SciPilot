"""
Module 6 tests — IBM Granite Synthesis Agent  (src/agents/synthesis.py)

All IBM API calls are bypassed using the ``_mock_response`` escape hatch
or by patching ``_call_granite``.  Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_synthesis.py -v
"""

from __future__ import annotations

from typing import List
from unittest.mock import MagicMock, patch

import pytest

from src.agents.retriever import RetrievalResult
from src.agents.synthesis import (
    SynthesisAgent,
    SynthesisResult,
    _clean_answer,
    _extract_cited_indices,
    build_prompt,
    reset_llm_client,
)
from src.rag.chunk import TextChunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(text: str = "passage text", idx: int = 0) -> TextChunk:
    return TextChunk(
        text=text,
        chunk_index=idx,
        doc_hash="hash",
        doc_title="Test Paper",
        source="paper.pdf",
        page_number=idx + 1,
        char_start=0,
        char_end=len(text),
    )


def _make_retrieval(n: int = 3, empty: bool = False) -> RetrievalResult:
    if empty:
        return RetrievalResult(chunks=[], scores=[], query="test query")
    chunks = [_make_chunk(f"The transformer architecture uses attention. Passage {i}.", i)
              for i in range(n)]
    scores = [0.9 - i * 0.05 for i in range(n)]
    return RetrievalResult(chunks=chunks, scores=scores, query="test query")


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:

    def test_contains_system_marker(self) -> None:
        retrieval = _make_retrieval(2)
        prompt = build_prompt("What is attention?", retrieval)
        assert "<|system|>" in prompt

    def test_contains_user_marker(self) -> None:
        retrieval = _make_retrieval(2)
        prompt = build_prompt("What is attention?", retrieval)
        assert "<|user|>" in prompt

    def test_contains_assistant_marker(self) -> None:
        retrieval = _make_retrieval(2)
        prompt = build_prompt("What is attention?", retrieval)
        assert "<|assistant|>" in prompt

    def test_contains_question(self) -> None:
        retrieval = _make_retrieval(2)
        prompt = build_prompt("What is multi-head attention?", retrieval)
        assert "multi-head attention" in prompt

    def test_contains_numbered_passages(self) -> None:
        retrieval = _make_retrieval(3)
        prompt = build_prompt("What is attention?", retrieval)
        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "[3]" in prompt

    def test_contains_source_metadata(self) -> None:
        retrieval = _make_retrieval(1)
        prompt = build_prompt("Q?", retrieval)
        assert "paper.pdf" in prompt

    def test_contains_page_number(self) -> None:
        retrieval = _make_retrieval(1)
        prompt = build_prompt("Q?", retrieval)
        assert "Page:" in prompt

    def test_empty_retrieval_shows_no_context(self) -> None:
        retrieval = _make_retrieval(empty=True)
        prompt = build_prompt("Q?", retrieval)
        assert "No context available" in prompt

    def test_passage_text_included(self) -> None:
        retrieval = _make_retrieval(1)
        prompt = build_prompt("Q?", retrieval)
        assert "transformer architecture" in prompt


# ---------------------------------------------------------------------------
# _extract_cited_indices
# ---------------------------------------------------------------------------

class TestExtractCitedIndices:

    def test_single_citation(self) -> None:
        assert _extract_cited_indices("See [1] for details.") == [1]

    def test_multiple_citations(self) -> None:
        result = _extract_cited_indices("As shown in [1] and [3], the method works [2].")
        assert result == [1, 3, 2]

    def test_deduplicates(self) -> None:
        result = _extract_cited_indices("[1] is mentioned again in [1].")
        assert result == [1]

    def test_no_citations_returns_empty(self) -> None:
        assert _extract_cited_indices("No citations here.") == []

    def test_two_digit_citation(self) -> None:
        assert _extract_cited_indices("See [12] for details.") == [12]

    def test_order_preserved(self) -> None:
        result = _extract_cited_indices("[3] then [1] then [2].")
        assert result == [3, 1, 2]


# ---------------------------------------------------------------------------
# _clean_answer
# ---------------------------------------------------------------------------

class TestCleanAnswer:

    def test_strips_role_tokens(self) -> None:
        raw = "<|assistant|>\nThe answer is here."
        assert "<|" not in _clean_answer(raw)

    def test_strips_answer_header(self) -> None:
        raw = "### Answer\nThe actual answer."
        cleaned = _clean_answer(raw)
        assert cleaned.startswith("The actual answer")

    def test_strips_whitespace(self) -> None:
        assert _clean_answer("  hello  ") == "hello"

    def test_preserves_content(self) -> None:
        content = "Attention mechanism uses query, key, and value matrices [1]."
        assert content in _clean_answer(content)


# ---------------------------------------------------------------------------
# SynthesisAgent.synthesise
# ---------------------------------------------------------------------------

class TestSynthesisAgentSynthesise:

    def setup_method(self) -> None:
        reset_llm_client()

    def test_returns_synthesis_result(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        result = agent.synthesise(
            "What is attention?",
            retrieval,
            _mock_response="The attention mechanism [1] scales dot products.",
        )
        assert isinstance(result, SynthesisResult)

    def test_answer_text_populated(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        result = agent.synthesise(
            "What is attention?",
            retrieval,
            _mock_response="The attention mechanism [1] scales dot products.",
        )
        assert len(result.answer) > 0

    def test_cited_indices_extracted(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(3)
        result = agent.synthesise(
            "What is attention?",
            retrieval,
            _mock_response="As shown in [1] and [2], attention is key.",
        )
        assert result.cited_indices == [1, 2]

    def test_question_stored_in_result(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        result = agent.synthesise(
            "What is multi-head attention?",
            retrieval,
            _mock_response="Answer here [1].",
        )
        assert "multi-head attention" in result.question

    def test_context_chunks_stored(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        result = agent.synthesise("Q?", retrieval, _mock_response="Answer [1].")
        assert len(result.context_chunks) == 2

    def test_prompt_stored(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(1)
        result = agent.synthesise("Q?", retrieval, _mock_response="A.")
        assert "<|system|>" in result.prompt

    def test_model_id_stored(self) -> None:
        agent = SynthesisAgent(model_id="ibm/test-model")
        retrieval = _make_retrieval(1)
        result = agent.synthesise("Q?", retrieval, _mock_response="A.")
        assert result.model_id == "ibm/test-model"

    def test_empty_retrieval_returns_no_context_message(self) -> None:
        agent = SynthesisAgent()
        result = agent.synthesise("Q?", _make_retrieval(empty=True))
        assert "do not contain sufficient" in result.answer.lower()
        assert result.cited_indices == []

    def test_raises_on_blank_question(self) -> None:
        agent = SynthesisAgent()
        with pytest.raises(ValueError, match="blank"):
            agent.synthesise("   ", _make_retrieval(1))

    def test_is_grounded_true_when_cited(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        result = agent.synthesise("Q?", retrieval, _mock_response="Answer [1].")
        assert result.is_grounded is True

    def test_is_grounded_false_when_no_citations(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        result = agent.synthesise("Q?", retrieval, _mock_response="No citations here.")
        assert result.is_grounded is False

    def test_latency_recorded(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(1)
        result = agent.synthesise("Q?", retrieval, _mock_response="A [1].")
        assert result.latency_s >= 0.0


# ---------------------------------------------------------------------------
# SynthesisAgent.synthesise_multi
# ---------------------------------------------------------------------------

class TestSynthesiseMulti:

    def test_returns_one_result_per_question(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)

        # Patch synthesise to use mock response
        from unittest.mock import patch as _patch
        original_synthesise = agent.synthesise

        def mock_synthesise(question, retrieval, _mock_response=None):
            return original_synthesise(
                question, retrieval,
                _mock_response=f"Answer for: {question} [1]."
            )

        agent.synthesise = mock_synthesise

        questions = ["What is Q1?", "What is Q2?", "What is Q3?"]
        results = agent.synthesise_multi(questions, retrieval)
        assert len(results) == 3

    def test_each_result_has_correct_question(self) -> None:
        agent = SynthesisAgent()
        retrieval = _make_retrieval(2)
        original_synthesise = agent.synthesise

        def mock_synthesise(question, retrieval, _mock_response=None):
            return original_synthesise(question, retrieval, _mock_response="A [1].")

        agent.synthesise = mock_synthesise
        questions = ["Alpha?", "Beta?"]
        results = agent.synthesise_multi(questions, retrieval)

        assert results[0].question == "Alpha?"
        assert results[1].question == "Beta?"


# ---------------------------------------------------------------------------
# SynthesisResult properties
# ---------------------------------------------------------------------------

class TestSynthesisResultProperties:

    def _make_result(self, cited: List[int] = None) -> SynthesisResult:
        chunks = [_make_chunk(f"chunk {i}", i) for i in range(3)]
        return SynthesisResult(
            answer="The answer cites [1] and [2].",
            cited_indices=cited if cited is not None else [1, 2],
            question="test question",
            context_chunks=chunks,
            model_id="ibm/granite-test",
            latency_s=0.5,
        )

    def test_cited_chunks_returns_referenced_chunks(self) -> None:
        result = self._make_result(cited=[1, 3])
        cited = result.cited_chunks
        assert len(cited) == 2
        assert cited[0].chunk_index == 0  # passage [1] → chunk index 0
        assert cited[1].chunk_index == 2  # passage [3] → chunk index 2

    def test_cited_chunks_empty_when_no_citations(self) -> None:
        result = self._make_result(cited=[])
        assert result.cited_chunks == []

    def test_repr_contains_word_count(self) -> None:
        result = self._make_result()
        assert "words=" in repr(result)

    def test_repr_contains_cited(self) -> None:
        result = self._make_result()
        assert "cited=" in repr(result)

    def test_repr_contains_latency(self) -> None:
        result = self._make_result()
        assert "latency=" in repr(result)
