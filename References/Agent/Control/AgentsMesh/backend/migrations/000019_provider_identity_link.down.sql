-- Recreate user_git_connections table
CREATE TABLE user_git_connections (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    provider_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(255) NOT NULL,

    access_token_encrypted TEXT,
    ssh_private_key_encrypted TEXT,
    ssh_public_key TEXT,

    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    last_used_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, name)
);

CREATE INDEX idx_user_git_connections_user ON user_git_connections(user_id);

-- Remove identity_id from user_repository_providers
DROP INDEX IF EXISTS idx_user_repository_providers_identity;
ALTER TABLE user_repository_providers DROP COLUMN IF EXISTS identity_id;
