from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserModel


async def get_user(
    session: AsyncSession,
    user_id: int,
):
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail='User not found.',
        )

    return user.to_dict()


async def get_users(
    session: AsyncSession,
    offset: int,
    limit: int,
):
    stmt = select(UserModel).offset(offset).limit(limit)
    result = await session.execute(stmt)
    users = result.scalars().all()

    return [user.to_dict() for user in users]
