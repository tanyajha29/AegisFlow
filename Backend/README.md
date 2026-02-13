# AegisFlow Backend

FastAPI backend with PostgreSQL, SQLAlchemy, JWT authentication, RBAC, admin APIs, and a Projects module with ownership rules.

## Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT (python-jose)
- Passlib bcrypt
- Pytest + httpx

## Features
- Signup and login with JWT access tokens
- `/auth/me` protected route
- Role-based access control (user/admin)
- Admin-only user management APIs
- Projects module with owner/admin authorization and soft delete
- Alembic migrations
- Test suite for auth, admin RBAC, and projects

## Project Structure (Backend)
```
Backend/
  app/
    api/
      routes/
        auth.py
        projects.py
        router.py
      deps.py
    core/
      config.py
      security.py
      logging.py
    db/
      base.py
      seed.py
      session.py
    models/
      user.py
      role.py
      project.py
    schemas/
      project.py
    utils/
      jwt.py
  alembic/
    env.py
    script.py.mako
    versions/
  tests/
  requirements.txt
  .env
```

## Requirements
- Python 3.13
- PostgreSQL (local or Docker)
- Virtualenv recommended

## Environment Variables
Defined in `Backend/.env`:
```
APP_ENV=development
DEBUG=true

JWT_SECRET=change_this_secret
JWT_EXPIRY_MINUTES=60
JWT_ALGORITHM=HS256

DATABASE_URL=postgresql://user:password@localhost:5432/dbname

CORS_ORIGINS=["http://localhost:3000"]
```

## Install
From `Backend/`:
```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run Server
From `Backend/`:
```bash
venv\Scripts\python -m uvicorn app.main:app --reload
```

## Database Migrations (Alembic)
From `Backend/`:
```bash
alembic upgrade head
```

To generate a new migration:
```bash
alembic revision --autogenerate -m "your message"
```

## Seeded Roles
On app startup, default roles are created if missing:
- `user`
- `admin`

## Authentication Overview
1. Signup via `/auth/signup`
2. Login via `/auth/login` to receive JWT
3. Use token in `Authorization: Bearer <token>` header

The JWT `sub` claim contains the user ID.

## API Endpoints

### Auth

**POST `/auth/signup`**
Request:
```json
{
  "username": "alice",
  "password": "Password123!"
}
```
Response: `201`
```json
{
  "id": 1,
  "username": "alice",
  "is_active": true
}
```

**POST `/auth/login`**
Request:
```json
{
  "email": "alice",
  "password": "Password123!"
}
```
Response: `200`
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

**GET `/auth/me`**
Headers:
```
Authorization: Bearer <token>
```
Response: `200`
```json
{
  "id": 1,
  "username": "alice",
  "is_active": true
}
```

### Admin APIs (admin only)

**GET `/auth/admin/users`**
Query params: `limit` (1-200), `offset` (>=0)

**PATCH `/auth/admin/users/{user_id}/role`**
Request:
```json
{
  "role_name": "admin"
}
```
Responses:
- `200` updated user
- `400` invalid role
- `404` user not found

**PATCH `/auth/admin/users/{user_id}/status`**
Request:
```json
{
  "is_active": false
}
```
Notes:
- Admin cannot deactivate themselves (returns `400`).

### Projects

**POST `/projects`**
Creates a project owned by the current user.
Request:
```json
{
  "name": "Project Alpha",
  "description": "First project"
}
```
Response: `201`
```json
{
  "id": 1,
  "name": "Project Alpha",
  "description": "First project",
  "owner_id": 1,
  "created_at": "2026-02-13T12:00:00Z"
}
```

**GET `/projects`**
- Auth required
- Admin: all active projects
- User: only their active projects
Query params: `limit` (1-200), `offset` (>=0)

**GET `/projects/{project_id}`**
- Owner or admin only
- `404` if not found

**PUT `/projects/{project_id}`**
- Owner or admin only
Request:
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**DELETE `/projects/{project_id}`**
- Owner or admin only
- Soft delete (`is_active=false`)
- Deactivated projects are excluded from listings

## Authorization Rules
- Only admins can access admin routes.
- Admins can access all projects.
- Owners can manage their own projects.
- Other users get `403 Forbidden`.
- Invalid tokens return `401 Unauthorized`.

## Tests
From `Backend/`:
```bash
venv\Scripts\python -m pytest -q
```

Test coverage:
- Signup, login, protected route
- Admin RBAC
- Project ownership rules

## Notes
- Passlib requires `bcrypt==3.2.2` for compatibility.
- `python-jose` emits a `datetime.utcnow()` deprecation warning; it does not affect functionality.
