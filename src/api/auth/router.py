from fastapi import APIRouter
from fastapi.security import HTTPBearer

from src.dependencies import current_user_access_dep, current_user_refresh_dep, session_dep

from . import services
from .schemas import SignIn as SignInSchema
from .schemas import SignUp as SignUpSchema
from .schemas import Token as TokenSchema
from .schemas import UserProfile as UserProfileSchema


router = APIRouter()


@router.post('/sign_up')
async def sign_up(
    session: session_dep,
    data: SignUpSchema,
) -> TokenSchema:
    result = await services.sign_up(
        session,
        data,
    )

    return result  # type: ignore[return-value]


@router.post('/sign_in')
async def sign_in(
    session: session_dep,
    data: SignInSchema,
) -> TokenSchema:
    result = await services.sign_in(
        session,
        data,
    )

    return result  # type: ignore[return-value]


security = HTTPBearer()


@router.post('/refresh')
async def refresh(
    current_user: current_user_refresh_dep,
    session: session_dep,
) -> TokenSchema:
    result = await services.refresh(
        session,
        current_user.id,
    )

    return result  # type: ignore[return-value]


@router.get('')
async def get_current_user(
    current_user: current_user_access_dep,
) -> UserProfileSchema:
    return current_user  # type: ignore[return-value]
