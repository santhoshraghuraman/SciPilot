"""
SciPilot — Streamlit Dashboard  (src/dashboard/app.py)
========================================================
Professional multi-panel research assistant UI.

Run with:
    cd SciPilot
    streamlit run src/dashboard/app.py

Panels:
  1. Sidebar     — settings (citation style, top-k, model)
  2. Upload      — PDF ingestion into FAISS
  3. Research    — ask questions, see grounded answers + confidence
  4. Reports     — download Markdown / PDF reports
  5. History     — browse past sessions

Architecture:
  - ``st.session_state`` holds the Orchestrator singleton, VectorStore,
    and conversation history so they survive Streamlit reruns.
  - The Orchestrator is initialised once on app load.
  - PDF ingestion happens synchronously on upload (acceptable for Lite
    accounts; a background thread can be added for production).
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import List, Optional

# ── Add project root to sys.path so imports work regardless of cwd ────────────
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Seed required env vars before importing settings ─────────────────────────
from dotenv import load_dotenv
load_dotenv(_ROOT / ".env", override=True)

os.environ.setdefault("WATSONX_API_KEY", os.getenv("WATSONX_API_KEY", "not-set"))
os.environ.setdefault("WATSONX_PROJECT_ID", os.getenv("WATSONX_PROJECT_ID", "not-set"))

import streamlit as st

from src.agents.memory import MemoryAgent, SessionRecord
from src.orchestrator import Orchestrator, ResearchRequest, ResearchResponse
from src.rag.chunk import chunk_documents
from src.rag.embed import embed_chunks
from src.rag.ingest import load_pdf_from_bytes, save_uploaded_pdf
from src.rag.vector_store import VectorStore
from src.utils.config import settings
from src.utils.helpers import format_file_size
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SciPilot — AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — minimal, professional
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
    /* Main containers */
    .block-container { padding-top: 1.5rem; }

    /* Confidence badges */
    .badge-high   { background:#d1fae5; color:#065f46;
                    padding:3px 10px; border-radius:12px;
                    font-weight:600; font-size:0.82rem; }
    .badge-medium { background:#fef3c7; color:#92400e;
                    padding:3px 10px; border-radius:12px;
                    font-weight:600; font-size:0.82rem; }
    .badge-low    { background:#fee2e2; color:#991b1b;
                    padding:3px 10px; border-radius:12px;
                    font-weight:600; font-size:0.82rem; }

    /* Answer card */
    .answer-card  { background:#f8fafc; border-left:4px solid #3b82d4;
                    padding:1rem 1.25rem; border-radius:4px;
                    margin-bottom:1rem; }

    /* Section dividers */
    hr { border:none; border-top:1px solid #e5e7eb; margin:1.5rem 0; }

    /* Source table */
    .source-tag   { font-family:monospace; background:#f0f4f8;
                    padding:1px 6px; border-radius:3px;
                    font-size:0.8rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state() -> None:
    """Initialise ``st.session_state`` keys on first run."""
    defaults = {
        "orchestrator": None,
        "vector_store": None,
        "memory_agent": None,
        "chat_history": [],        # list of {"role": ..., "content": ..., "data": ...}
        "ingested_docs": [],       # list of {"name": ..., "pages": ..., "size": ...}
        "last_response": None,     # most recent ResearchResponse
        "session_history": [],     # list of SessionRecord
        "api_key_ok": False,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _get_orchestrator() -> Orchestrator:
    """Return (or create) the singleton Orchestrator."""
    if st.session_state.orchestrator is None:
        orc = Orchestrator()
        orc.load_vector_store()
        st.session_state.orchestrator = orc
        st.session_state.vector_store = orc._vector_store
    return st.session_state.orchestrator


def _get_memory() -> MemoryAgent:
    """Return (or create) the singleton MemoryAgent."""
    if st.session_state.memory_agent is None:
        st.session_state.memory_agent = MemoryAgent(force_local=True)
    return st.session_state.memory_agent


# ---------------------------------------------------------------------------
# Confidence badge helper
# ---------------------------------------------------------------------------

def _verdict_badge(verdict: str) -> str:
    cls = {
        "HIGH": "badge-high",
        "MEDIUM": "badge-medium",
        "LOW": "badge-low",
    }.get(verdict.upper(), "badge-low")
    return f'<span class="{cls}">🔒 {verdict}</span>'


# ---------------------------------------------------------------------------
# Sidebar — settings
# ---------------------------------------------------------------------------

def _render_sidebar() -> dict:
    """Render the settings sidebar and return the current config dict."""
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg",
        width=80,
    )
    st.sidebar.title("🔬 SciPilot")
    st.sidebar.caption("IBM watsonx.ai × Llama 3.3 70B")
    st.sidebar.markdown("---")

    st.sidebar.subheader("⚙️ Settings")

    citation_style = st.sidebar.selectbox(
        "Citation Style",
        ["APA", "IEEE"],
        index=0,
        help="Format for the References section.",
    )

    top_k = st.sidebar.slider(
        "Top-K Retrieval",
        min_value=1,
        max_value=15,
        value=5,
        help="Number of context passages to retrieve per sub-question.",
    )

    generate_report = st.sidebar.checkbox(
        "Generate PDF/MD Report",
        value=True,
        help="Save a Markdown and PDF report to the reports/ directory.",
    )

    st.sidebar.markdown("---")

    # IBM credentials status
    st.sidebar.subheader("🔑 IBM Credentials")
    api_key = os.getenv("WATSONX_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")

    if api_key and api_key != "not-set" and project_id and project_id != "not-set":
        st.sidebar.success("✅ watsonx.ai credentials loaded")
        st.session_state.api_key_ok = True
    else:
        st.sidebar.warning(
            "⚠️ IBM credentials not set.\n\n"
            "Copy `.env.example` → `.env` and fill in your credentials."
        )
        st.session_state.api_key_ok = False

    st.sidebar.markdown("---")

    # Index status
    vs = st.session_state.get("vector_store")
    if vs is not None:
        size = vs.size
        if size > 0:
            st.sidebar.success(f"📚 Index: {size} chunk(s) ready")
        else:
            st.sidebar.info("📭 Index empty — upload PDFs first")
    else:
        st.sidebar.info("📭 Index not loaded")

    return {
        "citation_style": citation_style,
        "top_k": top_k,
        "generate_report": generate_report,
    }


# ---------------------------------------------------------------------------
# Tab 1 — Upload & Ingest
# ---------------------------------------------------------------------------

def _render_upload_tab() -> None:
    st.header("📄 Upload Research Papers")
    st.caption(
        "Upload one or more PDF files. SciPilot will extract text, "
        "chunk it, embed it with IBM watsonx.ai, and add it to the FAISS index."
    )

    uploaded_files = st.file_uploader(
        "Drop PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        ingest_btn = st.button(
            f"⚡ Ingest {len(uploaded_files)} file(s) into FAISS",
            type="primary",
            use_container_width=True,
        )

        if ingest_btn:
            _ingest_files(uploaded_files)

    # Show already-ingested docs
    if st.session_state.ingested_docs:
        st.markdown("---")
        st.subheader("✅ Ingested Documents")
        for doc in st.session_state.ingested_docs:
            col1, col2, col3 = st.columns([4, 2, 2])
            col1.write(f"📑 **{doc['name']}**")
            col2.write(f"{doc['pages']} pages")
            col3.write(doc["size"])

    # Empty state
    if not st.session_state.ingested_docs and not uploaded_files:
        st.info(
            "👆 Upload PDF research papers to get started. "
            "The system will extract and index the content automatically."
        )


def _ingest_files(uploaded_files) -> None:
    """Process uploaded PDFs: extract → chunk → embed → add to FAISS."""
    orc = _get_orchestrator()
    vs: VectorStore = st.session_state.vector_store

    progress = st.progress(0, text="Starting ingestion …")
    total = len(uploaded_files)

    all_chunks = []
    doc_infos = []

    for i, uf in enumerate(uploaded_files):
        progress.progress(
            int(i / total * 50),
            text=f"📖 Reading {uf.name} …",
        )

        pdf_bytes = uf.read()

        # Save to disk
        try:
            save_uploaded_pdf(pdf_bytes, uf.name)
        except Exception:
            pass

        # Extract pages
        try:
            pages = load_pdf_from_bytes(pdf_bytes, filename=uf.name)
        except Exception as e:
            st.error(f"❌ Failed to read **{uf.name}**: {e}")
            continue

        # Chunk
        chunks = chunk_documents(pages)
        all_chunks.extend(chunks)

        doc_infos.append({
            "name": uf.name,
            "pages": len(pages),
            "size": format_file_size(len(pdf_bytes)),
        })

    if not all_chunks:
        st.warning("No text could be extracted from the uploaded files.")
        progress.empty()
        return

    progress.progress(55, text=f"🧠 Embedding {len(all_chunks)} chunk(s) …")

    # Check credentials before calling IBM API
    if not st.session_state.api_key_ok:
        st.error(
            "❌ IBM watsonx.ai credentials not configured. "
            "Please set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env"
        )
        progress.empty()
        return

    try:
        embeddings = embed_chunks(all_chunks)
    except Exception as e:
        st.error(f"❌ Embedding failed: {e}")
        progress.empty()
        return

    progress.progress(85, text="💾 Saving to FAISS index …")

    vs.add_chunks(all_chunks, embeddings=embeddings)

    # Persist index to disk
    try:
        vs.save()
    except Exception:
        pass

    progress.progress(100, text="✅ Ingestion complete!")

    # Update state
    st.session_state.ingested_docs.extend(doc_infos)

    st.success(
        f"✅ Ingested **{len(all_chunks)} chunk(s)** from "
        f"**{len(doc_infos)} file(s)** into FAISS. "
        f"Index now has **{vs.size} chunk(s)**."
    )
    st.rerun()


# ---------------------------------------------------------------------------
# Tab 2 — Research Chat
# ---------------------------------------------------------------------------

def _render_research_tab(cfg: dict) -> None:
    st.header("💬 Research Assistant")
    st.caption(
        "Ask a research question. SciPilot will plan, retrieve, "
        "synthesise with IBM Granite, verify, and cite."
    )

    # ── Chat history ─────────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and msg.get("data"):
                _render_answer_card(msg["data"])
            else:
                st.markdown(msg["content"])

    # ── Input ─────────────────────────────────────────────────────────────
    question = st.chat_input("Ask a research question …")

    if question:
        # Show user message
        st.session_state.chat_history.append(
            {"role": "user", "content": question, "data": None}
        )
        with st.chat_message("user"):
            st.markdown(question)

        # Guard: check credentials
        if not st.session_state.api_key_ok:
            err = (
                "⚠️ IBM watsonx.ai credentials not configured. "
                "Please copy `.env.example` → `.env` and fill in your API key."
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": err, "data": None}
            )
            with st.chat_message("assistant"):
                st.warning(err)
            return

        # Guard: check index not empty
        vs = st.session_state.get("vector_store")
        if vs is None or vs.is_empty:
            warn = "📭 No documents indexed yet. Please upload PDFs in the Upload tab first."
            st.session_state.chat_history.append(
                {"role": "assistant", "content": warn, "data": None}
            )
            with st.chat_message("assistant"):
                st.warning(warn)
            return

        # Run pipeline
        with st.chat_message("assistant"):
            with st.spinner("🔬 Researching …"):
                response = _run_pipeline(question, cfg)

            if response:
                st.session_state.last_response = response
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response.answer, "data": response}
                )
                _render_answer_card(response)


def _run_pipeline(question: str, cfg: dict) -> Optional[ResearchResponse]:
    """Execute the full Orchestrator pipeline and handle errors."""
    orc = _get_orchestrator()
    try:
        request = ResearchRequest(
            question=question,
            citation_style=cfg["citation_style"],
            generate_report=cfg["generate_report"],
            top_k=cfg["top_k"],
        )
        return orc.run(request)
    except Exception as e:
        st.error(f"❌ Pipeline error: {e}")
        logger.error("Pipeline error: %s", e, exc_info=True)
        return None


def _render_answer_card(response: ResearchResponse) -> None:
    """Render a structured answer card from a ResearchResponse."""

    # ── Confidence badge ─────────────────────────────────────────────────
    badge = _verdict_badge(response.verdict)
    score_pct = int(response.confidence * 100)
    st.markdown(
        f"{badge} &nbsp; Confidence: **{score_pct}%**",
        unsafe_allow_html=True,
    )
    st.progress(response.confidence)

    # ── Answer ────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="answer-card">{response.answer}</div>',
        unsafe_allow_html=True,
    )

    # ── Sub-questions (collapsible) ───────────────────────────────────────
    if len(response.sub_questions) > 1:
        with st.expander("🗂️ Decomposed Sub-Questions"):
            for i, sq in enumerate(response.sub_questions, 1):
                st.markdown(f"**{i}.** {sq}")

    # ── Sources table ─────────────────────────────────────────────────────
    if response.sources:
        with st.expander(f"📑 Sources Used ({len(response.sources)} chunks)"):
            cols = st.columns([1, 4, 3, 2])
            cols[0].markdown("**#**")
            cols[1].markdown("**Title**")
            cols[2].markdown("**File**")
            cols[3].markdown("**Page**")
            for i, src in enumerate(response.sources[:10], 1):
                c1, c2, c3, c4 = st.columns([1, 4, 3, 2])
                c1.write(str(i))
                c2.write(str(src.get("title", "—"))[:50])
                c3.markdown(
                    f'<span class="source-tag">{src.get("source", "—")}</span>',
                    unsafe_allow_html=True,
                )
                c4.write(str(src.get("page", "—")))


# ---------------------------------------------------------------------------
# Tab 3 — Verification Details
# ---------------------------------------------------------------------------

def _render_verification_tab() -> None:
    st.header("🔬 Verification Details")

    response: Optional[ResearchResponse] = st.session_state.get("last_response")

    if response is None:
        st.info("Ask a research question first to see verification details.")
        return

    # Overall score
    verdict = response.verdict
    score = response.confidence
    badge = _verdict_badge(verdict)

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", f"{score:.0%}")
    col2.metric("Verdict", verdict)
    col3.metric("Citations Found", str(len(response.citations)))

    st.markdown(
        f"**Confidence:** {badge} — {score:.0%}",
        unsafe_allow_html=True,
    )
    st.progress(score)
    st.markdown("---")

    # Per-check breakdown
    st.subheader("Check Breakdown")
    st.caption(
        "Four independent quality checks are combined with weighted scoring "
        "to produce the overall confidence score."
    )

    check_info = {
        "citation_coverage": {
            "label": "📌 Citation Coverage",
            "weight": "35%",
            "desc": "Are all inline [N] markers backed by real context passages?",
        },
        "grounding_ratio": {
            "label": "🔗 Grounding Ratio",
            "weight": "35%",
            "desc": "What fraction of answer sentences share vocabulary with the context?",
        },
        "answer_quality": {
            "label": "📏 Answer Quality",
            "weight": "15%",
            "desc": "Is the answer a reasonable length (20–600 words)?",
        },
        "source_diversity": {
            "label": "📚 Source Diversity",
            "weight": "15%",
            "desc": "Does the answer draw from multiple distinct documents?",
        },
    }

    # Rebuild check scores from metadata
    checks = response.metadata.get("verification_checks", {})
    for name, info in check_info.items():
        check_score = checks.get(name, 0.0)
        with st.expander(
            f"{info['label']} — {check_score:.0%}  (weight {info['weight']})"
        ):
            st.caption(info["desc"])
            st.progress(check_score)
            color = (
                "green" if check_score >= 0.7
                else "orange" if check_score >= 0.4
                else "red"
            )
            st.markdown(
                f"Score: **:{color}[{check_score:.2f}]**",
            )


# ---------------------------------------------------------------------------
# Tab 4 — Citations & Reports
# ---------------------------------------------------------------------------

def _render_reports_tab() -> None:
    st.header("📚 Citations & Reports")

    response: Optional[ResearchResponse] = st.session_state.get("last_response")

    if response is None:
        st.info("Ask a research question first to generate citations and a report.")
        return

    # ── Citations ─────────────────────────────────────────────────────────
    st.subheader("References")
    if response.citations:
        for cite in response.citations:
            st.markdown(f"- {cite}")
    else:
        st.info("No citations were generated for this answer.")

    st.markdown("---")

    # ── Report downloads ──────────────────────────────────────────────────
    st.subheader("Download Report")

    col1, col2 = st.columns(2)

    # Markdown download
    if response.report_md_path and Path(response.report_md_path).exists():
        md_content = Path(response.report_md_path).read_text(encoding="utf-8")
        col1.download_button(
            label="⬇️ Download Markdown",
            data=md_content,
            file_name=Path(response.report_md_path).name,
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        col1.button(
            "📄 Markdown (not saved)",
            disabled=True,
            use_container_width=True,
        )

    # PDF download
    if response.report_pdf_path and Path(response.report_pdf_path).exists():
        pdf_bytes = Path(response.report_pdf_path).read_bytes()
        col2.download_button(
            label="⬇️ Download PDF",
            data=pdf_bytes,
            file_name=Path(response.report_pdf_path).name,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        col2.button(
            "📕 PDF (not saved)",
            disabled=True,
            use_container_width=True,
        )

    # ── Inline Markdown preview ───────────────────────────────────────────
    if response.report_md_path and Path(response.report_md_path).exists():
        with st.expander("👁️ Preview Report"):
            md_content = Path(response.report_md_path).read_text(encoding="utf-8")
            st.markdown(md_content)


# ---------------------------------------------------------------------------
# Tab 5 — Session History
# ---------------------------------------------------------------------------

def _render_history_tab() -> None:
    st.header("🕒 Session History")
    st.caption("Previous research sessions saved by the Memory Agent.")

    mem = _get_memory()

    col_refresh, col_clear = st.columns([2, 1])
    if col_refresh.button("🔄 Refresh History", use_container_width=True):
        st.session_state.session_history = mem.load_sessions(limit=20)

    # Load on first visit
    if not st.session_state.session_history:
        st.session_state.session_history = mem.load_sessions(limit=20)

    sessions: List[SessionRecord] = st.session_state.session_history

    if not sessions:
        st.info("No past sessions found. Run a research query to create one.")
        return

    st.markdown(f"**{len(sessions)} session(s) found.**")
    st.markdown("---")

    for rec in sessions:
        verdict_color = {
            "HIGH": "🟢",
            "MEDIUM": "🟡",
            "LOW": "🔴",
        }.get(rec.verdict, "⚪")

        with st.expander(
            f"{verdict_color} {rec.created_at[:10]}  —  "
            f"{rec.question[:70]}{'…' if len(rec.question) > 70 else ''}"
        ):
            col1, col2, col3 = st.columns(3)
            col1.metric("Confidence", f"{rec.confidence_score:.0%}")
            col2.metric("Verdict", rec.verdict)
            col3.metric("Chunks", str(rec.num_chunks))

            st.markdown("**Question:**")
            st.markdown(f"> {rec.question}")

            st.markdown("**Answer:**")
            st.markdown(
                f'<div class="answer-card">{rec.answer}</div>',
                unsafe_allow_html=True,
            )

            if rec.citation_strings:
                with st.expander("📚 References"):
                    for cite in rec.citation_strings:
                        st.markdown(f"- {cite}")

            # Delete button
            if st.button(
                f"🗑️ Delete session",
                key=f"del_{rec.session_id}",
            ):
                mem.delete_session(rec.session_id)
                st.session_state.session_history = mem.load_sessions(limit=20)
                st.rerun()


# ---------------------------------------------------------------------------
# Main app entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Render the full SciPilot Dashboard."""
    _init_state()

    # Sidebar
    cfg = _render_sidebar()

    # Header
    st.title("🔬 SciPilot")
    st.markdown(
        "**Agentic Research Assistant** — "
        "Powered by IBM watsonx.ai · Llama 3.3 70B · FAISS · LangChain"
    )
    st.markdown("---")

    # Tabs
    tab_upload, tab_research, tab_verify, tab_reports, tab_history = st.tabs([
        "📄 Upload",
        "💬 Research",
        "🔬 Verification",
        "📚 Reports",
        "🕒 History",
    ])

    with tab_upload:
        _render_upload_tab()

    with tab_research:
        _render_research_tab(cfg)

    with tab_verify:
        _render_verification_tab()

    with tab_reports:
        _render_reports_tab()

    with tab_history:
        _render_history_tab()

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#57606a;font-size:0.8rem;'>"
        "SciPilot v1.0.0 · IBM SkillsBuild × AICTE 2026 · "
        "Built with IBM watsonx.ai, Llama 3.3 70B, FAISS, Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
