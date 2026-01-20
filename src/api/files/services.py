from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import File as FileModel
from src.models import User as UserModel

from .schemas import FileUpdate as FileUpdateSchema


async def get_files(
    session: AsyncSession,
    user_id: int,
) -> Sequence[FileModel]:
    stmt = select(FileModel).where(FileModel.user_id == user_id)
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
    stored_name = uuid4().hex

    stmt = insert(FileModel).values(
        user_id=user.id,
        name=file.filename,
        stored_name=stored_name,
        size=file.size,
        content_type=file.content_type,
    )
    await session.execute(stmt)

    try:
        async with aiofiles.open(f'./storage/{stored_name}', 'wb') as out_file:
            while content := await file.read(1024):
                await out_file.write(content)
    except Exception:
        await session.rollback()
        raise

    await session.commit()


async def update_file(
    session: AsyncSession,
    user_id: int,
    file_id: int,
    data: FileUpdateSchema,
):
    stmt = select(FileModel).where(FileModel.id == file_id)
    result = await session.execute(stmt)
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found.',
        )

    if file.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to update this file.',
        )

    stmt = (
        update(FileModel)
        .where(FileModel.id == file_id)
        .values(
            **data.model_dump(
                exclude_unset=True,
            )
        )
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
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='File not found.',
        )

    if file.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to delete this file.',
        )

    stmt = delete(FileModel).where(FileModel.id == file_id)
    await session.execute(stmt)

    storage_path = Path('storage') / file.stored_name

    try:
        storage_path.unlink(missing_ok=True)
    except Exception:
        await session.rollback()
        raise

    await session.commit()
