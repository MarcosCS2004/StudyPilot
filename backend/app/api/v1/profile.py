"""
GET /api/v1/profile/progress
Devuelve progreso del alumno: racha, XP y asignaturas con temas.

TODO (backend): Reemplazar los datos mock por consultas reales a:
  - tabla users  → nombre, xp_total, racha_dias
  - tabla performance → nivel y pct_acierto por topic
"""
from fastapi import APIRouter
from app.schemas.api import ProfileProgressResponse, SubjectProgress, TopicLevel
import uuid

router = APIRouter(prefix="/profile", tags=["profile"])


# ─── Datos mock ──────────────────────────────────────────────────────────────
# Representa un alumno de ejemplo con dos asignaturas y varios temas.
# Reemplazar con lógica real cuando la BD esté disponible.

MOCK_PROFILE = ProfileProgressResponse(
    alumno_id="alumno-001",
    nombre="Carlos García",
    racha_dias=5,
    xp_total=1240,
    asignaturas=[
        SubjectProgress(
            asignatura_id="mate-101",
            nombre_asignatura="Matemáticas",
            temas=[
                TopicLevel(nombre_tema="Derivadas", nivel=7, pct_acierto=82.0),
                TopicLevel(nombre_tema="Integrales", nivel=4, pct_acierto=55.0),
                TopicLevel(nombre_tema="Límites", nivel=8, pct_acierto=90.0),
            ],
        ),
        SubjectProgress(
            asignatura_id="fis-101",
            nombre_asignatura="Física",
            temas=[
                TopicLevel(nombre_tema="Cinemática", nivel=6, pct_acierto=70.0),
                TopicLevel(nombre_tema="Dinámica", nivel=3, pct_acierto=42.0),
                TopicLevel(nombre_tema="Termodinámica", nivel=5, pct_acierto=60.0),
            ],
        ),
        SubjectProgress(
            asignatura_id="quim-101",
            nombre_asignatura="Química Orgánica",
            temas=[
                TopicLevel(nombre_tema="Alquenos", nivel=9, pct_acierto=94.0),
                TopicLevel(nombre_tema="Alcoholes", nivel=2, pct_acierto=30.0),
            ],
        ),
    ],
)


@router.get("/progress", response_model=ProfileProgressResponse)
async def get_progress():
    """Devuelve el progreso completo del alumno para el Dashboard."""
    return MOCK_PROFILE
