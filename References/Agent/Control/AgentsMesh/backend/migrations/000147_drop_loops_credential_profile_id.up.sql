-- Migration 000137: Drop loops.credential_profile_id.
-- The Pod orchestrator no longer consults this column; bundle binding flows
-- exclusively through the AgentFile layer (USE_ENV_BUNDLE declarations).
-- Keeping the column live would let users set a value that is then silently
-- ignored at run-time — a foot-gun the cleanup removes.

ALTER TABLE loops DROP COLUMN IF EXISTS credential_profile_id;
