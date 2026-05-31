-- Remove session_id and source_pod_key fields from pods table

DROP INDEX IF EXISTS idx_pods_source_pod_key;
ALTER TABLE pods DROP COLUMN IF EXISTS source_pod_key;

DROP INDEX IF EXISTS idx_pods_session_id;
ALTER TABLE pods DROP COLUMN IF EXISTS session_id;
