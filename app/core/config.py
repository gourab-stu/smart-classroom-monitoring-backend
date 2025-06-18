import os
from datetime import timedelta
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings

from app.utilities.parser import parse_duration


class Settings(BaseSettings):
    POSTGRES_URI: str = ""
    MONGO_URI: str = ""
    MONGO_DATABASE_NAME: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: int = 5379
    REDIS_USERNAME: str = ""
    REDIS_PASSWORD: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    OTP_EXPIRY_SECONDS: int = 500
    ACCESS_TOKEN_SECRET: str = ""
    ACCESS_TOKEN_EXPIRY: timedelta = timedelta(minutes=15)
    REFRESH_TOKEN_SECRET: str = ""
    REFRESH_TOKEN_EXPIRY: timedelta = timedelta(days=7)
    JWT_ALGORITHM: str = ""

    @field_validator("REDIS_PORT", "SMTP_PORT", "OTP_EXPIRY_SECONDS", mode="before")
    def convert_to_int(cls, value: str) -> int:
        return int(value)

    @field_validator("ACCESS_TOKEN_EXPIRY", "REFRESH_TOKEN_EXPIRY", mode="before")
    def convert_to_timedelta(cls, value: str) -> timedelta:
        return parse_duration(value)

    class Config:
        env_file = f".env.{os.getenv('ENV', 'local')}"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()
