from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
# Lo que recibimos al actualizar (campos opcionales)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    racha_dias: Optional[int] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    racha_dias: int
    created_at: datetime
    ultimo_acceso: Optional[datetime] = None

    # Esto le dice a Pydantic que lea los datos del objeto de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)