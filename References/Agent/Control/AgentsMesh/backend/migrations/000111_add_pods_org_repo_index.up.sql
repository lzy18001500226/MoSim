CREATE INDEX idx_pods_org_repo ON pods(organization_id, repository_id) WHERE repository_id IS NOT NULL;
