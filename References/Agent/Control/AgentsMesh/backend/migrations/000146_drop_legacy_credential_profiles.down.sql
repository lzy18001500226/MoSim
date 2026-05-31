-- Dev-only rollback. Recreates the legacy table with the migration-000090 shape
-- (agent_slug instead of agent_type_id) and copies credential-kind rows back
-- from env_bundles. Best-effort: agent_slug NULL bundles cannot round-trip and
-- are skipped — they didn't exist in the legacy schema anyway.

CREATE TABLE IF NOT EXISTS user_agent_credential_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_slug VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_runner_host BOOLEAN NOT NULL DEFAULT FALSE,
    credentials_encrypted JSONB,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, agent_slug, name)
);

CREATE INDEX IF NOT EXISTS idx_user_agent_cred_profiles_user
    ON user_agent_credential_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_agent_cred_profiles_agent_slug
    ON user_agent_credential_profiles(agent_slug);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_agent_cred_profiles_single_default
    ON user_agent_credential_profiles(user_id, agent_slug)
    WHERE is_default = TRUE;

CREATE TRIGGER update_user_agent_credential_profiles_updated_at
    BEFORE UPDATE ON user_agent_credential_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

INSERT INTO user_agent_credential_profiles (
    user_id, agent_slug, name, description,
    is_runner_host, credentials_encrypted, is_default, is_active, created_at, updated_at
)
SELECT
    owner_id, agent_slug, name, description,
    FALSE, data, kind_primary, is_active, created_at, updated_at
FROM env_bundles
WHERE owner_scope = 'user' AND kind = 'credential' AND agent_slug IS NOT NULL;

ALTER TABLE pods ADD COLUMN IF NOT EXISTS
    credential_profile_id BIGINT REFERENCES user_agent_credential_profiles(id) ON DELETE SET NULL;
