from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.error_history import ErrorHistoryCreate, ErrorHistoryResponse, ErrorHistoryUpdate
from app.services.error_history import ErrorHistoryService

router = APIRouter(tags=["Error History"])

@router.post("/", response_model=ErrorHistoryResponse, status_code=201)
def create_error(data: ErrorHistoryCreate, db: Session = Depends(get_db)):
    """Crea un nuevo registro de error."""
    try:
        return ErrorHistoryService.create(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{error_id}", response_model=ErrorHistoryResponse)
def get_error(error_id: int, db: Session = Depends(get_db)):
    """Obtiene un error por su ID."""
    record = ErrorHistoryService.get_by_id(db, error_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record

@router.get("/user/{user_id}", response_model=list[ErrorHistoryResponse])
def get_errors_by_user(user_id: str, db: Session = Depends(get_db)):
    """Obtiene todos los errores de un usuario."""
    return ErrorHistoryService.get_by_user(db, user_id)

@router.post("/user/{user_id}/chunk/{chunk_id}/fallo", response_model=ErrorHistoryResponse)
def increment_fallo(user_id: str, chunk_id: str, db: Session = Depends(get_db)):
    """Registra un fallo en un chunk. Crea el registro si no existe."""
    try:
        return ErrorHistoryService.increment_fallo(db, user_id, chunk_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{error_id}", response_model=ErrorHistoryResponse)
def update_error(error_id: int, data: ErrorHistoryUpdate, db: Session = Depends(get_db)):
    """Actualiza un registro de error."""
    try:
        record = ErrorHistoryService.update(db, error_id, data)
        if not record:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{error_id}", status_code=204)
def delete_error(error_id: int, db: Session = Depends(get_db)):
    """Elimina un registro de error."""
    success = ErrorHistoryService.delete(db, error_id)
    if not success:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return None

@router.delete("/user/{user_id}", status_code=204)
def delete_errors_by_user(user_id: str, db: Session = Depends(get_db)):
    """Elimina todos los errores de un usuario."""
    success = ErrorHistoryService.delete_by_user(db, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error al eliminar los registros")
    return None
    try:
        if not ErrorHistoryService.delete(db, error_id):
            raise HTTPException(status_code=404, detail="Registro no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))