"""
SciPilot — Verification Agent  (src/agents/verification.py)
=============================================================
Scores a ``SynthesisResult`` across four quality dimensions and returns
an overall confidence score in [0.0, 1.0] with a human-readable verdict.

The four checks are intentionally zero-dependency and deterministic —
they run locally with no LLM or network calls, making verification fast
and always available regardless of API quota.

Checks and weights:
  1. Citation Coverage   (weight 0.35) — Are inline [N] citations valid?
  2. Grounding Ratio     (weight 0.35) — Do answer sentences match context?
  3. Answer Quality      (weight 0.15) — Is the answer a reasonable length?
  4. Source Diversity    (weight 0.15) — Does the answer cite multiple docs?

Verdict mapping:
  score ≥ 0.70  →  HIGH
  score ≥ 0.40  →  MEDIUM
  score  < 0.40  →  LOW

Dependencies:
  - src.agents.synthesis  (SynthesisResult)
  - src.rag.chunk         (TextChunk)
  - src.utils.logger      (get_logger)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from src.agents.synthesis import SynthesisResult
from src.rag.chunk import TextChunk
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants — check weights (must sum to 1.0)
# ---------------------------------------------------------------------------

WEIGHT_CITATION_COVERAGE: float = 0.35
WEIGHT_GROUNDING_RATIO:   float = 0.35
WEIGHT_ANSWER_QUALITY:    float = 0.15
WEIGHT_SOURCE_DIVERSITY:  float = 0.15

_WEIGHT_SUM = (
    WEIGHT_CITATION_COVERAGE
    + WEIGHT_GROUNDING_RATIO
    + WEIGHT_ANSWER_QUALITY
    + WEIGHT_SOURCE_DIVERSITY
)
assert abs(_WEIGHT_SUM - 1.0) < 1e-9, f"Weights must sum to 1.0, got {_WEIGHT_SUM}"

# Answer word-count bounds for the quality check
_MIN_ANSWER_WORDS: int = 20
_MAX_ANSWER_WORDS: int = 600

# Minimum overlap words for a sentence to be considered "grounded"
_MIN_OVERLAP_WORDS: int = 3

# Minimum word length to count as a content word (filters stop words)
_MIN_WORD_LEN: int = 4

# Sentence splitter
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


# ---------------------------------------------------------------------------
# Verdict enum
# ---------------------------------------------------------------------------

class Verdict(str, Enum):
    """Human-readable confidence verdict."""
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


def score_to_verdict(score: float) -> Verdict:
    """
    Map a float confidence score to a ``Verdict``.

    Args:
        score: Float in [0.0, 1.0].

    Returns:
        ``Verdict.HIGH`` if score ≥ 0.70,
        ``Verdict.MEDIUM`` if score ≥ 0.40,
        ``Verdict.LOW`` otherwise.
    """
    if score >= 0.70:
        return Verdict.HIGH
    if score >= 0.40:
        return Verdict.MEDIUM
    return Verdict.LOW


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """
    Result of a single verification check.

    Attributes:
        name:    Short identifier (e.g. ``"citation_coverage"``).
        score:   Float in [0.0, 1.0].
        weight:  Contribution weight in the overall score.
        detail:  Human-readable explanation of this check's score.
    """
    name: str
    score: float
    weight: float
    detail: str

    @property
    def weighted_score(self) -> float:
        """Score × weight."""
        return self.score * self.weight


@dataclass
class VerificationResult:
    """
    Output of ``VerificationAgent.verify()``.

    Attributes:
        overall_score:   Weighted sum of all check scores, in [0.0, 1.0].
        verdict:         ``Verdict.HIGH``, ``MEDIUM``, or ``LOW``.
        checks:          Individual ``CheckResult`` objects.
        answer_words:    Word count of the verified answer.
        num_citations:   Number of inline citations found in the answer.
        num_context_chunks: Number of context chunks provided.
        metadata:        Additional key-value pairs.
    """
    overall_score: float
    verdict: Verdict
    checks: List[CheckResult]
    answer_words: int
    num_citations: int
    num_context_chunks: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_high_confidence(self) -> bool:
        return self.verdict == Verdict.HIGH

    @property
    def check_scores(self) -> Dict[str, float]:
        """Dict mapping check name → score."""
        return {c.name: c.score for c in self.checks}

    def summary(self) -> str:
        """One-line human-readable summary."""
        return (
            f"Verdict: {self.verdict.value} "
            f"(score={self.overall_score:.2f}) | "
            + " | ".join(f"{c.name}={c.score:.2f}" for c in self.checks)
        )

    def __repr__(self) -> str:
        return (
            f"VerificationResult(score={self.overall_score:.2f}, "
            f"verdict={self.verdict.value})"
        )


# ---------------------------------------------------------------------------
# Individual check implementations
# ---------------------------------------------------------------------------

def _content_words(text: str) -> set:
    """
    Extract lowercase content words (length ≥ _MIN_WORD_LEN) from *text*.

    Filters out short function words and strips punctuation to improve
    vocabulary overlap comparisons.

    Args:
        text: Any string.

    Returns:
        Set of lowercase content word strings.
    """
    tokens = re.findall(r"\b[a-zA-Z]{%d,}\b" % _MIN_WORD_LEN, text.lower())
    return set(tokens)


def check_citation_coverage(
    answer: str,
    num_context_chunks: int,
) -> CheckResult:
    """
    Check 1 — Citation Coverage.

    Measures: what fraction of the inline citation markers [N] in the
    answer correspond to valid context passage indices (1 ≤ N ≤ num_chunks)?

    Score:
        1.0 — all citations are valid (or no citations found)
        0.5 — some citations are out-of-range
        0.0 — all citations are invalid or answer has no citations at all
              when context is available (penalises ungrounded answers)

    Args:
        answer:             The generated answer text.
        num_context_chunks: Number of context passages provided.

    Returns:
        A ``CheckResult`` for citation coverage.
    """
    citation_matches = re.findall(r"\[(\d+)\]", answer)

    if not citation_matches:
        # No citations at all — penalise proportional to available context
        score = 0.0 if num_context_chunks > 0 else 1.0
        return CheckResult(
            name="citation_coverage",
            score=score,
            weight=WEIGHT_CITATION_COVERAGE,
            detail=(
                "No inline citations found."
                if num_context_chunks > 0
                else "No context provided — citation check skipped."
            ),
        )

    cited_indices = [int(m) for m in citation_matches]
    valid = [i for i in cited_indices if 1 <= i <= num_context_chunks]
    score = len(valid) / len(cited_indices)

    return CheckResult(
        name="citation_coverage",
        score=score,
        weight=WEIGHT_CITATION_COVERAGE,
        detail=(
            f"{len(valid)}/{len(cited_indices)} citations valid "
            f"(context has {num_context_chunks} passage(s))."
        ),
    )


def check_grounding_ratio(
    answer: str,
    context_chunks: List[TextChunk],
) -> CheckResult:
    """
    Check 2 — Grounding Ratio.

    Measures: what fraction of answer sentences share at least
    ``_MIN_OVERLAP_WORDS`` content words with the combined context.

    A sentence is "grounded" when it uses vocabulary drawn from the
    retrieved passages — indicating the model actually read and used
    the context rather than generating from prior knowledge.

    Args:
        answer:         The generated answer text.
        context_chunks: Retrieved context passages.

    Returns:
        A ``CheckResult`` for grounding ratio.
    """
    if not context_chunks:
        return CheckResult(
            name="grounding_ratio",
            score=0.5,   # neutral — no context to check against
            weight=WEIGHT_GROUNDING_RATIO,
            detail="No context chunks provided — grounding check neutral.",
        )

    # Build a combined vocabulary from all context chunks
    context_vocab: set = set()
    for chunk in context_chunks:
        context_vocab |= _content_words(chunk.text)

    # Split answer into sentences
    raw_sentences = _SENTENCE_RE.split(answer.strip())
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]

    if not sentences:
        return CheckResult(
            name="grounding_ratio",
            score=0.0,
            weight=WEIGHT_GROUNDING_RATIO,
            detail="Answer has no scoreable sentences.",
        )

    grounded = 0
    for sentence in sentences:
        sentence_words = _content_words(sentence)
        overlap = len(sentence_words & context_vocab)
        if overlap >= _MIN_OVERLAP_WORDS:
            grounded += 1

    score = grounded / len(sentences)

    return CheckResult(
        name="grounding_ratio",
        score=score,
        weight=WEIGHT_GROUNDING_RATIO,
        detail=(
            f"{grounded}/{len(sentences)} sentences grounded "
            f"(overlap threshold={_MIN_OVERLAP_WORDS} words)."
        ),
    )


def check_answer_quality(answer: str) -> CheckResult:
    """
    Check 3 — Answer Quality (length heuristic).

    Penalises answers that are suspiciously short (evasion / model refusing
    to answer) or excessively long (likely padding / repetition).

    Scoring:
        words < _MIN_ANSWER_WORDS  → score = words / _MIN_ANSWER_WORDS  (< 1.0)
        words > _MAX_ANSWER_WORDS  → score = _MAX_ANSWER_WORDS / words   (< 1.0)
        otherwise                  → score = 1.0

    Args:
        answer: The generated answer text.

    Returns:
        A ``CheckResult`` for answer quality.
    """
    words = len(answer.split())

    if words < _MIN_ANSWER_WORDS:
        score = words / _MIN_ANSWER_WORDS
        detail = f"Answer too short ({words} words; min={_MIN_ANSWER_WORDS})."
    elif words > _MAX_ANSWER_WORDS:
        score = _MAX_ANSWER_WORDS / words
        detail = f"Answer too long ({words} words; max={_MAX_ANSWER_WORDS})."
    else:
        score = 1.0
        detail = f"Answer length acceptable ({words} words)."

    return CheckResult(
        name="answer_quality",
        score=score,
        weight=WEIGHT_ANSWER_QUALITY,
        detail=detail,
    )


def check_source_diversity(context_chunks: List[TextChunk]) -> CheckResult:
    """
    Check 4 — Source Diversity.

    Rewards answers that draw from multiple distinct source documents.
    A higher number of unique document hashes in the context indicates
    the retriever pulled from a wider range of evidence.

    Scoring (sigmoid-like, capped at 1.0):
        unique_docs = 1  → 0.33
        unique_docs = 2  → 0.67
        unique_docs ≥ 3  → 1.00

    Args:
        context_chunks: Retrieved context passages used for the answer.

    Returns:
        A ``CheckResult`` for source diversity.
    """
    if not context_chunks:
        return CheckResult(
            name="source_diversity",
            score=0.0,
            weight=WEIGHT_SOURCE_DIVERSITY,
            detail="No context chunks — diversity check skipped.",
        )

    unique_docs = len({chunk.doc_hash for chunk in context_chunks})
    score = min(unique_docs / 3.0, 1.0)

    return CheckResult(
        name="source_diversity",
        score=score,
        weight=WEIGHT_SOURCE_DIVERSITY,
        detail=f"{unique_docs} unique source document(s) in context.",
    )


# ---------------------------------------------------------------------------
# Verification Agent
# ---------------------------------------------------------------------------

class VerificationAgent:
    """
    Quality-gates a ``SynthesisResult`` by running four independent checks
    and computing a weighted confidence score.

    Usage:
        agent = VerificationAgent()
        result = agent.verify(synthesis_result)
        print(result.verdict)         # HIGH / MEDIUM / LOW
        print(result.overall_score)   # e.g. 0.81
        print(result.summary())       # one-liner
    """

    def verify(self, synthesis: SynthesisResult) -> VerificationResult:
        """
        Run all four checks on *synthesis* and return a ``VerificationResult``.

        Args:
            synthesis: A ``SynthesisResult`` from Module 6.

        Returns:
            A fully populated ``VerificationResult``.
        """
        answer = synthesis.answer
        chunks = synthesis.context_chunks

        # ── Run individual checks ─────────────────────────────────────────
        c1 = check_citation_coverage(answer, len(chunks))
        c2 = check_grounding_ratio(answer, chunks)
        c3 = check_answer_quality(answer)
        c4 = check_source_diversity(chunks)

        checks = [c1, c2, c3, c4]

        # ── Compute weighted overall score ────────────────────────────────
        overall = sum(c.weighted_score for c in checks)
        overall = max(0.0, min(1.0, overall))  # clamp to [0, 1]

        verdict = score_to_verdict(overall)

        answer_words = len(answer.split())
        num_citations = len(re.findall(r"\[\d+\]", answer))

        result = VerificationResult(
            overall_score=overall,
            verdict=verdict,
            checks=checks,
            answer_words=answer_words,
            num_citations=num_citations,
            num_context_chunks=len(chunks),
        )

        logger.info(
            "Verification: score=%.2f verdict=%s | %s",
            overall,
            verdict.value,
            " | ".join(f"{c.name}={c.score:.2f}" for c in checks),
        )

        return result

    def verify_batch(
        self, syntheses: List[SynthesisResult]
    ) -> List[VerificationResult]:
        """
        Verify a list of synthesis results (e.g. from ``synthesise_multi``).

        Args:
            syntheses: List of ``SynthesisResult`` objects.

        Returns:
            List of ``VerificationResult`` objects in the same order.
        """
        return [self.verify(s) for s in syntheses]
