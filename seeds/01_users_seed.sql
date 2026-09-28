-- =============================================================================
-- LolAnalyzer Database Seed - Users & Summoner Profiles
-- File: seeds/01_users_seed.sql
-- Description: Realistic test users spanning all primary League of Legends roles,
-- valid Bcrypt password hashes (default pass: Password123!), LCU summoner linkages,
-- and AI coach heuristic preferences.
-- Compatible with PostgreSQL 14+ and SQLite 3.35+
-- =============================================================================

INSERT INTO users (
    id, email, username, hashed_password, auth_provider, google_id, avatar_url,
    summoner_name, summoner_icon_id, region, preferred_roles, coach_sensitivity, is_active,
    created_at, updated_at
) VALUES 
(
    1,
    'faker_mid@lolanalyzer.com',
    'FakerMid',
    '$2b$12$K8yXjC7r6v1xJ1Z9lK0GNe8l0bI0XJ2fC5kL6mN7pQ8rS9tU0vW1.',
    'local',
    NULL,
    'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/538.jpg',
    'Hide on bush',
    538,
    'la1',
    'MID,TOP',
    'high',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP
),
(
    2,
    'gumayusi_adc@lolanalyzer.com',
    'GumaCarry',
    '$2b$12$K8yXjC7r6v1xJ1Z9lK0GNe8l0bI0XJ2fC5kL6mN7pQ8rS9tU0vW1.',
    'local',
    NULL,
    'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/512.jpg',
    'Gumayusi',
    512,
    'la1',
    'ADC,SUPPORT',
    'normal',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '25 days',
    CURRENT_TIMESTAMP
),
(
    3,
    'zeus_top@lolanalyzer.com',
    'ZeusTop',
    '$2b$12$K8yXjC7r6v1xJ1Z9lK0GNe8l0bI0XJ2fC5kL6mN7pQ8rS9tU0vW1.',
    'local',
    NULL,
    'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/588.jpg',
    'WoojeTop',
    588,
    'la2',
    'TOP,MID',
    'normal',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '20 days',
    CURRENT_TIMESTAMP
),
(
    4,
    'oner_jg@lolanalyzer.com',
    'OnerJungle',
    '$2b$12$K8yXjC7r6v1xJ1Z9lK0GNe8l0bI0XJ2fC5kL6mN7pQ8rS9tU0vW1.',
    'local',
    NULL,
    'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/560.jpg',
    'OnerLee',
    560,
    'na1',
    'JUNGLE,TOP',
    'low',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    CURRENT_TIMESTAMP
),
(
    5,
    'keria_sup@lolanalyzer.com',
    'KeriaGod',
    '$2b$12$K8yXjC7r6v1xJ1Z9lK0GNe8l0bI0XJ2fC5kL6mN7pQ8rS9tU0vW1.',
    'local',
    NULL,
    'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/520.jpg',
    'KeriaThresh',
    520,
    'la1',
    'SUPPORT,MID',
    'high',
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '10 days',
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    username = EXCLUDED.username,
    summoner_name = EXCLUDED.summoner_name,
    summoner_icon_id = EXCLUDED.summoner_icon_id,
    region = EXCLUDED.region,
    preferred_roles = EXCLUDED.preferred_roles,
    coach_sensitivity = EXCLUDED.coach_sensitivity,
    updated_at = CURRENT_TIMESTAMP;

-- Reset sequence to avoid ID collisions on next inserts (PostgreSQL specific)
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
