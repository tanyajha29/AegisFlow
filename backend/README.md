<p align="center">
  <b>DristiScan Backend — FastAPI Security Engine</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-Vector%20Search-purple" />
  <img src="https://img.shields.io/badge/AI-RAG%20Enabled-orange" />
  <img src="https://img.shields.io/badge/Security-DevSecOps-red" />
</p>

---

## 🚀 Overview

The DristiScan Backend is a **FastAPI-based security scanning engine** responsible for:

* Static code analysis (SAST)
* Secret detection
* Dependency scanning
* AI-powered vulnerability explanation using **RAG (Retrieval-Augmented Generation)**
* Report generation (JSON + PDF)

It serves as the **core intelligence layer** of the DristiScan platform.

---

## 🧠 Key Capabilities

### 🔐 Security Scanning Engine

* Regex-based vulnerability detection (113+ rules)
* Injection, authentication, cryptography, and filesystem checks
* Line-by-line static code scanning

### 🤖 AI + RAG Integration

* Context-aware vulnerability explanations
* Knowledge sources:

  * OWASP Top 10
  * CWE dataset
  * NVD CVE records
* Vector similarity search using **pgvector**
* Local LLM inference via **Ollama**

### 📊 Reporting Engine

* Structured JSON reports
* PDF report generation
* Severity classification & prioritization

---

## ⚙️ Quickstart (Local)

### 1️⃣ Setup Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2️⃣ Configure Environment Variables

```bash
export DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/drishtiscan
export SECRET_KEY=supersecretkey_change_in_production
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3️⃣ Run Backend Server

```bash
uvicorn app.main:app --reload
```

---

## 🐳 Docker Setup

Run full system:

```bash
docker-compose up --build
```

* Backend runs on: **http://localhost:8000**

---

## 🧠 RAG Architecture (Backend Perspective)

```plaintext
Scan Result
    ↓
RAG Query Builder
    ↓
pgvector Similarity Search
    ↓
Top-K Security Knowledge Chunks
    ↓
Ollama (LLM)
    ↓
AI Explanation + Fix Suggestion
```

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
    services/
    scanners/
  rules/
    vulnerability_rules.json
```

---

## 🧾 Vulnerability Rule Engine

* Central file: `backend/rules/vulnerability_rules.json`
* Contains **113+ detection rules**

### Rule Fields:

* `name`
* `category`
* `severity`
* `pattern` (regex)
* `description`
* `remediation`
* `cwe_reference` (optional)

### Example Rule:

```json
{
  "name": "SQL Concatenation Injection",
  "category": "Injection",
  "severity": "Critical",
  "pattern": "(?i)select\\s+.*from\\s+.*\\+.*",
  "description": "SQL built via string concatenation.",
  "remediation": "Use parameterized queries."
}
```

---

## 🔌 Core API Endpoints

### 🔐 Authentication

* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/profile`

### 🔍 Scanning

* `POST /scan/code`
* `POST /scan/upload`

### 📊 Reports

* `GET /reports/{scan_id}`
* `GET /reports/{scan_id}/pdf`
* `GET /reports/history`

### 🤖 RAG / AI

* `POST /rag/explain`
* `POST /rag/fix`

---

## 🧪 Example Usage

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/scan/code \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"import os\\nos.system(input())","file_name":"example.py"}'
```

---

## 🧠 AI Output Example

```plaintext
Vulnerability: Command Injection
Severity: Critical

Explanation:
User input is directly passed to system command execution.

Fix:
Sanitize input and avoid using os.system()

Reference:
OWASP A03, CWE-78
```

---

## 🔐 Environment Variables

* `DATABASE_URL`
* `SECRET_KEY`
* `ACCESS_TOKEN_EXPIRE_MINUTES`
* `OLLAMA_URL`
* `OLLAMA_MODEL`
* `RAG_TOP_K`

---


