import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt.private_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
    expire_timedelta: timedelta | None = None,
    expire_minutes: int = settings.jwt.access_token_expires_minutes,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)

    if expire_timedelta:
        expire_time = now + expire_timedelta
    else:
        expire_time = now + timedelta(minutes=expire_minutes)
    jti = str(uuid.uuid4())
    to_encode.update(exp=expire_time, iat=now, jti=jti)

    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    jwt_token: str | bytes,
    public_key: str = settings.jwt.public_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
) -> dict:
    decoded = jwt.decode(jwt_token, public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    pwd_in_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_in_bytes, salt).decode()


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
