"""
LolAnalyzer Database - Alembic Migration Environment
Provides online and offline migration runners using project configuration settings.
"""

from logging.config import fileConfig
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from alembic import context
except ImportError:
    # Fallback / mock context for static analysis tools & IDE linters
    if TYPE_CHECKING:
        from alembic.runtime.environment import EnvironmentContext
        context: EnvironmentContext = None  # type: ignore

from config.database import get_sync_engine, settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config if hasattr(context, "config") else None

# Interpret the config file for Python logging.
if config and config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database metadata dynamically if using ORM auto-generation
target_metadata = None


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Configures the context with just a URL and not an Engine.
    """
    url = settings.sync_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Creates an Engine and associates a connection with the context.
    """
    connectable = get_sync_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True if settings.sync_database_url.startswith("sqlite") else False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context and context.is_offline_mode():
    run_migrations_offline()
elif context:
    run_migrations_online()
