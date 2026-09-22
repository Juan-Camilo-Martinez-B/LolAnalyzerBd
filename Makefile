# ==============================================================================
# LolAnalyzer Database Management Makefile
# ==============================================================================

.PHONY: help install up down restart logs psql init migrate rollback seed reset status test lint format clean

# Default target when running 'make'
help:
	@echo "========================================================================"
	@echo "               LolAnalyzer Database Management Commands                "
	@echo "========================================================================"
	@echo "  make install     - Install Python runtime and development dependencies"
	@echo "  make up          - Start PostgreSQL and pgAdmin containers in background"
	@echo "  make down        - Stop all running database containers"
	@echo "  make restart     - Restart database containers"
	@echo "  make logs        - Tail PostgreSQL container logs in real time"
	@echo "  make psql        - Open interactive PostgreSQL terminal in container"
	@echo "  make init        - Initialize database tables, views, and triggers"
	@echo "  make migrate     - Run pending Alembic and SQL schema migrations"
	@echo "  make rollback    - Downgrade the most recent schema migration"
	@echo "  make seed        - Populate database with realistic LoL test fixtures"
	@echo "  make reset       - Wipe and rebuild entire database from clean state"
	@echo "  make status      - Display current migration version and table statistics"
	@echo "  make test        - Execute automated database integrity and schema tests"
	@echo "  make lint        - Run SQL and Python code quality linters"
	@echo "  make format      - Auto-format Python scripts with Black"
	@echo "  make clean       - Remove cached files, pycache, and temporary test artifacts"
	@echo "========================================================================"

# Dependency Installation
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Docker Infrastructure Targets
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f postgres

psql:
	docker compose exec -it postgres psql -U lol_admin -d lol_analyzer_db

# Database Lifecycle Operations (via manage_db CLI)
init:
	python scripts/manage_db.py init

migrate:
	python scripts/manage_db.py migrate

rollback:
	python scripts/manage_db.py rollback

seed:
	python scripts/manage_db.py seed

reset:
	python scripts/manage_db.py reset

status:
	python scripts/manage_db.py status

# Quality Assurance & Testing
test:
	pytest scripts/test_db.py tests/ -v

lint:
	flake8 . --max-line-length=110 --exclude=.venv,env,migrations/versions
	sqlfluff lint schemas/ migrations/sql/ --dialect postgres

format:
	black .

# Clean Workspace
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
