from fastapi import APIRouter
from app.api.v1 import documents, study, autopsy, profile

router = APIRouter(prefix="/api/v1")
router.include_router(documents.router)
router.include_router(study.router)
router.include_router(autopsy.router)
router.include_router(profile.router)
