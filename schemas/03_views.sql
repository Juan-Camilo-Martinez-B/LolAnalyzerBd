-- =============================================================================
-- LolAnalyzer Database Schema - Analytical & Reporting Views
-- File: schemas/03_views.sql
-- Description: Precomputed aggregate views powering the tactical dashboard,
-- career overview, champion mastery, and real-time AI coach performance insights.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

-- =============================================================================
-- 1. View: v_player_stats_summary
-- Aggregates overall career metrics per user: Winrate %, KDA, Average CS/min,
-- Tilt trigger frequency, and AI Coach compliance rate %.
-- =============================================================================
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
