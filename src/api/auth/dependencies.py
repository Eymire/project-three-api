from collections.abc import Callable, Coroutine
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal, TypedDict

import jwt
from argon2 import PasswordHasher
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models import User as UserModel
from src.settings import jwt_settings


PASSWORD_HASHER = PasswordHasher(
    time_cost=2,
    memory_cost=19 * 1024,
    parallelism=1,
)


class JWTPayload(TypedDict):
    type: Literal['access', 'refresh']
    user_id: int
    expires_at: int


def hash_password(plain_password: str) -> str:
    return PASSWORD_HASHER.hash(plain_password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(
            stored_hash,
            plain_password,
        )
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
    }

    return create_jwt(
        'access',
        payload,
        timedelta(minutes=jwt_settings.access_token_lifetime_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
    }

    return create_jwt(
        'refresh',
        payload,
        timedelta(minutes=jwt_settings.refresh_token_lifetime_minutes),
    )


def create_jwt(
    token_type: Literal['access', 'refresh'],
    payload: dict,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(UTC)
    payload_copy = {
        'type': token_type,
        **payload,
        'expires_at': int((now + expires_delta).timestamp()),
    }

    return encode_jwt(payload_copy)


def encode_jwt(payload: dict) -> str:
    with open('./certificates/jwt-private.pem', encoding='utf-8') as key_file:
        private_key = key_file.read()

    return jwt.encode(payload, private_key, 'RS256')


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


security = HTTPBearer(auto_error=False)


def get_current_user_wrapper(
    token_type: str,
    required: bool,
) -> Callable[..., Coroutine[Any, Any, UserModel | None]]:
    async def get_current_user(
        session: Annotated[AsyncSession, Depends(get_session)],
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    ) -> UserModel | None:
        if not credentials:
            if required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Not authenticated.',
                )

            return None

        if credentials.scheme != 'Bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid authentication scheme.',
            )

        jwt_payload = decode_jwt(credentials.credentials)

        if not jwt_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token.',
            )

        if jwt_payload['type'] != token_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid token type.',
            )

        if jwt_payload['expires_at'] < int(datetime.now(UTC).timestamp()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has expired.',
            )

        stmt = select(UserModel).where(UserModel.id == jwt_payload['user_id'])
        result = await session.execute(stmt)
        result = result.scalar_one_or_none()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found.',
            )

        return result

    return get_current_user
