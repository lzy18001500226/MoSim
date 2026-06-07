-- Conversation messages (one row per message, user or assistant)
CREATE TABLE IF NOT EXISTS conversation_messages (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- 'user' or 'assistant'
    sender_name TEXT,                -- display name (null for assistant)
    sender_id TEXT,                  -- platform user ID (null for assistant)
    content TEXT NOT NULL,
    metadata TEXT,                   -- JSON blob with platform-specific fields
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_channel ON conversation_messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel_time ON conversation_messages(channel_id, created_at);
