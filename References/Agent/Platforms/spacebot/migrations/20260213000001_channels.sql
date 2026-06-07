-- Active channels tracked by the system.
CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    display_name TEXT,
    platform_meta TEXT,
    bulletin TEXT,
    permissions TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_channels_active ON channels(is_active, last_activity_at);
CREATE INDEX IF NOT EXISTS idx_channels_platform ON channels(platform);
