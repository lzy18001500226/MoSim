-- Migration 000138: Re-enable EnvBundle binding on Loops.
-- After 000137 dropped the legacy loops.credential_profile_id column, Loops
-- lost their ability to attach a credential to scheduled/triggered runs.
-- The new shape stores a bundle NAME (not id) — matching how Pod creation
-- references bundles via USE_ENV_BUNDLE "name" — so a bundle rename or
-- re-creation keeps the binding stable.
--
-- NULL means "no bundle, use the Runner's native env".

ALTER TABLE loops ADD COLUMN IF NOT EXISTS used_env_bundle TEXT;
COMMENT ON COLUMN loops.used_env_bundle IS 'Name of the EnvBundle to attach to every run of this loop (USE_ENV_BUNDLE "<name>" in the generated AgentFile layer). NULL = no bundle.';
