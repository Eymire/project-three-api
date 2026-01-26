from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    environment: Literal['development', 'production'] = 'development'


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    host: str
    name: str
    user: str
    password: str


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='JWT_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    access_token_lifetime_minutes: int
    refresh_token_lifetime_minutes: int


app_settings = AppSettings()  # type: ignore[call-arg]
db_settings = DBSettings()  # type: ignore[call-arg]
jwt_settings = JWTSettings()  # type: ignore[call-arg]
