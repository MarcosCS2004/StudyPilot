from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Subir e ingerir documento"""
    # TODO: Implementar lógica de ingestion/parser.py
    pass

@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """Listar documentos del usuario"""
    pass

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Eliminar documento"""
    pass
