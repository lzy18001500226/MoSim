-- Rollback: 000026_fix_git_credential_fk
-- Restore the original (incorrect) foreign key for rollback purposes

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_default_git_credential_id_fkey;

-- Note: This restores the incorrect FK for rollback compatibility
-- user_git_connections table may not exist, so this rollback might fail
ALTER TABLE users ADD CONSTRAINT users_default_git_credential_id_fkey
    FOREIGN KEY (default_git_credential_id)
    REFERENCES user_git_connections(id) ON DELETE SET NULL;
