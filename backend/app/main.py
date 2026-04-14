import logging
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .config import get_settings
from .database import Base, engine
from .models import user_model, scan_model, vulnerability_model  # ensure models are registered
from .routes import auth_routes, scan_routes, report_routes, rag_routes
from .utils.rate_limiter import rate_limiter


settings = get_settings()
cors_origins = set(settings.cors_origins or [])
# Ensure deployed frontend + current tunnel are allowed
cors_origins.update(
    {
        "https://drishti-scan.vercel.app",
        "https://grades-watershed-navigator-revisions.trycloudflare.com",
    }
)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("dristi-scan")

app = FastAPI(title=settings.project_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")
    # Pre-warm the sentence transformer so the first RAG request isn't blocked
    # by a model download. This runs once at startup inside the container.
    try:
        from .rag.retriever_service import _get_model
        _get_model()
        logger.info("SentenceTransformer pre-warmed successfully")
    except Exception as exc:
        logger.warning("SentenceTransformer pre-warm failed (non-fatal): %s", exc)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Request: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Response status: %s", response.status_code)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth_routes.router, dependencies=[Depends(rate_limiter)])
app.include_router(scan_routes.router, dependencies=[Depends(rate_limiter)])
app.include_router(report_routes.router, dependencies=[Depends(rate_limiter)])
app.include_router(report_routes.router, prefix="/api", dependencies=[Depends(rate_limiter)])
app.include_router(rag_routes.router, dependencies=[Depends(rate_limiter)])


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
