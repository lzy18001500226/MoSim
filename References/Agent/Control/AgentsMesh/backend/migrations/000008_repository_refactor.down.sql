-- Revert repository refactoring

-- Drop indexes
DROP INDEX IF EXISTS idx_repositories_deleted_at;
DROP INDEX IF EXISTS idx_repositories_imported_by;
DROP INDEX IF EXISTS idx_repositories_visibility;
DROP INDEX IF EXISTS idx_repositories_provider_type;

-- Drop unique constraint
ALTER TABLE repositories DROP CONSTRAINT IF EXISTS repositories_org_provider_path_unique;

-- Add back git_provider_id column (without foreign key - can't restore that)
ALTER TABLE repositories ADD COLUMN git_provider_id BIGINT;

-- Drop new columns
ALTER TABLE repositories
    DROP COLUMN IF EXISTS deleted_at,
    DROP COLUMN IF EXISTS imported_by_user_id,
    DROP COLUMN IF EXISTS visibility,
    DROP COLUMN IF EXISTS clone_url,
    DROP COLUMN IF EXISTS provider_base_url,
    DROP COLUMN IF EXISTS provider_type;

-- Note: Data migration from git_providers cannot be fully reversed
-- The git_provider_id will be NULL for all existing records
