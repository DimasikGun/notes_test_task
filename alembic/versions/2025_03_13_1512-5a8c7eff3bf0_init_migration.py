"""init migration

Revision ID: 5a8c7eff3bf0
Revises:
Create Date: 2025-03-13 15:12:18.213215

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "5a8c7eff3bf0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("username", name=op.f("uq_user_username")),
    )
    op.create_table(
        "note",
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_note_user_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_note")),
    )
    op.create_table(
        "note_history",
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["note_id"], ["note.id"], name=op.f("fk_note_history_note_id_note")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_note_history")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("note_history")
    op.drop_table("note")
    op.drop_table("user")
