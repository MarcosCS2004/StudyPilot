from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.student_profile import StudentProfile
from app.schemas.student_profile import StudentProfileCreate, StudentProfileUpdate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

class StudentProfileService:
    
    # --- CREATE ---
    @staticmethod
    def create_student_profile(db: Session, profile_data: StudentProfileCreate) -> StudentProfile | None:
        try:
            db_profile = StudentProfile(
                user_id=profile_data.user_id,
                tema=profile_data.tema,
                nivel_tema=profile_data.nivel_tema or 1,
                intervalo_sm2=profile_data.intervalo_sm2 or 1,
                facilidad_sm2=profile_data.facilidad_sm2 or 2.5,
                ultima_revision=profile_data.ultima_revision
            )
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except SQLAlchemyError as e:  # ← captura TODOS los errores de SQLAlchemy
            db.rollback()
            raise e  # ← relanza para que el router lo muestre

    # --- READ ---
    @staticmethod
    def get_student_profile(db: Session, profile_id: int) -> StudentProfile | None:
        """Obtiene un perfil de estudiante por su ID."""
        return db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()

    @staticmethod
    def get_student_profile_by_user(db: Session, user_id: str) -> StudentProfile | None:
        """Obtiene el perfil de estudiante de un usuario (relación 1:1)."""
        return db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()

    # --- UPDATE ---
    @staticmethod
    def update_student_profile(db: Session, profile_id: int, update_data: StudentProfileUpdate) -> StudentProfile | None:
        """Actualiza un perfil de estudiante."""
        db_profile = StudentProfileService.get_student_profile(db, profile_id)
        if not db_profile:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(db_profile, key):
                setattr(db_profile, key, value)

        try:
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_student_profile_by_user(db: Session, user_id: str, update_data: StudentProfileUpdate) -> StudentProfile | None:
        """Actualiza el perfil de estudiante de un usuario."""
        db_profile = StudentProfileService.get_student_profile_by_user(db, user_id)
        if not db_profile:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(db_profile, key):
                setattr(db_profile, key, value)

        try:
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_tema_and_nivel(db: Session, user_id: str, tema: str, nivel: int) -> StudentProfile | None:
        """Actualiza el tema y nivel del perfil de un usuario."""
        db_profile = StudentProfileService.get_student_profile_by_user(db, user_id)
        if not db_profile:
            return None

        db_profile.tema = tema
        db_profile.nivel_tema = nivel

        try:
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def update_sm2_values(db: Session, user_id: str, intervalo: int, facilidad: float, ultima_revision) -> StudentProfile | None:
        """Actualiza los valores del algoritmo SM2."""
        db_profile = StudentProfileService.get_student_profile_by_user(db, user_id)
        if not db_profile:
            return None

        db_profile.intervalo_sm2 = intervalo
        db_profile.facilidad_sm2 = facilidad
        db_profile.ultima_revision = ultima_revision

        try:
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except IntegrityError:
            db.rollback()
            return None

    # --- DELETE ---
    @staticmethod
    def delete_student_profile(db: Session, profile_id: int) -> bool:
        """Elimina un perfil de estudiante."""
        db_profile = StudentProfileService.get_student_profile(db, profile_id)
        if not db_profile:
            return False

        try:
            db.delete(db_profile)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

    @staticmethod
    def delete_student_profile_by_user(db: Session, user_id: str) -> bool:
        """Elimina el perfil de estudiante de un usuario."""
        db_profile = StudentProfileService.get_student_profile_by_user(db, user_id)
        if not db_profile:
            return False

        try:
            db.delete(db_profile)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False
