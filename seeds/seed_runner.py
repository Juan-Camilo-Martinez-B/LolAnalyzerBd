"""
LolAnalyzer Database - Seed Data Runner
Loads structured test datasets (users, match records, telemetry points)
into PostgreSQL or SQLite databases.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.database import get_sync_engine, settings

SEEDS_DIR = Path(__file__).resolve().parent

SEED_FILES = [
    "01_users_seed.sql",
    "02_matches_seed.sql",
    "03_telemetry_seed.sql",
]


def run_seeds() -> None:
    """Executes all seed files in sequential dependency order."""
    print("====================================================================")
    print(f"  LolAnalyzer Database Seeder -> Target: {settings.DB_ENGINE.upper()}")
    print("====================================================================")

    engine = get_sync_engine()
    is_sqlite = settings.sync_database_url.startswith("sqlite")

    with engine.connect() as conn:
        for seed_file in SEED_FILES:
            file_path = SEEDS_DIR / seed_file
            if not file_path.exists():
                print(f"[!] Warning: Seed file '{seed_file}' not found. Skipping.")
                continue

            print(f"[*] Applying seed: {seed_file}...")
            with open(file_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # For SQLite, filter out PostgreSQL specific statements like setval
            if is_sqlite:
                lines = [
                    line for line in sql_content.splitlines()
                    if not line.strip().startswith("SELECT setval(")
                ]
                sql_content = "\n".join(lines)

            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    # Ignore minor warnings on conflict or sequence resets
                    if "setval" in stmt and is_sqlite:
                        continue
                    print(f"    [-] Notice on statement: {e}")

            conn.commit()
            print(f"    [+] {seed_file} applied successfully.")

    print("====================================================================")
    print("  [✓] All database seeds have been loaded successfully!")
    print("====================================================================")


if __name__ == "__main__":
    run_seeds()
