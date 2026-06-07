CREATE TABLE IF NOT EXISTS saved_attachments (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    message_id TEXT,
    original_filename TEXT NOT NULL,
    saved_filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    disk_path TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_saved_attachments_channel ON saved_attachments(channel_id, created_at);
CREATE INDEX IF NOT EXISTS idx_saved_attachments_message ON saved_attachments(message_id);
