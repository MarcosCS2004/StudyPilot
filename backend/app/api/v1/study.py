import uuid
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.topic_mastery import TopicMasteryService
from app.services.error_history import ErrorHistoryService
from app.schemas.api import (
    NextQuestionResponse,
    QuestionOptions,
    AnswerPayload,
    AnswerResponse,
)
from app.services.ai.llm_client import llm_client
from app.services.ai.dual_rag import dual_rag
from app.services.ai.prompts import (
    QUESTION_SYSTEM,
    QUESTION_USER,
    ANSWER_EVAL_SYSTEM,
    ANSWER_EVAL_USER,
    FEYNMAN_SYSTEM,
    FEYNMAN_USER,
    FORECAST_SYSTEM,
    FORECAST_USER,
)

router = APIRouter(prefix="/study", tags=["study"])

# Cache in memory for questions
_question_cache: dict[str, dict] = {}

class FeynmanPayload(BaseModel):
    tema: str
    asignatura: str
    conceptos_clave: str
    explicacion_alumno: str

class FeynmanResponse(BaseModel):
    comprende: bool
    puntuacion: int
    lagunas: List[str]
    conceptos_correctos: List[str]
    feedback: str
    pregunta_sondeo: str

class ForecastResponse(BaseModel):
    nota_predicha: float
    confianza: int
    intervalo: dict
    temas_fuertes: List[dict]
    temas_debiles: List[dict]
    recomendacion: str

@router.get("/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    asignatura: str = Query(default="General"),
    tema: str = Query(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: Requesting next question for user {current_user.id} in {asignatura}/{tema}")
    topic = tema or asignatura
    
    # Verificar que el usuario tenga documentos subidos
    if not await dual_rag.has_documents(current_user.id):
        raise HTTPException(
            status_code=400, 
            detail="No tienes materiales de estudio subidos. Sube un PDF para que el tutor pueda generar preguntas personalizadas."
        )

    # Obtener nivel real del alumno para este tema
    mastery = TopicMasteryService.get_or_create(db, current_user.id, asignatura, topic)
    nivel_actual = mastery.nivel

    context = await dual_rag.retrieve_context(
        topic=topic,
        user_id=current_user.id,
        difficulty=nivel_actual,
    )

    user_prompt = QUESTION_USER.format(
        asignatura=asignatura,
        tema=topic,
        nivel_actual=nivel_actual,
        nivel_solicitado=nivel_actual,
        random_seed=str(uuid.uuid4())[:8],
        **context,
    )

    raw = await llm_client.generate_json(QUESTION_SYSTEM, user_prompt)
    
    # --- Robust Shuffle Logic ---
    import random
    
    # Extract original options and correct answer
    orig_options = raw["opciones"]
    orig_correct_letter = raw["respuesta_correcta"]
    correct_text = orig_options[orig_correct_letter]
    
    # Shuffle all option texts
    option_texts = list(orig_options.values())
    random.shuffle(option_texts)
    
    # Re-map to letters A, B, C, D
    shuffled_options = {
        "A": option_texts[0],
        "B": option_texts[1],
        "C": option_texts[2],
        "D": option_texts[3],
    }
    
    # Find new correct letter
    new_correct_letter = "A"
    for letter, text in shuffled_options.items():
        if text == correct_text:
            new_correct_letter = letter
            break
            
    print(f"DEBUG: Question shuffled. Original correct: {orig_correct_letter}, New correct: {new_correct_letter}")
    # ---------------------------

    question_id = str(uuid.uuid4())
    _question_cache[question_id] = {
        "enunciado": raw["enunciado"],
        "opciones": shuffled_options,
        "respuesta_correcta": new_correct_letter,
        "chunk_source": raw.get("chunk_source", ""),
        "nivel_dificultad": raw.get("nivel_dificultad", nivel_actual),
        "asignatura": asignatura,
        "tema": topic,
        "mastery_id": mastery.id
    }

    return NextQuestionResponse(
        question_id=question_id,
        asignatura=asignatura,
        tema=topic,
        enunciado=raw["enunciado"],
        opciones=QuestionOptions(**shuffled_options),
        nivel_dificultad=raw.get("nivel_dificultad", nivel_actual),
    )

@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(
    payload: AnswerPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = _question_cache.get(payload.question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")

    opciones = q["opciones"]
    user_prompt = ANSWER_EVAL_USER.format(
        enunciado=q["enunciado"],
        opcion_a=opciones.get("A", ""),
        opcion_b=opciones.get("B", ""),
        opcion_c=opciones.get("C", ""),
        opcion_d=opciones.get("D", ""),
        respuesta_correcta=q["respuesta_correcta"],
        respuesta_alumno=payload.respuesta,
        nivel_dificultad=q["nivel_dificultad"],
        chunk_source=q["chunk_source"],
    )

    raw = await llm_client.generate_json(ANSWER_EVAL_SYSTEM, user_prompt)
    
    # Persistir progreso y actualizar SM-2
    # quality: mapeamos correcto/incorrecto a 5 o 2
    quality = 5 if raw["correcto"] else 2
    mastery = TopicMasteryService.update_performance(
        db, q["mastery_id"], raw["correcto"], quality
    )
    
    db.commit()

    # Si falló, guardar en historial de errores
    if not raw["correcto"]:
        ErrorHistoryService.increment_fallo(
            db, current_user.id, q.get("chunk_source", "unknown"), q["tema"], raw.get("explicacion")
        )

    return AnswerResponse(
        correcto=raw["correcto"],
        respuesta_correcta=raw["respuesta_correcta"],
        explicacion=raw["explicacion"],
        nuevo_nivel_tema=mastery.nivel
    )

@router.post("/feynman", response_model=FeynmanResponse)
async def feynman_evaluation(
    payload: FeynmanPayload,
    current_user: User = Depends(get_current_user),
):
    context = await dual_rag.retrieve_context(
        topic=payload.tema,
        user_id=current_user.id,
        difficulty=10,
    )

    user_prompt = FEYNMAN_USER.format(
        tema=payload.tema,
        asignatura=payload.asignatura,
        conceptos_clave=payload.conceptos_clave,
        explicacion_alumno=payload.explicacion_alumno,
        chunks_from_notes=context["chunks_from_notes"],
    )

    raw = await llm_client.generate_json(FEYNMAN_SYSTEM, user_prompt)
    return FeynmanResponse(**raw)

from app.models.topic_mastery import TopicMastery

@router.get("/forecast", response_model=ForecastResponse)
async def exam_forecast(
    asignatura: str = Query(...),
    dias_hasta_examen: int = Query(default=7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    masteries = db.query(TopicMastery).filter(
        TopicMastery.user_id == current_user.id,
        TopicMastery.asignatura == asignatura
    ).all()
    
    import json
    topics_json = json.dumps([
        {"tema": m.tema, "nivel": m.nivel, "pct_acierto": m.pct_acierto, "dias_sin_repasar": 0}
        for m in masteries
    ])
    
    user_prompt = FORECAST_USER.format(
        nombre=current_user.nombre or current_user.email,
        asignatura=asignatura,
        dias_hasta_examen=dias_hasta_examen,
        topics_json=topics_json,
        accuracy_reciente="N/A",
    )

    raw = await llm_client.generate_json(FORECAST_SYSTEM, user_prompt)
    return ForecastResponse(**raw)
