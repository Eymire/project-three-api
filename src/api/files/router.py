from fastapi import APIRouter, Path, UploadFile, status
from fastapi.responses import FileResponse

from src.dependencies import current_user_access_dep, current_user_access_optional_dep, session_dep
from src.schemas.files import FileOut as FileOutSchema
from src.schemas.files import FileUpdate as FileUpdateSchema

from . import services


router = APIRouter()


@router.get('')
async def get_files(
    current_user: current_user_access_dep,
    session: session_dep,
) -> list[FileOutSchema]:
    result = await services.get_files(
        session,
        current_user.id,
    )

    return result  # type: ignore[return-value]


@router.get(
    '/{id}',
    description='Authentication optional if the file is public.',
)
async def get_file(
    current_user: current_user_access_optional_dep,
    session: session_dep,
    file_id: int = Path(alias='id'),
) -> FileOutSchema:
    result = await services.get_file(
        session,
        file_id,
        current_user.id if current_user else None,
    )

    return result  # type: ignore[return-value]


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
)
async def add_file(
    current_user: current_user_access_dep,
    session: session_dep,
    file: UploadFile,
):
    await services.add_file(
        session,
        current_user,
        file,
    )


@router.get('/{id}/download')
async def download_file(
    current_user: current_user_access_optional_dep,
    session: session_dep,
    file_id: int = Path(alias='id'),
):
    result = await services.get_file(
        session,
        file_id,
        current_user.id if current_user else None,
    )
    response = FileResponse(
        f'./storage/{result.stored_name}',
        filename=result.name,
        media_type=result.content_type,
    )

    return response


@router.patch('/{id}')
async def update_file(
    current_user: current_user_access_dep,
    session: session_dep,
    data: FileUpdateSchema,
    file_id: int = Path(alias='id'),
):
    await services.update_file(
        session,
        current_user.id,
        file_id,
        data,
    )


@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_file(
    current_user: current_user_access_dep,
    session: session_dep,
    file_id: int = Path(alias='id'),
):
    await services.delete_file(
        session,
        current_user.id,
        file_id,
    )
