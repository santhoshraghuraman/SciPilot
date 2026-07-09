"""
SciPilot — Planner Agent  (src/agents/planner.py)
===================================================
Decomposes a complex research question into 3–5 focused sub-questions
using IBM Granite, enabling the Retriever to perform targeted searches
for each aspect of the original question.

Why decomposition matters:
  A question like "How do transformers compare to RNNs in parallelism,
  memory efficiency, and long-range dependency handling?" touches at least
  three distinct topics. A single FAISS query blends all three signals,
  often retrieving mediocre passages for each. By decomposing into three
  targeted sub-questions, retrieval precision improves significantly.

Decomposition prompt strategy:
  - System message establishes the planning role.
  - User message provides the question and explicit format instructions.
  - Output is expected as a numbered list: "1. ...\n2. ...\n..."
  - Robust parser handles varied Granite output formats.
  - Fallback to [original_question] guarantees the pipeline never breaks.

Dependencies:
  - ibm-watsonx-ai
  - tenacity
  - src.utils.config  (settings)
  - src.utils.logger  (get_logger)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES: int = 3
DEFAULT_MIN_SUB_QUESTIONS: int = 2
DEFAULT_MAX_SUB_QUESTIONS: int = 5

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a scientific research planning assistant.
Your task is to break down a complex research question into smaller,
focused sub-questions that can each be answered independently.

Rules:
1. Output ONLY a numbered list of sub-questions. No explanations.
2. Each sub-question must be specific and self-contained.
3. Generate between {min_q} and {max_q} sub-questions.
4. Number each question: 1. ... 2. ... 3. ...
5. Do not repeat the original question as a sub-question."""

_USER_TEMPLATE = """Research Question: {question}

Sub-questions:"""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class PlannerResult:
    """
    Output of ``PlannerAgent.plan()``.

    Attributes:
        original_question: The input question passed to the planner.
        sub_questions:     Decomposed sub-questions (min 1 — fallback guaranteed).
        model_id:          IBM Granite model used.
        raw_response:      Raw text from the model (for debugging).
        used_fallback:     True when parsing failed and the original question
                           was used as the only sub-question.
    """

    original_question: str
    sub_questions: List[str]
    model_id: str = ""
    raw_response: str = ""
    used_fallback: bool = False

    @property
    def count(self) -> int:
        """Number of sub-questions generated."""
        return len(self.sub_questions)

    @property
    def is_decomposed(self) -> bool:
        """True when more than one sub-question was generated."""
        return self.count > 1

    def __repr__(self) -> str:
        return (
            f"PlannerResult(count={self.count}, "
            f"decomposed={self.is_decomposed}, "
            f"fallback={self.used_fallback})"
        )


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

# Matches lines like:  "1. question"  "1) question"  "- question"  "* question"
_LIST_ITEM_RE = re.compile(
    r"^\s*(?:\d+[.)]\s*|[-*•]\s*)(.+)$",
    re.MULTILINE,
)

# Matches a bare question line: starts with capital, ends with "?"
_BARE_QUESTION_RE = re.compile(r"^\s*([A-Z].+\?)\s*$", re.MULTILINE)


def parse_sub_questions(
    raw_text: str,
    min_q: int = DEFAULT_MIN_SUB_QUESTIONS,
    max_q: int = DEFAULT_MAX_SUB_QUESTIONS,
) -> List[str]:
    """
    Extract sub-questions from a raw Granite model response.

    Parsing order:
        1. Try numbered/bulleted list items (``_LIST_ITEM_RE``).
        2. Fall back to bare question sentences ending in ``?``.
        3. If still nothing, split on newlines and take non-blank lines.

    Args:
        raw_text: Raw text from the Granite API.
        min_q:    Minimum acceptable count (returns empty list if not met).
        max_q:    Maximum sub-questions to return.

    Returns:
        List of cleaned sub-question strings, length in [min_q, max_q],
        or empty list if parsing fails.
    """
    questions: List[str] = []

    # Strategy 1: numbered / bulleted list
    matches = _LIST_ITEM_RE.findall(raw_text)
    questions = [m.strip() for m in matches if m.strip()]

    # Strategy 2: bare questions ending in "?"
    if len(questions) < min_q:
        bare = _BARE_QUESTION_RE.findall(raw_text)
        questions = [q.strip() for q in bare if q.strip()]

    # Strategy 3: non-blank lines (last resort)
    if len(questions) < min_q:
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        # Filter: must be at least 10 chars to be a real question
        questions = [ln for ln in lines if len(ln) >= 10]

    # De-duplicate while preserving order
    seen: List[str] = []
    for q in questions:
        if q not in seen:
            seen.append(q)
    questions = seen

    # Enforce max
    questions = questions[:max_q]

    # Return empty list if below minimum (signals fallback needed)
    if len(questions) < min_q:
        return []

    return questions


# ---------------------------------------------------------------------------
# Lazy IBM client
# ---------------------------------------------------------------------------

_planner_client = None


def _get_planner_client():
    """
    Return a cached IBM Granite ``ModelInference`` client for the planner.

    Uses the instruct model with low temperature (0.1) for deterministic,
    structured list output.
    """
    global _planner_client

    if _planner_client is not None:
        return _planner_client

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params
    except ImportError as exc:
        raise ImportError(
            "ibm-watsonx-ai is not installed. Run: pip install ibm-watsonx-ai"
        ) from exc

    if not settings.watsonx_api_key or not settings.watsonx_project_id:
        raise RuntimeError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in .env"
        )

    credentials = Credentials(
        url=settings.watsonx_url,
        api_key=settings.watsonx_api_key,
    )

    params = {
        Params.MAX_NEW_TOKENS: 512,
        Params.TEMPERATURE: 0.1,     # low temperature for structured output
        Params.TOP_P: 0.9,
        Params.REPETITION_PENALTY: 1.05,
        Params.STOP_SEQUENCES: ["###", "<|user|>", "<|system|>"],
    }

    _planner_client = ModelInference(
        model_id=settings.granite_instruct_model,
        credentials=credentials,
        project_id=settings.watsonx_project_id,
        params=params,
    )

    logger.info(
        "PlannerAgent IBM client initialised (model=%s).",
        settings.granite_instruct_model,
    )
    return _planner_client


def reset_planner_client() -> None:
    """Clear cached client. Used by tests."""
    global _planner_client
    _planner_client = None


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(MAX_RETRIES),
    reraise=True,
)
def _call_granite_planner(prompt: str) -> str:
    """
    Call IBM Granite and return the generated text string.

    Args:
        prompt: Full formatted prompt.

    Returns:
        Generated text string from the model.
    """
    client = _get_planner_client()
    response = client.generate(prompt=prompt)
    return response["results"][0]["generated_text"]


# ---------------------------------------------------------------------------
# Planner Agent
# ---------------------------------------------------------------------------

class PlannerAgent:
    """
    Decomposes a complex research question into focused sub-questions
    using IBM Granite.

    Usage:
        agent = PlannerAgent()
        result = agent.plan("How do transformers compare to RNNs?")
        for q in result.sub_questions:
            print(q)
    """

    def __init__(
        self,
        min_sub_questions: int = DEFAULT_MIN_SUB_QUESTIONS,
        max_sub_questions: int = DEFAULT_MAX_SUB_QUESTIONS,
        model_id: Optional[str] = None,
    ) -> None:
        """
        Args:
            min_sub_questions: Minimum number of sub-questions to generate.
            max_sub_questions: Maximum number of sub-questions to generate.
            model_id:          Override the model ID from settings.
        """
        self._min_q = min_sub_questions
        self._max_q = max_sub_questions
        self._model_id = model_id or settings.granite_instruct_model
        logger.info(
            "PlannerAgent ready (model=%s, min=%d, max=%d).",
            self._model_id, self._min_q, self._max_q,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan(
        self,
        question: str,
        _mock_response: Optional[str] = None,
    ) -> PlannerResult:
        """
        Decompose *question* into focused sub-questions.

        Args:
            question:       The complex research question.
            _mock_response: Internal escape hatch for unit tests — if provided
                            the IBM API call is bypassed and this string is
                            parsed as the model response directly.

        Returns:
            A ``PlannerResult`` with sub-questions and metadata.

        Raises:
            ValueError: If question is blank.
        """
        question = question.strip()
        if not question:
            raise ValueError("question must not be blank.")

        prompt = self._build_prompt(question)

        # ── Call model (or use mock) ──────────────────────────────────────
        if _mock_response is not None:
            raw = _mock_response
        else:
            try:
                raw = _call_granite_planner(prompt)
            except Exception as exc:
                logger.error(
                    "PlannerAgent API call failed: %s — using fallback.", exc
                )
                return self._fallback(question, raw_response="", error=str(exc))

        # ── Parse sub-questions ───────────────────────────────────────────
        sub_questions = parse_sub_questions(raw, self._min_q, self._max_q)

        if not sub_questions:
            logger.warning(
                "Could not parse sub-questions from Granite response — "
                "falling back to original question."
            )
            return self._fallback(question, raw_response=raw)

        logger.info(
            "Decomposed question into %d sub-question(s): %s",
            len(sub_questions),
            sub_questions,
        )

        return PlannerResult(
            original_question=question,
            sub_questions=sub_questions,
            model_id=self._model_id,
            raw_response=raw,
            used_fallback=False,
        )

    def plan_or_passthrough(self, question: str) -> List[str]:
        """
        Convenience wrapper — always returns a list of question strings.

        If planning succeeds, returns sub-questions.
        If planning fails or is a simple question, returns [question].

        Args:
            question: Research question.

        Returns:
            List of question strings (≥ 1 element).
        """
        result = self.plan(question)
        return result.sub_questions

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, question: str) -> str:
        """
        Build the Granite instruct-format planning prompt.

        Args:
            question: The research question to decompose.

        Returns:
            Full prompt string.
        """
        system = _SYSTEM_PROMPT.format(
            min_q=self._min_q,
            max_q=self._max_q,
        )
        user = _USER_TEMPLATE.format(question=question)
        return (
            f"<|system|>\n{system}\n"
            f"<|user|>\n{user}\n"
            f"<|assistant|>\n"
        )

    @staticmethod
    def _fallback(
        question: str,
        raw_response: str = "",
        error: str = "",
    ) -> PlannerResult:
        """
        Return a fallback ``PlannerResult`` using the original question.

        Args:
            question:     The original research question.
            raw_response: Raw model output (may be empty on API error).
            error:        Error message if an exception occurred.

        Returns:
            ``PlannerResult`` with ``used_fallback=True`` and
            ``sub_questions=[question]``.
        """
        metadata: dict = {}
        if error:
            metadata["error"] = error
        return PlannerResult(
            original_question=question,
            sub_questions=[question],
            raw_response=raw_response,
            used_fallback=True,
        )
