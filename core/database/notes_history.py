from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.database.mixins import BaseNotesMixin

if TYPE_CHECKING:
    from .note import Note


class NoteHistory(BaseNotesMixin, Base):
    note_id: Mapped[int] = mapped_column(
        ForeignKey("note.id", ondelete="CASCADE"), nullable=False
    )

    note: Mapped["Note"] = relationship("Note", back_populates="note_history")
