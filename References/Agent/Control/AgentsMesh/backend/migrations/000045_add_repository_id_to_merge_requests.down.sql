-- Revert: remove repository_id from ticket_merge_requests

DROP INDEX IF EXISTS idx_ticket_merge_requests_repo_branch;
DROP INDEX IF EXISTS idx_ticket_merge_requests_pod_id;
DROP INDEX IF EXISTS idx_ticket_merge_requests_repository_id;

ALTER TABLE ticket_merge_requests ALTER COLUMN ticket_id SET NOT NULL;
ALTER TABLE ticket_merge_requests DROP COLUMN IF EXISTS repository_id;
