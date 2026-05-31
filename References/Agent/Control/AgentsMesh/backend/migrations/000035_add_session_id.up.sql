-- Add session_id field to pods table for agent session management
-- session_id is used by agents like Claude Code to identify sessions for resume functionality

ALTER TABLE pods ADD COLUMN session_id VARCHAR(36);

-- Create index for faster lookups by session_id
CREATE INDEX idx_pods_session_id ON pods(session_id);

-- Add source_pod_key for tracking resume relationships
-- When a pod is created via resume, source_pod_key points to the original pod
ALTER TABLE pods ADD COLUMN source_pod_key VARCHAR(100);

-- Create index for source_pod_key
CREATE INDEX idx_pods_source_pod_key ON pods(source_pod_key);
