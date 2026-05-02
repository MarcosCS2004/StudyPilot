"""
POST /api/v1/exam-autopsy/upload  → ExamAutopsyResponse

TODO (backend): Reemplazar con pipeline real:
  1. OCR del examen con Azure Document Intelligence
  2. Detectar preguntas falladas
  3. RAG search: buscar chunk más relevante en Qdrant por cada error
  4. LLM call: generar causa_error + resumen
  5. Crear sesion_refuerzo_id (sesión de estudio adaptativa sobre los temas fallados)
  6. Guardar resultado en BD
"""
from fastapi import APIRouter, File, UploadFile
from app.schemas.api import ExamAutopsyResponse, ErrorItem
from datetime import datetime
import uuid

router = APIRouter(prefix="/exam-autopsy", tags=["exam-autopsy"])


@router.post("/upload", response_model=ExamAutopsyResponse)
async def upload_exam(file: UploadFile = File(...)):
    """
    Analiza un examen fallado (PDF/JPG/PNG) y devuelve el diagnóstico de errores.
    Actualmente devuelve un reporte mock realista para que el frontend lo muestre.
    """
    content = await file.read()
    autopsy_id = str(uuid.uuid4())
    sesion_id = str(uuid.uuid4())

    # Mock: simula el análisis LLM + RAG sobre el examen subido.
    # En producción cada ErrorItem se genera cruzando las respuestas del alumno
    # con los chunks de sus apuntes (Qdrant) y un prompt de análisis de errores.

    return ExamAutopsyResponse(
        autopsy_id=autopsy_id,
        nombre_examen=file.filename or "Examen subido",
        fecha_analisis=datetime.utcnow().isoformat(),
        resumen=(
            "El alumno muestra dominio parcial de la materia. Los principales fallos "
            "se concentran en conceptos de Dinámica (confusión entre masa y peso) e "
            "Integrales (olvido de la constante de integración). "
            "Se recomienda una sesión de refuerzo de 20 min enfocada en estos dos temas."
        ),
        sesion_refuerzo_id=sesion_id,
        error_items=[
            ErrorItem(
                item_id=str(uuid.uuid4()),
                pregunta_original="¿Cuál es la aceleración de un objeto de 5 kg sometido a una fuerza neta de 15 N?",
                respuesta_alumno="75 m/s²",
                respuesta_correcta="3 m/s²",
                tipo_fallo="confusion",
                causa_error=(
                    "El alumno ha multiplicado F × m en lugar de dividir F / m. "
                    "Confunde la dirección de la operación en la Segunda Ley de Newton (F = ma → a = F/m)."
                ),
                chunk_source=(
                    "Segunda Ley de Newton: La aceleración de un cuerpo es directamente proporcional "
                    "a la fuerza neta aplicada e inversamente proporcional a su masa. a = F / m."
                ),
                asignatura="Física",
                tema="Dinámica",
            ),
            ErrorItem(
                item_id=str(uuid.uuid4()),
                pregunta_original="Calcula ∫(3x²) dx",
                respuesta_alumno="x³",
                respuesta_correcta="x³ + C",
                tipo_fallo="laguna",
                causa_error=(
                    "El alumno olvidó añadir la constante de integración C. "
                    "En integrales indefinidas siempre debe incluirse ya que representa "
                    "una familia de funciones, no una sola."
                ),
                chunk_source=(
                    "Toda integral indefinida debe expresarse con la constante de integración C: "
                    "∫f(x)dx = F(x) + C, donde C ∈ ℝ representa el valor inicial desconocido."
                ),
                asignatura="Matemáticas",
                tema="Integrales",
            ),
            ErrorItem(
                item_id=str(uuid.uuid4()),
                pregunta_original="Nombra el compuesto CH₃-CH=CH₂",
                respuesta_alumno="Propano",
                respuesta_correcta="Propeno",
                tipo_fallo="confusion",
                causa_error=(
                    "El alumno ha confundido el sufijo '-ano' (alcano, enlace simple) "
                    "con '-eno' (alqueno, doble enlace). La presencia de '=' indica doble enlace → alqueno → propeno."
                ),
                chunk_source=(
                    "Nomenclatura IUPAC de hidrocarburos: '-ano' = alcano (solo enlaces simples); "
                    "'-eno' = alqueno (mínimo un doble enlace C=C); '-ino' = alquino (triple enlace)."
                ),
                asignatura="Química Orgánica",
                tema="Alquenos",
            ),
        ],
    )
