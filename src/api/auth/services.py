from fastapi import HTTPException, status
from sqlalchemy import insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User as UserModel

from .dependencies import create_access_token, create_refresh_token, hash_password, verify_password
from .schemas import SignIn as SignInSchema
from .schemas import SignUp as SignUpSchema


async def sign_up(
    session: AsyncSession,
    data: SignUpSchema,
) -> dict:
    stmt = select(UserModel).where(
        or_(
            UserModel.name == data.name,
            UserModel.email == data.email,
        )
    )
    result = await session.execute(stmt)
    result = result.scalar_one_or_none()

    if result:
        conflict_field = 'name' if result.name == data.name else 'email'

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User with this {conflict_field} already exists.',
        )

    stmt = (
        insert(UserModel)
        .values(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        .returning(UserModel.id)
    )
    result = await session.execute(stmt)
    result = result.scalar_one()
    await session.commit()

    return {
        'access_token': create_access_token(result),
        'refresh_token': create_refresh_token(result),
    }


async def sign_in(
    session: AsyncSession,
    data: SignInSchema,
) -> dict:
    stmt = select(UserModel).where(UserModel.name == data.name)
    result = await session.execute(stmt)
    result = result.scalar_one_or_none()

    if not result or not verify_password(data.password, result.password_hash):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found.',
        )

    return {
        'access_token': create_access_token(result.id),
        'refresh_token': create_refresh_token(result.id),
    }


async def refresh(
    user_id: int,
) -> dict:
    return {
        'access_token': create_access_token(user_id),
        'refresh_token': create_refresh_token(user_id),
    }
