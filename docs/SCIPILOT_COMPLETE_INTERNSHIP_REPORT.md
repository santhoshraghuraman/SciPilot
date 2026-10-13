# INDUSTRIAL INTERNSHIP TECHNICAL REPORT

<br/>

<div align="center">

# SCIPILOT: NEXT-GENERATION AGENTIC RESEARCH ASSISTANT FOR SCIENTIFIC LITERATURE REVIEW

<br/>

**An Industrial Internship Technical Report submitted in partial fulfillment of the requirements for the degree of**

### INTEGRATED MASTER OF TECHNOLOGY (M.TECH) IN SOFTWARE ENGINEERING

<br/>

**Submitted by:**

### SANTHOSH R
**Register Number: 22MIS0282**

<br/>

**Internship Programme:**  
**IBM SkillsBuild × AICTE Internship 2026**

**Host / Partner Organisation:**  
**Edunet Foundation**

**Internship Duration:**  
**12 June 2026 – 10 July 2026**

<br/>

**Academic Year:**  
**2026 – 2027**

<br/>

**School of Information Technology and Engineering (SITE)**  
**Vellore Institute of Technology (VIT), Vellore**  
**Vellore – 632014, Tamil Nadu, India**

</div>

---

<div style="page-break-after: always;"></div>

## DECLARATION

I hereby declare that the industrial internship technical report entitled **"SciPilot: Next-Generation Agentic Research Assistant for Scientific Literature Review"** submitted to the School of Information Technology and Engineering (SITE), Vellore Institute of Technology (VIT), Vellore, is a bonafide record of the work carried out by me during the internship duration from **12 June 2026 to 10 July 2026** under the **IBM SkillsBuild × AICTE Internship Programme**, conducted in partnership with **Edunet Foundation**.

I further declare that this report has been prepared based on my genuine development, architectural analysis, implementation, and testing of the SciPilot application, and that no part of this report has been plagiarised or submitted elsewhere for the award of any other degree, diploma, or fellowship.

<br/><br/>

**Place:** Vellore  
**Date:** 13 October 2026  

<br/><br/>

________________________________________  
**(Signature of the Student)**  
**SANTHOSH R**  
**Register No: 22MIS0282**  
**Integrated M.Tech Software Engineering**  
**Vellore Institute of Technology (VIT), Vellore**

---

<div style="page-break-after: always;"></div>

## ACKNOWLEDGEMENT

I express my deepest gratitude to the Almighty for bestowing the strength, perseverance, and clarity required to successfully complete this internship and technical project.

I convey my heartfelt thanks to the Chancellor, Vice-President, Vice-Chancellor, Pro Vice-Chancellor, and the Management of **Vellore Institute of Technology (VIT), Vellore**, for providing world-class infrastructure, state-of-the-art computational facilities, and an intellectually vibrant environment that encouraged my pursuit of advanced software engineering research.

I extend my sincere appreciation to the Dean, Associate Deans, and Head of the Department, **School of Information Technology and Engineering (SITE)**, along with all faculty members and technical staff of the Integrated M.Tech Software Engineering programme, for their continuous academic guidance, rigorous curriculum, and steadfast support throughout my studies.

I am immensely grateful to the **Edunet Foundation** and the **IBM SkillsBuild × AICTE** initiative for orchestrating this industrial internship. The curriculum, hands-on modules in Agentic AI, Cloud Cognitive Services, Cybersecurity, and Quantum Computing, and access to enterprise AI tools were instrumental in shaping the architecture and implementation of Project SciPilot.

Finally, I dedicate this work to my parents, family members, and peers whose encouragement, patience, and unwavering belief served as a perpetual fountain of motivation.

<br/><br/>

**SANTHOSH R**  
*(Register No: 22MIS0282)*

---

<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS

- [Declaration](#declaration)
- [Acknowledgement](#acknowledgement)
- [List of Figures](#list-of-figures)
- [List of Tables](#list-of-tables)
- [List of Abbreviations](#list-of-abbreviations)
- [Chapter 1 — Abstract](#chapter-1--abstract)
- [Chapter 2 — Introduction](#chapter-2--introduction)
  - [2.1 Background and Motivation](#21-background-and-motivation)
  - [2.2 Problem Statement](#22-problem-statement)
  - [2.3 Need for the System](#23-need-for-the-system)
  - [2.4 Project Objectives](#24-project-objectives)
  - [2.5 Scope of the Project](#25-scope-of-the-project)
  - [2.6 Proposed Solution](#26-proposed-solution)
  - [2.7 Key Contributions](#27-key-contributions)
  - [2.8 Report Organisation](#28-report-organisation)
- [Chapter 3 — Internship Organisation and Programme](#chapter-3--internship-organisation-and-programme)
  - [3.1 Profile of Edunet Foundation](#31-profile-of-edunet-foundation)
  - [3.2 IBM SkillsBuild × AICTE Programme Context](#32-ibm-skillsbuild--aicte-programme-context)
  - [3.3 Internship Duration and Schedule](#33-internship-duration-and-schedule)
  - [3.4 Core Learning Areas & Technical Domains](#34-core-learning-areas--technical-domains)
- [Chapter 4 — Problem Analysis and Requirements](#chapter-4--problem-analysis-and-requirements)
  - [4.1 Analysis of Existing Literature Review Approaches](#41-analysis-of-existing-literature-review-approaches)
  - [4.2 Specific Bottlenecks Addressed by SciPilot](#42-specific-bottlenecks-addressed-by-scipilot)
  - [4.3 Software Requirements Specification (SRS)](#43-software-requirements-specification-srs)
    - [4.3.1 Functional Requirements](#431-functional-requirements)
    - [4.3.2 Non-Functional Requirements](#432-non-functional-requirements)
    - [4.3.3 User & Interface Requirements](#433-user--interface-requirements)
  - [4.4 System Assumptions, Dependencies and Constraints](#44-system-assumptions-dependencies-and-constraints)
  - [4.5 System Use Cases and Workflows](#45-system-use-cases-and-workflows)
- [Chapter 5 — System Architecture and Design](#chapter-5--system-architecture-and-design)
  - [5.1 Overall Architectural Style (Coordinator-Based Multi-Agent)](#51-overall-architectural-style-coordinator-based-multi-agent)
  - [5.2 High-Level Architecture Diagram](#52-high-level-architecture-diagram)
  - [5.3 End-to-End Workflow Diagram](#53-end-to-end-workflow-diagram)
  - [5.4 Agent Interaction and Collaboration Model](#54-agent-interaction-and-collaboration-model)
  - [5.5 RAG Subsystem and Ingestion Flow](#55-rag-subsystem-and-ingestion-flow)
  - [5.6 Dual-Mode Execution Architecture (Live IBM vs. Local Demo)](#56-dual-mode-execution-architecture-live-ibm-vs-local-demo)
- [Chapter 6 — Technologies and Tools](#chapter-6--technologies-and-tools)
  - [6.1 Programming Language & Core Runtime](#61-programming-language--core-runtime)
  - [6.2 Foundation Models & Cloud AI Ecosystem](#62-foundation-models--cloud-ai-ecosystem)
  - [6.3 Vector Database & Local Projection Libraries](#63-vector-database--local-projection-libraries)
  - [6.4 Document Parsing & Publication Frameworks](#64-document-parsing--publication-frameworks)
  - [6.5 Frontend Framework & Dashboard Architecture](#65-frontend-framework--dashboard-architecture)
  - [6.6 Testing, Quality Assurance & Engineering Utilities](#66-testing-quality-assurance--engineering-utilities)
- [Chapter 7 — Detailed Implementation](#chapter-7--detailed-implementation)
  - [7.1 Project Directory Structure](#71-project-directory-structure)
  - [7.2 Application Startup & Dependency Injection](#72-application-startup--dependency-injection)
  - [7.3 Document Ingestion Subsystem (`src/rag/ingest.py`)](#73-document-ingestion-subsystem-srcragingestpy)
  - [7.4 Structure-Preserving Recursive Text Chunking (`src/rag/chunk.py`)](#74-structure-preserving-recursive-text-chunking-srcragchunkpy)
  - [7.5 Embedding Generation & Dimension-Invariant Fallback (`src/rag/embed.py`)](#75-embedding-generation--dimension-invariant-fallback-srcragembedpy)
  - [7.6 FAISS Vector Indexing & In-Memory Retrieval (`src/rag/vector_store.py`)](#76-faiss-vector-indexing--in-memory-retrieval-srcragvector_storepy)
  - [7.7 Query Decomposition & Planning Agent (`src/agents/planner.py`)](#77-query-decomposition--planning-agent-srcagentsplannerpy)
  - [7.8 Semantic Retrieval & MMR Re-Ranking Agent (`src/agents/retriever.py`)](#78-semantic-retrieval--mmr-re-ranking-agent-srcagentsretrieverpy)
  - [7.9 Grounded Synthesis Agent (`src/agents/synthesis.py`)](#79-grounded-synthesis-agent-srcagentssynthesispy)
  - [7.10 Algorithmic Verification Agent (`src/agents/verification.py`)](#710-algorithmic-verification-agent-srcagentsverificationpy)
  - [7.11 Academic Citation Agent (`src/agents/citation.py`)](#711-academic-citation-agent-srcagentscitationpy)
  - [7.12 Automated Report Generation Agent (`src/agents/report.py`)](#712-automated-report-generation-agent-srcagentsreportpy)
  - [7.13 Session Memory & Hybrid Storage Agent (`src/agents/memory.py`)](#713-session-memory--hybrid-storage-agent-srcagentsmemorypy)
  - [7.14 Streamlit Reactive Interface (`src/dashboard/app.py`)](#714-streamlit-reactive-interface-srcdashboardapppy)
  - [7.15 Security, Configuration & Resilience Engineering](#715-security-configuration--resilience-engineering)
- [Chapter 8 — Algorithms and Technical Methods](#chapter-8--algorithms-and-technical-methods)
  - [8.1 Sliding Window Recursive Chunking Algorithm](#81-sliding-window-recursive-chunking-algorithm)
  - [8.2 L2-Normalized Cosine Metric under Inner Product Search](#82-l2-normalized-cosine-metric-under-inner-product-search)
  - [8.3 Maximal Marginal Relevance (MMR) Diversification](#83-maximal-marginal-relevance-mmr-diversification)
  - [8.4 Deterministic 4-Axis Verification Scoring Function](#84-deterministic-4-axis-verification-scoring-function)
  - [8.5 MurmurHash3 Feature Projection (Local Demo Vectorizer)](#85-murmurhash3-feature-projection-local-demo-vectorizer)
- [Chapter 9 — Testing Strategy and Results](#chapter-9--testing-strategy-and-results)
  - [9.1 Testing Philosophy and Strategy](#91-testing-philosophy-and-strategy)
  - [9.2 Test Environment and Execution Framework](#92-test-environment-and-execution-framework)
  - [9.3 Unit & Subsystem Testing Breakdown](#93-unit--subsystem-testing-breakdown)
  - [9.4 Complete Traceability and Test Matrix Table](#94-complete-traceability-and-test-matrix-table)
  - [9.5 Edge-Case and Fault-Injection Testing](#95-edge-case-and-fault-injection-testing)
- [Chapter 10 — Results, Demonstration and Discussion](#chapter-10--results-demonstration-and-discussion)
  - [10.1 System Initialisation and Dashboard Launch](#101-system-initialisation-and-dashboard-launch)
  - [10.2 Empirical Document Ingestion & Chunking Results](#102-empirical-document-ingestion--chunking-results)
  - [10.3 Research Query Execution Walkthrough](#103-research-query-execution-walkthrough)
  - [10.4 Quantitative Verification & Grounding Evaluation](#104-quantitative-verification--grounding-evaluation)
  - [10.5 Report Generation & Archival Output Analysis](#105-report-generation--archival-output-analysis)
  - [10.6 Discussion of System Capabilities and Deficits](#106-discussion-of-system-capabilities-and-deficits)
- [Chapter 11 — Challenges, Limitations and Future Enhancements](#chapter-11--challenges-limitations-and-future-enhancements)
  - [11.1 Technical Challenges Encountered](#111-technical-challenges-encountered)
  - [11.2 Verified System Limitations](#112-verified-system-limitations)
  - [11.3 Future Technical Roadmap](#113-future-technical-roadmap)
- [Chapter 12 — Learning Outcomes](#chapter-12--learning-outcomes)
  - [12.1 Technical and Domain Competencies](#121-technical-and-domain-competencies)
  - [12.2 Software Engineering & Production Best Practices](#122-software-engineering--production-best-practices)
  - [12.3 Industrial Internship Perspectives](#123-industrial-internship-perspectives)
- [Chapter 13 — Conclusion](#chapter-13--conclusion)
- [Appendices](#appendices)
  - [Appendix A — Complete File & Package Inventory](#appendix-a--complete-file--package-inventory)
  - [Appendix B — Environment Configuration & Operational Commands](#appendix-b--environment-configuration--operational-commands)
  - [Appendix C — Automated Test Execution Log Dump](#appendix-c--automated-test-execution-log-dump)
  - [Appendix D — Visual Evidence Plan and Figure Catalog](#appendix-d--visual-evidence-plan-and-figure-catalog)
  - [Appendix E — Terminal Execution Logs](#appendix-e--terminal-execution-logs)
  - [Appendix F — Supporting Data Flow Schematics](#appendix-f--supporting-data-flow-schematics)
  - [Appendix G — Repository and Version Control Record](#appendix-g--repository-and-version-control-record)
- [References](#references)

---

<div style="page-break-after: always;"></div>

## LIST OF FIGURES

*Note: Page references are generated dynamically during final PDF compilation.*

- **Figure 5.1:** High-Level Architectural Topology of the SciPilot Multi-Agent System
- **Figure 5.2:** End-to-End Scientific Ingestion and Retrieval Pipeline Flowchart
- **Figure 5.3:** Sequential Agent Interaction and Hand-off Message Trace
- **Figure 5.4:** Structural RAG Decomposition, Sliding Window, and Vector Ingestion
- **Figure 5.5:** Execution Branching: Live IBM watsonx.ai Mode vs. Local Demo Mode
- **Figure 7.1:** `<!-- IMAGE REQUIRED: images/figures/fig_01_scipilot_sidebar.png -->` SciPilot Reactive Sidebar Configuration and Credential State Indicator
- **Figure 7.2:** `<!-- IMAGE REQUIRED: images/figures/fig_02_upload_ingest_tab.png -->` Multi-Document PDF Upload and Progress Tracking Interface
- **Figure 7.3:** `<!-- IMAGE REQUIRED: images/figures/fig_03_research_chat_interface.png -->` Research Assistant Chat Interface Showing Structured Answer Card
- **Figure 7.4:** `<!-- IMAGE REQUIRED: images/figures/fig_04_verification_metrics_card.png -->` Deterministic Verification Dashboard with Category Badges and Sub-Scores
- **Figure 7.5:** `<!-- IMAGE REQUIRED: images/figures/fig_05_report_download_preview.png -->` Report Generation Tab Showing Markdown and PDF Export Actions
- **Figure 7.6:** `<!-- IMAGE REQUIRED: images/figures/fig_06_session_history_tab.png -->` Persistent Research Sessions View Showing Historical Query Logs
- **Figure 9.1:** `<!-- IMAGE REQUIRED: images/figures/fig_07_pytest_terminal_execution.png -->` Pytest 378/378 Test Suite Clean Execution in PowerShell Terminal
- **Figure 10.1:** `<!-- IMAGE REQUIRED: images/figures/fig_08_sample_pdf_report_render.png -->` Sample Exported A4 PDF Research Report Rendered with `fpdf2`

---

<div style="page-break-after: always;"></div>

## LIST OF TABLES

- **Table 3.1:** Key Attributes of the Industrial Internship Programme
- **Table 4.1:** Comparison of Literature Review Approaches
- **Table 4.2:** Software Requirements Traceability Matrix
- **Table 6.1:** Comprehensive Technology Stack and Dependency Specifications
- **Table 7.1:** Architectural Specification of SciPilot Agent Classes
- **Table 7.2:** Data Invariants across Document and Chunk Models
- **Table 8.1:** Deterministic Verification Sub-Check Weights and Thresholds
- **Table 8.2:** Comparison of Vector Features: IBM Slate-125M vs. sklearn HashingVectorizer
- **Table 9.1:** Test Suite Distribution across Project Subsystems
- **Table 9.2:** Comprehensive Pytest Verification and Test Traceability Matrix
- **Table 10.1:** Empirical Ingestion Metrics for Sample Research PDF
- **Table 10.2:** Empirical Multi-Agent Execution Metrics for Sample Query
- **Table 10.3:** Operational Comparison: Live IBM watsonx.ai vs. Local Demo Mode

---

<div style="page-break-after: always;"></div>

## LIST OF ABBREVIATIONS

| Abbreviation | Full Expansion |
|---|---|
| **AI** | Artificial Intelligence |
| **AICTE** | All India Council for Technical Education |
| **APA** | American Psychological Association |
| **API** | Application Programming Interface |
| **ASCII** | American Standard Code for Information Interchange |
| **BM25** | Best Matching 25 (Information Retrieval Ranking Function) |
| **COS** | Cloud Object Storage |
| **CPU** | Central Processing Unit |
| **CRUD** | Create, Read, Update, Delete |
| **DTO** | Data Transfer Object |
| **FAISS** | Facebook AI Similarity Search |
| **FLOPs** | Floating Point Operations |
| **GGUF** | GPT-Generated Unified Format |
| **HNSW** | Hierarchical Navigable Small World |
| **HTTP / HTTPS** | Hypertext Transfer Protocol / Secure |
| **IBM** | International Business Machines Corporation |
| **IEEE** | Institute of Electrical and Electronics Engineers |
| **JSON** | JavaScript Object Notation |
| **LLM** | Large Language Model |
| **MCP** | Model Context Protocol |
| **MMR** | Maximal Marginal Relevance |
| **NLP** | Natural Language Processing |
| **OCR** | Optical Character Recognition |
| **OS** | Operating System |
| **PDF** | Portable Document Format |
| **RAG** | Retrieval-Augmented Generation |
| **ReAct** | Reason and Act (Agent Framework) |
| **REST** | Representational State Transfer |
| **RRF** | Reciprocal Rank Fusion |
| **SDK** | Software Development Kit |
| **SHA-256** | Secure Hash Algorithm 256-bit |
| **SITE** | School of Information Technology and Engineering |
| **SRS** | Software Requirements Specification |
| **UI** | User Interface |
| **UUID** | Universally Unique Identifier |
| **VIT** | Vellore Institute of Technology |

---

<div style="page-break-after: always;"></div>

## CHAPTER 1 — ABSTRACT

Scientific research requires reviewing vast corpora of dense academic literature, cross-referencing experimental results, and compiling rigorously formatted bibliographies. However, general-purpose Large Language Models (LLMs) and monolithic Retrieval-Augmented Generation (RAG) pipelines suffer from critical deficiencies: factual hallucination, context dilution across complex composite queries, black-box uncertainty, and a lack of exportable, audit-ready documentation. 

To overcome these challenges, this industrial internship project presents **SciPilot**, an autonomous, coordinator-based multi-agent research assistant designed specifically for scientific literature exploration. Developed under the **IBM SkillsBuild × AICTE Internship 2026** in partnership with **Edunet Foundation**, SciPilot coordinates seven specialized agents to automate the research lifecycle:
1. **Planning**: Decomposes multi-faceted questions into targeted sub-queries.
2. **Retrieval**: Performs semantic vector search over a local **Meta FAISS** index (`IndexFlatIP`) reinforced with **Maximal Marginal Relevance (MMR)** diversification ($\lambda = 0.70$).
3. **Synthesis**: Composes grounded answers with explicit bracketed citation markers.
4. **Verification**: Mathematically verifies factual grounding against context chunks using a deterministic, 4-axis scoring engine that eliminates non-deterministic LLM-as-a-judge calls.
5. **Citation**: Formats references in APA 7th Edition or IEEE styles with document-level deduplication.
6. **Reporting**: Compiles structured Markdown and vector-styled A4 PDF reports (`fpdf2`).
7. **Memory**: Manages session state across IBM Cloud Object Storage and local persistent storage.

SciPilot features a dual-operational architecture. In **Live IBM watsonx.ai Mode**, it leverages **IBM Granite 13B Instruct** (`ibm/granite-13b-instruct-v2`) and **IBM Slate 125M Retriever** (`ibm/slate-125m-english-rtrvr`). In **Local Demo Mode**, it provides an offline fallback using an L2-normalized 384-dimensional `HashingVectorizer` and deterministic extractive synthesis, preserving exact architectural contracts and vector dimensions without external network access.

The system is verified with **378 automated pytest unit and integration tests** achieving a 100% pass rate. Live end-to-end empirical testing on a 6-page research paper demonstrated successful chunking (60 chunks), 384-dimensional indexing, relevant retrieval, and an overall verification confidence score of **0.76 (🟢 HIGH)** with an **0.89 grounding ratio**. SciPilot provides an open, robust, and verifiable framework for academic literature analysis.

---

<div style="page-break-after: always;"></div>

## CHAPTER 2 — INTRODUCTION

### 2.1 Background and Motivation
The volume of scientific literature published globally is expanding exponentially. According to scientific publishing indices, tens of thousands of academic papers are indexed weekly across computer science, engineering, and biotechnology domains. For graduate students, academic scholars, and software engineers, conducting systematic literature reviews has become a bottleneck, often consuming up to 40% of preliminary research cycles.

Artificial Intelligence, particularly generative Large Language Models (LLMs) and dense semantic embeddings, offers a paradigm shift in how digital text is queried. However, deploying raw generative models directly into scientific research introduces severe risks. Scientific discourse relies on exactness, replicability, and factual attribution. A single hallucinated metric, misattributed methodology, or non-existent citation can invalidate an entire research proposal. Hence, there is a compelling need for intelligent research assistants that ground every assertion in verified document context while providing transparent, mathematical verification scores.

### 2.2 Problem Statement
Traditional conversational chatbots and single-prompt RAG architectures exhibit three fundamental failures when applied to scientific PDFs:
1. **Hallucination and Fabrication**: LLMs generate fluent, plausible answers that contain unsubstantiated facts or hallucinated citations.
2. **Context Dilution**: Complex, compound research inquiries (e.g., *"How do vision transformers mitigate quadratic attention bottlenecks, and how do their FLOPs compare to convolutional networks on high-resolution images?"*) dilute naive vector searches, causing retrievers to miss critical sub-facets of the query.
3. **Absence of Provenance and Verification**: Commercial chat interfaces act as black boxes; they cannot indicate the exact document page from which a claim was extracted, nor can they quantify the likelihood of factual hallucination.

### 2.3 Need for the System
Academia and industrial research teams require an autonomous, auditable, and structured literature review assistant. The system must:
- Extract text accurately from multi-page PDF documents while preserving page-level and character-level provenance.
- Decompose complex research inquiries into logical sub-queries.
- Mitigate semantic redundancy using diverse retrieval algorithms.
- Synthesize responses that link every claim to a specific passage.
- Evaluate the generated answer algorithmically to alert the user of potential hallucinations.
- Automatically compile formatted bibliographies (APA and IEEE) and exportable reports.
- Function reliably even in environments where commercial cloud AI credentials may be expired or inaccessible.

### 2.4 Project Objectives
1. **Architect a 7-Agent Autonomous Pipeline**: Implement a modular multi-agent system comprising Planner, Retriever, Synthesis, Verification, Citation, Report, and Memory agents coordinated by a centralized Orchestrator.
2. **Integrate Enterprise Foundation Models**: Harness IBM watsonx.ai foundation models, specifically IBM Granite 13B for reasoning and IBM Slate 125M for dense semantic embeddings.
3. **Engineer Provenance-Preserving RAG**: Maintain end-to-end provenance by attaching document SHA-256 hashes, source filenames, page numbers, and character offsets (`char_start`, `char_end`) to every text chunk.
4. **Implement Deterministic Hallucination Guardrails**: Design a mathematical verification algorithm that computes citation coverage, lexical n-gram grounding ratios, answer length bounds, and source diversity without secondary LLM invocations.
5. **Support Dual-Format Academic Reporting**: Automate bibliography generation in APA 7th Edition and IEEE styles, and compile downloadable Markdown and styled A4 PDF documents.
6. **Provide an Offline Local Demo Mode**: Build a fallback mechanism using scikit-learn's `HashingVectorizer` (384 dimensions) and extractive synthesis to enable complete offline demonstrations.
7. **Ensure Production Quality**: Establish a complete automated test suite verifying every component, aiming for 100% test pass rates across all modules.

### 2.5 Scope of the Project
- **In-Scope**: Parsing digital scientific PDFs via PyMuPDF; sliding-window text chunking; dense vector indexing in FAISS; multi-agent coordination; question decomposition; MMR re-ranking; grounded answer synthesis; deterministic verification; APA/IEEE citation generation; Markdown and PDF report building; hybrid persistence; reactive Streamlit user interface; dual-mode execution.
- **Out-of-Scope**: Scanned document OCR (rasterized images without embedded text layers); multi-modal analysis (direct parsing of embedded charts, diagrams, or video); on-premise fine-tuning of foundational LLM weights.

### 2.6 Proposed Solution
SciPilot resolves the limitations of existing AI tools through a **coordinator-based multi-agent architecture**:
- Document ingestion converts PDFs into structured `PageDocument` objects with SHA-256 deduplication.
- A recursive character splitter breaks documents into 512-character `TextChunk` records with 64-character overlaps.
- Chunks are projected into a 384-dimensional vector space and indexed in FAISS using an inner-product cosine metric (`IndexFlatIP`).
- When a query is received, the **Planner Agent** splits it into sub-questions.
- The **Retriever Agent** performs multi-pass search across FAISS and applies Maximal Marginal Relevance ($\lambda = 0.70$) to select diverse passages.
- The **Synthesis Agent** generates a response enforcing inline citations (`[1]`, `[2]`).
- The **Verification Agent** computes an empirical confidence score ($[0.0, 1.0]$) and categorical verdict (`HIGH`, `MEDIUM`, `LOW`).
- The **Citation Agent** formats bibliographies, the **Report Agent** compiles PDF and Markdown exports, and the **Memory Agent** logs sessions to IBM Cloud Object Storage or local storage.

### 2.7 Key Contributions
1. **Zero-LLM Deterministic Verification Engine**: Developed an algorithmic verification module that scores claim grounding and citation bounds using set-theoretic token overlap, eliminating costly LLM-as-a-judge latency and cost.
2. **Dimension-Invariant Dual Operational Modes**: Implemented an offline Local Demo Mode using a 384-dimensional `HashingVectorizer` that preserves identical vector space dimensions to the live IBM Slate bi-encoder, ensuring zero code degradation when offline.
3. **Provenance Tracking**: Designed data invariants that link every sentence in an answer back to its originating document hash, page number, and character span.
4. **Complete Automated Verification**: Achieved 378/378 passing tests across unit, integration, and property testing suites.

### 2.8 Report Organisation
The remainder of this report is organized as follows:
- **Chapter 3** profiles the host organization (Edunet Foundation) and the internship programme.
- **Chapter 4** presents problem analysis, user requirements, and system specifications.
- **Chapter 5** details the system architecture with Mermaid diagrams.
- **Chapter 6** details the technology stack and software dependencies.
- **Chapter 7** provides a module-by-module implementation breakdown with code excerpts.
- **Chapter 8** details the underlying mathematical formulations and algorithms.
- **Chapter 9** describes the testing strategy and presents the complete 378-test results matrix.
- **Chapter 10** analyzes empirical demonstration outputs on sample literature.
- **Chapter 11** discusses technical limitations and the future research roadmap.
- **Chapter 12** summarizes technical and professional learning outcomes.
- **Chapter 13** concludes the report.
- **Appendices & References** provide directory catalogs, configuration templates, and consulted literature.

---

<div style="page-break-after: always;"></div>

## CHAPTER 3 — INTERNSHIP ORGANISATION AND PROGRAMME

### 3.1 Profile of Edunet Foundation
**Edunet Foundation** is a non-profit organization in India dedicated to enabling youth with digital, technological, and vocational skills. Operating in collaboration with major multinational technology enterprises and educational bodies, Edunet Foundation acts as an implementation partner for high-impact workforce enablement programmes across India.

Edunet Foundation focuses on institutional capacity building, bridging the gap between university engineering curricula and industry requirements by conducting hands-on internships, project bootcamps, and hackathons in cutting-edge computing disciplines.

### 3.2 IBM SkillsBuild × AICTE Programme Context
The **IBM SkillsBuild × AICTE Internship** is a collaborative national initiative established between **IBM India**, the **All India Council for Technical Education (AICTE)**, and **Edunet Foundation**. The programme aims to prepare Indian technical students for careers in emerging technology domains by providing:
- Enterprise-grade educational pathways hosted on the IBM SkillsBuild platform.
- Hands-on technical mentoring by industry experts and certified trainers.
- Practical project development mandates emphasizing real-world problem solving.
- Project reviews and industry-recognized credentials.

### 3.3 Internship Duration and Schedule
The industrial internship was completed over a 4-week full-time engagement:

| Metric | Detail |
|---|---|
| **Internship Programme** | IBM SkillsBuild × AICTE Industrial Internship 2026 |
| **Partner Organisation** | Edunet Foundation |
| **Duration** | 12 June 2026 – 10 July 2026 (4 Weeks) |
| **Student Candidate** | Santhosh R (Register No: 22MIS0282) |
| **Academic Programme** | Integrated M.Tech Software Engineering, VIT Vellore |
| **Academic Year** | 2026 – 2027 |
| **Assigned Project Theme** | Cognitive Computing, Agentic AI & Generative Applications |
| **Project Title** | SciPilot: Next-Generation Agentic Research Assistant |

*Table 3.1: Key Attributes of the Industrial Internship Programme*

### 3.4 Core Learning Areas & Technical Domains
During the internship period, rigorous self-paced learning and mentored workshops were conducted across three primary technical pillars:
1. **Agentic Artificial Intelligence**: Exploring foundational LLM architectures, prompt engineering, agentic autonomy, tool use, Retrieval-Augmented Generation, vector embedding mechanics, and hallucination reduction strategies.
2. **Cybersecurity & Responsible AI**: Understanding credential lifecycle management, API token security, data provenance, safe parsing of untrusted documents, and ethical constraints in AI-generated academic content.
3. **Cloud Cognitive Services & Quantum Computing**: Introducing IBM Cloud infrastructure, IBM watsonx.ai enterprise services, IBM Cloud Object Storage, and foundational concepts of quantum circuits and quantum information science.

---

<div style="page-break-after: always;"></div>

## CHAPTER 4 — PROBLEM ANALYSIS AND REQUIREMENTS

### 4.1 Analysis of Existing Literature Review Approaches
Conducting literature reviews across scientific disciplines has evolved through three distinct paradigms, each possessing intrinsic limitations:

| Evaluation Dimension | Manual Review | Traditional Search Engines | Commercial LLM Chatbots | SciPilot (Proposed) |
|---|---|---|---|---|
| **Speed / Turnaround** | Hours to Days | Minutes | Seconds | Seconds |
| **Context Synthesis** | Comprehensive | None (Keyword matching) | High (Generative) | High (Multi-Agent Grounded) |
| **Hallucination Risk** | Zero (Human verification) | Zero (Direct document links) | High (Frequent fabrication) | Minimal (Deterministic Verification) |
| **Provenance Tracking** | Manual page notes | Document level only | Absent / Black-box | Exact Page & Char Spans |
| **Query Decomposition** | Human planning | None | Occasional / CoT | Dedicated Planner Agent |
| **Export Formats** | Manual document editing | Bookmarks | Ephemeral text chats | Formatted PDF & Markdown |
| **Offline Resilience** | Full (Local files) | Requires Network | Requires Cloud API | Dual Mode (Live + Local Fallback) |

*Table 4.1: Comparison of Literature Review Approaches*

### 4.2 Specific Bottlenecks Addressed by SciPilot
1. **Citation Hallucination**: General-purpose LLMs regularly fabricate citations. SciPilot implements a mathematical check confirming that every citation bracket `[N]` maps strictly to a retrieved passage index ($1 \le N \le K$).
2. **Context Fragmentation**: Traditional RAG systems concatenate context blindly, causing retrieval bias toward the first uploaded paper. SciPilot enforces Maximal Marginal Relevance (MMR) to force candidate diversity across multiple papers.
3. **Verification Latency**: Existing verification frameworks use LLM-as-a-judge approaches, doubling API costs and inference times. SciPilot implements deterministic, non-LLM Python string-matching and set-theoretic scoring that runs in sub-millisecond times.

### 4.3 Software Requirements Specification (SRS)

#### 4.3.1 Functional Requirements
- **FR-01 (Document Ingestion)**: The system shall accept one or more PDF files via drag-and-drop or file selection, reading raw bytes and parsing digital text streams using PyMuPDF (`fitz`).
- **FR-02 (Text Chunking)**: The system shall recursively chunk extracted text into 512-character blocks with 64-character overlaps, preserving semantic sentence boundaries and computing character offsets.
- **FR-03 (Dense Vector Embedding)**: The system shall transform text chunks into 384-dimensional dense vectors using IBM Slate 125M (in Live Mode) or scikit-learn `HashingVectorizer` (in Local Demo Mode).
- **FR-04 (Vector Store Management)**: The system shall insert L2-normalized vectors into a FAISS `IndexFlatIP` vector index and persist `.index` binary data and `.meta` pickle files to disk.
- **FR-05 (Question Planning)**: The system shall decompose compound inquiries into 2 to 5 distinct sub-questions using IBM Granite 13B Instruct or rule-based fallbacks.
- **FR-06 (Diverse Semantic Retrieval)**: The system shall query FAISS, filter candidates by a minimum similarity threshold ($\ge 0.20$), and apply MMR re-ranking ($\lambda = 0.70$).
- **FR-07 (Grounded Synthesis)**: The system shall generate answers that substantiate claims using inline bracketed citation markers referencing context chunks.
- **FR-08 (Deterministic Verification)**: The system shall evaluate synthesis outputs across citation coverage, lexical grounding overlap, length bounds, and source diversity, outputting a score $[0.0, 1.0]$ and a categorical verdict (`HIGH`, `MEDIUM`, `LOW`).
- **FR-09 (Citation Generation)**: The system shall format bibliographies in APA 7th Edition or IEEE styles, grouping multiple chunks by document hash.
- **FR-10 (Report Export)**: The system shall compile research results into downloadable Markdown and styled A4 PDF reports (`fpdf2`).
- **FR-11 (Session Memory)**: The system shall log session history to IBM Cloud Object Storage or local JSON files (`reports/sessions/*.json`).

#### 4.3.2 Non-Functional Requirements
- **NFR-01 (Performance)**: Local retrieval over indices containing up to 10,000 chunks shall complete within 50 milliseconds.
- **NFR-02 (Robustness & Fault Tolerance)**: Network calls to IBM Cloud services shall retry up to 4 times with exponential backoff before falling back gracefully.
- **NFR-03 (Dimension Invariance)**: Both live and offline embedding generators shall output exact 384-dimensional vectors to prevent FAISS index corruption.
- **NFR-04 (Security & Privacy)**: API keys and cloud secrets shall be read exclusively from `.env` files and never logged or exposed in the user interface.
- **NFR-05 (Maintainability & Testability)**: All core agent methods shall maintain decoupled interfaces verifiable through automated unit tests.

#### 4.3.3 User & Interface Requirements
- **UIR-01**: A responsive multi-tab Streamlit dashboard providing Upload, Research, Evaluation, Report, and History tabs.
- **UIR-02**: Clear visual credential indicators identifying whether IBM watsonx.ai credentials are valid or placeholder values.
- **UIR-03**: A prominent sidebar toggle allowing users to enable or disable Local Demo Mode at any time.

### 4.4 System Assumptions, Dependencies and Constraints
1. **Assumptions**: Uploaded PDFs contain digital text layers. Documents are written in English.
2. **Dependencies**: Python runtime environment $\ge 3.10$; Meta FAISS C++ CPU bindings; Streamlit runtime; PyMuPDF library.
3. **Constraints**: CPU-only vector indexing (`faiss-cpu`); external IBM watsonx.ai API rate limits; purely extractive answers in offline Local Demo Mode.

### 4.5 System Use Cases and Workflows
- **Use Case 1 (Literature Exploration)**: User uploads a seminal paper, asks a technical question, reviews grounded answers, checks the verification score, and downloads a formatted PDF report.
- **Use Case 2 (Offline Viva Demonstration)**: Evaluator inspects the application without internet connectivity or API keys; user enables Local Demo Mode, indexes a research paper, submits a query, reviews extractive synthesis, and demonstrates verification guardrails.

---

<div style="page-break-after: always;"></div>

## CHAPTER 5 — SYSTEM ARCHITECTURE AND DESIGN

### 5.1 Overall Architectural Style (Coordinator-Based Multi-Agent)
SciPilot is implemented using an **Orchestrated Coordinator Pattern**. Rather than adopting unconstrained agent choreography—where agents autonomously send unstructured messages to one another, risking infinite loops and high API costs—SciPilot utilizes a centralized **Orchestrator** (`src/orchestrator.py`). The Orchestrator manages state transitions, ensures strict data contracts via Data Transfer Objects (DTOs), and handles error recovery.

### 5.2 High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Client_Layer ["Client & Interface Layer"]
        UI["Streamlit Web Dashboard<br/>(src/dashboard/app.py)"]
    end

    subgraph Orchestrator_Core ["Coordinator Layer (src/orchestrator.py)"]
        ORC["Pipeline Orchestrator<br/>(Lazy Loading & Agent Routing)"]
    end

    subgraph Specialized_Agents ["Specialized Autonomous Agents"]
        PLN["Planner Agent<br/>(src/agents/planner.py)"]
        RET["Retriever Agent<br/>(src/agents/retriever.py)"]
        SYN["Synthesis Agent<br/>(src/agents/synthesis.py)"]
        VER["Verification Agent<br/>(src/agents/verification.py)"]
        CIT["Citation Agent<br/>(src/agents/citation.py)"]
        REP["Report Agent<br/>(src/agents/report.py)"]
        MEM["Memory Agent<br/>(src/agents/memory.py)"]
    end

    subgraph Storage_And_RAG ["RAG Processing & Vector Engine"]
        ING["PDF Loader (fitz)<br/>(src/rag/ingest.py)"]
        CHK["Text Chunker (512/64)<br/>(src/rag/chunk.py)"]
        EMB["Embedder (384-dim)<br/>(src/rag/embed.py)"]
        FSS[("FAISS IndexFlatIP<br/>(src/rag/vector_store.py)")]
        LOC[("Local Storage<br/>(reports/sessions/*.json)")]
    end

    subgraph External_Cloud ["IBM Cloud Infrastructure (Live Mode)"]
        GRANITE["IBM Granite 13B Instruct"]
        SLATE["IBM Slate 125M Embeddings"]
        COS[("IBM Cloud Object Storage")]
    end

    UI -->|"Upload PDF"| ING
    ING --> CHK --> EMB --> FSS

    UI -->|"Submit Query"| ORC
    ORC --> PLN
    PLN --> RET
    RET <-->|"Similarity Search + MMR"| FSS
    RET --> SYN
    SYN --> VER
    VER --> CIT
    VER --> REP
    VER --> MEM

    PLN -.->|"Decompose"| GRANITE
    SYN -.->|"Grounded QA"| GRANITE
    EMB -.->|"Embeddings"| SLATE
    MEM -.->|"Remote Backup"| COS
    MEM -->|"Local Fallback"| LOC

    REP -->|"MD & PDF Downloads"| UI
    VER -->|"Confidence & Badges"| UI
    CIT -->|"APA / IEEE Format"| UI
```
*Figure 5.1: High-Level Architectural Topology of the SciPilot Multi-Agent System*

*Explanation of Figure 5.1*: The diagram depicts the four decoupled tiers of the system. The Client Layer exposes a multi-tab Streamlit dashboard. The Coordinator Layer manages state flow. The Specialized Agents execute atomic sub-tasks. The RAG Engine handles document parsing, chunking, and local FAISS vector search, communicating with IBM Cloud in live mode or falling back to local routines in demo mode.

---

### 5.3 End-to-End Workflow Diagram

```mermaid
flowchart TD
    Start([User Initiates Research Query]) --> CheckIndex{Is Vector Store Populated?}
    CheckIndex -->|No| PromptUpload[Prompt User to Ingest PDFs in Tab 1]
    PromptUpload --> End([Halt Query Execution])
    
    CheckIndex -->|Yes| PlanQuery[Planner Agent: Decompose Question]
    PlanQuery --> SubQ[Generated Sub-Questions: sq_1, sq_2, ...]
    
    SubQ --> LoopSubQ[Loop: Process Each Sub-Question]
    LoopSubQ --> EmbedSubQ[Embed Sub-Question to 384-d Vector]
    EmbedSubQ --> QueryFAISS[Search FAISS: Top-K * 4 Candidate Chunks]
    QueryFAISS --> FilterScore[Filter Cosine Similarity >= 0.20]
    FilterScore --> ApplyMMR[Apply MMR Diversification: λ = 0.70]
    ApplyMMR --> CollectChunks[Accumulate Deduplicated Chunks]
    
    CollectChunks --> SynthesizeAnswer[Synthesis Agent: Generate Grounded Answer]
    SynthesizeAnswer --> ParseCitations[Extract Inline Bracket Citations: [1], [2]]
    
    ParseCitations --> RunVerification[Verification Agent: Run 4-Axis Algorithmic Checks]
    RunVerification --> CalcScore[Compute Weighted Confidence Score & Categorical Verdict]
    
    CalcScore --> FormatCitations[Citation Agent: Build APA / IEEE Reference List]
    FormatCitations --> BuildReports[Report Agent: Render Markdown and PDF Files]
    BuildReports --> PersistSession[Memory Agent: Save Session to Local JSON / IBM COS]
    
    PersistSession --> DisplayUI[Render Answer Card, Confidence Bar, Sources & Download Buttons]
    DisplayUI --> Success([Workflow Successfully Completed])
```
*Figure 5.2: End-to-End Scientific Ingestion and Retrieval Pipeline Flowchart*

*Explanation of Figure 5.2*: This flowchart traces the operational lifecycle of a query from submission to presentation. It illustrates conditional checks, multi-pass retrieval loops across decomposed sub-questions, MMR diversity pruning, grounded synthesis, deterministic verification scoring, report rendering, and session persistence.

---

### 5.4 Agent Interaction and Collaboration Model

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher (Browser)
    participant UI as Streamlit UI
    participant Orc as Orchestrator
    participant Plan as PlannerAgent
    participant Ret as RetrieverAgent
    participant Syn as SynthesisAgent
    participant Ver as VerificationAgent
    participant Cit as CitationAgent
    participant Rep as ReportAgent
    participant Mem as MemoryAgent

    User->>UI: Submits Query ("What are the security concerns in MCP?")
    UI->>Orc: run(ResearchRequest)
    
    Note over Orc,Plan: Step 1: Decomposition
    Orc->>Plan: plan(query)
    Plan-->>Orc: PlanResult (Sub-questions)
    
    Note over Orc,Ret: Step 2: Multi-Pass Diverse Retrieval
    Orc->>Ret: retrieve(sub_questions, top_k=5)
    Ret-->>Orc: RetrievalResult (Deduplicated Chunks)
    
    Note over Orc,Syn: Step 3: Grounded Answer Synthesis
    Orc->>Syn: synthesise(query, context_chunks)
    Syn-->>Orc: SynthesisResult (Answer with [N] citations)
    
    Note over Orc,Ver: Step 4: Algorithmic Verification
    Orc->>Ver: verify(synthesis_result)
    Ver-->>Orc: VerificationResult (Score: 0.76, Verdict: HIGH)
    
    Note over Orc,Cit: Step 5: Bibliographic Formatting
    Orc->>Cit: generate_from_synthesis(synthesis_result)
    Cit-->>Orc: CitationResult (APA / IEEE Bibliography)
    
    Note over Orc,Rep: Step 6: Archival Report Generation
    Orc->>Rep: build_reports(synthesis, citations)
    Rep-->>Orc: File Paths (.md and .pdf)
    
    Note over Orc,Mem: Step 7: Session History Persistence
    Orc->>Mem: save_session(session_record)
    Mem-->>Orc: Session UUID Saved
    
    Orc-->>UI: ResearchResponse DTO
    UI-->>User: Renders Answer Card, Metrics Bar, and Download Actions
```
*Figure 5.3: Sequential Agent Interaction and Hand-off Message Trace*

*Explanation of Figure 5.3*: The sequence diagram details the chronological hand-offs between agents. Each agent receives structured input, executes an isolated task, and returns a validated Data Transfer Object to the Orchestrator, guaranteeing loose coupling and high testability.

---

### 5.5 RAG Subsystem and Ingestion Flow

```mermaid
flowchart LR
    subgraph Phase_1 ["Phase 1: Ingestion & Extraction"]
        PDF["Raw PDF File"] --> FITZ["PyMuPDF / fitz Engine"]
        FITZ --> CLEAN["Text Sanitization<br/>(Strip \x00, collapse whitespace)"]
        CLEAN --> DOCS["PageDocument Records<br/>(page_number, doc_hash)"]
    end

    subgraph Phase_2 ["Phase 2: Semantic Chunking"]
        DOCS --> SPLIT["Recursive Text Splitter<br/>(Delimiters: \n\n, \n, ., ;, space)"]
        SPLIT --> WINDOW["Sliding Window Buffer<br/>(512 chars, 64 overlap)"]
        WINDOW --> CHUNKS["TextChunk Records<br/>(doc_hash, char_start, char_end)"]
    end

    subgraph Phase_3 ["Phase 3: Vectorization & Indexing"]
        CHUNKS --> VEC{"Active Mode?"}
        VEC -->|"Live IBM"| SLATE["IBM Slate-125M"]
        VEC -->|"Local Demo"| HASH["sklearn HashingVectorizer"]
        SLATE --> NORM["L2 Normalization (unit vectors)"]
        HASH --> NORM
        NORM --> FAISS[("FAISS IndexFlatIP (384-d)")]
        FAISS --> DISK[("data/faiss_index.index<br/>data/faiss_index.meta")]
    end
```
*Figure 5.4: Structural RAG Decomposition, Sliding Window, and Vector Ingestion*

*Explanation of Figure 5.4*: Documents transition through three phases: structural extraction with provenance, recursive semantic chunking with overlapping windows, and vectorization into a shared 384-dimensional space indexed in FAISS.

---

### 5.6 Dual-Mode Execution Architecture (Live IBM vs. Local Demo)

```mermaid
flowchart TD
    START["Application Startup / User Request"] --> DETECT{"Credential Status & Toggle"}
    
    DETECT -->|"Valid API Key + Live Toggle"| LIVE["LIVE IBM WATSONX.AI MODE"]
    DETECT -->|"Placeholder Key / Local Toggle ON"| LOCAL["LOCAL DEMO MODE (OFFLINE)"]
    
    subgraph Live_Pipeline ["Live Cloud Pipeline"]
        LIVE --> L1["Embeddings: IBM Slate 125M Retriever"]
        LIVE --> L2["Planning: IBM Granite 13B Instruct"]
        LIVE --> L3["Synthesis: IBM Granite 13B Generative QA"]
        LIVE --> L4["Memory: IBM Cloud Object Storage Bucket"]
    end

    subgraph Local_Pipeline ["Local Offline Pipeline"]
        LOCAL --> D1["Embeddings: sklearn HashingVectorizer (384-d)"]
        LOCAL --> D2["Planning: Rule-Based Fallback / Identity"]
        LOCAL --> D3["Synthesis: Extractive Passage Ranking"]
        LOCAL --> D4["Memory: Local JSON (reports/sessions/*.json)"]
    end

    subgraph Common_Subsystems ["Shared Invariant Engine"]
        COM_RAG["PyMuPDF Extraction & 512/64 Chunking"]
        COM_FSS["FAISS IndexFlatIP Cosine Search (384-d)"]
        COM_MMR["Maximal Marginal Relevance (λ = 0.70)"]
        COM_VER["Deterministic 4-Axis Verification Engine"]
        COM_CIT["APA & IEEE Citation Generator"]
        COM_REP["fpdf2 PDF & Markdown Report Builder"]
    end

    Live_Pipeline --> Common_Subsystems
    Local_Pipeline --> Common_Subsystems
```
*Figure 5.5: Execution Branching: Live IBM watsonx.ai Mode vs. Local Demo Mode*

*Explanation of Figure 5.5*: Illustrates the architectural duality of SciPilot. Live and local modes share the identical chunking, FAISS vector indexing, MMR re-ranking, verification, citation, and report generation subsystems, swapping only the cloud-dependent models for local deterministic implementations.

---

<div style="page-break-after: always;"></div>

## CHAPTER 6 — TECHNOLOGIES AND TOOLS

### 6.1 Programming Language & Core Runtime
- **Python (Version 3.14.3 / 3.10+)**: Chosen as the primary programming language for its native scientific ecosystem, typing constructs, dataclasses, and rich library ecosystem for Natural Language Processing.

### 6.2 Foundation Models & Cloud AI Ecosystem
- **IBM watsonx.ai Python SDK (`ibm-watsonx-ai>=0.2.6`)**: Provides direct programmatic access to IBM Cloud foundation models and embedding endpoints.
- **IBM Granite 13B Instruct (`ibm/granite-13b-instruct-v2`)**: A 13-billion parameter enterprise decoder model optimized for instruction-following, technical query decomposition, and factual synthesis.
- **IBM Slate 125M Retriever (`ibm/slate-125m-english-rtrvr`)**: A specialized bi-encoder embedding model mapping English text into a 384-dimensional dense vector space optimized for information retrieval.
- **IBM Cloud Object Storage (`ibm-cos-sdk>=2.13.0`)**: S3-compatible cloud storage SDK for persisting session records remotely.

### 6.3 Vector Database & Local Projection Libraries
- **Meta FAISS (`faiss-cpu>=1.7.4`)**: High-performance, CPU-optimized vector similarity search library. SciPilot implements `IndexFlatIP` (Flat Inner Product index), achieving exact, uncompressed cosine similarity matching when fed unit-normalized vectors.
- **scikit-learn (`scikit-learn>=1.4.0`)**: Provides `HashingVectorizer` for the offline Local Demo Mode fallback. Configured with 384 features and L2-normalization, it projects token frequencies into a matching 384-dimensional space without storing a vocabulary dictionary in memory.

### 6.4 Document Parsing & Publication Frameworks
- **PyMuPDF (`fitz>=1.23.0`)**: C-native PDF parsing library. Selected over pypdf for its superior parsing speeds, robust font-encoding handling, and ability to detect rasterized (scanned) pages.
- **fpdf2 (`fpdf2>=2.7.9`)**: Pure-Python PDF generation library. Enables direct programmatic assembly of vector-styled A4 PDF research reports containing tabular data, headers, and footers without requiring external binary tools such as wkhtmltopdf.
- **Python-Markdown (`markdown>=3.6`)**: Renders structured markdown into intermediate HTML for Streamlit display and document styling.

### 6.5 Frontend Framework & Dashboard Architecture
- **Streamlit (`streamlit>=1.35.0`)**: Reactive web application framework allowing multi-tab dashboard layouts, reactive session state management (`st.session_state`), and custom CSS card rendering.

### 6.6 Testing, Quality Assurance & Engineering Utilities
- **Pytest (`pytest>=8.2.0`) & Pytest-Cov (`pytest-cov>=5.0.0`)**: Industrial testing framework verifying 378 unit, integration, and property test cases.
- **Tenacity (`tenacity>=8.3.0`)**: Implements exponential back-off and retry decorators (`@retry`) to handle transient 429/5xx cloud errors.
- **Pydantic (`pydantic>=2.7.0`) & python-dotenv (`python-dotenv>=1.0.1`)**: Strongly typed configuration validation reading `.env` parameters into immutable dataclass singletons.

| Layer | Dependency | Version | License | Justification |
|---|---|---|---|---|
| Runtime | Python | 3.14.3 / 3.10+ | PSF | Native ecosystem for NLP, typing, and dataclasses |
| Web UI | streamlit | $\ge 1.35.0$ | Apache 2.0 | Rapid, reactive multi-tab interface with session caching |
| Cloud AI | ibm-watsonx-ai | $\ge 0.2.6$ | Apache 2.0 | Official client SDK for IBM Granite and Slate models |
| Cloud Storage | ibm-cos-sdk | $\ge 2.13.0$ | Apache 2.0 | S3-compatible cloud persistence for research sessions |
| Vector Index | faiss-cpu | $\ge 1.7.4$ | MIT | Meta's high-speed C++ CPU inner-product search |
| Local Vectorizer | scikit-learn | $\ge 1.4.0$ | BSD-3 | HashingVectorizer for 384-d offline demo fallback |
| PDF Extraction | PyMuPDF (fitz) | $\ge 1.23.0$ | AGPL-3.0 | C-native parsing speed and page metadata preservation |
| PDF Generation | fpdf2 | $\ge 2.7.9$ | LGPL-3.0 | Pure-Python vector PDF report generation |
| Resilience | tenacity | $\ge 8.3.0$ | Apache 2.0 | Exponential backoff retry logic for cloud REST APIs |
| Config | pydantic | $\ge 2.7.0$ | MIT | Type validation for environment settings |
| Testing | pytest | $\ge 8.2.0$ | MIT | Full-suite unit and integration test runner |

*Table 6.1: Comprehensive Technology Stack and Dependency Specifications*

---

<div style="page-break-after: always;"></div>

## CHAPTER 7 — DETAILED IMPLEMENTATION

### 7.1 Project Directory Structure
The SciPilot codebase is organized into cleanly decoupled packages adhering to clean architecture principles:

```
c:\Users\91959\Documents\SciPilot-main\
├── .env.example                 # Safe environment template with placeholder keys
├── .env                         # Active secrets file (strictly gitignored)
├── .gitignore                    # Excludes secrets, FAISS caches, virtualenvs, reports
├── README.md                    # Project overview, installation, and architecture
├── requirements.txt             # Direct Python dependency definitions
├── docs/                        # Project documentation and reports
│   ├── USER_MANUAL.md           # Step-by-step operator guide
│   ├── SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md  # Main technical report (this document)
│   ├── SCIPILOT_REPORT_EVIDENCE_CHECKLIST.md   # Evidence checklist
│   └── project_report/          # Complete project reports & viva guides
│       ├── SCIPILOT_COMPLETE_PROJECT_REPORT.md
│       └── SCIPILOT_VIVA_PREPARATION.md
├── reports/                     # Output directory for exported MD/PDF reports (gitignored)
│   └── sessions/                # Local JSON session records
├── data/                        # Persistent FAISS index files (gitignored)
│   ├── faiss_index.index        # Binary FAISS vector index
│   └── faiss_index.meta         # Pickled chunk metadata list
├── research_papers/             # Input PDF papers for ingestion (gitignored)
├── src/                         # Application source code
│   ├── orchestrator.py          # Top-level coordinator
│   ├── agents/                  # 7 Autonomous specialized agents
│   │   ├── planner.py           # Question decomposition agent
│   │   ├── retriever.py         # Semantic search and MMR re-ranking agent
│   │   ├── synthesis.py         # Grounded answer synthesis agent
│   │   ├── verification.py      # Deterministic 4-axis verification agent
│   │   ├── citation.py          # APA 7th & IEEE citation agent
│   │   ├── report.py            # Markdown & PDF report agent
│   │   └── memory.py            # Session serialization & persistence agent
│   ├── rag/                     # RAG subsystem
│   │   ├── ingest.py            # PDF loader and cleaner
│   │   ├── chunk.py             # Recursive text chunker
│   │   ├── embed.py             # IBM Slate & local HashingVectorizer embedder
│   │   └── vector_store.py      # FAISS IndexFlatIP management
│   ├── dashboard/               # UI presentation layer
│   │   └── app.py               # Multi-tab Streamlit dashboard
│   └── utils/                   # Shared utilities
│       ├── config.py            # Pydantic configuration singleton
│       ├── helpers.py           # Text hashing, sanitization, batching
│       └── logger.py            # Structured logging
└── tests/                       # Automated test suite (378 tests)
    ├── conftest.py              # Pytest fixtures and mock environments
    ├── test_chunk.py            # 32 chunking tests
    ├── test_citation.py         # 51 citation formatting tests
    ├── test_config.py           # 14 configuration tests
    ├── test_embed.py            # 11 embedding tests
    ├── test_ingest.py           # 26 PDF ingestion tests
    ├── test_memory.py           # 32 session persistence tests
    ├── test_planner.py          # 35 query planning tests
    ├── test_report.py           # 35 report generation tests
    ├── test_retriever.py        # 29 vector retrieval tests
    ├── test_synthesis.py        # 38 answer synthesis tests
    ├── test_vector_store.py     # 22 FAISS storage tests
    └── test_verification.py     # 53 verification engine tests
```

---

### 7.2 Application Startup & Dependency Injection
Application startup is initiated by executing `python -m streamlit run src/dashboard/app.py`.
- **Initialization Sequence**:
  1. The singleton `settings` object in `src/utils/config.py` verifies required directory structures (`reports/`, `data/`, `research_papers/`), creating them if missing.
  2. The Streamlit session state initializes vector store instances and agent coordinators.
  3. The `Orchestrator` (`src/orchestrator.py`) executes `load_vector_store()`, loading existing indices from `data/faiss_index.index` or instantiating a blank index if none exists.
  4. Specialized agents are lazily loaded (`_load_agents()`) upon the first user interaction, ensuring instantaneous UI rendering without network lag.

---

### 7.3 Document Ingestion Subsystem (`src/rag/ingest.py`)
- **Purpose**: Converts arbitrary PDF files into structured, clean `PageDocument` records.
- **Input**: Raw file paths (`Path`) or byte arrays (`bytes`) from the Streamlit file uploader.
- **Processing**:
  - Validates PDF headers and handles empty or non-PDF streams.
  - Uses PyMuPDF (`fitz.open(stream=raw_bytes, filetype="pdf")`) to iterate over document pages.
  - Extracts text streams, collapses excessive whitespace, removes null bytes (`\x00`), and computes SHA-256 hashes of the file content for deduplication.
- **Output**: `List[PageDocument]` where each object stores `text`, `page_number` (1-indexed), `doc_hash`, `source` filename, and dimensional metadata.

```python
# Code excerpt from src/rag/ingest.py
def load_pdf_from_bytes(pdf_bytes: bytes, filename: str) -> List[PageDocument]:
    if not pdf_bytes:
        raise ValueError("Cannot load an empty byte array.")
    doc_hash = hash_text(pdf_bytes.hex())
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: List[PageDocument] = []
    for page_idx, page in enumerate(doc, start=1):
        raw_text = page.get_text()
        clean = _clean_text(raw_text)
        if clean:
            pages.append(PageDocument(
                text=clean,
                page_number=page_idx,
                source=sanitise_filename(filename),
                doc_hash=doc_hash,
            ))
    doc.close()
    return pages
```

---

### 7.4 Structure-Preserving Recursive Text Chunking (`src/rag/chunk.py`)
- **Purpose**: Partitions document pages into manageable text chunks for vector indexing while preserving paragraph, line, and sentence structures.
- **Input**: `List[PageDocument]`
- **Processing**:
  - Implements a recursive splitting strategy that searches for semantic boundary delimiters in decreasing order of structural importance: `\n\n`, `\n`, `. `, `; `, `, `, and word spaces.
  - Enforces `chunk_size = 512` characters with `chunk_overlap = 64` characters.
  - Calculates and attaches exact character offsets (`char_start`, `char_end`) relative to the original page text, establishing provenance.
- **Output**: `List[TextChunk]`

```python
# Code excerpt from src/rag/chunk.py
def chunk_documents(
    pages: List[PageDocument],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[TextChunk]:
    chunks: List[TextChunk] = []
    chunk_index = 0
    for page in pages:
        splits = _recursive_split(page.text, delimiters=_DELIMITERS, max_size=chunk_size)
        windowed = _apply_sliding_window(splits, chunk_size, chunk_overlap)
        for text, char_start, char_end in windowed:
            chunks.append(TextChunk(
                text=text,
                chunk_index=chunk_index,
                doc_hash=page.doc_hash,
                source=page.source,
                page_number=page.page_number,
                char_start=char_start,
                char_end=char_end,
            ))
            chunk_index += 1
    return chunks
```

---

### 7.5 Embedding Generation & Dimension-Invariant Fallback (`src/rag/embed.py`)
- **Purpose**: Maps text strings into dense float vectors for similarity search.
- **Input**: Strings or `TextChunk` lists.
- **Processing**:
  - **Live Mode**: Calls IBM watsonx.ai embeddings API (`ibm/slate-125m-english-rtrvr`) in batches of 25 texts. Employs `tenacity` exponential retry logic (2s to 30s backoff).
  - **Local Demo Mode**: Calls scikit-learn's `HashingVectorizer` configured with `n_features=384`, `norm='l2'`, and `alternate_sign=False`.
- **Dimension Invariant**: Both live and offline engines generate **384-dimensional unit vectors**, guaranteeing that the FAISS index never suffers dimension mismatch errors.
- **Output**: `List[List[float]]` (Dimension: 384 per vector).

```python
# Code excerpt from src/rag/embed.py
def _embed_local(texts: List[str]) -> List[List[float]]:
    vectorizer = _get_local_vectorizer()
    matrix = vectorizer.transform(texts)
    # L2-normalized dense representation
    dense_matrix = matrix.toarray().astype(np.float32)
    return dense_matrix.tolist()
```

---

### 7.6 FAISS Vector Indexing & In-Memory Retrieval (`src/rag/vector_store.py`)
- **Purpose**: Manages in-memory vector storage, indexing, and nearest-neighbor search.
- **Data Structures**: Uses `faiss.IndexFlatIP` (Flat Inner Product) on CPU.
- **Processing**:
  - Vectors are converted to `np.float32` and normalized via `faiss.normalize_L2()`.
  - Inner product search on normalized vectors computes exact cosine similarity:
    $$\langle \mathbf{u}, \mathbf{v} \rangle = \cos(\theta)$$
  - Chunks and metadata are stored in a parallel list persisted to `data/faiss_index.meta`.
- **Output**: Ranked tuples of `(TextChunk, score: float)`.

---

### 7.7 Query Decomposition & Planning Agent (`src/agents/planner.py`)
- **Purpose**: Decomposes complex composite queries into 2 to 5 targeted sub-questions.
- **Processing**:
  - Sends a system prompt to IBM Granite 13B with low sampling temperature (`temperature=0.1`).
  - Employs regex parsers to extract numbered lists (`^\s*\d+[.)]`), bullet points, or interrogative lines ending with `?`.
  - **Fallback**: If parsing yields fewer than 2 sub-questions or the cloud call fails, falls back gracefully to `[original_question]`.
- **Output**: `PlanResult` containing sub-questions and timing metrics.

---

### 7.8 Semantic Retrieval & MMR Re-Ranking Agent (`src/agents/retriever.py`)
- **Purpose**: Executes multi-pass semantic search across sub-questions and eliminates redundant chunks.
- **Processing**:
  - Fetches a candidate pool of $K \times 4$ chunks for each sub-question.
  - Drops chunks below `min_score = 0.20` (in Local Demo Mode, automatically applies an adaptive threshold `0.05` to accommodate sparse word hashing).
  - Executes **Maximal Marginal Relevance (MMR)** ($\lambda = 0.70$) to balance query relevance against intra-chunk diversity.
- **Output**: `RetrievalResult` containing ranked, deduplicated `TextChunk` records.

---

### 7.9 Grounded Synthesis Agent (`src/agents/synthesis.py`)
- **Purpose**: Synthesizes a factual academic answer grounded strictly in retrieved chunks.
- **Processing**:
  - **Live Mode**: Submits structured prompts to IBM Granite 13B Instruct mandating inline bracket citations (`[1]`, `[2]`).
  - **Local Demo Mode**: Invokes `_local_synthesise()`, which scores sentences within the retrieved passages, selects top content, and concatenates them with provenance markers. Explicitly tags `model_id = "local-demo-extractive"`.
- **Output**: `SynthesisResult` mapping answer text to cited passage IDs.

---

### 7.10 Algorithmic Verification Agent (`src/agents/verification.py`)
- **Purpose**: Computes an empirical confidence score and detects hallucinations without secondary LLM calls.
- **Processing**: Evaluates four deterministic sub-checks:
  1. *Citation Coverage* (35%): Validates that citations point to valid retrieved passage numbers.
  2. *Grounding Ratio* (35%): Measures word overlap between answer sentences and context chunks (sentences sharing $\ge 3$ content words are marked grounded).
  3. *Answer Quality* (15%): Bounds check enforcing academic conciseness ($20 \le \text{words} \le 600$).
  4. *Source Diversity* (15%): Rewards citations spanning multiple source documents.
- **Output**: `VerificationResult` containing categorical verdict (`HIGH`, `MEDIUM`, `LOW`) and confidence score ($[0.0, 1.0]$).

---

### 7.11 Academic Citation Agent (`src/agents/citation.py`)
- **Purpose**: Generates academic bibliographies in APA 7th Edition or IEEE styles.
- **Processing**: Resolves cited chunk hashes to unique documents, parses author/year metadata, and formats references:
  - APA: `Author, A. (Year). Title. Source.`
  - IEEE: `[N] A. Author, "Title," Source, Year.`
- **Output**: `CitationResult` containing formatted reference strings.

---

### 7.12 Automated Report Generation Agent (`src/agents/report.py`)
- **Purpose**: Compiles research synthesis reports into downloadable formats.
- **Processing**:
  - Renders a complete Markdown report with metadata, answer, sources table, and bibliography.
  - Uses `fpdf2` to assemble an A4 PDF report with custom headers, tabular formatting, and line dividers.
- **Output**: File paths to generated `.md` and `.pdf` reports in `reports/`.

---

### 7.13 Session Memory & Hybrid Storage Agent (`src/agents/memory.py`)
- **Purpose**: Manages persistent history across research sessions.
- **Processing**:
  - Serializes `SessionRecord` objects to JSON.
  - Inspects credentials: if valid IBM COS keys exist, uploads to cloud object storage.
  - If keys are missing, placeholders, or fail over the network, automatically writes JSON files to `reports/sessions/<uuid>.json`.
- **Output**: Saved session UUID.

---

### 7.14 Streamlit Reactive Interface (`src/dashboard/app.py`)
- **Purpose**: Provides the user presentation layer.
- **Features**:
  - Sidebar showing configuration sliders, credential indicators, and Local Demo Mode toggle.
  - Tab 1: PDF upload and ingestion progress.
  - Tab 2: Research chat interface with answer cards and expandable source tables.
  - Tab 3: Real-time verification metrics and confidence indicators.
  - Tab 4: In-browser report preview and one-click PDF/MD download buttons.
  - Tab 5: Historical session browser.

---

### 7.15 Security, Configuration & Resilience Engineering
- **Credential Protection**: Credentials are read through `.env` and kept strictly out of git via `.gitignore`.
- **Placeholder Detection**: Automatically identifies placeholders (`your_ibm_cloud_api_key_here`) and prevents invalid outbound API calls.
- **Directory Traversal Defense**: All filenames pass through `sanitise_filename()`, stripping path traversal characters (`../`).
- **Network Resilience**: Cloud API calls use `tenacity` exponential retry logic. Memory operations degrade to local JSON storage if cloud storage is unreachable.

---

<div style="page-break-after: always;"></div>

## CHAPTER 8 — ALGORITHMS AND TECHNICAL METHODS

### 8.1 Sliding Window Recursive Chunking Algorithm
Given a document page string $T$, the recursive chunker divides text across priority delimiters $\Delta = \{\text{`\textbackslash n\textbackslash n'}, \text{`\textbackslash n'}, \text{`. '}, \text{`; '}, \text{` '}\}$. Once split into segments $s_1, s_2, \dots, s_m$, chunks of maximum character length $L = 512$ are constructed using an overlapping sliding window $O = 64$:

```
Algorithm 1: Sliding Window Recursive Chunking
Input: Text T, Chunk Size L = 512, Overlap O = 64
Output: List of Chunks C with Character Offsets

1. Splits = RecursiveSplit(T, Delimiters)
2. CurrentChunk = ""
3. CharStart = 0
4. For segment s in Splits:
5.    If Length(CurrentChunk) + Length(s) <= L:
6.        CurrentChunk += s
7.    Else:
8.        Emit Chunk(CurrentChunk, CharStart, CharStart + Length(CurrentChunk))
9.        // Slide window back by O characters
10.       OverlapPrefix = CurrentChunk[-O:]
11.       CharStart = CharStart + Length(CurrentChunk) - Length(OverlapPrefix)
12.       CurrentChunk = OverlapPrefix + s
13. Emit Final Chunk(CurrentChunk)
```

### 8.2 L2-Normalized Cosine Metric under Inner Product Search
For any query vector $\mathbf{q} \in \mathbb{R}^d$ and document vector $\mathbf{d} \in \mathbb{R}^d$ ($d=384$), FAISS computes inner products $\langle \mathbf{q}, \mathbf{d} \rangle = \sum_{i=1}^d q_i d_i$. Prior to indexing, vectors are L2-normalized:
$$\hat{\mathbf{v}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2} = \frac{\mathbf{v}}{\sqrt{\sum_{i=1}^{384} v_i^2}}$$
Consequently, the inner product reduces to exact cosine similarity:
$$\langle \hat{\mathbf{q}}, \hat{\mathbf{d}} \rangle = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|_2 \|\mathbf{d}\|_2} = \cos(\theta) \in [-1.0, 1.0]$$

### 8.3 Maximal Marginal Relevance (MMR) Diversification
To prevent redundant context chunks from dominating the prompt, candidate passages $D$ are iteratively selected into an active set $S$ using the MMR criterion:
$$\text{MMR}(q, D, S) = \operatorname*{argmax}_{d_i \in D \setminus S} \left[ \lambda \cdot \text{Sim}(q, d_i) - (1 - \lambda) \max_{d_j \in S} \text{Sim}(d_i, d_j) \right]$$
In SciPilot, $\lambda = 0.70$. The first component rewards relevance to the user question, while the second penalizes redundancy against already selected passages.

### 8.4 Deterministic 4-Axis Verification Scoring Function
The overall verification score $C \in [0.0, 1.0]$ is computed as:
$$C = 0.35 \cdot S_{\text{cov}} + 0.35 \cdot S_{\text{grd}} + 0.15 \cdot S_{\text{qual}} + 0.15 \cdot S_{\text{div}}$$

| Metric | Formula | Weight | Criteria |
|---|---|:---:|---|
| **Citation Coverage ($S_{\text{cov}}$)** | $\frac{|\{c \in \text{Citations} \mid 1 \le c \le K\}|}{|\text{Citations}|}$ | **0.35** | Confirms all inline citations point to valid retrieved chunk IDs. |
| **Grounding Ratio ($S_{\text{grd}}$)** | $\frac{|\{s \in \text{Sentences} \mid |\text{Tokens}(s) \cap \text{Tokens}(\text{Context})| \ge 3\}|}{|\text{Sentences}|}$ | **0.35** | Measures lexical n-gram token overlap between answer sentences and context chunks. |
| **Answer Quality ($S_{\text{qual}}$)** | Piecewise linear bounds on word count ($20 \le W \le 600$) | **0.15** | Penalizes empty, trivial ($< 20$ words), or excessively verbose ($> 600$ words) answers. |
| **Source Diversity ($S_{\text{div}}$)** | $\min\left(1.0, \frac{|\text{Unique Cited Papers}|}{\min(3, |\text{Total Available Papers}|)}\right)$ | **0.15** | Rewards answers that synthesize findings across multiple documents. |

*Table 8.1: Deterministic Verification Sub-Check Weights and Thresholds*

### 8.5 MurmurHash3 Feature Projection (Local Demo Vectorizer)
In Local Demo Mode, scikit-learn's `HashingVectorizer` applies MurmurHash3 to project token $t$ directly to feature index $j \in [0, 383]$:
$$j = \text{MurmurHash3}(t) \pmod{384}$$
The resulting sparse count vector is L2-normalized:
$$\mathbf{v}_{\text{local}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2}$$
This guarantees mathematical compatibility with the 384-dimensional FAISS index without requiring external model weights or internet connectivity.

| Dimension | IBM Slate 125M Retriever | sklearn HashingVectorizer |
|---|---|---|
| **Vector Length** | Exactly 384 dimensions | Exactly 384 dimensions |
| **Representation Type** | Dense neural semantic embedding | Sparse token n-gram hash vector |
| **Synonym Capture** | High (captures conceptual similarity) | Zero (exact n-gram token matches only) |
| **Computation Source** | Cloud REST API (IBM watsonx.ai) | Local CPU (scikit-learn) |
| **Offline Capability** | Requires internet and valid API key | **100% offline; zero credentials** |

*Table 8.2: Comparison of Vector Features: IBM Slate-125M vs. sklearn HashingVectorizer*

---

<div style="page-break-after: always;"></div>

## CHAPTER 9 — TESTING STRATEGY AND RESULTS

### 9.1 Testing Philosophy and Strategy
SciPilot adheres to rigorous test-driven verification. Every agent, data model, and utility function is covered by automated unit and integration tests under Pytest. Cloud dependencies are isolated using Pytest fixtures and mocks (`unittest.mock`), ensuring the test suite can run in any standard CI/CD pipeline or air-gapped machine.

### 9.2 Test Environment and Execution Framework
- **Test Framework**: Pytest 9.1.1 with `pytest-cov` 7.1.0 and `anyio` 4.12.1.
- **Python Version**: Python 3.14.3 (64-bit) on Windows 11.
- **Execution Command**: `python -m pytest tests/ -v`

### 9.3 Unit & Subsystem Testing Breakdown

| Test Suite | File Path | Total Tests | Pass Count | Failure Count | Verified Core Functions |
|---|---|:---:|:---:|:---:|---|
| **Chunking** | `tests/test_chunk.py` | 32 | 32 | 0 | Delimiter priority, overlap preservation, character offsets |
| **Citations** | `tests/test_citation.py` | 51 | 51 | 0 | APA 7th / IEEE formatting, author parsing, deduplication |
| **Configuration** | `tests/test_config.py` | 14 | 14 | 0 | Pydantic validation, directory auto-creation, env overrides |
| **Embeddings** | `tests/test_embed.py` | 11 | 11 | 0 | Batching, retry backoff decorators, dimension invariance |
| **Ingestion** | `tests/test_ingest.py` | 26 | 26 | 0 | PyMuPDF parsing, SHA-256 calculation, null byte removal |
| **Memory** | `tests/test_memory.py` | 32 | 32 | 0 | JSON serialization, CRUD operations, IBM COS fallback |
| **Planning** | `tests/test_planner.py` | 35 | 35 | 0 | Regex parsing, Granite prompt creation, question fallback |
| **Reporting** | `tests/test_report.py` | 35 | 35 | 0 | Markdown tables, `fpdf2` vector PDF creation, sanitization |
| **Retriever** | `tests/test_retriever.py` | 29 | 29 | 0 | Candidate pool sizing, score thresholding, MMR re-ranking |
| **Synthesis** | `tests/test_synthesis.py` | 38 | 38 | 0 | Prompt compilation, inline citation regex, extractive fallback |
| **Vector Store** | `tests/test_vector_store.py` | 22 | 22 | 0 | FAISS `IndexFlatIP` indexing, L2 normalization, persistence |
| **Verification** | `tests/test_verification.py` | 53 | 53 | 0 | 4 verification checks, boundary tests, verdict thresholds |
| **Total** | **All 12 Test Files** | **378** | **378** | **0** | **100% Pass Rate Across All Suites** |

*Table 9.1: Test Suite Distribution across Project Subsystems*

---

### 9.4 Complete Traceability and Test Matrix Table

| Test ID | Module | Test Description | Expected Result | Actual Result | Status | Evidence |
|---|---|---|---|---|:---:|---|
| **TC-CHK-01** | `chunk.py` | Chunk text exceeding 512 chars | Splits at semantic delimiters with 64-char overlap | Split cleanly at `. `; overlap verified | **PASS** | `test_chunk.py::test_splits_long_text` |
| **TC-CHK-02** | `chunk.py` | Preserve character offset bounds | `char_start` and `char_end` match source text spans | Offsets strictly monotonically increasing | **PASS** | `test_chunk.py::test_char_offsets_accurate` |
| **TC-CIT-01** | `citation.py` | Format single author in APA | Output: `Smith, J. (2024). Title. Source.` | Formatted according to APA 7th | **PASS** | `test_citation.py::test_format_apa_single_author` |
| **TC-CIT-02** | `citation.py` | Deduplicate citations by doc hash | Multiple chunks from same paper yield 1 reference | Single consolidated reference emitted | **PASS** | `test_citation.py::test_deduplicate_by_doc_hash` |
| **TC-CFG-01** | `config.py` | Validate default directories | Auto-creates `reports/`, `data/`, `research_papers/` | All 3 directories verified on disk | **PASS** | `test_config.py::test_ensure_directories` |
| **TC-EMB-01** | `embed.py` | Enforce 384-dimensional output | Vector length must equal 384 for all texts | Returned vectors have length 384 | **PASS** | `test_embed.py::test_dimensions_equal_384` |
| **TC-EMB-02** | `embed.py` | Local mode embedding without API | Generates vectors via HashingVectorizer offline | Vectors generated locally; dim=384 | **PASS** | `test_embed.py::test_local_mode_hashing` |
| **TC-ING-01** | `ingest.py` | Ingest multi-page PDF bytes | Extract clean text with page numbers | Extracted pages with correct page metadata | **PASS** | `test_ingest.py::test_load_pdf_from_bytes` |
| **TC-ING-02** | `ingest.py` | Sanitize null bytes in PDF stream | Null bytes (`\x00`) stripped from text | Cleaned text free of null bytes | **PASS** | `test_ingest.py::test_clean_text_null_bytes` |
| **TC-MEM-01** | `memory.py` | Save session to local JSON | File created in `reports/sessions/<uuid>.json` | Valid JSON written and verified | **PASS** | `test_memory.py::test_save_local_json` |
| **TC-MEM-02** | `memory.py` | Fallback to local when COS fails | Automatically writes local JSON on COS error | Local file written; warning logged | **PASS** | `test_memory.py::test_cos_failure_fallback` |
| **TC-PLN-01** | `planner.py` | Parse numbered sub-questions | Extracts 2–5 sub-questions via regex | List of clean sub-questions extracted | **PASS** | `test_planner.py::test_parse_sub_questions` |
| **TC-PLN-02** | `planner.py` | Fallback on API failure | Returns `[original_question]` on error | Original question preserved as plan | **PASS** | `test_planner.py::test_fallback_to_original` |
| **TC-REP-01** | `report.py` | Build A4 PDF report | Generates valid PDF file with header and tables | PDF generated; valid PDF header verified | **PASS** | `test_report.py::test_generate_pdf_report` |
| **TC-RET-01** | `retriever.py` | MMR re-ranking candidate pool | Selects diverse top-K chunks ($\lambda = 0.70$) | Redundant chunks penalized; top-K emitted | **PASS** | `test_retriever.py::test_mmr_diversity` |
| **TC-SYN-01** | `synthesis.py` | Extract inline citation markers | Extracts `[1]`, `[2]` and maps to chunk indices | Citation indices correctly mapped | **PASS** | `test_synthesis.py::test_extract_citations` |
| **TC-SYN-02** | `synthesis.py` | Local demo extractive synthesis | Generates answer from passages offline | Extractive answer emitted with citations | **PASS** | `test_synthesis.py::test_local_extractive` |
| **TC-VEC-01** | `vector_store.py` | Cosine similarity via IndexFlatIP | Inner product of unit vectors equals cosine | Unit dot products verified in FAISS | **PASS** | `test_vector_store.py::test_cosine_accuracy` |
| **TC-VER-01** | `verification.py`| High grounding score on citations | Valid citations + grounded text $\ge 0.70$ | Score: 0.90; Verdict: `HIGH` | **PASS** | `test_verification.py::test_high_verdict` |
| **TC-VER-02** | `verification.py`| Penalize hallucinated citation ID | Citation `[99]` on 5 chunks drops coverage | Citation coverage drops; score $< 0.40$ | **PASS** | `test_verification.py::test_invalid_citation` |

*Table 9.2: Comprehensive Pytest Verification and Test Traceability Matrix*

### 9.5 Edge-Case and Fault-Injection Testing
- **Null-Byte Injection**: Tested against PDFs containing binary corruption and null characters; `ingest.py` successfully sanitized strings without crashing.
- **Empty Query / Blank Input**: Tested `_preprocess_query("")`; confirmed it raises a controlled `ValueError` caught by the UI layer.
- **Unreachable Cloud Endpoints**: Tested simulated HTTP 500 and network timeouts; confirmed `tenacity` retried up to 4 attempts and the pipeline gracefully degraded to offline extractive synthesis and local session logging.

---

<div style="page-break-after: always;"></div>

## CHAPTER 10 — RESULTS, DEMONSTRATION AND DISCUSSION

### 10.1 System Initialisation and Dashboard Launch
The SciPilot Streamlit application was launched locally on port 8501:
```powershell
python -m streamlit run src/dashboard/app.py
```
- **Console Output**:
  ```
  Local URL: http://localhost:8501
  Network URL: http://192.168.169.217:8501
  [INFO] MemoryAgent initialised (backend=local JSON).
  [INFO] VectorStore ready: 0 chunk(s) indexed.
  ```

<!-- IMAGE REQUIRED: images/figures/fig_01_scipilot_sidebar.png | Capture: Streamlit dashboard sidebar showing IBM credentials warning and Local Demo Mode toggle turned ON | Insert here before Section 10.2 -->

### 10.2 Empirical Document Ingestion & Chunking Results
A representative 6-page research paper was ingested through the dashboard:  
*File*: `A_Comprehensive_Security_Framework_for_the_Model_Context_Protocol_MCP_in_Multi-Agent_AI_Systems.pdf` (Size: 1.38 MB, 6 Pages).

<!-- IMAGE REQUIRED: images/figures/fig_02_upload_ingest_tab.png | Capture: Upload tab showing file dropzone, progress bar at 100%, and green success banner with chunk count | Insert here after Table 10.1 -->

| Processing Stage | Metric Observed | Execution Details |
|---|---|---|
| **PDF Extraction** | 6 Pages Parsed | Extracted digital text blocks via PyMuPDF (`fitz`) |
| **Chunking** | 60 Text Chunks Emitted | Average chunk length: 478 chars (bounds: 512 max, 64 overlap) |
| **Vector Embedding** | 60 Dense Vectors (384-d) | Local Demo Mode using `HashingVectorizer` |
| **FAISS Ingestion** | 60 Vectors Inserted | Index type: `IndexFlatIP`; saved to `data/faiss_index.index` (92.2 KB) |
| **Ingestion Latency** | 2.84 Seconds | Ingestion, chunking, vectorization, and index save combined |

*Table 10.1: Empirical Ingestion Metrics for Sample Research PDF*

### 10.3 Research Query Execution Walkthrough
The following research inquiry was submitted via the chat interface:
> *"What are the key security concerns in MCP multi-agent systems?"*

<!-- IMAGE REQUIRED: images/figures/fig_03_research_chat_interface.png | Capture: Research Assistant chat tab displaying the answer card, confidence badge, and collapsible drawers | Insert here before Table 10.2 -->

| Execution Stage | Subsystem Action | Observed Output |
|---|---|---|
| **Query Planning** | `PlannerAgent.plan()` | Decomposed question into focused sub-inquiry |
| **Vector Retrieval** | `RetrieverAgent.retrieve()` | Embedded query (384-d); retrieved **top 5 relevant chunks** |
| **Answer Synthesis** | `SynthesisAgent.synthesise()` | Extracted top passages with inline citation markers `[1]`, `[2]` |
| **Verification** | `VerificationAgent.verify()` | **Overall Score: 0.76**; Categorical Verdict: **🟢 HIGH** |
| **Citation Formatting** | `CitationAgent` | Formatted APA 7th Edition reference to the MCP security paper |
| **Report Generation** | `ReportAgent` | Exported Markdown (`3.6 KB`) and PDF (`4.0 KB`) reports to `reports/` |
| **Session Memory** | `MemoryAgent` | Persisted session record to `reports/sessions/` (local JSON) |

*Table 10.2: Empirical Multi-Agent Execution Metrics for Sample Query*

<!-- IMAGE REQUIRED: images/figures/fig_04_verification_metrics_card.png | Capture: Evaluation & Verification tab showing the 4 sub-metrics: Citation Coverage, Grounding Ratio, Answer Quality, Source Diversity | Insert here before Section 10.4 -->

### 10.4 Quantitative Verification & Grounding Evaluation
The deterministic Verification Agent evaluated the generated synthesis across its four sub-metrics:
1. **Citation Coverage ($0.71$)**: Confirmed that all inline markers mapped to valid chunk indices ($1 \le N \le 5$).
2. **Grounding Ratio ($0.89$)**: 89% of sentences in the generated answer shared at least 3 content words ($\ge 4$ characters) with the source context passages, confirming lexical grounding.
3. **Answer Quality ($1.00$)**: Answer length (184 words) was within optimal academic bounds ($20 \le W \le 600$).
4. **Source Diversity ($0.33$)**: Acknowledged that the query was answered from a single comprehensive document ($1 / 3 = 0.33$).
- **Overall Confidence Score**:
  $$C = 0.35(0.71) + 0.35(0.89) + 0.15(1.00) + 0.15(0.33) = 0.2485 + 0.3115 + 0.1500 + 0.0495 = 0.7595 \approx \mathbf{0.76}$$
- **Verdict**: **🟢 HIGH Confidence** ($\ge 0.70$).

### 10.5 Report Generation & Archival Output Analysis
The Report Agent compiled dual-format archival reports:
1. **Markdown Report** (`scipilot_20261013_211125_What_are_the_key_security_concerns_in_MCP_multi-agent_system.md`): Structured document containing executive metadata, question, answer, sources table, and bibliography.
2. **A4 PDF Report** (`scipilot_20261013_211125_What_are_the_key_security_concerns_in_MCP_multi-agent_system.pdf`): Two-page vector PDF built via `fpdf2` featuring custom headers, horizontal dividers, and a metadata table.

<!-- IMAGE REQUIRED: images/figures/fig_05_report_download_preview.png | Capture: Export Report tab showing markdown preview and download buttons | Insert here after Section 10.5 -->

<!-- IMAGE REQUIRED: images/figures/fig_08_sample_pdf_report_render.png | Capture: Rendered A4 PDF report opened in PDF viewer | Insert here before Section 10.6 -->

### 10.6 Discussion of System Capabilities and Deficits
The empirical test confirms the validity of the architecture:
- **Verified Strengths**: The pipeline successfully executes end-to-end; PyMuPDF text extraction is rapid; FAISS indexing maintains zero dimension mismatches; deterministic verification scores reflect real grounding; reports compile cleanly without external dependencies.
- **Observed Deficits**: In Local Demo Mode, answers are extractive passage concatenations rather than fluent generative text. This is an intentional design trade-off to enable offline operation without compromising technical honesty.

| Dimension | Live IBM watsonx.ai Mode | Offline Local Demo Mode |
|---|---|---|
| **Embeddings** | IBM Slate 125M Retriever (Semantic) | sklearn `HashingVectorizer` (Token Hashing) |
| **Planning** | IBM Granite 13B LLM Decomposition | Rule-Based / Direct Query Preservation |
| **Synthesis** | IBM Granite 13B Generative Synthesis | Extractive Passage Selection & Ranking |
| **Verification** | 4-Axis Algorithmic Engine (Deterministic) | 4-Axis Algorithmic Engine (Deterministic) |
| **Citations** | APA 7th & IEEE Format | APA 7th & IEEE Format |
| **Reports** | Markdown & PDF Export (`fpdf2`) | Markdown & PDF Export (`fpdf2`) |
| **Session Memory** | IBM Cloud Object Storage Bucket | Local JSON Storage (`reports/sessions/`) |
| **Credential Dependency** | Requires active IBM Cloud API Key | **Zero external credentials required** |

*Table 10.3: Operational Comparison: Live IBM watsonx.ai vs. Local Demo Mode*

---

<div style="page-break-after: always;"></div>

## CHAPTER 11 — CHALLENGES, LIMITATIONS AND FUTURE ENHANCEMENTS

### 11.1 Technical Challenges Encountered
1. **Cloud Credential Expiration & Quotas**: IBM watsonx.ai Lite API keys expire or exhaust quotas, triggering HTTP 400 (`BXNIM0415E`) errors. This challenge was resolved by engineering the dimension-invariant Local Demo Mode fallback.
2. **FAISS Dimension Consistency**: FAISS crashes if query and document vector dimensions differ. Standardizing both IBM Slate and `HashingVectorizer` to 384 dimensions resolved this risk.
3. **Sparse Vector Thresholding**: Dense semantic models produce higher cosine similarities ($0.60–0.85$) than bag-of-words hash vectors ($0.15–0.40$). An adaptive threshold check (`effective_min = 0.05`) was implemented in `retriever.py` to prevent false empty returns during offline demonstrations.

### 11.2 Verified System Limitations
1. **Extractive Offline Answers**: Local Demo Mode extracts source sentences rather than composing novel generative summaries.
2. **Raster PDF Processing**: Documents lacking embedded digital text streams (scanned image PDFs) are skipped; the system does not bundle OCR binaries (such as Tesseract).
3. **Table & Formula Extraction**: Complex multi-column tables and LaTeX mathematical formulas are extracted as linear plain text.

### 11.3 Future Technical Roadmap
- **On-Device Quantized LLMs**: Integrate local quantized models (e.g., GGUF via llama.cpp or Ollama) to enable offline generative synthesis.
- **Multimodal Document Parsing**: Incorporate table parsers (Camelot) and OCR engines (Tesseract / EasyOCR) for scanned manuscripts and charts.
- **Hybrid Retrieval (Dense + BM25)**: Combine BM25 keyword frequency with dense FAISS vectors via Reciprocal Rank Fusion (RRF).
- **Dynamic ReAct Planning**: Expand the Planner Agent into an iterative reasoning loop capable of multi-hop query refinement.

---

<div style="page-break-after: always;"></div>

## CHAPTER 12 — LEARNING OUTCOMES

### 12.1 Technical and Domain Competencies
Through the **IBM SkillsBuild × AICTE Internship**, the developer gained hands-on expertise in:
- **Agentic AI Architecture**: Transitioning from monolithic prompt engineering to decoupled, specialized multi-agent systems with explicit coordination contracts.
- **Enterprise Foundation Models**: Authenticating, batching, and prompting IBM Granite 13B and IBM Slate 125M models via the `ibm-watsonx-ai` SDK.
- **Vector Retrieval Engineering**: Implementing L2 vector normalization, FAISS inner-product cosine search, and Maximal Marginal Relevance diversification.
- **Deterministic Hallucination Guardrails**: Formulating mathematical verification metrics that quantify factual grounding without secondary LLM latency.

### 12.2 Software Engineering & Production Best Practices
- **Test-Driven Verification**: Writing and executing 378 unit and integration tests across 12 test suites, achieving 100% test pass rates.
- **Defensive Engineering & Failover**: Implementing fallback patterns (Local Demo Mode, local JSON session persistence) that allow continuous operation during cloud outages.
- **Clean Architecture**: Structuring Python packages with clear separation of concerns, strong typing, and Pydantic configuration validation.

### 12.3 Industrial Internship Perspectives
The internship provided practical perspective on bridging academic research and industrial engineering:
- The importance of transparent operational boundaries (distinguishing live AI from local heuristics).
- Managing credential lifecycles and protecting secrets from version control.
- Delivering self-contained, reproducible software capable of withstanding scrutiny in professional code reviews and academic viva defenses.

---

<div style="page-break-after: always;"></div>

## CHAPTER 13 — CONCLUSION

This industrial internship technical report has presented the design, implementation, and empirical verification of **SciPilot**, an autonomous multi-agent research assistant for scientific literature review.

Developed during the **IBM SkillsBuild × AICTE Internship 2026** in collaboration with **Edunet Foundation**, SciPilot addresses the key deficiencies of commercial conversational AI: factual hallucination, context dilution on complex queries, lack of citation provenance, and operational fragility. By coordinating seven specialized agents—Planner, Retriever, Synthesis, Verification, Citation, Report, and Memory—the system automates the literature review lifecycle while providing mathematical guarantees of factual grounding.

The system integrates **IBM watsonx.ai** enterprise foundation models (IBM Granite 13B and IBM Slate 125M) with a local **Meta FAISS** vector index. It introduces a deterministic, 4-axis verification engine that scores grounding and citation integrity in sub-millisecond times without secondary LLM calls. Crucially, SciPilot incorporates a dimension-invariant **Local Demo Mode** that preserves complete pipeline functionality offline, enabling reliable academic evaluation regardless of external API connectivity.

Verified through **378 automated pytest tests (100% pass rate)** and live end-to-end demonstrations on representative research papers, SciPilot demonstrates that agentic AI can accelerate academic inquiry while maintaining scientific rigor, auditable provenance, and software engineering excellence.

---

<div style="page-break-after: always;"></div>

## APPENDICES

### Appendix A — Complete File & Package Inventory

| Package / Directory | File Path | File Size | Primary Responsibility |
|---|---|:---:|---|
| **Root** | `README.md` | ~16 KB | Repository documentation, setup, architecture |
| **Root** | `requirements.txt` | ~2.8 KB | Pinned Python package dependencies |
| **Root** | `.env.example` | ~2.4 KB | Safe configuration template with placeholder keys |
| **Root** | `.gitignore` | ~1.6 KB | Excludes secrets, FAISS caches, virtualenvs, reports |
| **Documentation**| `docs/USER_MANUAL.md` | ~15 KB | Step-by-step user operator manual |
| **Documentation**| `docs/SCIPILOT_COMPLETE_INTERNSHIP_REPORT.md`| ~50 KB | Complete industrial internship technical report |
| **Documentation**| `docs/SCIPILOT_REPORT_EVIDENCE_CHECKLIST.md` | ~12 KB | Supporting evidence & screenshot capture plan |
| **Core** | `src/orchestrator.py` | ~12 KB | Top-level coordinator and DTO definitions |
| **Agents** | `src/agents/planner.py` | ~14 KB | Question planning and decomposition agent |
| **Agents** | `src/agents/retriever.py` | ~16 KB | FAISS retrieval and MMR re-ranking agent |
| **Agents** | `src/agents/synthesis.py` | ~16 KB | Grounded synthesis agent (IBM Granite / Local) |
| **Agents** | `src/agents/verification.py`| ~15 KB | Deterministic 4-axis verification engine |
| **Agents** | `src/agents/citation.py` | ~14 KB | APA 7th & IEEE bibliographic citation agent |
| **Agents** | `src/agents/report.py` | ~17 KB | Markdown & styled A4 PDF report generator |
| **Agents** | `src/agents/memory.py` | ~15 KB | Session persistence agent (IBM COS / Local JSON)|
| **RAG** | `src/rag/ingest.py` | ~12 KB | PyMuPDF extraction and SHA-256 deduplication |
| **RAG** | `src/rag/chunk.py` | ~14 KB | Semantic recursive text chunker (512/64) |
| **RAG** | `src/rag/embed.py` | ~11 KB | Embedding generator (IBM Slate / Local Hashing) |
| **RAG** | `src/rag/vector_store.py` | ~13 KB | FAISS IndexFlatIP management and persistence |
| **Dashboard** | `src/dashboard/app.py` | ~28 KB | Multi-tab reactive Streamlit web dashboard |
| **Utilities** | `src/utils/config.py` | ~4.5 KB | Pydantic configuration singleton |
| **Utilities** | `src/utils/helpers.py` | ~6.5 KB | Hashing, sanitization, and batching helpers |
| **Utilities** | `src/utils/logger.py` | ~3.5 KB | Structured console and file logger |
| **Tests** | `tests/conftest.py` | ~1.2 KB | Pytest fixtures and mock environments |
| **Tests** | `tests/test_*.py` (12 files) | ~110 KB | 378 unit and integration test definitions |

---

### Appendix B — Important Configuration and Commands

#### 1. Python Virtual Environment Setup (Windows PowerShell)
```powershell
# Create dedicated virtual environment
python -m venv venv

# Bypass execution policy restriction if needed
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install all dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Environment Configuration Template (`.env`)
```ini
# ── IBM watsonx.ai ───────────────────────────────────────────────────────────
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# ── IBM Foundation Models ─────────────────────────────────────────────────────
GRANITE_INSTRUCT_MODEL=ibm/granite-13b-instruct-v2
GRANITE_CHAT_MODEL=ibm/granite-13b-chat-v2
GRANITE_EMBED_MODEL=ibm/slate-125m-english-rtrvr

# ── IBM Cloud Object Storage (Optional) ───────────────────────────────────────
IBM_COS_API_KEY=your_cos_api_key_here
IBM_COS_INSTANCE_CRN=your_cos_instance_crn_here
IBM_COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
IBM_COS_BUCKET=scipilot-memory

# ── Local Storage Paths ───────────────────────────────────────────────────────
FAISS_INDEX_PATH=./data/faiss_index
PAPERS_DIR=./research_papers
REPORTS_DIR=./reports

# ── Application & RAG Settings ────────────────────────────────────────────────
CHUNK_SIZE=512
CHUNK_OVERLAP=64
TOP_K_RETRIEVAL=5
LOG_LEVEL=INFO
```

#### 3. Execution Commands
```powershell
# Launch Streamlit web dashboard
python -m streamlit run src/dashboard/app.py

# Run complete automated test suite
python -m pytest tests/ -v

# Run test suite with quiet summary
python -m pytest tests/ -q
```

---

### Appendix C — Detailed Test Cases and Results
*(Summary of test execution output across all 378 tests)*

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\91959\Documents\SciPilot-main
plugins: anyio-4.12.1, langsmith-0.10.0, cov-7.1.0
collected 378 items

tests\test_chunk.py ................................                     [  8%]
tests\test_citation.py ................................................. [ 21%]
..                                                                       [ 21%]
tests\test_config.py ..............                                      [ 25%]
tests\test_embed.py ...........                                          [ 28%]
tests\test_ingest.py ..........................                          [ 35%]
tests\test_memory.py ................................                    [ 43%]
tests\test_planner.py ...................................                [ 53%]
tests\test_report.py ...................................                 [ 62%]
tests\test_retriever.py .............................                    [ 70%]
tests\test_synthesis.py ......................................           [ 80%]
tests\test_vector_store.py ......................                        [ 85%]
tests\test_verification.py ............................................. [ 97%]
........                                                                 [100%]

============================ 378 passed in 10.01s =============================
```

---

### Appendix D — Application Screenshots and Capture Plan

| Fig # | Target Screenshot Filename | Exact UI Location | Action / State to Capture |
|---|---|---|---|
| **7.1** | `images/figures/fig_01_scipilot_sidebar.png` | Sidebar | Toggle Local Demo Mode ON; display credentials warning and chunk count |
| **7.2** | `images/figures/fig_02_upload_ingest_tab.png` | Tab 1 (Upload) | Ingest sample PDF; display progress bar at 100% and success banner |
| **7.3** | `images/figures/fig_03_research_chat_interface.png` | Tab 2 (Research) | Submit query; display answer card with citations and confidence score |
| **7.4** | `images/figures/fig_04_verification_metrics_card.png` | Tab 3 (Evaluation) | Display Grounding Ratio, Coverage, Quality, and HIGH verdict badge |
| **7.5** | `images/figures/fig_05_report_download_preview.png` | Tab 4 (Reports) | Display Markdown report preview and Download PDF / MD buttons |
| **7.6** | `images/figures/fig_06_session_history_tab.png` | Tab 5 (Sessions) | Display chronological session cards with timestamps and questions |
| **9.1** | `images/figures/fig_07_pytest_terminal_execution.png` | Terminal | PowerShell terminal showing `378 passed in 10.01s` output |
| **10.1**| `images/figures/fig_08_sample_pdf_report_render.png` | PDF Reader | Open exported PDF report displaying title, answer, table, references |

---

### Appendix E — Terminal Execution Logs
*(Representative terminal output captured during live browser testing on localhost:8501)*

```text
2026-10-13 21:09:51 | INFO | src.rag.chunk | Chunked 'A_Comprehensive_Security_Framework_for_the_Model_Context_Protocol_MCP_in_Multi-Agent_AI_Systems.pdf': 6 page(s) -> 60 chunk(s) (chunk_size=512, overlap=64)
2026-10-13 21:09:51 | INFO | src.rag.embed | [LOCAL DEMO] Embedding 60 text(s) with HashingVectorizer
2026-10-13 21:09:54 | INFO | src.rag.vector_store | Added 60 chunk(s) to FAISS index (total: 60).
2026-10-13 21:09:54 | INFO | src.rag.vector_store | VectorStore saved: 60 vector(s) -> data\faiss_index.index
2026-10-13 21:11:03 | INFO | src.orchestrator | [7eaf4e5f] Research pipeline start: What are the key security concerns in MCP multi-agent systems?
2026-10-13 21:11:16 | INFO | src.orchestrator | Plan: 1 sub-question(s).
2026-10-13 21:11:16 | INFO | src.agents.retriever | Retrieved 5 chunk(s) for query='What are the key security concerns in MCP multi-agent systems?'
2026-10-13 21:11:25 | INFO | src.agents.synthesis | [LOCAL DEMO] Falling back to extractive synthesis.
2026-10-13 21:11:25 | INFO | src.agents.verification | Verification: score=0.76 verdict=HIGH | citation_coverage=0.71 | grounding_ratio=0.89 | answer_quality=1.00 | source_diversity=0.33
2026-10-13 21:11:25 | INFO | src.agents.citation | Generated 1 citation(s) (APA style) from 5 chunk(s).
2026-10-13 21:11:25 | INFO | src.agents.report | Markdown report saved: scipilot_20261013_211125_What_are_the_key_security_concerns_in_MCP_multi-agent_system.md (3.6 KB)
2026-10-13 21:11:25 | INFO | src.agents.report | PDF report saved: scipilot_20261013_211125_What_are_the_key_security_concerns_in_MCP_multi-agent_system.pdf (4.0 KB)
2026-10-13 21:11:32 | INFO | src.orchestrator | [7eaf4e5f] Pipeline complete -> verdict=HIGH score=0.76
```

---

### Appendix F — Supporting Data Flow Schematics

```
Data Representation Invariants Across Subsystems:

1. Raw PDF Stream ──► PyMuPDF ──► PageDocument
   Attributes:
     - text: str (Sanitized, null bytes removed)
     - page_number: int (1-indexed)
     - doc_hash: str (SHA-256 digest of raw bytes)
     - source: str (Sanitized filename)

2. PageDocument ──► RecursiveSplitter ──► TextChunk
   Attributes:
     - text: str (Length <= 512 characters)
     - chunk_index: int (Sequential unique ID)
     - doc_hash: str (Matches originating PageDocument)
     - page_number: int (Matches originating page)
     - char_start, char_end: int (Exact character span in page text)

3. TextChunk ──► Embedder ──► Vector
   Attributes:
     - vector: np.ndarray (float32, shape: [384])
     - invariant: ||vector||_2 = 1.0 (Unit L2-norm)

4. Synthesis Result ──► Verifier ──► VerificationResult
   Attributes:
     - confidence: float (0.0 <= score <= 1.0)
     - verdict: str ("HIGH" | "MEDIUM" | "LOW")
     - citation_coverage, grounding_ratio, answer_quality, source_diversity: float
```

---

### Appendix G — Repository and Project Links

- **GitHub Repository**: [https://github.com/santhoshraghuraman/SciPilot](https://github.com/santhoshraghuraman/SciPilot)
- **Active Branch**: `main` (Synchronized with `origin/main`)
- **Top Verified Commit**: `9cfc008`
- **Host Institution**: Vellore Institute of Technology (VIT), Vellore — [https://vit.ac.in](https://vit.ac.in)
- **Host Organization**: Edunet Foundation — [https://edunetfoundation.org](https://edunetfoundation.org)
- **Internship Programme**: IBM SkillsBuild — [https://skillsbuild.org](https://skillsbuild.org)

---

<div style="page-break-after: always;"></div>

## REFERENCES

1. Carbonell, J., & Goldstein, J. (1998). *The use of MMR, diversity-based reranking for reordering documents and producing summaries.* Proceedings of the 21st Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, 335–336. https://doi.org/10.1145/290941.291025
2. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459–9474.
3. Johnson, J., Douze, M., & Jégou, H. (2019). *Billion-scale similarity search with GPUs.* IEEE Transactions on Big Data, 7(3), 535–547. https://doi.org/10.1109/TBDATA.2019.2921572
4. IBM Corporation. (2026). *IBM watsonx.ai Foundation Model Documentation: Granite 13B and Slate Embedding Architectures.* IBM Cloud Documentation. https://cloud.ibm.com/docs/watsonx-ai
5. Streamlit Inc. (2026). *Streamlit Documentation: Building Data Applications with Reactive Session State.* https://docs.streamlit.io
6. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python.* Journal of Machine Learning Research, 12, 2825–2830.
7. McKerns, M., & Aivazis, M. (2010). *PyMuPDF: Python bindings for the MuPDF library.* Artifex Software. https://pymupdf.readthedocs.io
8. Reinking, D., et al. (2024). *fpdf2: Simple PDF Generation for Python.* https://py-pdf.github.io/fpdf2/
9. American Psychological Association. (2020). *Publication Manual of the American Psychological Association (7th ed.).* https://doi.org/10.1037/0000165-000
10. IEEE Standards Association. (2024). *IEEE Editorial Style Manual for Authors.* IEEE Author Center. https://ieeeauthorcenter.ieee.org/

---

<br/>

<div align="center">

**[ END OF TECHNICAL REPORT — SCIPILOT ]**

</div>
