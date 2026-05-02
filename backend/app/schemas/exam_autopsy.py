from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ExamAutopsyCreate(BaseModel):
    user_id: str
    subject_id: int
    fecha_examen: Optional[datetime] = None
    analisis_status: Optional[str] = None

class ExamAutopsyUpdate(BaseModel):
    fecha_examen: Optional[datetime] = None
    analisis_status: Optional[str] = None

class ExamAutopsyResponse(BaseModel):
    id: str
    user_id: str
    subject_id: int
    fecha_examen: Optional[datetime] = None
    analisis_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ExamAutopsyListResponse(BaseModel):
    examenes: list[ExamAutopsyResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
