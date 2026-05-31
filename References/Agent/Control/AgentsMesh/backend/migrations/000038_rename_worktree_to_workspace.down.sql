-- Revert: rename workspace_path back to worktree_path

ALTER TABLE pods RENAME COLUMN workspace_path TO worktree_path;
