# SciPilot 🔬
### Autonomous Multi-Agent AI Research Assistant for Scientific Literature

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![IBM watsonx.ai](https://img.shields.io/badge/AI-IBM%20watsonx.ai-054ADA.svg)](https://www.ibm.com/watsonx)
[![Tests: 378 Passed](https://img.shields.io/badge/Tests-378%20Passed-brightgreen.svg)](https://pytest.org/)

**IBM SkillsBuild × AICTE Internship 2026**  
**Author:** Santhosh R (Reg. No: 22MIS0282)  
**Institution:** Vellore Institute of Technology (VIT), Vellore  
**Repository:** [https://github.com/santhoshraghuraman/SciPilot](https://github.com/santhoshraghuraman/SciPilot)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement & Objectives](#problem-statement--objectives)
3. [Key Features](#key-features)
4. [Live IBM Mode vs. Local Demo Mode](#live-ibm-mode-vs-local-demo-mode)
5. [System Architecture](#system-architecture)
6. [Technology Stack](#technology-stack)
7. [Repository Structure](#repository-structure)
8. [Prerequisites](#prerequisites)
9. [Installation & Setup (Windows PowerShell)](#installation--setup-windows-powershell)
10. [Configuration & Environment Variables](#configuration--environment-variables)
11. [Running the Application](#running-the-application)
12. [User Guide & Workflow Walkthrough](#user-guide--workflow-walkthrough)
13. [Running Automated Tests](#running-automated-tests)
14. [Troubleshooting Common Issues](#troubleshooting-common-issues)
15. [Security & Credential Handling](#security--credential-handling)
16. [Current Limitations & Future Enhancements](#current-limitations--future-enhancements)
17. [Project Credits](#project-credits)

---

## Project Overview

**SciPilot** is an agentic Retrieval-Augmented Generation (RAG) platform designed to accelerate scientific inquiry across academic papers. Built using Python, Streamlit, FAISS, and IBM watsonx.ai enterprise services, SciPilot moves beyond traditional single-prompt question-answering by coordinating seven specialized autonomous agents:

- **Planning**: Breaks compound scientific questions into manageable sub-queries.
- **Retrieval & Diversification**: Searches dense vector indices and applies Maximal Marginal Relevance (MMR) to prevent redundant context.
- **Synthesis**: Combines evidence into structured scientific answers with exact citation markers.
- **Verification**: Mathematically verifies factual grounding against retrieved source chunks to suppress hallucinations.
- **Citation**: Formats references into standardized academic citation formats (APA / IEEE).
- **Report Generation**: Compiles publication-ready Markdown and PDF summaries.
- **Session Memory**: Persists conversation context and research history across sessions.

SciPilot provides full operational duality: an enterprise **Live IBM watsonx.ai Mode** powered by IBM Slate embeddings and IBM Granite 13B models, and an offline **Local Demo Mode** that allows complete pipeline inspection and academic viva demonstration without external cloud credentials.

---

## Problem Statement & Objectives

### The Problem
Researchers, graduate students, and software engineers spend hours navigating dense academic literature. Standard commercial large language models suffer from:
1. **Hallucination Risk**: Unverifiable claims made without traceable references to specific PDF pages.
2. **Context Blindness**: Missing multi-hop dependencies across lengthy scientific papers.
3. **Rigid Formatting**: Lack of ready-to-use bibliographies (APA/IEEE) and archival research reports.
4. **Cloud Brittleness**: Inability to demonstrate or evaluate application mechanics when external API limits, quota restrictions, or network interruptions occur.

### Project Objectives
- Build a modular, verifiable 7-agent RAG workflow tailored to research papers.
- Integrate IBM watsonx.ai foundation models (`ibm/granite-13b-instruct-v2` and `ibm/slate-125m-english-rtrvr`).
- Implement rigorous quantitative verification (grounding ratios, citation coverage, source diversity).
- Support automatic export of structured Markdown and PDF reports.
- Implement an offline fallback (Local Demo Mode) with consistent vector dimensions for educational and viva evaluation.
- Achieve 100% automated test coverage across core agent contracts.

---

## Key Features

- **📑 Multi-Document PDF Ingestion**: High-throughput PDF extraction via PyMuPDF (`fitz`), maintaining page-level provenance and SHA-256 document hashing.
- **🧩 Semantic Chunking**: Sliding window text chunking (512 characters, 64-character overlap) preserving sentence and paragraph continuity.
- **⚡ High-Performance Vector Retrieval**: In-memory and disk-persisted FAISS `IndexFlatIP` vector index with normalized cosine similarity search.
- **🔀 MMR Diversification**: Maximal Marginal Relevance algorithm ($\lambda=0.7$) balancing semantic relevance with informational diversity.
- **🤖 Autonomous Multi-Agent Pipeline**: Dedicated Python agents orchestrated through [`src/orchestrator.py`](file:///c:/Users/91959/Documents/SciPilot-main/src/orchestrator.py).
- **🛡️ Quantitative Hallucination Guardrails**: Deterministic claim verification calculating:
  - *Citation Coverage*: Ratio of generated assertions linked to source chunks.
  - *Grounding Ratio*: N-gram overlap between generated text and source context.
  - *Confidence Verdicts*: Transparent `HIGH` ($\ge 0.70$), `MEDIUM` ($0.40–0.69$), or `LOW` ($< 0.40$) ratings.
- **📚 Academic Citation Formatting**: Instant toggling between **APA 7th Edition** and **IEEE** referencing styles.
- **📄 Dual-Format Report Export**: Dynamic generation of publication-ready Markdown and standalone PDF reports with metadata and tables.
- **💾 Hybrid Persistence**: Research history logged to IBM Cloud Object Storage (COS) in live mode or local JSON records in offline mode.
- **🧪 Local Demo Mode**: Zero-cloud-dependency demonstration with scikit-learn hashing vectors and extractive synthesis.

---

## Live IBM Mode vs. Local Demo Mode

SciPilot maintains a clean separation between live IBM cloud features and offline fallbacks:

| Feature / Pipeline Stage | Live IBM watsonx.ai Mode | Offline Local Demo Mode |
|---|---|---|
| **Embeddings** | IBM watsonx.ai `ibm/slate-125m-english-rtrvr` (384-dimensional dense semantic vectors) | scikit-learn `HashingVectorizer` (384-dimensional normalized hash vectors) |
| **Question Planning** | IBM Granite 13B Instruct LLM decomposition into 2–5 sub-questions | Deterministic rule-based decomposition / original question |
| **Answer Generation** | IBM Granite 13B generative synthesis with grounded prompt templates | Local extractive synthesis (relevant passage selection with citations) |
| **Verification Engine** | Grounding ratio + citation coverage validation | Identical deterministic verification engine |
| **Citations (APA / IEEE)** | Full academic bibliography generation | Full academic bibliography generation |
| **Report Export** | Markdown & PDF generation (`fpdf2`) | Markdown & PDF generation (`fpdf2`) |
| **Session Memory** | IBM Cloud Object Storage (S3 API via `ibm-cos-sdk`) | Local file storage in `reports/sessions/*.json` |
| **API Credentials** | Requires valid `WATSONX_API_KEY` & `WATSONX_PROJECT_ID` | **No external credentials required** |

> [!NOTE]
> Local Demo Mode is explicitly labelled throughout the dashboard and code. Hashing vectors are lightweight bag-of-words approximations and should never be represented as IBM Slate semantic embeddings; extractive passages should not be described as generative IBM Granite output.

---

## System Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │               Streamlit Web Interface                  │
                    │               (src/dashboard/app.py)                   │
                    └──────────────────────────┬─────────────────────────────┘
                                               │
                                 User Ingestion / Query
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SciPilot Orchestrator                                         │
│                              (src/orchestrator.py)                                         │
│                                                                                            │
│   ┌─────────────────────┐       ┌──────────────────────┐       ┌───────────────────────┐   │
│   │   1. PlannerAgent   │ ────► │  2. RetrieverAgent   │ ────► │  3. SynthesisAgent    │   │
│   │  (Decompose Query)  │       │   (FAISS + MMR Search│       │ (IBM Granite / Local) │   │
│   └─────────────────────┘       └──────────────────────┘       └───────────┬───────────┘   │
│                                                                            │               │
│   ┌─────────────────────┐       ┌──────────────────────┐       ┌───────────▼───────────┐   │
│   │   6. MemoryAgent    │ ◄──── │   5. ReportAgent     │ ◄──── │ 4. VerificationAgent  │   │
│   │ (IBM COS / Local)   │       │   (PDF / Markdown)   │       │  (Grounding & Scores) │   │
│   └─────────────────────┘       └──────────────────────┘       └───────────────────────┘   │
│              ▲                                                             ▲               │
│              │                                                             │               │
│              └─────────────────────── CitationAgent ───────────────────────┘               │
│                                      (APA / IEEE)                                          │
└──────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 RAG Ingestion Pipeline                                     │
│                                                                                            │
│     PDF Files ──► PyMuPDF Extraction ──► Chunking (512/64) ──► Embeddings (384-dim)        │
│                                                                      │                     │
│                                                                      ▼                     │
│                                                            FAISS Vector Store              │
│                                                          (IndexFlatIP Cosine)              │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

- **Core Language**: Python 3.10+ (tested on Python 3.14 on Windows 11)
- **Foundation LLMs & Cloud AI**:
  - `ibm/granite-13b-instruct-v2`: Query planning and grounded generative answering
  - `ibm/slate-125m-english-rtrvr`: Dense text embeddings (384 dimensions)
  - `ibm-watsonx-ai`: Official IBM Watson Python SDK
  - `ibm-cos-sdk`: IBM Cloud Object Storage SDK (S3-compatible API)
- **Vector Indexing**:
  - `faiss-cpu`: Meta FAISS library for high-speed inner-product similarity search
- **Local Fallback Engine**:
  - `scikit-learn`: `HashingVectorizer` producing matching 384-dimensional dense vectors
- **Document Processing**:
  - `PyMuPDF` (`fitz`): High-accuracy text and metadata extraction from PDF files
  - `fpdf2`: Pure-Python PDF generation for academic reports
  - `markdown`: Markdown parser and renderer
- **Web Application**:
  - `streamlit`: Interactive dashboard with multi-tab layout and session caching
- **Testing & Quality Assurance**:
  - `pytest`: Complete test framework (378 passing unit and integration tests)
  - `tenacity`: Exponential backoff and retry handling for remote API interactions
  - `python-dotenv`: Environment variable management

---

## Repository Structure

```
SciPilot/
├── src/
│   ├── agents/
│   │   ├── citation.py          # Formats references into APA / IEEE bibliographies
│   │   ├── memory.py            # Session state persistence (IBM COS or local JSON)
│   │   ├── planner.py           # Breaks complex queries into research sub-questions
│   │   ├── report.py            # Generates archival Markdown and PDF research reports
│   │   ├── retriever.py         # FAISS vector retrieval with MMR diversification
│   │   ├── synthesis.py         # Generates grounded answers (IBM Granite / local fallback)
│   │   └── verification.py      # Quantitative hallucination and grounding scoring
│   ├── dashboard/
│   │   └── app.py               # Streamlit web application (5 interactive tabs)
│   ├── rag/
│   │   ├── chunk.py             # Character and token-based sliding window chunking
│   │   ├── embed.py             # Embedding generator (IBM Slate / Local HashingVectorizer)
│   │   ├── ingest.py            # PDF loading, deduplication (SHA-256), and text extraction
│   │   └── vector_store.py      # FAISS IndexFlatIP management and disk persistence
│   ├── utils/
│   │   ├── config.py            # Centralized Pydantic/dataclass configuration singleton
│   │   ├── helpers.py           # Text hashing, formatting, and file utilities
│   │   └── logger.py            # Structured logging across all components
│   └── orchestrator.py          # Coordinates 7 agents into an end-to-end pipeline
├── tests/                       # Complete pytest suite (378 tests)
│   ├── test_chunk.py
│   ├── test_citation.py
│   ├── test_config.py
│   ├── test_embed.py
│   ├── test_ingest.py
│   ├── test_memory.py
│   ├── test_planner.py
│   ├── test_report.py
│   ├── test_retriever.py
│   ├── test_synthesis.py
│   ├── test_vector_store.py
│   └── test_verification.py
├── docs/
│   ├── USER_MANUAL.md           # Step-by-step user guide for first-time users
│   └── project_report/          # Comprehensive academic reports and viva preparation notes
├── research_papers/             # Local PDF papers for ingestion (gitignored)
├── reports/                     # Output directory for exported MD/PDF reports (gitignored)
├── data/                        # Persistent FAISS index files (gitignored)
├── .env.example                 # Safe configuration template with placeholder keys
├── .gitignore                   # Excludes secrets, FAISS caches, virtualenvs, reports
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## Prerequisites

- **Operating System**: Windows 10/11, macOS, or Linux.
- **Python**: Version 3.10, 3.11, 3.12, 3.13, or 3.14.
- **Memory**: Minimum 4 GB RAM (8 GB recommended).
- **Disk Space**: At least 500 MB free space for dependencies and vector indexes.

---

## Installation & Setup (Windows PowerShell)

Open Windows PowerShell and run the following commands sequentially:

```powershell
# 1. Clone the repository
git clone https://github.com/santhoshraghuraman/SciPilot.git
cd SciPilot

# 2. Verify Python installation
python --version

# 3. Create a dedicated Python virtual environment
python -m venv venv

# 4. Activate the virtual environment
# Note: If script execution is restricted, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# 5. Upgrade pip to the latest release
python -m pip install --upgrade pip

# 6. Install all project dependencies
pip install -r requirements.txt
```

---

## Configuration & Environment Variables

Copy the provided `.env.example` template to `.env`:

```powershell
Copy-Item .env.example .env
```

### Option A: Running in Local Demo Mode (No Credentials Needed)
If you do not have active IBM Cloud API credentials, leave the `.env` file as default with placeholder strings:
```ini
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```
SciPilot automatically detects these placeholder patterns and starts in **Local Demo Mode**, activating the local vectorizer and extractive answering without errors.

### Option B: Running in Live IBM watsonx.ai Mode
To connect to live IBM Cloud services, open `.env` in a text editor (e.g. `notepad .env`) and supply your active IBM Cloud credentials:

```ini
# ── IBM watsonx.ai ───────────────────────────────────────────────────────────
WATSONX_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# ── IBM Foundation Models ─────────────────────────────────────────────────────
GRANITE_INSTRUCT_MODEL=ibm/granite-13b-instruct-v2
GRANITE_CHAT_MODEL=ibm/granite-13b-chat-v2
GRANITE_EMBED_MODEL=ibm/slate-125m-english-rtrvr

# ── IBM Cloud Object Storage (Optional) ───────────────────────────────────────
IBM_COS_API_KEY=your_actual_cos_api_key
IBM_COS_INSTANCE_CRN=your_actual_cos_instance_crn
IBM_COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
IBM_COS_BUCKET=scipilot-memory
```

---

## Running the Application

Ensure your virtual environment is active, then launch the Streamlit dashboard:

```powershell
python -m streamlit run src/dashboard/app.py
```

Once initialized, open your web browser and navigate to:
```
http://localhost:8501
```

To stop the Streamlit server at any time, press `Ctrl + C` in the PowerShell terminal.

---

## User Guide & Workflow Walkthrough

For complete, screenshot-annotated instructions, consult the [SciPilot User Manual](docs/USER_MANUAL.md).

### 1. Ingesting Research Papers (Tab 1: "📄 Upload Research Papers")
1. Drag and drop one or more PDF research papers into the upload box.
2. Click **⚡ Ingest 1 file(s) into FAISS**.
3. SciPilot extracts page text, creates sliding-window chunks, generates 384-dimensional embeddings, and saves the index to `data/faiss_index.index`.
4. A success banner will confirm: `✅ Ingested X chunk(s) from 1 file(s) into FAISS`.

### 2. Asking Research Questions (Tab 2: "💬 Research Assistant")
1. Navigate to the **Research Assistant** tab.
2. In the input box at the bottom, type your scientific inquiry (e.g., *"What are the key security concerns in MCP multi-agent systems?"*).
3. The pipeline will:
   - Decompose your question via the **Planner Agent**.
   - Retrieve relevant chunks via the **Retriever Agent** using FAISS and MMR.
   - Synthesise a grounded answer with inline citations (`[1]`, `[2]`).
   - Display a **Confidence Score** progress bar and collapsible lists of sub-questions and sources.

### 3. Reviewing Verification Metrics (Tab 3: "📊 Evaluation & Verification")
- Review quantitative hallucination guardrail metrics:
  - **Verdict**: `HIGH`, `MEDIUM`, or `LOW`.
  - **Overall Confidence Score**: Aggregate reliability percentage.
  - **Citation Coverage**: Proportion of assertions grounded in source citations.
  - **Grounding Ratio**: N-gram semantic alignment against context chunks.
  - **Source Diversity**: Spread of source chunks across pages and documents.

### 4. Exporting Reports (Tab 4: "📝 Export Report")
- Preview the structured scientific synthesis report.
- Download the generated report as **Markdown (`.md`)** or **PDF (`.pdf`)** containing formatted answers, sources tables, and bibliographies.

### 5. Reviewing Session History (Tab 5: "💾 Sessions")
- Inspect past research queries, confidence scores, and timestamps.
- Sessions are saved in IBM Cloud Object Storage or locally under `reports/sessions/`.

---

## Running Automated Tests

SciPilot includes an extensive test suite verifying every component, agent contract, and edge case.

Execute the full test suite with:

```powershell
python -m pytest tests/ -v
```

To run tests with a compact summary:

```powershell
python -m pytest tests/ -q
```

### Verified Test Results
```
tests/test_chunk.py ........ (32 passed)
tests/test_citation.py ..... (51 passed)
tests/test_config.py ....... (14 passed)
tests/test_embed.py ........ (11 passed)
tests/test_ingest.py ....... (26 passed)
tests/test_memory.py ....... (32 passed)
tests/test_planner.py ...... (35 passed)
tests/test_report.py ....... (35 passed)
tests/test_retriever.py .... (29 passed)
tests/test_synthesis.py .... (38 passed)
tests/test_vector_store.py . (22 passed)
tests/test_verification.py . (53 passed)
============================ 378 passed in 10.17s ============================
```

---

## Troubleshooting Common Issues

### 1. `BXNIM0415E: Provided API key could not be found`
- **Cause**: An invalid or placeholder IBM Cloud API key was used in live mode.
- **Solution**: Switch to **Local Demo Mode** using the sidebar toggle, or provide a valid IBM Cloud API key in `.env`.

### 2. `ExecutionPolicy` Restriction in PowerShell
- **Symptom**: `cannot be loaded because running scripts is disabled on this system`.
- **Solution**: Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window before activating `venv`.

### 3. `ModuleNotFoundError: No module named 'sklearn'`
- **Cause**: The virtual environment is missing scikit-learn.
- **Solution**: Run `pip install scikit-learn` or reinstall dependencies with `pip install -r requirements.txt`.

### 4. FAISS Dimension Mismatch Error
- **Symptom**: `Index dimension 384 does not match query dimension ...`
- **Solution**: Delete old index files (`Remove-Item data/faiss_index.*`) and re-ingest your papers. Both IBM Slate and Local Demo Mode are standardized to 384 dimensions.

---

## Security & Credential Handling

- **Never Commit Secrets**: The `.env` file is explicitly ignored in `.gitignore`.
- **Placeholder Detection**: The application automatically inspects credentials and will refuse to send placeholder strings to external IBM endpoints.
- **Local Isolation**: Uploaded research papers, generated reports, and FAISS index files remain strictly on your local machine unless IBM COS is explicitly configured.

---

## Current Limitations & Future Enhancements

### Current Limitations
1. **Local Mode Answer Synthesis**: In Local Demo Mode, answers are extractive concatenations rather than generative text. Generative reasoning requires an active IBM Granite API key.
2. **Tabular Data in PDFs**: Complex multi-column scientific tables and embedded figures are parsed as linear text by PyMuPDF.
3. **In-Memory Scale**: The local FAISS index operates in memory; indexing hundreds of large textbooks may require chunk pruning or sharding.

### Future Enhancements
- Integration of local quantized models (e.g. GGUF / Ollama) for offline generative reasoning.
- Support for multimodal ingestion (OCR on diagrams, charts, and chemical formulas).
- Hybrid search combining BM25 keyword matching with dense vector similarity.
- Docker containerization for one-click cross-platform deployment.

---

## Project Credits

- **Developer**: Santhosh R
- **Registration Number**: 22MIS0282
- **Degree Program**: Integrated M.Tech. Software Engineering (5 Years)
- **Institution**: School of Information Technology and Engineering (SITE), Vellore Institute of Technology (VIT), Vellore, Tamil Nadu, India
- **Internship**: IBM SkillsBuild × AICTE Internship 2026
- **Mentor / Support**: Edunet Foundation & IBM Academic Initiative

---
*Developed with IBM watsonx.ai, IBM Granite Models, and Open-Source Python Technologies.*
