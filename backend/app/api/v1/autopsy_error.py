from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.autopsy_error import AutopsyErrorCreate, AutopsyErrorResponse, AutopsyErrorUpdate, AutopsyErrorListResponse
from app.services.autopsy_error import AutopsyErrorService

router = APIRouter(tags=["Autopsy Errors"])

@router.post("/", response_model=AutopsyErrorResponse, status_code=201)
def create_autopsy_error(data: AutopsyErrorCreate, db: Session = Depends(get_db)):
    """Crea un nuevo error de autopsia."""
    try:
        return AutopsyErrorService.create(db, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{error_item_id}", response_model=AutopsyErrorResponse)
def get_autopsy_error(error_item_id: int, db: Session = Depends(get_db)):
    """Obtiene un error de autopsia por su ID."""
    record = AutopsyErrorService.get_by_id(db, error_item_id)
    if not record:
        raise HTTPException(status_code=404, detail="Error no encontrado")
    return record

@router.get("/autopsy/{autopsy_id}", response_model=AutopsyErrorListResponse)
def get_autopsy_errors(autopsy_id: str, db: Session = Depends(get_db)):
    """Obtiene todos los errores de una autopsia."""
    errors = AutopsyErrorService.get_by_autopsy(db, autopsy_id)
    total = AutopsyErrorService.count_by_autopsy(db, autopsy_id)
    return AutopsyErrorListResponse(errores=errors, total=total)

@router.get("/autopsy/{autopsy_id}/tipo/{tipo_fallo}", response_model=list[AutopsyErrorResponse])
def get_autopsy_errors_by_tipo(autopsy_id: str, tipo_fallo: str, db: Session = Depends(get_db)):
    """Obtiene errores de una autopsia filtrados por tipo de fallo."""
    errors = AutopsyErrorService.get_by_autopsy(db, autopsy_id)
    return [e for e in errors if e.tipo_fallo == tipo_fallo]

@router.get("/autopsy/{autopsy_id}/impacto/{nivel_impacto}", response_model=list[AutopsyErrorResponse])
def get_autopsy_errors_by_impacto(autopsy_id: str, nivel_impacto: str, db: Session = Depends(get_db)):
    """Obtiene errores de una autopsia filtrados por nivel de impacto."""
    return AutopsyErrorService.get_by_nivel_impacto(db, autopsy_id, nivel_impacto)

@router.put("/{error_item_id}", response_model=AutopsyErrorResponse)
def update_autopsy_error(error_item_id: int, data: AutopsyErrorUpdate, db: Session = Depends(get_db)):
    """Actualiza un error de autopsia."""
    try:
        record = AutopsyErrorService.update(db, error_item_id, data)
        if not record:
            raise HTTPException(status_code=404, detail="Error no encontrado")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{error_item_id}", status_code=204)
def delete_autopsy_error(error_item_id: int, db: Session = Depends(get_db)):
    """Elimina un error de autopsia."""
    success = AutopsyErrorService.delete(db, error_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Error no encontrado")
    return None

@router.delete("/autopsy/{autopsy_id}", status_code=204)
def delete_autopsy_errors(autopsy_id: str, db: Session = Depends(get_db)):
    """Elimina todos los errores de una autopsia."""
    success = AutopsyErrorService.delete_by_autopsy(db, autopsy_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error al eliminar los registros")
    return None
