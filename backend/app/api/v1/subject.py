from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services.subject import SubjectService

router = APIRouter()

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(user_id: str, subject_in: SubjectCreate, db: Session = Depends(get_db)):
    return SubjectService.create_subject(db, user_id, subject_in)

@router.get("/", response_model=List[SubjectResponse])
def read_subjects(user_id: str, db: Session = Depends(get_db)):
    return SubjectService.get_subjects_by_user(db, user_id)

@router.get("/{subject_id}", response_model=SubjectResponse)
def read_subject(subject_id: int, user_id: str, db: Session = Depends(get_db)):
    subject = SubjectService.get_subject(db, subject_id, user_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return subject

@router.patch("/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, user_id: str, subject_in: SubjectUpdate, db: Session = Depends(get_db)):
    updated = SubjectService.update_subject(db, subject_id, user_id, subject_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")
    return updated

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, user_id: str, db: Session = Depends(get_db)):
    if not SubjectService.delete_subject(db, subject_id, user_id):
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")