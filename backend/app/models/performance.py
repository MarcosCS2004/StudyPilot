from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from datetime import datetime

class Performance(Base):
    __tablename__ = "performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    topic = Column(String)
    difficulty_level = Column(Float, default=1.0)  # SM-2 easiness factor
    repetitions = Column(Integer, default=0)
    interval = Column(Integer, default=1)  # días
    next_review = Column(DateTime)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
