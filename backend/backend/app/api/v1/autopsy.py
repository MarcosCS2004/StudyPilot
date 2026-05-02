from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/autopsy", tags=["autopsy"])

@router.post("/analyze")
async def analyze_exam(exam_data: dict, db: Session = Depends(get_db)):
    """Analizar examen fallado y generar insights"""
    # TODO: Implementar analyzer.py
    pass

@router.get("/report/{exam_id}")
async def get_autopsy_report(exam_id: str, db: Session = Depends(get_db)):
    """Obtener reporte detallado del análisis"""
    pass
