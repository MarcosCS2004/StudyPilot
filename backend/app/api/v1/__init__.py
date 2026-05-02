from fastapi import APIRouter
from .user import router as users_router
from .subject import router as subjects_router
from .document import router as documents_router
from .student_profile import router as student_profile_router
from .error_history import router as error_history_router
from .autopsy_error import router as autopsy_error_router
from .exam_autopsy import router as exam_autopsy_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["Usuarios"])
router.include_router(subjects_router, prefix="/subjects", tags=["Asignaturas"])
router.include_router(documents_router, prefix="/documents", tags=["Documentos"])
router.include_router(student_profile_router, prefix="/student-profile", tags=["Perfil Estudiante"])
router.include_router(error_history_router, prefix="/error-history", tags=["Historial de Errores"])
router.include_router(autopsy_error_router, prefix="/autopsy-errors", tags=["Errores de Autopsia"])
router.include_router(exam_autopsy_router, prefix="/exam-autopsy", tags=["Análisis de Exámenes"])