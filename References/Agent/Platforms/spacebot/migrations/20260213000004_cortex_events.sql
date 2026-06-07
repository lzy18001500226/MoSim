-- Cortex action history: bulletin generations, maintenance runs, health interventions.

CREATE TABLE IF NOT EXISTS cortex_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cortex_events_type ON cortex_events(event_type, created_at);
CREATE INDEX idx_cortex_events_created ON cortex_events(created_at);
