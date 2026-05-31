-- 000149_loop_used_env_bundles_array.down.sql
-- Revert to single-string column. Multi-bundle assignments lose all but
-- the first entry — the row's first bundle wins to preserve the historical
-- "USE_ENV_BUNDLE comes first in merge order" intent.
BEGIN;

ALTER TABLE loops ADD COLUMN used_env_bundle TEXT;

UPDATE loops
SET used_env_bundle = used_env_bundles[1]
WHERE array_length(used_env_bundles, 1) >= 1;

ALTER TABLE loops DROP COLUMN used_env_bundles;

COMMIT;
