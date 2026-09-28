-- =============================================================================
-- LolAnalyzer Database Seed - Fine-Grained Telemetry Points
-- File: seeds/03_telemetry_seed.sql
-- Description: High-resolution time-series timeline points across games
-- to render interactive CS/min curves, death markers, and AI tactical advice logs.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

INSERT INTO match_telemetry_points (
    id, match_id, game_time_seconds, cs, cs_per_minute, kills, deaths,
    flash_ready, advice_text
) VALUES
-- Match 1 (Ahri Mid - Win, 30 min duration)
(1, 1, 60.0, 0, 0.0, 0, 0, TRUE, NULL),
(2, 1, 180.0, 18, 6.0, 0, 0, TRUE, 'Oleada equilibrada en mid. Mantén visión en arbusto de río.'),
(3, 1, 300.0, 38, 7.6, 1, 0, TRUE, 'Primer asesinato logrado. Aprovecha la prioridad para colocar centinela profundo.'),
(4, 1, 420.0, 56, 8.0, 2, 0, FALSE, 'Destello utilizado defensivamente. Juega seguro los próximos 5 minutos.'),
(5, 1, 600.0, 82, 8.2, 3, 0, FALSE, 'Excelente CS/min (8.2). El dragón aparecerá en 60 segundos.'),
(6, 1, 780.0, 110, 8.4, 4, 1, TRUE, 'Destello recuperado. Busca flanqueo con Encanto en la pelea de heraldo.'),
(7, 1, 960.0, 136, 8.5, 5, 1, TRUE, 'Torre de mid destruida. Rota a bot para empujar la ventaja.'),
(8, 1, 1200.0, 172, 8.6, 6, 1, TRUE, 'Control de visión superior en zona de Barón.'),
(9, 1, 1500.0, 215, 8.6, 8, 1, TRUE, 'Pelea por alma de dragón. Guarda definitiva para escapar de iniciaciones pesadas.'),
(10, 1, 1820.0, 245, 8.1, 9, 1, TRUE, 'Victoria asegurada tras Barón Nashor.'),

-- Match 7 (Jinx ADC - Win, 34 min duration)
(11, 7, 60.0, 0, 0.0, 0, 0, TRUE, NULL),
(12, 7, 180.0, 19, 6.3, 0, 0, TRUE, 'Buen control de oleada contra botlane agresiva.'),
(13, 7, 360.0, 48, 8.0, 1, 0, TRUE, 'Prioridad bot asegurada. Dragón disponible.'),
(14, 7, 600.0, 92, 9.2, 3, 0, FALSE, '3 Kills tempranas. Prioriza Mítico + Grebas de Berserker.'),
(15, 7, 900.0, 142, 9.4, 6, 1, TRUE, 'Posicionamiento seguro detrás del soporte en teamfights.'),
(16, 7, 1200.0, 195, 9.75, 9, 1, TRUE, 'Pico de poder de 3 objetos alcanzado. Agrupa con el equipo.'),
(17, 7, 1500.0, 248, 9.92, 12, 2, FALSE, 'Mantente a rango máximo de Cohetes en pelea de Barón.'),
(18, 7, 1800.0, 288, 9.6, 13, 2, TRUE, 'Inhibidor central destruido.'),
(19, 7, 2050.0, 312, 9.1, 14, 2, TRUE, 'Victoria con KDA sobresaliente (14/2/9).'),

-- Match 3 (Orianna Mid - Loss with tilt episodes)
(20, 3, 60.0, 0, 0.0, 0, 0, TRUE, NULL),
(21, 3, 180.0, 14, 4.6, 0, 1, FALSE, 'Gank enemigo exitoso. Precaución: destello no disponible.'),
(22, 3, 300.0, 26, 5.2, 0, 2, FALSE, 'Alerta de Tilt: 2 muertes consecutivas. Congela oleada bajo torre.'),
(23, 3, 600.0, 62, 6.2, 1, 3, TRUE, 'Evita sobreextenderte sin visión del jungla rival.'),
(24, 3, 900.0, 105, 7.0, 2, 4, TRUE, 'Onda de Choque acertada en 3 objetivos. Mantén la calma.'),
(25, 3, 1200.0, 148, 7.4, 2, 5, TRUE, 'Presión enemiga en inhibidor bot.'),
(26, 3, 1680.0, 210, 7.5, 3, 5, TRUE, 'Derrota tras asedio en base.')
ON CONFLICT (id) DO UPDATE SET
    match_id = EXCLUDED.match_id,
    game_time_seconds = EXCLUDED.game_time_seconds,
    cs = EXCLUDED.cs,
    cs_per_minute = EXCLUDED.cs_per_minute,
    kills = EXCLUDED.kills,
    deaths = EXCLUDED.deaths,
    flash_ready = EXCLUDED.flash_ready,
    advice_text = EXCLUDED.advice_text;

-- Reset sequence to avoid ID collisions on next inserts (PostgreSQL specific)
SELECT setval('match_telemetry_points_id_seq', (SELECT MAX(id) FROM match_telemetry_points));
