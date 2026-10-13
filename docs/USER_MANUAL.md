# SciPilot — Complete User Manual 📖
### Step-by-Step Operator Guide for Researchers, Students & Evaluators

**Author:** Santhosh R (Reg. No: 22MIS0282)  
**Project:** SciPilot — Autonomous Multi-Agent AI Research Assistant  
**Internship:** IBM SkillsBuild × AICTE Internship 2026  
**Repository:** [https://github.com/santhoshraghuraman/SciPilot](https://github.com/santhoshraghuraman/SciPilot)

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Hardware & Software Prerequisites](#2-hardware--software-prerequisites)
3. [First-Time Installation (Windows PowerShell)](#3-first-time-installation-windows-powershell)
4. [Operational Modes: Live IBM Mode vs. Local Demo Mode](#4-operational-modes-live-ibm-mode-vs-local-demo-mode)
5. [Configuration & Credentials (.env Setup)](#5-configuration--credentials-env-setup)
6. [Starting and Stopping SciPilot](#6-starting-and-stopping-scipilot)
7. [Navigating the User Interface](#7-navigating-the-user-interface)
   - [Sidebar Controls](#sidebar-controls)
   - [Tab 1: Upload & Ingest Research Papers](#tab-1-upload--ingest-research-papers)
   - [Tab 2: Research Assistant (Querying)](#tab-2-research-assistant-querying)
   - [Tab 3: Evaluation & Verification](#tab-3-evaluation--verification)
   - [Tab 4: Export Reports](#tab-4-export-reports)
   - [Tab 5: Session History](#tab-5-session-history)
8. [Understanding Verification Scores & Badges](#8-understanding-verification-scores--badges)
9. [Running the Test Suite](#9-running-the-test-suite)
10. [Troubleshooting & FAQs](#10-troubleshooting--faqs)

---

## 1. Introduction

Welcome to **SciPilot**. SciPilot is an autonomous multi-agent research assistant designed to parse, index, search, and answer complex scientific questions across research papers (PDF format). 

Whether you are evaluating SciPilot for an academic viva, an industrial internship review, or personal research, this manual walks you through every step from an empty terminal to a fully running, verified application.

---

## 2. Hardware & Software Prerequisites

Before installing SciPilot, confirm your system meets these requirements:

- **Operating System**: Windows 10 or Windows 11 (64-bit).
- **Python**: Python 3.10 to 3.14 installed.
  - Check in PowerShell: `python --version`
  - Ensure **"Add Python to PATH"** was checked during Python installation.
- **RAM**: Minimum 4 GB RAM (8 GB recommended).
- **Internet Connection**:
  - Required for initial `pip install` dependency download.
  - Required for Live IBM Mode (connecting to IBM Cloud endpoints).
  - *Not required* for running the application in Local Demo Mode once dependencies are installed.

---

## 3. First-Time Installation (Windows PowerShell)

Follow these step-by-step commands in **Windows PowerShell**:

### Step 3.1: Open PowerShell
Press `Win + X` and select **Terminal** or **Windows PowerShell**.

### Step 3.2: Navigate to or Clone the Repository
```powershell
# Clone the repository from GitHub
git clone https://github.com/santhoshraghuraman/SciPilot.git
cd SciPilot
```

### Step 3.3: Set PowerShell Execution Policy (If Needed)
If you have never run Python virtual environments in PowerShell before, enable script execution:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Step 3.4: Create and Activate a Virtual Environment
```powershell
# Create a fresh virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```
*When activated, your prompt will show `(venv)` at the beginning of the line.*

### Step 3.5: Install Dependencies
```powershell
# Upgrade pip to the latest version
python -m pip install --upgrade pip

# Install all project requirements
pip install -r requirements.txt
```

---

## 4. Operational Modes: Live IBM Mode vs. Local Demo Mode

SciPilot is designed to run in two distinct modes. Understanding the difference is essential for academic accuracy and viva presentations:

### 🌐 Live IBM watsonx.ai Mode
- **Embeddings**: Uses IBM's `ibm/slate-125m-english-rtrvr` model hosted on IBM Cloud to produce dense 384-dimensional semantic embeddings.
- **Query Planning**: Uses IBM Granite 13B Instruct (`ibm/granite-13b-instruct-v2`) to break complex questions into multiple sub-questions.
- **Answer Synthesis**: Uses IBM Granite 13B generative capabilities to compose original natural-language answers strictly grounded in context chunks.
- **Session Memory**: Uploads session records to IBM Cloud Object Storage (COS) via S3 API calls.
- **Requirement**: Requires an active IBM Cloud account, project ID, and valid API key in `.env`.

### 🧪 Local Demo Mode (Offline Demonstration)
- **Embeddings**: Uses `scikit-learn`'s `HashingVectorizer` to generate consistent 384-dimensional L2-normalized vectors locally.
  > **Important**: This is a bag-of-words token hashing representation, **not** an IBM Slate semantic model.
- **Query Planning**: Gracefully degrades to rule-based analysis or direct sub-query evaluation.
- **Answer Synthesis**: Uses deterministic extractive synthesis by extracting, ranking, and concatenating the highest-scoring source passages with explicit citation markers.
  > **Important**: Answers in Local Demo Mode are extractive excerpts, **not** generative IBM Granite text.
- **Session Memory**: Automatically saves sessions to local JSON files (`reports/sessions/*.json`).
- **Requirement**: **Zero external credentials required.** Works completely offline.

---

## 5. Configuration & Credentials (.env Setup)

SciPilot ships with a template configuration file named `.env.example`.

### To Run in Local Demo Mode:
Create your local `.env` by copying the example:
```powershell
Copy-Item .env.example .env
```
Leave the placeholder values unchanged (`your_ibm_cloud_api_key_here`, etc.). SciPilot automatically detects placeholder patterns and activates **Local Demo Mode** without raising errors.

### To Run in Live IBM Mode:
Open `.env` in a text editor:
```powershell
notepad .env
```
Replace the placeholder values with your genuine IBM credentials:
```ini
WATSONX_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

---

## 6. Starting and Stopping SciPilot

### Starting the Application:
Ensure your virtual environment is active, then execute:
```powershell
python -m streamlit run src/dashboard/app.py
```

Streamlit will output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open your browser to: **`http://localhost:8501`**

### Stopping the Application:
To terminate the server, switch to your PowerShell window and press:
```
Ctrl + C
```

---

## 7. Navigating the User Interface

### Sidebar Controls
The left sidebar contains key controls and status badges:

1. **🔬 SciPilot Header**: Displays app name, version (v1.0.0), and description.
2. **⚙️ Research Configuration**:
   - **Citation Style**: Choose between `APA` (default) and `IEEE`.
   - **Top-K Retrieval**: Slider from 1 to 10 (default: 5 chunks).
   - **Auto-Generate Report**: Checkbox to toggle Markdown/PDF report generation on each query.
3. **🔑 IBM Credentials Status**:
   - `✅ watsonx.ai credentials loaded`: Valid IBM credentials detected.
   - `⚠️ IBM credentials not set or contain placeholders`: No API keys detected.
4. **🧪 Local Demo Mode Toggle**:
   - A toggle switch allowing you to switch between Live IBM Mode and Local Demo Mode at any time.
   - When active, an information card highlights that local embeddings and extractive answers are in use.
5. **📚 Index Status**: Shows how many document chunks are currently indexed in FAISS.

---

### Tab 1: Upload & Ingest Research Papers
1. Click the **📄 Upload Research Papers** tab.
2. Drag and drop one or more PDF files into the upload box (or click "Browse files").
   - *Example test file*: `research_papers/A_Comprehensive_Security_Framework_for_the_Model_Context_Protocol_MCP_in_Multi-Agent_AI_Systems.pdf`
3. Click the primary button: **⚡ Ingest 1 file(s) into FAISS**.
4. Observe the progress bar:
   - Reading PDF pages with PyMuPDF.
   - Splitting into 512-character chunks with 64-character overlap.
   - Generating 384-dimensional vector embeddings.
   - Writing the index to `data/faiss_index.index` and metadata to `data/faiss_index.meta`.
5. When complete, a success banner displays:
   `✅ Ingested 60 chunk(s) from 1 file(s) into FAISS. Index now has 60 chunk(s).`

---

### Tab 2: Research Assistant (Querying)
1. Switch to the **💬 Research Assistant** tab.
2. Look at the chat input box at the bottom: `"Ask a research question …"`.
3. Enter a technical research question, for example:
   ```
   What are the key security concerns in MCP multi-agent systems?
   ```
4. Press Enter.
5. The pipeline executes:
   - **Planner Agent**: Analyzes question.
   - **Retriever Agent**: Generates query vector, searches FAISS, and applies MMR diversification.
   - **Synthesis Agent**: Generates answer with citations (`[1]`, `[2]`).
   - **Verification Agent**: Calculates grounding metrics.
6. The response renders as an interactive answer card:
   - **Confidence Badge & Progress Bar**: Visual indication of response reliability.
   - **Answer Text**: Grounded answer with source citations.
   - **🗂️ Decomposed Sub-Questions** *(Collapsible)*: Expand to see planner output.
   - **📑 Sources Used** *(Collapsible)*: Expand to view source titles, file names, page numbers, and similarity scores.

---

### Tab 3: Evaluation & Verification
1. Switch to the **📊 Evaluation & Verification** tab.
2. Inspect the mathematical metrics computed for the latest answer:
   - **Overall Confidence Score**: Aggregate score between 0.0 and 1.0.
   - **Citation Coverage**: Proportion of assertions backed by explicit context citations.
   - **Grounding Ratio**: N-gram token overlap between answer text and source chunks.
   - **Source Diversity**: Proportion of unique sources/pages referenced.
   - **Status Card**: Explains whether the answer meets strict academic safety thresholds.

---

### Tab 4: Export Reports
1. Switch to the **📝 Export Report** tab.
2. View the formatted scientific research report, containing:
   - Executive Question & Timestamp.
   - Grounded Answer text.
   - Structured Sources Table.
   - Full Academic Bibliography (APA or IEEE).
   - Technical Metadata table.
3. Download the report directly to your machine:
   - Click **⬇️ Download Markdown (.md)**
   - Click **⬇️ Download PDF (.pdf)**
4. All reports are automatically archived in the `reports/` folder.

---

### Tab 5: Session History
1. Switch to the **💾 Sessions** tab.
2. View the chronological log of all research queries completed.
3. Each entry shows:
   - Question and Answer preview.
   - Verification verdict (`HIGH`, `MEDIUM`, `LOW`).
   - Confidence percentage.
   - Timestamp and unique session ID.

---

## 8. Understanding Verification Scores & Badges

SciPilot evaluates responses using a deterministic scoring formula:

$$\text{Confidence Score} = 0.35 \times \text{Coverage} + 0.35 \times \text{Grounding} + 0.15 \times \text{Quality} + 0.15 \times \text{Diversity}$$

| Badge | Score Range | Meaning | Recommendation |
|---|---|---|---|
| 🟢 **HIGH** | $\ge 70\%$ | Strong factual grounding; high citation alignment | Reliable for academic synthesis |
| 🟡 **MEDIUM** | $40\% - 69\%$ | Moderate grounding; some claims lack direct citations | Cross-reference with source PDF |
| 🔴 **LOW** | $< 40\%$ | Low semantic grounding; potential hallucination | Review source material manually |

---

## 9. Running the Test Suite

To verify that all 7 agents and utilities are working correctly, run the automated test suite from PowerShell:

```powershell
python -m pytest tests/ -v
```

### Expected Output:
```
tests/test_chunk.py ................................                     [  8%]
tests/test_citation.py ................................................. [ 21%]
tests/test_config.py ..............                                      [ 25%]
tests/test_embed.py ...........                                          [ 28%]
tests/test_ingest.py ..........................                          [ 35%]
tests/test_memory.py ................................                    [ 43%]
tests/test_planner.py ...................................                [ 53%]
tests/test_report.py ...................................                 [ 62%]
tests/test_retriever.py .............................                    [ 70%]
tests/test_synthesis.py ......................................           [ 80%]
tests/test_vector_store.py ......................                        [ 85%]
tests/test_verification.py ............................................. [ 97%]
........................................................................ [100%]

============================ 378 passed in 10.17s ============================
```

---

## 10. Troubleshooting & FAQs

### Q1: When I run `.\venv\Scripts\Activate.ps1`, I get an "ExecutionPolicy" error.
**Fix**: PowerShell restricts script execution by default. Run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then run `.\venv\Scripts\Activate.ps1` again.

### Q2: Streamlit shows `BXNIM0415E: Provided API key could not be found`.
**Fix**: Your `.env` has an invalid IBM Cloud API key. Open the sidebar, find the **🧪 Local Demo Mode** section, and turn **ON** the toggle switch. The app will immediately work offline.

### Q3: Ingestion fails with `No text could be extracted`.
**Fix**: The uploaded PDF may be an image scan without an OCR text layer. PyMuPDF extracts programmatic text layers. Ensure the PDF contains selectable text.

### Q4: How do I clear the FAISS vector index and start fresh?
**Fix**: Delete the local index files in PowerShell:
```powershell
Remove-Item -Path data\faiss_index.* -ErrorAction SilentlyContinue
```
Then restart Streamlit or refresh the page.

### Q5: How do I change the citation style from APA to IEEE?
**Fix**: Open the sidebar on the left, locate **Citation Style**, select **IEEE**, and submit your research query. The Bibliography will format using numbered brackets (`[1]`, `[2]`).

---

*SciPilot User Manual — IBM SkillsBuild × AICTE Internship 2026*
