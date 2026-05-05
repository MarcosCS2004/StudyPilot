"""
Router principal de la API v1.
Registra todos los sub-routers de cada módulo.
"""
from fastapi import APIRouter
from app.api.v1 import auth, documents, study, autopsy, profile, chat, exam_autopsy

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(documents.router)
router.include_router(study.router)
router.include_router(autopsy.router)
router.include_router(profile.router)
router.include_router(chat.router)
router.include_router(exam_autopsy.router, prefix="/exam-autopsy")
