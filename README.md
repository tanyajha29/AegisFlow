# DristiScan – Cloud Code Security Scanner

![DristiScan Logo](docs/screens/logo.png)

DristiScan is a DevSecOps-inspired platform that analyzes source code, dependencies, and GitHub repositories for security vulnerabilities. It combines rule-based static analysis, dependency scanning, secret detection, and optional AI-assisted insights (via Ollama) to generate professional vulnerability reports. Key capabilities include multi-language code scanning, GitHub repository scanning, automated vulnerability classification, risk scoring, and downloadable PDF/JSON reports through an interactive dashboard.

## Features
- Source code vulnerability scanning (multi-language)
- GitHub repository scanning
- Dependency vulnerability detection
- Secret key detection
- AI-based vulnerability explanations (Ollama)
- Risk scoring system with severity bands
- Professional PDF reports (with optional AI executive insight)
- Interactive security dashboard with trends/history

## Architecture
- **Frontend**: React (Vite), Tailwind, Chart.js, Framer Motion, lucide-react; REST to backend.
- **Backend**: FastAPI, SQLAlchemy, Pydantic Settings, JWT auth, reportlab PDFs, optional AI via Ollama.
- **DB**: PostgreSQL.
- **Containers**: Docker Compose orchestrates `backend`, `frontend`, `db`.
- **Pipeline**: Rule engine (100+ regex rules) → SAST → secrets → dependency advisories → optional Semgrep/Bandit → optional Ollama AI → risk scoring.

### Scanning Pipeline
```
User Code / Repo
        │
        ▼
Rule Engine (100+ rules)
        │
        ▼
SAST Analysis
        │
        ▼
Secret Detection
        │
        ▼
Dependency Scanner
        │
        ▼
Optional Tools
 ├─ Semgrep
 ├─ Bandit
 └─ AI Analysis (Ollama)
        │
        ▼
Risk Scoring
        │
        ▼
Vulnerability Report (PDF/JSON)
```

## Repo Structure
```
backend/
  app/
    main.py                # FastAPI entrypoint
    config.py              # Settings (env-driven)
    database.py            # SQLAlchemy engine/session
    models/                # users, scans, vulnerabilities
    routes/                # auth, scan, reports
    scanners/              # sast, secrets, dependency rules
    services/              # scanner orchestration, risk, reports, GitHub fetch, AI summary
    utils/                 # JWT, files, pdf, rate limiter
frontend/
  src/
    App.jsx                # Routes
    context/               # Auth + Scan contexts
    pages/                 # Dashboard, Scan, Results, Reports, History, Settings, Login
    components/            # Layout, cards, charts, scan tabs/progress, filters, vuln list
docker-compose.yml
docs/screens/              # UI screenshots
```

## Quick Start (Docker)
```bash
docker-compose up --build
# Frontend: http://localhost:5173   (or your WSL IP)
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```
If using WSL2 + Docker, set `VITE_API_BASE_URL=http://<wsl-ip>:8000` and open `http://<wsl-ip>:5173`.

## Backend: Local (without Compose)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # PowerShell/Git Bash adjust
pip install -r requirements.txt

# required env
set DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/drishtiscan
set SECRET_KEY=your-secret
set ACCESS_TOKEN_EXPIRE_MINUTES=60
set GITHUB_TOKEN=your-github-token   # recommended for repo scans
set OLLAMA_URL=http://localhost:11434

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend: Local (without Compose)
```bash
cd frontend
npm ci --legacy-peer-deps
VITE_API_BASE_URL=http://localhost:8000 npm run dev
# Open http://localhost:5173
```

### Environment Variables (backend)
- `DATABASE_URL` (required) e.g. `postgresql://admin:adminpassword@db:5432/drishtiscan`
- `SECRET_KEY` or `JWT_SECRET_KEY` (required for JWT)
- `ALGORITHM` (default HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60)
- `GITHUB_TOKEN` (recommended for repo scans)
- `OLLAMA_URL` (default `http://localhost:11434`)
- `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB`, `ALLOWED_FILE_TYPES` (optional)

## Core API Endpoints
- **Auth**: `POST /auth/register`, `POST /auth/login`, `GET /auth/profile`
- **Scan**: `POST /scan/code`, `POST /scan/upload`, `POST /scan/repo`
- **Reports**: `GET /reports/history`, `GET /reports/{scan_id}`, `GET /reports/{scan_id}/pdf`
- **Health**: `GET /health`

### Example (code scan)
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tester@example.com","password":"Password123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/scan/code \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"import os\nos.system(input())","file_name":"demo.py"}'
```

### Example (repo scan)
```bash
curl -X POST http://localhost:8000/scan/repo \
 -H "Authorization: Bearer $TOKEN" \
 -H "Content-Type: application/json" \
 -d '{"repo_url":"https://github.com/user/project"}'
```

## Example Vulnerability Output
```
Type: SQL Injection
Severity: Critical
File: login.py
Line: 24
Description: User input is concatenated into a SQL query without sanitization.
Remediation: Use parameterized queries with placeholders.
```

## AI Security Analysis
DristiScan can optionally use a local Ollama model to add:
- Executive insight summaries in PDFs
- Vulnerability explanations and remediation hints
- Suspicious code pattern analysis

## UI Preview
### Dashboard
![Dashboard](docs/screens/ui-screen-1.png)
### Scaning Page
![Scan Workspace](docs/screens/ui-screen-2.png)
### Scan Results
![Scan Progress](docs/screens/ui-screen-3.png)
### Scan History
![Results & Filters](docs/screens/ui-screen-4.png)
### Reports
![Reports Download](docs/screens/ui-screen-5.png)

## Frontend Walkthrough
- **Scan**: Animated tabs for code paste, file upload, and GitHub repo scan; live progress panel.
- **Results**: Severity filters + search, animated vulnerability list, PDF download.
- **Reports**: Animated list with inline PDF download.
- **Dashboard**: Live stats from `/reports/history` (totals, avg score, severity pie, score trend).
- **History/Settings**: History table; settings stub for profile/API key.

## Scanners (backend)
- **Rule engine**: 100+ regex rules in `backend/rules/vulnerability_rules.json`.
- **SAST**: heuristics for SQLi, command injection, eval/exec, file access, DOM XSS.
- **Secrets**: AWS keys, generic tokens, private keys, JWTs.
- **Dependencies**: minimal advisories for common packages.
- **AI (optional)**: Ollama adds an “AI Security Review” finding and PDF insight.
- **Risk**: Weighted severity → score (100 - points) + risk bands.

## Repo Scanning
- `POST /scan/repo` with `{ "repo_url": "https://github.com/user/repo" }`
- Uses GitHub API + `GITHUB_TOKEN` to fetch supported files (py/js/ts/java/go/php/rb/c/cpp), scans all files, aggregates findings.

## Development Tips
- Update deps: `pip install -r backend/requirements.txt` and `npm ci --legacy-peer-deps` (frontend).
- Clean uploads: backend stores temp files under `backend/uploads` (auto cleanup via background task).
- Logs: `docker logs drishti_scan_backend` / `drishti_scan_frontend` for containerized runs.
- If DB schema drifts, `docker-compose down -v && docker-compose up --build`.

## Production Checklist
- Use managed Postgres + proper credentials/rotation.
- Set strong `SECRET_KEY`, adjust token expiry.
- Put Nginx/Traefik in front with HTTPS and gzip.
- Add Alembic migrations before schema changes.
- Externalize rate limiting (Redis) and storage (S3) for uploads.
- Hook scanners to real vulnerability feeds (e.g., OSV) and SAST engines.

## Limitations
- Rule-based scanning can produce false positives.
- Dependency scanner uses a limited advisory dataset.
- AI quality depends on the local model.
- Large repositories may take longer to scan.

## Future Improvements
- Integrate CVE feeds (NVD / OSV)
- Add container security scanning
- Implement distributed scan workers
- Support additional languages
- Expand dependency vulnerability database

## License
MIT License


