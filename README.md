# SciPilot 🔬
### Next-Generation Agentic Research Assistant

**IBM SkillsBuild × AICTE 2026 Project**

---

## Overview

SciPilot is a fully agentic AI research assistant built on **IBM watsonx.ai** and **IBM Granite** models. It can:

- 📄 Ingest and parse research papers (PDF)
- 🔍 Retrieve semantically relevant passages using FAISS
- 🧠 Answer research questions with grounded generation via IBM Granite
- 📝 Generate APA / IEEE citations automatically
- 📊 Produce structured Markdown and PDF research reports
- 🤖 Decompose complex questions via a Planner Agent
- ✅ Verify AI-generated claims via a Verification Agent
- 💾 Persist session memory to IBM Cloud Object Storage
- 🖥️ Expose everything through a professional Streamlit dashboard

---

## Technology Stack

| Layer | Technology |
|---|---|
| LLM / Embeddings | IBM watsonx.ai · IBM Granite |
| Vector Store | FAISS |
| PDF Parsing | PyMuPDF (fitz) |
| Orchestration | LangChain · LangFlow |
| UI | Streamlit |
| Object Storage | IBM Cloud Object Storage (ibm-cos-sdk) |
| Language | Python 3.10+ |
| IDE / Assistant | IBM BOB |

---

## Folder Structure

```
SciPilot/
├── src/
│   ├── agents/
│   │   ├── planner.py          # Decomposes research questions
│   │   ├── retriever.py        # Semantic search over FAISS
│   │   ├── synthesis.py        # IBM Granite grounded QA
│   │   ├── verification.py     # Claim verification + confidence
│   │   ├── citation.py         # APA / IEEE citation generator
│   │   ├── report.py           # Markdown / PDF report generator
│   │   └── memory.py           # Session memory → IBM COS
│   ├── rag/
│   │   ├── ingest.py           # PDF upload & text extraction
│   │   ├── chunk.py            # Text chunking strategies
│   │   ├── embed.py            # watsonx.ai embeddings
│   │   └── vector_store.py     # FAISS index management
│   ├── dashboard/
│   │   └── app.py              # Streamlit UI
│   ├── utils/
│   │   ├── config.py           # Env-driven configuration
│   │   ├── logger.py           # Structured logging
│   │   └── helpers.py          # Shared utilities
│   └── orchestrator.py         # Top-level agent orchestrator
├── research_papers/            # Uploaded PDFs (gitignored)
├── reports/                    # Generated reports (gitignored)
├── screenshots/                # UI screenshots for docs
├── docs/                       # Architecture diagrams, notes
├── tests/                      # Pytest suite
├── .env.example                # Environment variable template
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/<your-username>/SciPilot.git
cd SciPilot

# 2. Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your IBM watsonx.ai credentials

# 5. Run the dashboard
streamlit run src/dashboard/app.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `WATSONX_API_KEY` | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID |
| `WATSONX_URL` | watsonx.ai service URL |
| `IBM_COS_API_KEY` | IBM Cloud Object Storage API key |
| `IBM_COS_INSTANCE_CRN` | COS service instance CRN |
| `IBM_COS_ENDPOINT` | COS endpoint URL |
| `IBM_COS_BUCKET` | COS bucket name |
| `FAISS_INDEX_PATH` | Local path for FAISS index |
| `LOG_LEVEL` | Logging verbosity (DEBUG/INFO/WARNING) |

---

## Architecture

```
User (Streamlit UI)
        │
        ▼
  Orchestrator
  ┌─────┴──────────────────────────────────┐
  │  Planner Agent  →  Sub-questions       │
  │  Retriever      →  FAISS Top-K         │
  │  Synthesis      →  IBM Granite Answer  │
  │  Verification   →  Confidence Score    │
  │  Citation       →  APA / IEEE          │
  │  Report         →  MD / PDF            │
  │  Memory         →  IBM COS             │
  └────────────────────────────────────────┘
        │
        ▼
   RAG Pipeline
   (PDF → Chunk → Embed → FAISS)
```

---

## IBM Models Used

| Model ID | Usage |
|---|---|
| `ibm/granite-13b-instruct-v2` | Question answering, synthesis |
| `ibm/granite-13b-chat-v2` | Conversational interface |
| `ibm/slate-125m-english-rtrvr` | Embeddings (retrieval) |

---

## License

Apache 2.0 — See [LICENSE](LICENSE)

---

*Built with ❤️ using IBM watsonx.ai · IBM BOB · IBM Granite*
