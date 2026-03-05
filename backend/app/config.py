import os
from functools import lru_cache
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Dristi-Scan"
    environment: str = Field(default="development")
    database_url: str = Field(default="postgresql://admin:adminpassword@localhost:5432/drishtiscan")
    secret_key: str = Field(default="change-me")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    upload_dir: str = Field(default=os.path.join(os.getcwd(), "backend", "uploads"))
    max_upload_size_mb: int = Field(default=5)
    allowed_file_types: set[str] = Field(
        default_factory=lambda: {".py", ".js", ".java", ".php", ".txt", ".json", ".lock", ".md"}
    )
    cors_origins: list[str | AnyHttpUrl] = Field(default_factory=lambda: ["*"])
    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
