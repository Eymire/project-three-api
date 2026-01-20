from fastapi import APIRouter

from .auth.router import router as auth_router
from .files.router import router as files_router


router = APIRouter()

router.include_router(
    auth_router,
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    files_router,
    prefix='/files',
    tags=['files'],
)
