from fastapi import APIRouter, Depends, status
from pydantic import TypeAdapter

from api.v1.notes.exceptions import note_not_found_exc
from api.v1.notes.helpers import (
    create_note_with_jwt,
    delete_users_note_with_jwt,
    get_all_users_notes_with_jwt,
    get_single_users_note_with_jwt,
    get_users_note_history_with_jwt,
    update_users_note_with_jwt,
)
from api.v1.notes.schemas import NoteSchema, NoteSchemaWithHistory
from core.database import Note

router = APIRouter(tags=["notes"], prefix="/notes")


@router.get("/", response_model=list[NoteSchema])
async def get_users_notes(
    notes: list[Note] = Depends(get_all_users_notes_with_jwt),
):
    ta = TypeAdapter(list[NoteSchema])
    return ta.validate_python(notes, from_attributes=True)


@router.post("/", response_model=NoteSchema, status_code=status.HTTP_201_CREATED)
async def create_note(note: Note = Depends(create_note_with_jwt)):
    return NoteSchema.model_validate(note, from_attributes=True)


@router.get("/{note_id}", response_model=NoteSchema)
async def get_user_single_note(note: Note = Depends(get_single_users_note_with_jwt)):
    return NoteSchema.model_validate(note, from_attributes=True)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_note(
    note_delete_status: bool = Depends(delete_users_note_with_jwt),
):
    if not note_delete_status:
        raise note_not_found_exc


@router.patch("/{note_id}", response_model=NoteSchema)
async def update_users_note(upd_note=Depends(update_users_note_with_jwt)):
    return NoteSchema.model_validate(upd_note, from_attributes=True)


@router.get("/history/{note_id}", response_model=NoteSchemaWithHistory)
async def get_users_note_history(
    note_with_history: Note = Depends(get_users_note_history_with_jwt),
):
    return NoteSchemaWithHistory.model_validate(note_with_history, from_attributes=True)
