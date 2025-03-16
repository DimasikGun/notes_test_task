from datetime import datetime

from pydantic import BaseModel, Field


class CreateNoteSchema(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    text: str


class UpdateNoteSchema(BaseModel):
    title: str | None = Field(min_length=3, max_length=150, default=None)
    text: str | None = None


class NoteSchema(CreateNoteSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    summarization: str
    user_id: int


class NoteHistorySchema(CreateNoteSchema):
    id: int
    created_at: datetime
    note_id: int


class NoteSchemaWithHistory(NoteSchema):
    note_history: list[NoteHistorySchema]
