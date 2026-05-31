-- Prevent concurrent resume of the same sandbox
-- This partial unique index ensures that only one active pod can exist
-- for a given source_pod_key at any time, preventing race conditions
-- where two resume requests could pass the application-level check simultaneously.

-- PostgreSQL partial unique index: only applies to rows where
-- source_pod_key IS NOT NULL AND status is active
-- Active statuses: initializing, running, paused, disconnected
-- Note: 'disconnected' means user closed browser but pod still runs on runner
CREATE UNIQUE INDEX idx_pods_source_pod_key_active_unique
ON pods(source_pod_key)
WHERE source_pod_key IS NOT NULL
  AND status IN ('initializing', 'running', 'paused', 'disconnected');

-- Note: This index will cause a unique constraint violation if two pods
-- try to resume the same sandbox simultaneously. The application should
-- catch this error and return an appropriate message to the user.
