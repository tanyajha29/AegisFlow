from fastapi import APIRouter

try:
	from app.api.routes import auth
except Exception:
	auth = None

api_router = APIRouter()
if auth is not None and hasattr(auth, "router"):
	api_router.include_router(auth.router)
