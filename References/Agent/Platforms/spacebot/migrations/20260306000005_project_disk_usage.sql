-- Cache disk usage on repos and worktrees so the UI can show sizes inline.
ALTER TABLE project_repos ADD COLUMN disk_usage_bytes INTEGER;
ALTER TABLE project_worktrees ADD COLUMN disk_usage_bytes INTEGER;
