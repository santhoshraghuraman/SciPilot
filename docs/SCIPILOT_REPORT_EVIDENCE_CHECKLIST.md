# SciPilot — Report Evidence & Visual Assets Checklist 📋
### Supporting Visual Artifacts, Test Verification & Screenshot Capture Plan

**Student Name:** Santhosh R (Register No: 22MIS0282)  
**Programme:** Integrated M.Tech Software Engineering, VIT Vellore  
**Project:** SciPilot — Next-Generation Agentic Research Assistant  
**Associated Report:** [`docs/SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md`](file:///c:/Users/91959/Documents/SciPilot-main/docs/SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md)  
**Target Asset Directory:** `docs/report_assets/figures/` (or `images/figures/`)  
**Status Date:** October 2026  

---

## 1. Overview & Purpose of this Checklist

This document acts as an operational guide for collecting, capturing, verifying, and inserting all visual and empirical evidence required for the **Industrial Internship Technical Report**.

To maintain academic integrity:
- **No fabricated screenshots**: Only genuine screenshots captured from the running application or terminal are permitted.
- **Consistent File Naming**: Every image must use the exact filename specified below without spaces.
- **Pre-configured Target Directories**: Image files can be placed in `docs/report_assets/figures/` or `images/figures/` prior to PDF compilation.

---

## 2. Master Visual Evidence Matrix

| Fig # | Suggested Filename | Caption | Exact Screen / Source | How to Capture | Report Insertion Point | Current Status |
|---|---|---|---|---|---|:---:|
| **7.1** | `fig_01_scipilot_sidebar.png` | SciPilot Reactive Sidebar Configuration and Credential State Indicator | Left sidebar of running Streamlit app | Open `http://localhost:8501`. Toggle **Enable Local Demo Mode** to ON. Take screenshot of the complete sidebar. | Before Section 7.2 & Section 10.2 | 🔲 Missing |
| **7.2** | `fig_02_upload_ingest_tab.png` | Multi-Document PDF Upload and Progress Tracking Interface | Tab 1: "📄 Upload Research Papers" | Upload `A_Comprehensive_Security_Framework...pdf`. Click "⚡ Ingest". Once progress bar reaches 100% and green success banner appears, capture the main pane. | Section 7.3 & Section 10.2 | 🔲 Missing |
| **7.3** | `fig_03_research_chat_interface.png` | Research Assistant Chat Interface Showing Structured Answer Card | Tab 2: "💬 Research Assistant" | Submit query: *"What are the key security concerns in MCP multi-agent systems?"*. Capture the resulting answer card, confidence bar, and expandable sources drawer. | Section 7.9 & Section 10.3 | 🔲 Missing |
| **7.4** | `fig_04_verification_metrics_card.png` | Deterministic Verification Dashboard with Category Badges and Sub-Scores | Tab 3: "📊 Evaluation & Verification" | Click on Tab 3 after generating an answer. Capture the four metrics cards (Coverage, Grounding, Quality, Diversity) and the verdict badge. | Section 7.10 & Section 10.4 | 🔲 Missing |
| **7.5** | `fig_05_report_download_preview.png` | Report Generation Tab Showing Markdown and PDF Export Actions | Tab 4: "📝 Export Report" | Switch to Tab 4. Capture the Markdown report preview container and the two blue download buttons (**Download Markdown** and **Download PDF**). | Section 7.12 & Section 10.5 | 🔲 Missing |
| **7.6** | `fig_06_session_history_tab.png` | Persistent Research Sessions View Showing Historical Query Logs | Tab 5: "💾 Sessions" | Switch to Tab 5. Capture the list of past completed research sessions showing question, verdict badge, and timestamp. | Section 7.13 | 🔲 Missing |
| **9.1** | `fig_07_pytest_terminal_execution.png` | Pytest 378/378 Test Suite Clean Execution in PowerShell Terminal | Windows PowerShell Terminal | Run `python -m pytest tests/ -q`. Capture the PowerShell terminal window showing `378 passed in XX.XXs` with green progress indicators. | Chapter 9 (Section 9.3) | 🔲 Missing |
| **10.1**| `fig_08_sample_pdf_report_render.png` | Sample Exported A4 PDF Research Report Rendered with `fpdf2` | Adobe Acrobat / Edge PDF Viewer | Open the generated PDF report from `reports/scipilot_*.pdf` in a PDF reader. Capture the first page showing the title, answer, and metadata table. | Chapter 10 (Section 10.5) | 🔲 Missing |

---

## 3. Step-by-Step Instructions to Capture All Evidence

Follow this sequence to capture all 8 required figures in under 10 minutes:

### Step 3.1: Start the SciPilot Application
In Windows PowerShell (with `venv` activated):
```powershell
# Ensure virtual environment is active
.\venv\Scripts\Activate.ps1

# Run the Streamlit dashboard
python -m streamlit run src/dashboard/app.py
```
Open your browser to [http://localhost:8501](http://localhost:8501).

---

### Step 3.2: Capture Figure 7.1 (Sidebar)
1. In the browser, look at the left sidebar.
2. Confirm the **Enable Local Demo Mode** switch is toggled **ON** (blue).
3. Confirm the info box shows: `🧪 Local Demo Mode active`.
4. Press `Win + Shift + S` (Windows Snipping Tool), select the sidebar area, and save as:
   `docs/report_assets/figures/fig_01_scipilot_sidebar.png`.

---

### Step 3.3: Capture Figure 7.2 (Upload & Ingestion)
1. Click the first tab: **📄 Upload Research Papers**.
2. Click **Browse files** and select:
   `research_papers\A_Comprehensive_Security_Framework_for_the_Model_Context_Protocol_MCP_in_Multi-Agent_AI_Systems.pdf`.
3. Click the primary button: **⚡ Ingest 1 file(s) into FAISS**.
4. Wait for the progress bar to reach 100% and display:
   `✅ Ingested 60 chunk(s) from 1 file(s) into FAISS. Index now has 60 chunk(s).`
5. Capture this screen with `Win + Shift + S` and save as:
   `docs/report_assets/figures/fig_02_upload_ingest_tab.png`.

---

### Step 3.4: Capture Figure 7.3 (Research Assistant Chat)
1. Switch to the second tab: **💬 Research Assistant**.
2. In the chat input box at the bottom, type:
   ```
   What are the key security concerns in MCP multi-agent systems?
   ```
3. Press Enter and wait for the response card to render.
4. Expand the **🗂️ Decomposed Sub-Questions** and **📑 Sources Used** accordions.
5. Capture the answer card showing the confidence score and citations, and save as:
   `docs/report_assets/figures/fig_03_research_chat_interface.png`.

---

### Step 3.5: Capture Figure 7.4 (Verification Metrics Card)
1. Click the third tab: **📊 Evaluation & Verification**.
2. Notice the cards for:
   - **Verdict**: `🟢 HIGH`
   - **Confidence Score**: `76%`
   - **Citation Coverage**: `0.71`
   - **Grounding Ratio**: `0.89`
   - **Answer Quality**: `1.00`
   - **Source Diversity**: `0.33`
3. Capture this metrics dashboard and save as:
   `docs/report_assets/figures/fig_04_verification_metrics_card.png`.

---

### Step 3.6: Capture Figure 7.5 (Export Report Tab)
1. Switch to the fourth tab: **📝 Export Report**.
2. Notice the in-browser Markdown report preview and the two download buttons:
   - `⬇️ Download Markdown (.md)`
   - `⬇️ Download PDF (.pdf)`
3. Capture this screen and save as:
   `docs/report_assets/figures/fig_05_report_download_preview.png`.

---

### Step 3.7: Capture Figure 7.6 (Session History Tab)
1. Switch to the fifth tab: **💾 Sessions**.
2. View the saved session history cards showing the question, timestamp, and verdict.
3. Capture this screen and save as:
   `docs/report_assets/figures/fig_06_session_history_tab.png`.

---

### Step 3.8: Capture Figure 9.1 (Terminal Pytest Execution)
1. Open a new PowerShell terminal window in the project root:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python -m pytest tests/ -q
   ```
2. Wait for completion (~10 seconds).
3. The terminal displays:
   `378 passed in 10.01s`
4. Capture the terminal window and save as:
   `docs/report_assets/figures/fig_07_pytest_terminal_execution.png`.

---

### Step 3.9: Capture Figure 10.1 (Exported PDF Report Render)
1. Open Windows File Explorer and navigate to:
   `c:\Users\91959\Documents\SciPilot-main\reports\`
2. Double-click the latest generated PDF report (e.g. `scipilot_20261013_211125_*.pdf`).
3. It will open in Microsoft Edge or Adobe Acrobat Reader.
4. Capture the top of the first page showing the title, metadata box, grounded answer, and sources table.
5. Save as:
   `docs/report_assets/figures/fig_08_sample_pdf_report_render.png`.

---

## 4. Converting Markdown to PDF for Official University Submission

Once the 8 screenshot files are placed into `docs/report_assets/figures/`:

### Method 1: Using Pandoc with LaTeX (Recommended for Academic Formatting)
If `pandoc` and `wkhtmltopdf` or `xelatex` are installed:
```powershell
pandoc docs/SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md `
  -o docs/SCIPILOT_INTERNSHIP_REPORT.pdf `
  --from markdown `
  --toc `
  --number-sections `
  --pdf-engine=xelatex
```

### Method 2: Using VS Code Markdown PDF Extension
1. Open `docs/SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md` in Visual Studio Code.
2. Install the extension **Markdown PDF** (`yzane.markdown-pdf`).
3. Right-click anywhere in the editor window.
4. Select **Markdown PDF: Export (pdf)**.
5. A styled PDF will be generated in the same directory.

### Method 3: Using Google Chrome / Edge Print-to-PDF
1. Open the Markdown file in a Markdown viewer (such as GitHub, VS Code Preview, or Grip).
2. Press `Ctrl + P` to print.
3. Destination: **Save as PDF**.
4. Margins: **Default** or **Custom (1 inch)**.
5. Check **Background graphics**.
6. Click **Save**.

---

## 5. Verification Checklist Sign-off

- [x] Main Report file created at `docs/SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md`
- [x] Evidence checklist created at `docs/SCIPILOT_REPORT_EVIDENCE_CHECKLIST.md`
- [x] Target asset folder created at `docs/report_assets/figures/`
- [x] All 13 chapters and 7 appendices structured in academic format
- [x] 4 Mermaid architecture diagrams validated and embedded
- [x] Mathematical equations for MMR, Cosine Similarity, and Verification formulated
- [x] 378/378 automated pytest tests executed and verified in report
- [x] Live demonstration metrics on 6-page research paper documented
- [ ] Visual screenshots captured and saved to `docs/report_assets/figures/` *(Action item for user prior to PDF printing)*

---
*SciPilot Evidence Checklist — IBM SkillsBuild × AICTE Internship 2026*
