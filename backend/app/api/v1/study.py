from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/study", tags=["study"])

@router.get("/next-question")
async def get_next_question(db: Session = Depends(get_db)):
    """Obtener siguiente pregunta adaptativa usando SM-2"""
    # TODO: Implementar sm2_engine.py
    pass

@router.post("/submit-answer")
async def submit_answer(answer: dict, db: Session = Depends(get_db)):
    """Enviar respuesta y actualizar progreso"""
    pass

@router.get("/progress")
async def get_progress(db: Session = Depends(get_db)):
    """Ver progreso del estudiante"""
    pass
