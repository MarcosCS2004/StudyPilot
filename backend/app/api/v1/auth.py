"""
POST /api/v1/auth/login → Devuelve un access_token

Módulo mock de autenticación para que el frontend pueda iniciar sesión.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login. Acepta cualquier usuario y contraseña para pruebas.
    Devuelve un token JWT simulado.
    """
    # En producción aquí se validaría la contraseña contra la BD
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña requeridos")

    return Token(
        access_token="mock-jwt-token-12345",
        token_type="bearer",
        user_name=form_data.username.split("@")[0].capitalize()
    )
