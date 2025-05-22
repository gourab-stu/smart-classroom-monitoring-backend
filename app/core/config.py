import os
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    POSTGRES_URI: str = ""
    MONGO_URI: str = ""
    MONGO_DATABASE_NAME: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: str = ""
    REDIS_USERNAME: str = ""
    REDIS_PASSWORD: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: str = ""
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    OTP_EXPIRY_SECONDS: int = 300
    # TWILIO_ACCOUNT_SID: str
    # TWILIO_AUTH_TOKEN: str
    # TWILIO_PHONE_NUMBER: str
    # JWT_SECRET_KEY: str
    # JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file: str = f".env.{'local' if os.getenv('ENV') == 'local' else 'development' if os.getenv('ENV') == 'development' else 'production'}"


settings = Settings()
