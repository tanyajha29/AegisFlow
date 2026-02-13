from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    PROJECT_NAME: str = "AegisFlow"

    # Environment
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_EXPIRY_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

settings = Settings()
