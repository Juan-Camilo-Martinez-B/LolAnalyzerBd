-- =============================================================================
-- LolAnalyzer Database Schema - Triggers, Functions & Stored Procedures
-- File: schemas/04_triggers_functions.sql
-- Description: Business logic routines, audit triggers, and maintenance procedures.
-- Compatible with PostgreSQL 14+ (with SQLite trigger annotations)
-- =============================================================================

-- =============================================================================
-- 1. Function: fn_update_timestamp()
-- Reusable PL/pgSQL function to automatically refresh the `updated_at`
-- column with the current UTC timestamp prior to persisting row modifications.
-- =============================================================================
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 2. Trigger: trg_users_updated_at
-- Binds the timestamp updater function to row update events on the `users` table.
-- Ensures strict audit trails whenever player profile or settings change.
-- =============================================================================
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION fn_update_timestamp();
