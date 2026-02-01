from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "AegisFlow"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Security
    JWT_SECRET: str
    JWT_EXPIRY_MINUTES: int = 60

    # Database
    DATABASE_URL: str

    # CORS
    CORS_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"
        extra = "forbid"

settings = Settings()
