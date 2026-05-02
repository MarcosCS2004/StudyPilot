import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Document(Base):
    __tablename__ = 'Documents'

    id = Column('DocumentId', String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column('UserId', String(36), ForeignKey('Users.UserId'), nullable=False, index=True)
    subject_id = Column('SubjectId', Integer, ForeignKey('Subjects.SubjectId'), nullable=False, index=True)
    nombre_original = Column('NombreOriginal', String(255), nullable=False)
    blob_url = Column('BlobUrl', String(500), nullable=True)
    status = Column('Status', String(50), default='pending', nullable=False)  # pending, processing, completed, failed
    fecha_subida = Column('FechaSubida', DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="documents")
    subject = relationship("Subject", back_populates="documents")
