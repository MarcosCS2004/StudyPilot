from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.exam_autopsy import ExamAutopsy
from app.schemas.exam_autopsy import ExamAutopsyCreate, ExamAutopsyUpdate

class ExamAutopsyService:

    @staticmethod
    def create(db: Session, data: ExamAutopsyCreate) -> ExamAutopsy:
        """Crea una nueva autopsia de examen."""
        try:
            record = ExamAutopsy(
                user_id=data.user_id,
                subject_id=data.subject_id,
                fecha_examen=data.fecha_examen,
                analisis_status=data.analisis_status
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_id(db: Session, autopsy_id: str) -> ExamAutopsy | None:
        """Obtiene una autopsia por su ID."""
        return db.query(ExamAutopsy).filter(ExamAutopsy.id == autopsy_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: str) -> list[ExamAutopsy]:
        """Obtiene todas las autopsias de un usuario."""
        return db.query(ExamAutopsy).filter(ExamAutopsy.user_id == user_id).all()

    @staticmethod
    def count_by_user(db: Session, user_id: str) -> int:
        """Cuenta autopsias de un usuario."""
        return db.query(ExamAutopsy).filter(ExamAutopsy.user_id == user_id).count()

    @staticmethod
    def get_by_subject(db: Session, subject_id: int) -> list[ExamAutopsy]:
        """Obtiene todas las autopsias de una asignatura."""
        return db.query(ExamAutopsy).filter(ExamAutopsy.subject_id == subject_id).all()

    @staticmethod
    def count_by_subject(db: Session, subject_id: int) -> int:
        """Cuenta autopsias de una asignatura."""
        return db.query(ExamAutopsy).filter(ExamAutopsy.subject_id == subject_id).count()

    @staticmethod
    def get_by_user_and_subject(db: Session, user_id: str, subject_id: int) -> list[ExamAutopsy]:
        """Obtiene autopsias de un usuario para una asignatura específica."""
        return db.query(ExamAutopsy).filter(
            ExamAutopsy.user_id == user_id,
            ExamAutopsy.subject_id == subject_id
        ).all()

    @staticmethod
    def get_by_estado(db: Session, estado: str) -> list[ExamAutopsy]:
        """Obtiene autopsias filtradas por estado."""
        return db.query(ExamAutopsy).filter(ExamAutopsy.analisis_status == estado).all()

    @staticmethod
    def update(db: Session, autopsy_id: str, data: ExamAutopsyUpdate) -> ExamAutopsy | None:
        """Actualiza una autopsia de examen."""
        try:
            record = ExamAutopsyService.get_by_id(db, autopsy_id)
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
    def update_estado(db: Session, autopsy_id: str, estado: str) -> ExamAutopsy | None:
        """Actualiza solo el estado de una autopsia."""
        try:
            record = ExamAutopsyService.get_by_id(db, autopsy_id)
            if not record:
                return None
            record.analisis_status = estado
            db.commit()
            db.refresh(record)
            return record
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def delete(db: Session, autopsy_id: str) -> bool:
        """Elimina una autopsia de examen."""
        try:
            record = ExamAutopsyService.get_by_id(db, autopsy_id)
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
        """Elimina todas las autopsias de un usuario."""
        try:
            db.query(ExamAutopsy).filter(ExamAutopsy.user_id == user_id).delete()
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise e
