-- =============================================================================
-- Migration: V2__add_performance_indexes.sql
-- Description: Adds B-Tree optimization indexes for Users, Token Blacklist,
-- Match History, and Telemetry Time-Series.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

-- 1. Users Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_summoner ON users (summoner_name, region);

-- 2. Token Blacklist Indexes
CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist (token_jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires ON token_blacklist (expires_at);

-- 3. Match Records Indexes
CREATE INDEX IF NOT EXISTS idx_matches_user_played ON match_records (user_id, played_at DESC);
CREATE INDEX IF NOT EXISTS idx_matches_user_role ON match_records (user_id, role);
CREATE INDEX IF NOT EXISTS idx_matches_user_champion ON match_records (user_id, champion_name);
CREATE INDEX IF NOT EXISTS idx_matches_game_id ON match_records (game_id);
CREATE INDEX IF NOT EXISTS idx_matches_user_win ON match_records (user_id, win);

-- 4. Match Telemetry Points Indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_match_timeline ON match_telemetry_points (match_id, game_time_seconds ASC);
CREATE INDEX IF NOT EXISTS idx_telemetry_match_time ON match_telemetry_points (match_id, game_time_seconds);
