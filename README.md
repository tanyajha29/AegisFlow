<p align="center">
  <img src="docs/screens/logo.png" alt="DristiScan Logo" width="220" />
</p>

<h1 align="center">DristiScan - Cloud Code Security Scanner</h1>

<p align="center">
A modern DevSecOps-inspired platform for scanning source code, dependencies, and GitHub repositories to detect vulnerabilities and generate professional security reports.
</p>

---

## Overview

DristiScan is a full-stack cybersecurity SaaS platform that analyzes codebases for security vulnerabilities using a combination of:

- Rule-based static analysis
- Secret detection
- Dependency scanning
- AI-assisted insights (via Ollama)

It provides:

- Multi-language code scanning
- GitHub repository analysis
- Risk scoring
- Downloadable PDF/JSON reports
- Interactive security dashboard

---

## Features

- Multi-language source code scanning
- GitHub repository scanning
- Dependency vulnerability detection
- Secret key and credential detection
- AI-powered vulnerability explanations (Ollama)
- Risk scoring with severity classification
- Professional PDF and JSON reports
- Interactive dashboard with analytics and history

---

## Architecture

- Frontend: React (Vite), Tailwind CSS, Chart.js, Framer Motion
- Backend: FastAPI, SQLAlchemy, Pydantic Settings, JWT Auth
- Database: PostgreSQL
- Containers: Docker Compose (frontend, backend, db)
- AI Integration: Local models via Ollama

---

## Scanning Pipeline
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
 +- Semgrep
 +- Bandit
 +- AI Analysis (Ollama)
        |
        v
Risk Scoring
        |
        v
Vulnerability Report (PDF / JSON)
```

---

## Project Structure
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
```

---

## Quick Start (Docker)
```bash
docker-compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Backend Setup (Local)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # on PowerShell/Git Bash adjust accordingly
pip install -r requirements.txt

set DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/drishtiscan
set SECRET_KEY=your-secret
set ACCESS_TOKEN_EXPIRE_MINUTES=60
set GITHUB_TOKEN=your-github-token
set OLLAMA_URL=http://localhost:11434

uvicorn app.main:app --reload
```

### Frontend Setup (Local)
```bash
cd frontend
npm ci --legacy-peer-deps
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

---

## Environment Variables (backend)
- DATABASE_URL ï¿½ PostgreSQL connection string
- SECRET_KEY ï¿½ JWT secret key
- ACCESS_TOKEN_EXPIRE_MINUTES ï¿½ Token expiry
- GITHUB_TOKEN ï¿½ Required for repo scanning
- OLLAMA_URL ï¿½ Local AI endpoint
- UPLOAD_DIR ï¿½ File upload path
- MAX_UPLOAD_SIZE_MB ï¿½ Upload size limit

---

## API Endpoints
- Auth: POST /auth/register, POST /auth/login, GET /auth/profile
- Scan: POST /scan/code, POST /scan/upload, POST /scan/repo
- Reports: GET /reports/history, GET /reports/{scan_id}, GET /reports/{scan_id}/pdf
- Health: GET /health

---

## Example Usage
Code Scan
```bash
curl -X POST http://localhost:8000/scan/code \
 -H "Authorization: Bearer TOKEN" \
 -H "Content-Type: application/json" \
 -d '{"code":"import os\\nos.system(input())","file_name":"demo.py"}'
```

Repo Scan
```bash
curl -X POST http://localhost:8000/scan/repo \
 -H "Authorization: Bearer TOKEN" \
 -H "Content-Type: application/json" \
 -d '{"repo_url":"https://github.com/user/project"}'
```

---

## Example Vulnerability Output
```
Type: SQL Injection
Severity: Critical
File: login.py
Line: 24
Description: User input is concatenated into a SQL query without sanitization.
Remediation: Use parameterized queries with placeholders.
```

---

## AI Security Analysis
DristiScan integrates with Ollama to provide:
- AI-generated vulnerability explanations
- Remediation suggestions
- Executive summaries in reports

---

## UI Preview
- Dashboard
- Scan Workspace
- Scan Results
- History
- Reports

---

## Scanning Capabilities
- Rule-based vulnerability engine (100+ rules)
- Static analysis (SQLi, command injection, XSS, etc.)
- Secret detection (API keys, tokens, credentials)
- Dependency risk detection
- Optional AI-based analysis via Ollama
- Risk scoring and severity classification

---

## GitHub Repository Scanning
- Accepts repository URLs
- Fetches files via GitHub API
- Scans multi-language codebases
- Aggregates vulnerabilities into a unified report

---

## Development Tips
- Use docker logs for debugging containers
- Clean uploads directory periodically
- Reset database with:
```bash
docker-compose down -v
docker-compose up --build
```

---

## Production Checklist
- Use managed PostgreSQL
- Configure HTTPS (Nginx / Traefik)
- Secure environment variables
- Add Alembic migrations
- Integrate Redis for rate limiting
- Connect real vulnerability feeds (OSV, NVD)

---

## Limitations
- Rule-based scanning may produce false positives
- Dependency database is limited
- AI accuracy depends on model quality
- Large repositories may increase scan time

---

## Future Improvements
- CVE/NVD integration
- Container security scanning
- Distributed scan workers
- Expanded language support
- Advanced dependency intelligence

## Environment Variables (clean reference)
- `DATABASE_URL` – PostgreSQL connection string
- `SECRET_KEY` – JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` – Token expiry
- `GITHUB_TOKEN` – GitHub token for repo scans
- `OLLAMA_URL` – Ollama base URL (e.g., `http://host.docker.internal:11434` or `http://172.17.0.1:11434` on WSL)
- `OLLAMA_MODEL` – Model name (e.g., `deepseek-coder`)
- `OLLAMA_TIMEOUT_SECONDS` – Timeout for Ollama calls
- `UPLOAD_DIR` – File upload path
- `MAX_UPLOAD_SIZE_MB` – Upload size limit

### Ollama setup (Docker / WSL)
1) Bind Ollama to all interfaces:
```bash
sudo pkill -f "ollama serve" || true
sudo OLLAMA_HOST=0.0.0.0 ollama serve
```
2) Pull a model:
```bash
OLLAMA_HOST=0.0.0.0 ollama pull deepseek-coder:latest
```
3) In `.env` set a reachable URL:
```bash
OLLAMA_URL=http://host.docker.internal:11434   # or http://172.17.0.1:11434 in WSL
OLLAMA_MODEL=deepseek-coder
OLLAMA_TIMEOUT_SECONDS=60
```
4) Restart backend:
```bash
docker compose up -d backend
```
