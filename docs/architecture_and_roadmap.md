# Arquitectura y Roadmap de Base de Datos - LolAnalyzer

Este documento define las decisiones arquitectónicas, el flujo de desarrollo, la estrategia de particionado y la hoja de ruta para el almacenamiento de datos en **LolAnalyzer**.

---

## 1. Principios de Diseño Arquitectónico

1. **Fuente Única de Verdad (Single Source of Truth)**:
   - Todo cambio estructural a las entidades del sistema debe originarse en este repositorio (`lol-analyzer-bd`) mediante una migración versionada antes de consumirse en los modelos ORM del backend.
2. **Compatibilidad Dual de Motores**:
   - **Producción / Nube (Supabase / AWS PostgreSQL 16)**: Aprovecha tipos avanzados como `TIMESTAMPTZ`, funciones `PL/pgSQL`, triggers automáticos y connection pooling por puerto 6543 (`pgbouncer`).
   - **Desarrollo Rápido / Pruebas Aisladas (SQLite 3.35+)**: Permite a cualquier desarrollador ejecutar la suite de pruebas completa en milisegundos sin requerir servicios de red activos.
3. **Optimización para Series Temporales de Alta Frecuencia**:
   - La tabla `match_telemetry_points` almacena cientos de puntos por partida. Los índices compuestos `(match_id, game_time_seconds ASC)` permiten al backend realizar lecturas en $O(\log N + K)$ donde $K$ es la cantidad de puntos de la partida.

---

## 2. Flujo de Trabajo para Nuevas Migraciones

Para incorporar cambios al esquema:
1. Crear el script SQL incremental en `migrations/sql/V<N>__<descripcion>.sql`.
2. Crear la revisión tipada de Alembic con `alembic revision -m "<descripcion>"` o generar el archivo en `migrations/versions/`.
3. Ejecutar las pruebas automatizadas:
   ```powershell
   pytest scripts/test_db.py tests/ -v
   ```
4. Aplicar a Supabase:
   ```powershell
   python scripts/manage_db.py migrate
   ```

---

## 3. Hoja de Ruta (Roadmap) Futura

- [ ] **v1.1.0 - Particionado de Telemetría**: Implementar particionamiento por rango (`PARTITION BY RANGE (played_at)`) para archivar partidas antiguas sin degradar el rendimiento de inserción.
- [ ] **v1.2.0 - Tareas Programadas con pg_cron**: Limpieza periódica automática de tokens revocados expirados en `token_blacklist`.
- [ ] **v1.3.0 - Capa de Caché L2 con Redis**: Integración de vistas materializadas cacheadas para la tabla de líderes y estadísticas globales de la comunidad.
