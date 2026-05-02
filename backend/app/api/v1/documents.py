"""
POST /api/v1/documents/upload  → UploadResponse

TODO (backend): Reemplazar con lógica real de ingestion:
  - Parsear archivo con Azure Document Intelligence (OCR)
  - Chunking del texto
  - Generar embeddings y guardar en Qdrant (vector store)
  - Guardar metadata en tabla document (BD)
"""
from fastapi import APIRouter, File, UploadFile, Form
from app.schemas.api import UploadResponse
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/jpeg",
    "image/png",
}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    asignatura_id: str = Form(default="default"),
):
    """
    Recibe un archivo (PDF/DOCX/JPG/PNG) y lo ingiere para el RAG.
    Actualmente simula el procesamiento; devuelve file_id y estado.
    """
    if file.content_type not in ALLOWED_TYPES:
        return UploadResponse(
            file_id="",
            status="error",
            mensaje=f"Tipo de archivo no soportado: {file.content_type}",
        )

    # Leer el archivo (necesario para que no quede el stream colgado)
    content = await file.read()
    file_id = str(uuid.uuid4())

    # TODO: Aquí llamar al pipeline de ingestion:
    #   parsed_text = await azure_ocr.parse(content, file.content_type)
    #   chunks = chunker.split(parsed_text)
    #   await qdrant.upsert(chunks, asignatura_id=asignatura_id)
    #   await db.save_document_meta(file_id, file.filename, asignatura_id)

    return UploadResponse(
        file_id=file_id,
        status="done",
        mensaje=f"Archivo '{file.filename}' ({len(content) // 1024} KB) procesado correctamente.",
    )
