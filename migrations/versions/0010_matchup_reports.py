"""keep the lane plans each player received

Revision ID: 0010_matchup_reports
Revises: 0009_riot_profiles
Create Date: 2026-11-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010_matchup_reports"
down_revision: Union[str, None] = "0009_riot_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if "matchup_reports" in set(sa.inspect(bind).get_table_names()):
        return
    op.create_table(
        "matchup_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("champion", sa.String(length=40), nullable=False),
        sa.Column("opponent", sa.String(length=40), nullable=False),
        sa.Column("lane", sa.String(length=12), nullable=False),
        sa.Column("plan_lane", sa.String(length=400), nullable=False),
        sa.Column("plan_fight", sa.String(length=400), nullable=False),
        sa.Column("plan_avoid", sa.String(length=400), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="rules"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "champion", "opponent", "lane", name="uq_matchup_report_user_matchup"),
    )
    op.create_index("ix_matchup_reports_user_updated", "matchup_reports", ["user_id", "updated_at"])


def downgrade() -> None:
    bind = op.get_bind()
    if "matchup_reports" not in set(sa.inspect(bind).get_table_names()):
        return
    op.drop_index("ix_matchup_reports_user_updated", table_name="matchup_reports")
    op.drop_table("matchup_reports")
