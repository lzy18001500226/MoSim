-- Track chunk-level progress for file ingestion to survive restarts.
CREATE TABLE IF NOT EXISTS ingestion_progress (
    content_hash TEXT NOT NULL,
    chunk_index  INTEGER NOT NULL,
    total_chunks INTEGER NOT NULL,
    filename     TEXT NOT NULL,
    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (content_hash, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_ingestion_progress_hash ON ingestion_progress(content_hash);
