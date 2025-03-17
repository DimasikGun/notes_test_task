from fastapi import APIRouter, Depends
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.analytics.controllers import get_all_notes
from api.v1.analytics.helpers import get_analytics
from api.v1.analytics.schemas import AnalyticsSchema
from api.v1.notes.schemas import NoteSchema
from core.database.db_helper import db_helper

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsSchema)
async def get_analytics_of_all_notes(
    analytics: AnalyticsSchema = Depends(get_analytics),
):
    return analytics


@router.get("/notes", response_model=list[NoteSchema])
async def get_all_notes_without_auth(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    ta = TypeAdapter(list[NoteSchema])
    notes = await get_all_notes(session)
    return ta.validate_python(notes, from_attributes=True)
