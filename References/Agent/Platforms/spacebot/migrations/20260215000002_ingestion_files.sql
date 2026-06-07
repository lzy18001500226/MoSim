-- Track ingested files for UI history and progress visibility.
CREATE TABLE IF NOT EXISTS ingestion_files (
    content_hash TEXT PRIMARY KEY,
    filename     TEXT NOT NULL,
    file_size    INTEGER NOT NULL,
    total_chunks INTEGER NOT NULL,
    status       TEXT NOT NULL DEFAULT 'processing',
    started_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
