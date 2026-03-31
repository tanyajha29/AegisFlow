from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, scan, report

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Drishti-Scan API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(report.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Drishti-Scan API"}

