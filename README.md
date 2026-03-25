
<p align="center">
  <img src="docs/screens/logo.png" alt="DristiScan Logo" width="220" />
</p>

<h1 align="center">DristiScan — AI-Powered Code Security Scanner</h1>

<p align="center">
  <b>SAST • RAG Intelligence • AI Fix Suggestions • pgvector • Ollama</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-Vector%20DB-purple" />
  <img src="https://img.shields.io/badge/AI-RAG%20Pipeline-orange" />
  <img src="https://img.shields.io/badge/Security-DevSecOps-red" />
</p>

<p align="center">
A production-grade DevSecOps platform that combines static analysis with Retrieval-Augmented Generation (RAG) to deliver context-aware, explainable, and remediation-focused security intelligence.
</p>

<p align="center">
  <b>SAST • RAG Intelligence • AI Fix Suggestions • pgvector • Ollama</b>
</p>

---

## 🚀 Overview

DristiScan is a full-stack cybersecurity SaaS platform designed to scan source code, dependencies, and repositories to detect vulnerabilities and transform them into **actionable security intelligence**.

Unlike traditional tools that only detect issues, DristiScan:

* Explains vulnerabilities using trusted security knowledge
* Suggests secure fixes with reasoning
* Maps findings to OWASP, CWE, and CVE
* Uses vector search + AI for contextual insights

---

## 🧠 What Makes DristiScan Different

> Traditional scanners → detect
> DristiScan → **detect + explain + fix + prioritize**

* 🔍 Context-aware vulnerability explanations
* 🧾 Grounded AI responses (OWASP, CWE, CVE)
* 🛠️ Framework-specific remediation suggestions
* 📊 Risk-based prioritization
* 🧠 RAG-powered security intelligence

---

## ✨ Features

### 🔐 Security Scanning

* Multi-language static code analysis
* GitHub repository scanning
* Dependency vulnerability detection
* Secret & credential detection

### 🤖 AI Security Intelligence (RAG)

* Retrieval-Augmented Generation pipeline
* Knowledge sources:

  * OWASP Top 10
  * CWE dataset
  * NVD / CVE vulnerabilities
* Explainable AI with references
* Fix suggestions with reasoning
* Secure code examples

### 📊 Reporting & Insights

* Interactive security dashboard
* Risk scoring & severity classification
* PDF & JSON reports
* Scan history tracking

---

## 🏗️ System Architecture

```plaintext
                    ┌──────────────────────────┐
                    │        Frontend UI        │
                    │  React + Tailwind + UI   │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │        Backend API        │
                    │   FastAPI (Auth + APIs)  │
                    └────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼

┌──────────────────┐   ┌──────────────────┐   ┌────────────────────────┐
│  Scanner Engine   │   │   RAG Engine      │   │    Report Engine        │
│                  │   │                  │   │                        │
│ - SAST Rules     │   │ - Query Builder  │   │ - PDF Generator        │
│ - Secrets Scan   │   │ - Retriever      │   │ - JSON Reports         │
│ - Dependencies   │   │ - LLM Reasoning  │   │ - Risk Summary         │
└─────────┬────────┘   └─────────┬────────┘   └─────────┬──────────────┘
          │                      │                      │
          ▼                      ▼                      ▼

┌──────────────────┐   ┌──────────────────────────────┐
│  PostgreSQL DB    │   │   Vector DB (pgvector)       │
│                  │   │                              │
│ - Users           │   │ - OWASP chunks               │
│ - Findings        │   │ - CWE entries                │
│ - Reports         │   │ - CVE records                │
└──────────────────┘   │ - Embeddings (384-dim)       │
                       └────────────┬─────────────────┘
                                    │
                                    ▼
                       ┌──────────────────────────┐
                       │     AI Engine (LLM)       │
                       │     Ollama (Local LLM)    │
                       │  - Explain                │
                       │  - Fix Suggestions        │
                       └──────────────────────────┘
```

---

## 🧠 RAG Pipeline

```plaintext
Knowledge Base → Clean → Chunk → Embed → Store (pgvector)
                                      ↓
User Query / Finding → Embed → Similarity Search
                                      ↓
Top-K Relevant Chunks
                                      ↓
LLM → Grounded Explanation + Fix
```

---

## 📊 RAG Dataset

* OWASP Top 10 (A01–A10)
* CWE (~399 entries)
* NVD CVE (~9000 records)
* Total chunks: ~9500+
* Embedding model: `all-MiniLM-L6-v2` (384 dimensions)

---

## 📂 Project Structure

```bash
backend/
  app/
    rag/
      knowledge_base/
      chunks/
      embeddings/
      retriever.py
      orchestrator.py
    models/
    routes/
    scanners/
    services/

frontend/
  src/
    pages/
    components/

docker-compose.yml
```

---

## ⚡ Quick Start (Docker)

```bash
docker compose up --build
```

| Service  | URL                        |
| -------- | -------------------------- |
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |

---

## 🧪 Local Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

* `DATABASE_URL` – PostgreSQL connection
* `OLLAMA_URL` – LLM endpoint
* `OLLAMA_MODEL` – model name
* `RAG_TOP_K` – retrieval count
* `UPLOAD_DIR` – file storage

---

## 🔌 API Endpoints

### Scanning

* `POST /scan/code`
* `POST /scan/repo`

### Reports

* `GET /reports/{id}`
* `GET /reports/{id}/pdf`

### RAG / AI

* `POST /rag/explain`
* `POST /rag/fix`

---

## 🛡️ Example Output

```plaintext
Vulnerability: SQL Injection
Severity: Critical

Explanation:
User input is directly used in SQL query → attacker can manipulate DB

Fix:
Use parameterized queries

Reference:
OWASP A03, CWE-89
```

---

## 🤖 AI Security Engine

* Ollama (local LLM)
* RAG-based knowledge grounding
* Context-aware vulnerability analysis
* Secure fix recommendations

---

## 🚀 Production Readiness

* Dockerized services
* PostgreSQL + pgvector for vector search
* Local LLM support
* Modular architecture

---

## 🔮 Future Enhancements

* CI/CD integration
* VS Code extension
* Multi-repo scanning
* Security policy engine
* Automated patch generation

---

## 👩‍💻 Author

Built as a production-grade DevSecOps + AI Security system.
