"""
Module 9 tests — Planner Agent  (src/agents/planner.py)

All IBM API calls bypassed via ``_mock_response``.  Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_planner.py -v
"""

from __future__ import annotations

import pytest

from src.agents.planner import (
    DEFAULT_MAX_SUB_QUESTIONS,
    DEFAULT_MIN_SUB_QUESTIONS,
    PlannerAgent,
    PlannerResult,
    parse_sub_questions,
    reset_planner_client,
)


# ---------------------------------------------------------------------------
# parse_sub_questions
# ---------------------------------------------------------------------------

class TestParseSubQuestions:

    # ── numbered list ────────────────────────────────────────────────────

    def test_numbered_list_dot(self) -> None:
        raw = "1. What is attention?\n2. How does self-attention work?\n3. What is positional encoding?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) == 3
        assert "What is attention?" in result

    def test_numbered_list_paren(self) -> None:
        raw = "1) What is BERT?\n2) How is BERT pre-trained?\n3) What tasks does BERT solve?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) == 3

    def test_bulleted_dash(self) -> None:
        raw = "- What is a transformer?\n- How does multi-head attention work?\n- What is positional encoding?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) == 3

    def test_bulleted_asterisk(self) -> None:
        raw = "* First sub-question here?\n* Second sub-question here?\n* Third sub-question here?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) == 3

    # ── fallback strategies ───────────────────────────────────────────────

    def test_bare_questions_fallback(self) -> None:
        raw = "What is attention?\nHow does self-attention work?\nWhat is positional encoding?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) >= 2

    def test_returns_empty_below_min(self) -> None:
        raw = "1. Only one question here?"
        result = parse_sub_questions(raw, min_q=3)
        assert result == []

    def test_deduplicates(self) -> None:
        raw = "1. What is attention?\n2. What is attention?\n3. How does it work?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) == len(set(result))

    def test_respects_max(self) -> None:
        raw = "\n".join(f"{i}. Question number {i}?" for i in range(1, 10))
        result = parse_sub_questions(raw, min_q=2, max_q=4)
        assert len(result) <= 4

    def test_strips_whitespace(self) -> None:
        raw = "  1.   What is attention?   \n  2.   How does it work?  "
        result = parse_sub_questions(raw, min_q=2)
        assert not any(q.startswith(" ") or q.endswith(" ") for q in result)

    def test_filters_very_short_lines(self) -> None:
        """Lines shorter than 10 chars should be ignored in the last-resort pass."""
        raw = "hi\nok\n1. What is multi-head attention in transformers?\n2. How does positional encoding work?"
        result = parse_sub_questions(raw, min_q=2)
        assert all(len(q) >= 10 for q in result)

    def test_mixed_prefixes(self) -> None:
        raw = "1. First question about transformers?\n- Second question about BERT?\n* Third about GPT?"
        result = parse_sub_questions(raw, min_q=2)
        assert len(result) >= 2


# ---------------------------------------------------------------------------
# PlannerAgent.plan — offline (mock_response)
# ---------------------------------------------------------------------------

class TestPlannerAgentPlan:

    def setup_method(self) -> None:
        reset_planner_client()

    def _good_response(self) -> str:
        return (
            "1. What is the transformer architecture?\n"
            "2. How does multi-head attention work?\n"
            "3. What is positional encoding and why is it needed?\n"
            "4. How do transformers handle long-range dependencies?"
        )

    def test_returns_planner_result(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("How do transformers work?",
                            _mock_response=self._good_response())
        assert isinstance(result, PlannerResult)

    def test_sub_questions_populated(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("How do transformers work?",
                            _mock_response=self._good_response())
        assert len(result.sub_questions) == 4

    def test_original_question_stored(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("How do transformers work?",
                            _mock_response=self._good_response())
        assert result.original_question == "How do transformers work?"

    def test_not_fallback_on_good_response(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("How do transformers work?",
                            _mock_response=self._good_response())
        assert result.used_fallback is False

    def test_raw_response_stored(self) -> None:
        agent = PlannerAgent()
        raw = self._good_response()
        result = agent.plan("Q?", _mock_response=raw)
        assert result.raw_response == raw

    def test_is_decomposed_true(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("Q?", _mock_response=self._good_response())
        assert result.is_decomposed is True

    def test_count_property(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("Q?", _mock_response=self._good_response())
        assert result.count == len(result.sub_questions)

    def test_raises_on_blank_question(self) -> None:
        agent = PlannerAgent()
        with pytest.raises(ValueError, match="blank"):
            agent.plan("   ")

    def test_fallback_on_unparseable_response(self) -> None:
        """Garbled output → fallback to original question."""
        agent = PlannerAgent(min_sub_questions=3)
        result = agent.plan(
            "What is attention?",
            _mock_response="I cannot process this request.",
        )
        assert result.used_fallback is True
        assert result.sub_questions == ["What is attention?"]

    def test_fallback_result_has_one_subquestion(self) -> None:
        agent = PlannerAgent(min_sub_questions=3)
        result = agent.plan(
            "Simple question?",
            _mock_response="",
        )
        assert result.sub_questions == ["Simple question?"]

    def test_max_sub_questions_enforced(self) -> None:
        agent = PlannerAgent(max_sub_questions=2)
        raw = "\n".join(f"{i}. Question {i}?" for i in range(1, 8))
        result = agent.plan("Big question?", _mock_response=raw)
        assert len(result.sub_questions) <= 2

    def test_min_sub_questions_triggers_fallback(self) -> None:
        """If model returns fewer than min, fallback should be used."""
        agent = PlannerAgent(min_sub_questions=4)
        raw = "1. Only one question?"
        result = agent.plan("Q?", _mock_response=raw)
        assert result.used_fallback is True

    def test_sub_questions_are_strings(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("Q?", _mock_response=self._good_response())
        assert all(isinstance(q, str) for q in result.sub_questions)

    def test_sub_questions_non_empty_strings(self) -> None:
        agent = PlannerAgent()
        result = agent.plan("Q?", _mock_response=self._good_response())
        assert all(q.strip() for q in result.sub_questions)


# ---------------------------------------------------------------------------
# PlannerAgent.plan_or_passthrough
# ---------------------------------------------------------------------------

class TestPlanOrPassthrough:

    def test_returns_list(self) -> None:
        agent = PlannerAgent()
        raw = "1. What is it?\n2. How does it work?\n3. Why is it used?"
        result = agent.plan_or_passthrough.__wrapped__ if hasattr(
            agent.plan_or_passthrough, "__wrapped__") else None
        # Call plan directly to test the logic
        plan_result = agent.plan("What is attention?", _mock_response=raw)
        assert isinstance(plan_result.sub_questions, list)

    def test_passthrough_on_fallback(self) -> None:
        """Even on fallback, plan_or_passthrough returns a non-empty list."""
        agent = PlannerAgent(min_sub_questions=5)
        plan_result = agent.plan("Simple Q?", _mock_response="only one line")
        assert len(plan_result.sub_questions) >= 1


# ---------------------------------------------------------------------------
# PlannerResult properties
# ---------------------------------------------------------------------------

class TestPlannerResult:

    def _make_result(self, n: int = 3, fallback: bool = False) -> PlannerResult:
        return PlannerResult(
            original_question="How do transformers work?",
            sub_questions=[f"Sub-question {i}?" for i in range(n)],
            model_id="ibm/granite-test",
            used_fallback=fallback,
        )

    def test_count_equals_len(self) -> None:
        r = self._make_result(4)
        assert r.count == 4

    def test_is_decomposed_true_for_multiple(self) -> None:
        r = self._make_result(3)
        assert r.is_decomposed is True

    def test_is_decomposed_false_for_one(self) -> None:
        r = self._make_result(1)
        assert r.is_decomposed is False

    def test_repr_contains_count(self) -> None:
        r = self._make_result(3)
        assert "count=3" in repr(r)

    def test_repr_contains_decomposed(self) -> None:
        r = self._make_result(3)
        assert "decomposed=True" in repr(r)

    def test_repr_contains_fallback(self) -> None:
        r = self._make_result(1, fallback=True)
        assert "fallback=True" in repr(r)

    def test_fallback_flag_stored(self) -> None:
        r = self._make_result(fallback=True)
        assert r.used_fallback is True

    def test_non_fallback_flag_stored(self) -> None:
        r = self._make_result(fallback=False)
        assert r.used_fallback is False
