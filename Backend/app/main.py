from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# Initialize logging as early as possible
setup_logging()

def create_application() -> FastAPI:
    """
    Application factory.
    Allows clean startup, testing, and future scalability.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # CORS configuration (frontend integration)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()


@app.get("/health", tags=["health"])
def health_check():
    """
    Liveness probe.
    Confirms the service is running.
    """
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
def readiness_check():
    """
    Readiness probe.
    Confirms the service is ready to accept traffic.
    DB connectivity will be added later.
    """
    return {"status": "ready"}
