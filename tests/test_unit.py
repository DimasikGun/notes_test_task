import time
from datetime import timedelta

import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.controllers import create_user, get_user
from api.v1.auth.schemas import UserSchema
from api.v1.auth.security_utils import (
    decode_jwt,
    encode_jwt,
    hash_password,
    validate_password,
)
from core.utils.case_convertor import camel_case_to_snake_case


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("SomeSDK", "some_sdk"),
        ("RServoDrive", "r_servo_drive"),
        ("SDKDemo", "sdk_demo"),
        ("CamelCase", "camel_case"),
        ("SimpleTest", "simple_test"),
        ("ABC", "abc"),
        ("Test123", "test123"),
        ("", ""),
    ],
)
def test_camel_case_to_snake_case(input_str, expected):
    assert camel_case_to_snake_case(input_str) == expected


def test_encode_decode_jwt(payload: dict[str, str]):
    token = encode_jwt(payload)

    decoded_payload = decode_jwt(token)

    assert decoded_payload["sub"] == "user123"
    assert "exp" in decoded_payload
    assert "iat" in decoded_payload
    assert "jti" in decoded_payload


def test_jwt_expiration(payload: dict[str, str]):
    token = encode_jwt(payload, expire_timedelta=timedelta(seconds=2))

    decoded_payload = decode_jwt(token)
    assert "exp" in decoded_payload

    time.sleep(3)

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_jwt(token)


def test_hash_password(password: str):
    hashed = hash_password(password)

    assert hashed != password
    assert validate_password(password, hashed)


def test_validate_password(password: str):
    hashed = hash_password(password)
    wrong_password = "WrongPassword123!"

    assert not validate_password(wrong_password, hashed)


@pytest.mark.asyncio
async def test_create_and_get_user(
    db_session: AsyncSession, user_schema_in: UserSchema
):
    user_created = await create_user(db_session, user_schema_in)

    assert user_created is not None
    assert user_created.username == user_schema_in.username

    user_get = await get_user(db_session, user_created.id)

    assert user_get is not None
    assert user_get.username == user_get.username
