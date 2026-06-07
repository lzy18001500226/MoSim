-- Cortex chat: persistent admin conversation with the cortex, one per agent.

CREATE TABLE IF NOT EXISTS cortex_chat_messages (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    channel_context TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cortex_chat_created ON cortex_chat_messages(created_at);
