from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Note


async def get_all_notes_for_analytics(
    session: AsyncSession,
) -> list[tuple[str, str]]:
    stmt = select(Note.title, Note.text).order_by(Note.id)
    result: Result = await session.execute(stmt)
    return result.all()


async def get_all_notes(session: AsyncSession) -> list[Note]:
    stmt = select(Note).order_by(Note.id)
    result: Result = await session.execute(stmt)
    notes = result.scalars().all()
    return list(notes)
