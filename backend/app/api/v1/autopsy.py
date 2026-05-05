import uuid
from datetime import datetime
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.schemas.api import ErrorItem, ExamAutopsyResponse
from app.services.ai.dual_rag import dual_rag
from app.services.ai.llm_client import llm_client
from app.services.ai.prompts import (
    AUTOPSY_IMAGE_USER,
    AUTOPSY_SYSTEM,
    AUTOPSY_USER,
)
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.error_history import ErrorHistoryService

router = APIRouter(prefix="/autopsy", tags=["autopsy"])

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.post("/upload", response_model=ExamAutopsyResponse)
async def upload_exam(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts exam photo (JPG/PNG) or text-based file (PDF/DOCX/TXT).
    """
    content = await file.read()
    mime = file.content_type or ""

    # Initial search query
    if mime not in IMAGE_MIME_TYPES:
        exam_text_preview = content.decode("utf-8", errors="ignore")[:200]
        initial_query = exam_text_preview or file.filename or "exam review"
        failed_topics = [initial_query]
    else:
        # Heuristic for images: search for the filename but also for recent user topics
        filename_query = (file.filename or "exam").replace("_", " ").rsplit(".", 1)[0]
        recent_errors = await ErrorHistoryService.get_all_recent(current_user.id, limit=3)
        recent_topics = list(set([e["tema"] for e in recent_errors if e.get("tema")]))
        failed_topics = ([filename_query] if len(filename_query) > 3 else []) + recent_topics
        if not failed_topics:
            failed_topics = ["General"]

    # Context retrieval
    notes_chunks = await dual_rag.retrieve_autopsy_context(
        failed_topics=failed_topics,
        user_id=current_user.id,
    )

    # Prior errors
    history = await ErrorHistoryService.get_all_recent(current_user.id, limit=10)
    error_history = "; ".join(f"{e['tema']}: {e['descripcion']}" for e in history) if history else "None"

    # LLM Call
    try:
        if mime in IMAGE_MIME_TYPES:
            raw = await llm_client.generate_with_image(
                system=AUTOPSY_SYSTEM,
                user=AUTOPSY_IMAGE_USER.format(
                    notes_chunks=notes_chunks,
                    error_history=error_history,
                ),
                image_bytes=content,
                mime_type=mime,
            )
        else:
            exam_text = content.decode("utf-8", errors="ignore")[:5000]
            raw = await llm_client.generate_json(
                system=AUTOPSY_SYSTEM,
                user=AUTOPSY_USER.format(
                    exam_text=exam_text,
                    notes_chunks=notes_chunks,
                    error_history=error_history,
                ),
            )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"LLM unavailable: {exc}")

    # --- PERSISTENCE ---
    from app.models.exam_autopsy import ExamAutopsy
    from app.models.autopsy_error import AutopsyError
    from app.models.subject import Subject

    # Try to find a relevant subject for this autopsy
    raw_error_items = raw.get("error_items", [])
    if raw_error_items:
        subject_name = raw_error_items[0].get("asignatura", "General")
    else:
        subject_name = "General"
    
    subject = db.query(Subject).filter(Subject.nombre == subject_name).first()
    subject_id = subject.id if subject else 1 # Default to 1 if not found

    db_autopsy = ExamAutopsy(
        user_id=current_user.id,
        subject_id=subject_id,
        fecha_examen=datetime.utcnow(),
        analisis_status="completada"
    )
    db.add(db_autopsy)
    db.flush() # Get ID

    error_items = []
    for raw_item in raw.get("error_items", []):
        try:
            # Map to ErrorItem schema for API response
            item_id = str(uuid.uuid4())
            error_items.append(ErrorItem(item_id=item_id, **raw_item))
            
            # Map to AutopsyError model for DB
            db_error = AutopsyError(
                autopsy_id=db_autopsy.id,
                pregunta_texto=raw_item.get("pregunta_original", ""),
                respuesta_alumno=raw_item.get("respuesta_alumno", ""),
                marca_profesor=raw_item.get("respuesta_correcta", ""), # Usamos esto como referencia
                tipo_fallo=raw_item.get("tipo_fallo", "parcial"),
                causa_error=raw_item.get("causa_error", ""),
                pregunta_refuerzo="" # Podríamos generarla después
            )
            db.add(db_error)
        except Exception as e:
            print(f"DEBUG: Error mapping autopsy item: {e}")
            continue

    # --- SAVE FILE LOCALLY ---
    import os
    UPLOAD_DIR = "static/uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    file_name = f"{db_autopsy.id}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(content)
    
    exam_image_url = f"http://localhost:8000/static/uploads/{file_name}"
    db_autopsy.exam_image_url = exam_image_url
    # -------------------------

    db.commit()

    return ExamAutopsyResponse(
        autopsy_id=db_autopsy.id,
        nombre_examen=file.filename or "Uploaded exam",
        fecha_analisis=db_autopsy.fecha_examen.isoformat(),
        error_items=error_items,
        sesion_refuerzo_id=str(uuid.uuid4()),
        resumen=raw.get("resumen", "Analysis complete."),
        exam_image_url=exam_image_url
    )
