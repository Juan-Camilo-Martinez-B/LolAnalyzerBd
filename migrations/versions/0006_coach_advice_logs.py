"""store coach advice on the account

Revision ID: 0006_coach_advice_logs
Revises: 0005_user_theme_preference
Create Date: 2026-10-09 02:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_coach_advice_logs"
down_revision: Union[str, None] = "0005_user_theme_preference"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "coach_advice_logs" in set(inspector.get_table_names()):
        return
    op.create_table(
        "coach_advice_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("advice_text", sa.String(length=240), nullable=False),
        sa.Column("trigger_type", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("champion_name", sa.String(length=40), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("game_time_seconds", sa.Float(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_coach_advice_logs_user_id", "coach_advice_logs", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "coach_advice_logs" not in set(inspector.get_table_names()):
        return
    op.drop_index("ix_coach_advice_logs_user_id", table_name="coach_advice_logs")
    op.drop_table("coach_advice_logs")
