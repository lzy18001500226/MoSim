-- Migration: 000015_agent_credential_profiles
-- Add user agent credential profiles for managing multiple credential configurations per agent type
-- Core concept: Each user can have multiple credential profiles per agent type (RunnerHost or custom)

-- ============================================================================
-- 1. User Agent Credential Profiles
-- ============================================================================
-- Stores user-level credential configuration profiles for each agent type
-- - RunnerHost mode: No credentials injected, use Runner's local environment
-- - Custom mode: User-provided BASE_URL and API_KEY

CREATE TABLE user_agent_credential_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_type_id BIGINT NOT NULL REFERENCES agent_types(id) ON DELETE CASCADE,

    -- Profile info
    name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Credential type
    is_runner_host BOOLEAN NOT NULL DEFAULT FALSE,

    -- Encrypted credentials (for non-RunnerHost profiles)
    -- Stored as: {"base_url": "xxx", "api_key": "xxx", ...}
    credentials_encrypted JSONB,

    -- Status
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Each user can have only one profile with the same name per agent type
    UNIQUE(user_id, agent_type_id, name)
);

CREATE INDEX idx_user_agent_cred_profiles_user ON user_agent_credential_profiles(user_id);
CREATE INDEX idx_user_agent_cred_profiles_agent_type ON user_agent_credential_profiles(agent_type_id);
CREATE INDEX idx_user_agent_cred_profiles_default ON user_agent_credential_profiles(user_id, agent_type_id, is_default)
    WHERE is_default = TRUE;

-- Trigger for updated_at
CREATE TRIGGER update_user_agent_credential_profiles_updated_at
    BEFORE UPDATE ON user_agent_credential_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_agent_credential_profiles IS 'User agent credential profiles. Each user can have multiple credential configurations per agent type.';
COMMENT ON COLUMN user_agent_credential_profiles.is_runner_host IS 'When true, no credentials are injected - use Runner local environment';
COMMENT ON COLUMN user_agent_credential_profiles.credentials_encrypted IS 'Encrypted JSONB containing credential fields (e.g., base_url, api_key)';

-- ============================================================================
-- 2. Add credential_profile_id to pods table
-- ============================================================================
-- Stores which credential profile was used when creating the pod

ALTER TABLE pods ADD COLUMN IF NOT EXISTS
    credential_profile_id BIGINT REFERENCES user_agent_credential_profiles(id) ON DELETE SET NULL;

COMMENT ON COLUMN pods.credential_profile_id IS 'Reference to the credential profile used for this pod. NULL means use default profile or RunnerHost.';

-- ============================================================================
-- 3. Ensure only one default profile per user per agent type
-- ============================================================================
-- Create a partial unique index to enforce only one default per user per agent type

CREATE UNIQUE INDEX idx_user_agent_cred_profiles_single_default
    ON user_agent_credential_profiles(user_id, agent_type_id)
    WHERE is_default = TRUE;
