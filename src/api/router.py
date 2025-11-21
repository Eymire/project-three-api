from fastapi import APIRouter

from src.api.auth.router import router as auth_router
from src.api.users.router import router as users_router


router = APIRouter()

router.include_router(
    auth_router,
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)
