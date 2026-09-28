# LolAnalyzer Database 🎮📊

Repositorio centralizado para el diseño, desarrollo, versionamiento, migraciones y datos de prueba de la base de datos de **LolAnalyzer** (Asistente Táctico en Tiempo Real y Copilot de IA para League of Legends).

[![CI Pipeline](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=githubactions&logoColor=white)](https://github.com/Juan-Camilo-Martinez-B/LolAnalyzerBd/actions)
[![Database](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Cloud DB](https://img.shields.io/badge/Supabase-Supported-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Migrations](https://img.shields.io/badge/Alembic-1.20-red?logo=python&logoColor=white)](https://alembic.sqlalchemy.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)

---

## 📌 Arquitectura del Repositorio

```text
lol-analyzer-bd/
├── .github/workflows/db-ci.yml       # Pipeline CI: Validación SQL y pruebas automatizadas
├── config/
│   ├── .env.example                  # Plantilla de variables de entorno (Postgres / SQLite)
│   └── database.py                   # Conexión centralizada y pool de conexiones
├── docs/
│   ├── data_dictionary.md            # Diccionario formal de datos, campos y restricciones
│   ├── er_diagram.md                 # Diagrama Entidad-Relación (Mermaid)
│   ├── procedures_and_views.md       # Documentación de vistas analíticas y triggers
│   └── architecture_and_roadmap.md   # Decisiones de diseño y hoja de ruta v1.1.0+
├── migrations/
│   ├── versions/                     # Revisiones de migración Python (Alembic)
│   │   ├── 0001_create_initial_schema.py
│   │   ├── 0002_add_indexes_and_constraints.py
│   │   └── 0003_add_views_and_triggers.py
│   ├── sql/                          # Migraciones puras en SQL (compatibles con Flyway)
│   │   ├── V1__initial_tables_and_types.sql
│   │   ├── V2__add_performance_indexes.sql
│   │   └── V3__add_views_and_triggers.sql
│   ├── alembic.ini                   # Configuración central de Alembic
│   └── env.py                        # Runner de migraciones online/offline
├── schemas/
│   ├── 01_tables.sql                 # DDL de tablas (users, tokens, matches, telemetry)
│   ├── 02_indexes.sql                # Índices B-Tree optimizados para consultas de IA
│   ├── 03_views.sql                  # Vistas SQL analíticas (player_summary, champ_stats)
│   └── 04_triggers_functions.sql     # Triggers de auditoría y procedimientos de purga
├── seeds/
│   ├── 01_users_seed.sql             # Invocadores de prueba con Bcrypt y enlaces LCU
│   ├── 02_matches_seed.sql           # Historial realista de partidas (roles variados)
│   ├── 03_telemetry_seed.sql         # Series temporales minuto a minuto para gráficos
│   └── seed_runner.py                # Script ejecutor automático de semillas
├── scripts/
│   ├── manage_db.py                  # CLI unificada de gestión de base de datos
│   └── test_db.py                    # Suite de pruebas automatizadas de integridad relacional
├── tests/
│   └── test_migrations.py            # Pruebas de ciclo de vida de migraciones e idempotencia
├── docker-compose.yml                # Despliegue local de PostgreSQL 16 + pgAdmin 4
├── Makefile                          # Atajos para desarrollo y despliegue
├── requirements.txt                  # Dependencias de producción
├── requirements-dev.txt              # Dependencias de pruebas y linters
├── CHANGELOG.md                      # Historial de cambios y versiones (v1.0.0)
└── README.md                         # Documentación principal
```

---

## 🗄️ Modelo Entidad - Relación (ERD)

```mermaid
erDiagram
    users ||--o{ match_records : "owns (1:N, ON DELETE CASCADE)"
    match_records ||--o{ match_telemetry_points : "contains (1:N, ON DELETE CASCADE)"

    users {
        int id PK
        varchar email UK
        varchar username
        varchar hashed_password
        varchar auth_provider
        varchar google_id UK
        varchar summoner_name
        varchar region
        varchar preferred_roles
        varchar coach_sensitivity
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    token_blacklist {
        int id PK
        varchar token_jti UK
        timestamptz revoked_at
        timestamptz expires_at
    }

    match_records {
        int id PK
        int user_id FK
        bigint game_id
        varchar champion_name
        varchar role
        int kills
        int deaths
        int assists
        int cs
        int gold_earned
        int gold_difference
        int duration_seconds
        boolean win
        int tilt_triggers_count
        int advices_received_count
        int advices_followed_count
        timestamptz played_at
    }

    match_telemetry_points {
        int id PK
        int match_id FK
        double_precision game_time_seconds
        int cs
        double_precision cs_per_minute
        int kills
        int deaths
        boolean flash_ready
        varchar advice_text
    }
```

---

## 🚀 Guía de Inicio Rápido

### 1. Instalación de Dependencias
```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz copiando la plantilla:
```powershell
cp config/.env.example .env
```
Configura tu cadena de conexión a **Supabase** o PostgreSQL local:
```env
DATABASE_URL=postgresql://postgres.your-project-ref:your-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 3. Operaciones con la CLI `manage_db.py`

| Comando | Descripción |
| :--- | :--- |
| `python scripts/manage_db.py init` | Crea todas las tablas, índices, triggers y vistas en la BD. |
| `python scripts/manage_db.py migrate` | Ejecuta las migraciones pendientes con Alembic hasta `head`. |
| `python scripts/manage_db.py rollback` | Revierte un paso de migración (`downgrade -1`). |
| `python scripts/manage_db.py seed` | Inserta usuarios, partidas y telemetría de prueba. |
| `python scripts/manage_db.py status` | Muestra el estado de la conexión y conteo de filas por tabla. |
| `python scripts/manage_db.py reset` | Elimina y reconstruye todo el esquema desde cero. |

---

## 🧪 Pruebas Automatizadas y Calidad

Para ejecutar las pruebas de integridad relacional, borrado en cascada y ciclos de migración:
```powershell
pytest scripts/test_db.py tests/ -v
```

Para verificar calidad y formato de código:
```powershell
flake8 . --max-line-length=110 --exclude=.venv,env,migrations/versions
sqlfluff lint schemas/ migrations/sql/ --dialect postgres
```

---

## 👥 Contribuidores & Créditos
Proyecto desarrollado para la asignatura de Programación Web (7mo Semestre) - **LolAnalyzer**.
