from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.dependencies import get_current_user_from_token_type
from src.database import get_session
from src.schemas import UserSchema


session_dep = Annotated[AsyncSession, Depends(get_session)]
current_user_from_access_dep = Annotated[
    UserSchema, Depends(get_current_user_from_token_type('access'))
]
current_user_from_refresh_dep = Annotated[
    UserSchema, Depends(get_current_user_from_token_type('refresh'))
]
