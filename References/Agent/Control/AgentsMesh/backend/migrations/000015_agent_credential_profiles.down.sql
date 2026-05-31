-- Rollback: 000015_agent_credential_profiles

-- Remove credential_profile_id from pods table
ALTER TABLE pods DROP COLUMN IF EXISTS credential_profile_id;

-- Drop indexes
DROP INDEX IF EXISTS idx_user_agent_cred_profiles_single_default;
DROP INDEX IF EXISTS idx_user_agent_cred_profiles_default;
DROP INDEX IF EXISTS idx_user_agent_cred_profiles_agent_type;
DROP INDEX IF EXISTS idx_user_agent_cred_profiles_user;

-- Drop trigger
DROP TRIGGER IF EXISTS update_user_agent_credential_profiles_updated_at ON user_agent_credential_profiles;

-- Drop table
DROP TABLE IF EXISTS user_agent_credential_profiles;
