import os
from functools import lru_cache
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Dristi-Scan"
    environment: str = Field(default="development")
    database_url: str = Field(default="postgresql://admin:adminpassword@localhost:5432/drishtiscan")
    secret_key: str = Field(default="change-me")
    jwt_secret_key: str | None = Field(default=None, description="Optional alias for SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    upload_dir: str = Field(default=os.path.join(os.getcwd(), "backend", "uploads"))
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
    log_level: str = Field(default="INFO")
    github_token: str | None = Field(default=None, description="GitHub token for repository scanning")
    ollama_url: AnyHttpUrl | str = Field(default="http://localhost:11434", description="Ollama base URL")
    ollama_model: str = Field(default="deepseek-coder", description="Default Ollama model for AI agents")
    ollama_timeout_seconds: float = Field(default=15.0, description="HTTP timeout for Ollama calls")
    ai_injection_enabled: bool = Field(default=False, description="Enable Injection Agent (Phase 2)")
    ai_secrets_enabled: bool = Field(default=False, description="Enable Secrets Agent (Phase 3)")
    ai_auth_enabled: bool = Field(default=False, description="Enable Auth Agent (Phase 4)")
    ai_dependency_enabled: bool = Field(default=False, description="Enable Dependency Agent (Phase 5)")
    ai_planner_enabled: bool = Field(default=False, description="Enable Planner Agent (Phase 6)")
    ai_report_enabled: bool = Field(default=True, description="Enable Report Agent (Phase 9)")
    rag_kb_path: str = Field(default=os.path.join(os.getcwd(), "backend", "app", "rag", "kb"))
    rag_top_k: int = Field(default=5, description="Top-k KB chunks to retrieve for RAG explanations")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # allow JWT_SECRET_KEY alias
    if settings.jwt_secret_key and settings.secret_key == "change-me":
        settings.secret_key = settings.jwt_secret_key
    return settings
