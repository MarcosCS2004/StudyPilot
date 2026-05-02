from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()

# --- CREATE ---
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = UserService.create_user(db, user_in)
    if not user:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    return user

# --- READ (Todos los usuarios) ---
@router.get("/", response_model=List[UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return UserService.get_users(db, skip=skip, limit=limit)

# --- READ (Un usuario por ID) ---
# Nota: Usamos str porque tu ID ahora es un UUID de SQL Server
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user

# --- UPDATE ---
@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_in: UserUpdate, db: Session = Depends(get_db)):
    # exclude_unset=True evita que enviemos datos "None" al servicio si el usuario no los mandó
    update_data = user_in.model_dump(exclude_unset=True) 
    user = UserService.update_user(db, user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user

# --- DELETE ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")