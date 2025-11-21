from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserSignUpSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserSignInSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
    token_type: str = 'Bearer'
