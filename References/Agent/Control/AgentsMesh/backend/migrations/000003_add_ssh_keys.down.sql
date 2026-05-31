-- Migration: 000003_add_ssh_keys (down)
-- Remove SSH Keys table and ssh_key_id column from git_providers

-- Remove ssh_key_id column from git_providers
ALTER TABLE git_providers DROP COLUMN IF EXISTS ssh_key_id;

-- Drop trigger
DROP TRIGGER IF EXISTS update_ssh_keys_updated_at ON ssh_keys;

-- Drop SSH Keys table
DROP TABLE IF EXISTS ssh_keys;
