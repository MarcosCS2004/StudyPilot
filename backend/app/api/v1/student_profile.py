from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.student_profile import StudentProfileCreate, StudentProfileResponse, StudentProfileUpdate
from app.services.student_profile import StudentProfileService

router = APIRouter(tags=["Student Profile"])

# --- CREATE ---
@router.post("/", response_model=StudentProfileResponse, status_code=201)
def create_student_profile(
    profile_data: StudentProfileCreate,
    db: Session = Depends(get_db)
):
    try:
        return StudentProfileService.create_student_profile(db, profile_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- READ ---
@router.get("/{profile_id}", response_model=StudentProfileResponse)
def get_student_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un perfil de estudiante por su ID."""
    profile = StudentProfileService.get_student_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile

@router.get("/user/{user_id}", response_model=StudentProfileResponse)
def get_student_profile_by_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Obtiene el perfil de estudiante de un usuario."""
    profile = StudentProfileService.get_student_profile_by_user(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="El usuario no tiene perfil asignado")
    return profile

# --- UPDATE ---
@router.put("/{profile_id}", response_model=StudentProfileResponse)
def update_student_profile(
    profile_id: int,
    update_data: StudentProfileUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un perfil de estudiante."""
    profile = StudentProfileService.update_student_profile(db, profile_id, update_data)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile

@router.put("/user/{user_id}", response_model=StudentProfileResponse)
def update_student_profile_by_user(
    user_id: str,
    update_data: StudentProfileUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza el perfil de estudiante de un usuario."""
    profile = StudentProfileService.update_student_profile_by_user(db, user_id, update_data)
    if not profile:
        raise HTTPException(status_code=404, detail="El usuario no tiene perfil asignado")
    return profile

@router.patch("/user/{user_id}/tema", response_model=StudentProfileResponse)
def update_user_tema(
    user_id: str,
    tema: str,
    nivel: int = 1,
    db: Session = Depends(get_db)
):
    """Actualiza el tema y nivel del perfil de un usuario."""
    profile = StudentProfileService.update_tema_and_nivel(db, user_id, tema, nivel)
    if not profile:
        raise HTTPException(status_code=404, detail="El usuario no tiene perfil asignado")
    return profile

@router.patch("/user/{user_id}/sm2", response_model=StudentProfileResponse)
def update_user_sm2(
    user_id: str,
    intervalo: int,
    facilidad: float,
    db: Session = Depends(get_db)
):
    """Actualiza los valores del algoritmo SM2 del perfil de un usuario."""
    from datetime import datetime
    profile = StudentProfileService.update_sm2_values(db, user_id, intervalo, facilidad, datetime.now())
    if not profile:
        raise HTTPException(status_code=404, detail="El usuario no tiene perfil asignado")
    return profile

# --- DELETE ---
@router.delete("/{profile_id}", status_code=204)
def delete_student_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un perfil de estudiante."""
    success = StudentProfileService.delete_student_profile(db, profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return None

@router.delete("/user/{user_id}", status_code=204)
def delete_student_profile_by_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Elimina el perfil de estudiante de un usuario."""
    success = StudentProfileService.delete_student_profile_by_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="El usuario no tiene perfil asignado")
    return None
