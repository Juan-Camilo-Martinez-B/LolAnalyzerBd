"""store one post-match analysis per user and game

Revision ID: 0008_match_analyses
Revises: 0007_local_match_history
Create Date: 2026-11-07 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_match_analyses"
down_revision: Union[str, None] = "0007_local_match_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "match_analyses" in set(inspector.get_table_names()):
        return
    op.create_table(
        "match_analyses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("external_match_id", sa.String(length=40), nullable=False),
        sa.Column("champion_name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="UNKNOWN"),
        sa.Column("win", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metrics_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("strengths", sa.String(length=300), nullable=False),
        sa.Column("improvements", sa.String(length=300), nullable=False),
        sa.Column("focus", sa.String(length=300), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="rules"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "external_match_id", name="uq_match_analysis_user_game"),
    )
    op.create_index("ix_match_analyses_user_created", "match_analyses", ["user_id", "created_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "match_analyses" not in set(inspector.get_table_names()):
        return
    op.drop_index("ix_match_analyses_user_created", table_name="match_analyses")
    op.drop_table("match_analyses")
