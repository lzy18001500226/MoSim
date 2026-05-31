-- 000149_loop_used_env_bundles_array.up.sql
-- Promote `loops.used_env_bundle TEXT` (single name) to
-- `loops.used_env_bundles TEXT[]` (ordered list of names) so the Loop
-- create/edit dialog can attach multiple EnvBundles in the same merge order
-- the Pod create dialog uses.
--
-- The ordered list mirrors Pod's `agentfile_layer` semantics: each name
-- becomes a `USE_ENV_BUNDLE "<name>"` line emitted in array order; later
-- entries override earlier ones on conflicting env keys.
--
-- Stored as TEXT[] (not JSONB) to match the project convention for ordered
-- string lists (cf. channel_bindings.granted_scopes / pending_scopes).

BEGIN;

ALTER TABLE loops
  ADD COLUMN used_env_bundles TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[];

-- Carry existing single-bundle assignments forward as one-element arrays.
UPDATE loops
SET used_env_bundles = ARRAY[used_env_bundle]
WHERE used_env_bundle IS NOT NULL AND used_env_bundle <> '';

ALTER TABLE loops DROP COLUMN used_env_bundle;

COMMENT ON COLUMN loops.used_env_bundles IS 'Ordered list of EnvBundle names to attach to every run of this loop (each emitted as USE_ENV_BUNDLE "<name>" in the generated AgentFile layer, in array order; later entries override earlier ones on conflicting keys). Empty array = no bundles.';

COMMIT;
