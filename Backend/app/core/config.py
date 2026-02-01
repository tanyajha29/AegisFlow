from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AegisFlow"
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
