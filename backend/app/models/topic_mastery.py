import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class TopicMastery(Base):
    """Un registro POR CADA tema que el alumno ha estudiado"""
    __tablename__ = 'TopicMastery'

    id = Column('MasteryId', Integer, primary_key=True, autoincrement=True)
    user_id = Column('UserId', String(36), ForeignKey('Users.UserId'), nullable=False, index=True)
    asignatura = Column('Asignatura', String(255), nullable=False)
    tema = Column('Tema', String(255), nullable=False)
    nivel = Column('Nivel', Integer, default=1)             # 1-10
    pct_acierto = Column('PctAcierto', Float, default=0.0)       # 0-100
    total_intentos = Column('TotalIntentos', Integer, default=0)
    aciertos = Column('Aciertos', Integer, default=0)
    intervalo_sm2 = Column('IntervaloSM2', Integer, default=1)     # días hasta próximo repaso
    facilidad_sm2 = Column('FacilidadSM2', Float, default=2.5)     # EF del SM-2
    repeticion_num = Column('RepeticionNum', Integer, default=0)    # n en SM-2
    ultima_revision = Column('UltimaRevision', DateTime(timezone=True), server_default=func.now())
    proxima_revision = Column('ProximaRevision', DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint('UserId', 'Tema', name='uq_user_topic'),)

    # Relación con User
    user = relationship("User", back_populates="topic_masteries")
