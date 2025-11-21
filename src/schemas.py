from datetime import datetime

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: bytes
    created_at: datetime


class UserShowSchema(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
