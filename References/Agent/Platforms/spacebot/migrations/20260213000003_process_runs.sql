-- Branch and worker run history for channel timeline display.

CREATE TABLE IF NOT EXISTS branch_runs (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    description TEXT NOT NULL,
    conclusion TEXT,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE INDEX idx_branch_runs_channel ON branch_runs(channel_id, started_at);

CREATE TABLE IF NOT EXISTS worker_runs (
    id TEXT PRIMARY KEY,
    channel_id TEXT,
    task TEXT NOT NULL,
    result TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE
);

CREATE INDEX idx_worker_runs_channel ON worker_runs(channel_id, started_at);
