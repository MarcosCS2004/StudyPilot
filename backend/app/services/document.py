from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

class DocumentService:
    
    # --- CREATE ---
    @staticmethod
    def create_document(db: Session, document_data: DocumentCreate) -> Document | None:
        """Crea un nuevo documento."""
        try:
            db_document = Document(
                user_id=document_data.user_id,
                subject_id=document_data.subject_id,
                nombre_original=document_data.nombre_original,
                blob_url=document_data.blob_url,
                status='pending'
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            return db_document
        except IntegrityError:
            db.rollback()
            return None

    # --- READ ---
    @staticmethod
    def get_document(db: Session, document_id: str) -> Document | None:
        """Obtiene un documento por su ID."""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_documents_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 10) -> list[Document]:
        """Obtiene todos los documentos de un usuario con paginación."""
        return db.query(Document).filter(
            Document.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_documents_by_subject(db: Session, subject_id: int, skip: int = 0, limit: int = 10) -> list[Document]:
        """Obtiene todos los documentos de una asignatura con paginación."""
        return db.query(Document).filter(
            Document.subject_id == subject_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_documents_by_user_and_subject(db: Session, user_id: str, subject_id: int) -> list[Document]:
        """Obtiene documentos de un usuario para una asignatura específica."""
        return db.query(Document).filter(
            Document.user_id == user_id,
            Document.subject_id == subject_id
        ).all()

    @staticmethod
    def count_documents_by_user(db: Session, user_id: str) -> int:
        """Cuenta documentos de un usuario."""
        return db.query(Document).filter(Document.user_id == user_id).count()

    # --- UPDATE ---
    @staticmethod
    def update_document(db: Session, document_id: str, update_data: DocumentUpdate) -> Document | None:
        """Actualiza un documento existente."""
        db_document = DocumentService.get_document(db, document_id)
        if not db_document:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(db_document, key):
                setattr(db_document, key, value)

        try:
            db.commit()
            db.refresh(db_document)
            return db_document
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_document_status(db: Session, document_id: str, status: str) -> Document | None:
        """Actualiza solo el estado de un documento."""
        db_document = DocumentService.get_document(db, document_id)
        if not db_document:
            return None

        db_document.status = status
        try:
            db.commit()
            db.refresh(db_document)
            return db_document
        except IntegrityError:
            db.rollback()
            return None

    # --- DELETE ---
    @staticmethod
    def delete_document(db: Session, document_id: str) -> bool:
        """Elimina un documento."""
        db_document = DocumentService.get_document(db, document_id)
        if not db_document:
            return False

        try:
            db.delete(db_document)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

    @staticmethod
    def delete_documents_by_user(db: Session, user_id: str) -> bool:
        """Elimina todos los documentos de un usuario."""
        try:
            db.query(Document).filter(Document.user_id == user_id).delete()
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False
