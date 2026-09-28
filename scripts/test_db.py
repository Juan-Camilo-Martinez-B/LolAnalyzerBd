"""
LolAnalyzer Database - Automated Integrity & Constraint Test Suite
Validates relational integrity, UNIQUE constraints, cascading deletes,
and the validity of analytical views across PostgreSQL and SQLite.
"""

import os
import sys
import uuid
from pathlib import Path
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.database import get_sync_engine, settings


@pytest.fixture(scope="module")
def db_engine():
    """Provides test database engine instance."""
    return get_sync_engine()


def test_db_connection(db_engine):
    """Test 1: Verify successful database connectivity."""
    with db_engine.connect() as conn:
        res = conn.execute(text("SELECT 1"))
        assert res.scalar() == 1


def test_users_table_exists(db_engine):
    """Test 2: Verify users table and schema structure."""
    with db_engine.connect() as conn:
        res = conn.execute(text("SELECT COUNT(*) FROM users"))
        assert res.scalar() is not None


def test_unique_email_constraint(db_engine):
    """Test 3: Assert duplicate email raises an IntegrityError."""
    unique_suffix = str(uuid.uuid4())[:8]
    test_email = f"duplicate_{unique_suffix}@test.com"

    with db_engine.connect() as conn:
        # First insertion
        conn.execute(
            text("""
                INSERT INTO users (email, username, auth_provider, region)
                VALUES (:email, 'TestUser1', 'local', 'la1')
            """),
            {"email": test_email},
        )
        conn.commit()

        # Second duplicate insertion must fail
        with pytest.raises(IntegrityError):
            conn.execute(
                text("""
                    INSERT INTO users (email, username, auth_provider, region)
                    VALUES (:email, 'TestUser2', 'local', 'la1')
                """),
                {"email": test_email},
            )
            conn.commit()


def test_cascade_deletion(db_engine):
    """Test 4: Verify ON DELETE CASCADE from User -> MatchRecord -> Telemetry."""
    unique_suffix = str(uuid.uuid4())[:8]
    test_email = f"cascade_{unique_suffix}@test.com"

    with db_engine.connect() as conn:
        # 1. Insert User
        user_res = conn.execute(
            text("""
                INSERT INTO users (email, username, auth_provider, region)
                VALUES (:email, 'CascadeUser', 'local', 'la1')
                RETURNING id
            """),
            {"email": test_email},
        )
        user_id = user_res.scalar()
        conn.commit()

        # 2. Insert Match for this User
        match_res = conn.execute(
            text("""
                INSERT INTO match_records (user_id, champion_name, role, kills, deaths, assists, cs, duration_seconds, win)
                VALUES (:user_id, 'Ahri', 'MID', 5, 0, 5, 100, 1200, true)
                RETURNING id
            """),
            {"user_id": user_id},
        )
        match_id = match_res.scalar()
        conn.commit()

        # 3. Insert Telemetry Point for this Match
        conn.execute(
            text("""
                INSERT INTO match_telemetry_points (match_id, game_time_seconds, cs, kills, deaths)
                VALUES (:match_id, 60.0, 10, 1, 0)
            """),
            {"match_id": match_id},
        )
        conn.commit()

        # 4. Delete User
        conn.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
        conn.commit()

        # 5. Assert Match and Telemetry were automatically purged
        remaining_matches = conn.execute(
            text("SELECT COUNT(*) FROM match_records WHERE id = :match_id"),
            {"match_id": match_id},
        ).scalar()
        remaining_telemetry = conn.execute(
            text("SELECT COUNT(*) FROM match_telemetry_points WHERE match_id = :match_id"),
            {"match_id": match_id},
        ).scalar()

        assert remaining_matches == 0
        assert remaining_telemetry == 0


def test_analytical_views(db_engine):
    """Test 5: Verify analytical views execute without syntax errors."""
    with db_engine.connect() as conn:
        try:
            conn.execute(text("SELECT * FROM v_player_stats_summary LIMIT 5"))
            conn.execute(text("SELECT * FROM v_champion_performance LIMIT 5"))
            conn.execute(text("SELECT * FROM v_tilt_coach_analytics LIMIT 5"))
        except Exception as e:
            pytest.fail(f"View query execution failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
