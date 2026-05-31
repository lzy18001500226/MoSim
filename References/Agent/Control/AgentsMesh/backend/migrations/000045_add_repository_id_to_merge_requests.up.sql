-- Add repository_id to ticket_merge_requests table
-- MR is now primarily associated with repository, ticket becomes optional

-- Add repository_id column (not null)
ALTER TABLE ticket_merge_requests ADD COLUMN IF NOT EXISTS repository_id BIGINT;

-- Create index for repository_id
CREATE INDEX IF NOT EXISTS idx_ticket_merge_requests_repository_id ON ticket_merge_requests(repository_id);

-- Make ticket_id nullable (was not null before)
ALTER TABLE ticket_merge_requests ALTER COLUMN ticket_id DROP NOT NULL;

-- Add index for pod_id if not exists
CREATE INDEX IF NOT EXISTS idx_ticket_merge_requests_pod_id ON ticket_merge_requests(pod_id);

-- Add composite index for repository + branch queries
CREATE INDEX IF NOT EXISTS idx_ticket_merge_requests_repo_branch ON ticket_merge_requests(repository_id, source_branch);
