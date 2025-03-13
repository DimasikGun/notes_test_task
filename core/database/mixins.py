from datetime import datetime, UTC

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class BaseNotesMixin:
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(UTC), server_default=func.now()
    )
