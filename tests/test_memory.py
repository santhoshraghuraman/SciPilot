"""
Module 11 tests — Memory Agent  (src/agents/memory.py)

IBM COS calls are mocked.  Local-backend tests use tmp_path (real I/O).
Tests run 100% offline.

Run with:
    cd SciPilot
    python -m pytest tests/test_memory.py -v
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from src.agents.memory import (
    MemoryAgent,
    SessionRecord,
    _cos_available,
    _local_delete,
    _local_dir,
    _local_get,
    _local_list,
    _local_put,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_record(
    question: str = "What is attention?",
    answer: str = "Attention is a mechanism [1].",
    verdict: str = "HIGH",
    confidence: float = 0.85,
) -> SessionRecord:
    return SessionRecord(
        question=question,
        answer=answer,
        sub_questions=["What is self-attention?", "How is it computed?"],
        cited_sources=["paper.pdf"],
        citation_strings=["Smith, J. (2017). *Title*. *arXiv*."],
        citation_style="APA",
        confidence_score=confidence,
        verdict=verdict,
        model_id="ibm/granite-13b-instruct-v2",
        num_chunks=3,
    )


# ---------------------------------------------------------------------------
# SessionRecord — serialisation
# ---------------------------------------------------------------------------

class TestSessionRecordSerialisation:

    def test_to_json_returns_string(self) -> None:
        r = _make_record()
        assert isinstance(r.to_json(), str)

    def test_to_json_is_valid_json(self) -> None:
        r = _make_record()
        data = json.loads(r.to_json())
        assert isinstance(data, dict)

    def test_to_json_contains_required_fields(self) -> None:
        r = _make_record()
        data = json.loads(r.to_json())
        for field in ("session_id", "question", "answer", "created_at"):
            assert field in data

    def test_from_json_round_trips(self) -> None:
        r = _make_record()
        json_str = r.to_json()
        restored = SessionRecord.from_json(json_str)
        assert restored.session_id == r.session_id
        assert restored.question == r.question
        assert restored.answer == r.answer

    def test_from_json_restores_verdict(self) -> None:
        r = _make_record(verdict="MEDIUM")
        restored = SessionRecord.from_json(r.to_json())
        assert restored.verdict == "MEDIUM"

    def test_from_json_restores_confidence(self) -> None:
        r = _make_record(confidence=0.72)
        restored = SessionRecord.from_json(r.to_json())
        assert restored.confidence_score == pytest.approx(0.72)

    def test_from_json_raises_on_missing_field(self) -> None:
        bad = json.dumps({"question": "Q?", "answer": "A."})  # missing session_id
        with pytest.raises(ValueError, match="missing required field"):
            SessionRecord.from_json(bad)

    def test_session_id_auto_generated(self) -> None:
        r = SessionRecord(question="Q?", answer="A.")
        assert len(r.session_id) == 36  # UUID4 format: 8-4-4-4-12

    def test_two_records_have_different_ids(self) -> None:
        r1 = SessionRecord(question="Q?", answer="A.")
        r2 = SessionRecord(question="Q?", answer="A.")
        assert r1.session_id != r2.session_id

    def test_created_at_is_iso_string(self) -> None:
        r = SessionRecord(question="Q?", answer="A.")
        assert "T" in r.created_at  # ISO format: YYYY-MM-DDTHH:MM:SSZ

    def test_repr_contains_session_id_prefix(self) -> None:
        r = _make_record()
        assert r.session_id[:8] in repr(r)

    def test_repr_contains_verdict(self) -> None:
        r = _make_record(verdict="MEDIUM")
        assert "MEDIUM" in repr(r)


# ---------------------------------------------------------------------------
# Local backend operations
# ---------------------------------------------------------------------------

class TestLocalBackend:

    def test_put_creates_file(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            _local_put(r.session_id, r.to_json())
        assert (tmp_path / "sessions" / f"{r.session_id}.json").exists()

    def test_get_returns_json(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            _local_put(r.session_id, r.to_json())
            json_str = _local_get(r.session_id)
        data = json.loads(json_str)
        assert data["session_id"] == r.session_id

    def test_get_raises_on_missing(self, tmp_path: Path) -> None:
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            with pytest.raises(KeyError, match="not found"):
                _local_get("nonexistent-id")

    def test_list_returns_ids(self, tmp_path: Path) -> None:
        r1 = _make_record()
        r2 = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            _local_put(r1.session_id, r1.to_json())
            _local_put(r2.session_id, r2.to_json())
            ids = _local_list()
        assert r1.session_id in ids
        assert r2.session_id in ids

    def test_delete_removes_file(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            _local_put(r.session_id, r.to_json())
            _local_delete(r.session_id)
            remaining = _local_list()
        assert r.session_id not in remaining

    def test_delete_nonexistent_is_noop(self, tmp_path: Path) -> None:
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            # Should not raise
            _local_delete("does-not-exist")


# ---------------------------------------------------------------------------
# MemoryAgent — local backend (force_local=True)
# ---------------------------------------------------------------------------

class TestMemoryAgentLocal:

    def _agent(self, tmp_path: Path) -> MemoryAgent:
        """Return a MemoryAgent using local backend in tmp_path."""
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            m.ibm_cos_instance_crn = None
            agent = MemoryAgent(force_local=True)
        agent._tmp_path = tmp_path  # store for later patches
        return agent

    def test_backend_is_local(self, tmp_path: Path) -> None:
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            m.ibm_cos_instance_crn = None
            agent = MemoryAgent(force_local=True)
        assert agent.backend == "local"

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            agent.save_session(r)
            loaded = agent.load_session(r.session_id)
        assert loaded.session_id == r.session_id
        assert loaded.answer == r.answer

    def test_load_sessions_returns_all(self, tmp_path: Path) -> None:
        records = [_make_record(f"Q{i}?", f"A{i}.") for i in range(3)]
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            for r in records:
                agent.save_session(r)
            loaded = agent.load_sessions()
        assert len(loaded) == 3

    def test_load_sessions_sorted_by_date(self, tmp_path: Path) -> None:
        records = [_make_record(f"Q{i}?", f"A{i}.") for i in range(3)]
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            for r in records:
                agent.save_session(r)
            loaded = agent.load_sessions(sort_by_date=True)
        # Timestamps must be non-ascending
        dates = [r.created_at for r in loaded]
        assert dates == sorted(dates, reverse=True)

    def test_load_sessions_limit(self, tmp_path: Path) -> None:
        records = [_make_record(f"Q{i}?", f"A{i}.") for i in range(5)]
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            for r in records:
                agent.save_session(r)
            loaded = agent.load_sessions(limit=2)
        assert len(loaded) == 2

    def test_delete_removes_session(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            agent.save_session(r)
            agent.delete_session(r.session_id)
            remaining = agent.list_session_ids()
        assert r.session_id not in remaining

    def test_list_session_ids(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            agent.save_session(r)
            ids = agent.list_session_ids()
        assert r.session_id in ids

    def test_load_missing_raises_key_error(self, tmp_path: Path) -> None:
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            with pytest.raises(KeyError):
                agent.load_session("no-such-session")

    def test_save_returns_session_id(self, tmp_path: Path) -> None:
        r = _make_record()
        with patch("src.agents.memory.settings") as m:
            m.reports_dir = tmp_path
            m.ibm_cos_api_key = None
            agent = MemoryAgent(force_local=True)
            returned_id = agent.save_session(r)
        assert returned_id == r.session_id


# ---------------------------------------------------------------------------
# MemoryAgent — COS backend (fully mocked)
# ---------------------------------------------------------------------------

class TestMemoryAgentCOS:

    def _mock_cos(self) -> MagicMock:
        """Return a mock COS client."""
        return MagicMock()

    def test_backend_is_cos_when_credentials_present(self) -> None:
        with patch("src.agents.memory.settings") as m:
            m.ibm_cos_api_key = "key"
            m.ibm_cos_instance_crn = "crn"
            agent = MemoryAgent(force_local=False)
        # COS available because credentials are set
        assert agent.backend == "cos"

    def test_save_calls_cos_put(self) -> None:
        r = _make_record()
        mock_client = self._mock_cos()
        with patch("src.agents.memory._cos_client", return_value=mock_client), \
             patch("src.agents.memory._cos_available", return_value=True), \
             patch("src.agents.memory.settings") as m:
            m.ibm_cos_bucket = "test-bucket"
            m.ibm_cos_api_key = "key"
            agent = MemoryAgent(force_local=False)
            agent._use_cos = True
            agent.save_session(r)
        mock_client.put_object.assert_called_once()

    def test_load_session_calls_cos_get(self) -> None:
        r = _make_record()
        mock_client = self._mock_cos()
        mock_client.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=r.to_json().encode()))
        }
        with patch("src.agents.memory._cos_client", return_value=mock_client), \
             patch("src.agents.memory.settings") as m:
            m.ibm_cos_bucket = "test-bucket"
            agent = MemoryAgent(force_local=True)
            agent._use_cos = True
            loaded = agent.load_session(r.session_id)
        assert loaded.session_id == r.session_id

    def test_list_session_ids_calls_cos_list(self) -> None:
        mock_client = self._mock_cos()
        mock_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "sessions/abc-123.json"},
                {"Key": "sessions/def-456.json"},
            ]
        }
        with patch("src.agents.memory._cos_client", return_value=mock_client), \
             patch("src.agents.memory.settings") as m:
            m.ibm_cos_bucket = "test-bucket"
            agent = MemoryAgent(force_local=True)
            agent._use_cos = True
            ids = agent.list_session_ids()
        assert "abc-123" in ids
        assert "def-456" in ids

    def test_delete_calls_cos_delete(self) -> None:
        mock_client = self._mock_cos()
        with patch("src.agents.memory._cos_client", return_value=mock_client), \
             patch("src.agents.memory.settings") as m:
            m.ibm_cos_bucket = "test-bucket"
            agent = MemoryAgent(force_local=True)
            agent._use_cos = True
            agent.delete_session("some-id")
        mock_client.delete_object.assert_called_once()
