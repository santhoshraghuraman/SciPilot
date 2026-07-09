"""
SciPilot — Memory Agent  (src/agents/memory.py)
================================================
Persists research sessions to IBM Cloud Object Storage (primary) or to a
local JSON directory (fallback).  Provides full CRUD for session records.

Session lifecycle:
  1. Orchestrator completes a research pipeline run.
  2. Orchestrator calls ``MemoryAgent.save_session(record)``.
  3. The record is serialised to JSON and uploaded to IBM COS bucket
     ``settings.ibm_cos_bucket`` under key ``sessions/<session_id>.json``.
  4. The Dashboard calls ``MemoryAgent.load_sessions()`` to populate the
     history panel; ``MemoryAgent.load_session(id)`` to re-display a past result.

Storage backends:
  IBM COS (primary):
    - Used when ``IBM_COS_API_KEY`` is set in .env
    - Object key format: ``sessions/<session_id>.json``
    - Uses ``ibm-cos-sdk`` (ibm_boto3 + ibm_botocore)

  Local JSON (fallback):
    - Used when COS credentials are absent (dev / CI environments)
    - Files written to ``settings.reports_dir / sessions /``
    - Filenames: ``<session_id>.json``

Dependencies:
  - ibm-cos-sdk  (optional — ``pip install ibm-cos-sdk``)
  - src.utils.config  (settings)
  - src.utils.helpers (ensure_dir, sanitise_filename)
  - src.utils.logger  (get_logger)
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.config import settings
from src.utils.helpers import ensure_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)

# COS object key prefix for all session records
_COS_PREFIX = "sessions/"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SessionRecord:
    """
    Canonical representation of one completed research session.

    Attributes:
        session_id:       UUID string, auto-generated if not provided.
        question:         The original research question.
        answer:           The grounded answer from IBM Granite.
        sub_questions:    Sub-questions from the Planner Agent.
        cited_sources:    List of source file names cited in the answer.
        citation_strings: Formatted citation strings (APA / IEEE).
        citation_style:   "APA" or "IEEE".
        confidence_score: Overall verification score [0.0–1.0].
        verdict:          "HIGH", "MEDIUM", or "LOW".
        model_id:         IBM Granite model used.
        num_chunks:       Number of context chunks retrieved.
        md_report_path:   Path to the saved Markdown report (optional).
        pdf_report_path:  Path to the saved PDF report (optional).
        created_at:       ISO 8601 timestamp of session creation.
        metadata:         Any additional key-value pairs.
    """

    question: str
    answer: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sub_questions: List[str] = field(default_factory=list)
    cited_sources: List[str] = field(default_factory=list)
    citation_strings: List[str] = field(default_factory=list)
    citation_style: str = "APA"
    confidence_score: float = 0.0
    verdict: str = "LOW"
    model_id: str = ""
    num_chunks: int = 0
    md_report_path: Optional[str] = None
    pdf_report_path: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_json(self, indent: int = 2) -> str:
        """
        Serialise this record to a JSON string.

        Args:
            indent: JSON indentation (default 2 spaces).

        Returns:
            JSON string.
        """
        return json.dumps(asdict(self), indent=indent, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "SessionRecord":
        """
        Deserialise a ``SessionRecord`` from a JSON string.

        Args:
            json_str: JSON string previously produced by ``to_json()``.

        Returns:
            A ``SessionRecord`` instance.

        Raises:
            ValueError: If the JSON is missing required fields.
        """
        data = json.loads(json_str)
        # Required fields check
        for required in ("session_id", "question", "answer"):
            if required not in data:
                raise ValueError(
                    f"SessionRecord JSON missing required field: '{required}'"
                )
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def __repr__(self) -> str:
        return (
            f"SessionRecord(id={self.session_id[:8]}…, "
            f"verdict={self.verdict}, "
            f"q={self.question[:40]!r})"
        )


# ---------------------------------------------------------------------------
# IBM COS backend
# ---------------------------------------------------------------------------

def _cos_client():
    """
    Create and return an IBM COS (boto3-compatible) client.

    Returns:
        A configured ``ibm_boto3.client`` object.

    Raises:
        ImportError:  If ``ibm-cos-sdk`` is not installed.
        RuntimeError: If required COS credentials are missing.
    """
    try:
        import ibm_boto3
        from ibm_botocore.client import Config
    except ImportError as exc:
        raise ImportError(
            "ibm-cos-sdk is not installed. Run: pip install ibm-cos-sdk"
        ) from exc

    if not settings.ibm_cos_api_key or not settings.ibm_cos_instance_crn:
        raise RuntimeError(
            "IBM_COS_API_KEY and IBM_COS_INSTANCE_CRN must be set in .env"
        )

    return ibm_boto3.client(
        "s3",
        ibm_api_key_id=settings.ibm_cos_api_key,
        ibm_service_instance_id=settings.ibm_cos_instance_crn,
        config=Config(signature_version="oauth"),
        endpoint_url=settings.ibm_cos_endpoint,
    )


def _cos_available() -> bool:
    """
    Return True when IBM COS credentials are configured.

    Does NOT make a network call — only checks that the required
    settings are non-empty.
    """
    return bool(settings.ibm_cos_api_key and settings.ibm_cos_instance_crn)


# ---------------------------------------------------------------------------
# COS storage operations
# ---------------------------------------------------------------------------

def _cos_put(session_id: str, json_str: str) -> None:
    """
    Upload a session JSON to IBM COS.

    Args:
        session_id: Used as part of the object key.
        json_str:   Serialised session JSON string.
    """
    client = _cos_client()
    key = f"{_COS_PREFIX}{session_id}.json"
    client.put_object(
        Bucket=settings.ibm_cos_bucket,
        Key=key,
        Body=json_str.encode("utf-8"),
        ContentType="application/json",
    )
    logger.info("Session uploaded to COS: s3://%s/%s", settings.ibm_cos_bucket, key)


def _cos_get(session_id: str) -> str:
    """
    Download a session JSON from IBM COS.

    Args:
        session_id: The session to retrieve.

    Returns:
        JSON string for the session.

    Raises:
        KeyError: If the session does not exist in COS.
    """
    client = _cos_client()
    key = f"{_COS_PREFIX}{session_id}.json"
    try:
        response = client.get_object(Bucket=settings.ibm_cos_bucket, Key=key)
        return response["Body"].read().decode("utf-8")
    except Exception as exc:
        raise KeyError(f"Session '{session_id}' not found in COS: {exc}") from exc


def _cos_list() -> List[str]:
    """
    List all session IDs stored in IBM COS.

    Returns:
        List of session ID strings (without prefix or .json suffix).
    """
    client = _cos_client()
    response = client.list_objects_v2(
        Bucket=settings.ibm_cos_bucket,
        Prefix=_COS_PREFIX,
    )
    ids: List[str] = []
    for obj in response.get("Contents", []):
        key: str = obj["Key"]
        # Strip prefix and .json suffix
        name = key[len(_COS_PREFIX):]
        if name.endswith(".json"):
            ids.append(name[:-5])
    return ids


def _cos_delete(session_id: str) -> None:
    """
    Delete a session from IBM COS.

    Args:
        session_id: The session to delete.
    """
    client = _cos_client()
    key = f"{_COS_PREFIX}{session_id}.json"
    client.delete_object(Bucket=settings.ibm_cos_bucket, Key=key)
    logger.info("Session deleted from COS: %s", key)


# ---------------------------------------------------------------------------
# Local JSON backend
# ---------------------------------------------------------------------------

def _local_dir() -> Path:
    """Return (and create) the local sessions directory."""
    d = Path(settings.reports_dir) / "sessions"
    ensure_dir(d)
    return d


def _local_put(session_id: str, json_str: str) -> None:
    path = _local_dir() / f"{session_id}.json"
    path.write_text(json_str, encoding="utf-8")
    logger.info("Session saved locally: %s", path)


def _local_get(session_id: str) -> str:
    path = _local_dir() / f"{session_id}.json"
    if not path.exists():
        raise KeyError(f"Session '{session_id}' not found at {path}")
    return path.read_text(encoding="utf-8")


def _local_list() -> List[str]:
    return [p.stem for p in _local_dir().glob("*.json")]


def _local_delete(session_id: str) -> None:
    path = _local_dir() / f"{session_id}.json"
    if path.exists():
        path.unlink()
        logger.info("Session deleted locally: %s", path)


# ---------------------------------------------------------------------------
# Memory Agent
# ---------------------------------------------------------------------------

class MemoryAgent:
    """
    Persists and retrieves research sessions.

    Automatically uses IBM COS when credentials are configured;
    falls back to local JSON files otherwise.

    Usage:
        agent = MemoryAgent()

        # Save
        record = SessionRecord(question="...", answer="...")
        agent.save_session(record)

        # Load all
        history = agent.load_sessions()

        # Load one
        record = agent.load_session("some-uuid")

        # Delete
        agent.delete_session("some-uuid")
    """

    def __init__(self, force_local: bool = False) -> None:
        """
        Args:
            force_local: If True, always use local storage even when COS
                         credentials are present.  Useful for testing.
        """
        self._use_cos = _cos_available() and not force_local
        backend = "IBM COS" if self._use_cos else "local JSON"
        logger.info("MemoryAgent initialised (backend=%s).", backend)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_session(self, record: SessionRecord) -> str:
        """
        Persist a session record.

        Args:
            record: The ``SessionRecord`` to save.

        Returns:
            The ``session_id`` of the saved record.
        """
        json_str = record.to_json()
        if self._use_cos:
            _cos_put(record.session_id, json_str)
        else:
            _local_put(record.session_id, json_str)
        logger.info(
            "Session saved (id=%s, verdict=%s).",
            record.session_id[:8],
            record.verdict,
        )
        return record.session_id

    def load_session(self, session_id: str) -> SessionRecord:
        """
        Load a single session by ID.

        Args:
            session_id: UUID string of the session to load.

        Returns:
            The deserialised ``SessionRecord``.

        Raises:
            KeyError: If the session does not exist.
        """
        if self._use_cos:
            json_str = _cos_get(session_id)
        else:
            json_str = _local_get(session_id)
        return SessionRecord.from_json(json_str)

    def load_sessions(
        self,
        limit: Optional[int] = None,
        sort_by_date: bool = True,
    ) -> List[SessionRecord]:
        """
        Load all stored sessions.

        Args:
            limit:        Maximum number of sessions to return (most recent first
                          when ``sort_by_date=True``).
            sort_by_date: Sort sessions descending by ``created_at``.

        Returns:
            List of ``SessionRecord`` objects.
        """
        if self._use_cos:
            ids = _cos_list()
        else:
            ids = _local_list()

        records: List[SessionRecord] = []
        for sid in ids:
            try:
                if self._use_cos:
                    json_str = _cos_get(sid)
                else:
                    json_str = _local_get(sid)
                records.append(SessionRecord.from_json(json_str))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not load session '%s': %s", sid, exc)

        if sort_by_date:
            records.sort(key=lambda r: r.created_at, reverse=True)

        if limit is not None:
            records = records[:limit]

        logger.info("Loaded %d session(s).", len(records))
        return records

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session by ID.

        Args:
            session_id: UUID string of the session to delete.
        """
        if self._use_cos:
            _cos_delete(session_id)
        else:
            _local_delete(session_id)
        logger.info("Session deleted (id=%s).", session_id[:8])

    def list_session_ids(self) -> List[str]:
        """
        Return the IDs of all stored sessions without loading their content.

        Returns:
            List of session ID strings.
        """
        if self._use_cos:
            return _cos_list()
        return _local_list()

    @property
    def backend(self) -> str:
        """``'cos'`` or ``'local'`` — the active storage backend."""
        return "cos" if self._use_cos else "local"
