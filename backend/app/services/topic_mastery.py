from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.topic_mastery import TopicMastery
from app.schemas.topic_mastery import TopicMasteryCreate, TopicMasteryUpdate
from datetime import datetime

class TopicMasteryService:
    
    @staticmethod
    def get_or_create(db: Session, user_id: str, asignatura: str, tema: str) -> TopicMastery:
        mastery = db.query(TopicMastery).filter(
            TopicMastery.user_id == user_id,
            TopicMastery.tema == tema
        ).first()
        
        if not mastery:
            mastery = TopicMastery(
                user_id=user_id,
                asignatura=asignatura,
                tema=tema
            )
            db.add(mastery)
            db.commit()
            db.refresh(mastery)
        return mastery

    @staticmethod
    def update_performance(db: Session, mastery_id: int, correct: bool, quality: int):
        from app.services.adaptive.sm2_engine import sm2_engine
        mastery = db.query(TopicMastery).filter(TopicMastery.id == mastery_id).first()
        if not mastery:
            return None
            
        # Actualizar estadísticas básicas
        mastery.total_intentos += 1
        if correct:
            mastery.aciertos += 1
        mastery.pct_acierto = (mastery.aciertos / mastery.total_intentos) * 100
        
        # Aplicar SM-2
        sm2_result = sm2_engine.calculate_next_interval(
            mastery.facilidad_sm2,
            mastery.repeticion_num,
            quality
        )
        
        mastery.intervalo_sm2 = sm2_result["interval"]
        mastery.facilidad_sm2 = sm2_result["ef"]
        mastery.repeticion_num = sm2_result["n"]
        mastery.ultima_revision = datetime.utcnow()
        
        # Calcular próxima revisión
        from datetime import timedelta
        mastery.proxima_revision = mastery.ultima_revision + timedelta(days=mastery.intervalo_sm2)
        
        # Ajustar nivel (lógica simple: +1 si acierto, -1 si fallo, min 1 max 10)
        if correct:
            mastery.nivel = min(10, mastery.nivel + 1)
        else:
            mastery.nivel = max(1, mastery.nivel - 1)
            
        db.commit()
        db.refresh(mastery)
        return mastery

    @staticmethod
    def get_user_progress(db: Session, user_id: str):
        return db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
