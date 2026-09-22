"""create initial schema tables

Revision ID: 0001_create_initial_schema
Revises: 
Create Date: 2026-09-22 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = '0001_create_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('auth_provider', sa.String(length=50), server_default='local', nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('summoner_name', sa.String(length=100), nullable=True),
        sa.Column('summoner_icon_id', sa.Integer(), nullable=True),
        sa.Column('region', sa.String(length=20), server_default='la1', nullable=False),
        sa.Column('preferred_roles', sa.String(length=100), server_default='MID,TOP', nullable=False),
        sa.Column('coach_sensitivity', sa.String(length=20), server_default='normal', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('google_id', name='uq_users_google_id'),
        sa.CheckConstraint("auth_provider IN ('local', 'google', 'both')", name='chk_users_auth_provider'),
        sa.CheckConstraint("coach_sensitivity IN ('low', 'normal', 'high')", name='chk_users_coach_sensitivity')
    )

    # 2. token_blacklist table
    op.create_table(
        'token_blacklist',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('token_jti', sa.String(length=255), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_jti', name='uq_token_blacklist_jti')
    )

    # 3. match_records table
    op.create_table(
        'match_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.BigInteger(), nullable=True),
        sa.Column('champion_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('kills', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deaths', sa.Integer(), server_default='0', nullable=False),
        sa.Column('assists', sa.Integer(), server_default='0', nullable=False),
        sa.Column('cs', sa.Integer(), server_default='0', nullable=False),
        sa.Column('gold_earned', sa.Integer(), server_default='0', nullable=False),
        sa.Column('gold_difference', sa.Integer(), server_default='0', nullable=False),
        sa.Column('duration_seconds', sa.Integer(), server_default='0', nullable=False),
        sa.Column('win', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('tilt_triggers_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('advices_received_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('advices_followed_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('played_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_matches_user', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT', 'UNKNOWN')", name='chk_matches_role'),
        sa.CheckConstraint('kills >= 0', name='chk_matches_kills'),
        sa.CheckConstraint('deaths >= 0', name='chk_matches_deaths'),
        sa.CheckConstraint('assists >= 0', name='chk_matches_assists'),
        sa.CheckConstraint('cs >= 0', name='chk_matches_cs'),
        sa.CheckConstraint('duration_seconds >= 0', name='chk_matches_duration')
    )

    # 4. match_telemetry_points table
    op.create_table(
        'match_telemetry_points',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('game_time_seconds', sa.Float(), nullable=False),
        sa.Column('cs', sa.Integer(), server_default='0', nullable=False),
        sa.Column('cs_per_minute', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('kills', sa.Integer(), server_default='0', nullable=False),
        sa.Column('deaths', sa.Integer(), server_default='0', nullable=False),
        sa.Column('flash_ready', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('advice_text', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['match_records.id'], name='fk_telemetry_match', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('game_time_seconds >= 0.0', name='chk_telemetry_time'),
        sa.CheckConstraint('cs >= 0', name='chk_telemetry_cs'),
        sa.CheckConstraint('cs_per_minute >= 0.0', name='chk_telemetry_cs_pm'),
        sa.CheckConstraint('kills >= 0', name='chk_telemetry_kills'),
        sa.CheckConstraint('deaths >= 0', name='chk_telemetry_deaths')
    )


def downgrade() -> None:
    op.drop_table('match_telemetry_points')
    op.drop_table('match_records')
    op.drop_table('token_blacklist')
    op.drop_table('users')
