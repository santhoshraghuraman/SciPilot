"""
Module 10 tests — Verification Agent  (src/agents/verification.py)

Pure Python — no IBM API calls.  Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_verification.py -v
"""

from __future__ import annotations

from typing import List

import pytest

from src.agents.synthesis import SynthesisResult
from src.agents.verification import (
    WEIGHT_ANSWER_QUALITY,
    WEIGHT_CITATION_COVERAGE,
    WEIGHT_GROUNDING_RATIO,
    WEIGHT_SOURCE_DIVERSITY,
    CheckResult,
    Verdict,
    VerificationAgent,
    VerificationResult,
    check_answer_quality,
    check_citation_coverage,
    check_grounding_ratio,
    check_source_diversity,
    score_to_verdict,
)
from src.rag.chunk import TextChunk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(
    text: str = "The transformer architecture uses multi-head attention mechanisms.",
    doc_hash: str = "hash_a",
    page: int = 1,
) -> TextChunk:
    return TextChunk(
        text=text,
        chunk_index=0,
        doc_hash=doc_hash,
        doc_title="Test Paper",
        source="paper.pdf",
        page_number=page,
        char_start=0,
        char_end=len(text),
    )


def _make_synthesis(
    answer: str = "The transformer uses attention [1] and positional encoding [2].",
    chunks: List[TextChunk] = None,
    cited: List[int] = None,
) -> SynthesisResult:
    if chunks is None:
        chunks = [
            _make_chunk("Attention mechanism uses queries and keys.", "h1"),
            _make_chunk("Positional encoding encodes sequence order.", "h2"),
        ]
    return SynthesisResult(
        answer=answer,
        cited_indices=cited or [1, 2],
        question="What is the transformer?",
        context_chunks=chunks,
        model_id="ibm/granite-test",
    )


# ---------------------------------------------------------------------------
# score_to_verdict
# ---------------------------------------------------------------------------

class TestScoreToVerdict:

    def test_high_at_0_7(self) -> None:
        assert score_to_verdict(0.70) == Verdict.HIGH

    def test_high_above_0_7(self) -> None:
        assert score_to_verdict(0.95) == Verdict.HIGH

    def test_medium_at_0_4(self) -> None:
        assert score_to_verdict(0.40) == Verdict.MEDIUM

    def test_medium_between_0_4_and_0_7(self) -> None:
        assert score_to_verdict(0.55) == Verdict.MEDIUM

    def test_low_below_0_4(self) -> None:
        assert score_to_verdict(0.39) == Verdict.LOW

    def test_low_at_zero(self) -> None:
        assert score_to_verdict(0.0) == Verdict.LOW


# ---------------------------------------------------------------------------
# check_citation_coverage
# ---------------------------------------------------------------------------

class TestCheckCitationCoverage:

    def test_all_valid_citations_score_1(self) -> None:
        r = check_citation_coverage("See [1] and [2].", num_context_chunks=2)
        assert r.score == 1.0

    def test_out_of_range_citation_lowers_score(self) -> None:
        r = check_citation_coverage("See [1] and [5].", num_context_chunks=2)
        assert r.score < 1.0

    def test_no_citations_with_context_scores_0(self) -> None:
        r = check_citation_coverage("No citations here.", num_context_chunks=3)
        assert r.score == 0.0

    def test_no_citations_no_context_scores_1(self) -> None:
        r = check_citation_coverage("Answer with no context.", num_context_chunks=0)
        assert r.score == 1.0

    def test_all_invalid_scores_0(self) -> None:
        r = check_citation_coverage("[99] and [100].", num_context_chunks=2)
        assert r.score == 0.0

    def test_partial_valid_half_score(self) -> None:
        # [1] valid, [3] invalid out of 2 chunks → 1/2 = 0.5
        r = check_citation_coverage("[1] and [3].", num_context_chunks=2)
        assert r.score == pytest.approx(0.5)

    def test_check_name(self) -> None:
        r = check_citation_coverage("text [1]", num_context_chunks=1)
        assert r.name == "citation_coverage"

    def test_check_weight(self) -> None:
        r = check_citation_coverage("text [1]", num_context_chunks=1)
        assert r.weight == WEIGHT_CITATION_COVERAGE

    def test_weighted_score_computed(self) -> None:
        r = check_citation_coverage("text [1]", num_context_chunks=1)
        assert r.weighted_score == pytest.approx(r.score * r.weight)


# ---------------------------------------------------------------------------
# check_grounding_ratio
# ---------------------------------------------------------------------------

class TestCheckGroundingRatio:

    def test_well_grounded_answer_scores_high(self) -> None:
        chunk = _make_chunk(
            "Transformer architecture uses attention mechanism with query key value."
        )
        answer = (
            "The transformer architecture uses attention mechanism. "
            "The query key value structure enables parallelism."
        )
        r = check_grounding_ratio(answer, [chunk])
        assert r.score > 0.0

    def test_ungrounded_answer_scores_low(self) -> None:
        chunk = _make_chunk("Completely unrelated fruit salad recipe.")
        answer = "Quantum entanglement affects neutrino oscillation frequency."
        r = check_grounding_ratio(answer, [chunk])
        assert r.score < 1.0

    def test_no_context_returns_neutral(self) -> None:
        r = check_grounding_ratio("Some answer.", [])
        assert r.score == 0.5

    def test_check_name(self) -> None:
        r = check_grounding_ratio("answer text.", [_make_chunk()])
        assert r.name == "grounding_ratio"

    def test_check_weight(self) -> None:
        r = check_grounding_ratio("answer text.", [_make_chunk()])
        assert r.weight == WEIGHT_GROUNDING_RATIO

    def test_score_between_0_and_1(self) -> None:
        chunk = _make_chunk("attention mechanism transformer architecture deep learning.")
        answer = "Deep learning with attention mechanism in transformer."
        r = check_grounding_ratio(answer, [chunk])
        assert 0.0 <= r.score <= 1.0


# ---------------------------------------------------------------------------
# check_answer_quality
# ---------------------------------------------------------------------------

class TestCheckAnswerQuality:

    def test_good_length_scores_1(self) -> None:
        answer = " ".join(["word"] * 50)  # 50 words — within [20, 600]
        r = check_answer_quality(answer)
        assert r.score == 1.0

    def test_too_short_scores_below_1(self) -> None:
        answer = "Too short."  # 2 words
        r = check_answer_quality(answer)
        assert r.score < 1.0

    def test_too_long_scores_below_1(self) -> None:
        answer = " ".join(["word"] * 700)  # 700 words — above max 600
        r = check_answer_quality(answer)
        assert r.score < 1.0

    def test_empty_answer_scores_zero(self) -> None:
        r = check_answer_quality("")
        assert r.score == 0.0

    def test_check_name(self) -> None:
        r = check_answer_quality("Good length answer with many words here now.")
        assert r.name == "answer_quality"

    def test_check_weight(self) -> None:
        r = check_answer_quality("word " * 30)
        assert r.weight == WEIGHT_ANSWER_QUALITY

    def test_score_between_0_and_1(self) -> None:
        r = check_answer_quality("word " * 5)
        assert 0.0 <= r.score <= 1.0


# ---------------------------------------------------------------------------
# check_source_diversity
# ---------------------------------------------------------------------------

class TestCheckSourceDiversity:

    def test_single_source_scores_low(self) -> None:
        chunks = [_make_chunk(doc_hash="same"), _make_chunk(doc_hash="same")]
        r = check_source_diversity(chunks)
        assert r.score < 0.5

    def test_two_sources_scores_medium(self) -> None:
        chunks = [_make_chunk(doc_hash="h1"), _make_chunk(doc_hash="h2")]
        r = check_source_diversity(chunks)
        assert r.score == pytest.approx(2 / 3)

    def test_three_or_more_sources_scores_1(self) -> None:
        chunks = [
            _make_chunk(doc_hash="h1"),
            _make_chunk(doc_hash="h2"),
            _make_chunk(doc_hash="h3"),
        ]
        r = check_source_diversity(chunks)
        assert r.score == 1.0

    def test_no_chunks_scores_zero(self) -> None:
        r = check_source_diversity([])
        assert r.score == 0.0

    def test_check_name(self) -> None:
        r = check_source_diversity([_make_chunk()])
        assert r.name == "source_diversity"

    def test_check_weight(self) -> None:
        r = check_source_diversity([_make_chunk()])
        assert r.weight == WEIGHT_SOURCE_DIVERSITY


# ---------------------------------------------------------------------------
# VerificationAgent.verify
# ---------------------------------------------------------------------------

class TestVerificationAgentVerify:

    def test_returns_verification_result(self) -> None:
        agent = VerificationAgent()
        syn = _make_synthesis()
        result = agent.verify(syn)
        assert isinstance(result, VerificationResult)

    def test_overall_score_in_range(self) -> None:
        agent = VerificationAgent()
        result = agent.verify(_make_synthesis())
        assert 0.0 <= result.overall_score <= 1.0

    def test_verdict_is_valid_enum(self) -> None:
        agent = VerificationAgent()
        result = agent.verify(_make_synthesis())
        assert result.verdict in (Verdict.HIGH, Verdict.MEDIUM, Verdict.LOW)

    def test_four_checks_returned(self) -> None:
        agent = VerificationAgent()
        result = agent.verify(_make_synthesis())
        assert len(result.checks) == 4

    def test_check_names_correct(self) -> None:
        agent = VerificationAgent()
        result = agent.verify(_make_synthesis())
        names = {c.name for c in result.checks}
        assert names == {
            "citation_coverage",
            "grounding_ratio",
            "answer_quality",
            "source_diversity",
        }

    def test_high_quality_answer_gets_high_verdict(self) -> None:
        chunks = [
            _make_chunk(
                "The transformer architecture uses multi-head attention and "
                "feed-forward layers for sequence processing.",
                doc_hash=f"h{i}",
            )
            for i in range(3)
        ]
        answer = (
            "The transformer architecture uses multi-head attention [1] and "
            "feed-forward layers [2] for sequence processing. "
            "This enables parallelism and long-range dependencies [3]. "
            "The architecture has replaced recurrent networks in many tasks. "
            "Multi-head attention allows attending to multiple positions simultaneously. "
            "The encoder decoder structure processes input and output sequences."
        )
        syn = _make_synthesis(answer=answer, chunks=chunks, cited=[1, 2, 3])
        result = VerificationAgent().verify(syn)
        assert result.verdict in (Verdict.HIGH, Verdict.MEDIUM)

    def test_empty_answer_scores_zero_quality(self) -> None:
        """An empty answer should score 0.0 on the answer_quality check."""
        syn = _make_synthesis(answer="", chunks=[], cited=[])
        result = VerificationAgent().verify(syn)
        quality_check = next(c for c in result.checks if c.name == "answer_quality")
        assert quality_check.score == 0.0

    def test_no_citations_no_context_verdict_not_high(self) -> None:
        """With no context and no meaningful answer, verdict should not be HIGH."""
        syn = _make_synthesis(answer="no", chunks=[], cited=[])
        result = VerificationAgent().verify(syn)
        assert result.verdict != Verdict.HIGH

    def test_answer_words_stored(self) -> None:
        syn = _make_synthesis(answer="word " * 30)
        result = VerificationAgent().verify(syn)
        assert result.answer_words == 30

    def test_num_citations_stored(self) -> None:
        syn = _make_synthesis(answer="See [1] and [2] and [3].")
        result = VerificationAgent().verify(syn)
        assert result.num_citations == 3

    def test_num_context_chunks_stored(self) -> None:
        chunks = [_make_chunk(doc_hash=f"h{i}") for i in range(4)]
        syn = _make_synthesis(chunks=chunks)
        result = VerificationAgent().verify(syn)
        assert result.num_context_chunks == 4

    def test_check_scores_dict(self) -> None:
        result = VerificationAgent().verify(_make_synthesis())
        cs = result.check_scores
        assert "citation_coverage" in cs
        assert "grounding_ratio" in cs

    def test_is_high_confidence_property(self) -> None:
        # Force a HIGH verdict with a manually set score
        agent = VerificationAgent()
        result = agent.verify(_make_synthesis())
        assert result.is_high_confidence == (result.verdict == Verdict.HIGH)

    def test_summary_contains_verdict(self) -> None:
        result = VerificationAgent().verify(_make_synthesis())
        assert result.verdict.value in result.summary()

    def test_repr_contains_score(self) -> None:
        result = VerificationAgent().verify(_make_synthesis())
        assert "score=" in repr(result)


# ---------------------------------------------------------------------------
# VerificationAgent.verify_batch
# ---------------------------------------------------------------------------

class TestVerifyBatch:

    def test_returns_list_same_length(self) -> None:
        agent = VerificationAgent()
        syntheses = [_make_synthesis() for _ in range(3)]
        results = agent.verify_batch(syntheses)
        assert len(results) == 3

    def test_each_element_is_verification_result(self) -> None:
        agent = VerificationAgent()
        results = agent.verify_batch([_make_synthesis()])
        assert isinstance(results[0], VerificationResult)


# ---------------------------------------------------------------------------
# CheckResult.weighted_score
# ---------------------------------------------------------------------------

class TestCheckResult:

    def test_weighted_score_calculation(self) -> None:
        c = CheckResult(name="test", score=0.8, weight=0.25, detail="ok")
        assert c.weighted_score == pytest.approx(0.2)

    def test_zero_score_zero_weighted(self) -> None:
        c = CheckResult(name="test", score=0.0, weight=0.35, detail="none")
        assert c.weighted_score == 0.0
