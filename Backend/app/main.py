from fastapi import FastAPI
from app.api.router import api_router
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.seed import seed_default_roles

app = FastAPI(title="AegisFlow API")

# Initialize DB tables on startup (non-blocking if DB unavailable)
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_default_roles(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

app.include_router(api_router)
