-- =============================================================================
-- LolAnalyzer Database Schema - Query Optimization & Performance Indexes
-- File: schemas/02_indexes.sql
-- Description: B-Tree Indexes designed for sub-millisecond lookups,
-- authentication queries, token revocations, and time-series telemetry slicing.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

-- =============================================================================
-- 1. Indexes for User Authentication & Profile Lookups
-- Accelerates login credential verification, OAuth token mapping,
-- and Riot summoner profile lookups.
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_summoner ON users (summoner_name, region);

-- =============================================================================
-- 2. Indexes for Token Revocation & Cleanup
-- Allows O(1) JWT blacklist validation during protected request verification
-- and fast periodic purging of expired blacklisted tokens.
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist (token_jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires ON token_blacklist (expires_at);

-- =============================================================================
-- 3. Indexes for Match History & Multi-Criteria Filtering
-- Optimizes historical match pagination, winrate aggregations,
-- role-based performance analysis, and champion mastery stats.
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_matches_user_played ON match_records (user_id, played_at DESC);
CREATE INDEX IF NOT EXISTS idx_matches_user_role ON match_records (user_id, role);
CREATE INDEX IF NOT EXISTS idx_matches_user_champion ON match_records (user_id, champion_name);
CREATE INDEX IF NOT EXISTS idx_matches_game_id ON match_records (game_id);
CREATE INDEX IF NOT EXISTS idx_matches_user_win ON match_records (user_id, win);

-- =============================================================================
-- 4. Indexes for High-Frequency Telemetry & Visual Analytics
-- Supports linear-time retrieval of game timeline points, CS/min progression curves,
-- death event clusters, and coach advice telemetry streams.
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_telemetry_match_timeline ON match_telemetry_points (match_id, game_time_seconds ASC);
CREATE INDEX IF NOT EXISTS idx_telemetry_match_time ON match_telemetry_points (match_id, game_time_seconds);
