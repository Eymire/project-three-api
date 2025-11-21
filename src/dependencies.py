from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session


session_dep = Annotated[AsyncSession, Depends(get_session)]
