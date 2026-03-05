# DristiScan – Cloud Code Security Scanner

A full-stack SaaS for scanning source code and dependencies, classifying vulnerabilities, and delivering PDF/JSON reports. Built with FastAPI + PostgreSQL + React (Vite) + Tailwind.

---

## Architecture
- **Frontend**: React (Vite), Tailwind, Chart.js, Framer Motion. Communicates with backend via REST.
- **Backend**: FastAPI, SQLAlchemy, Pydantic Settings, JWT auth, PDF reports (fpdf2).
- **DB**: PostgreSQL.
- **Containers**: Docker Compose orchestrates `backend`, `frontend`, `db`.
- **Background**: FastAPI background tasks (simple) for cleanup; scanners are modular (SAST, secrets, dependencies).

---

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
    services/              # scanner orchestration, risk, reports
    utils/                 # JWT, files, pdf, rate limiter
frontend/
  src/
    App.jsx                # Routes
    context/               # Auth + Scan contexts
    pages/                 # Dashboard, Scan, Results, Reports, History, Settings, Login
    components/            # Layout, cards, charts, editor panel, badges
docker-compose.yml
```

---

## Prerequisites
- Docker + Docker Compose **or** Python 3.11+ and Node 18+ with PostgreSQL.

---

## Quick Start (Docker)
```bash
docker-compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

---

## Backend: Local (without Compose)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash/PowerShell adjusted
pip install -r requirements.txt

# required env (override defaults as needed)
set DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/drishtiscan
set SECRET_KEY=your-secret
set ACCESS_TOKEN_EXPIRE_MINUTES=60

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables (backend)
- `DATABASE_URL` (required) e.g. `postgresql://admin:adminpassword@db:5432/drishtiscan`
- `SECRET_KEY` (required for JWT)
- `ALGORITHM` (default HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60)
- `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB`, `ALLOWED_FILE_TYPES` (optional)

---

## Frontend: Local (without Compose)
```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
# Open http://localhost:5173
```

---

## Core API Endpoints
- **Auth**
  - `POST /auth/register` – `{email, password}`
  - `POST /auth/login` – `{email, password}` → `access_token`
  - `GET /auth/profile` – Bearer token
- **Scan**
  - `POST /scan/code` – `{ code, file_name }`
  - `POST /scan/upload` – multipart `file`
- **Reports**
  - `GET /reports/{scan_id}`
  - `GET /reports/{scan_id}/pdf`
  - `GET /reports/history`
- **Health**: `GET /health`

### Example (curl)
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tester@example.com","password":"Password123"}' | jq -r .access_token)

curl -X POST http://localhost:8000/scan/code \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"import os\nos.system(input())","file_name":"demo.py"}'
```

---

## Frontend Walkthrough
- **Login/Signup**: DristiScan branding with eye icon.
- **Dashboard**: Live stats from `/reports/history` (totals, avg score, severity pie, score trend).
- **Scan**: Paste code or upload file; uses `/scan/code` or `/scan/upload`; progress + error hints.
- **Results**: Shows last scan, risk score/level, severity breakdown, and vulnerability cards.
- **History & Reports**: Pulls `/reports/history`; report rows show score/issues; PDF/JSON endpoints available.
- **Settings**: Profile stub, API key placeholder, theme toggles.

---

## Scanners (backend)
- **SAST**: regex rules for SQLi, command injection, eval/exec, file access, DOM XSS.
- **Secrets**: AWS keys, generic tokens, private keys, JWTs.
- **Dependencies**: `requirements.txt` / `package.json` minimal advisory examples.
- **Risk**: Weighted severity → score (100 - points) + risk level bands.

---

## Development Tips
- Update dependencies: `pip install -r backend/requirements.txt` and `npm install` (frontend).
- Clean uploads: backend stores temp files under `backend/uploads` (auto cleanup via background task).
- Logs: backend logs requests/errors; check `docker logs drishti_scan_backend`.
- If DB schema drifts, drop volumes: `docker-compose down -v && docker-compose up --build`.

---

## Thunder Client / Postman Quick Import
Use base URL `http://localhost:8000` and sequence:
1) POST /auth/register
2) POST /auth/login → save `token`
3) GET /auth/profile (Bearer)
4) POST /scan/code (Bearer)
5) GET /reports/{scan_id} (Bearer)
6) GET /reports/history (Bearer)

---

## Production Checklist
- Use managed Postgres + proper credentials/rotation.
- Set strong `SECRET_KEY`, adjust token expiry.
- Put Nginx/Traefik in front with HTTPS and gzip.
- Add Alembic migrations before schema changes.
- Externalize rate limiting (Redis) and storage (S3) for uploads.
- Hook scanners to real vulnerability feeds (e.g., OSV) and SAST engines.

---

## Licensing / Contributions
Internal project; open a PR or issue for changes. Provide logs and reproduction steps for bugs.
