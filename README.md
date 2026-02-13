#  AegisFlow
Production‑Ready Workflow & Project Management System

AegisFlow is a full‑stack workflow management system built with modern backend architecture and secure authentication practices. It demonstrates real‑world backend engineering, RBAC security, project ownership enforcement, testing, migrations, and a production‑ready structure.

Designed as a scalable SaaS‑ready backend with extensibility for enterprise‑grade features.

## 🌐 Live Overview
Modular backend system with authentication, role-based access control, and project management capabilities.

## 🏗 System Architecture
Client (Frontend)  
↓  
FastAPI Application Layer  
↓  
Service Layer (Business Logic)  
↓  
SQLAlchemy ORM  
↓  
PostgreSQL Database

Authentication Flow:  
User → Login → JWT Issued → Protected Routes → Role/Ownership Checks → DB

## 🛠 Tech Stack
Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic (Migrations)
- JWT (python-jose)
- Passlib (bcrypt)
- Pytest

DevOps & Tooling
- Docker (container-ready)
- Environment variable configuration
- Structured project layout
- Migration-based schema management

## ✨ Core Features
🔐 Authentication System
- User Signup
- Secure Login
- Password hashing with bcrypt
- JWT Access Tokens
- Token expiry handling
- `/auth/me` protected endpoint
- Secure dependency-based token validation

🛡 Role-Based Access Control (RBAC)
- Roles: `user`, `admin`
- Admin-only APIs
- Role validation dependency
- Prevent self-deactivation
- Clean authorization architecture

👤 Admin Management
- List users (paginated)
- Update user role
- Activate/Deactivate users
- Strict permission checks
- HTTP status consistency

📁 Project Management Module
- Create project
- View project
- Update project
- Soft delete project
- Owner-only access
- Admin override access
- Pagination support
- Inactive projects hidden

## 🗃 Database Design
Entities
- Users
- Roles
- Projects

Relationships
- User ↔ Role (Many-to-One)
- User ↔ Project (One-to-Many ownership)

Includes
- Soft delete strategy
- Timestamp tracking
- Migration-driven schema changes

## 🧪 Testing
Coverage
- Authentication tests
- RBAC tests
- Admin access tests 
- Ownership enforcement tests
- Soft delete verification

Framework
- pytest

Status
- All tests passing

## 📂 Project Structure
```
aegisflow/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── db/
│   │   ├── core/
│   │   ├── services/
│   │   └── utils/
│   ├── alembic/
│   ├── tests/
│   ├── alembic.ini
│   ├── requirements.txt
├── docker-compose.yml
├── .env
└── README.md
```

## ⚙️ Local Development Setup
1. Clone Repository
```bash
git clone https://github.com/your-username/aegisflow.git
cd aegisflow
```

2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Environment Variables
Create `.env`:
```bash
APP_ENV=development
DEBUG=true

JWT_SECRET=your_secret
JWT_EXPIRY_MINUTES=60

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aegisflow
```

4. Run Migrations
```bash
alembic upgrade head
```

5. Start Server
```bash
uvicorn app.main:app --reload
```

Access API Docs:  
`http://localhost:8000/docs`

## 🐳 Docker Setup
```bash
docker compose up --build
```

Runs:
- Backend
- PostgreSQL

## 📡 API Endpoints
Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/signup` | Create user |
| POST | `/auth/login` | Login & receive JWT |
| GET | `/auth/me` | Current user |

Admin

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/auth/admin/users` | List users |
| PATCH | `/auth/admin/users/{id}/role` | Update role |
| PATCH | `/auth/admin/users/{id}/status` | Activate/Deactivate |

Projects

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/projects` | Create project |
| GET | `/projects` | List projects |
| GET | `/projects/{id}` | View project |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Soft delete |

## 🔒 Security Highlights
- Password hashing with bcrypt
- JWT token expiry
- Role validation dependency
- Ownership enforcement
- Soft deletion pattern
- Admin override checks
- Protected route dependencies

## 📈 Scalability Considerations
- Migration-based DB evolution
- Modular architecture
- Service-layer ready
- Clean dependency injection
- Separation of concerns

## 🚀 Planned Enhancements
- Task module (Project → Tasks)
- Audit logging
- Refresh tokens
- Rate limiting
- Redis caching
- CI/CD integration
- Cloud deployment
- Monitoring & logging

## 🧠 Engineering Highlights
This project demonstrates:
- Backend system design
- Secure authentication implementation
- Authorization logic enforcement
- Database relationship modeling
- Migration-based schema management
- RESTful API design
- Production-readiness mindset
- Automated testing strategy

## 🎯 Why This Project Stands Out
This is not a CRUD demo. It includes:
- Secure authentication
- RBAC
- Ownership logic
- Admin controls
- Soft delete patterns
- Migration workflows
- Structured architecture
- Test coverage

These are concepts used in real production systems.

## 👩‍💻 Author
Tanya Jha  
Backend Developer  
FastAPI | PostgreSQL | System Design
