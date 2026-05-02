from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DocumentCreate(BaseModel):
    user_id: str
    subject_id: int
    nombre_original: str
    blob_url: Optional[str] = None

class DocumentUpdate(BaseModel):
    nombre_original: Optional[str] = None
    blob_url: Optional[str] = None
    status: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    subject_id: int
    nombre_original: str
    blob_url: Optional[str] = None
    status: str
    fecha_subida: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListResponse(BaseModel):
    documentos: list[DocumentResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
