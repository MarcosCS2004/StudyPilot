from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ErrorHistory(Base):
    __tablename__ = "ErrorHistory"

    error_id = Column("ErrorId", Integer, primary_key=True, autoincrement=True)
    user_id = Column("UserId", String(36), ForeignKey("Users.UserId"), nullable=False, index=True)
    chunk_id = Column("ChunkId", String(200), nullable=False, index=True)
    tema = Column("Tema", String(255), nullable=False, index=True)
    asignatura = Column("Asignatura", String(255), nullable=True)
    descripcion = Column("Descripcion", String(1000), nullable=True)
    tipo_fallo = Column("TipoFallo", String(50), nullable=True)  # laguna/confusion/parcial
    veces_fallado = Column("VecesFallado", Integer, nullable=False, default=0)
    fecha_ultimo_fallo = Column("FechaUltimoFallo", DateTime, nullable=True)

    # Relación con User
    user = relationship("User", back_populates="error_history")