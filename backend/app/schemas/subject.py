from pydantic import BaseModel, ConfigDict
from typing import Optional

class SubjectCreate(BaseModel):
    nombre: str

class SubjectUpdate(BaseModel):
    nombre: Optional[str] = None

class SubjectResponse(BaseModel):
    id: int
    user_id: str
    nombre: str

    model_config = ConfigDict(from_attributes=True)