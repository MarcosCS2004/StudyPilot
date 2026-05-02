import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class StudentProfile(Base):
    __tablename__ = 'StudentProfile'

    id = Column('ProfileId', Integer, primary_key=True, autoincrement=True)
    user_id = Column('UserId', String(36), ForeignKey('Users.UserId'), nullable=False, unique=True, index=True)
    tema = Column('Tema', String(255), nullable=True)
    nivel_tema = Column('NivelTema', Integer, default=1, nullable=False)
    intervalo_sm2 = Column('IntervaloSM2', Integer, default=1, nullable=False)
    facilidad_sm2 = Column('FacilidadSM2', Float, default=2.5, nullable=False)
    ultima_revision = Column('UltimaRevision', DateTime(timezone=True), nullable=True)

    # Relación 1:1 con User
    user = relationship("User", back_populates="student_profile", uselist=False)
