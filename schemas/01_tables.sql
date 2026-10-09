-- =============================================================================
-- LolAnalyzer Database Schema - Core Tables Definition
-- File: schemas/01_tables.sql
-- Description: Defines foundational DDL tables for Users, Authentication,
-- Match History, and High-Frequency In-Game Telemetry.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

-- =============================================================================
-- 1. Table: users
-- Represents authenticated summoners, local/OAuth credentials,
-- LoL account linkage, and tactical AI coach configurations.
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NULL,
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
    google_id VARCHAR(255) NULL,
    avatar_url VARCHAR(500) NULL,

    -- League of Legends Summoner Linkage (via Riot LCU client)
    summoner_name VARCHAR(100) NULL,
    summoner_icon_id INTEGER NULL,
    region VARCHAR(20) NOT NULL DEFAULT 'la1',

    -- AI Tactical Coach Preferences & Heuristic Sensitivity
    preferred_roles VARCHAR(100) NOT NULL DEFAULT 'MID,TOP',
    coach_sensitivity VARCHAR(20) NOT NULL DEFAULT 'normal',
    theme_preference VARCHAR(20) NOT NULL DEFAULT 'light',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    session_version INTEGER NOT NULL DEFAULT 1,
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE NULL,

    -- Riot account identifiers only. Match payloads stay on Riot's API.
    riot_puuid VARCHAR(80) NULL,
    riot_game_name VARCHAR(100) NULL,
    riot_tag_line VARCHAR(20) NULL,

    -- Audit Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Integrity Constraints
    CONSTRAINT chk_users_auth_provider CHECK (auth_provider IN ('local', 'google', 'both')),
    CONSTRAINT chk_users_coach_sensitivity CHECK (coach_sensitivity IN ('low', 'normal', 'high')),
    CONSTRAINT chk_users_theme_preference CHECK (theme_preference IN ('light', 'system', 'dark')),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT uq_users_google_id UNIQUE (google_id),
    CONSTRAINT uq_users_riot_puuid UNIQUE (riot_puuid)
);

-- =============================================================================
-- 2. Table: token_blacklist
-- Stores cryptographically revoked JWT Unique Identifiers (jti) for immediate
-- session termination and protection against token replay attacks.
-- =============================================================================
CREATE TABLE IF NOT EXISTS token_blacklist (
    id SERIAL PRIMARY KEY,
    token_jti VARCHAR(255) NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Integrity Constraints
    CONSTRAINT uq_token_blacklist_jti UNIQUE (token_jti)
);

-- =============================================================================
-- 3. Table: match_records
-- Historical match outcomes, performance metrics (KDA, CS, Gold),
-- win/loss result, and behavioral tilt / AI coaching interactions.
-- =============================================================================
CREATE TABLE IF NOT EXISTS match_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    game_id BIGINT NULL,
    champion_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    kills INTEGER NOT NULL DEFAULT 0,
    deaths INTEGER NOT NULL DEFAULT 0,
    assists INTEGER NOT NULL DEFAULT 0,
    cs INTEGER NOT NULL DEFAULT 0,
    gold_earned INTEGER NOT NULL DEFAULT 0,
    gold_difference INTEGER NOT NULL DEFAULT 0,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    win BOOLEAN NOT NULL DEFAULT FALSE,

    -- Behavioral Tilt & Real-Time AI Coach Analytics
    tilt_triggers_count INTEGER NOT NULL DEFAULT 0,
    advices_received_count INTEGER NOT NULL DEFAULT 0,
    advices_followed_count INTEGER NOT NULL DEFAULT 0,

    played_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys & Constraints
    CONSTRAINT fk_matches_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT chk_matches_role CHECK (role IN ('TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT', 'UNKNOWN')),
    CONSTRAINT chk_matches_kills CHECK (kills >= 0),
    CONSTRAINT chk_matches_deaths CHECK (deaths >= 0),
    CONSTRAINT chk_matches_assists CHECK (assists >= 0),
    CONSTRAINT chk_matches_cs CHECK (cs >= 0),
    CONSTRAINT chk_matches_duration CHECK (duration_seconds >= 0)
);

-- =============================================================================
-- 4. Table: match_telemetry_points
-- High-frequency time-series data captured during match execution:
-- CS progression, CS/min rate, kills, deaths, flash cooldown state,
-- and instantaneous tactical coach advice.
-- =============================================================================
CREATE TABLE IF NOT EXISTS match_telemetry_points (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL,
    game_time_seconds DOUBLE PRECISION NOT NULL,
    cs INTEGER NOT NULL DEFAULT 0,
    cs_per_minute DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    kills INTEGER NOT NULL DEFAULT 0,
    deaths INTEGER NOT NULL DEFAULT 0,
    flash_ready BOOLEAN NOT NULL DEFAULT TRUE,
    advice_text VARCHAR(255) NULL,

    -- Foreign Keys & Constraints
    CONSTRAINT fk_telemetry_match FOREIGN KEY (match_id)
        REFERENCES match_records (id) ON DELETE CASCADE,
    CONSTRAINT chk_telemetry_time CHECK (game_time_seconds >= 0.0),
    CONSTRAINT chk_telemetry_cs CHECK (cs >= 0),
    CONSTRAINT chk_telemetry_cs_pm CHECK (cs_per_minute >= 0.0),
    CONSTRAINT chk_telemetry_kills CHECK (kills >= 0),
    CONSTRAINT chk_telemetry_deaths CHECK (deaths >= 0)
);

-- =============================================================================
-- 5. Table: security_answers
-- Hashed recovery answers. Plaintext answers are never stored.
-- =============================================================================
CREATE TABLE IF NOT EXISTS security_answers (
    user_id INTEGER PRIMARY KEY,
    favorite_champion_hash VARCHAR(255) NOT NULL,
    peak_elo_hash VARCHAR(255) NOT NULL,
    first_main_hash VARCHAR(255) NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
);

-- =============================================================================
-- 6. Table: auth_attempts
-- Shared lockout counter. subject_hash is not the raw email.
-- =============================================================================
CREATE TABLE IF NOT EXISTS auth_attempts (
    id SERIAL PRIMARY KEY,
    subject_hash VARCHAR(64) NOT NULL,
    purpose VARCHAR(32) NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    window_started TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    locked_until TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT uq_auth_attempt_subject UNIQUE (subject_hash, purpose)
);

-- =============================================================================
-- 7. Table: coach_advice_logs
-- Tips the AI already gave this account. They stay after logout.
-- =============================================================================
CREATE TABLE IF NOT EXISTS coach_advice_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    advice_text VARCHAR(240) NOT NULL,
    trigger_type VARCHAR(40) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    champion_name VARCHAR(40) NOT NULL,
    role VARCHAR(20) NOT NULL,
    game_time_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
    source VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_coach_advice_logs_user_id ON coach_advice_logs (user_id);

-- =============================================================================
-- 8. Table: riot_cache
-- TTL cache for Riot responses. It is not a permanent match archive.
-- =============================================================================
CREATE TABLE IF NOT EXISTS riot_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    payload TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
