-- Add thread support to cortex chat. Existing messages get a default thread.

ALTER TABLE cortex_chat_messages ADD COLUMN thread_id TEXT NOT NULL DEFAULT 'default';

CREATE INDEX idx_cortex_chat_thread ON cortex_chat_messages(thread_id, created_at);
