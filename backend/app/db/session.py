"""
Sesión de base de datos SQLAlchemy.
Usa SQLite por defecto en desarrollo (no necesita servidor).
En producción, cambiar DATABASE_URL a PostgreSQL en el .env
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLite no necesita 'check_same_thread' en FastAPI con asyncio
connect_args = {}
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL or "sqlite:///./studypilot_dev.db",
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
