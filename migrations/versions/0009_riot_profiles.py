"""several League profiles per analyzer account

A LolAnalyzer account is not tied to one League account: each stored game
keeps the puuid it was played with, the profiles seen in the client are
listed per account, and one Riot ID can be linked to several accounts.

Revision ID: 0009_riot_profiles
Revises: 0008_match_analyses
Create Date: 2026-11-08 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_riot_profiles"
down_revision: Union[str, None] = "0008_match_analyses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    history_columns = {column["name"] for column in inspector.get_columns("local_match_history")}
    if "riot_puuid" not in history_columns:
        op.add_column("local_match_history", sa.Column("riot_puuid", sa.String(length=80), nullable=True))
        op.create_index("ix_local_match_user_puuid", "local_match_history", ["user_id", "riot_puuid"])
        # Games stored before this change belong to the Riot ID linked at the time.
        op.execute(
            "UPDATE local_match_history SET riot_puuid = "
            "(SELECT riot_puuid FROM users WHERE users.id = local_match_history.user_id) "
            "WHERE riot_puuid IS NULL"
        )

    if "riot_profiles" not in tables:
        op.create_table(
            "riot_profiles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("puuid", sa.String(length=80), nullable=False),
            sa.Column("game_name", sa.String(length=100), nullable=True),
            sa.Column("tag_line", sa.String(length=20), nullable=True),
            sa.Column("profile_icon_id", sa.Integer(), nullable=True),
            sa.Column("summoner_level", sa.Integer(), nullable=True),
            sa.Column("ranked_solo_json", sa.Text(), nullable=True),
            sa.Column(
                "last_seen_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "puuid", name="uq_riot_profile_user_puuid"),
        )
        op.create_index("ix_riot_profiles_user_seen", "riot_profiles", ["user_id", "last_seen_at"])

    # One Riot ID can now be linked to several analyzer accounts.
    user_indexes = {index["name"] for index in inspector.get_indexes("users")}
    user_uniques = {constraint["name"] for constraint in inspector.get_unique_constraints("users")}
    if "uq_users_riot_puuid" in user_uniques:
        op.drop_constraint("uq_users_riot_puuid", "users", type_="unique")
    elif "uq_users_riot_puuid" in user_indexes:
        op.drop_index("uq_users_riot_puuid", table_name="users")
    if "ix_users_riot_puuid" not in user_indexes:
        op.create_index("ix_users_riot_puuid", "users", ["riot_puuid"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_riot_puuid" in user_indexes:
        op.drop_index("ix_users_riot_puuid", table_name="users")
    # Restoring uniqueness fails if two accounts share a Riot ID; unlink one first.
    op.create_index("uq_users_riot_puuid", "users", ["riot_puuid"], unique=True)

    if "riot_profiles" in set(inspector.get_table_names()):
        op.drop_index("ix_riot_profiles_user_seen", table_name="riot_profiles")
        op.drop_table("riot_profiles")

    history_columns = {column["name"] for column in inspector.get_columns("local_match_history")}
    if "riot_puuid" in history_columns:
        op.drop_index("ix_local_match_user_puuid", table_name="local_match_history")
        with op.batch_alter_table("local_match_history") as batch:
            batch.drop_column("riot_puuid")
