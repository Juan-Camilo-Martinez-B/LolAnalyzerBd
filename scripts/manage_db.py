"""
LolAnalyzer Database - Unified Administrative CLI
Provides one-command operations for schema initialization, Alembic migrations,
seed data population, database reset, status checks, and schema inspection.
"""

import argparse
import os
import sys
from pathlib import Path
from sqlalchemy import inspect, text

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from alembic import command
from alembic.config import Config
from config.database import get_sync_engine, settings
from seeds.seed_runner import run_seeds

SCHEMAS_DIR = BASE_DIR / "schemas"
ALEMBIC_INI_PATH = BASE_DIR / "migrations" / "alembic.ini"


def get_alembic_config() -> Config:
    """Creates an Alembic configuration pointing to project alembic.ini."""
    cfg = Config(str(ALEMBIC_INI_PATH))
    cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    cfg.set_main_option("sqlalchemy.url", settings.sync_database_url)
    return cfg


def cmd_init() -> None:
    """Initializes tables, indexes, functions, triggers, and views directly via SQL."""
    print("====================================================================")
    print(f"  [>] Initializing Schema on Engine: {settings.DB_ENGINE.upper()}")
    print("====================================================================")

    engine = get_sync_engine()
    is_sqlite = settings.sync_database_url.startswith("sqlite")

    sql_sequence = [
        "01_tables.sql",
        "02_indexes.sql",
        "04_triggers_functions.sql",
        "03_views.sql",
    ]

    with engine.connect() as conn:
        for file_name in sql_sequence:
            file_path = SCHEMAS_DIR / file_name
            if not file_path.exists():
                print(f"[!] Warning: Schema file '{file_name}' not found.")
                continue

            print(f"[*] Executing DDL: {file_name}...")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if is_sqlite and "04_triggers_functions.sql" in file_name:
                # PostgreSQL PL/pgSQL functions aren't directly parsed by SQLite engine
                print("    [-] Skipped PL/pgSQL functions for SQLite runtime.")
                continue

            statements = [s.strip() for s in content.split(";") if s.strip()]
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"    [-] Notice: {e}")

            conn.commit()
            print(f"    [+] {file_name} executed.")

    print("====================================================================")
    print("  [✓] Database schema initialized successfully!")
    print("====================================================================")


def cmd_migrate() -> None:
    """Applies all pending Alembic migrations up to head."""
    print("====================================================================")
    print(f"  [>] Running Alembic Migrations (upgrade head)...")
    print("====================================================================")
    cfg = get_alembic_config()
    command.upgrade(cfg, "head")
    print("  [✓] Migrations applied successfully!")


def cmd_rollback() -> None:
    """Rolls back the most recent migration (-1)."""
    print("====================================================================")
    print(f"  [>] Rolling back 1 migration step (downgrade -1)...")
    print("====================================================================")
    cfg = get_alembic_config()
    command.downgrade(cfg, "-1")
    print("  [✓] Rollback executed successfully!")


def cmd_seed() -> None:
    """Loads realistic LoL match and telemetry seeds."""
    run_seeds()


def cmd_reset() -> None:
    """Drops all tables, functions, views, and rebuilds cleanly."""
    confirm = input("Are you sure you want to WIPE and reset the entire database? (y/N): ")
    if confirm.lower() != "y":
        print("Operation cancelled.")
        return

    print("====================================================================")
    print("  [!] Wiping Database Schema...")
    print("====================================================================")

    engine = get_sync_engine()
    with engine.connect() as conn:
        conn.execute(text("DROP VIEW IF EXISTS v_tilt_coach_analytics CASCADE;"))
        conn.execute(text("DROP VIEW IF EXISTS v_champion_performance CASCADE;"))
        conn.execute(text("DROP VIEW IF EXISTS v_player_stats_summary CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS match_telemetry_points CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS match_records CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS token_blacklist CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        conn.commit()

    print("  [+] Wipe complete. Rebuilding schema...")
    cmd_init()


def cmd_status() -> None:
    """Displays current database health, connection metadata, and table row counts."""
    print("====================================================================")
    print("  LolAnalyzer Database - Status Report")
    print("====================================================================")
    print(f"  Engine:            {settings.DB_ENGINE.upper()}")
    print(f"  Connection URL:    {settings.sync_database_url.split('@')[-1] if '@' in settings.sync_database_url else settings.sync_database_url}")
    print("--------------------------------------------------------------------")

    engine = get_sync_engine()
    inspector = inspect(engine)

    try:
        tables = inspector.get_table_names()
        print(f"  Tables Found:      {len(tables)} ({', '.join(tables) if tables else 'None'})")

        with engine.connect() as conn:
            for table in ["users", "token_blacklist", "match_records", "match_telemetry_points"]:
                if table in tables:
                    res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = res.scalar()
                    print(f"    - {table:<25}: {count:>6} rows")

        views = inspector.get_view_names()
        print(f"  Views Found:       {len(views)} ({', '.join(views) if views else 'None'})")

    except Exception as e:
        print(f"  [!] Connection or inspection error: {e}")

    print("====================================================================")


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="LolAnalyzer Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("init", help="Initialize DDL schema (tables, views, triggers)")
    subparsers.add_parser("migrate", help="Run pending Alembic migrations")
    subparsers.add_parser("rollback", help="Downgrade most recent migration step")
    subparsers.add_parser("seed", help="Load test data fixtures into database")
    subparsers.add_parser("reset", help="Wipe and rebuild entire database")
    subparsers.add_parser("status", help="Show connection status and table statistics")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "migrate":
        cmd_migrate()
    elif args.command == "rollback":
        cmd_rollback()
    elif args.command == "seed":
        cmd_seed()
    elif args.command == "reset":
        cmd_reset()
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
