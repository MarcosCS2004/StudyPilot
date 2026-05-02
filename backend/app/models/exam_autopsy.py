import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ExamAutopsy(Base):
    __tablename__ = "ExamAutopsies"

    id = Column("AutopsyId", String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column("UserId", String(36), ForeignKey("Users.UserId"), nullable=False, index=True)
    subject_id = Column("SubjectId", Integer, ForeignKey("Subjects.SubjectId"), nullable=False, index=True)
    fecha_examen = Column("FechaExamen", DateTime(timezone=True), nullable=True)
    analisis_status = Column("AnalisisStatus", String(100), nullable=True)

    # Relaciones
    user = relationship("User", back_populates="exams_autopsy")
    subject = relationship("Subject", back_populates="exams_autopsy")
    error_items = relationship("AutopsyError", back_populates="autopsy", cascade="all, delete-orphan")
