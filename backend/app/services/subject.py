from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate

class SubjectService:
    @staticmethod
    def create_subject(db: Session, user_id: str, subject_data: SubjectCreate):
        db_subject = Subject(
            user_id=user_id,
            nombre=subject_data.nombre
        )
        db.add(db_subject)
        db.commit()
        db.refresh(db_subject)
        return db_subject
    
    @staticmethod
    def get_subject(db: Session, subject_id: int, user_id: str):
        """Busca una asignatura específica por ID y que pertenezca al usuario."""
        return db.query(Subject).filter(
            Subject.id == subject_id, 
            Subject.user_id == user_id
        ).first()

    @staticmethod
    def get_subjects_by_user(db: Session, user_id: str):
        # Obligatorio order_by para SQL Server
        return db.query(Subject).filter(Subject.user_id == user_id).order_by(Subject.nombre).all()

    @staticmethod
    def update_subject(db: Session, subject_id: int, user_id: str, update_data: dict):
        db_subject = SubjectService.get_subject(db, subject_id, user_id)
        if not db_subject:
            return None
        
        for key, value in update_data.items():
            if hasattr(db_subject, key):
                setattr(db_subject, key, value)
        
        db.commit()
        db.refresh(db_subject)
        return db_subject

    @staticmethod
    def delete_subject(db: Session, subject_id: int, user_id: str):
        db_subject = db.query(Subject).filter(
            Subject.id == subject_id, 
            Subject.user_id == user_id
        ).first()
        if db_subject:
            db.delete(db_subject)
            db.commit()
            return True
        return False