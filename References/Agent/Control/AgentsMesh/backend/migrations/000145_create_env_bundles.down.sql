-- Down migration: drop env_bundles. Legacy user_agent_credential_profiles is
-- untouched on the way down — it was preserved through 000134, so this
-- rollback only undoes the new table.

DROP TABLE IF EXISTS env_bundles;
