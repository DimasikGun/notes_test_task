import time
from datetime import timedelta

import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils import validation_error
from api.v1.auth.controllers import create_user, get_user, get_user_by_username
from api.v1.auth.schemas import UserSchema
from api.v1.auth.security_utils import (
    decode_jwt,
    encode_jwt,
    hash_password,
    validate_password,
)
from api.v1.notes.controllers import (
    create_note,
    delete_note,
    get_note,
    get_note_history,
    get_user_notes,
    update_note_and_create_history,
)
from api.v1.notes.schemas import CreateNoteSchema, NoteSchema, UpdateNoteSchema
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

    user_get_by_username = await get_user_by_username(db_session, user_created.username)

    assert user_get_by_username is not None
    assert user_get_by_username.id == user_created.id


def test_validation_error():
    loc = ["field"]
    msg = "Invalid value"
    input_value = "wrong_input"
    reason = "Must be a positive integer"
    expected = {
        "detail": [
            {
                "type": "value_error",
                "loc": loc,
                "msg": msg,
                "input": input_value,
                "ctx": {"reason": reason},
            }
        ]
    }
    assert validation_error(loc, msg, input_value, reason) == expected


@pytest.mark.asyncio
async def test_create_and_get_note(db_session: AsyncSession):
    user_schema_in = UserSchema(username="user_note", password="StrongTestPassword123!")
    user = await create_user(db_session, user_schema_in)
    note_data = CreateNoteSchema(title="Test Note", text="This is a test note")
    note_created = await create_note(db_session, note_data, user.id)

    assert note_created is not None
    assert note_created.title == note_data.title
    assert note_created.user_id == user.id

    note_fetched = await get_note(
        db_session, note_created.id, user.id
    )  # Передаем user_id
    assert note_fetched is not None
    assert note_fetched.id == note_created.id
    assert note_fetched.title == note_created.title


@pytest.mark.asyncio
async def test_get_user_notes(db_session: AsyncSession):
    user_schema_in = UserSchema(
        username="user_note2", password="StrongTestPassword123!"
    )
    user = await create_user(db_session, user_schema_in)
    note_data_1 = CreateNoteSchema(title="Note 1", text="First note")
    note_data_2 = CreateNoteSchema(title="Note 2", text="Second note")
    await create_note(db_session, note_data_1, user.id)
    await create_note(db_session, note_data_2, user.id)

    notes = await get_user_notes(db_session, user.id)
    assert len(notes) == 2
    assert notes[0].title == "Note 2"


@pytest.mark.asyncio
async def test_create_and_get_note_history(db_session: AsyncSession):
    user_schema_in = UserSchema(
        username="user_note3", password="StrongTestPassword123!"
    )
    user = await create_user(db_session, user_schema_in)
    note_data = CreateNoteSchema(title="Original Note", text="Content")
    note = await create_note(db_session, note_data, user.id)
    old_note = NoteSchema.model_validate(note, from_attributes=True)
    new_data = UpdateNoteSchema(title="Updated Note", text="Updated content")
    note_with_history = await update_note_and_create_history(
        db_session, note, new_data, old_note
    )

    assert note_with_history is not None
    assert note_with_history.title == "Updated Note"
    assert note_with_history.text == "Updated content"
    assert note_with_history.user_id == user.id

    history_entries = await get_note_history(db_session, note.id)
    assert len(history_entries) == 1
    history_entry = history_entries[0]

    assert history_entry.title == "Original Note"
    assert history_entry.text == "Content"
    assert history_entry.note_id == note.id
    assert history_entry.created_at is not None


@pytest.mark.asyncio
async def test_update_note(db_session: AsyncSession):
    user_schema_in = UserSchema(
        username="user_note4", password="StrongTestPassword123!"
    )
    user = await create_user(db_session, user_schema_in)
    note_data = CreateNoteSchema(title="Initial Title", text="Initial content")
    note = await create_note(db_session, note_data, user.id)
    old_note = NoteSchema.model_validate(note, from_attributes=True)
    update_data = UpdateNoteSchema(title="Updated Title", text="Updated content")
    updated_note = await update_note_and_create_history(
        db_session, note, update_data, old_note
    )

    assert updated_note is not None
    assert updated_note.title == update_data.title
    assert updated_note.text == update_data.text


@pytest.mark.asyncio
async def test_delete_note(db_session: AsyncSession):
    user_schema_in = UserSchema(
        username="user_note5", password="StrongTestPassword123!"
    )
    user = await create_user(db_session, user_schema_in)
    note_data = CreateNoteSchema(title="Note to delete", text="This will be deleted")
    note = await create_note(db_session, note_data, user.id)

    delete_result = await delete_note(db_session, note.id, user.id)
    assert delete_result is True

    deleted_note = await get_note(db_session, note.id, user.id)
    assert deleted_note is None
