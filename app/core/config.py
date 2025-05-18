import os


POSTGRES_URL: str = str(object=os.getenv(key="POSTGRES_URL"))
MONGO_URL: str = str(object=os.getenv(key="MONGO_URL"))
MONGO_DATABASE_NAME: str = str(object=os.getenv(key="MONGO_DATABASE_NAME"))
REDIS_HOST: str = str(object=os.getenv(key="REDIS_HOST"))
REDIS_PORT: str = str(object=os.getenv(key="REDIS_PORT"))
REDIS_USERNAME: str = str(object=os.getenv(key="REDIS_USERNAME"))
REDIS_PASSWORD: str = str(object=os.getenv(key="REDIS_PASSWORD"))
SMTP_PORT: str = str(object=os.getenv(key="SMTP_PORT"))
SMTP_USERNAME: str = str(object=os.getenv(key="SMTP_USERNAME"))
SMTP_PASSWORD: str = str(object=os.getenv(key="SMTP_PASSWORD"))
# TWILIO_ACCOUNT_SID: str
# TWILIO_AUTH_TOKEN: str
# TWILIO_PHONE_NUMBER: str
# OTP_EXPIRY_SECONDS: int = 300
# JWT_SECRET_KEY: str
# JWT_ALGORITHM: str = "HS256"
