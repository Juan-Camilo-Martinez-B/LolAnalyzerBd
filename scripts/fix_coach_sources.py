"""
Relabels coach tips that Groq wrote but the backend stored as "gemini".

Before backend 1.1.0 every model name that was not Llama (for example
openai/gpt-oss-120b) was saved with source "gemini". Gemini stopped being
used before the first tip was stored, so only rows created up to the 1.1.0
fix are touched.

Without --apply it only prints what would change. Running it twice is safe:
once the rows say "groq" nothing else matches.

    python scripts/fix_coach_sources.py
    python scripts/fix_coach_sources.py --apply
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.database import settings  # noqa: E402

# Instante en que se desplego el backend 1.1.0 (guarda Groq como "groq").
FIXED_AT = "2026-11-08T06:45:00+00:00"

MATCHING = "FROM coach_advice_logs WHERE source = 'gemini' AND created_at < CAST(:fixed_at AS timestamptz)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Corrige la fuente de los consejos de Groq guardados como gemini.")
    parser.add_argument("--apply", action="store_true", help="Aplica el cambio. Sin esta opcion solo muestra el conteo.")
    args = parser.parse_args()

    engine = create_engine(settings.sync_database_url)
    with engine.begin() as connection:
        count = connection.execute(text(f"SELECT count(*) {MATCHING}"), {"fixed_at": FIXED_AT}).scalar_one()
        print(f"Consejos guardados como gemini antes de la 1.1.0: {count}")
        if not args.apply or count == 0:
            if count:
                print("Nada cambiado. Usa --apply para corregirlos.")
            return 0
        updated = connection.execute(
            text("UPDATE coach_advice_logs SET source = 'groq' "
                 "WHERE source = 'gemini' AND created_at < CAST(:fixed_at AS timestamptz)"),
            {"fixed_at": FIXED_AT},
        ).rowcount
        print(f"Consejos corregidos a groq: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
