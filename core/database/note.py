from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.database.mixins import BaseNotesMixin

if TYPE_CHECKING:
    from .notes_history import NoteHistory
    from .user import User


class Note(BaseNotesMixin, Base):
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    summarization: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="notes")
    note_history: Mapped[list["NoteHistory"]] = relationship(
        "NoteHistory",
        back_populates="note",
        cascade="all, delete-orphan",
        order_by="NoteHistory.created_at.desc()",
    )
