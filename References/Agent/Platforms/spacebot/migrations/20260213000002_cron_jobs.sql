-- Cron job configurations table
CREATE TABLE IF NOT EXISTS cron_jobs (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    interval_secs INTEGER NOT NULL DEFAULT 3600,
    delivery_target TEXT NOT NULL,
    active_start_hour INTEGER,
    active_end_hour INTEGER,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Cron job execution log table
CREATE TABLE IF NOT EXISTS cron_executions (
    id TEXT PRIMARY KEY,
    cron_id TEXT NOT NULL,
    executed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success INTEGER NOT NULL,
    result_summary TEXT,
    FOREIGN KEY (cron_id) REFERENCES cron_jobs(id) ON DELETE CASCADE
);
