from pydantic import BaseModel, EmailStr, Field


class SignIn(BaseModel):
    name: str = Field(min_length=4, max_length=32)
    password: str = Field(min_length=8)


class SignUp(BaseModel):
    name: str = Field(min_length=4, max_length=32)
    email: EmailStr
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'
