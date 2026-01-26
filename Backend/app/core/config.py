from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration.
    All values come from environment variables.
    """

    # Application
    APP_NAME: str = "AegisFlow API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    APP_ENV: str = "development"

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    # Database
    DATABASE_URL: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton settings object
settings = Settings()
