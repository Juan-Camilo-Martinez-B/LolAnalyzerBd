"""add account recovery, lockout and riot link identifiers

Revision ID: 0004_auth_recovery_and_riot_link
Revises: 0003_add_views_and_triggers
Create Date: 2026-09-29 22:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_auth_recovery_and_riot_link"
down_revision: Union[str, None] = "0003_add_views_and_triggers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    timestamp = sa.DateTime(timezone=True)

    additions = {
        "session_version": sa.Column("session_version", sa.Integer(), nullable=False, server_default="1"),
        "failed_login_count": sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
        "locked_until": sa.Column("locked_until", timestamp, nullable=True),
        "riot_puuid": sa.Column("riot_puuid", sa.String(length=80), nullable=True),
        "riot_game_name": sa.Column("riot_game_name", sa.String(length=100), nullable=True),
        "riot_tag_line": sa.Column("riot_tag_line", sa.String(length=20), nullable=True),
    }
    for name, column in additions.items():
        if name not in user_columns:
            op.add_column("users", column)

    index_names = {index["name"] for index in inspector.get_indexes("users")}
    if "uq_users_riot_puuid" not in index_names:
        op.create_index("uq_users_riot_puuid", "users", ["riot_puuid"], unique=True)

    tables = set(inspector.get_table_names())
    if "security_answers" not in tables:
        op.create_table(
            "security_answers",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("favorite_champion_hash", sa.String(length=255), nullable=False),
            sa.Column("peak_elo_hash", sa.String(length=255), nullable=False),
            sa.Column("first_main_hash", sa.String(length=255), nullable=False),
            sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("locked_until", timestamp, nullable=True),
            sa.Column("updated_at", timestamp, server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("user_id"),
        )
    if "auth_attempts" not in tables:
        op.create_table(
            "auth_attempts",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("subject_hash", sa.String(length=64), nullable=False),
            sa.Column("purpose", sa.String(length=32), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("window_started", timestamp, server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("locked_until", timestamp, nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("subject_hash", "purpose", name="uq_auth_attempt_subject"),
        )
    if "riot_cache" not in tables:
        op.create_table(
            "riot_cache",
            sa.Column("cache_key", sa.String(length=255), nullable=False),
            sa.Column("payload", sa.Text(), nullable=False),
            sa.Column("expires_at", timestamp, nullable=False),
            sa.PrimaryKeyConstraint("cache_key"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "riot_cache" in tables:
        op.drop_table("riot_cache")
    if "auth_attempts" in tables:
        op.drop_table("auth_attempts")
    if "security_answers" in tables:
        op.drop_table("security_answers")
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    for name in (
        "riot_tag_line",
        "riot_game_name",
        "riot_puuid",
        "locked_until",
        "failed_login_count",
        "session_version",
    ):
        if name in user_columns:
            op.drop_column("users", name)
