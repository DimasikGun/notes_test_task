from datetime import UTC, datetime

from sqlalchemy import Result, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.v1.notes.schemas import CreateNoteSchema, NoteSchema, UpdateNoteSchema
from core.database import Note, NoteHistory


async def get_note(session: AsyncSession, note_id: int, user_id: int) -> Note:
    stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    return await session.scalar(stmt)


async def get_user_notes(session: AsyncSession, user_id: int) -> list[Note]:
    stmt = select(Note).where(Note.user_id == user_id).order_by(Note.updated_at.desc())
    result: Result = await session.execute(stmt)
    notes = result.scalars().all()
    return list(notes)


async def create_note(
    session: AsyncSession, note_in: CreateNoteSchema, user_id: int, summarization: str
) -> Note:
    note_dict = note_in.model_dump(exclude_none=True)
    note_dict["user_id"] = user_id
    note_dict["summarization"] = summarization
    note = Note(**note_dict)
    session.add(note)
    await session.commit()
    return note


async def get_note_history(session: AsyncSession, note_id: int) -> list[NoteHistory]:
    stmt = (
        select(NoteHistory)
        .where(NoteHistory.note_id == note_id)
        .order_by(NoteHistory.created_at.desc())
    )
    result: Result = await session.execute(stmt)
    note_history = result.scalars().all()
    return list(note_history)


async def update_note_and_create_history(
    session: AsyncSession,
    note: Note,
    note_in: UpdateNoteSchema,
    old_note: NoteSchema,
    summarization: str,
) -> Note:
    now = datetime.now(UTC)
    update_data = note_in.model_dump(exclude_unset=True)
    await session.execute(
        update(Note)
        .where(Note.id == old_note.id)
        .values(**update_data, updated_at=now, summarization=summarization)
    )
    note_history = NoteHistory(
        created_at=now,
        title=old_note.title,
        text=old_note.text,
        note_id=old_note.id,
    )
    note.updated_at = now
    session.add(note_history)
    await session.commit()
    await session.refresh(note)

    return note


async def delete_note(session: AsyncSession, note_id: int, user_id: int) -> bool:
    stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    note = await session.scalar(stmt)
    if note:
        await session.delete(note)
        await session.commit()
        return True
    return False


async def get_note_with_history(
    session: AsyncSession, note_id: int, user_id: int
) -> Note | None:
    stmt = (
        select(Note)
        .where(Note.id == note_id, Note.user_id == user_id)
        .options(selectinload(Note.note_history))
    )
    return await session.scalar(stmt)
