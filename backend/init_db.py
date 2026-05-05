import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.models.base import Base
# Import all models to ensure they are registered
from app.models.user import User
from app.models.subject import Subject
from app.models.document import Document
from app.models.topic_mastery import TopicMastery
from app.models.error_history import ErrorHistory
from app.models.exam_autopsy import ExamAutopsy
from app.models.autopsy_error import AutopsyError

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_db()
