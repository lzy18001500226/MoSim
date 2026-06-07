-- Agent profile: cortex-generated personality data displayed on the overview card.
-- One row per agent, upserted each time the cortex regenerates.
CREATE TABLE IF NOT EXISTS agent_profile (
    agent_id    TEXT PRIMARY KEY NOT NULL,
    display_name TEXT,           -- optional human-friendly name the cortex picks
    status      TEXT,            -- short mood/status line (e.g. "deep in a rewrite")
    bio         TEXT,            -- 2-3 sentence self-description
    avatar_seed TEXT,            -- seed string for deterministic gradient generation
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
