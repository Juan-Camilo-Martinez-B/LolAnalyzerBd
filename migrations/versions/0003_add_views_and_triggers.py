"""add analytical views, stored functions and triggers

Revision ID: 0003_add_views_and_triggers
Revises: 0002_add_indexes_and_constraints
Create Date: 2026-09-22 10:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = '0003_add_views_and_triggers'
down_revision: Union[str, None] = '0002_add_indexes_and_constraints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update timestamp function & trigger
    op.execute("""
    CREATE OR REPLACE FUNCTION fn_update_timestamp()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
    CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();
    """)

    # 2. Reset matches stored procedure
    op.execute("""
    CREATE OR REPLACE FUNCTION sp_reset_user_matches(p_user_id INTEGER)
    RETURNS INTEGER AS $$
    DECLARE
        v_deleted_count INTEGER := 0;
    BEGIN
        WITH deleted_rows AS (
            DELETE FROM match_records
            WHERE user_id = p_user_id
            RETURNING id
        )
        SELECT COUNT(*) INTO v_deleted_count FROM deleted_rows;

        RETURN v_deleted_count;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 3. View: v_player_stats_summary
    op.execute("""
    CREATE OR REPLACE VIEW v_player_stats_summary AS
    SELECT
        u.id AS user_id,
        u.username,
        u.summoner_name,
        u.region,
        COUNT(m.id) AS total_matches,
        COALESCE(SUM(CASE WHEN m.win = TRUE THEN 1 ELSE 0 END), 0) AS total_wins,
        COALESCE(SUM(CASE WHEN m.win = FALSE THEN 1 ELSE 0 END), 0) AS total_losses,
        ROUND(
            CASE
                WHEN COUNT(m.id) > 0
                THEN (SUM(CASE WHEN m.win = TRUE THEN 1.0 ELSE 0.0 END) / COUNT(m.id)) * 100.0
                ELSE 0.0
            END, 2
        ) AS winrate_percentage,
        COALESCE(SUM(m.kills), 0) AS total_kills,
        COALESCE(SUM(m.deaths), 0) AS total_deaths,
        COALESCE(SUM(m.assists), 0) AS total_assists,
        ROUND(
            CASE
                WHEN COALESCE(SUM(m.deaths), 0) > 0
                THEN (SUM(m.kills) + SUM(m.assists))::NUMERIC / SUM(m.deaths)::NUMERIC
                ELSE (SUM(m.kills) + SUM(m.assists))::NUMERIC
            END, 2
        ) AS average_kda,
        ROUND(COALESCE(AVG(m.cs), 0.0), 1) AS average_cs,
        ROUND(
            COALESCE(
                AVG(
                    CASE
                        WHEN m.duration_seconds > 0
                        THEN (m.cs * 60.0) / m.duration_seconds
                        ELSE 0.0
                    END
                ), 0.0
            ), 2
        ) AS average_cs_per_minute,
        COALESCE(SUM(m.tilt_triggers_count), 0) AS total_tilt_triggers,
        ROUND(COALESCE(AVG(m.tilt_triggers_count), 0.0), 2) AS avg_tilt_triggers_per_match,
        COALESCE(SUM(m.advices_received_count), 0) AS total_advices_received,
        COALESCE(SUM(m.advices_followed_count), 0) AS total_advices_followed,
        ROUND(
            CASE
                WHEN COALESCE(SUM(m.advices_received_count), 0) > 0
                THEN (SUM(m.advices_followed_count)::NUMERIC / SUM(m.advices_received_count)::NUMERIC) * 100.0
                ELSE 0.0
            END, 2
        ) AS coach_compliance_rate_percentage
    FROM users u
    LEFT JOIN match_records m ON u.id = m.user_id
    GROUP BY u.id, u.username, u.summoner_name, u.region;
    """)

    # 4. View: v_champion_performance
    op.execute("""
    CREATE OR REPLACE VIEW v_champion_performance AS
    SELECT
        m.user_id,
        m.champion_name,
        m.role,
        COUNT(m.id) AS games_played,
        COALESCE(SUM(CASE WHEN m.win = TRUE THEN 1 ELSE 0 END), 0) AS wins,
        COALESCE(SUM(CASE WHEN m.win = FALSE THEN 1 ELSE 0 END), 0) AS losses,
        ROUND(
            (SUM(CASE WHEN m.win = TRUE THEN 1.0 ELSE 0.0 END) / COUNT(m.id)) * 100.0, 1
        ) AS winrate_percentage,
        ROUND(
            CASE
                WHEN SUM(m.deaths) > 0
                THEN (SUM(m.kills) + SUM(m.assists))::NUMERIC / SUM(m.deaths)::NUMERIC
                ELSE (SUM(m.kills) + SUM(m.assists))::NUMERIC
            END, 2
        ) AS avg_kda,
        ROUND(AVG(m.kills), 1) AS avg_kills,
        ROUND(AVG(m.deaths), 1) AS avg_deaths,
        ROUND(AVG(m.assists), 1) AS avg_assists,
        ROUND(
            AVG(
                CASE
                    WHEN m.duration_seconds > 0
                    THEN (m.cs * 60.0) / m.duration_seconds
                    ELSE 0.0
                END
            ), 2
        ) AS avg_cs_per_minute,
        ROUND(AVG(m.gold_difference), 0) AS avg_gold_difference
    FROM match_records m
    GROUP BY m.user_id, m.champion_name, m.role;
    """)

    # 5. View: v_tilt_coach_analytics
    op.execute("""
    CREATE OR REPLACE VIEW v_tilt_coach_analytics AS
    SELECT
        m.user_id,
        m.role,
        COUNT(m.id) AS total_games_analyzed,
        COALESCE(SUM(m.tilt_triggers_count), 0) AS total_tilt_episodes,
        ROUND(COALESCE(AVG(m.tilt_triggers_count), 0.0), 2) AS avg_tilt_per_game,
        COALESCE(SUM(m.advices_received_count), 0) AS total_ai_advices_given,
        COALESCE(SUM(m.advices_followed_count), 0) AS total_ai_advices_followed,
        ROUND(
            CASE
                WHEN COALESCE(SUM(m.advices_received_count), 0) > 0
                THEN (SUM(m.advices_followed_count)::NUMERIC / SUM(m.advices_received_count)::NUMERIC) * 100.0
                ELSE 0.0
            END, 1
        ) AS coach_compliance_percentage,
        ROUND(
            COALESCE(
                (SUM(CASE WHEN m.win = TRUE AND m.advices_followed_count > 0 THEN 1.0 ELSE 0.0 END) /
                 NULLIF(SUM(CASE WHEN m.advices_followed_count > 0 THEN 1.0 ELSE 0.0 END), 0)) * 100.0, 0.0
            ), 1
        ) AS winrate_when_following_coach_pct,
        ROUND(
            COALESCE(
                (SUM(CASE WHEN m.win = TRUE AND m.tilt_triggers_count = 0 THEN 1.0 ELSE 0.0 END) /
                 NULLIF(SUM(CASE WHEN m.tilt_triggers_count = 0 THEN 1.0 ELSE 0.0 END), 0)) * 100.0, 0.0
            ), 1
        ) AS winrate_without_tilt_pct
    FROM match_records m
    GROUP BY m.user_id, m.role;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_tilt_coach_analytics;")
    op.execute("DROP VIEW IF EXISTS v_champion_performance;")
    op.execute("DROP VIEW IF EXISTS v_player_stats_summary;")
    op.execute("DROP FUNCTION IF EXISTS sp_reset_user_matches(INTEGER);")
    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS fn_update_timestamp();")
