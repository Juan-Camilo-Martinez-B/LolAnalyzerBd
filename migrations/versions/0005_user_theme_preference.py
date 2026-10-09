"""add the account theme preference

Revision ID: 0005_user_theme_preference
Revises: 0004_auth_recovery_and_riot_link
Create Date: 2026-10-08 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_user_theme_preference"
down_revision: Union[str, None] = "0004_auth_recovery_and_riot_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "theme_preference" not in columns:
        op.add_column(
            "users",
            sa.Column("theme_preference", sa.String(length=20), nullable=False, server_default="light"),
        )
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_theme_preference")
        op.create_check_constraint(
            "chk_users_theme_preference",
            "users",
            "theme_preference IN ('light', 'system', 'dark')",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_theme_preference")
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "theme_preference" in columns:
        op.drop_column("users", "theme_preference")
