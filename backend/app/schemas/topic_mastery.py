from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TopicMasteryBase(BaseModel):
    asignatura: str
    tema: str
    nivel: int = 1
    pct_acierto: float = 0.0
    total_intentos: int = 0
    aciertos: int = 0
    intervalo_sm2: int = 1
    facilidad_sm2: float = 2.5
    repeticion_num: int = 0
    ultima_revision: Optional[datetime] = None
    proxima_revision: Optional[datetime] = None

class TopicMasteryCreate(TopicMasteryBase):
    user_id: str

class TopicMasteryUpdate(BaseModel):
    nivel: Optional[int] = None
    pct_acierto: Optional[float] = None
    total_intentos: Optional[int] = None
    aciertos: Optional[int] = None
    intervalo_sm2: Optional[int] = None
    facilidad_sm2: Optional[float] = None
    repeticion_num: Optional[int] = None
    ultima_revision: Optional[datetime] = None
    proxima_revision: Optional[datetime] = None

class TopicMasteryResponse(TopicMasteryBase):
    id: int
    user_id: str

    model_config = ConfigDict(from_attributes=True)
