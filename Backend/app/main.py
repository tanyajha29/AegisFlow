from fastapi import FastAPI
from app.api.router import api_router
from app.db.session import engine
from app.db.base import Base

app = FastAPI(title="AegisFlow API")

# Initialize DB tables on startup (non-blocking if DB unavailable)
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

app.include_router(api_router)
