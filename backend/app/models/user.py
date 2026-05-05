import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = 'Users'

    id = Column('UserId', String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column('Email', String(255), unique=True, index=True, nullable=False)
    hashed_password = Column('HashedPassword', String(255), nullable=False)
    created_at = Column('CreatedAt', DateTime(timezone=True), server_default=func.now())
    racha_dias = Column('RachaDias', Integer, default=0)
    xp_total = Column('XpTotal', Integer, default=0)
    nombre = Column('Nombre', String(255), nullable=True)
    ultimo_acceso = Column('UltimoAcceso', DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    topic_masteries = relationship("TopicMastery", back_populates="user", cascade="all, delete-orphan")
    error_history = relationship("ErrorHistory", back_populates="user", cascade="all, delete-orphan")
    exams_autopsy = relationship("ExamAutopsy", back_populates="user", cascade="all, delete-orphan")