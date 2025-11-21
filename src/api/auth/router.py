from fastapi import APIRouter

from src.dependencies import (
    current_user_from_access_dep,
    current_user_from_refresh_dep,
    session_dep,
)
from src.schemas import UserShowSchema

from . import services
from .schemas import TokenSchema, UserSignInSchema, UserSignUpSchema


router = APIRouter()


@router.post('/sign_up')
async def sign_up(
    session: session_dep,
    data: UserSignUpSchema,
) -> UserShowSchema:
    result = await services.sign_up(
        session,
        data,
    )

    return result  # type: ignore


@router.post('/sign_in')
async def sign_in(
    session: session_dep,
    data: UserSignInSchema,
) -> TokenSchema:
    result = await services.sign_in(
        session,
        data,
    )

    return result  # type: ignore


@router.post('/refresh_sign_in')
async def refresh_sign_in(
    current_user: current_user_from_refresh_dep,
) -> TokenSchema:
    result = await services.refresh_sign_in(current_user.id)

    return result  # type: ignore


@router.get('/me')
async def profile(
    current_user: current_user_from_access_dep,
) -> UserShowSchema:
    return current_user  # type: ignore
