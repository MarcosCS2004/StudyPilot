from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StudyPilot"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str
    
    # Azure
    AZURE_ENDPOINT: str
    AZURE_API_KEY: str
    AZURE_STORAGE_ACCOUNT: str
    AZURE_STORAGE_KEY: str
    
    # AI Services
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Vector Store
    QDRANT_URL: str = "http://localhost:6333"
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 64
    
    class Config:
        env_file = ".env"

settings = Settings()
