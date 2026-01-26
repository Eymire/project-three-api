from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.enums import UserScope, UserSubscribePlan


class User(BaseModel):
    id: int
    name: str
    email: str
    subscribe_plan: UserSubscribePlan
    scope: UserScope
    password_hash: str
    used_storage: int
    created_at: datetime


class UserProfile(BaseModel):
    id: int
    name: str
    subscribe_plan: UserSubscribePlan
    email: EmailStr
    used_storage: int
    created_at: datetime
