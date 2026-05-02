from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentListResponse, DocumentUpdate
from app.services.document import DocumentService

router = APIRouter(tags=["Documentos"])

# --- CREATE ---
@router.post("/", response_model=DocumentResponse, status_code=201)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Crea un nuevo documento."""
    document = DocumentService.create_document(db, document_data)
    if not document:
        raise HTTPException(status_code=400, detail="No se pudo crear el documento")
    return document

# --- READ ---
@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Obtiene un documento por su ID."""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document

@router.get("/user/{user_id}", response_model=DocumentListResponse)
def get_user_documents(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtiene todos los documentos de un usuario."""
    documents = DocumentService.get_documents_by_user(db, user_id, skip, limit)
    total = DocumentService.count_documents_by_user(db, user_id)
    return DocumentListResponse(documentos=documents, total=total)

@router.get("/subject/{subject_id}", response_model=DocumentListResponse)
def get_subject_documents(
    subject_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtiene todos los documentos de una asignatura."""
    documents = DocumentService.get_documents_by_subject(db, subject_id, skip, limit)
    total = db.query(Document).filter(Document.subject_id == subject_id).count()
    return DocumentListResponse(documentos=documents, total=total)

@router.get("/user/{user_id}/subject/{subject_id}", response_model=list[DocumentResponse])
def get_user_subject_documents(
    user_id: str,
    subject_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene documentos de un usuario para una asignatura específica."""
    documents = DocumentService.get_documents_by_user_and_subject(db, user_id, subject_id)
    return documents

# --- UPDATE ---
@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un documento existente."""
    document = DocumentService.update_document(db, document_id, update_data)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document

@router.patch("/{document_id}/status", response_model=DocumentResponse)
def update_document_status(
    document_id: str,
    status: str = Query(..., description="Nuevo estado: pending, processing, completed, failed"),
    db: Session = Depends(get_db)
):
    """Actualiza solo el estado de un documento."""
    valid_statuses = ["pending", "processing", "completed", "failed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Estado inválido. Estados válidos: {', '.join(valid_statuses)}"
        )
    
    document = DocumentService.update_document_status(db, document_id, status)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document

# --- DELETE ---
@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Elimina un documento."""
    success = DocumentService.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return None

@router.delete("/user/{user_id}", status_code=204)
def delete_user_documents(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Elimina todos los documentos de un usuario."""
    success = DocumentService.delete_documents_by_user(db, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudieron eliminar los documentos")
    return None
