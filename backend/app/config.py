from functools import lru_cache
from pathlib import Path
from pydantic import Field, AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent


def _default_upload_dir() -> str:
    return str(BACKEND_DIR / "uploads")


def _default_rag_kb_path() -> str:
    return str(BACKEND_DIR / "app" / "rag" / "kb")


def _default_report_logo_path() -> str:
    candidates = [
        BACKEND_DIR / "app" / "assets" / "dristiscan-logo.png",
        REPO_DIR / "docs" / "screens" / "logo.png",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(candidates[0])


class Settings(BaseSettings):
    project_name: str = "Dristi-Scan"
    environment: str = Field(default="development")
    database_url: str = Field(default="postgresql://admin:adminpassword@localhost:5432/drishtiscan")
    secret_key: str = Field(default="change-me")
    jwt_secret_key: str | None = Field(default=None, description="Optional alias for SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    upload_dir: str = Field(default_factory=_default_upload_dir)
    max_upload_size_mb: int = Field(default=5)
    allowed_file_types: set[str] = Field(
        default_factory=lambda: {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".php",
            ".go",
            ".rb",
            ".c",
            ".cpp",
            ".txt",
            ".json",
            ".lock",
            ".md",
        }
    )
    cors_origins: list[str | AnyHttpUrl] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = Field(default=False, description="Allow credentialed CORS requests")
    log_level: str = Field(default="INFO")
    github_token: str | None = Field(default=None, description="GitHub token for repository scanning")
    ollama_url: AnyHttpUrl | str = Field(default="http://localhost:11434", description="Ollama base URL (legacy)")
    ollama_model: str = Field(default="deepseek-coder", description="Ollama model (legacy fallback)")
    ollama_timeout_seconds: float = Field(default=120.0, description="Ollama timeout (legacy)")
    # OpenRouter / unified LLM config
    llm_provider: str = Field(default="openrouter", description="LLM provider: openrouter | ollama")
    llm_model: str = Field(default="openrouter/auto", description="LLM model identifier")
    llm_timeout_seconds: float = Field(default=120.0, description="LLM request timeout")
    llm_temperature: float = Field(default=0.0, description="LLM sampling temperature")
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter base URL")
    openrouter_site_url: str = Field(default="http://localhost:5173", description="Sent as HTTP-Referer")
    openrouter_site_name: str = Field(default="DristiScan", description="Sent as X-Title")
    fernet_key: str | None = Field(default=None, description="Fernet key for encrypting MFA secrets")
    report_logo_path: str = Field(default_factory=_default_report_logo_path, description="Path to the DristiScan logo used in PDF reports")
    rag_debug: bool = Field(default=False, description="Enable verbose RAG debug logging")
    prewarm_embeddings_on_startup: bool = Field(default=False, description="Warm the embedding model during startup")
    ai_injection_enabled: bool = Field(default=False, description="Enable Injection Agent (Phase 2)")
    ai_secrets_enabled: bool = Field(default=False, description="Enable Secrets Agent (Phase 3)")
    ai_auth_enabled: bool = Field(default=False, description="Enable Auth Agent (Phase 4)")
    ai_dependency_enabled: bool = Field(default=False, description="Enable Dependency Agent (Phase 5)")
    ai_planner_enabled: bool = Field(default=False, description="Enable Planner Agent (Phase 6)")
    ai_report_enabled: bool = Field(default=True, description="Enable Report Agent (Phase 9)")
    rag_kb_path: str = Field(default_factory=_default_rag_kb_path)
    rag_top_k: int = Field(default=5, description="Top-k KB chunks to retrieve for RAG explanations")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Allow CORS_ORIGINS to be provided as:
        - comma-separated string
        - single '*' string
        - JSON-like list string
        """
        if v is None:
            return ["*"]
        if isinstance(v, str):
            raw = v.strip()
            if raw == "*":
                return ["*"]
            if raw.startswith("[") and raw.endswith("]"):
                # try to parse simple list strings: ["a","b"]
                try:
                    import json

                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            return [item.strip() for item in raw.split(",") if item.strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # allow JWT_SECRET_KEY alias
    if settings.jwt_secret_key and settings.secret_key == "change-me":
        settings.secret_key = settings.jwt_secret_key
    return settings
