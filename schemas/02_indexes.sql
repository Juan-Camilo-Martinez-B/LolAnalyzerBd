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
