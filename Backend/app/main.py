from fastapi import FastAPI
from app.api.routes.router import api_router
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AegisFlow Backend")

app.include_router(api_router, prefix="/api")
