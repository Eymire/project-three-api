from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import File as FileModel
from src.models import User as UserModel
from src.schemas.files import FileUpdate as FileUpdateSchema

from .utils import subscribe_plan_to_storage_limit


async def get_files(
    session: AsyncSession,
    user_id: int,
) -> Sequence[FileModel]:
    stmt = (
        select(FileModel).where(FileModel.user_id == user_id).order_by(FileModel.created_at.desc())
    )
    result = await session.execute(stmt)
    result = result.scalars().all()

    return result


async def get_file(
    session: AsyncSession,
    file_id: int,
    user_id: int | None,
) -> FileModel:
    stmt = select(FileModel).where(FileModel.id == file_id)
    result = await session.execute(stmt)
    result = result.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found.',
        )

    if result.visibility == 'private' and result.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this file.',
        )

    return result


async def add_file(
    session: AsyncSession,
    user: UserModel,
    file: UploadFile,
):
    if user.used_storage + file.size > subscribe_plan_to_storage_limit[user.subscribe_plan]:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Storage limit exceeded.',
        )

    stored_name = uuid4().hex
    storage_path = Path('storage') / stored_name

    try:
        async with aiofiles.open(storage_path, 'wb') as out_file:
            while content := await file.read(4 * 1024 * 1024):  # 4 MB
                await out_file.write(content)
    except Exception:
        storage_path.unlink(missing_ok=True)
        raise

    stmt = (
        update(UserModel)
        .where(UserModel.id == user.id)
        .values(used_storage=UserModel.used_storage + file.size)
    )
    await session.execute(stmt)

    stmt = insert(FileModel).values(
        user_id=user.id,
        name=file.filename,
        stored_name=stored_name,
        size=file.size,
        content_type=file.content_type,
    )
    await session.execute(stmt)
    await session.commit()


async def update_file(
    session: AsyncSession,
    user_id: int,
    file_id: int,
    data: FileUpdateSchema,
):
    stmt = select(FileModel).where(FileModel.id == file_id)
    result = await session.execute(stmt)
    result = result.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found.',
        )

    if result.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to update this file.',
        )

    if data.model_dump(exclude_unset=True):
        stmt = (
            update(FileModel)
            .where(FileModel.id == file_id)
            .values(**data.model_dump(exclude_unset=True))
        )
        await session.execute(stmt)
        await session.commit()


async def delete_file(
    session: AsyncSession,
    user_id: int,
    file_id: int,
):
    stmt = select(FileModel).where(FileModel.id == file_id)
    result = await session.execute(stmt)
    result = result.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found.',
        )

    if result.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to delete this file.',
        )

    storage_path = Path('storage') / result.stored_name
    storage_path.unlink(missing_ok=True)

    stmt = (
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(used_storage=UserModel.used_storage - result.size)
    )
    await session.execute(stmt)

    stmt = delete(FileModel).where(FileModel.id == file_id)
    await session.execute(stmt)
    await session.commit()
