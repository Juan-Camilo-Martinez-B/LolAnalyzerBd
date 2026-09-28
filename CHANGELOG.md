# Registro de Cambios (Changelog) - LolAnalyzer Database

Todos los cambios notables en la arquitectura, migraciones y procedimientos de la base de datos están documentados aquí siguiendo el formato [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] - 2026-09-28

### Añadido (Added)
- **Esquema Relacional Base**:
  - Creación de la tabla `users` con soporte de autenticación híbrida (local Bcrypt y Google OAuth2) y vinculación al cliente Riot LCU.
  - Creación de la tabla `token_blacklist` para revocación criptográfica inmediata de JWTs (`token_jti`).
  - Creación de la tabla `match_records` con métricas individuales de rendimiento (KDA, CS, oro, win/loss) y contadores heurísticos de tilt/coach.
  - Creación de la tabla `match_telemetry_points` para captura de series temporales de alta resolución segundo a segundo.
- **Índices y Optimización**:
  - Índices B-Tree para autenticación rápida (`users.email`, `users.username`, `users.google_id`, `(summoner_name, region)`).
  - Índices de tiempo lineal sobre series temporales `(match_id, game_time_seconds ASC)`.
  - Índices compuestos en historial de partidas `(user_id, played_at DESC)`, `(user_id, role)` y `(user_id, champion_name)`.
- **Procedimientos, Funciones y Triggers**:
  - Función PL/pgSQL `fn_update_timestamp()` y trigger `trg_users_updated_at` para actualización automática de auditoría.
  - Procedimiento almacenado `sp_reset_user_matches(p_user_id)` para purga transaccional y atómica de estadísticas por usuario.
- **Vistas SQL Analíticas**:
  - Vista `v_player_stats_summary` para métricas consolidadas del invocador (winrate, KDA acumulado, CS/min normalizado).
  - Vista `v_champion_performance` para analítica agrupada por campeón y soporte a Champion Select.
  - Vista `v_tilt_coach_analytics` para correlación entre alertas de tilt, consejos aplicados y winrate.
- **Sistema Dual de Migraciones**:
  - Migraciones puras en SQL versionado (`V1__initial_tables_and_types.sql`, `V2__add_performance_indexes.sql`, `V3__add_views_and_triggers.sql`).
  - Entorno de migraciones programático en Python con Alembic (`alembic.ini`, `env.py`, revisiones `0001`, `0002`, `0003`).
- **Semillas y Datasets de Prueba**:
  - 5 invocadores de prueba en roles MID, TOP, ADC, JG, SUP (`01_users_seed.sql`).
  - 19 partidas históricas realistas con campeones variados (`02_matches_seed.sql`).
  - Series temporales de telemetría con curvas de CS y consejos emitidos (`03_telemetry_seed.sql`).
  - Script ejecutor automático de semillas (`seeds/seed_runner.py`).
- **Herramientas de Administración y Pruebas**:
  - CLI unificada `scripts/manage_db.py` (`init`, `migrate`, `rollback`, `seed`, `reset`, `status`).
  - Suite de pruebas de integridad relacional `scripts/test_db.py` con `pytest`.
  - Pruebas de ciclo de vida de migraciones e idempotencia `tests/test_migrations.py`.
- **Integración y Despliegue**:
  - Integración nativa con **Supabase PostgreSQL** (Pooler puerto 6543 y directo 5432).
  - `docker-compose.yml` para despliegue local de PostgreSQL 16 y pgAdmin 4.
  - Pipeline de CI en GitHub Actions (`.github/workflows/db-ci.yml`) con validación de sintaxis y testing automático.
