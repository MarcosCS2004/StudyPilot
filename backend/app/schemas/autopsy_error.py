from pydantic import BaseModel, ConfigDict
from typing import Optional

class AutopsyErrorCreate(BaseModel):
    autopsy_id: str
    pregunta_texto: Optional[str] = None
    respuesta_alumno: Optional[str] = None
    marca_profesor: Optional[str] = None
    tipo_fallo: Optional[str] = None
    nivel_impacto: Optional[str] = None
    causa_error: Optional[str] = None
    pregunta_refuerzo: Optional[str] = None

class AutopsyErrorUpdate(BaseModel):
    pregunta_texto: Optional[str] = None
    respuesta_alumno: Optional[str] = None
    marca_profesor: Optional[str] = None
    tipo_fallo: Optional[str] = None
    nivel_impacto: Optional[str] = None
    causa_error: Optional[str] = None
    pregunta_refuerzo: Optional[str] = None

class AutopsyErrorResponse(BaseModel):
    error_item_id: int
    autopsy_id: str
    pregunta_texto: Optional[str] = None
    respuesta_alumno: Optional[str] = None
    marca_profesor: Optional[str] = None
    tipo_fallo: Optional[str] = None
    nivel_impacto: Optional[str] = None
    causa_error: Optional[str] = None
    pregunta_refuerzo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AutopsyErrorListResponse(BaseModel):
    errores: list[AutopsyErrorResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
