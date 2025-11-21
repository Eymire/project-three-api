from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal, TypedDict

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models import UserModel
from src.schemas import UserSchema
from src.settings import JWT_ACCESS_LIFETIME_MINUTES, JWT_REFRESH_LIFETIME_DAYS


class JWTData(TypedDict):
    user_id: int


class JWTPayload(TypedDict):
    type: Literal['access', 'refresh']
    user_id: int
    exp: int


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    )


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed_password,
    )


def create_access_token(user_id: int) -> tuple[str, int]:
    jwt_data = JWTData(user_id=user_id)

    return encode_jwt(
        jwt_data,
        'access',
        timedelta(minutes=JWT_ACCESS_LIFETIME_MINUTES),
    )


def create_refresh_token(user_id: int) -> tuple[str, int]:
    jwt_data = JWTData(user_id=user_id)

    return encode_jwt(
        jwt_data,
        'refresh',
        timedelta(days=JWT_REFRESH_LIFETIME_DAYS),
    )


def encode_jwt(
    jwt_data: JWTData,
    token_type: Literal['access', 'refresh'],
    expire_timedelta: timedelta,
) -> tuple[str, int]:
    exp = int((datetime.now(UTC) + expire_timedelta).timestamp())

    data = {
        'type': token_type,
        **jwt_data,
        'exp': exp,
    }

    with open('./certificates/jwt-private.pem', encoding='utf-8') as key_file:
        private_key = key_file.read()

    return jwt.encode(data, private_key, 'RS256'), exp


def decode_jwt(token: str) -> JWTPayload | None:
    with open('./certificates/jwt-public.pem', encoding='utf-8') as key_file:
        public_key = key_file.read()

    try:
        data = jwt.decode(
            token,
            public_key,
            ['RS256'],
        )
    except Exception:
        return None

    return data


security = HTTPBearer()


def get_current_user_from_token_type(token_type: str):
    async def get_auth_user_from_token(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> UserSchema:
        if credentials.scheme != 'Bearer':
            raise HTTPException(
                status_code=403,
                detail='Invalid authentication scheme.',
            )

        jwt_data = decode_jwt(credentials.credentials)

        if not jwt_data:
            raise HTTPException(
                status_code=401,
                detail='Invalid token.',
            )

        if jwt_data['type'] != token_type:
            raise HTTPException(
                status_code=401,
                detail='Invalid token type.',
            )

        if jwt_data['exp'] < int(datetime.now(UTC).timestamp()):
            raise HTTPException(
                status_code=401,
                detail='Invalid token.',
            )

        stmt = select(UserModel).where(UserModel.id == jwt_data['user_id'])
        result = await session.execute(stmt)
        result = result.scalar_one_or_none()

        if not result:
            raise HTTPException(
                status_code=404,
                detail='User not found.',
            )

        return UserSchema.model_validate(result.to_dict())

    return get_auth_user_from_token
