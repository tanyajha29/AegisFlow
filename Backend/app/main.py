from fastapi import FastAPI
from app.api.routes.router import api_router

# Defer SQLAlchemy imports to avoid startup errors on Python 3.13
# (DB setup should be done in a separate management command or when
# running with a compatible Python/SQLAlchemy version)

app = FastAPI(title="AegisFlow Backend")

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
	return {"status": "ok"}
