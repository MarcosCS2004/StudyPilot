from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class StudentProfileCreate(BaseModel):
    user_id: str
    tema: Optional[str] = None
    nivel_tema: Optional[int] = 1
    intervalo_sm2: Optional[int] = 1
    facilidad_sm2: Optional[float] = 2.5
    ultima_revision: Optional[datetime] = None

class StudentProfileUpdate(BaseModel):
    tema: Optional[str] = None
    nivel_tema: Optional[int] = None
    intervalo_sm2: Optional[int] = None
    facilidad_sm2: Optional[float] = None
    ultima_revision: Optional[datetime] = None

class StudentProfileResponse(BaseModel):
    id: int
    user_id: str
    tema: Optional[str] = None
    nivel_tema: int
    intervalo_sm2: int
    facilidad_sm2: float
    ultima_revision: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
