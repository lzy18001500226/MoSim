-- Migration: 000014_user_settings_refactor
-- Refactor settings architecture: separate organization settings from personal settings
-- Core principle: "permissions follow the user"

-- ============================================================================
-- 1. User Repository Providers (for importing repositories)
-- ============================================================================
-- Replaces organization-level git_providers for repository import functionality
-- OAuth configuration for connecting to GitHub/GitLab/Gitee to fetch repository lists

CREATE TABLE user_repository_providers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Provider info
    provider_type VARCHAR(50) NOT NULL,       -- github, gitlab, gitee
    name VARCHAR(100) NOT NULL,               -- User-defined name
    base_url VARCHAR(255) NOT NULL,           -- https://github.com, https://gitlab.company.com

    -- OAuth configuration (for API access to fetch repos)
    client_id VARCHAR(255),
    client_secret_encrypted TEXT,

    -- Bot token (alternative to OAuth)
    bot_token_encrypted TEXT,

    -- Status
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, name)
);

CREATE INDEX idx_user_repository_providers_user ON user_repository_providers(user_id);
CREATE INDEX idx_user_repository_providers_type ON user_repository_providers(provider_type);

-- Trigger for updated_at
CREATE TRIGGER update_user_repository_providers_updated_at
    BEFORE UPDATE ON user_repository_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_repository_providers IS 'User-owned repository providers for importing repositories. Replaces organization-level git_providers.';

-- ============================================================================
-- 2. User Git Credentials (for Git operations: clone/push/pull)
-- ============================================================================
-- Unified credential storage with multiple types:
-- - runner_local: Use Runner machine's local git config (virtual, no actual credential stored)
-- - oauth: Shared from Repository Provider (references provider)
-- - pat: Personal Access Token
-- - ssh_key: SSH private key

CREATE TABLE user_git_credentials (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,
    credential_type VARCHAR(20) NOT NULL,     -- runner_local, oauth, pat, ssh_key

    -- OAuth type: reference to Repository Provider
    repository_provider_id BIGINT REFERENCES user_repository_providers(id) ON DELETE CASCADE,

    -- PAT type
    pat_encrypted TEXT,

    -- SSH Key type
    public_key TEXT,
    private_key_encrypted TEXT,
    fingerprint VARCHAR(255),

    -- Host pattern for matching repositories (optional)
    host_pattern VARCHAR(255),                -- e.g., github.com, gitlab.company.com, * for all

    -- Status
    is_default BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, name),

    -- Ensure credential_type is valid
    CONSTRAINT valid_credential_type CHECK (credential_type IN ('runner_local', 'oauth', 'pat', 'ssh_key'))
);

CREATE INDEX idx_user_git_credentials_user ON user_git_credentials(user_id);
CREATE INDEX idx_user_git_credentials_type ON user_git_credentials(credential_type);
CREATE INDEX idx_user_git_credentials_default ON user_git_credentials(user_id, is_default) WHERE is_default = TRUE;

-- Trigger for updated_at
CREATE TRIGGER update_user_git_credentials_updated_at
    BEFORE UPDATE ON user_git_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_git_credentials IS 'User Git credentials for Git operations. SSH Key is a credential type, not a separate concept.';

-- ============================================================================
-- 3. Organization Agent Configs (default agent configuration)
-- ============================================================================
-- Stores organization-level default configuration for agents
-- Pod creation can override these defaults

CREATE TABLE organization_agent_configs (
    id BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    agent_type_id BIGINT NOT NULL REFERENCES agent_types(id) ON DELETE CASCADE,

    -- Dynamic configuration from Plugin UI (JSON)
    config_values JSONB NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(organization_id, agent_type_id)
);

CREATE INDEX idx_org_agent_configs_org ON organization_agent_configs(organization_id);
CREATE INDEX idx_org_agent_configs_agent ON organization_agent_configs(agent_type_id);

-- Trigger for updated_at
CREATE TRIGGER update_organization_agent_configs_updated_at
    BEFORE UPDATE ON organization_agent_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE organization_agent_configs IS 'Organization-level default agent configurations. Pod creation can override these defaults.';

-- ============================================================================
-- 4. Add config_overrides to pods table
-- ============================================================================
-- Stores Pod-level configuration overrides (merged with organization defaults)

ALTER TABLE pods ADD COLUMN IF NOT EXISTS config_overrides JSONB DEFAULT '{}';

COMMENT ON COLUMN pods.config_overrides IS 'Pod-level configuration overrides, merged with organization defaults during Pod creation.';

-- ============================================================================
-- 5. Add default_git_credential_id to users table
-- ============================================================================
-- User's default Git credential preference

ALTER TABLE users ADD COLUMN IF NOT EXISTS default_git_credential_id BIGINT REFERENCES user_git_credentials(id) ON DELETE SET NULL;

COMMENT ON COLUMN users.default_git_credential_id IS 'User default Git credential. NULL means use Runner local credential.';
