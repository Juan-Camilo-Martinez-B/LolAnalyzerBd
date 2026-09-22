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
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Audit Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Integrity Constraints
    CONSTRAINT chk_users_auth_provider CHECK (auth_provider IN ('local', 'google', 'both')),
    CONSTRAINT chk_users_coach_sensitivity CHECK (coach_sensitivity IN ('low', 'normal', 'high')),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT uq_users_google_id UNIQUE (google_id)
);
