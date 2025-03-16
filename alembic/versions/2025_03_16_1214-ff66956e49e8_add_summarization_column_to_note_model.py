"""add 'summarization' column to note model

Revision ID: ff66956e49e8
Revises: 82cbbb810c81
Create Date: 2025-03-16 12:14:08.173697

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "ff66956e49e8"
down_revision: Union[str, None] = "82cbbb810c81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("note", sa.Column("summarization", sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("note", "summarization")
