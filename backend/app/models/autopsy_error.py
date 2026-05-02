from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class AutopsyError(Base):
    __tablename__ = "AutopsyErrors"

    error_item_id = Column("ErrorItemId", Integer, primary_key=True, autoincrement=True)
    autopsy_id = Column("AutopsyId", String(36), ForeignKey("ExamAutopsies.AutopsyId"), nullable=False, index=True)
    pregunta_texto = Column("PreguntaTexto", String(500), nullable=True)
    respuesta_alumno = Column("RespuestaAlumno", String(500), nullable=True)
    marca_profesor = Column("MarcaProfesor", String(255), nullable=True)
    tipo_fallo = Column("TipoFallo", String(50), nullable=True)
    nivel_impacto = Column("NivelImpacto", String(50), nullable=True)
    causa_error = Column("CausaError", Text, nullable=True)
    pregunta_refuerzo = Column("PreguntaRefuerzo", String(500), nullable=True)

    # Relación con ExamAutopsy
    autopsy = relationship("ExamAutopsy", back_populates="error_items")
