"""
LolAnalyzer Database - Migration Lifecycle & Idempotency Tests
Verifies full Alembic migration cycles (upgrade -> downgrade -> re-upgrade)
to ensure schema changes are reversible, atomic, and idempotent.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import inspect

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from alembic import command
from alembic.config import Config
from config.database import get_sync_engine, settings

ALEMBIC_INI_PATH = BASE_DIR / "migrations" / "alembic.ini"


@pytest.fixture(scope="module")
def alembic_cfg():
    """Generates test Alembic configuration."""
    cfg = Config(str(ALEMBIC_INI_PATH))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", settings.sync_database_url)
    return cfg


def test_migration_upgrade_to_head(alembic_cfg):
    """Test 1: Assert Alembic can migrate cleanly up to the latest revision (head)."""
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic upgrade head failed: {e}")

    engine = get_sync_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "token_blacklist" in tables
    assert "match_records" in tables
    assert "match_telemetry_points" in tables


def test_migration_downgrade_one_step(alembic_cfg):
    """Test 2: Assert Alembic can rollback 1 step without corrupting previous revisions."""
    try:
        command.downgrade(alembic_cfg, "-1")
    except Exception as e:
        pytest.fail(f"Alembic downgrade -1 failed: {e}")


def test_migration_re_upgrade_to_head(alembic_cfg):
    """Test 3: Assert re-upgrading to head succeeds cleanly (idempotency verification)."""
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic re-upgrade to head failed: {e}")

    engine = get_sync_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "match_records" in tables


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
