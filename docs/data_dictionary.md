# Diccionario de Datos - LolAnalyzer Database

Este documento describe la especificación formal del modelo relacional, tipos de datos, restricciones de integridad, reglas de negocio e índices para la base de datos de **LolAnalyzer**.

---

## 1. Tabla: `users`
Almacena la información de los invocadores registrados, autenticación híbrida (local y OAuth2), vinculación con el cliente Riot LCU y preferencias del coach táctico de IA.

| Columna | Tipo de Dato | Nulo | Por Defecto | Clave | Restricciones / Reglas de Negocio | Descripción |
| :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| `id` | `SERIAL / INT` | No | Autoincremental | **PK** | `PRIMARY KEY` | Identificador único secuencial del usuario. |
| `email` | `VARCHAR(255)` | No | - | **UQ** | `UNIQUE` | Correo electrónico principal del usuario (usado para login local). |
| `username` | `VARCHAR(100)` | No | - | - | Longitud máx. 100 | Nombre visible en la plataforma LolAnalyzer. |
| `hashed_password`| `VARCHAR(255)` | Sí | `NULL` | - | Formato Bcrypt (`$2b$...`) | Contraseña encriptada para auth local (nula para login puro con Google). |
| `auth_provider` | `VARCHAR(50)` | No | `'local'` | - | `CHECK (auth_provider IN ('local', 'google', 'both'))` | Proveedor de identidad utilizado. |
| `google_id` | `VARCHAR(255)` | Sí | `NULL` | **UQ** | `UNIQUE` | Identificador único de sujeto (`sub`) emitido por Google OAuth 2.0. |
| `avatar_url` | `VARCHAR(500)` | Sí | `NULL` | - | Formato URL válido | URL de la imagen de perfil del usuario. |
| `summoner_name` | `VARCHAR(100)` | Sí | `NULL` | - | Riot ID / Invocador | Nombre del invocador detectado automáticamente por Riot LCU. |
| `summoner_icon_id`| `INTEGER` | Sí | `NULL` | - | Ícono LoL Data Dragon | ID numérico del ícono de invocador en League of Legends. |
| `region` | `VARCHAR(20)` | No | `'la1'` | - | e.g. `'la1'`, `'la2'`, `'na1'` | Servidor regional de Riot Games. |
| `preferred_roles`| `VARCHAR(100)` | No | `'MID,TOP'` | - | CSV de roles estándar | Roles prioritarios del jugador (`TOP`, `JUNGLE`, `MID`, `ADC`, `SUPPORT`). |
| `coach_sensitivity`| `VARCHAR(20)` | No | `'normal'` | - | `CHECK (coach_sensitivity IN ('low', 'normal', 'high'))` | Sensibilidad de disparo para consejos heurísticos de IA. |
| `is_active` | `BOOLEAN` | No | `TRUE` | - | - | Estado de la cuenta (activo/suspendido). |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | - | UTC | Fecha y hora de creación de la cuenta. |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | - | Auto-actualizado vía trigger | Fecha y hora de la última modificación del perfil. |

---

## 2. Tabla: `token_blacklist`
Mantiene los identificadores únicos de JWT (`jti`) revocados para garantizar cierre de sesión criptográfico inmediato y mitigación de ataques de repetición.

| Columna | Tipo de Dato | Nulo | Por Defecto | Clave | Restricciones / Reglas de Negocio | Descripción |
| :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| `id` | `SERIAL / INT` | No | Autoincremental | **PK** | `PRIMARY KEY` | Identificador único del registro de revocación. |
| `token_jti` | `VARCHAR(255)` | No | - | **UQ** | `UNIQUE` | Identificador único criptográfico (`jti`) extraído del JWT. |
| `revoked_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | - | UTC | Marca temporal en la que el usuario cerró sesión. |
| `expires_at` | `TIMESTAMPTZ` | No | - | - | UTC | Fecha de expiración original del token (permite depuración automática). |

---

## 3. Tabla: `match_records`
Registra el historial de partidas disputadas por el invocador con estadísticas globales de rendimiento y métricas de comportamiento táctico/psicológico.

| Columna | Tipo de Dato | Nulo | Por Defecto | Clave | Restricciones / Reglas de Negocio | Descripción |
| :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| `id` | `SERIAL / INT` | No | Autoincremental | **PK** | `PRIMARY KEY` | Identificador único de la partida registrada. |
| `user_id` | `INTEGER` | No | - | **FK** | `FOREIGN KEY (users.id) ON DELETE CASCADE` | Invocador dueño del registro histórico. |
| `game_id` | `BIGINT` | Sí | `NULL` | - | Riot Match ID | Identificador oficial de partida emitido por Riot Games. |
| `champion_name` | `VARCHAR(100)` | No | - | - | e.g. `'Ahri'`, `'Jinx'` | Nombre del campeón utilizado. |
| `role` | `VARCHAR(50)` | No | - | - | `CHECK (role IN ('TOP','JUNGLE','MID','ADC','SUPPORT','UNKNOWN'))` | Posición de juego en la partida. |
| `kills` | `INTEGER` | No | `0` | - | `CHECK (kills >= 0)` | Asesinatos conseguidos. |
| `deaths` | `INTEGER` | No | `0` | - | `CHECK (deaths >= 0)` | Muertes acumuladas. |
| `assists` | `INTEGER` | No | `0` | - | `CHECK (assists >= 0)` | Asistencias a aliados. |
| `cs` | `INTEGER` | No | `0` | - | `CHECK (cs >= 0)` | Creep Score (minions y monstruos asesinados). |
| `gold_earned` | `INTEGER` | No | `0` | - | - | Oro total obtenido en la partida. |
| `gold_difference`| `INTEGER` | No | `0` | - | - | Diferencia neta de oro contra el rival de línea al finalizar. |
| `duration_seconds`| `INTEGER` | No | `0` | - | `CHECK (duration_seconds >= 0)` | Duración total de la partida en segundos. |
| `win` | `BOOLEAN` | No | `FALSE` | - | `TRUE` (Victoria) / `FALSE` (Derrota) | Resultado de la partida. |
| `tilt_triggers_count`| `INTEGER` | No | `0` | - | - | Número de episodios de tilt detectados por el motor heurístico. |
| `advices_received_count`| `INTEGER` | No | `0` | - | - | Total de sugerencias tácticas emitidas por el Copilot de IA. |
| `advices_followed_count`| `INTEGER` | No | `0` | - | - | Total de sugerencias acatadas exitosamente por el jugador. |
| `played_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | - | UTC | Fecha y hora en la que se disputó la partida. |

---

## 4. Tabla: `match_telemetry_points`
Registra la serie temporal de alta frecuencia segundo a segundo durante el transcurso de una partida para renderizar curvas de CS/minuto, destellos y consejos de IA en el dashboard.

| Columna | Tipo de Dato | Nulo | Por Defecto | Clave | Restricciones / Reglas de Negocio | Descripción |
| :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| `id` | `SERIAL / INT` | No | Autoincremental | **PK** | `PRIMARY KEY` | Identificador único del punto de telemetría. |
| `match_id` | `INTEGER` | No | - | **FK** | `FOREIGN KEY (match_records.id) ON DELETE CASCADE` | Partida a la que pertenece este fotograma temporal. |
| `game_time_seconds`| `DOUBLE PRECISION` | No | - | - | `CHECK (game_time_seconds >= 0.0)` | Segundo exacto de la partida en el que se capturó la muestra. |
| `cs` | `INTEGER` | No | `0` | - | `CHECK (cs >= 0)` | Creep Score acumulado en este instante. |
| `cs_per_minute` | `DOUBLE PRECISION` | No | `0.0` | - | `CHECK (cs_per_minute >= 0.0)` | Tasa instantánea de súbditos por minuto. |
| `kills` | `INTEGER` | No | `0` | - | `CHECK (kills >= 0)` | Asesinatos acumulados en este segundo. |
| `deaths` | `INTEGER` | No | `0` | - | `CHECK (deaths >= 0)` | Muertes acumuladas en este segundo. |
| `flash_ready` | `BOOLEAN` | No | `TRUE` | - | `TRUE` (Disponible) / `FALSE` (En Enfriamiento) | Estado del hechizo de invocador Destello (Flash). |
| `advice_text` | `VARCHAR(255)` | Sí | `NULL` | - | - | Consejo táctico emitido por el Copilot de IA en este segundo. |
