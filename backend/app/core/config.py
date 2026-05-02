"""
Configuración de la aplicación con pydantic-settings.
Todas las variables son opcionales para permitir arrancar el backend
en modo mock/desarrollo sin necesitar BD, Redis ni servicios cloud.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "StudyPilot"
    API_V1_STR: str = "/api/v1"

    # Database – opcional en modo mock
    DATABASE_URL: Optional[str] = "sqlite:///./studypilot_dev.db"
    REDIS_URL: Optional[str] = "redis://localhost:6379"

    # Azure – opcional en modo mock
    AZURE_ENDPOINT: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    AZURE_STORAGE_KEY: Optional[str] = None

    # AI Services – opcional en modo mock
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Vector Store
    QDRANT_URL: str = "http://localhost:6333"
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64

    class Config:
        env_file = ".env"
        extra = "ignore"  # ignora variables extras del .env


settings = Settings()
