-- Soft-delete for memories: forgotten memories stay in the database but are
-- excluded from search and recall.
ALTER TABLE memories ADD COLUMN forgotten INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_memories_forgotten ON memories(forgotten);
