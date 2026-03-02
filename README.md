# Drishti-Scan
A production-ready cloud-based Code Security Scanner SaaS application.

## Features
- **Authentication**: Secure JWT-based registration and login.
- **Code Scanner**: Paste code snippets or upload files (.py, .js, .json, etc.).
- **SAST**: Regular expression based scanning for SQLi, XSS, Command Injection, and more.
- **Secret Detection**: Identifies AWS keys, generic API keys, JWTs, and private keys.
- **Dependency Checking**: Scans `requirements.txt` and `package.json` for known outdated packages.
- **Reporting**: Generates a risk score, severity distribution charts, and downloadable PDF reports.

## Tech Stack
- **Backend**: FastAPI (Python), PostgreSQL, SQLAlchemy
- **Frontend**: React (Vite), Tailwind CSS, Chart.js
- **DevOps**: Docker, Docker Compose, GitHub Actions

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.

### Running with Docker Compose
1. Clone the repository.
2. Navigate to the root directory `Drishti-Scan`.
3. Run the following command to build and start the services:
   ```bash
   docker-compose up --build
   ```
4. Access the web interface at `http://localhost:5173`
5. Access the API documentation at `http://localhost:8000/docs`

### Local Setup (Without Docker Compose for Backend/Frontend)
1. Start a local PostgreSQL instance and create a database named `drishtiscan` with user `admin` and password `adminpassword` (or update `.env`).
2. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
3. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Next Steps for Production
- Set up a robust secret management injected via environment variables.
- Use a production WSGI server (e.g., Gunicorn with Uvicorn workers).
- Integrate an actual vulnerability database feed (e.g., OSV API) rather than static mock rules.
- Set up HTTPS via Nginx or Traefik reverse proxy.
- Implement pagination and rate-limiting on endpoints.
