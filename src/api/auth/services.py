from fastapi import HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.dependencies import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_password,
)
from src.models import UserModel

from .schemas import UserSignInSchema, UserSignUpSchema


async def sign_up(
    session: AsyncSession,
    data: UserSignUpSchema,
):
    stmt = (
        insert(UserModel)
        .values(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        .returning(UserModel)
    )
    result = await session.execute(stmt)
    result = result.scalar()
    await session.commit()

    return result


async def sign_in(
    session: AsyncSession,
    data: UserSignInSchema,
):
    stmt = select(UserModel).where(UserModel.email == data.email)
    result = await session.execute(stmt)
    result = result.scalar()

    if (not result) or (not validate_password(data.password, result.hashed_password)):
        raise HTTPException(
            status_code=401,
            detail='Invalid name or password.',
        )

    access_token, access_token_expires_at = create_access_token(result.id)
    refresh_token, refresh_token_expires_at = create_refresh_token(result.id)

    return {
        'access_token': access_token,
        'access_token_expires_at': access_token_expires_at,
        'refresh_token': refresh_token,
        'refresh_token_expires_at': refresh_token_expires_at,
    }


async def refresh_sign_in(user_id: int):
    access_token, access_token_expires_at = create_access_token(user_id)
    refresh_token, refresh_token_expires_at = create_refresh_token(user_id)

    return {
        'access_token': access_token,
        'access_token_expires_at': access_token_expires_at,
        'refresh_token': refresh_token,
        'refresh_token_expires_at': refresh_token_expires_at,
    }
