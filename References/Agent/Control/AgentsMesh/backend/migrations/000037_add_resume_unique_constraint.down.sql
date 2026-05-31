-- Remove the partial unique index for resume constraint
DROP INDEX IF EXISTS idx_pods_source_pod_key_active_unique;
