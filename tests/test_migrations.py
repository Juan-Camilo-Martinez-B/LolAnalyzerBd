"""
LolAnalyzer Database - Migration Lifecycle & Idempotency Tests
Verifies full Alembic migration cycles (upgrade -> downgrade -> re-upgrade)
to ensure schema changes are reversible, atomic, and idempotent.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine, inspect

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

ALEMBIC_INI_PATH = BASE_DIR / "migrations" / "alembic.ini"


@pytest.fixture(scope="module")
def alembic_test_env():
    """Generates an isolated test SQLite database and Alembic configuration."""
    test_db_path = BASE_DIR / "test_alembic_migrations.db"
    if test_db_path.exists():
        test_db_path.unlink()

    test_db_url = f"sqlite:///{test_db_path}"
    test_engine = create_engine(test_db_url)

    cfg = Config(str(ALEMBIC_INI_PATH))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", test_db_url)

    yield {"cfg": cfg, "engine": test_engine, "db_path": test_db_path}

    test_engine.dispose()
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass


def test_migration_upgrade_to_head(alembic_test_env):
    """Test 1: Assert Alembic can migrate cleanly up to the latest revision (head)."""
    cfg = alembic_test_env["cfg"]
    engine = alembic_test_env["engine"]

    try:
        command.upgrade(cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic upgrade head failed: {e}")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "token_blacklist" in tables
    assert "match_records" in tables
    assert "match_telemetry_points" in tables


def test_migration_downgrade_one_step(alembic_test_env):
    """Test 2: Assert Alembic can rollback 1 step without corrupting previous revisions."""
    cfg = alembic_test_env["cfg"]
    try:
        command.downgrade(cfg, "-1")
    except Exception as e:
        pytest.fail(f"Alembic downgrade -1 failed: {e}")


def test_migration_re_upgrade_to_head(alembic_test_env):
    """Test 3: Assert re-upgrading to head succeeds cleanly (idempotency verification)."""
    cfg = alembic_test_env["cfg"]
    engine = alembic_test_env["engine"]

    try:
        command.upgrade(cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic re-upgrade to head failed: {e}")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "match_records" in tables


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
