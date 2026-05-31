-- Migration: 000014_user_settings_refactor (DOWN)
-- Rollback user settings refactor

-- Remove default_git_credential_id from users
ALTER TABLE users DROP COLUMN IF EXISTS default_git_credential_id;

-- Remove config_overrides from pods
ALTER TABLE pods DROP COLUMN IF EXISTS config_overrides;

-- Drop organization_agent_configs
DROP TRIGGER IF EXISTS update_organization_agent_configs_updated_at ON organization_agent_configs;
DROP TABLE IF EXISTS organization_agent_configs;

-- Drop user_git_credentials
DROP TRIGGER IF EXISTS update_user_git_credentials_updated_at ON user_git_credentials;
DROP TABLE IF EXISTS user_git_credentials;

-- Drop user_repository_providers
DROP TRIGGER IF EXISTS update_user_repository_providers_updated_at ON user_repository_providers;
DROP TABLE IF EXISTS user_repository_providers;
