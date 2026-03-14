# DristiScan – Cloud Code Security Scanner

Full-stack SaaS for scanning source code, dependencies, and entire GitHub repositories, classifying vulnerabilities, and exporting PDF/JSON reports. Built with FastAPI + PostgreSQL + React (Vite) + Tailwind + Framer Motion, with optional local AI analysis via Ollama.

---

## Architecture
- **Frontend**: React (Vite), Tailwind, Chart.js, Framer Motion, lucide-react icons. REST to backend.
- **Backend**: FastAPI, SQLAlchemy, Pydantic Settings, JWT auth, reportlab PDF; optional AI via Ollama.
- **DB**: PostgreSQL.
- **Containers**: Docker Compose orchestrates `backend`, `frontend`, `db`.
- **Pipeline**: Rule engine (100+ regex rules) → SAST → secrets → dependency advisories → optional Semgrep/Bandit → optional Ollama AI → risk scoring.

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
    services/              # scanner orchestration, risk, reports, github fetch
    utils/                 # JWT, files, pdf, rate limiter
frontend/
  src/
    App.jsx                # Routes
    context/               # Auth + Scan contexts
    pages/                 # Dashboard, Scan, Results, Reports, History, Settings, Login
    components/            # Layout, cards, charts, scan tabs/progress, filters, vuln list
docker-compose.yml
```

## Prerequisites
- Docker + Docker Compose **or** Python 3.11+ and Node 18+ with PostgreSQL.
- Optional: Ollama running locally (defaults to `http://localhost:11434`) for AI findings.

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

### Examples
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tester@example.com","password":"Password123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/scan/code \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"import os\nos.system(input())","file_name":"demo.py"}'
```

## Frontend Walkthrough
- **Scan**: Animated tabs for code paste, file upload, and GitHub repo scan (`/scan/repo`); live progress panel.
- **Results**: Severity filters + search, animated vulnerability list, PDF download.
- **Reports**: Animated list with inline PDF download.
- **Dashboard**: Live stats from `/reports/history` (totals, avg score, severity pie, score trend).
- **History/Settings**: History table; settings stub for profile/API key.

## Scanners (backend)
- **Rule engine**: 100+ regex rules in `backend/rules/vulnerability_rules.json`.
- **SAST**: heuristics for SQLi, command injection, eval/exec, file access, DOM XSS.
- **Secrets**: AWS keys, generic tokens, private keys, JWTs.
- **Dependencies**: minimal advisories for common packages.
- **AI (optional)**: Ollama (`codellama` by default) adds an “AI Security Review” finding.
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

## Licensing / Contributions
Internal project; open a PR or issue for changes. Provide logs and reproduction steps for bugs.
