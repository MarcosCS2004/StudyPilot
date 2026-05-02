from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.exam_autopsy import ExamAutopsyCreate, ExamAutopsyResponse, ExamAutopsyUpdate, ExamAutopsyListResponse
from app.services.exam_autopsy import ExamAutopsyService

router = APIRouter(tags=["Exam Autopsy"])

@router.post("/", response_model=ExamAutopsyResponse, status_code=201)
def create_exam_autopsy(data: ExamAutopsyCreate, db: Session = Depends(get_db)):
    """Crea una nueva autopsia de examen."""
    try:
        return ExamAutopsyService.create(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{autopsy_id}", response_model=ExamAutopsyResponse)
def get_exam_autopsy(autopsy_id: str, db: Session = Depends(get_db)):
    """Obtiene una autopsia de examen por su ID."""
    record = ExamAutopsyService.get_by_id(db, autopsy_id)
    if not record:
        raise HTTPException(status_code=404, detail="Autopsia no encontrada")
    return record

@router.get("/user/{user_id}", response_model=ExamAutopsyListResponse)
def get_user_autopsies(user_id: str, db: Session = Depends(get_db)):
    """Obtiene todas las autopsias de un usuario."""
    autopsies = ExamAutopsyService.get_by_user(db, user_id)
    total = ExamAutopsyService.count_by_user(db, user_id)
    return ExamAutopsyListResponse(examenes=autopsies, total=total)

@router.get("/subject/{subject_id}", response_model=ExamAutopsyListResponse)
def get_subject_autopsies(subject_id: int, db: Session = Depends(get_db)):
    """Obtiene todas las autopsias de una asignatura."""
    autopsies = ExamAutopsyService.get_by_subject(db, subject_id)
    total = ExamAutopsyService.count_by_subject(db, subject_id)
    return ExamAutopsyListResponse(examenes=autopsies, total=total)

@router.get("/user/{user_id}/subject/{subject_id}", response_model=list[ExamAutopsyResponse])
def get_user_subject_autopsies(user_id: str, subject_id: int, db: Session = Depends(get_db)):
    """Obtiene autopsias de un usuario para una asignatura específica."""
    return ExamAutopsyService.get_by_user_and_subject(db, user_id, subject_id)

@router.get("/estado/{estado}", response_model=list[ExamAutopsyResponse])
def get_autopsies_by_estado(estado: str, db: Session = Depends(get_db)):
    """Obtiene autopsias filtradas por estado (pendiente, completada, etc)."""
    return ExamAutopsyService.get_by_estado(db, estado)

@router.put("/{autopsy_id}", response_model=ExamAutopsyResponse)
def update_exam_autopsy(autopsy_id: str, data: ExamAutopsyUpdate, db: Session = Depends(get_db)):
    """Actualiza una autopsia de examen."""
    try:
        record = ExamAutopsyService.update(db, autopsy_id, data)
        if not record:
            raise HTTPException(status_code=404, detail="Autopsia no encontrada")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{autopsy_id}/estado", response_model=ExamAutopsyResponse)
def update_autopsy_estado(autopsy_id: str, estado: str, db: Session = Depends(get_db)):
    """Actualiza solo el estado de una autopsia."""
    valid_estados = ["pendiente", "procesando", "completada", "error"]
    if estado not in valid_estados:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Estados válidos: {', '.join(valid_estados)}"
        )
    
    record = ExamAutopsyService.update_estado(db, autopsy_id, estado)
    if not record:
        raise HTTPException(status_code=404, detail="Autopsia no encontrada")
    return record
def delete_exam_autopsy(autopsy_id: str, db: Session = Depends(get_db)):
    """Elimina una autopsia de examen."""
    success = ExamAutopsyService.delete(db, autopsy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Autopsia no encontrada")
    return None

@router.delete("/user/{user_id}", status_code=204)
def delete_user_autopsies(user_id: str, db: Session = Depends(get_db)):
    """Elimina todas las autopsias de un usuario."""
    success = ExamAutopsyService.delete_by_user(db, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error al eliminar las autopsias")
    return None
