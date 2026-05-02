"""
StudyPilot – Pydantic Schemas
Espeja exactamente los tipos de frontend/src/types/api.ts
"""
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


# ─── Profile & Progress ───────────────────────────────────────────────────────

class TopicLevel(BaseModel):
    nombre_tema: str
    nivel: int          # 1–10
    pct_acierto: float  # 0–100

class SubjectProgress(BaseModel):
    asignatura_id: str
    nombre_asignatura: str
    temas: list[TopicLevel]

class ProfileProgressResponse(BaseModel):
    alumno_id: str
    nombre: str
    racha_dias: int
    xp_total: int
    asignaturas: list[SubjectProgress]


# ─── Study Session ────────────────────────────────────────────────────────────

class QuestionOptions(BaseModel):
    A: str
    B: str
    C: str
    D: str

class NextQuestionResponse(BaseModel):
    question_id: str
    asignatura: str
    tema: str
    enunciado: str
    opciones: QuestionOptions
    nivel_dificultad: int  # 1–10

class AnswerPayload(BaseModel):
    question_id: str
    respuesta: Literal["A", "B", "C", "D"]

class AnswerResponse(BaseModel):
    correcto: bool
    respuesta_correcta: Literal["A", "B", "C", "D"]
    explicacion: str
    nuevo_nivel_tema: int
    xp_ganado: int
    siguiente_question_id: Optional[str] = None


# ─── Document Upload ──────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    file_id: str
    status: str   # "idle" | "uploading" | "processing" | "done" | "error"
    mensaje: str


# ─── Exam Autopsy ─────────────────────────────────────────────────────────────

FaultType = Literal["confusion", "laguna", "parcial"]

class ErrorItem(BaseModel):
    item_id: str
    pregunta_original: str
    respuesta_alumno: str
    respuesta_correcta: str
    tipo_fallo: FaultType
    causa_error: str
    chunk_source: str   # Fragmento literal de los apuntes relacionado
    asignatura: str
    tema: str

class ExamAutopsyResponse(BaseModel):
    autopsy_id: str
    nombre_examen: str
    fecha_analisis: str  # ISO datetime string
    error_items: list[ErrorItem]
    sesion_refuerzo_id: str
    resumen: str
