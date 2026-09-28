# Diagrama Entidad - Relación (ERD) - LolAnalyzer

Este documento contiene el modelo conceptual y lógico del esquema de base de datos de **LolAnalyzer** expresado en notación Mermaid interactiva.

---

## 1. Diagrama Entidad-Relación Visual (Mermaid)

```mermaid
erDiagram
    users ||--o{ match_records : "owns (1:N, ON DELETE CASCADE)"
    match_records ||--o{ match_telemetry_points : "contains (1:N, ON DELETE CASCADE)"

    users {
        int id PK "SERIAL / Autoincrement"
        varchar email UK "UNIQUE"
        varchar username
        varchar hashed_password "Nullable (Bcrypt)"
        varchar auth_provider "local | google | both"
        varchar google_id UK "Nullable"
        varchar avatar_url "Nullable"
        varchar summoner_name "Nullable (Riot LCU)"
        int summoner_icon_id "Nullable"
        varchar region "la1 | la2 | na1"
        varchar preferred_roles "MID,TOP,..."
        varchar coach_sensitivity "low | normal | high"
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    token_blacklist {
        int id PK "SERIAL / Autoincrement"
        varchar token_jti UK "UNIQUE (JWT JTI)"
        timestamptz revoked_at
        timestamptz expires_at
    }

    match_records {
        int id PK "SERIAL / Autoincrement"
        int user_id FK "FK -> users.id"
        bigint game_id "Nullable (Riot Game ID)"
        varchar champion_name "Ahri, Jinx, ..."
        varchar role "TOP, JUNGLE, MID, ADC, SUPPORT"
        int kills
        int deaths
        int assists
        int cs
        int gold_earned
        int gold_difference
        int duration_seconds
        boolean win "TRUE = Victory, FALSE = Defeat"
        int tilt_triggers_count
        int advices_received_count
        int advices_followed_count
        timestamptz played_at
    }

    match_telemetry_points {
        int id PK "SERIAL / Autoincrement"
        int match_id FK "FK -> match_records.id"
        double_precision game_time_seconds "Game second timestamp"
        int cs
        double_precision cs_per_minute
        int kills
        int deaths
        boolean flash_ready
        varchar advice_text "Nullable (AI Coach prompt)"
    }
```

---

## 2. Descripción de Cardinalidades y Reglas de Integridad

1. **`users` (1) a `match_records` (N)**:
   - Un usuario puede registrar múltiples partidas a lo largo de su historial ($0..N$).
   - Cada partida pertenece obligatoriamente a exactamente un usuario ($1..1$).
   - Regla de cascada: Si un usuario elimina su cuenta, se eliminan todas sus partidas asociadas mediante `ON DELETE CASCADE`.

2. **`match_records` (1) a `match_telemetry_points` (N)**:
   - Cada partida contiene una serie temporal de fotogramas de telemetría ($0..N$) tomados segundo a segundo o minuto a minuto.
   - Cada punto de telemetría pertenece estrictamente a una partida ($1..1$).
   - Regla de cascada: Si una partida es eliminada, todos sus puntos de telemetría se destruyen automáticamente vía `ON DELETE CASCADE`.

3. **`token_blacklist` (Entidad Independiente de Seguridad)**:
   - No mantiene claves foráneas directas para permitir la revocación inmediata sin requerir bloqueos de fila en la tabla de usuarios.
   - Mantiene una clave única (`UNIQUE`) sobre `token_jti` con un índice de alto rendimiento para validación en $O(1)$.
