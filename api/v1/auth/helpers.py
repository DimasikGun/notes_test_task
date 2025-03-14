from datetime import timedelta

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.controllers import create_user, get_user, get_user_by_username
from api.v1.auth.exceptions import (
    invalid_token_exc,
    unauthed_exc,
    user_not_found_exc,
    username_taken_exc,
)
from api.v1.auth.schemas import UserSchema
from api.v1.auth.security_utils import (
    decode_jwt,
    encode_jwt,
    hash_password,
    validate_password,
)
from core.config import settings
from core.database import User
from core.database.db_helper import db_helper

http_bearer = HTTPBearer()


async def validate_auth_user(
    user_in: UserSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    user = await get_user_by_username(session, user_in.username)
    if not user:
        raise user_not_found_exc
    if not validate_password(user_in.password, user.password):
        raise unauthed_exc
    return user


async def create_auth_user(
    user_in: UserSchema, session: AsyncSession = Depends(db_helper.session_getter)
) -> User:
    user_in.password = hash_password(user_in.password)
    try:
        user = await create_user(session, user_in)
    except IntegrityError:
        raise username_taken_exc
    return user


async def create_jwt_token(
    token_type: str, token_data: dict, expire_timedelta: timedelta = None
) -> str:
    payload = {settings.jwt.TOKEN_TYPE_FIELD: token_type}
    payload.update(token_data)
    token = encode_jwt(payload, expire_timedelta=expire_timedelta)
    return token


async def create_access_token(user: User) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "username": user.username,
    }
    access_token = await create_jwt_token(settings.jwt.ACCESS_TOKEN_TYPE, jwt_payload)
    return access_token


async def create_refresh_token(user: User) -> str:
    jwt_payload = {"sub": str(user.id)}
    access_token = await create_jwt_token(
        settings.jwt.REFRESH_TOKEN_TYPE,
        jwt_payload,
        expire_timedelta=timedelta(days=settings.jwt.refresh_token_expires_days),
    )
    return access_token


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise invalid_token_exc
    return payload


async def get_user_by_jwt_sub(
    payload: dict, session: AsyncSession = Depends(db_helper.session_getter)
) -> User:
    user = await get_user(session, int(payload.get("sub")))
    if not user:
        raise user_not_found_exc
    return user


async def get_current_user_by_access_token(
    payload: dict = Depends(get_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    if payload.get(settings.jwt.TOKEN_TYPE_FIELD) != settings.jwt.ACCESS_TOKEN_TYPE:
        raise invalid_token_exc
    return await get_user_by_jwt_sub(payload, session)


async def get_current_user_by_refresh_token(
    payload: dict = Depends(get_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    if payload.get(settings.jwt.TOKEN_TYPE_FIELD) != settings.jwt.REFRESH_TOKEN_TYPE:
        raise invalid_token_exc
    return await get_user_by_jwt_sub(payload, session)
