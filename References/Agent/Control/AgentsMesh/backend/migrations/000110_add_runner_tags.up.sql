ALTER TABLE runners ADD COLUMN tags JSONB DEFAULT '[]';
CREATE INDEX idx_runners_tags ON runners USING GIN (tags);
