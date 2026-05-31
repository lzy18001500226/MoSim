-- Rename worktree_path to workspace_path for clarity
-- The concept remains the same: the working directory inside a sandbox

ALTER TABLE pods RENAME COLUMN worktree_path TO workspace_path;
