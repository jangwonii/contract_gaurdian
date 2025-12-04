# AGENTS.md

> Meta
- Human language: Korean (UI/설명은 한국어 위주, 코드/주석/커밋 메시지는 영어 또는 한–영 혼합 가능)
- Course: Deep Learning / Cloud – Term Project (LLM-based Agent App)
- Goal: “일반 챗봇”이 아니라 **특정 기능을 수행하는 LLM 기반 Agent 앱**을 구현하는 것.
- This file describes the project goals, constraints, and recommended agent responsibilities so that code assistants (e.g., GitHub Copilot / OpenAI Codex / VSCode assistants) can help implement the project.

---

## 1. Assignment Constraints & Grading Criteria

**Hard constraints (must)**

1. This project **must be an LLM-based Agent app**, NOT a simple QA chatbot.
2. We must implement a **specific, non-trivial functionality** that cannot be solved by a single prompt.
   - Example concept (not our final spec, just for context):  
     - “Input 3 documents → output integrated summary.”  
     - “Upload study material file → generate 10 fill-in-the-blank questions and auto-grade answers.”
3. The app **must have a UI** (web or desktop).  
4. We **must not just clone an existing Agent app from the internet**. Existing apps can be referenced for ideas, but the final app must be our own design and implementation.
5. The project should be **reproducible from this repository** (no hidden manual steps if possible).

**Grading Focus**

- Originality of the topic.
- Implementation difficulty (non-triviality).
- App completeness (end-to-end pipeline working).
- Report completeness (architecture, design, experiments, limitations).
- Bonus: **Multi-modal** (e.g., image + text) earns extra points.

---

## 2. Product Idea: Contract Risk Analysis Agent App

**App name (working):** `Contract Guardian` (or similar)

**Target users**

- 일반 개인 사용자 (노동자, 세입자, 프리랜서 등)
- 근로계약서, 임대차 계약서, 용역 계약서 등을 전문지식 없이 빠르게 이해하고 싶은 사람

**Core Problem**

- People struggle to understand key clauses and hidden “danger” terms in contracts.
- They may **miss unfair or risky clauses** (해지, 책임, 손해배상, 과도한 의무 등).

**Proposed Solution**

User uploads a **contract (PDF / image)** →  
System automatically:

1. Runs **OCR** to extract raw text.  
2. Splits text into clauses (조항 단위 분리).  
3. Uses **LLM-based Agent(s)** to:
   - Summarize each clause.
   - Classify each clause into categories (e.g., payment, termination, responsibility, penalty).
   - Detect **risky / unfair clauses** and assign **risk scores (0–100)** with explanation.
4. Provides a **visual dashboard** summarizing:
   - Overall risk level.
   - List of high-risk clauses with reasons.
   - Category-based view of clauses.
5. (Optionally) Exports an **analysis report** as PDF.

**Legal scope**

- This app **does not provide legal advice**.  
- It is a **risk signal and explanation tool**, not a lawyer.

---

## 3. High-Level Architecture

We assume a simple 3-layer architecture:

1. **Frontend (UI)**
   - Web-based UI (React or any SPA framework is OK).
   - Main screens:
     - Document upload screen (PDF/image).
     - Analysis progress / status.
     - Result dashboard (risk overview).
     - Clause-level detail view (summary, category, risk score, explanation).

2. **Backend (Application + Domain)**
   - Typical stack: Python (FastAPI/Flask) or Java (Spring Boot) — either is OK as long as consistent.
   - Exposes REST APIs:
     - `POST /api/documents` – upload contract file.
     - `POST /api/documents/{id}/analyze` – trigger analysis pipeline.
     - `GET  /api/documents/{id}/result` – get structured analysis result.
   - Implements:
     - `OCRService` – wraps OCR engine (e.g., Tesseract).
     - `ClauseExtractor` – splits text into clauses.
     - `LLMAgent` – orchestrates calls to LLM provider via unified interface.
     - `RiskAnalyzer` – computes risk score per clause using `RiskPolicy`.
     - `AnalysisFacade` – single entry point for the full pipeline.

3. **Infrastructure / External Services**
   - LLM provider (OpenAI / local model etc.) behind an adapter interface.
   - OCR engine (e.g., Tesseract) behind service wrapper.
   - Storage (local filesystem or DB) for:
     - Uploaded documents.
     - Extracted clauses.
     - Analysis results.

---

## 4. Repository & File Layout (Desired)

> NOTE for code assistants: If these folders/files do not exist yet, propose and create them.

- `/frontend/`
  - React (Vite/CRA/Next) app for UI.
  - Key directories:
    - `/src/pages/` – pages: UploadPage, ResultPage.
    - `/src/components/` – reusable UI components.
    - `/src/api/` – API client wrappers.
- `/backend/`
  - Backend server (FastAPI or Spring Boot).
  - Sub-packages/modules:
    - `/backend/domain/` – entities: `Document`, `Clause`, `ClauseRisk`, `AnalysisResult`, `User`.
    - `/backend/application/` – use cases & services:
      - `AnalysisFacade`
      - `OCRService`
      - `ClauseExtractor`
      - `LLMAgent`
      - `RiskAnalyzer`
    - `/backend/infrastructure/` – external integrations:
      - `TesseractOCRAdapter`
      - `OpenAILLMProvider`, `DummyLLMProvider`
      - Repository/DAO for persistence.
- `/docs/`
  - `AGENTS.md` (this file)
  - `REPORT.md` or `report_draft.md` – for final report draft.
  - `API_SPEC.md` – API documentation (optional).
- `/config/`
  - Configuration for OCR, LLM endpoints, API keys (never commit real keys).

---

## 5. Agents & Responsibilities

Below “Agent” means a logical role for an AI assistant (like Copilot/Codex) to follow when editing the repo or answering questions.

### 5.1 Project Planner Agent

**Goal**

- Turn the above assignment + idea into concrete tasks, milestones, and issues.

**Responsibilities**

- Define **MVP scope**.
- Break project into steps:
  - Initial skeleton of backend and frontend.
  - OCR pipeline.
  - Clause extraction logic.
  - LLM integration.
  - Risk analysis.
  - UI integration.
  - Testing & report.
- Keep a simple TODO list in `docs/ROADMAP.md` or GitHub issues.

---

### 5.2 Backend Architect Agent

**Goal**

- Design and refine the backend architecture based on domain concepts.

**Responsibilities**

- Define domain models:
  - `Document`, `Clause`, `ClauseRisk`, `AnalysisResult`, `User`.
- Design REST API endpoints and request/response schemas.
- Ensure separation of layers:
  - Controllers (HTTP layer) vs application services vs domain entities vs infrastructure adapters.
- Avoid hardcoding secrets; use environment variables/config files.

---

### 5.3 OCR & Preprocessing Agent

**Goal**

- Implement document upload + OCR + basic text cleaning.

**Responsibilities**

- Create file upload endpoint:
  - Accept PDF/image.
  - Save file with generated document ID.
- Implement OCR pipeline:
  - For images: run OCR directly.
  - For PDFs: either direct text extraction or per-page OCR.
- Normalize text:
  - Handle line breaks, spacing, encoding.
- Provide `extractText(document)` or similar method for upper layers.

---

### 5.4 Clause Extraction Agent

**Goal**

- Split extracted text into logical contract clauses.

**Responsibilities**

- Implement heuristic or LLM-assisted clause splitting:
  - Use headings, numbering (e.g., “제1조”, “제2조”), bullet points, or newline patterns.
- Represent each clause with:
  - `id`, `rawText`, maybe `position` (page/clause index).
- Provide `splitIntoClauses(documentText)` function returning list of clauses.

---

### 5.5 LLM Orchestrator Agent

**Goal**

- Orchestrate all calls to the LLM provider in a structured, reusable way.

**Responsibilities**

- Define `ILLMProvider` interface with methods like:
  - `summarizeClause(clauseText) -> summary`
  - `classifyClause(clauseText) -> category label(s)`
  - `analyzeRisk(clauseText) -> risk hints / explanation`
- Implement at least:
  - `DummyLLMProvider` for development (return mock data).
  - `OpenAILLMProvider` or other real provider (using API key from env).
- Implement `LLMAgent` that uses `ILLMProvider` to:
  - Loop over clauses.
  - Attach summary, category, risk explanation to each clause.
- Ensure prompts clearly state that:
  - Output must be structured (e.g., JSON-like).
  - The model should not give legal advice, only risk indications.

---

### 5.6 Risk Scoring Agent

**Goal**

- Assign numeric risk scores to clauses using policy-based strategy.

**Responsibilities**

- Define `RiskPolicy` interface (e.g., `score(clause) -> ClauseRisk`).
- Implement example policies:
  - `EmploymentRiskPolicy` for employment contracts.
  - `LeaseRiskPolicy` for rental contracts.
- Use `RiskAnalyzer` to:
  - Take clause data (summary, category, risk hints).
  - Compute risk score (0–100).
  - Return an `AnalysisResult` with per-clause and overall risk.
- Design for extensibility:
  - New contract types can plug in new policies without editing existing analyzer code (Strategy pattern).

---

### 5.7 Facade & Pipeline Agent

**Goal**

- Provide a clean, single entrypoint for the whole analysis pipeline.

**Responsibilities**

- Implement `AnalysisFacade.analyze(documentId)` which:
  1. Loads document.
  2. Runs OCR.
  3. Runs clause extraction.
  4. Calls LLM agent for summaries/categories/risk hints.
  5. Calls RiskAnalyzer to compute scores.
  6. Stores and returns `AnalysisResult`.
- Ensure controllers/UI only call the Facade, not individual low-level services.

---

### 5.8 Frontend/UI Agent

**Goal**

- Build a clean, minimal UI for end users.

**Responsibilities**

- Implement:
  - File upload page:
    - Drag&drop or file input for PDF/image.
    - Shows upload status.
  - Analysis result page:
    - Overview: overall risk gauge/indicator.
    - Table/list of clauses:
      - Clause index / short text
      - Category
      - Risk score (colored)
      - “Details” button
    - Detail view:
      - Original text
      - Summary
      - Risk explanation
- Handle loading states, errors, and empty states gracefully.
- Optional: support **basic mobile responsiveness**.

---

### 5.9 Evaluation & Report Agent

**Goal**

- Help write the final report and describe experiments/limitations.

**Responsibilities**

- Maintain `docs/REPORT.md` with:
  - Problem definition and motivation.
  - System architecture & diagrams.
  - Agent flow and design patterns (Facade, Strategy, Adapter).
  - Implementation details (libraries, frameworks).
  - Example scenarios (sample contracts).
  - Limitations & future work.
- Summarize how the implementation satisfies:
  - Term project requirements.
  - Evaluation criteria.

---

## 6. Coding & Collaboration Rules for AI Assistants

1. **Do not expose real API keys or secrets**.  
   - Use environment variables and `.env.example`.
2. **Prefer clarity over cleverness**.  
   - Write readable, well-structured code.
   - Add short comments for non-obvious logic.
3. **Keep layers separated**:
   - No direct OCR/LLM calls in controller/route handlers; go through services/Facades.
4. **Error handling**:
   - For external service failures (LLM/OCR), return meaningful error messages and/or partial results.
5. **Tests** (if time allows):
   - Unit tests for clause splitting and risk scoring.
   - Simple integration test for the pipeline with dummy provider.
6. **Language**:
   - UI text and user-facing messages: Korean.
   - Internal code comments and identifiers: English strongly preferred.

---

## 7. Definition of Done (MVP)

The project can be considered **MVP complete** when:

1. A user can upload a **real PDF or image contract** via the UI.
2. The backend:
   - Runs OCR (or direct text extraction for PDFs).
   - Splits text into clauses.
   - Calls LLM provider via `LLMAgent` to:
     - Summarize and classify each clause.
     - Produce risk hints/explanations.
   - Uses `RiskAnalyzer` to compute numeric risk scores.
3. The frontend shows:
   - Overall document risk level.
   - List of clauses with summary, category, risk score.
   - Detail view with original text + risk explanation.
4. At least one **sample contract** runs end-to-end without manual intervention.
5. A draft of the final **REPORT.md** exists describing what was built.

If possible, also support:

- Exporting a simple analysis report (Markdown/PDF).
- Handling at least two contract types (e.g., 근로 + 임대).

---
