"""archive match summaries taken from the local League client

Revision ID: 0007_local_match_history
Revises: 0006_coach_advice_logs
Create Date: 2026-11-07 08:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_local_match_history"
down_revision: Union[str, None] = "0006_coach_advice_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "local_match_history" in set(inspector.get_table_names()):
        return
    op.create_table(
        "local_match_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("external_match_id", sa.String(length=40), nullable=False),
        sa.Column("champion_name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="UNKNOWN"),
        sa.Column("kills", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deaths", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("kda", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cs_per_min", sa.Float(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("win", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("queue_id", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("game_mode", sa.String(length=40), nullable=False, server_default="CLASSIC"),
        sa.Column("gold_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("vision_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("damage_dealt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("trinket_id", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("played_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="lcu"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "external_match_id", name="uq_local_match_user_game"),
    )
    op.create_index("ix_local_match_history_user_id", "local_match_history", ["user_id"])
    op.create_index(
        "ix_local_match_history_user_played",
        "local_match_history",
        ["user_id", "played_at"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "local_match_history" not in set(inspector.get_table_names()):
        return
    op.drop_index("ix_local_match_history_user_played", table_name="local_match_history")
    op.drop_index("ix_local_match_history_user_id", table_name="local_match_history")
    op.drop_table("local_match_history")
