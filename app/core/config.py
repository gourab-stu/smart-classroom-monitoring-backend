from datetime import timedelta
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings

from app.utilities.parser import parse_duration


class Settings(BaseSettings):
    POSTGRES_URI: str
    MONGO_URI: str
    MONGO_DATABASE_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    OTP_EXPIRY_SECONDS: int
    ACCESS_TOKEN_SECRET: str
    ACCESS_TOKEN_EXPIRY: timedelta
    REFRESH_TOKEN_SECRET: str
    REFRESH_TOKEN_EXPIRY: timedelta
    JWT_ALGORITHM: str

    @field_validator("REDIS_PORT", "SMTP_PORT", "OTP_EXPIRY_SECONDS", mode="before")
    def convert_to_int(cls, value: str) -> int:
        return int(value)

    @field_validator("ACCESS_TOKEN_EXPIRY", "REFRESH_TOKEN_EXPIRY", mode="before")
    def convert_to_timedelta(cls, value: str) -> timedelta:
        return parse_duration(value)

    class Config:
        env_file: str = f".env.{os.getenv('ENV', 'local')}"


settings = Settings()

__all__ = ["settings"]
