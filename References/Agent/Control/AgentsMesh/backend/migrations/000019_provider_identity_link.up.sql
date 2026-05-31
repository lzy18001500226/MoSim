-- Add identity_id foreign key to user_repository_providers
-- This links OAuth-based providers to their identity for access token retrieval

ALTER TABLE user_repository_providers
ADD COLUMN identity_id BIGINT REFERENCES user_identities(id) ON DELETE SET NULL;

CREATE INDEX idx_user_repository_providers_identity ON user_repository_providers(identity_id);

-- Drop the old user_git_connections table (confirmed no important data)
-- First remove the foreign key constraint from users table
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_default_git_credential_id_fkey;
ALTER TABLE users DROP COLUMN IF EXISTS default_git_credential_id;
DROP TABLE IF EXISTS user_git_connections;
