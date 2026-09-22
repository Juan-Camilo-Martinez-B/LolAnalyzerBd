"""
LolAnalyzer Database - Core Configuration & Engine Provider
Handles environment variables, URL synthesis, connection pooling,
and provides sync and async engines for migrations, scripts, and ORMs.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Base directories
CONFIG_DIR = Path(__file__).resolve().parent
ROOT_DIR = CONFIG_DIR.parent

# Load .env if present in root or config folder
load_dotenv(ROOT_DIR / ".env")
load_dotenv(CONFIG_DIR / ".env")


class DatabaseSettings(BaseSettings):
    """Database connection and environment parameters."""
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Engine selector ('postgresql' or 'sqlite')
    DB_ENGINE: str = "postgresql"

    # PostgreSQL Parameters
    POSTGRES_USER: str = "lol_admin"
    POSTGRES_PASSWORD: str = "lol_secure_password_2026"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "lol_analyzer_db"

    # Explicit URLs (Overrides individual parameters if provided)
    DATABASE_URL: Optional[str] = None
    ASYNC_DATABASE_URL: Optional[str] = None

    # SQLite Settings
    SQLITE_DB_PATH: str = str(ROOT_DIR / "lol_analyzer.db")

    # Pooling and Logging
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    @property
    def sync_database_url(self) -> str:
        """Returns standard synchronous database URL (psycopg2 / sqlite)."""
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            url = self.DATABASE_URL.strip()
            # Normalize postgres:// -> postgresql://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url

        if self.DB_ENGINE.lower() == "sqlite":
            return f"sqlite:///{self.SQLITE_DB_PATH}"

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        """Returns asynchronous database URL (asyncpg / aiosqlite)."""
        if self.ASYNC_DATABASE_URL and self.ASYNC_DATABASE_URL.strip():
            url = self.ASYNC_DATABASE_URL.strip()
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        if self.DB_ENGINE.lower() == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> DatabaseSettings:
    """Returns singleton instance of database settings."""
    return DatabaseSettings()


settings = get_settings()


def get_sync_engine(echo: Optional[bool] = None) -> Engine:
    """Creates a synchronous SQLAlchemy engine for migrations and CLI scripts."""
    url = settings.sync_database_url
    is_sqlite = url.startswith("sqlite")
    kwargs: Dict[str, Any] = {"echo": settings.DB_ECHO if echo is None else echo}

    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_size"] = settings.DB_POOL_SIZE
        kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT
        kwargs["pool_pre_ping"] = True

    return create_engine(url, **kwargs)


def get_async_engine(echo: Optional[bool] = None) -> AsyncEngine:
    """Creates an asynchronous SQLAlchemy engine for high-concurrency operations."""
    url = settings.async_database_url
    is_sqlite = url.startswith("sqlite")
    kwargs: Dict[str, Any] = {"echo": settings.DB_ECHO if echo is None else echo}

    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_size"] = settings.DB_POOL_SIZE
        kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT
        kwargs["pool_pre_ping"] = True

    return create_async_engine(url, **kwargs)
