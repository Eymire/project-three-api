from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.dependencies import get_current_user_wrapper
from src.database import get_session
from src.models import User as UserModel


session_dep = Annotated[
    AsyncSession,
    Depends(get_session),
]
current_user_access_dep = Annotated[
    UserModel,
    Depends(get_current_user_wrapper('access', required=True)),
]
current_user_refresh_dep = Annotated[
    UserModel,
    Depends(get_current_user_wrapper('refresh', required=True)),
]
current_user_access_optional_dep = Annotated[
    UserModel | None,
    Depends(get_current_user_wrapper('access', required=False)),
]
