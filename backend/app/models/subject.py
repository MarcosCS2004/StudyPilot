from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base

class Subject(Base):
    __tablename__ = 'Subjects'

    id = Column('SubjectId', Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column('UserId', String(36), ForeignKey('Users.UserId'), nullable=False)
    nombre = Column('Nombre', String(255), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="subjects")
    documents = relationship("Document", back_populates="subject", cascade="all, delete-orphan")
    exams_autopsy = relationship("ExamAutopsy", back_populates="subject", cascade="all, delete-orphan")