-- =============================================================================
-- LolAnalyzer Database Seed - Match Records Dataset
-- File: seeds/02_matches_seed.sql
-- Description: Historical match records across diverse champions, roles,
-- realistic in-game durations (20-35 mins), KDA statistics, gold differentials,
-- and AI coaching / tilt occurrences.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

INSERT INTO match_records (
    id, user_id, game_id, champion_name, role, kills, deaths, assists,
    cs, gold_earned, gold_difference, duration_seconds, win,
    tilt_triggers_count, advices_received_count, advices_followed_count, played_at
) VALUES
-- User 1 (FakerMid - MID / TOP)
(
    1, 1, 689124501, 'Ahri', 'MID', 9, 1, 11,
    245, 14850, 3200, 1820, TRUE,
    0, 4, 4, CURRENT_TIMESTAMP - INTERVAL '7 days'
),
(
    2, 1, 689124502, 'Azir', 'MID', 7, 3, 9,
    298, 16200, 2100, 2140, TRUE,
    1, 5, 4, CURRENT_TIMESTAMP - INTERVAL '6 days'
),
(
    3, 1, 689124503, 'Orianna', 'MID', 3, 5, 6,
    210, 10800, -1800, 1680, FALSE,
    2, 6, 3, CURRENT_TIMESTAMP - INTERVAL '5 days'
),
(
    4, 1, 689124504, 'Sylas', 'MID', 12, 2, 8,
    230, 15900, 4500, 1750, TRUE,
    0, 3, 3, CURRENT_TIMESTAMP - INTERVAL '4 days'
),
(
    5, 1, 689124505, 'LeBlanc', 'MID', 8, 4, 5,
    185, 12400, 800, 1590, TRUE,
    1, 4, 3, CURRENT_TIMESTAMP - INTERVAL '2 days'
),
(
    6, 1, 689124506, 'Yone', 'TOP', 4, 6, 3,
    195, 11200, -2400, 1880, FALSE,
    3, 7, 2, CURRENT_TIMESTAMP - INTERVAL '1 day'
),

-- User 2 (GumaCarry - ADC)
(
    7, 2, 689124510, 'Jinx', 'ADC', 14, 2, 9,
    312, 18400, 5200, 2050, TRUE,
    0, 5, 5, CURRENT_TIMESTAMP - INTERVAL '6 days'
),
(
    8, 2, 689124511, 'KaiSa', 'ADC', 10, 3, 7,
    265, 15100, 2800, 1830, TRUE,
    1, 4, 4, CURRENT_TIMESTAMP - INTERVAL '4 days'
),
(
    9, 2, 689124512, 'Varus', 'ADC', 2, 6, 4,
    190, 9800, -3100, 1520, FALSE,
    2, 5, 2, CURRENT_TIMESTAMP - INTERVAL '3 days'
),
(
    10, 2, 689124513, 'Aphelios', 'ADC', 8, 4, 10,
    280, 16000, 1900, 1990, TRUE,
    1, 6, 5, CURRENT_TIMESTAMP - INTERVAL '1 day'
),

-- User 3 (ZeusTop - TOP)
(
    11, 3, 689124520, 'Aatrox', 'TOP', 8, 2, 6,
    240, 14200, 3100, 1790, TRUE,
    0, 3, 3, CURRENT_TIMESTAMP - INTERVAL '5 days'
),
(
    12, 3, 689124521, 'Jayce', 'TOP', 6, 5, 4,
    225, 12900, 500, 1710, FALSE,
    2, 5, 3, CURRENT_TIMESTAMP - INTERVAL '3 days'
),
(
    13, 3, 689124522, 'Gnar', 'TOP', 5, 1, 11,
    215, 13400, 2600, 1850, TRUE,
    0, 4, 4, CURRENT_TIMESTAMP - INTERVAL '1 day'
),

-- User 4 (OnerJungle - JUNGLE)
(
    14, 4, 689124530, 'LeeSin', 'JUNGLE', 11, 3, 8,
    160, 13800, 3400, 1680, TRUE,
    0, 4, 3, CURRENT_TIMESTAMP - INTERVAL '4 days'
),
(
    15, 4, 689124531, 'Sejuani', 'JUNGLE', 2, 2, 14,
    140, 11200, 1800, 1820, TRUE,
    0, 3, 3, CURRENT_TIMESTAMP - INTERVAL '2 days'
),
(
    16, 4, 689124532, 'Viego', 'JUNGLE', 4, 7, 3,
    155, 10500, -2200, 1740, FALSE,
    2, 6, 2, CURRENT_TIMESTAMP - INTERVAL '1 day'
),

-- User 5 (KeriaGod - SUPPORT)
(
    17, 5, 689124540, 'Thresh', 'SUPPORT', 2, 1, 18,
    35, 9400, 2100, 1810, TRUE,
    0, 4, 4, CURRENT_TIMESTAMP - INTERVAL '3 days'
),
(
    18, 5, 689124541, 'Nautilus', 'SUPPORT', 1, 4, 15,
    28, 8600, 900, 1720, TRUE,
    1, 3, 3, CURRENT_TIMESTAMP - INTERVAL '2 days'
),
(
    19, 5, 689124542, 'Bard', 'SUPPORT', 3, 5, 12,
    42, 8900, -1400, 1890, FALSE,
    1, 5, 3, CURRENT_TIMESTAMP - INTERVAL '1 day'
)
ON CONFLICT (id) DO UPDATE SET
    champion_name = EXCLUDED.champion_name,
    role = EXCLUDED.role,
    kills = EXCLUDED.kills,
    deaths = EXCLUDED.deaths,
    assists = EXCLUDED.assists,
    cs = EXCLUDED.cs,
    gold_earned = EXCLUDED.gold_earned,
    gold_difference = EXCLUDED.gold_difference,
    duration_seconds = EXCLUDED.duration_seconds,
    win = EXCLUDED.win,
    tilt_triggers_count = EXCLUDED.tilt_triggers_count,
    advices_received_count = EXCLUDED.advices_received_count,
    advices_followed_count = EXCLUDED.advices_followed_count,
    played_at = EXCLUDED.played_at;

-- Reset sequence to avoid ID collisions on next inserts (PostgreSQL specific)
SELECT setval('match_records_id_seq', (SELECT MAX(id) FROM match_records));
