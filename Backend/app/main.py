from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.router import api_router
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.seed import seed_default_roles

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_default_roles(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
    yield

app = FastAPI(title="AegisFlow API", lifespan=lifespan)
app.include_router(api_router)
