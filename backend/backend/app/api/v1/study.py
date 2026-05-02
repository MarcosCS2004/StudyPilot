"""
GET  /api/v1/study/next-question   → NextQuestionResponse
POST /api/v1/study/answer          → AnswerResponse

TODO (backend): Reemplazar datos mock con:
  - next-question: algoritmo SM-2 (sm2_engine.py) + generación LLM de la pregunta
  - answer: evaluar respuesta, actualizar Performance en BD, generar explicación con LLM
"""
from fastapi import APIRouter
from app.schemas.api import NextQuestionResponse, QuestionOptions, AnswerPayload, AnswerResponse
import uuid
import random

router = APIRouter(prefix="/study", tags=["study"])


# ─── Banco de preguntas mock ──────────────────────────────────────────────────
# Simula lo que generaría el LLM basándose en los apuntes del alumno.

MOCK_QUESTIONS = [
    {
        "question_id": "q-deriv-001",
        "asignatura": "Matemáticas",
        "tema": "Derivadas",
        "enunciado": "¿Cuál es la derivada de f(x) = x³ + 2x² - 5x + 1?",
        "opciones": {
            "A": "3x² + 4x - 5",
            "B": "3x² + 2x - 5",
            "C": "x³ + 4x - 5",
            "D": "3x² + 4x + 1",
        },
        "respuesta_correcta": "A",
        "nivel_dificultad": 4,
        "explicacion": "Aplicando la regla de la potencia: d/dx(xⁿ) = n·xⁿ⁻¹. "
                       "Para x³ obtenemos 3x², para 2x² obtenemos 4x, y para -5x obtenemos -5. "
                       "La constante 1 desaparece al derivar.",
    },
    {
        "question_id": "q-integ-001",
        "asignatura": "Matemáticas",
        "tema": "Integrales",
        "enunciado": "¿Cuál es el resultado de ∫ 2x dx?",
        "opciones": {
            "A": "2x + C",
            "B": "x² + C",
            "C": "2x² + C",
            "D": "x + C",
        },
        "respuesta_correcta": "B",
        "nivel_dificultad": 3,
        "explicacion": "La integral de 2x se calcula como: ∫2x dx = 2·(x²/2) + C = x² + C. "
                       "Recuerda que la constante de integración C siempre debe añadirse.",
    },
    {
        "question_id": "q-cine-001",
        "asignatura": "Física",
        "tema": "Cinemática",
        "enunciado": "Un coche viaja a 72 km/h. ¿Cuál es su velocidad en m/s?",
        "opciones": {
            "A": "72 m/s",
            "B": "20 m/s",
            "C": "25 m/s",
            "D": "18 m/s",
        },
        "respuesta_correcta": "B",
        "nivel_dificultad": 2,
        "explicacion": "Para convertir km/h a m/s, dividimos entre 3.6. "
                       "72 km/h ÷ 3.6 = 20 m/s. "
                       "Alternativamente: 72 × (1000m/3600s) = 20 m/s.",
    },
    {
        "question_id": "q-dinam-001",
        "asignatura": "Física",
        "tema": "Dinámica",
        "enunciado": "Según la Segunda Ley de Newton, si aplicamos una fuerza de 10 N a un objeto de 2 kg, ¿cuál es su aceleración?",
        "opciones": {
            "A": "20 m/s²",
            "B": "0.2 m/s²",
            "C": "5 m/s²",
            "D": "12 m/s²",
        },
        "respuesta_correcta": "C",
        "nivel_dificultad": 3,
        "explicacion": "La Segunda Ley de Newton establece F = m·a, por lo tanto a = F/m. "
                       "Sustituyendo: a = 10 N / 2 kg = 5 m/s².",
    },
    {
        "question_id": "q-alq-001",
        "asignatura": "Química Orgánica",
        "tema": "Alquenos",
        "enunciado": "¿Cuál es el nombre del alqueno con fórmula molecular C₃H₆?",
        "opciones": {
            "A": "Propano",
            "B": "Propino",
            "C": "Propeno",
            "D": "Buteno",
        },
        "respuesta_correcta": "C",
        "nivel_dificultad": 3,
        "explicacion": "Los alquenos tienen la fórmula general CₙH₂ₙ. Con n=3, la fórmula es C₃H₆. "
                       "El prefijo 'prop-' indica 3 carbonos y el sufijo '-eno' indica doble enlace. "
                       "El nombre correcto es propeno (también llamado propileno).",
    },
]

# Índice rotativo para simular progresión (en producción sería SM-2)
_question_index = 0


@router.get("/next-question", response_model=NextQuestionResponse)
async def get_next_question(asignatura_id: str | None = None):
    """
    Devuelve la siguiente pregunta adaptativa.
    Si se pasa asignatura_id, filtra por asignatura.
    TODO: Implementar algoritmo SM-2 real con sm2_engine.py
    """
    global _question_index

    pool = MOCK_QUESTIONS
    if asignatura_id:
        # Mapeo simple: el asignatura_id del dashboard apunta a estos nombres
        asig_map = {
            "mate-101": "Matemáticas",
            "fis-101": "Física",
            "quim-101": "Química Orgánica",
        }
        nombre = asig_map.get(asignatura_id)
        if nombre:
            pool = [q for q in MOCK_QUESTIONS if q["asignatura"] == nombre]
        if not pool:
            pool = MOCK_QUESTIONS

    q = pool[_question_index % len(pool)]
    _question_index += 1

    return NextQuestionResponse(
        question_id=q["question_id"],
        asignatura=q["asignatura"],
        tema=q["tema"],
        enunciado=q["enunciado"],
        opciones=QuestionOptions(**q["opciones"]),
        nivel_dificultad=q["nivel_dificultad"],
    )


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(payload: AnswerPayload):
    """
    Evalúa la respuesta del alumno y devuelve feedback.
    TODO: 
      - Persistir resultado en tabla performance (BD)
      - Actualizar nivel SM-2 del tema
      - Generar explicación con LLM (openai/azure)
    """
    # Buscar la pregunta por ID
    question = next(
        (q for q in MOCK_QUESTIONS if q["question_id"] == payload.question_id),
        MOCK_QUESTIONS[0],
    )

    correcto = payload.respuesta == question["respuesta_correcta"]
    xp = 30 if correcto else 5  # XP base; en producción depende del nivel SM-2

    return AnswerResponse(
        correcto=correcto,
        respuesta_correcta=question["respuesta_correcta"],
        explicacion=question["explicacion"],
        nuevo_nivel_tema=question["nivel_dificultad"] + (1 if correcto else 0),
        xp_ganado=xp,
    )
