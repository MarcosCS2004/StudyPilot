from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.autopsy_error import AutopsyError
from app.schemas.autopsy_error import AutopsyErrorCreate, AutopsyErrorUpdate

class AutopsyErrorService:

    @staticmethod
    def create(db: Session, data: AutopsyErrorCreate) -> AutopsyError:
        """Crea un nuevo error de autopsia."""
        try:
            record = AutopsyError(
                autopsy_id=data.autopsy_id,
                pregunta_texto=data.pregunta_texto,
                respuesta_alumno=data.respuesta_alumno,
                marca_profesor=data.marca_profesor,
                tipo_fallo=data.tipo_fallo,
                nivel_impacto=data.nivel_impacto,
                causa_error=data.causa_error,
                pregunta_refuerzo=data.pregunta_refuerzo
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_id(db: Session, error_item_id: int) -> AutopsyError | None:
        """Obtiene un error por su ID."""
        return db.query(AutopsyError).filter(AutopsyError.error_item_id == error_item_id).first()

    @staticmethod
    def get_by_autopsy(db: Session, autopsy_id: str) -> list[AutopsyError]:
        """Obtiene todos los errores de una autopsia."""
        return db.query(AutopsyError).filter(AutopsyError.autopsy_id == autopsy_id).all()

    @staticmethod
    def count_by_autopsy(db: Session, autopsy_id: str) -> int:
        """Cuenta los errores de una autopsia."""
        return db.query(AutopsyError).filter(AutopsyError.autopsy_id == autopsy_id).count()

    @staticmethod
    def get_by_tipo_fallo(db: Session, tipo_fallo: str) -> list[AutopsyError]:
        """Obtiene errores por tipo de fallo."""
        return db.query(AutopsyError).filter(AutopsyError.tipo_fallo == tipo_fallo).all()

    @staticmethod
    def get_by_nivel_impacto(db: Session, autopsy_id: str, nivel_impacto: str) -> list[AutopsyError]:
        """Obtiene errores de una autopsia por nivel de impacto."""
        return db.query(AutopsyError).filter(
            AutopsyError.autopsy_id == autopsy_id,
            AutopsyError.nivel_impacto == nivel_impacto
        ).all()

    @staticmethod
    def update(db: Session, error_item_id: int, data: AutopsyErrorUpdate) -> AutopsyError | None:
        """Actualiza un error de autopsia."""
        try:
            record = AutopsyErrorService.get_by_id(db, error_item_id)
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
    def delete(db: Session, error_item_id: int) -> bool:
        """Elimina un error de autopsia."""
        try:
            record = AutopsyErrorService.get_by_id(db, error_item_id)
            if not record:
                return False
            db.delete(record)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def delete_by_autopsy(db: Session, autopsy_id: str) -> bool:
        """Elimina todos los errores de una autopsia."""
        try:
            db.query(AutopsyError).filter(AutopsyError.autopsy_id == autopsy_id).delete()
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise e
