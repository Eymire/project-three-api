from datetime import datetime

from pydantic import BaseModel

from src.enums import FileVisibility


class FileOut(BaseModel):
    id: int
    user_id: int
    name: str
    size: int
    content_type: str
    visibility: FileVisibility
    created_at: datetime


class FileUpdate(BaseModel):
    name: str | None = None
    visibility: FileVisibility | None = None
