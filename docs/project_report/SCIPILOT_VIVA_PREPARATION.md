# SciPilot 🔬 — Comprehensive Viva Voce Preparation Guide

**Candidate Name:** Santhosh R  
**Registration Number:** 22MIS0282  
**Degree:** Integrated M.Tech. Software Engineering  
**Department:** School of Information Technology & Engineering (SITE), VIT Vellore  
**Viva Dates:** 14–16 October 2026  
**Project:** SciPilot — Next-Generation Agentic AI Research Assistant  
**Industry Partner:** IBM SkillsBuild × AICTE Internship 2026  
**GitHub Repository:** [https://github.com/santhoshraghuraman/SciPilot](https://github.com/santhoshraghuraman/SciPilot)  

---

## 1. The 60-Second Elevator Pitch
*(Use this when the examiner asks: "Introduce yourself and give a brief overview of your project.")*

> *"Good morning respected examiners. I am Santhosh R, registration number 22MIS0282, pursuing Integrated M.Tech. in Software Engineering at VIT Vellore.
>
> During my IBM SkillsBuild internship, I developed **SciPilot**, an agentic AI research assistant designed to automate scientific literature review. Traditional RAG systems often suffer from hallucinations, diluted context retrieval on complex queries, and unverified citations. 
>
> SciPilot solves this through an orchestrated multi-agent pipeline powered by **IBM watsonx.ai** and a local **FAISS** vector store. The system ingests research papers in PDF format, performs structure-preserving text extraction, and chunks the content with full provenance tracking. When a researcher poses a question, our **Planner Agent** breaks it down into atomic sub-questions, our **Retriever Agent** performs multi-pass semantic search with **Maximal Marginal Relevance (MMR)** re-ranking, and **IBM Granite 13B** synthesizes a grounded response.
>
> To ensure scientific rigor, I designed a deterministic **Verification Agent** that scores the answer across four empirical dimensions: citation validity, grounding overlap, length bounds, and source diversity. Finally, the system formats APA or IEEE citations, generates downloadable Markdown and PDF reports, and persists sessions to IBM Cloud Object Storage or local storage through an interactive Streamlit dashboard."*

---

## 2. The 3-Minute Technical Deep Dive
*(Use this if the panel says: "Explain the end-to-end technical implementation and architecture in detail.")*

> *"Thank you. Let me walk you through the four core layers of SciPilot:
>
> **1. Ingestion & Preprocessing Subsystem:**
> When a user uploads PDF papers in the Streamlit UI, the ingestion module uses PyMuPDF (`fitz`) to extract text while capturing page numbers, metadata, and SHA-256 document hashes. We perform semantic recursive character chunking with a 512-character window and 64-character overlap. Crucially, each chunk retains its exact provenance—including `doc_hash`, `source`, `page_number`, and character start/end offsets. These chunks are embedded using IBM’s **Slate-125M** bi-encoder into 384-dimensional dense vectors and indexed in FAISS using `IndexFlatIP`. By applying L2-normalization to all vectors, inner-product search functions as mathematically exact cosine similarity.
>
> **2. Agentic Orchestration Layer:**
> In `src/orchestrator.py`, we employ an orchestrated coordinator pattern rather than unconstrained agent choreography. When a query arrives:
> - The **Planner Agent** queries IBM Granite with low temperature (0.1) to decompose complex, multi-variable questions into 2 to 5 targeted sub-questions.
> - The **Retriever Agent** queries FAISS for each sub-question, retrieves a candidate pool of `top_k * 4` chunks, filters out low-similarity passages below 0.20 cosine similarity, and applies **Maximal Marginal Relevance (MMR)** with $\lambda = 0.70$ to balance high relevance with topical diversity.
>
> **3. Grounded Synthesis & 4-Check Verification:**
> - The **Synthesis Agent** injects the retrieved passages into a structured prompt for IBM Granite 13B Instruct, forcing it to cite evidence using inline markers like `[1]`, `[2]`.
> - Then, our **Verification Agent** steps in. Instead of relying on a slow, non-deterministic LLM-as-a-judge, it executes four fast, deterministic algorithmic checks:
>   1. *Citation Coverage (35% weight):* Are all bracketed citations valid indices within the retrieved set?
>   2. *Grounding Ratio (35% weight):* What proportion of sentences share lexical content words with the source passages?
>   3. *Answer Quality (15% weight):* Does the response adhere to academic word count bounds (20–600 words)?
>   4. *Source Diversity (15% weight):* Does the synthesis integrate findings from multiple papers?
> - This yields an overall confidence score between 0.0 and 1.0 and assigns a `HIGH`, `MEDIUM`, or `LOW` verdict.
>
> **4. Bibliographic Formatting & Output Delivery:**
> The **Citation Agent** resolves chunk hashes to unique documents, formatting references in APA 7th edition or IEEE style. The **Report Agent** compiles a Markdown document and a vector-styled PDF report via `fpdf2`. Finally, the **Memory Agent** serializes the session into JSON and persists it to IBM Cloud Object Storage or local storage, rendered seamlessly in the Streamlit dashboard."*

---

## 3. Hand-Drawable Whiteboard Architecture
*(If asked to draw the architecture on a whiteboard or paper during the viva, draw these 4 clean horizontal blocks connected by arrows)*

```
+-----------------------------------------------------------------------+
|  1. USER INTERFACE (Streamlit - src/dashboard/app.py)                 |
|     [Upload Tab]       [Research Chat]       [Verification & Reports]  |
+-----------------------------------------------------------------------+
        | (Upload PDF)                                    | (Ask Query)
        v                                                 v
+-------------------------------+       +-------------------------------+
| 2. INGESTION & RAG PIPELINE   |       | 3. MULTI-AGENT ORCHESTRATOR   |
|    - PyMuPDF (Text & Hash)    |       |    (src/orchestrator.py)      |
|    - Recursive Chunk (512/64) |       |                               |
|    - Slate-125M (384-d Embed) |       |  [Planner Agent] (Sub-qs)     |
|    - FAISS IndexFlatIP        |       |        |                      |
|      (L2-Normalized Cosine)   | <---> |  [Retriever Agent] (MMR 0.7)  |
+-------------------------------+       |        |                      |
                                        |  [Synthesis Agent] (Granite)  |
                                        |        |                      |
                                        |  [Verification Agent] (4-Chk) |
                                        +-------------------------------+
                                                 |
                                                 v
                                        +-------------------------------+
                                        | 4. OUTPUT & PERSISTENCE       |
                                        |  - Citation Agent (APA/IEEE)  |
                                        |  - Report Agent (MD / PDF)    |
                                        |  - Memory Agent (COS / JSON)  |
                                        +-------------------------------+
```

---

## 4. 45+ Most Likely Viva Questions & High-Scoring Answers

### Category 1: High-Level Concepts & Project Scope

#### Q1. What is the fundamental difference between standard RAG and Agentic RAG in SciPilot?
**Answer:** Standard (naive) RAG takes a user's single query, computes an embedding, retrieves top-$k$ nearest chunks, and directly prompts an LLM. This fails on complex, multi-part research questions because one vector cannot capture three distinct topics simultaneously.  
In SciPilot’s **Agentic RAG**, an autonomous **Planner Agent** breaks the inquiry down into atomic sub-questions, executes multiple targeted retrieval passes, applies **MMR re-ranking** to prevent passage duplication, and runs a dedicated **Verification Agent** to mathematically audit the generated response before presenting it to the user.

#### Q2. Why did you choose IBM watsonx.ai and IBM Granite over OpenAI or local Ollama models?
**Answer:** This project was developed as part of the IBM SkillsBuild × AICTE initiative. IBM watsonx.ai provides enterprise-grade governance, strict data privacy guarantees, and foundation models like **IBM Granite 13B** and **IBM Slate 125M**. Granite models are trained on curated, vetted academic and enterprise datasets, minimizing copyrighted training contamination and bias, which is essential for scholarly applications.

#### Q3. What is the role of `src/orchestrator.py`?
**Answer:** `Orchestrator` implements the coordinator design pattern. It manages the lifecycle of the system, coordinates data handoffs between the 7 specialized agents, ensures dependencies are lazily loaded on first use to prevent slow boot times, and encapsulates execution within clean `ResearchRequest` and `ResearchResponse` dataclasses.

---

### Category 2: RAG, Embeddings & Preprocessing

#### Q4. Why did you use PyMuPDF (`fitz`) instead of pypdf or PyPDF2?
**Answer:** PyMuPDF is a Python binding for MuPDF, a C-native rendering engine. It is significantly faster (typically 10x faster than pure-Python libraries like PyPDF2), reliably preserves page numbers, cleanly handles multi-column academic paper formats, extracts document metadata (title, authors, creation date), and detects null bytes that often corrupt downstream NLP tokenizers.

#### Q5. What chunking strategy did you use and why?
**Answer:** We implemented **Recursive Character Chunking** in `src/rag/chunk.py`. Rather than splitting arbitrarily at fixed character counts, it tries a priority hierarchy of separators: double newline (`\n\n` for paragraphs), single newline (`\n`), sentence terminators (`. `, `! `, `? `), clause boundaries (`; `, `, `), and finally space (` `).  
We set `chunk_size = 512` characters with `chunk_overlap = 64` characters. The overlap guarantees that sentences spanning boundary edges are never bifurcated, preserving semantic continuity.

#### Q6. What is chunk provenance and why is it critical for research?
**Answer:** Provenance is the verifiable audit trail of where a piece of information originated. In SciPilot, every `TextChunk` records:
1. `doc_hash`: SHA-256 digest of the source PDF.
2. `source`: Original PDF filename.
3. `page_number`: Exact 1-based page number where the chunk appears.
4. `char_start` and `char_end`: Exact character offsets in the extracted stream.  
This allows the Citation and Report agents to attribute statements to the exact page of the paper rather than guessing.

#### Q7. Which embedding model did you use, and what is its dimensionality?
**Answer:** We used **IBM Slate 125M English Retriever** (`ibm/slate-125m-english-rtrvr`), which produces **384-dimensional** dense vector representations. It is specifically pre-trained and fine-tuned as a bi-encoder for semantic passage retrieval.

---

### Category 3: FAISS Mathematics & Vector Search

#### Q8. Why did you choose `IndexFlatIP` instead of `IndexFlatL2` in FAISS?
**Answer:** In high-dimensional semantic search, **cosine similarity** is the gold standard because it measures the angle between vectors, making it invariant to vector magnitude (document length).  
Cosine similarity formula:
$$\text{CosineSim}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
If vectors $u$ and $v$ are L2-normalized such that $\|u\|_2 = 1$ and $\|v\|_2 = 1$, the denominator becomes 1, and cosine similarity simplifies to the **inner product** (dot product):
$$\text{CosineSim}(u, v) = u \cdot v$$
FAISS’s `IndexFlatIP` computes the inner product directly. By normalizing all vectors in-place using `faiss.normalize_L2()`, `IndexFlatIP` computes exact cosine similarity with maximum hardware efficiency.

#### Q9. How does FAISS store metadata in SciPilot?
**Answer:** Native FAISS C++ indices only store vector arrays and internal integer IDs; they do not store arbitrary Python dictionaries or text strings.  
In SciPilot (`src/rag/vector_store.py`), we maintain a parallel Python list `_chunks` whose index corresponds 1-to-1 with the FAISS row index. On persistence, we save `<path>.index` (the binary vector index) alongside `<path>.meta` (the pickled list of `TextChunk` objects).

#### Q10. What is Maximal Marginal Relevance (MMR) and why is it used?
**Answer:** When retrieving top-$k$ passages, pure cosine similarity often retrieves 5 nearly identical paragraphs from the same section of a paper. **Maximal Marginal Relevance (MMR)** (Carbonell & Goldstein, 1998) resolves this by penalizing candidates that are overly similar to passages already selected:
$$\text{MMR} = \operatorname*{argmax}_{d_i \in D \setminus S} \left[ \lambda \cdot \text{Sim}(q, d_i) - (1 - \lambda) \max_{d_j \in S} \text{Sim}(d_i, d_j) \right]$$
We set $\lambda = 0.70$, giving 70% weight to query relevance and 30% weight to diversity across selected chunks.

---

### Category 4: The Multi-Agent System & Communication

#### Q11. How do the agents communicate with each other?
**Answer:** Agents communicate via strongly typed Python dataclasses mediated by the `Orchestrator`:
- `ResearchRequest` $\rightarrow$ `PlannerAgent` $\rightarrow$ `PlannerResult` (sub-questions list).
- Sub-questions $\rightarrow$ `RetrieverAgent` $\rightarrow$ `RetrievalResult` (chunks + cosine scores).
- `RetrievalResult` $\rightarrow$ `SynthesisAgent` $\rightarrow$ `SynthesisResult` (answer + cited indices).
- `SynthesisResult` $\rightarrow$ `VerificationAgent` $\rightarrow$ `VerificationResult` (score + verdict).
- `SynthesisResult` + `VerificationResult` $\rightarrow$ `CitationAgent` & `ReportAgent` $\rightarrow$ `ResearchResponse`.

#### Q12. What happens if the Planner Agent fails or returns an invalid output?
**Answer:** The Planner Agent is engineered with **graceful degradation** in `src/agents/planner.py`:
1. It attempts regex parsing of numbered lists.
2. It falls back to sentences ending in `?`.
3. If parsing fails, or if fewer than 2 sub-questions are generated, or if the IBM API encounters an exception, it activates `_fallback()`, which passes the user's original query as the sole question (`used_fallback = True`). The pipeline never crashes.

---

### Category 5: Verification & Hallucination Mitigation

#### Q13. How does the Verification Agent work without an LLM?
**Answer:** Many systems use a second LLM ("LLM-as-a-judge") to check answers, which introduces latency, costs API tokens, and can hallucinate itself.  
SciPilot’s `VerificationAgent` (`src/agents/verification.py`) is **100% deterministic, zero-dependency, and local**. It evaluates 4 specific metrics:
1. **Citation Coverage (Weight 0.35):** Verifies that all inline citations (`[1]`, `[2]`) exist in the retrieved context pool ($1 \le N \le \text{total\_chunks}$).
2. **Grounding Ratio (Weight 0.35):** Tokenizes answer sentences and context chunks, filters stop words ($\ge 4$ characters), and measures whether each answer sentence shares at least 3 content words with the context.
3. **Answer Quality (Weight 0.15):** Ensures length falls within academic norms ($20 \le \text{words} \le 600$).
4. **Source Diversity (Weight 0.15):** Awards higher scores when the answer synthesizes content from multiple unique PDF documents.

#### Q14. What are the confidence score thresholds and verdicts?
**Answer:**
- $\text{Score} \ge 0.70 \implies \mathbf{HIGH}$ confidence (Green badge)
- $0.40 \le \text{Score} < 0.70 \implies \mathbf{MEDIUM}$ confidence (Yellow badge)
- $\text{Score} < 0.40 \implies \mathbf{LOW}$ confidence (Red badge)

---

### Category 6: Citation & Report Generation

#### Q15. How does SciPilot format APA and IEEE citations?
**Answer:** `src/agents/citation.py` inspects `TextChunk` metadata:
- **APA 7th Edition:** `Author, A. B. (Year). Title. Source.`
- **IEEE Style:** `[N] A. B. Author, "Title," Source, Year.`
It deduplicates citations by `doc_hash` so that if 5 chunks from the same paper are cited, that paper appears only once in the bibliography.

#### Q16. Why did you use `fpdf2` instead of HTML-to-PDF converters?
**Answer:** Tools like `pdfkit` or `weasyprint` depend on external system binaries (`wkhtmltopdf` or C-libraries like `cairo`/`pango`), which cause deployment and platform compatibility issues on Windows and cloud VMs. `fpdf2` is pure Python, lightweight, has zero external binary dependencies, and provides precise programmatic control over A4 page margins, headers, tables, and typography.

---

### Category 7: Python & Software Engineering Practices

#### Q17. How do you handle configuration and secrets management?
**Answer:** We use **Pydantic Settings** (`BaseSettings`) in `src/utils/config.py`. It loads from `.env`, validates data types at startup, and maps environment variables like `WATSONX_API_KEY` and `GRANITE_INSTRUCT_MODEL`. Default values (`"not-set"`) prevent crashes during unit testing, while `.env` is gitignored to protect secrets.

#### Q18. How did you ensure fault tolerance on IBM API calls?
**Answer:** We decorated API invocation methods with the **Tenacity** library (`@retry`):
- Exponential backoff: starts at 2s, doubles to 4s, 8s, up to 30s.
- Maximum attempts: 3 to 4 attempts.
- Reraises the exception if all attempts fail, allowing the calling agent to cleanly transition to its fallback mode.

#### Q19. How did you verify the software?
**Answer:** We wrote a comprehensive Pytest suite containing **378 unit and integration tests** across all 14 test modules in `tests/`. It covers boundary conditions, malformed PDFs, empty queries, mock vector spaces, and verification score mathematics. All 378 tests pass in under 14 seconds.

---

### Category 8: Limitations & Future Scope

#### Q20. What are the current limitations of SciPilot?
**Answer:**
1. **OCR on Scanned PDFs:** We currently extract native text streams. Papers scanned as pure raster images without an embedded text layer require an OCR engine like Tesseract.
2. **Cloud API Dependency:** Live generation relies on watsonx.ai service uptime and API quotas.
3. **Table & Figure Extraction:** While text inside tables is extracted, tabular layout and mathematical formulas in complex graphics are flattened into text streams.

#### Q21. What is the future scope of this project?
**Answer:**
1. Adding multimodal document parsing using vision-language models (e.g. Granite Vision) to interpret figures, charts, and diagrams.
2. Integrating Graph RAG (Knowledge Graphs) to discover hidden citation connections across hundreds of papers.
3. Expanding export formats to LaTeX (`.tex`) and BibTeX (`.bib`) for academic submission workflows.

---

## 5. Step-by-Step Viva Demonstration Checklist

When asked to give a live demo, follow these exact steps:

1. **Verify Local Execution:**
   - Open your browser to: [http://localhost:8501](http://localhost:8501).
   - Show the examiner the clean, responsive SciPilot header and sidebar.

2. **Walk Through the Sidebar Settings:**
   - Point out **Citation Style** selection (`APA` vs `IEEE`).
   - Show the **Top-K Retrieval** slider (defaults to 5).
   - Show the **Generate PDF/MD Report** checkbox.
   - Point out the **IBM Credentials** indicator and **FAISS Index status** badge.

3. **Demonstrate Tab 1 — Document Ingestion:**
   - Click on the **Upload** tab.
   - Mention: *"Here, researchers upload one or more academic PDFs. The system extracts text using PyMuPDF, performs semantic recursive chunking with 512-character windows and 64-character overlap, generates 384-d embeddings, and indexes them in FAISS."*

4. **Demonstrate Tab 2 — Research Chat:**
   - Click on the **Research** tab.
   - Explain how a user enters a research question.
   - Show how the response card renders the answer with inline citations (`[1]`), expandable **Decomposed Sub-Questions**, and an expandable **Sources Table** showing file names and page numbers.

5. **Demonstrate Tab 3 — Verification Details:**
   - Click on the **Verification** tab.
   - Walk through the 4 metrics:
     - 📌 *Citation Coverage (35%)*
     - 🔗 *Grounding Ratio (35%)*
     - 📏 *Answer Quality (15%)*
     - 📚 *Source Diversity (15%)*
   - Show the progress bars and the overall confidence verdict (`HIGH` / `MEDIUM` / `LOW`).

6. **Demonstrate Tab 4 — Citations & Reports:**
   - Show the formatted References section (APA or IEEE).
   - Highlight the **Download Markdown** and **Download PDF** buttons generated by `fpdf2`.

7. **Demonstrate Tab 5 — Session History:**
   - Show the **Session History** panel.
   - Explain how the **Memory Agent** persists sessions locally or to IBM Cloud Object Storage.

8. **Show the Test Suite (Examiners love this):**
   - Open the terminal and run: `python -m pytest`
   - Point out: *"We have 378 unit and integration tests covering chunking, embeddings, verification mathematics, and FAISS vector persistence—all passing 100%."*

---

## 6. How to Answer Tricky Questions Honestly

- **If the examiner asks:** *"Why do the credentials say 'not set' or show a warning right now?"*  
  **Answer:** *"In the local repository, API keys are kept in `.env` and excluded from version control to prevent security leaks on public GitHub repositories. In demo mode without live API keys, the system demonstrates full local capability: PDF parsing, chunking, FAISS index management, deterministic verification, citation generation, and PDF report creation all run completely locally."*

- **If asked:** *"Did you build everything from scratch or use libraries?"*  
  **Answer:** *"I leveraged robust foundational libraries for core primitives—PyMuPDF for PDF reading, FAISS for vector math, fpdf2 for PDF generation, and Streamlit for UI. However, the multi-agent orchestration, the recursive chunking algorithm with provenance tracking, the Planner fallback engine, the 4-check Verification Agent, and the APA/IEEE citation deduplication engine were custom-architected and coded specifically for SciPilot."*

- **If asked:** *"Why did you use LangChain in the stack if you wrote custom agents?"*  
  **Answer:** *"We include LangChain and LangChain-IBM in our environment for its standard schema interfaces and connectors, but to achieve strict deterministic verification and lightweight execution, we built our agent pipelines as modular Python classes rather than black-box autonomous agents."*
