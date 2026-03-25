
<p align="center">
  <img src="docs/screens/logo.png" alt="DristiScan Logo" width="220" />
</p>

<h1 align="center">DristiScan — Code Security Scanner</h1>

<p align="center">
A modern DevSecOps-inspired platform for scanning source code, dependencies, and GitHub repositories to detect vulnerabilities and generate professional security reports.
</p>

---

## 🚀 Overview

DristiScan is a full-stack cybersecurity SaaS platform that analyzes codebases for security vulnerabilities using:

- Rule-based static analysis
- Secret detection
- Dependency scanning
- AI-assisted insights (via Ollama)

### 🔍 Key Capabilities

- Multi-language code scanning  
- GitHub repository analysis  
- Risk scoring and severity classification  
- Downloadable PDF & JSON reports  
- Interactive security dashboard  

---

## ✨ Features

- Multi-language source code scanning  
- GitHub repository scanning  
- Dependency vulnerability detection  
- Secret key and credential detection  
- AI-powered vulnerability explanations & fix suggestions (Ollama RAG)  
- Risk scoring with severity classification  
- Professional PDF and JSON reports  
- Interactive dashboard with analytics and history  

---

## 🏗️ Architecture

| Layer        | Technology Stack |
|-------------|----------------|
| Frontend     | React (Vite), Tailwind CSS, Chart.js, Framer Motion |
| Backend      | FastAPI, SQLAlchemy, Pydantic, JWT Authentication |
| Database     | PostgreSQL |
| Containers   | Docker Compose |
| AI Engine    | Ollama (Local LLMs) |

---

## ⚙️ Scanning Pipeline

```

User Code / Repository
|
v
Rule Engine (100+ rules)
|
v
SAST Analysis
|
v
Secret Detection
|
v
Dependency Scanner
|
v
Optional Tools
├─ Semgrep
├─ Bandit
└─ AI Analysis (Ollama)
|
v
Risk Scoring
|
v
Vulnerability Report (PDF / JSON)

```

---

## 📂 Project Structure

```

backend/
app/
main.py
config.py
database.py
models/
routes/
scanners/
services/
utils/

frontend/
src/
App.jsx
context/
pages/
components/

docker-compose.yml
docs/screens/

````

---

## ⚡ Quick Start (Docker)

```bash
docker-compose up --build
````

| Service  | URL                                                      |
| -------- | -------------------------------------------------------- |
| Frontend | [http://localhost:5173](http://localhost:5173)           |
| Backend  | [http://localhost:8000](http://localhost:8000)           |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## 🖼️ Product Screens

| Dashboard | Start a Scan |
| --- | --- |
| <img src="docs/screens/dashboard.png" alt="Dashboard overview" width="100%" style="border:1px solid #e5e7eb; border-radius:12px;"> | <img src="docs/screens/scan.png" alt="Scan launch form" width="100%" style="border:1px solid #e5e7eb; border-radius:12px;"> |

| Findings | Reports |
| --- | --- |
| <img src="docs/screens/results.png" alt="Findings & filters" width="100%" style="border:1px solid #e5e7eb; border-radius:12px;"> | <img src="docs/screens/reports.png" alt="Report exports" width="100%" style="border:1px solid #e5e7eb; border-radius:12px;"> |

---

## 🧪 Local Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Adjust for OS
pip install -r requirements.txt

set DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/drishtiscan
set SECRET_KEY=your-secret
set ACCESS_TOKEN_EXPIRE_MINUTES=60
set GITHUB_TOKEN=your-github-token
set OLLAMA_URL=http://localhost:11434

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci --legacy-peer-deps
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

---

## 🔐 Environment Variables

### Backend

* `DATABASE_URL` — PostgreSQL connection string
* `SECRET_KEY` — JWT secret key
* `ACCESS_TOKEN_EXPIRE_MINUTES` — Token expiry
* `GITHUB_TOKEN` — GitHub token for repo scans
* `OLLAMA_URL` — Ollama endpoint
* `OLLAMA_MODEL` — Model name (e.g., `deepseek-coder`)
* `OLLAMA_TIMEOUT_SECONDS` — Timeout for AI calls
* `UPLOAD_DIR` — File upload path
* `MAX_UPLOAD_SIZE_MB` — Upload size limit

---

## 🔌 API Endpoints

### Authentication

* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/profile`

### Scanning

* `POST /scan/code`
* `POST /scan/upload`
* `POST /scan/repo`

### Reports

* `GET /reports/history`
* `GET /reports/{scan_id}`
* `GET /reports/{scan_id}/pdf`

### RAG / AI Insights

* `POST /rag/explain` — grounded explanation for an existing finding
* `POST /rag/fix` — grounded fix suggestion for an existing finding

### Health

* `GET /health`

---

## 📌 Example Usage

### Code Scan

```bash
curl -X POST http://localhost:8000/scan/code \
 -H "Authorization: Bearer TOKEN" \
 -H "Content-Type: application/json" \
 -d '{"code":"import os\\nos.system(input())","file_name":"demo.py"}'
```

### Repository Scan

```bash
curl -X POST http://localhost:8000/scan/repo \
 -H "Authorization: Bearer TOKEN" \
 -H "Content-Type: application/json" \
 -d '{"repo_url":"https://github.com/user/project"}'
```

---

## 🛡️ Example Vulnerability Output

```
Type: SQL Injection
Severity: Critical
File: login.py
Line: 24
Description: User input is concatenated into a SQL query without sanitization.
Remediation: Use parameterized queries with placeholders.
```

---

## 🤖 AI Security Analysis

- Local Ollama integration for Explain and Suggest Fix
- RAG-backed knowledge base (SQL Injection, XSS, Command Injection, Secrets, Path Traversal)
- Frontend AI Insights Drawer with tabs (Explain / Suggest Fix), code preview, and grounded references

---

## 🧠 Scanning Capabilities

* Rule-based vulnerability engine (100+ rules)
* Static analysis (SQLi, XSS, command injection, etc.)
* Secret detection (API keys, tokens, credentials)
* Dependency risk analysis
* Optional AI-based insights
* Risk scoring and severity classification

---

## 🔗 GitHub Repository Scanning

* Accepts repository URLs
* Fetches code via GitHub API
* Supports multi-language analysis
* Generates unified vulnerability reports

---

## 🛠️ Development Tips

* Use `docker logs` for debugging
* Clean upload directories periodically
* Reset environment:

```bash
docker-compose down -v
docker-compose up --build
```

---

## 🚀 Production Checklist

* Use managed PostgreSQL
* Enable HTTPS (Nginx / Traefik)
* Secure environment variables
* Add Alembic migrations
* Integrate Redis (rate limiting)
* Connect vulnerability feeds (OSV, NVD)

---

## ⚠️ Limitations

* Rule-based scanning may produce false positives
* Limited dependency database
* AI accuracy depends on model quality
* Large repositories may increase scan time

---

## 🔮 Future Improvements

* CVE/NVD integration
* Container security scanning
* Distributed scanning workers
* Expanded language support
* Advanced dependency intelligence

---

## 🤖 Ollama Setup (Docker / WSL)

### 1. Start Ollama

```bash
sudo pkill -f "ollama serve" || true
sudo OLLAMA_HOST=0.0.0.0 ollama serve
```

### 2. Pull Model

```bash
OLLAMA_HOST=0.0.0.0 ollama pull deepseek-coder:latest
```

### 3. Configure `.env`

```bash
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=deepseek-coder
OLLAMA_TIMEOUT_SECONDS=60
```

### 4. Restart Backend

```bash
docker compose up -d backend
```

### Cross-host Docker tip

If Ollama runs on a different machine than your Docker host (e.g., laptop vs. Ubuntu server), set `OLLAMA_URL` to the reachable IP of that machine, for example:

```
OLLAMA_URL=http://192.168.1.50:11434
```

Ensure Ollama is started with `OLLAMA_HOST=0.0.0.0 ollama serve` (or equivalent) and that port `11434` is open to the Docker host.
