from fastapi import APIRouter, Path, Query

from src.dependencies import session_dep
from src.schemas import UserShowSchema

from . import services


router = APIRouter()


@router.get('/{id}')
async def get_user(
    session: session_dep,
    user_id: int = Path(alias='id'),
) -> UserShowSchema:
    result = await services.get_user(
        session,
        user_id,
    )

    return result


@router.get('')
async def get_users(
    session: session_dep,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, le=100),
) -> list[UserShowSchema]:
    result = await services.get_users(
        session,
        offset,
        limit,
    )

    return result  # type: ignore
