from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.helpers import get_current_user_by_access_token
from api.v1.notes.controllers import (
    create_note,
    delete_note,
    get_note,
    get_note_with_history,
    get_user_notes,
    update_note_and_create_history,
)
from api.v1.notes.exceptions import invalid_upd_found_exc, note_not_found_exc
from api.v1.notes.schemas import CreateNoteSchema, NoteSchema, UpdateNoteSchema
from core.database import Note, User
from core.database.db_helper import db_helper


async def create_note_with_jwt(
    note_in: CreateNoteSchema,
    user: User = Depends(get_current_user_by_access_token),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Note:
    note = await create_note(session, note_in, user.id)
    return note


async def get_all_users_notes_with_jwt(
    user: User = Depends(get_current_user_by_access_token),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> list[Note]:
    notes = await get_user_notes(session, user.id)
    return notes


async def get_single_users_note_with_jwt(
    note_id: int,
    user: User = Depends(get_current_user_by_access_token),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Note:
    note = await get_note(session, note_id, user.id)
    if not note:
        raise note_not_found_exc
    return note


async def delete_users_note_with_jwt(
    note_id: int,
    user: User = Depends(get_current_user_by_access_token),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> bool:
    status = await delete_note(session, note_id, user.id)
    return status


async def update_users_note_with_jwt(
    note_id: int,
    note_in: UpdateNoteSchema,
    user: User = Depends(get_current_user_by_access_token),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Note:
    note = await get_note(session, note_id, user.id)
    if not note:
        raise note_not_found_exc
    old_note = NoteSchema.model_validate(note, from_attributes=True)
    if not (note_in.title and note_in.text):
        raise invalid_upd_found_exc
    if note_in.title == old_note.title and note_in.text == old_note.text:
        raise invalid_upd_found_exc
    note = await update_note_and_create_history(session, note, note_in, old_note)
    return note


async def get_users_note_history_with_jwt(
    note_id: int,
    user: User = Depends(get_current_user_by_access_token),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Note:
    note_with_history = await get_note_with_history(session, note_id, user.id)
    if not note_with_history:
        raise note_not_found_exc
    return note_with_history
