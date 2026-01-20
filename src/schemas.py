from datetime import datetime

from pydantic import BaseModel

from src.enums import FileVisibility, UserScope


class User(BaseModel):
    id: int
    name: str
    email: str
    scope: UserScope
    password_hash: str
    created_at: datetime


class File(BaseModel):
    id: int
    user_id: int
    name: str
    stored_name: str
    size: int
    content_type: str
    visibility: FileVisibility
    created_at: datetime
