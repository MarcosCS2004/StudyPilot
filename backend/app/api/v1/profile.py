from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.api import ProfileProgressResponse, SubjectProgress, TopicLevel
from app.models.user import User
from app.models.topic_mastery import TopicMastery
from app.api.v1.auth import get_current_user
from itertools import groupby

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/progress", response_model=ProfileProgressResponse)
def get_profile_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns full student profile: XP, streak, and mastery per subject/topic.
    """
    masteries = db.query(TopicMastery).filter(TopicMastery.user_id == current_user.id).all()
    masteries.sort(key=lambda x: x.asignatura)
    
    subjects_list = []
    for asignatura, group in groupby(masteries, key=lambda x: x.asignatura):
        temas = [
            TopicLevel(
                nombre_tema=m.tema,
                nivel=m.nivel,
                pct_acierto=m.pct_acierto
            ) for m in group
        ]
        subjects_list.append(
            SubjectProgress(
                asignatura_id=asignatura.lower().replace(" ", "-"),
                nombre_asignatura=asignatura,
                temas=temas
            )
        )

    return ProfileProgressResponse(
        alumno_id=str(current_user.id),
        nombre=current_user.nombre or current_user.email.split("@")[0],
        asignaturas=subjects_list
    )
