-- 000156_agents_is_internal.up.sql
-- Add `is_internal` flag to the agents table as a second line of defense
-- against test fixtures leaking into the user-facing agent picker.
--
-- The primary defense is the migration-vs-seed split (see ADR
-- 2026-05-26-test-fixture-isolation): production DBs never receive test
-- agents in the first place. This column gives the backend a way to
-- exclude an agent from list views (ListBuiltinActive → frontend) even
-- if a misconfigured environment somehow ended up with one — for example
-- if an operator manually copies a dev seed into prod.
--
-- Internal agents are still visible to:
--   - the runner discovery path (ListAllActive) — agents need to launch
--     for legitimate test runs against the same backend
--   - admin/internal APIs that explicitly pass includeInternal=true
BEGIN;

ALTER TABLE agents
    ADD COLUMN is_internal BOOLEAN NOT NULL DEFAULT false;

COMMENT ON COLUMN agents.is_internal IS
    'When true, the agent is excluded from the user-facing list (ListBuiltinActive). '
    'Used to mark e2e/test fixtures so they cannot accidentally surface in production UIs.';

COMMIT;
