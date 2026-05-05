from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ErrorHistoryCreate(BaseModel):
    user_id: str
    chunk_id: str
    tema: str
    asignatura: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_fallo: Optional[str] = None
    veces_fallado: Optional[int] = 0
    fecha_ultimo_fallo: Optional[datetime] = None

class ErrorHistoryUpdate(BaseModel):
    tema: Optional[str] = None
    asignatura: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_fallo: Optional[str] = None
    veces_fallado: Optional[int] = None
    fecha_ultimo_fallo: Optional[datetime] = None

class ErrorHistoryResponse(BaseModel):
    error_id: int
    user_id: str
    chunk_id: str
    tema: str
    asignatura: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_fallo: Optional[str] = None
    veces_fallado: int
    fecha_ultimo_fallo: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)