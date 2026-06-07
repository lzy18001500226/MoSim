-- Link workers to projects and worktrees for project-aware execution.
ALTER TABLE worker_runs ADD COLUMN project_id TEXT;
ALTER TABLE worker_runs ADD COLUMN worktree_id TEXT;
CREATE INDEX IF NOT EXISTS idx_worker_runs_project ON worker_runs(project_id);
