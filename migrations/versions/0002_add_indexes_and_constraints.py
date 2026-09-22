"""add performance indexes and constraints

Revision ID: 0002_add_indexes_and_constraints
Revises: 0001_create_initial_schema
Create Date: 2026-09-22 10:16:30.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = '0002_add_indexes_and_constraints'
down_revision: Union[str, None] = '0001_create_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users Indexes
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    op.create_index('idx_users_google_id', 'users', ['google_id'], unique=False)
    op.create_index('idx_users_summoner', 'users', ['summoner_name', 'region'], unique=False)

    # 2. Token Blacklist Indexes
    op.create_index('idx_token_blacklist_jti', 'token_blacklist', ['token_jti'], unique=False)
    op.create_index('idx_token_blacklist_expires', 'token_blacklist', ['expires_at'], unique=False)

    # 3. Match Records Indexes
    op.create_index('idx_matches_user_played', 'match_records', ['user_id', sa.text('played_at DESC')], unique=False)
    op.create_index('idx_matches_user_role', 'match_records', ['user_id', 'role'], unique=False)
    op.create_index('idx_matches_user_champion', 'match_records', ['user_id', 'champion_name'], unique=False)
    op.create_index('idx_matches_game_id', 'match_records', ['game_id'], unique=False)
    op.create_index('idx_matches_user_win', 'match_records', ['user_id', 'win'], unique=False)

    # 4. Telemetry Points Indexes
    op.create_index('idx_telemetry_match_timeline', 'match_telemetry_points', ['match_id', sa.text('game_time_seconds ASC')], unique=False)
    op.create_index('idx_telemetry_match_time', 'match_telemetry_points', ['match_id', 'game_time_seconds'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_telemetry_match_time', table_name='match_telemetry_points')
    op.drop_index('idx_telemetry_match_timeline', table_name='match_telemetry_points')
    op.drop_index('idx_matches_user_win', table_name='match_records')
    op.drop_index('idx_matches_game_id', table_name='match_records')
    op.drop_index('idx_matches_user_champion', table_name='match_records')
    op.drop_index('idx_matches_user_role', table_name='match_records')
    op.drop_index('idx_matches_user_played', table_name='match_records')
    op.drop_index('idx_token_blacklist_expires', table_name='token_blacklist')
    op.drop_index('idx_token_blacklist_jti', table_name='token_blacklist')
    op.drop_index('idx_users_summoner', table_name='users')
    op.drop_index('idx_users_google_id', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
