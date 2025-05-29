from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(data: dict, secret: str, expiry: timedelta, algorithm: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expiry
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm)


def decode_token(token: str, secret: str, algorithm: str):
    try:
        return jwt.decode(token, secret, algorithm)
    except JWTError:
        return None
