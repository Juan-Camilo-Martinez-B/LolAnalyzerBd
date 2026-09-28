# Documentación de Vistas, Triggers y Procedimientos Almacenados

Este documento describe la lógica de negocio encapsulated en el motor de base de datos de **LolAnalyzer**.

---

## 1. Vistas SQL Analíticas

### A. `v_player_stats_summary`
Proporciona una consolidación precalculada del historial de cada invocador:
- **Campos expuestos**: `user_id`, `username`, `summoner_name`, `region`, `total_matches`, `total_wins`, `total_losses`, `winrate_percentage`, `total_kills`, `total_deaths`, `total_assists`, `average_kda`, `average_cs`, `average_cs_per_minute`, `total_tilt_triggers`, `avg_tilt_triggers_per_match`, `total_advices_received`, `total_advices_followed`, `coach_compliance_rate_percentage`.
- **Casos de uso**: Dashboard principal del usuario, tarjeta de perfil y métricas de desempeño histórico.

### B. `v_champion_performance`
Agrupa el desempeño del jugador a nivel de campeón y rol:
- **Campos expuestos**: `user_id`, `champion_name`, `role`, `games_played`, `wins`, `losses`, `winrate_percentage`, `avg_kda`, `avg_kills`, `avg_deaths`, `avg_assists`, `avg_cs_per_minute`, `avg_gold_difference`.
- **Casos de uso**: Pestaña de maestría de campeones y recomendaciones automáticas en la fase de Champion Select.

### C. `v_tilt_coach_analytics`
Cruza los disparadores de frustración (tilt) con la adherencia a los consejos del coach de IA:
- **Campos expuestos**: `user_id`, `role`, `total_games_analyzed`, `total_tilt_episodes`, `avg_tilt_per_game`, `total_ai_advices_given`, `total_ai_advices_followed`, `coach_compliance_percentage`, `winrate_when_following_coach_pct`, `winrate_without_tilt_pct`.
- **Casos de uso**: Gráfico de impacto del Copilot y mapa de calor psicológico del invocador.

---

## 2. Funciones y Triggers

### A. Función `fn_update_timestamp()`
- **Lenguaje**: `PL/pgSQL`
- **Comportamiento**: Asigna `NEW.updated_at = CURRENT_TIMESTAMP` antes de que se complete una instrucción `UPDATE` en la fila.

### B. Trigger `trg_users_updated_at`
- **Tabla objetivo**: `users`
- **Evento**: `BEFORE UPDATE ON users FOR EACH ROW`
- **Efecto**: Garantiza una trazabilidad estricta de cuándo se modificaron configuraciones, avatares o contraseñas.

---

## 3. Procedimientos Almacenados

### A. Función / Procedimiento `sp_reset_user_matches(p_user_id INTEGER)`
- **Propósito**: Ejecuta la purga transaccional y atómica de todas las partidas registradas y su respectiva telemetría asociada para un usuario específico.
- **Retorno**: `INTEGER` indicando la cantidad exacta de partidas eliminadas.
- **Garantía**: Se ejecuta en una sola transacción sin dejar registros huérfanos gracias al borrado en cascada.
