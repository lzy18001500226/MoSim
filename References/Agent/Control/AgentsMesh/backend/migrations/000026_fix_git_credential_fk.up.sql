-- Migration: 000026_fix_git_credential_fk
-- Fix: users.default_git_credential_id foreign key points to wrong table
-- The FK was pointing to user_git_connections (old table) instead of user_git_credentials

-- Drop the incorrect foreign key constraint (if exists from previous migrations)
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_default_git_credential_id_fkey;

-- Add the column if it doesn't exist (was removed in migration 19)
ALTER TABLE users ADD COLUMN IF NOT EXISTS default_git_credential_id BIGINT;

-- Add the correct foreign key constraint
ALTER TABLE users ADD CONSTRAINT users_default_git_credential_id_fkey
    FOREIGN KEY (default_git_credential_id)
    REFERENCES user_git_credentials(id) ON DELETE SET NULL;
