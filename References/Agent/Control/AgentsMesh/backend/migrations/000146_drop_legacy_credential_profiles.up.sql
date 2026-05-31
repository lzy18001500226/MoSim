-- Migration 000135: Retire the legacy credential table and the pod FK column.
-- Runs AFTER all callers have been switched to env_bundles (REST handlers,
-- ConfigBuilder, Rust core, frontend). Verify env_bundles has every credential
-- profile copied (the corresponding env_bundles rows were inserted by 000134)
-- before running this in production.

ALTER TABLE pods DROP COLUMN IF EXISTS credential_profile_id;
DROP TABLE IF EXISTS user_agent_credential_profiles;
