from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.database.mixins import BaseNotesMixin

if TYPE_CHECKING:
    from .user import User
    from .notes_history import NoteHistory


class Note(BaseNotesMixin, Base):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(UTC), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notes")
    note_history: Mapped[list["NoteHistory"]] = relationship(
        "NoteHistory", back_populates="note", order_by="NoteHistory.created_at"
    )
