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

class AutopsyErrorResponse(BaseModel):
    error_item_id: int
    pregunta_texto: str
    respuesta_alumno: str
    marca_profesor: str
    tipo_fallo: str
    causa_error: str
    
    model_config = ConfigDict(from_attributes=True)

class ExamAutopsyResponse(BaseModel):
    id: str
    user_id: str
    subject_id: int
    fecha_examen: Optional[datetime] = None
    analisis_status: Optional[str] = None
    exam_image_url: Optional[str] = None
    error_items: list[AutopsyErrorResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ExamAutopsyListResponse(BaseModel):
    examenes: list[ExamAutopsyResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
