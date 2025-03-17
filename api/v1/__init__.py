from fastapi import APIRouter

from api.v1.analytics.views import router as analytics_router
from api.v1.auth.views import router as auth_router
from api.v1.notes.views import router as notes_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(analytics_router)
router.include_router(notes_router)
