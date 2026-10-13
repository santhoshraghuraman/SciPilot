"""
SciPilot — Centralised Configuration
=====================================
Reads all settings from environment variables (loaded from .env).
Every module imports `settings` from this file — no magic strings elsewhere.

Why:
    - Single source of truth for all config values.
    - Changing a credential or path requires editing ONE file (.env).
    - Pydantic BaseSettings validates types at startup, catching mistakes early.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Load .env file from the project root (two levels up from this file)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """
    All application settings with defaults and validation.

    Pydantic-settings reads each field from the matching environment variable.
    The variable name is the uppercased field name (e.g. ``app_name`` → APP_NAME).
    If a required variable is missing at startup it raises a clear error.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = Field(default="SciPilot", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ── IBM watsonx.ai ────────────────────────────────────────────────────────
    watsonx_api_key: str = Field(default="not-set", alias="WATSONX_API_KEY")
    watsonx_project_id: str = Field(default="not-set", alias="WATSONX_PROJECT_ID")
    watsonx_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        alias="WATSONX_URL",
    )

    # ── IBM Granite Model IDs ─────────────────────────────────────────────────
    granite_instruct_model: str = Field(
        default="ibm/granite-13b-instruct-v2",
        alias="GRANITE_INSTRUCT_MODEL",
    )
    granite_chat_model: str = Field(
        default="ibm/granite-13b-chat-v2",
        alias="GRANITE_CHAT_MODEL",
    )
    granite_embed_model: str = Field(
        default="ibm/slate-125m-english-rtrvr",
        alias="GRANITE_EMBED_MODEL",
    )

    # ── IBM Cloud Object Storage ───────────────────────────────────────────────
    ibm_cos_api_key: Optional[str] = Field(default=None, alias="IBM_COS_API_KEY")
    ibm_cos_instance_crn: Optional[str] = Field(
        default=None, alias="IBM_COS_INSTANCE_CRN"
    )
    ibm_cos_endpoint: str = Field(
        default="https://s3.us-south.cloud-object-storage.appdomain.cloud",
        alias="IBM_COS_ENDPOINT",
    )
    ibm_cos_bucket: str = Field(default="scipilot-memory", alias="IBM_COS_BUCKET")

    # ── Local Paths ───────────────────────────────────────────────────────────
    faiss_index_path: Path = Field(
        default=Path("./data/faiss_index"),
        alias="FAISS_INDEX_PATH",
    )
    papers_dir: Path = Field(
        default=Path("./research_papers"),
        alias="PAPERS_DIR",
    )
    reports_dir: Path = Field(
        default=Path("./reports"),
        alias="REPORTS_DIR",
    )

    # ── RAG Settings ──────────────────────────────────────────────────────────
    chunk_size: int = Field(default=512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=64, alias="CHUNK_OVERLAP")
    top_k_retrieval: int = Field(default=5, alias="TOP_K_RETRIEVAL")

    # ── LLM Generation ────────────────────────────────────────────────────────
    max_new_tokens: int = Field(default=1024, alias="MAX_NEW_TOKENS")
    temperature: float = Field(default=0.2, alias="TEMPERATURE")
    top_p: float = Field(default=0.9, alias="TOP_P")
    repetition_penalty: float = Field(default=1.1, alias="REPETITION_PENALTY")

    def ensure_directories(self) -> None:
        """
        Create required local directories if they do not exist.
        Called once at application startup by orchestrator.py.
        """
        for directory in [
            self.faiss_index_path.parent,
            self.papers_dir,
            self.reports_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Singleton — import `settings` everywhere instead of instantiating locally
# ---------------------------------------------------------------------------
settings = Settings()
