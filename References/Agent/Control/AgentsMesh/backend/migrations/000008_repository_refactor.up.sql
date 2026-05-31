-- Refactor repositories table to be self-contained (no git_provider_id dependency)
-- This supports the "权限跟人走" (credentials follow the person) design

-- Step 1: Add new columns to repositories table
ALTER TABLE repositories
    ADD COLUMN provider_type VARCHAR(50),
    ADD COLUMN provider_base_url VARCHAR(255),
    ADD COLUMN clone_url VARCHAR(500),
    ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'organization',
    ADD COLUMN imported_by_user_id BIGINT REFERENCES users(id);

-- Step 2: Migrate existing data from git_providers
UPDATE repositories r
SET
    provider_type = gp.provider_type,
    provider_base_url = gp.base_url,
    -- Generate clone_url based on provider type and full_path
    clone_url = CASE
        WHEN gp.provider_type = 'github' THEN 'https://github.com/' || r.full_path || '.git'
        WHEN gp.provider_type = 'gitlab' THEN gp.base_url || '/' || r.full_path || '.git'
        WHEN gp.provider_type = 'gitee' THEN 'https://gitee.com/' || r.full_path || '.git'
        ELSE gp.base_url || '/' || r.full_path || '.git'
    END,
    -- Set imported_by to first org member with owner role if available, otherwise NULL
    imported_by_user_id = (
        SELECT om.user_id FROM organization_members om
        WHERE om.organization_id = r.organization_id AND om.role = 'owner'
        ORDER BY om.joined_at ASC LIMIT 1
    )
FROM git_providers gp
WHERE r.git_provider_id = gp.id;

-- Step 3: Make provider_type and provider_base_url NOT NULL after data migration
ALTER TABLE repositories
    ALTER COLUMN provider_type SET NOT NULL,
    ALTER COLUMN provider_base_url SET NOT NULL;

-- Set default provider_type for any rows that might have been missed
UPDATE repositories SET provider_type = 'github' WHERE provider_type IS NULL;
UPDATE repositories SET provider_base_url = 'https://github.com' WHERE provider_base_url IS NULL;

-- Step 4: Drop the git_provider_id foreign key and column
-- First drop the unique constraint that includes git_provider_id
ALTER TABLE repositories DROP CONSTRAINT IF EXISTS repositories_git_provider_id_external_id_key;

-- Drop the foreign key constraint
ALTER TABLE repositories DROP CONSTRAINT IF EXISTS repositories_git_provider_id_fkey;

-- Drop the git_provider_id column
ALTER TABLE repositories DROP COLUMN git_provider_id;

-- Step 5: Add new unique constraint (organization_id, provider_type, provider_base_url, full_path)
ALTER TABLE repositories
    ADD CONSTRAINT repositories_org_provider_path_unique
    UNIQUE(organization_id, provider_type, provider_base_url, full_path);

-- Step 6: Add indexes for new columns
CREATE INDEX idx_repositories_provider_type ON repositories(provider_type);
CREATE INDEX idx_repositories_visibility ON repositories(visibility);
CREATE INDEX idx_repositories_imported_by ON repositories(imported_by_user_id);

-- Step 7: Add soft delete support
ALTER TABLE repositories ADD COLUMN deleted_at TIMESTAMPTZ;
CREATE INDEX idx_repositories_deleted_at ON repositories(deleted_at);
