from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate

class UserService:
    
    # --- CREATE ---
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User | None:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            return None 
            
        db_user = User(
            email=user_data.email,
            hashed_password=user_data.password # Texto plano para proyecto académico
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            return None

    # --- READ ---
    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        """Busca un usuario por su ID primario."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Busca un usuario por su email."""
        return db.query(User).filter(User.email == email).first()

    # --- UPDATE ---
    @staticmethod
    def update_user(db: Session, user_id: int, update_data: dict) -> User | None:
        """Actualiza campos específicos de un usuario pasados como diccionario."""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return None
            
        for key, value in update_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
            # Manejamos el caso especial de la contraseña
            elif key == "password":
                setattr(db_user, "hashed_password", value)
                
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            return None

    # --- DELETE ---
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Elimina un usuario. Cuidado: eliminará en cascada sus perfiles si está configurado así."""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return False
            
        try:
            db.delete(db_user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False