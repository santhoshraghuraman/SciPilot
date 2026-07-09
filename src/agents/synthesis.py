"""
SciPilot — IBM Granite Synthesis Agent  (src/agents/synthesis.py)
==================================================================
Given a research question and a set of retrieved context chunks, calls
IBM Granite to produce a grounded, cited answer.

Prompt strategy (Granite instruct format):
  - A system message establishes the "research assistant" persona and
    the strict rule: answer ONLY from the provided context.
  - The user message contains the numbered context passages followed by
    the research question.
  - The model is expected to cite passages inline as [1], [2], etc.

IBM watsonx.ai SDK:
  https://ibm.github.io/watson-machine-learning-py-client/

Dependencies:
  - ibm-watsonx-ai
  - tenacity
  - src.agents.retriever  (RetrievalResult)
  - src.utils.config      (settings)
  - src.utils.logger      (get_logger)
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.agents.retriever import RetrievalResult
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES: int = 3
_CITATION_RE = re.compile(r"\[(\d+)\]")  # matches [1], [12], etc.

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are SciPilot, an expert scientific research assistant powered by IBM Granite.

Your task is to answer research questions accurately and concisely using ONLY the context passages provided.

Rules:
1. Base every claim on the provided context. Do NOT use outside knowledge.
2. Cite the passage number inline, e.g. [1], [2], when you use information from it.
3. If the context does not contain enough information to answer the question, say:
   "The provided documents do not contain sufficient information to answer this question."
4. Keep the answer focused, well-structured, and suitable for an academic audience.
5. Do not repeat the question in your answer."""

_CONTEXT_BLOCK_TEMPLATE = """### Context Passages

{passages}

"""

_USER_TEMPLATE = """{context}### Research Question

{question}

### Answer"""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SynthesisResult:
    """
    The output of ``SynthesisAgent.synthesise()``.

    Attributes:
        answer:          The grounded answer text produced by IBM Granite.
        cited_indices:   1-based passage indices cited in the answer (e.g. [1, 3]).
        question:        The original research question.
        context_chunks:  The ``RetrievalResult`` chunks used as context.
        prompt:          The full prompt sent to the model (for debugging).
        model_id:        IBM model identifier used for this response.
        input_tokens:    Approximate input token count.
        output_tokens:   Output token count.
        latency_s:       Wall-clock seconds for the API call.
        metadata:        Any additional key-value pairs.
    """

    answer: str
    cited_indices: List[int]
    question: str
    context_chunks: List[Any]          # List[TextChunk], typed as Any to avoid circular
    prompt: str = ""
    model_id: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_grounded(self) -> bool:
        """True when the answer cites at least one passage."""
        return len(self.cited_indices) > 0

    @property
    def cited_chunks(self) -> List[Any]:
        """Return only the chunks that are actually cited in the answer."""
        # cited_indices are 1-based; context_chunks list is 0-based
        result = []
        for idx in self.cited_indices:
            pos = idx - 1
            if 0 <= pos < len(self.context_chunks):
                result.append(self.context_chunks[pos])
        return result

    def __repr__(self) -> str:
        return (
            f"SynthesisResult(words={len(self.answer.split())}, "
            f"cited={self.cited_indices}, "
            f"grounded={self.is_grounded}, "
            f"latency={self.latency_s:.2f}s)"
        )


# ---------------------------------------------------------------------------
# Lazy IBM client
# ---------------------------------------------------------------------------

_llm_client = None


def _get_llm_client():
    """
    Return a cached ``ibm_watsonx_ai`` ModelInference client.

    Lazy initialisation avoids importing the heavy IBM SDK at module load
    time and allows tests to patch this function cleanly.

    Returns:
        A configured ``ModelInference`` instance.

    Raises:
        ImportError:  If ``ibm-watsonx-ai`` is not installed.
        RuntimeError: If credentials are missing from settings.
    """
    global _llm_client

    if _llm_client is not None:
        return _llm_client

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

    generate_params = {
        Params.MAX_NEW_TOKENS: settings.max_new_tokens,
        Params.TEMPERATURE: settings.temperature,
        Params.TOP_P: settings.top_p,
        Params.REPETITION_PENALTY: settings.repetition_penalty,
        Params.STOP_SEQUENCES: ["###", "<|user|>", "<|system|>"],
    }

    _llm_client = ModelInference(
        model_id=settings.granite_instruct_model,
        credentials=credentials,
        project_id=settings.watsonx_project_id,
        params=generate_params,
    )

    logger.info(
        "IBM Granite LLM client initialised (model=%s).",
        settings.granite_instruct_model,
    )
    return _llm_client


def reset_llm_client() -> None:
    """Clear the cached LLM client. Used by tests."""
    global _llm_client
    _llm_client = None


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def build_prompt(question: str, retrieval: RetrievalResult) -> str:
    """
    Construct the full Granite instruct-format prompt.

    The prompt structure:
        <|system|>
        {SYSTEM_PROMPT}
        <|user|>
        ### Context Passages
        [1] Source: ... | Page: ...
        <passage text>

        [2] ...

        ### Research Question
        {question}

        ### Answer
        <|assistant|>

    Args:
        question:  The research question.
        retrieval: ``RetrievalResult`` containing ranked context chunks.

    Returns:
        Complete prompt string ready for the Granite model.
    """
    # Build numbered passage block
    passage_lines: List[str] = []
    for i, chunk in enumerate(retrieval.chunks, start=1):
        header = (
            f"[{i}] Source: {chunk.source} | "
            f"Page: {chunk.page_number} | "
            f"Title: {chunk.doc_title}"
        )
        passage_lines.append(f"{header}\n{chunk.text.strip()}")

    passages_str = "\n\n".join(passage_lines) if passage_lines else "(No context available)"
    context_block = _CONTEXT_BLOCK_TEMPLATE.format(passages=passages_str)
    user_content = _USER_TEMPLATE.format(context=context_block, question=question)

    prompt = (
        f"<|system|>\n{_SYSTEM_PROMPT}\n"
        f"<|user|>\n{user_content}\n"
        f"<|assistant|>\n"
    )
    return prompt


def _extract_cited_indices(answer_text: str) -> List[int]:
    """
    Parse inline citation markers from *answer_text* and return the unique
    1-based passage indices in the order they first appear.

    Example:
        "Attention was proposed in [1] and extended in [2] and [1]."
        → [1, 2]

    Args:
        answer_text: Raw answer string from the model.

    Returns:
        Sorted list of unique cited 1-based indices.
    """
    matches = _CITATION_RE.findall(answer_text)
    seen: List[int] = []
    for m in matches:
        idx = int(m)
        if idx not in seen:
            seen.append(idx)
    return seen


def _clean_answer(raw: str) -> str:
    """
    Strip prompt artefacts from the raw model output.

    Granite sometimes echoes the ``### Answer`` header or leaves trailing
    stop-sequence tokens in the response. This function cleans them out.

    Args:
        raw: Raw text returned by ``ModelInference.generate_text()``.

    Returns:
        Cleaned answer string.
    """
    # Remove any residual Granite role tokens
    cleaned = re.sub(r"<\|.*?\|>", "", raw)
    # Remove leading "### Answer" if the model echoed it
    cleaned = re.sub(r"^#+\s*Answer\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


# ---------------------------------------------------------------------------
# Synthesis Agent
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(MAX_RETRIES),
    reraise=True,
)
def _call_granite(prompt: str) -> Dict[str, Any]:
    """
    Make a single retried call to the IBM Granite text generation API.

    Args:
        prompt: The full formatted prompt string.

    Returns:
        The raw API response dict.
    """
    client = _get_llm_client()
    response = client.generate(prompt=prompt)
    return response


class SynthesisAgent:
    """
    Calls IBM Granite to produce a grounded, cited answer from retrieved
    context chunks.

    Usage:
        agent = SynthesisAgent()
        result = agent.synthesise(
            question="What is multi-head attention?",
            retrieval=retrieval_result,
        )
        print(result.answer)
    """

    def __init__(self, model_id: Optional[str] = None) -> None:
        """
        Args:
            model_id: Override the model ID from settings.  Useful for
                      switching between granite-13b-instruct and granite-13b-chat.
        """
        self._model_id = model_id or settings.granite_instruct_model
        logger.info("SynthesisAgent ready (model=%s).", self._model_id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesise(
        self,
        question: str,
        retrieval: RetrievalResult,
        _mock_response: Optional[str] = None,
    ) -> SynthesisResult:
        """
        Generate a grounded answer for *question* using context from *retrieval*.

        Args:
            question:       Research question string.
            retrieval:      ``RetrievalResult`` from the Retriever Agent.
            _mock_response: Internal escape hatch for unit tests — if provided,
                            the IBM API is bypassed and this string is used as
                            the answer directly.

        Returns:
            A fully populated ``SynthesisResult``.
        """
        question = question.strip()
        if not question:
            raise ValueError("question must not be blank.")

        prompt = build_prompt(question, retrieval)

        # ── No-context fast path ──────────────────────────────────────────
        if retrieval.is_empty:
            logger.warning(
                "SynthesisAgent called with empty retrieval for question: %s",
                question[:80],
            )
            return SynthesisResult(
                answer=(
                    "The provided documents do not contain sufficient "
                    "information to answer this question."
                ),
                cited_indices=[],
                question=question,
                context_chunks=[],
                prompt=prompt,
                model_id=self._model_id,
            )

        # ── Call IBM Granite ──────────────────────────────────────────────
        t0 = time.perf_counter()

        if _mock_response is not None:
            raw_answer = _mock_response
            input_tokens = 0
            output_tokens = 0
        else:
            try:
                response = _call_granite(prompt)
                raw_answer = response["results"][0]["generated_text"]
                input_tokens = response["results"][0].get("input_token_count", 0)
                output_tokens = response["results"][0].get("generated_token_count", 0)
            except Exception as exc:
                logger.error("IBM Granite API call failed: %s", exc)
                raise

        latency = time.perf_counter() - t0

        # ── Post-process ──────────────────────────────────────────────────
        answer = _clean_answer(raw_answer)
        cited_indices = _extract_cited_indices(answer)

        logger.info(
            "Synthesis complete — %d words, cited=%s, latency=%.2fs",
            len(answer.split()),
            cited_indices,
            latency,
        )

        return SynthesisResult(
            answer=answer,
            cited_indices=cited_indices,
            question=question,
            context_chunks=retrieval.chunks,
            prompt=prompt,
            model_id=self._model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_s=latency,
        )

    def synthesise_multi(
        self,
        questions: List[str],
        retrieval: RetrievalResult,
    ) -> List[SynthesisResult]:
        """
        Synthesise answers for multiple sub-questions (from the Planner Agent)
        using the same retrieval context.

        Args:
            questions: List of sub-questions from ``PlannerAgent``.
            retrieval: Shared ``RetrievalResult`` context.

        Returns:
            List of ``SynthesisResult`` objects, one per question.
        """
        results: List[SynthesisResult] = []
        for i, q in enumerate(questions, start=1):
            logger.info("Synthesising answer %d/%d: %s", i, len(questions), q[:60])
            results.append(self.synthesise(q, retrieval))
        return results
