from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.error_history import ErrorHistory
from app.schemas.error_history import ErrorHistoryCreate, ErrorHistoryUpdate
from datetime import datetime

class ErrorHistoryService:

    @staticmethod
    def create(db: Session, data: ErrorHistoryCreate) -> ErrorHistory:
        """Crea un nuevo registro de error."""
        try:
            record = ErrorHistory(
                user_id=data.user_id,
                chunk_id=data.chunk_id,
                tema=data.tema,
                asignatura=data.asignatura,
                descripcion=data.descripcion,
                tipo_fallo=data.tipo_fallo,
                veces_fallado=data.veces_fallado or 0,
                fecha_ultimo_fallo=data.fecha_ultimo_fallo or datetime.utcnow()
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_id(db: Session, error_id: int) -> ErrorHistory | None:
        """Obtiene un registro por su ID."""
        return db.query(ErrorHistory).filter(ErrorHistory.error_id == error_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: str) -> list[ErrorHistory]:
        """Obtiene todos los errores de un usuario."""
        return db.query(ErrorHistory).filter(ErrorHistory.user_id == user_id).all()

    @staticmethod
    def get_by_user_and_chunk(db: Session, user_id: str, chunk_id: str) -> ErrorHistory | None:
        """Obtiene el error de un usuario para un chunk específico."""
        return db.query(ErrorHistory).filter(
            ErrorHistory.user_id == user_id,
            ErrorHistory.chunk_id == chunk_id
        ).first()

    @staticmethod
    def increment_fallo(db: Session, user_id: str, chunk_id: str, tema: str, descripcion: str = None) -> ErrorHistory:
        """Incrementa el contador de fallos o crea el registro si no existe."""
        try:
            record = ErrorHistoryService.get_by_user_and_chunk(db, user_id, chunk_id)
            if record:
                record.veces_fallado = (record.veces_fallado or 0) + 1
                record.fecha_ultimo_fallo = datetime.utcnow()
                if descripcion: record.descripcion = descripcion
            else:
                record = ErrorHistory(
                    user_id=user_id,
                    chunk_id=chunk_id,
                    tema=tema,
                    descripcion=descripcion,
                    veces_fallado=1,
                    fecha_ultimo_fallo=datetime.utcnow()
                )
                db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    async def get_recent(user_id: str, topic: str, limit: int = 3) -> list[dict]:
        """Versión async para el orquestador RAG."""
        from app.db.session import SessionLocal
        with SessionLocal() as db:
            errors = db.query(ErrorHistory).filter(
                ErrorHistory.user_id == user_id,
                ErrorHistory.tema == topic
            ).order_by(ErrorHistory.fecha_ultimo_fallo.desc()).limit(limit).all()
            
            return [
                {
                    "tema": e.tema,
                    "descripcion": e.descripcion or f"Error en {e.tema}",
                    "tipo_fallo": e.tipo_fallo
                } for e in errors
            ]

    @staticmethod
    async def get_all_recent(user_id: str, limit: int = 10) -> list[dict]:
        """Obtiene todos los errores recientes de un usuario."""
        from app.db.session import SessionLocal
        with SessionLocal() as db:
            errors = db.query(ErrorHistory).filter(
                ErrorHistory.user_id == user_id
            ).order_by(ErrorHistory.fecha_ultimo_fallo.desc()).limit(limit).all()
            
            return [
                {
                    "tema": e.tema,
                    "descripcion": e.descripcion or f"Error en {e.tema}",
                    "tipo_fallo": e.tipo_fallo
                } for e in errors
            ]

    @staticmethod
    def update(db: Session, error_id: int, data: ErrorHistoryUpdate) -> ErrorHistory | None:
        """Actualiza un registro de error."""
        try:
            record = ErrorHistoryService.get_by_id(db, error_id)
            if not record:
                return None
            update_dict = data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def delete(db: Session, error_id: int) -> bool:
        """Elimina un registro de error."""
        try:
            record = ErrorHistoryService.get_by_id(db, error_id)
            if not record:
                return False
            db.delete(record)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def delete_by_user(db: Session, user_id: str) -> bool:
        """Elimina todos los errores de un usuario."""
        try:
            db.query(ErrorHistory).filter(ErrorHistory.user_id == user_id).delete()
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise e