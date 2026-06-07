-- Add current_branch column to track the checked-out branch (distinct from
-- default_branch which tracks the remote's default, e.g. "main").
-- Nullable because existing rows don't have this info until the next scan.
ALTER TABLE project_repos ADD COLUMN current_branch TEXT;
