from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Dashboard del usuario con estadísticas"""
    pass

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Estadísticas detalladas de rendimiento"""
    pass
